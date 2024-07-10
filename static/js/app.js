document.addEventListener('DOMContentLoaded', () => {
    const noteForm = document.getElementById('noteForm');
    const showNotesButton = document.getElementById('showNotesButton');

    const fetchAndDisplayNotes = async () => {
        const response = await fetch('/notes');
        const notes = await response.json();

        // Prepara i dati delle note per la visualizzazione
        let notesHtml = '';
        notes.forEach(note => {
            notesHtml += `<div class="note">
                            <h2>${note.title}</h2>
                            <p>${note.content}</p>
                            <small>Utente: ${note.user}</small>
                          </div>`;
        });

        // Salva le note nel localStorage per poterle recuperare in webnotes.html
        localStorage.setItem('notes', JSON.stringify(notes));

        // Redireziona l'utente a webnotes.html
        window.location.href = '/webnotes.html';
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
    });

    showNotesButton.addEventListener('click', fetchAndDisplayNotes);
});
