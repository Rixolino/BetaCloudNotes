from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Route per la homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route per la pagina webnotes
@app.route('/webnotes.html')
def webnotes():
    return render_template('webnotes.html')

# Simulazione dei dati delle note
notes = [
    {'user': 'Simone', 'title': 'Nota 1', 'content': 'Contenuto della nota 1'},
    {'user': 'Simone', 'title': 'Nota 2', 'content': 'Contenuto della nota 2'},
    {'user': 'Simone', 'title': 'Nota 3', 'content': 'Contenuto della nota 3'},
]

# Route per ottenere le note
@app.route('/notes')
def get_notes():
    return jsonify(notes)

# Route per aggiungere una nota
@app.route('/notes', methods=['POST'])
def add_note():
    data = request.get_json()
    notes.append(data)
    return jsonify({'message': 'Nota aggiunta'})

if __name__ == '__main__':
    app.run(debug=True)
