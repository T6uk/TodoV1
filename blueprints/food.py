import csv
import random

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required
import sqlite3

food_bp = Blueprint('food', __name__)


def get_food_db_connection():
    conn = sqlite3.connect('food_list.db')
    conn.row_factory = sqlite3.Row
    return conn


@food_bp.route('/food')
@login_required
def food():
    conn = get_food_db_connection()
    foods = conn.execute('SELECT * FROM foods').fetchall()
    conn.close()
    food_names = [food['name'] for food in foods]  # Extract food names for the frontend
    return render_template('food.html', foods=foods, food_names=food_names)


@food_bp.route('/add_food', methods=['POST'])
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
    return redirect(url_for('food.food'))


@food_bp.route('/delete_food/<int:id>', methods=['POST'])
@login_required
def delete_food(id):
    conn = get_food_db_connection()
    conn.execute('DELETE FROM foods WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('food.food'))


# Route to get foods based on category and type from the database
@food_bp.route('/get_foods/<category>/<food_type>')
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


@food_bp.route('/save_meal_plan', methods=['POST'])
@login_required
def save_meal_plan():
    data = request.get_json()
    print("🔹 Received meal plan data:", data)  # Debugging

    if not data or "mealPlan" not in data:
        return jsonify({"message": "Invalid data received"}), 400

    conn = get_food_db_connection()
    c = conn.cursor()

    try:
        for entry in data["mealPlan"]:
            print(f"🔹 Processing entry: {entry}")  # Debugging
            c.execute("""
                INSERT INTO meal_plans (day, breakfast, lunch, dinner, snack)
                VALUES (?, COALESCE(?, ''), COALESCE(?, ''), COALESCE(?, ''), COALESCE(?, ''))
                ON CONFLICT(day) DO UPDATE SET
                breakfast = COALESCE(excluded.breakfast, meal_plans.breakfast),
                lunch = COALESCE(excluded.lunch, meal_plans.lunch),
                dinner = COALESCE(excluded.dinner, meal_plans.dinner),
                snack = COALESCE(excluded.snack, meal_plans.snack)
            """, (entry["day"], entry["breakfast"], entry["lunch"], entry["dinner"], entry["snack"]))
        conn.commit()

        # 🔹 Fetch and print database content after saving
        c.execute("SELECT * FROM meal_plans")
        all_rows = c.fetchall()
        print("🔹 Database state after saving:", all_rows)

        return jsonify({"message": "Meal plan updated successfully"})

    except Exception as e:
        print("❌ Error saving meal plan:", str(e))
        return jsonify({"message": "Error saving meal plan"}), 500

    finally:
        conn.close()


@food_bp.route('/get_meal_plan', methods=['GET'])
@login_required
def get_meal_plan():
    conn = get_food_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM meal_plans")
    meal_plan = c.fetchall()

    # If table is empty, return default empty plan
    if not meal_plan:
        meal_plan_list = [
            {"day": day, "breakfast": None, "lunch": None, "dinner": None, "snack": None}
            for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        ]
    else:
        meal_plan_list = [
            {
                "day": row["day"],
                "breakfast": row["breakfast"],
                "lunch": row["lunch"],
                "dinner": row["dinner"],
                "snack": row["snack"]
            }
            for row in meal_plan
        ]

    conn.close()
    return jsonify(meal_plan_list)
