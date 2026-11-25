@echo off
REM Arranca Uniweb (Django + SQLite) en el puerto 8000.
cd /d "%~dp0"

if not exist venv\Scripts\python.exe (
  echo Creando entorno virtual...
  python -m venv venv
  venv\Scripts\python -m pip install -r requirements.txt
)

venv\Scripts\python manage.py migrate
venv\Scripts\python manage.py runserver 0.0.0.0:8000
