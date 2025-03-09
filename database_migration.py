import sqlite3


def migrate_database():
    """
    Add position column to todos table if it doesn't exist
    """
    print("Starting database migration...")
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Check if position column exists
    cursor.execute("PRAGMA table_info(todos)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'position' not in columns:
        print("Adding position column to todos table...")

        # Add the position column
        cursor.execute("ALTER TABLE todos ADD COLUMN position INTEGER DEFAULT 0")

        # Initialize position values based on existing rows
        cursor.execute("SELECT id FROM todos WHERE completed = 0 AND deleted = 0 ORDER BY id")
        active_todos = cursor.fetchall()

        for i, (todo_id,) in enumerate(active_todos):
            cursor.execute("UPDATE todos SET position = ? WHERE id = ?", (i, todo_id))

        print(f"Updated position for {len(active_todos)} active todo items")

        # For completed and deleted todos, just set position based on ID to avoid conflicts
        cursor.execute("UPDATE todos SET position = id WHERE completed = 1 OR deleted = 1")

        conn.commit()
        print("Migration completed successfully!")
    else:
        print("Position column already exists, no migration needed.")

    conn.close()


if __name__ == "__main__":
    migrate_database()