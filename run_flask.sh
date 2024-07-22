#!/bin/sh

# Assicurati di essere nella directory del progetto
cd "$(dirname "$0")"

# Esporta le variabili di ambiente
export FLASK_APP=app.py
export FLASK_ENV=development

# Esegui il server Flask
flask run
