---
title: GAL Compiler
emoji: 🌱
colorFrom: green
colorTo: yellow
sdk: docker
pinned: false
---

# GAL Compiler

GAL Compiler is a web-based compiler and interpreter for the GAL
(Grow A Language) programming language. It includes a browser editor, lexical
analysis, LL(1) syntax analysis, AST building, semantic validation,
intermediate-code generation, program execution, and an optional Gemini-powered
AI assistant.

Live app:

```text
https://clarkoer-gal.hf.space/
```

## Features

- Lexical analysis with token table output
- LL(1) parser using CFG, FIRST, FOLLOW, and PREDICT sets
- AST builder and semantic validation
- Runtime interpreter for `root()`, functions, variables, arrays, loops,
  conditionals, input, and output
- Web editor with syntax highlighting and run modes
- Socket.IO execution for interactive `water()` input
- Optional AI chatbot using Gemini with offline fallback help

## Project Structure

```text
my GAL code/
  Backend/
    server.py              Flask + Socket.IO API entry point
    lexer/                 Scanner, tokens, delimiters, lexical errors
    parser/                LL(1) parser and AST builder
    cfg/                   Grammar, FIRST sets, PREDICT sets
    semantic/              Semantic analyzer
    interpreter/           Runtime interpreter
    ai/                    Gemini prompt and fallback chatbot replies
  UI/
    index.html             Browser interface
    main.js                Editor actions and API calls
    style.pixel.css        UI styling
  requirements.txt         Python dependencies
  start.ps1                Windows PowerShell starter
  start.bat                Windows Command Prompt starter
  Dockerfile               Hugging Face Spaces / Docker deployment
```

## Requirements

- Python 3.10 or newer is recommended.
- Git, if cloning from GitHub.
- A browser such as Chrome, Edge, or Firefox.
- Optional: Gemini API key for the AI assistant.

The backend dependencies are listed in `requirements.txt`:

```text
flask
flask-socketio
flask-cors
eventlet
google-genai
sentence-transformers
numpy
```

## Local Setup on Windows

### Option A: One-command start

PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

Command Prompt:

```bat
start.bat
```

The script creates `.venv`, activates it, installs `requirements.txt`, sets
`PORT=5000` when no port is provided, and starts `Backend/server.py`.

Then open:

```text
http://localhost:5000
```

### Option B: Manual start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python Backend/server.py
```

Then open:

```text
http://localhost:5000
```

## Local Setup on macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python Backend/server.py
```

Then open:

```text
http://localhost:5000
```

## Environment Variables

The system reads environment variables directly from the operating system.
It does not automatically load a `.env` file.

| Variable | Required | Purpose | Default |
|---|---:|---|---|
| `PORT` | No | Backend server port | `5000` locally, `7860` in Docker |
| `DEBUG` | No | Enables Flask debug mode when set to `True` | `False` |
| `GEMINI_API_KEY` | No | Enables Gemini AI chatbot mode | empty / fallback mode |

### Set Gemini API Key on Windows PowerShell

```powershell
$env:GEMINI_API_KEY="your_gemini_api_key_here"
python Backend/server.py
```

### Set Gemini API Key on Command Prompt

```bat
set GEMINI_API_KEY=your_gemini_api_key_here
python Backend\server.py
```

### Set Gemini API Key on macOS or Linux

```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
python Backend/server.py
```

Do not commit your real API key to GitHub.

If `GEMINI_API_KEY` is missing, the compiler still runs. The AI chatbot will use
the local fallback replies instead of Gemini.

## Hugging Face Spaces Setup

This repository uses Docker for Hugging Face Spaces. The Space reads the port
from the Dockerfile:

```text
PORT=7860
```

To enable Gemini on Hugging Face:

1. Open your Hugging Face Space.
2. Go to **Settings**.
3. Open **Repository secrets**.
4. Add this secret:

```text
GEMINI_API_KEY=your_gemini_api_key_here
```

5. Restart or rebuild the Space.

Without this secret, the compiler still works, but the chatbot returns fallback
answers.

## Running the System

When the server starts successfully, it prints API endpoints similar to:

```text
Server running at http://0.0.0.0:5000
POST http://localhost:5000/api/lex
POST http://localhost:5000/api/parse
POST http://localhost:5000/api/semantic
POST http://localhost:5000/api/icg
POST http://localhost:5000/api/chat
Socket.IO: run_code
```

Open the browser at:

```text
http://localhost:5000
```

The Flask backend serves the `UI` folder directly, so you do not need a separate
frontend server.

## API Endpoints

All main compiler endpoints receive JSON.

### Health Check

```http
GET /api/health
```

Returns a simple server status response.

### Lexical Analysis

```http
POST /api/lex
Content-Type: application/json

{
  "source_code": "root() { reclaim; }"
}
```

Returns lexer tokens and lexical errors.

### Syntax Analysis

```http
POST /api/parse
Content-Type: application/json

{
  "source_code": "root() { reclaim; }"
}
```

Runs lexer first, then LL(1) parser.

### Semantic Analysis

```http
POST /api/semantic
Content-Type: application/json

{
  "source_code": "root() { seed x = 1; reclaim; }"
}
```

Runs lexer, parser, AST builder, and semantic validator.

### Intermediate Code Generation

```http
POST /api/icg
Content-Type: application/json

{
  "source_code": "root() { seed x = 1; reclaim; }"
}
```

Runs the compiler stages needed for intermediate-code generation.

### Full Run / Execution

```http
POST /api/run
Content-Type: application/json

{
  "source_code": "root() { plant(\"Hello Garden!\"); reclaim; }"
}
```

Runs the full non-interactive pipeline:

```text
source code -> lexer -> parser/builder -> semantic analyzer -> interpreter
```

### AI Chat

```http
POST /api/chat
Content-Type: application/json

{
  "message": "How do I create an array?",
  "session_id": "default",
  "editor_code": ""
}
```

If `GEMINI_API_KEY` is set, this uses Gemini. If not, it uses the local fallback
AI responses.

### Clear AI Chat Session

```http
POST /api/chat/clear
Content-Type: application/json

{
  "session_id": "default"
}
```

Clears the stored chat history for that session.

## Socket.IO Runtime Events

Interactive execution uses Socket.IO so `water()` input can pause and resume.

| Event | Direction | Purpose |
|---|---|---|
| `connect` | browser -> server | Opens a runtime session |
| `disconnect` | browser -> server | Ends a runtime session |
| `run_code` | browser -> server | Runs source code interactively |
| `output` | server -> browser | Sends `plant()` output or runtime messages |
| `input_required` | server -> browser | Requests input for `water()` |
| `capture_input` | browser -> server | Sends user input back to interpreter |
| `execution_complete` | server -> browser | Tells UI the run finished |

## Quick Start GAL Program

Paste this into the editor and click **Run**:

```gal
root() {
    seed x = 10;
    seed y = 5;
    seed sum;

    sum = x + y;

    plant("Sum:", sum);
    reclaim;
}
```

Expected output:

```text
Sum: 15
```

## Interactive Input Example

```gal
root() {
    seed a;
    seed b;
    seed sum;

    plant("Enter first number:");
    water(a);

    plant("Enter second number:");
    water(b);

    sum = a + b;
    plant("Sum:", sum);

    reclaim;
}
```

When the program reaches `water(a)` or `water(b)`, the UI asks for input.

## Language Overview

Common GAL keywords:

| GAL keyword | Meaning |
|---|---|
| `root` | Main function |
| `pollinate` | Function declaration |
| `reclaim` | Return / end function |
| `seed` | Integer type |
| `tree` | Double/float type |
| `leaf` | Character type |
| `vine` | String type |
| `branch` | Boolean type |
| `plant` | Output |
| `water` | Input |
| `spring` | If |
| `bud` | Else-if |
| `wither` | Else |
| `cultivate` | For loop |
| `grow` | While loop |
| `tend` | Do-while loop |
| `harvest` | Switch |
| `variety` | Case |
| `soil` | Default |
| `prune` | Break |
| `skip` | Continue |
| `bundle` | Struct-like type |
| `fertile` | Constant |

## Troubleshooting

### Could not connect to server

Make sure the backend is running:

```powershell
python Backend/server.py
```

Then open:

```text
http://localhost:5000
```

If you opened the UI with VS Code Live Server on another port, the UI will try
to call:

```text
http://localhost:5000
```

So the Flask backend must still be running on port `5000`.

### Port already in use

Use another port:

PowerShell:

```powershell
$env:PORT="5001"
python Backend/server.py
```

Command Prompt:

```bat
set PORT=5001
python Backend\server.py
```

Then open:

```text
http://localhost:5001
```

### PowerShell script cannot run

Use:

```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

### Gemini chatbot only gives fallback answers

Check that the key is set in the same terminal where the server starts:

```powershell
echo $env:GEMINI_API_KEY
```

Then restart:

```powershell
python Backend/server.py
```

### Dependencies fail to install

Upgrade pip and reinstall:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Hugging Face push rejected because of binary files

Large generated PDFs or binary files should not be pushed directly to Hugging
Face unless the Space/repository uses Git LFS or Xet storage. Keep source files,
code, and small documentation in Git, and avoid committing large generated
artifacts when possible.
