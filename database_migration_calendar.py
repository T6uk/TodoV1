import sqlite3


def migrate_calendar_database():
    """
    Create the events table for calendar functionality
    """
    print("Starting calendar database migration...")
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Check if events table exists
    cursor.execute("PRAGMA table_info(events)")
    columns = cursor.fetchall()

    if not columns:
        print("Creating events table...")

        cursor.execute('''
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

        print("Events table created successfully!")

        # Add sample events
        print("Adding sample events...")

        import json
        from datetime import datetime, timedelta

        today = datetime.now()

        sample_events = [
            # Weekly team meeting every Monday at 9am
            (
                'Tiimi koosolek',
                'Iganädalane tiimi koosolek',
                today.strftime('%Y-%m-%d'),
                '09:00',
                today.strftime('%Y-%m-%d'),
                '10:00',
                'work',
                'weekly',
                1,
                json.dumps(['1']),
                'never',
                None,
                None,
                None,
                None,
                None,
                1
            ),

            # Personal event next week
            (
                'Trenni minek',
                'Ujumine',
                (today + timedelta(days=7)).strftime('%Y-%m-%d'),
                '18:00',
                (today + timedelta(days=7)).strftime('%Y-%m-%d'),
                '19:30',
                'health',
                'none',
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                1
            ),

            # Family event
            (
                'Perekonna õhtusöök',
                'Perekonna kohtumine restoranis',
                (today + timedelta(days=3)).strftime('%Y-%m-%d'),
                '19:00',
                (today + timedelta(days=3)).strftime('%Y-%m-%d'),
                '21:00',
                'family',
                'none',
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                1
            ),

            # Monthly recurring event
            (
                'Kuuaruanne',
                'Igakuine aruanne koostamine',
                (today.replace(day=1) + timedelta(days=25)).strftime('%Y-%m-%d'),
                '10:00',
                (today.replace(day=1) + timedelta(days=25)).strftime('%Y-%m-%d'),
                '12:00',
                'work',
                'monthly',
                1,
                None,
                'never',
                None,
                None,
                None,
                None,
                None,
                1
            ),

            # All-day event
            (
                'Tähtpäev',
                'Oluline tähtpäev',
                (today + timedelta(days=14)).strftime('%Y-%m-%d'),
                '',
                (today + timedelta(days=14)).strftime('%Y-%m-%d'),
                '',
                'personal',
                'yearly',
                1,
                None,
                'never',
                None,
                None,
                None,
                None,
                None,
                1
            )
        ]

        cursor.executemany('''
            INSERT INTO events (
                title, description, start_date, start_time, end_date, end_time, 
                category, recurrence, recurrence_interval, recurrence_weekdays, 
                recurrence_end, recurrence_count, recurrence_until, exceptions, 
                exception_to, exception_date, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_events)

        print(f"Added {len(sample_events)} sample events")
    else:
        print("Events table already exists, checking for needed columns...")

        # Check for missing columns
        columns = [column[1] for column in columns]
        missing_columns = []

        if 'recurrence' not in columns:
            missing_columns.append("ADD COLUMN recurrence TEXT DEFAULT 'none'")
        if 'recurrence_interval' not in columns:
            missing_columns.append("ADD COLUMN recurrence_interval INTEGER DEFAULT 1")
        if 'recurrence_weekdays' not in columns:
            missing_columns.append("ADD COLUMN recurrence_weekdays TEXT")
        if 'recurrence_end' not in columns:
            missing_columns.append("ADD COLUMN recurrence_end TEXT DEFAULT 'never'")
        if 'recurrence_count' not in columns:
            missing_columns.append("ADD COLUMN recurrence_count INTEGER DEFAULT 10")
        if 'recurrence_until' not in columns:
            missing_columns.append("ADD COLUMN recurrence_until TEXT")
        if 'exceptions' not in columns:
            missing_columns.append("ADD COLUMN exceptions TEXT")
        if 'exception_to' not in columns:
            missing_columns.append("ADD COLUMN exception_to INTEGER")
        if 'exception_date' not in columns:
            missing_columns.append("ADD COLUMN exception_date TEXT")

        # Add missing columns
        for column_sql in missing_columns:
            print(f"Adding column: {column_sql}")
            cursor.execute(f"ALTER TABLE events {column_sql}")

    conn.commit()
    conn.close()
    print("Calendar database migration completed!")


if __name__ == "__main__":
    migrate_calendar_database()