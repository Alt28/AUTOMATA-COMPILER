@echo off
setlocal enabledelayedexpansion
set PROJ=%~dp0
cd /d "%PROJ%"

if not exist .venv (
  py -3 -m venv .venv
)
call .venv\Scripts\activate.bat

if exist requirements.txt (
  python -m pip install --quiet -r requirements.txt
) else (
  python -m pip install --quiet flask flask-socketio eventlet
)

python server.py
