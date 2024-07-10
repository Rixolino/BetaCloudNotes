from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)

# Import models after initializing db
from models import Note

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/notes', methods=['POST'])
def add_note():
    data = request.get_json()
    new_note = Note(
        title=data['title'],
        content=data['content']
    )
    db.session.add(new_note)
    db.session.commit()
    return jsonify({"message": "Note added successfully!"})

@app.route('/notes', methods=['GET'])
def get_notes():
    notes = Note.query.all()
    output = []
    for note in notes:
        note_data = {'id': note.id, 'title': note.title, 'content': note.content, 'created_at': note.created_at, 'updated_at': note.updated_at}
        output.append(note_data)
    return jsonify(output)

if __name__ == '__main__':
    if not os.path.exists('notes.db'):
        db.create_all()
    app.run(debug=True)
