from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id


# This is a simple in-memory user store. Replace with a database in production.
users = {'admin': {'password': '999'}}


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


# Database setup
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_food_db_connection():
    conn = sqlite3.connect('food_list.db')
    conn.row_factory = sqlite3.Row
    return conn


# Ensure the database and table exist
def init_food_db():
    conn = sqlite3.connect('food_list.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS foods (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        category TEXT NOT NULL,
                        type TEXT NOT NULL
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
            participants TEXT      -- A comma-separated list of participants (or store as JSON)
        )
    ''')
    conn.commit()
    conn.close()


init_db()
init_food_db()


# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Vale kasutajanimi või parool!')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    return redirect(url_for('todo'))


@app.route('/todo', methods=['GET', 'POST'])
@login_required
def todo():
    conn = get_db_connection()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        date = request.form['date']
        by_who = request.form['by_who']
        priority = request.form['priority']

        conn.execute(
            'INSERT INTO todos (name, description, date, by_who, priority, deleted) VALUES (?, ?, ?, ?, ?, 0)',
            (name, description, date, by_who, priority)
        )
        conn.commit()

    # Fetch and format data
    def fetch_and_format(query):
        todos = conn.execute(query).fetchall()
        formatted_todos = []
        for todo in todos:
            todo_dict = dict(todo)
            # Check if the date is a string and needs to be formatted
            if isinstance(todo_dict['date'], str):
                todo_dict['date'] = datetime.strptime(todo_dict['date'], '%Y-%m-%d').strftime('%d. %b %Y')
            formatted_todos.append(todo_dict)
        return formatted_todos

    active_todos = fetch_and_format('SELECT * FROM todos WHERE completed = 0 AND deleted = 0')
    completed_todos = fetch_and_format('SELECT * FROM todos WHERE completed = 1 AND deleted = 0')
    deleted_todos = fetch_and_format('SELECT * FROM todos WHERE deleted = 1')

    conn.close()

    tab = request.args.get('tab', 'active-todos')
    return render_template(
        'todo.html',
        tab=tab,
        todos=active_todos,
        completed_todos=completed_todos,
        deleted_todos=deleted_todos
    )


@app.route('/complete_todo/<int:id>')
@login_required
def complete_todo(id):
    conn = get_db_connection()
    conn.execute('UPDATE todos SET completed = 1 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    tab = request.args.get('tab', 'active-todos')
    return redirect(url_for('todo', tab=tab))


@app.route('/delete_todo/<int:id>')
@login_required
def delete_todo(id):
    conn = get_db_connection()
    conn.execute('UPDATE todos SET deleted = 1 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    tab = request.args.get('tab', 'completed-todos')
    return redirect(url_for('todo', tab=tab))


@app.route('/restore_todo/<int:id>')
@login_required
def restore_todo(id):
    conn = get_db_connection()
    conn.execute('UPDATE todos SET deleted = 0 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    tab = request.args.get('tab', 'deleted-todos')
    return redirect(url_for('todo', tab=tab))


@app.route('/permanent_delete_todo/<int:id>')
@login_required
def permanent_delete_todo(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM todos WHERE id = ?', (id,))
    conn.commit()
    tab = request.args.get('tab', 'deleted-todos')
    return redirect(url_for('todo', tab=tab))


@app.route('/edit_todo', methods=['POST'])
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

    return redirect(url_for('todo'))


@app.route('/calendar')
@login_required
def calendar():
    conn = get_db_connection()
    events = conn.execute('SELECT * FROM calendar_events').fetchall()
    conn.close()

    formatted_events = []
    for event in events:
        # Determine the background color based on the event owner
        if event['eventOwner'] == 'Eliis':
            backgroundColor = 'pink'
        elif event['eventOwner'] == 'Romet':
            backgroundColor = 'blue'
        else:
            backgroundColor = 'green'

        formatted_events.append({
            'id': event['id'],
            'title': event['title'],
            'start': event['date'],  # Only the date is used
            'backgroundColor': backgroundColor,
            'extendedProps': {
                'description': event['description'],
                'eventOwner': event['eventOwner']
            }
        })

    return render_template('calendar.html', events=formatted_events)


@app.route('/add_event', methods=['POST'])
@login_required
def add_event():
    data = request.get_json()  # Use JSON data instead of form data
    title = data['title']
    description = data['description']
    date = data['date']
    eventOwner = data['eventOwner']

    # Determine the color based on the event owner
    if eventOwner == 'Eliis':
        color = 'pink'
    elif eventOwner == 'Romet':
        color = 'blue'
    else:
        color = 'green'

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO calendar_events (title, description, date, color, eventOwner)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, description, date, color, eventOwner))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Event added successfully'}), 200


@app.route('/edit_event/<int:id>', methods=['POST'])
@login_required
def edit_event(id):
    data = request.get_json()  # Use JSON data instead of form data
    title = data['title']
    description = data['description']
    date = data['date']
    eventOwner = data['eventOwner']

    # Determine the color based on the event owner
    if eventOwner == 'Eliis':
        color = 'pink'
    elif eventOwner == 'Romet':
        color = 'blue'
    else:
        color = 'green'

    conn = get_db_connection()
    conn.execute('''
        UPDATE calendar_events
        SET title = ?, description = ?, date = ?, color = ?, eventOwner = ?
        WHERE id = ?
    ''', (title, description, date, color, eventOwner, id))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Event updated successfully'}), 200


@app.route('/delete_event/<int:id>')
@login_required
def delete_event(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM calendar_events WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Event deleted successfully'}), 200


# Homepage (Lifestyle Page)
@app.route('/lifestyle')
def lifestyle():
    return render_template('lifestyle.html')


# Routes for challenges
# Route to render the challenge page (HTML)
@app.route('/challenges')
@login_required
def challenges():
    return render_template('challenges.html')


# Route to fetch all challenges (JSON response)
@app.route('/fetch_challenges', methods=['GET'])
def fetch_challenges():
    conn = get_db_connection()
    challenges = conn.execute('SELECT * FROM challenges').fetchall()
    conn.close()
    # Convert challenges to list of dictionaries
    challenge_list = [{'id': chall['id'], 'name': chall['name'], 'description': chall['description'],
                       'start_time': chall['start_time'], 'end_time': chall['end_time'],
                       'participants': chall['participants']} for chall in
                      challenges]
    return jsonify(challenge_list)


# Route to fetch a specific challenge details by id
@app.route('/fetch_challenge_details/<int:id>', methods=['GET'])
@login_required
def fetch_challenge_details(id):
    conn = get_db_connection()
    challenge = conn.execute('SELECT * FROM challenges WHERE id = ?', (id,)).fetchone()
    conn.close()
    if challenge:
        return jsonify({
            'id': challenge['id'],
            'name': challenge['name'],
            'description': challenge['description'],
            'start_time': challenge['start_time'],
            'end_time': challenge['end_time'],
            'participants': challenge['participants']
        })
    return jsonify({'message': 'Challenge not found'}), 404


# Route to add a new challenge
@app.route('/add_challenge', methods=['POST'])
@login_required
def add_challenge():
    data = request.get_json()
    name = data['name']
    description = data['description']
    start_time = data['start_time']
    end_time = data['end_time']
    participants = data['participants']

    conn = get_db_connection()
    conn.execute('INSERT INTO challenges (name, description, start_time, end_time, participants) '
                 'VALUES (?, ?, ?, ?, ?)', (name, description, start_time, end_time, participants))
    conn.commit()
    conn.close()

    return jsonify({"message": "Challenge added successfully!"}), 201


# Route to edit a challenge
@app.route('/edit_challenge/<int:id>', methods=['POST'])
@login_required
def edit_challenge(id):
    data = request.get_json()
    name = data['name']
    description = data['description']
    start_time = data['start_time']
    end_time = data['end_time']
    participants = data['participants']

    conn = get_db_connection()
    conn.execute('UPDATE challenges SET name = ?, description = ?, start_time = ?, end_time = ?, participants = ? '
                 'WHERE id = ?', (name, description, start_time, end_time, participants, id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Challenge updated successfully!"})


# Route to delete a challenge
@app.route('/delete_challenge/<int:id>', methods=['DELETE'])
@login_required
def delete_challenge(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM challenges WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Challenge deleted successfully!"})


@app.route('/food')
@login_required
def food():
    conn = get_food_db_connection()
    foods = conn.execute('SELECT * FROM foods').fetchall()
    conn.close()
    food_names = [food['name'] for food in foods]  # Extract food names for the frontend
    return render_template('food.html', foods=foods, food_names=food_names)


@app.route('/add_food', methods=['POST'])
@login_required
def add_food():
    name = request.form.get('name')
    category = request.form.get('category')
    food_type = request.form.get('type')

    if name and category and food_type:
        conn = get_food_db_connection()
        conn.execute('INSERT INTO foods (name, category, type) VALUES (?, ?, ?)',
                     (name, category, food_type))
        conn.commit()
        conn.close()
    return redirect(url_for('food'))


@app.route('/delete_food/<int:id>', methods=['POST'])
@login_required
def delete_food(id):
    conn = get_food_db_connection()
    conn.execute('DELETE FROM foods WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('food'))


# Route to get foods based on category and type from the database
@app.route('/get_foods/<category>/<food_type>')
@login_required
def get_foods(category, food_type):
    conn = get_food_db_connection()
    c = conn.cursor()

    query = "SELECT * FROM foods WHERE 1=1"

    # Add filters to the query if category/type is provided
    if category != 'all':
        query += " AND category = ?"
    if food_type != 'all':
        query += " AND type = ?"

    params = []
    if category != 'all':
        params.append(category)
    if food_type != 'all':
        params.append(food_type)

    c.execute(query, params)
    foods = c.fetchall()
    conn.close()

    # Convert rows to list of dictionaries
    foods_list = [dict(food) for food in foods]

    return jsonify(foods_list)

if __name__ == '__main__':
    app.run(debug=True)
