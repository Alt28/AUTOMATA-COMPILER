---
title: GAL Compiler
emoji: 🌱
colorFrom: green
colorTo: yellow
sdk: docker
pinned: false
---

# GAL Compiler

A web-based compiler for the GAL (Grow A Language) programming language with lexical analysis, parsing, and semantic checking.

https://clarkoer-gal.hf.space/

## Features

- **Lexical Analysis** - Tokenizes GAL source code
- **Syntax Analysis** - LL(1) parsing with error recovery
- **Semantic Analysis** - Type checking and variable scope validation
- **Web Interface** - Built-in code editor with syntax highlighting
- **Real-time Feedback** - Instant error detection and reporting

## Installation

1. **Clone or download** this project

2. **Install Python dependencies:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

## Running the Compiler

### Option A: one-command start on Windows

PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

Command Prompt:

```bat
start.bat
```

The script creates `.venv`, installs `requirements.txt`, and starts the server.

### Option B: manual start

1. **Create and activate a virtual environment:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. **Install dependencies:**
   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

3. **Start the server:**
   ```powershell
   python Backend/server.py
   ```

4. **Open your browser:**
   ```
   http://localhost:5000
   ```

## Quick Start Example

Paste this code into the editor:

```gal
root(){
  sprout ~3;
  seed x = 10;
  bud 'Hello';
}
```

Click **"Analyze"** to see the lexical tokens, syntax tree, and semantic analysis results.

## Language Syntax

GAL supports:

- **Comments:** `//` line comments or `/* */` block comments
- **Keywords:** `root`, `sprout`, `seed`, `bud`, `plant`, `grow`, `harvest`
- **Data Types:** Integers, characters (single quotes), strings (double quotes)
- **Operators:** `+`, `-`, `*`, `/`, `~` (negate)
- **Control Flow:** Function calls and basic expressions

## Troubleshooting

**Port already in use?**
- Make sure no other application is using port 5000
- Or modify the port in `Backend/server.py`

**Dependencies not installing?**
- Ensure Python 3.8+ is installed
- Try: `pip install --upgrade pip` then reinstall dependencies

**Page not loading?**
- Verify the server is running (check terminal output)
- Try accessing `http://127.0.0.1:5000` instead
