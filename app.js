document.addEventListener('DOMContentLoaded', () => {
    const noteForm = document.getElementById('noteForm');
    const notesDiv = document.getElementById('notes');

    const fetchNotes = async () => {
        const response = await fetch('/notes');
        const notes = await response.json();
        notesDiv.innerHTML = '';
        notes.forEach(note => {
            const noteElement = document.createElement('div');
            noteElement.classList.add('note');
            noteElement.innerHTML = `<h2>${note.title}</h2><p>${note.content}</p><small>${new Date(note.created_at).toLocaleString()}</small>`;
            notesDiv.appendChild(noteElement);
        });
    }

    noteForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const title = document.getElementById('title').value;
        const content = document.getElementById('content').value;

        await fetch('/notes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title, content })
        });

        noteForm.reset();
        fetchNotes();
    });

    fetchNotes();
});
