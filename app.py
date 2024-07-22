from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_socketio import SocketIO
from datetime import datetime
import hashlib
import os
import pickle

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()  # Secret key for session management
socketio = SocketIO(app)

# Global variables for storing notes and user data
notes = []
next_id = 1  # Counter for note IDs
users = {}  # Dictionary to store registered users
user_profiles = {}  # Dictionary to store user profiles

blacklist = set()  # Use a set for fast lookups

# Load blacklist from file (optional)
def load_blacklist():
    global blacklist
    try:
        with open('blacklist.dat', 'rb') as f:
            blacklist = pickle.load(f)
    except FileNotFoundError:
        blacklist = set()

# Save blacklist to file (optional)
def save_blacklist():
    with open('blacklist.dat', 'wb') as f:
        pickle.dump(blacklist, f)

# Load blacklist at startup
load_blacklist()


# Function to load data from the file
def load_data():
    global users, user_profiles, notes, next_id
    try:
        with open('data.dat', 'rb') as f:
            users, user_profiles, notes, next_id = pickle.load(f)
    except FileNotFoundError:
        users = {}
        user_profiles = {}
        notes = []
        next_id = 1
    except Exception as e:
        print(f"Error loading data: {e}")
        users = {}
        user_profiles = {}
        notes = []
        next_id = 1

# Function to save data to the file
def save_data():
    with open('data.dat', 'wb') as f:
        pickle.dump((users, user_profiles, notes, next_id), f)

# Load data at startup
load_data()

# Route for the homepage
@app.route('/')
def index():
    return render_template('main.html')

@app.route('/webnotes')
def webnotes():
    return render_template('webnotes.html')

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Check if the username is blacklisted
        if username in blacklist:
            return jsonify({'message': 'This account has been deleted and cannot be used to log in.'}), 403
        
        if username in users and users[username] == hashed_password:
            session['username'] = username
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'message': 'Login failed'}), 401
    
    return render_template('login.html')


# Route for the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']

        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Check if the username is blacklisted
        if username in blacklist:
            return jsonify({'message': 'This username has been blacklisted and cannot be used for registration.'}), 403
        
        if username in users:
            return jsonify({'message': 'Username already exists'}), 400
        if password != confirm_password:
            return jsonify({'message': 'Passwords do not match'}), 400
        
        users[username] = hashed_password
        user_profiles[username] = {
            'username': username,
            'email': f'{username}@example.com',  # Example default email
            'joined': datetime.now()
        }
        save_data()  # Save data after registration
        return jsonify({'message': 'Registration successful'}), 200
    
    return render_template('register.html')


# Route for the user profile page
@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    if username not in user_profiles:
        user_profiles[username] = {
            'username': username,
            'email': f'{username}@example.com',  # Example default email
            'joined': datetime.now()
        }
    
    return render_template('profile.html', profile=user_profiles[username])

# Route to update the user profile
@app.route('/update-profile', methods=['PUT'])
def update_profile():
    if 'username' not in session:
        return jsonify({'message': 'User not authenticated'}), 401
    
    username = session['username']
    data = request.get_json()
    
    # Update email if provided
    if 'email' in data:
        user_profiles[username]['email'] = data['email']
    
    # Update username if provided and different
    if 'username' in data and data['username'] != username:
        new_username = data['username']
        
        if new_username in user_profiles:
            return jsonify({'message': 'Username already exists'}), 400
        
        # Copy the profile to the new username
        user_profiles[new_username] = user_profiles.pop(username)
        user_profiles[new_username]['username'] = new_username  # Update the username in the profile
        session['username'] = new_username  # Update the username in the session
        
        # Update notes to reflect the new username
        for note in notes:
            if note['user'] == username:
                note['user'] = new_username
        
        save_data()  # Save data after updating profile
        return jsonify({'message': f'Welcome, {new_username}! Profile updated successfully.'}), 200
    
    save_data()  # Save data after updating profile
    return jsonify({'message': 'Profile updated successfully.'}), 200

# Route for logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

# Route to get notes
@app.route('/notes', methods=['GET'])
def get_notes():
    return jsonify(notes)

# Route to add a note
@app.route('/notes', methods=['POST'])
def add_note():
    global next_id
    data = request.get_json()
    current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    note = {
        'id': next_id,
        'user': session.get('username'),
        'title': data['title'],
        'content': data['content'],
        'date': current_time
    }
    notes.append(note)
    next_id += 1
    save_data()  # Save data after adding a note
    return jsonify({'message': 'Note added successfully'}), 201

# Route to edit a note
@app.route('/notes/<int:id>', methods=['PUT'])
def edit_note(id):
    note = next((note for note in notes if note['id'] == id), None)
    if note is None:
        return jsonify({'message': 'Note not found'}), 404

    if note['user'] != session.get('username'):
        return jsonify({'message': 'You do not have permission to edit this note'}), 403

    data = request.get_json()
    note['content'] = data.get('content', note['content'])
    save_data()  # Save data after editing a note
    return jsonify({'message': 'Note updated successfully'}), 200

# Route to delete a note
@app.route('/notes/<int:id>', methods=['DELETE'])
def delete_note(id):
    global notes
    note = next((note for note in notes if note['id'] == id), None)
    if note is None:
        return jsonify({'message': 'Note not found'}), 404

    if note['user'] != session.get('username'):
        return jsonify({'message': 'You do not have permission to delete this note'}), 403

    notes = [note for note in notes if note['id'] != id]
    save_data()  # Save data after deleting a note
    return jsonify({'message': 'Note deleted successfully'}), 200

@app.route('/delete-profile', methods=['DELETE'])
def delete_profile():
    if 'username' not in session:
        return jsonify({'message': 'User not authenticated'}), 401
    
    username = session['username']
    
    if username in users:
        del users[username]  # Remove from main users dictionary
        
        # Add username to blacklist
        blacklist.add(username)
        save_blacklist()  # Save blacklist to file
        
        # Delete the user-specific file if applicable
        if os.path.exists(f'{username}.dat'):
            os.remove(f'{username}.dat')
        
        # Logout the user
        session.pop('username', None)
        
        return jsonify({'message': 'Profile deleted successfully.'}), 200
    
    return jsonify({'message': 'Profile not found.'}), 404


if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)