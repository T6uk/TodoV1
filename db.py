import sqlite3


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_food_db_connection():
    conn = sqlite3.connect('food_list.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_food_db():
    conn = sqlite3.connect('food_list.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS foods (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        category TEXT NOT NULL,
                        type TEXT NOT NULL
                 )''')
    c.execute('''CREATE TABLE IF NOT EXISTS meal_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    day TEXT NOT NULL,
                    breakfast TEXT,
                    lunch TEXT,
                    dinner TEXT,
                    snack TEXT
                )''')
    conn.commit()
    conn.close()


def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            by_who TEXT NOT NULL,
            priority TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0,
            deleted BOOLEAN NOT NULL DEFAULT 0
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS calendar_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL,  -- Only the date is stored
            color TEXT,
            eventOwner TEXT NOT NULL
        )
    ''')
    conn.execute(''' 
        CREATE TABLE IF NOT EXISTS challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            start_time TIMESTAMP,  -- The start time of the challenge
            end_time TIMESTAMP,    -- The end time of the challenge
            completed TEXT NOT NULL DEFAULT 'no',
            deleted TEXT NOT NULL DEFAULT 'no',
            participants TEXT      -- A comma-separated list of participants (or store as JSON)
        )
    ''')
    conn.commit()
    conn.close()


init_db()
init_food_db()
