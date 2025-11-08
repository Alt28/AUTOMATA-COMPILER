# Grow A Language - Local Test Guide

This project includes a small Flask + Socket.IO backend and a web UI (Monaco editor + xterm) to test the lexer and simulate program runs.
The lexer supports line comments with both `//` and `#`, and block comments with `/* ... */`.

## 1) Install Python dependencies

```powershell
# In the project folder
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install flask flask-socketio simple-websocket
```

Notes:
- `flask-socketio` needs a websocket backend; `simple-websocket` is the pure-Python option included above.

## 2) Start the backend

```powershell
python .\server.py
```

This serves `index.html` and provides APIs:

## 3) Open the UI

Navigate to:

Option A — PowerShell (recommended on Windows):

1) Open PowerShell in the project folder
```
cd "c:\Users\clarence\Downloads\my GAL code"
```
2) One command start (creates venv, installs deps from requirements.txt, runs)
```
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

Option B — Double-click batch file:

1) In File Explorer, double-click `start.bat`

Option C — Manual

```
py -3 -m venv .venv
 .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python .\server.py
```

App will be available at http://localhost:5000

## 4) Try a quick test

- Paste this sample into the editor:

```
root(){
  sprout ~3; // sample line comment
  bud 'X';
}
```

- Click “Lexical” to see tokens in the right-hand table and any errors in the terminal.
- Click “Run” to stream example output in the terminal.

## 5) CLI testing (optional)

The lexer can be run standalone:

```powershell
python .\GALalexer.py -c "root(){ sprout ~3; }"
```

Human-readable format:
```powershell
python .\GALalexer.py -c "root(){ sprout ~3; }" --no-json
```

## Troubleshooting
- Ensure the virtual environment is active before installing and running.
- If Socket.IO doesn’t connect, verify the backend is running on port 5000 and that your browser is not blocking mixed content.
- If dependencies are missing, reinstall: `pip install flask flask-socketio simple-websocket`.

## Language notes
- Comments supported by the lexer:
  - Line comments starting with `//` or `#` (continue to the end of the line)
  - Block comments using `/* ... */`