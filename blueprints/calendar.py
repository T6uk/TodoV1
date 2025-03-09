from flask import Blueprint, render_template, request, redirect, url_for, jsonify, abort
from flask_login import login_required, current_user
import sqlite3
from datetime import datetime, timedelta
import json

calendar_bp = Blueprint('calendar', __name__)


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


@calendar_bp.route('/calendar')
@login_required
def calendar():
    """Display the calendar view"""
    return render_template('calendar.html')


@calendar_bp.route('/calendar/get_events')
@login_required
def get_events():
    """API to get all events as JSON"""
    conn = get_db_connection()

    # Get events from database
    events = conn.execute('''
        SELECT 
            id, 
            title, 
            description, 
            start_date, 
            start_time, 
            end_date, 
            end_time, 
            category,
            recurrence,
            recurrence_interval,
            recurrence_weekdays,
            recurrence_end,
            recurrence_count,
            recurrence_until
        FROM events
        WHERE deleted = 0
    ''').fetchall()

    # Convert to list of dicts
    events_list = []
    for event in events:
        event_dict = dict(event)

        # Parse weekdays from JSON string if exists
        if event_dict['recurrence_weekdays']:
            try:
                event_dict['weekdays'] = json.loads(event_dict['recurrence_weekdays'])
            except:
                event_dict['weekdays'] = []
        else:
            event_dict['weekdays'] = []

        events_list.append(event_dict)

    conn.close()
    return jsonify(events_list)


@calendar_bp.route('/calendar/add_event', methods=['POST'])
@login_required
def add_event():
    """Add a new event"""
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        start_date = request.form['start_date']
        start_time = request.form.get('start_time', '')
        end_date = request.form.get('end_date', start_date)
        end_time = request.form.get('end_time', '')
        category = request.form['category']

        # Recurrence information
        recurrence = request.form.get('recurrence', 'none')
        recurrence_interval = request.form.get('recurrence_interval', 1)
        recurrence_end = request.form.get('recurrence_end', 'never')
        recurrence_count = request.form.get('recurrence_count', 10)
        recurrence_until = request.form.get('recurrence_until', '')

        # Weekdays for weekly recurrence
        weekdays = request.form.getlist('weekdays')
        recurrence_weekdays = json.dumps(weekdays) if weekdays else None

        # Check if this is a recurring event and what scope to edit
        scope = request.form.get('edit_scope', 'single')
        instance_id = request.form.get('instance_id', '')

        if scope == 'single' and instance_id:
            # Create exception for this occurrence
            # Extract date from instance ID
            instance_date = instance_id.split('_')[-1].split('T')[0]

            # Create a new single event for this exception
            conn.execute('''
                INSERT INTO events (
                    title, 
                    description, 
                    start_date, 
                    start_time, 
                    end_date, 
                    end_time, 
                    category,
                    recurrence,
                    exception_to,
                    exception_date,
                    user_id,
                    deleted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'none', ?, ?, ?, 0)
            ''', (
                title,
                description,
                start_date,
                start_time,
                end_date,
                end_time,
                category,
                id,
                instance_date,
                current_user.id
            ))

            # Add this date to exceptions in the recurring event
            event = conn.execute('SELECT exceptions FROM events WHERE id = ?', (id,)).fetchone()
            exceptions = json.loads(event['exceptions']) if event['exceptions'] else []
            exceptions.append(instance_date)
            conn.execute('UPDATE events SET exceptions = ? WHERE id = ?', (json.dumps(exceptions), id))

        elif scope == 'future' and instance_id:
            # End the current series at this instance and create a new series
            instance_date = instance_id.split('_')[-1].split('T')[0]

            # Update original event to end before this instance
            conn.execute('''
                UPDATE events
                SET recurrence_end = 'on-date',
                    recurrence_until = ?
                WHERE id = ?
            ''', (instance_date, id))

            # Create new recurring event from this instance onwards
            conn.execute('''
                INSERT INTO events (
                    title, 
                    description, 
                    start_date, 
                    start_time, 
                    end_date, 
                    end_time, 
                    category, 
                    recurrence,
                    recurrence_interval,
                    recurrence_weekdays,
                    recurrence_end,
                    recurrence_count,
                    recurrence_until,
                    user_id,
                    deleted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            ''', (
                title,
                description,
                start_date,
                start_time,
                end_date,
                end_time,
                category,
                recurrence,
                recurrence_interval,
                recurrence_weekdays,
                recurrence_end,
                recurrence_count,
                recurrence_until,
                current_user.id
            ))
        else:
            # Update the main recurring event (all occurrences)
            conn.execute('''
                UPDATE events
                SET title = ?,
                    description = ?,
                    start_date = ?,
                    start_time = ?,
                    end_date = ?,
                    end_time = ?,
                    category = ?,
                    recurrence = ?,
                    recurrence_interval = ?,
                    recurrence_weekdays = ?,
                    recurrence_end = ?,
                    recurrence_count = ?,
                    recurrence_until = ?
                WHERE id = ?
            ''', (
                title,
                description,
                start_date,
                start_time,
                end_date,
                end_time,
                category,
                recurrence,
                recurrence_interval,
                recurrence_weekdays,
                recurrence_end,
                recurrence_count,
                recurrence_until,
                id
            ))

        conn.commit()

    # Get event data for display in the edit form
    event = conn.execute('''
        SELECT * FROM events WHERE id = ?
    ''', (id,)).fetchone()

    if not event:
        conn.close()
        abort(404)

    # If this is a recurring event, load the weekdays
    weekdays = []
    if event['recurrence_weekdays']:
        try:
            weekdays = json.loads(event['recurrence_weekdays'])
        except:
            pass

    conn.close()

    # Check if this is an instance of a recurring event
    instance_id = request.args.get('instance', '')

    return render_template(
        'edit_event.html',
        event=event,
        weekdays=weekdays,
        instance_id=instance_id,
        edit_scope=request.args.get('scope', '')
    )


@calendar_bp.route('/calendar/delete_event/<int:id>', methods=['GET'])
@login_required
def delete_event(id):
    """Delete an event"""
    conn = get_db_connection()

    # Check if this is an instance of a recurring event
    instance_id = request.args.get('instance', '')
    scope = request.args.get('scope', 'all')

    if instance_id and scope == 'single':
        # Add exception for this instance
        instance_date = instance_id.split('_')[-1].split('T')[0]

        event = conn.execute('SELECT exceptions FROM events WHERE id = ?', (id,)).fetchone()
        exceptions = json.loads(event['exceptions']) if event['exceptions'] else []
        exceptions.append(instance_date)

        conn.execute('UPDATE events SET exceptions = ? WHERE id = ?', (json.dumps(exceptions), id))
    elif instance_id and scope == 'future':
        # End the series at this instance
        instance_date = instance_id.split('_')[-1].split('T')[0]

        conn.execute('''
            UPDATE events
            SET recurrence_end = 'on-date',
                recurrence_until = ?
            WHERE id = ?
        ''', (instance_date, id))
    else:
        # Mark the event as deleted
        conn.execute('UPDATE events SET deleted = 1 WHERE id = ?', (id,))

    conn.commit()
    conn.close()

    return redirect(url_for('calendar.calendar'))


@calendar_bp.route('/calendar/db_setup')
@login_required
def setup_db():
    """Set up the database tables for the calendar"""
    conn = get_db_connection()

    # Check if events table exists
    table_exists = conn.execute('''
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='events'
    ''').fetchone()

    if not table_exists:
        conn.execute('''
            CREATE TABLE events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                start_date TEXT NOT NULL,
                start_time TEXT,
                end_date TEXT,
                end_time TEXT,
                category TEXT NOT NULL,
                recurrence TEXT DEFAULT 'none',
                recurrence_interval INTEGER DEFAULT 1,
                recurrence_weekdays TEXT,
                recurrence_end TEXT DEFAULT 'never',
                recurrence_count INTEGER DEFAULT 10,
                recurrence_until TEXT,
                exceptions TEXT,
                exception_to INTEGER,
                exception_date TEXT,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted INTEGER DEFAULT 0
            )
        ''')

        # Create some sample events
        sample_events = [
            (
            'Koosolek', 'Iganädalane tiimi koosolek', '2025-03-10', '09:00', '2025-03-10', '10:00', 'work', 'weekly', 1,
            json.dumps(['1']), 'never', None, None, None, None, None, 1),
            ('Sünnipäev', 'Anna sünnipäev', '2025-03-15', '', '2025-03-15', '', 'family', 'yearly', 1, None, 'never',
             None, None, None, None, None, 1),
            (
            'Arsti visiit', 'Hambaarsti kontroll', '2025-03-12', '14:30', '2025-03-12', '15:30', 'health', 'none', None,
            None, None, None, None, None, None, None, 1)
        ]

        for event in sample_events:
            conn.execute('''
                INSERT INTO events (
                    title, description, start_date, start_time, end_date, end_time, 
                    category, recurrence, recurrence_interval, recurrence_weekdays, 
                    recurrence_end, recurrence_count, recurrence_until, exceptions, 
                    exception_to, exception_date, user_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', event)

        conn.commit()
        message = "Kalendri andmebaas loodud edukalt!"
    else:
        message = "Kalendri andmebaas on juba olemas."

    conn.close()

    return message
    start_time = request.form.get('start_time', '')
    end_date = request.form.get('end_date', start_date)
    end_time = request.form.get('end_time', '')
    category = request.form['category']

    # Recurrence information
    recurrence = request.form.get('recurrence', 'none')
    recurrence_interval = request.form.get('recurrence_interval', 1)
    recurrence_end = request.form.get('recurrence_end', 'never')
    recurrence_count = request.form.get('recurrence_count', 10)
    recurrence_until = request.form.get('recurrence_until', '')

    # Weekdays for weekly recurrence
    weekdays = request.form.getlist('weekdays')
    recurrence_weekdays = json.dumps(weekdays) if weekdays else None

    conn = get_db_connection()
    conn.execute('''
            INSERT INTO events (
                title, 
                description, 
                start_date, 
                start_time, 
                end_date, 
                end_time, 
                category, 
                recurrence,
                recurrence_interval,
                recurrence_weekdays,
                recurrence_end,
                recurrence_count,
                recurrence_until,
                user_id,
                deleted
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        ''', (
        title,
        description,
        start_date,
        start_time,
        end_date,
        end_time,
        category,
        recurrence,
        recurrence_interval,
        recurrence_weekdays,
        recurrence_end,
        recurrence_count,
        recurrence_until,
        current_user.id,
    ))

    conn.commit()
    conn.close()

    return redirect(url_for('calendar.calendar'))


@calendar_bp.route('/calendar/edit_event/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    """Edit an existing event"""
    conn = get_db_connection()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        start_date = request.form['start_date']