# Grow A Language - guide

This project includes a small Flask + Socket.IO backend and a web UI (Monaco editor + xterm) to test the lexer and simulate program runs.
The lexer supports line comments with both `//` and `#`, and block comments with `/* ... */`.


<img src="./docs/screenshots/lexer-view.png" alt="The compiler" width="1911" height="861" />



## 1) Install Python dependencies (local dev)

```powershell
# In the project folder
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Notes:
- No eventlet/gevent required. The server runs Socket.IO in threading mode for maximum Windows compatibility.

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

If you use VS Code Live Server

- You can still click “Go Live” to serve `index.html` on port 5500. The frontend now auto-routes API calls and Socket.IO to the Flask backend on port 5000 if it detects a different origin.
- Just make sure the Python server is running (use `start.ps1`), then open the page via Live Server.

### Docker (alternative quick start)

Build and run the container:

```powershell
docker build -t gal-web .
docker run --rm -p 5000:5000 gal-web
```

Then open: http://localhost:5000

Override port (example 8080):

```powershell
docker run --rm -e PORT=8080 -p 8080:8080 gal-web
```

Set debug mode (not recommended in production):

```powershell
docker run --rm -e DEBUG=true -p 5000:5000 gal-web
```

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

## 6) Basic integration test

From another shell while the server runs:

```powershell
Invoke-RestMethod -Uri http://localhost:5000/health
Invoke-RestMethod -Method Post -Uri http://localhost:5000/api/lex -ContentType 'application/json' -Body '{"source_code":"root(){ seed x = 10; }"}' | ConvertTo-Json -Depth 4
```

You should see `status: ok` and a JSON object containing `tokens` and `meta`.

Safe mode (force fallback lexer):

```powershell
Invoke-RestMethod -Method Post -Uri 'http://localhost:5000/api/lex?safeMode=1' -ContentType 'application/json' -Body '{"source_code":"seed x = 1; plant(x);"}' | ConvertTo-Json -Depth 4
```
Expect `meta.lexer` to be `fallback` if the built-in fallback ran.

Scripted integration test (Python):

```powershell
python .\tests\integration_lex.py
```

## Troubleshooting
- Ensure the virtual environment is active before installing and running.
- If Socket.IO doesn’t connect, verify the backend is running on port 5000 and that your browser is not blocking mixed content.
- If dependencies are missing, reinstall with: `pip install -r requirements.txt`.
- On Windows, the server forces Socket.IO to use `threading` for maximum compatibility; you don't need eventlet or gevent.

## Language notes
- Comments supported by the lexer:
  - Line comments starting with `//` or `#` (continue to the end of the line)

  - Block comments using `/* ... */`
