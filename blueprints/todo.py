from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required
import sqlite3
from datetime import datetime, timedelta

todo_bp = Blueprint('todo', __name__)


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


# Helper functions for date checking
def is_due_soon(date_str):
    """Check if a date is within the next 3 days"""
    if isinstance(date_str, str):
        try:
            # Convert from display format back to date object
            date_obj = datetime.strptime(date_str, '%d. %b %Y').date()
        except ValueError:
            try:
                # Try ISO format as fallback
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return False
    else:
        return False

    today = datetime.now().date()
    return today <= date_obj <= today + timedelta(days=3)


def is_overdue(date_str):
    """Check if a date is in the past"""
    if isinstance(date_str, str):
        try:
            # Convert from display format back to date object
            date_obj = datetime.strptime(date_str, '%d. %b %Y').date()
        except ValueError:
            try:
                # Try ISO format as fallback
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return False
    else:
        return False

    today = datetime.now().date()
    return date_obj < today


@todo_bp.route('/todo', methods=['GET', 'POST'])
@login_required
def todo():
    conn = get_db_connection()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        date = request.form['date']
        by_who = request.form['by_who']
        priority = request.form['priority']

        # Get the highest position value for proper ordering
        max_position = conn.execute('SELECT COALESCE(MAX(position), 0) FROM todos').fetchone()[0]

        conn.execute(
            'INSERT INTO todos (name, description, date, by_who, priority, deleted, position) VALUES (?, ?, ?, ?, ?, 0, ?)',
            (name, description, date, by_who, priority, max_position + 1)
        )
        conn.commit()

    def fetch_and_format(query):
        todos = conn.execute(query).fetchall()
        formatted_todos = []
        for todo in todos:
            todo_dict = dict(todo)
            # Store original date for comparison
            todo_dict['raw_date'] = todo_dict['date']
            if isinstance(todo_dict['date'], str):
                try:
                    # Format date for display
                    todo_dict['date'] = datetime.strptime(todo_dict['date'], '%Y-%m-%d').strftime('%d. %b %Y')
                except ValueError:
                    pass  # Keep original format if parsing fails
            formatted_todos.append(todo_dict)
        return formatted_todos

    # Retrieve todos ordered by position for active todos
    active_todos = fetch_and_format('SELECT * FROM todos WHERE completed = 0 AND deleted = 0 ORDER BY position')
    completed_todos = fetch_and_format('SELECT * FROM todos WHERE completed = 1 AND deleted = 0')
    deleted_todos = fetch_and_format('SELECT * FROM todos WHERE deleted = 1')

    conn.close()
    tab = request.args.get('tab', 'active-todos')

    # Pass helper functions to the template
    return render_template(
        'todo.html',
        tab=tab,
        todos=active_todos,
        completed_todos=completed_todos,
        deleted_todos=deleted_todos,
        is_due_soon=is_due_soon,
        is_overdue=is_overdue
    )


@todo_bp.route('/complete_todo/<int:id>')
@login_required
def complete_todo(id):
    conn = get_db_connection()
    conn.execute('UPDATE todos SET completed = 1 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    tab = request.args.get('tab', 'active-todos')
    return redirect(url_for('todo.todo', tab=tab))


@todo_bp.route('/delete_todo/<int:id>')
@login_required
def delete_todo(id):
    conn = get_db_connection()
    conn.execute('UPDATE todos SET deleted = 1 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    tab = request.args.get('tab', 'completed-todos')
    return redirect(url_for('todo.todo', tab=tab))


@todo_bp.route('/restore_todo/<int:id>')
@login_required
def restore_todo(id):
    conn = get_db_connection()
    conn.execute('UPDATE todos SET deleted = 0 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    tab = request.args.get('tab', 'deleted-todos')
    return redirect(url_for('todo.todo', tab=tab))


@todo_bp.route('/permanent_delete_todo/<int:id>')
@login_required
def permanent_delete_todo(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM todos WHERE id = ?', (id,))
    conn.commit()
    tab = request.args.get('tab', 'deleted-todos')
    return redirect(url_for('todo.todo', tab=tab))


@todo_bp.route('/edit_todo', methods=['POST'])
@login_required
def edit_todo():
    todo_id = request.form['id']
    name = request.form['name']
    description = request.form['description']
    date = request.form['date']
    by_who = request.form['by_who']
    priority = request.form['priority']

    conn = get_db_connection()
    conn.execute('''
        UPDATE todos 
        SET name = ?, description = ?, date = ?, by_who = ?, priority = ?
        WHERE id = ?
    ''', (name, description, date, by_who, priority, todo_id))
    conn.commit()
    conn.close()

    return redirect(url_for('todo.todo'))


# New routes for bulk actions
@todo_bp.route('/bulk_complete', methods=['POST'])
@login_required
def bulk_complete():
    todo_ids = request.form.get('todo_ids', '')
    if todo_ids:
        ids = [int(id_) for id_ in todo_ids.split(',')]
        placeholders = ','.join(['?'] * len(ids))

        conn = get_db_connection()
        conn.execute(f'UPDATE todos SET completed = 1 WHERE id IN ({placeholders})', ids)
        conn.commit()
        conn.close()

    return redirect(url_for('todo.todo', tab='active-todos'))


@todo_bp.route('/bulk_delete', methods=['POST'])
@login_required
def bulk_delete():
    todo_ids = request.form.get('todo_ids', '')
    source_tab = request.form.get('source_tab', 'active-todos')

    if todo_ids:
        ids = [int(id_) for id_ in todo_ids.split(',')]
        placeholders = ','.join(['?'] * len(ids))

        conn = get_db_connection()
        conn.execute(f'UPDATE todos SET deleted = 1 WHERE id IN ({placeholders})', ids)
        conn.commit()
        conn.close()

    return redirect(url_for('todo.todo', tab=source_tab))


@todo_bp.route('/bulk_restore', methods=['POST'])
@login_required
def bulk_restore():
    todo_ids = request.form.get('todo_ids', '')
    if todo_ids:
        ids = [int(id_) for id_ in todo_ids.split(',')]
        placeholders = ','.join(['?'] * len(ids))

        conn = get_db_connection()
        conn.execute(f'UPDATE todos SET deleted = 0 WHERE id IN ({placeholders})', ids)
        conn.commit()
        conn.close()

    return redirect(url_for('todo.todo', tab='deleted-todos'))


@todo_bp.route('/bulk_permanent_delete', methods=['POST'])
@login_required
def bulk_permanent_delete():
    todo_ids = request.form.get('todo_ids', '')
    if todo_ids:
        ids = [int(id_) for id_ in todo_ids.split(',')]
        placeholders = ','.join(['?'] * len(ids))

        conn = get_db_connection()
        conn.execute(f'DELETE FROM todos WHERE id IN ({placeholders})', ids)
        conn.commit()
        conn.close()

    return redirect(url_for('todo.todo', tab='deleted-todos'))


@todo_bp.route('/update_priority', methods=['POST'])
@login_required
def update_priority():
    data = request.json
    todo_id = data.get('todo_id')
    new_position = data.get('new_position')

    if not todo_id or new_position is None:
        return jsonify({"success": False, "error": "Missing parameters"}), 400

    conn = get_db_connection()
    try:
        # Get all active todos
        active_todos = conn.execute(
            'SELECT id FROM todos WHERE completed = 0 AND deleted = 0 ORDER BY position'
        ).fetchall()

        # Create a new ordered list based on the drag-and-drop action
        todo_ids = [row['id'] for row in active_todos]
        todo_id = int(todo_id)

        # Remove the todo from its current position and insert at new position
        if todo_id in todo_ids:
            todo_ids.remove(todo_id)
            todo_ids.insert(new_position, todo_id)

        # Update all positions
        for i, id_ in enumerate(todo_ids):
            conn.execute('UPDATE todos SET position = ? WHERE id = ?', (i, id_))

        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()