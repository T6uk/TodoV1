import datetime

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
import sqlite3

challenges_bp = Blueprint('challenge', __name__)


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


@challenges_bp.route('/challenges')
@login_required
def challenges():
    return render_template('challenges.html')


# Route to fetch all challenges (JSON response)
@challenges_bp.route('/fetch_challenges', methods=['GET'])
def fetch_challenges():
    conn = get_db_connection()
    challenges = conn.execute('SELECT * FROM challenges').fetchall()
    conn.close()
    # Convert challenges to list of dictionaries
    challenge_list = [{'id': chall['id'], 'name': chall['name'], 'description': chall['description'],
                       'start_time': chall['start_time'], 'end_time': chall['end_time'],
                       'participants': chall['participants'], 'completed': chall['completed'],
                       'deleted': chall['deleted']} for chall in
                      challenges]
    return jsonify(challenge_list)


# Route to fetch a specific challenge details by id
@challenges_bp.route('/fetch_challenge_details/<int:id>', methods=['GET'])
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
            'completed': challenge['completed'],
            'deleted': challenge['deleted'],
            'participants': challenge['participants']
        })
    return jsonify({'message': 'Challenge not found'}), 404


# Route to add a new challenge
@challenges_bp.route('/add_challenge', methods=['POST'])
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
@challenges_bp.route('/edit_challenge/<int:id>', methods=['POST'])
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
@challenges_bp.route('/delete_challenge/<int:id>', methods=['DELETE'])
@login_required
def delete_challenge(id):
    conn = get_db_connection()
    conn.execute("UPDATE challenges SET deleted = 'yes' WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Challenge deleted successfully!"})


# Route to delete a challenge
@challenges_bp.route('/delete_perm_challenge/<int:id>', methods=['DELETE'])
@login_required
def delete_perm_challenge(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM challenges WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Challenge deleted successfully!"})


# Route to check and update completed challenges
@challenges_bp.route('/update_completed_challenges', methods=['POST'])
def update_completed_challenges():
    conn = get_db_connection()
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Update challenges where end_time has passed
    conn.execute("UPDATE challenges SET completed = 'yes' WHERE end_time <= ? AND completed = 'no'", (now,))
    conn.execute("UPDATE challenges SET completed = 'no' WHERE end_time > ? AND completed = 'yes'", (now,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Completed challenges updated!"})
