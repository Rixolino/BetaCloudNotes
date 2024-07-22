@echo off

cd /workspaces/BetaCloudNotes/

set FLASK_APP=app.py
set FLASK_ENV=development

flask run
