import os
from datetime import datetime
from pathlib import Path

from flask import Flask, redirect, url_for, request, flash, render_template, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from blueprints.todo import todo_bp
from blueprints.calendar import calendar_bp
from blueprints.challenges import challenges_bp
from blueprints.food import food_bp
from blueprints.games import games_bp
import sqlite3
import random
import csv

THIS_FOLDER = Path(__file__).parent.resolve()
# Load facts from CSV file
FACTS_FILE = THIS_FOLDER / "all_facts.csv"


def load_facts():
    facts = []
    with open(FACTS_FILE, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            facts.append({"category": row[0], "fact": row[1]})
    return facts


FACTS = load_facts()  # Load facts on startup


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
                    day TEXT NOT NULL UNIQUE,
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

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.register_blueprint(todo_bp)
app.register_blueprint(calendar_bp)
app.register_blueprint(challenges_bp)
app.register_blueprint(food_bp)
app.register_blueprint(games_bp)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id


# Simple in-memory user store
users = {'admin': {'password': '999'}}


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('todo.todo'))
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
    return redirect(url_for('todo.todo'))


@app.route("/random_fact")
def random_fact():
    fact = random.choice(FACTS)
    return jsonify(fact)


if __name__ == '__main__':
    app.run(debug=True)