document.addEventListener('DOMContentLoaded', () => {
    const noteForm = document.getElementById('noteForm');
    const showNotesLink = document.getElementById('showNotesLink');

    const fetchAndDisplayNotes = async () => {
        const response = await fetch('/notes');
        const notes = await response.json();

        // Salva le note nel localStorage per poterle recuperare in webnotes.html
        localStorage.setItem('notes', JSON.stringify(notes));

        // Redireziona l'utente a webnotes.html in una nuova scheda del browser
        window.open('/webnotes.html', '_blank');
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

    // Usa un link anziché un pulsante per reindirizzare
    showNotesLink.addEventListener('click', fetchAndDisplayNotes);
});
