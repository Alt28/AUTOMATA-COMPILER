# GAL Compiler — Defense-Prep Walkthrough

## File 1 of 7: `server.py`

This is the entry point of the entire GAL compiler system. Every panel question about "how does my system actually run a program" starts here.

---

## 1. FILE PURPOSE

`server.py` is the **HTTP and WebSocket server** of the GAL compiler. It is the bridge between the browser-based frontend (the IDE the user types code in) and the Python backend (lexer, parser, semantic analyzer, ICG, interpreter).

Its job is:

1. **Receive** GAL source code from the frontend (either as a one-shot HTTP POST, or as a `run_code` Socket.IO event for interactive runs).
2. **Drive the compiler pipeline** stage by stage, in this fixed order:
   `lex → parse → AST → semantic → (optionally) ICG → interpret`.
3. **Stop at the first failing stage** and return a structured error response that tells the frontend *which* stage failed and *what* the errors were.
4. **Stream program output** back to the user in real time (via Socket.IO) when the program is actually running, and **collect input** from the user when the program calls `water()`.
5. **Serve the static UI** files (HTML/CSS/JS) so the whole thing works as one app.

Where it sits in the pipeline:

```
  Browser (UI/index.html)
      │  POST /api/lex, /api/parse, /api/semantic, /api/icg, /api/run
      │  WebSocket: run_code, capture_input
      ▼
  ┌─────────── server.py ──────────────┐
  │  Flask + Socket.IO + eventlet      │
  │                                    │
  │  Calls:                            │
  │    lexer.lex()                     │
  │    LL1Parser.parse() / .parse_and_build()
  │    GALsemantic.validate_ast()      │
  │    icg.generate_icg()              │
  │    GALinterpreter.Interpreter()    │
  └────────────────────────────────────┘
```

What depends on it: nothing inside the backend depends on `server.py`. Everything else (lexer, parser, etc.) is **library code** that `server.py` orchestrates. That separation is intentional — the lexer doesn't know it's running on a server, which means you could run the compiler from a CLI, a unit test, or a different web framework without modifying any of the language code.

---

## 2. IMPORTS / DEPENDENCIES

```python
import warnings
warnings.filterwarnings("ignore", message=".*RLock.*were not greened.*")

import eventlet
eventlet.monkey_patch()
```

- **`warnings.filterwarnings(...)`** — silences a cosmetic warning that `eventlet` emits during startup about thread locks. It's irrelevant to behavior; we just don't want it cluttering the console during a demo.
- **`eventlet`** + **`eventlet.monkey_patch()`** — this is the *cooperative concurrency* layer. `monkey_patch()` rewrites Python's standard library (sockets, threading, time) to use eventlet's green threads instead of OS threads. We need this because:
  - Socket.IO must support many simultaneous WebSocket connections without blocking.
  - When the interpreter calls `water()` and waits for input, it can't block the whole server — eventlet lets the server park that one request and keep handling others.
  - **If you remove these lines:** Socket.IO will silently fall back to a less reliable mode and `water()` may deadlock the server during a demo.

```python
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
```

- **`Flask`** — the web framework. `Flask(__name__, ...)` creates the app object that handles all HTTP routes.
- **`request`** — gives access to the incoming HTTP request body (used in every endpoint via `request.get_json()`).
- **`jsonify`** — builds JSON responses with the right `Content-Type` header.
- **`send_from_directory`** — serves the static UI files (HTML, CSS, JS, images) from the `UI/` folder.
- **`CORS`** — Cross-Origin Resource Sharing. Lets the browser frontend talk to the backend even if served from a different port during development.
- **`SocketIO, emit`** — bidirectional WebSocket support. `emit()` is what we use to push output back to the browser in real time during program execution.

```python
import os
from google import genai
```

- **`os`** — used for environment variables (e.g., `GEMINI_API_KEY`, `PORT`) and joining file paths.
- **`genai`** — Google Gemini SDK, used by the AI chat-helper feature (the `/api/chat` endpoint). This is **not part of the compiler**; it's an optional helper.

```python
from lexer import lex, get_token_description
from Gal_Parser import LL1Parser
from cfg import cfg, first_sets, predict_sets
from GALsemantic import analyze_semantics, validate_ast
from icg import generate_icg
from GALinterpreter import Interpreter, InterpreterError, _CancelledError
from gal_fallback import fallback_reply
```

These are **the seven layers of your compiler**, each imported here so `server.py` can call them in order:

| Import | What it is | Stage |
|---|---|---|
| `lex` | Function that turns source text into a list of tokens | Lexical |
| `get_token_description` | Maps a token type to its human-readable label (for the lexeme table in the UI) | Lexical (display) |
| `LL1Parser` | The LL(1) table-driven parser class | Syntax |
| `cfg, first_sets, predict_sets` | The grammar (productions) and pre-computed FIRST/PREDICT sets the parser uses | Syntax |
| `analyze_semantics` | Legacy entry point — runs the full lex→parse→semantic flow in one call | Semantic |
| `validate_ast` | Tree-walking semantic validator that runs **after** the parser has built the AST | Semantic |
| `generate_icg` | Produces three-address code (TAC) for display purposes | ICG |
| `Interpreter` | The tree-walking interpreter that actually runs the program | Execution |
| `InterpreterError, _CancelledError` | Custom exceptions raised during execution | Execution |
| `fallback_reply` | Rule-based AI helper response used when Gemini is unavailable | Helper (not pipeline) |

**`analyze_semantics` may be possibly unused at the server layer** — the server uses `validate_ast` instead, which is the newer two-step API (`parse_and_build` then `validate_ast`). The legacy `analyze_semantics` function is still imported but I do not see a direct call to it in this file. Mark this for verification before defense — it is harmless to leave imported.

---

## 3. GLOBAL CONSTANTS / VARIABLES

```python
app = Flask(__name__, static_folder='../UI', static_url_path='')
```

The Flask application object. `static_folder='../UI'` tells Flask "static files live one folder up, in the UI directory." This is what lets `send_from_directory('../UI', 'index.html')` serve the IDE's HTML page.

```python
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
```

Wraps the Flask app with CORS support and Socket.IO. `cors_allowed_origins="*"` means any browser can connect — fine for a local development tool, but you would tighten this in production.

```python
interpreters = {}
```

This is the **per-session interpreter registry**. The dictionary maps a Socket.IO session ID (`sid`) to the `Interpreter` instance currently running for that user. Critical because:

- One user can have only one program running at a time.
- When the user clicks "Run" again while a program is still waiting on input, the server cancels the old interpreter (`old_interp._cancelled = True`) before starting a new one.
- When the user disconnects, we pop their entry so memory doesn't leak.

```python
parser = LL1Parser(
    cfg=cfg,
    predict_sets=predict_sets,
    first_sets=first_sets,
    start_symbol="<program>",
    end_marker="EOF",
    skip_token_types={'\n'}
)
```

The parser instance is built **once** at server startup and reused for every request. This is a deliberate optimization:

- Building a parser involves loading the grammar dictionary (`cfg`) and the predict-set table — heavy work.
- The parser itself is **stateless** during parsing (each call to `parser.parse(tokens)` works on its own input), so it's safe to share across requests.
- `skip_token_types={'\n'}` is the **token-filtering rule** — the parser will silently skip newline tokens during parsing. Newlines are produced by the lexer for line tracking but they have no role in GAL grammar.

This single line answers a likely panel question: *"Where does the parser skip newlines?"* — right here.

```python
_prompt_path = os.path.join(os.path.dirname(__file__), 'gal_prompt.txt')
with open(_prompt_path, 'r', encoding='utf-8') as _f:
    GAL_SYSTEM_PROMPT = _f.read()

_gemini_client = None
_chat_sessions = {}
```

These globals belong to the AI chat-helper feature only — not the compiler. `GAL_SYSTEM_PROMPT` is the system prompt loaded from disk that teaches Gemini about the GAL language. `_chat_sessions` holds conversation history per session.

---

## 4. CLASSES AND FUNCTIONS

There are three classes/helpers and a long list of route handlers. I'll group them.

### Helper: `_display_value(val)` — lines 20-28

```python
def _display_value(val):
    """Escape special chars in token values for safe display (like C's repr)."""
    if val is None:
        return ''
    s = str(val)
    s = s.replace('\n', '\\n')
    s = s.replace('\t', '\\t')
    s = s.replace('\r', '\\r')
    return s
```

**What it does:** Turns a token's raw value into a safe display string. A `\n` character becomes the two-character string `\n` so it doesn't break the JSON or the lexeme table in the UI.

**When it is called:** Every time the server converts a list of `Token` objects into JSON-serializable dicts (in `/api/lex`, `/api/parse`, `/api/semantic`, `/api/icg`).

**Why it exists:** Without it, a literal newline in a token value would be embedded directly into JSON and break the table rendering or make it visually empty.

### Class: `SessionEmitter` — lines 38-45

```python
class SessionEmitter:
    """Wrapper around SocketIO that always emits to a specific client session."""
    def __init__(self, sio, sid):
        self._sio = sio
        self._sid = sid
    def emit(self, event, data=None, **kwargs):
        self._sio.emit(event, data, to=self._sid, **kwargs)
```

**What it is:** A thin wrapper around the Socket.IO object that "remembers" a single client session ID.

**Why it exists:** The interpreter calls `self.socketio.emit('output', {...})` to print things. But the interpreter doesn't know which Socket.IO session it belongs to. By passing a `SessionEmitter(sio, sid)` to the interpreter constructor, the interpreter can call `.emit(...)` and the emitter handles the routing — guaranteeing output goes to the right user, not broadcast to everyone connected.

**Compiler stage:** Execution / runtime I/O.

### Class: `OutputCollector` — lines 347-358

```python
class OutputCollector:
    """Drop-in replacement for SessionEmitter that collects output in a list."""
    def __init__(self):
        self.outputs = []
        self.needs_input = False

    def emit(self, event, data=None, **kwargs):
        if event == 'output' and data:
            self.outputs.append(data.get('output', ''))
        elif event == 'input_required':
            self.needs_input = True
            raise _InputNeeded()  # Abort interpreter when input is needed
```

**What it is:** Same shape as `SessionEmitter` (it has an `.emit()` method), but instead of forwarding events to Socket.IO, it **collects output in a list**.

**Why it exists:** The HTTP `/api/run` endpoint runs a program synchronously and returns all output in one response — it doesn't have a live Socket.IO connection to stream to. `OutputCollector` lets us reuse the same `Interpreter` class without changes. This is a classic **adapter pattern**.

**Edge case:** If the program calls `water()` (input), `OutputCollector` raises `_InputNeeded` to abort — because there's no way to deliver an interactive prompt over a one-shot HTTP request.

### Exception: `_InputNeeded` — lines 361-363

```python
class _InputNeeded(Exception):
    pass
```

A private sentinel exception used only inside this file, raised by `OutputCollector` and caught by `/api/run` to know that "this program needs input we can't provide here."

### Route handlers: `/`, `/<path>`, `/images/<path>` — lines 65-78

```python
@app.route('/')
def index():
    return send_from_directory('../UI', 'index.html')
```

These three routes serve the **frontend** — the IDE itself. When you visit `http://localhost:5000/`, this hands back `index.html` from the UI folder. The other two routes serve CSS, JS, and images.

### Route handler: `/api/lex` — lines 80-119

This is the **Lexical Analysis endpoint**. It runs the lexer and returns the tokens in JSON. This is what the IDE calls when the user clicks "Lex" or "Tokenize." Detailed explanation in section 5 below.

### Route handler: `/api/parse` — lines 121-182

The **Syntax Analysis endpoint**. Runs lex → parse and returns success/errors. Detailed below.

### Route handler: `/api/semantic` — lines 192-263

The **Semantic Analysis endpoint**. Runs lex → parse → AST → semantic and returns the symbol table. Detailed below.

### Route handler: `/api/icg` — lines 265-342

The **Intermediate Code Generation endpoint**. Runs lex → parse → semantic → ICG and returns TAC instructions for display. Detailed below.

### Route handler: `/api/run` — lines 365-446

The **synchronous execution endpoint** (no Socket.IO needed). Runs the entire pipeline including the interpreter, returns all output in one HTTP response. Used for non-interactive programs.

### Socket.IO handlers: `connect`, `disconnect`, `run_code`, `capture_input` — lines 451-554

These power the **live, interactive execution** flow. Detailed below.

### Route handlers: `/api/chat`, `/api/chat/clear` — lines 578-659

The AI chat helper. Calls Google Gemini, falls back to a rule-based reply if no API key. **Not part of the compiler pipeline** — purely a learning aid for users.

### `if __name__ == '__main__':` — lines 662-675

The startup block. Reads the `PORT` env var, prints a banner showing each API endpoint, and runs the server on `0.0.0.0` so it's reachable from any browser on the local network.

---

## 5. LINE-BY-LINE / BLOCK-BY-BLOCK EXPLANATION

I'll cover the most important blocks. The four endpoints `/api/lex`, `/api/parse`, `/api/semantic`, `/api/run` and the Socket.IO `run_code` handler form the heart of the file — every panel question about pipeline order traces back to these.

### 5.1 Eventlet bootstrap

```python
import warnings
warnings.filterwarnings("ignore", message=".*RLock.*were not greened.*")

import eventlet
eventlet.monkey_patch()
```

**What this block does:** Replaces Python's blocking I/O primitives with eventlet's cooperative ones, so the server can handle many simultaneous WebSocket connections without spawning OS threads.

**Why this logic is needed:** The `run_code` flow uses `socketio.start_background_task(run_interpreter)` (line 544), which schedules the interpreter to run on a green thread. If eventlet weren't monkey-patched, `wait_for_input()` inside the interpreter would block the whole event loop and freeze every user.

**What happens next:** The rest of the file imports Flask and registers routes; by the time any request arrives, eventlet is already in charge.

**Defense answer:** *"Eventlet provides cooperative concurrency. We monkey-patch the standard library so that `water()` (input-waiting) and Socket.IO event loops both yield to each other instead of blocking. Without it, two users running programs simultaneously would freeze each other."*

### 5.2 The `parser` global initialization

```python
parser = LL1Parser(
    cfg=cfg,
    predict_sets=predict_sets,
    first_sets=first_sets,
    start_symbol="<program>",
    end_marker="EOF",
    skip_token_types={'\n'}
)
```

**What this block does:** Constructs **one** parser instance reused for every request.

**Why it is needed:** Building the parser involves loading the entire grammar (`cfg`) and the parsing table (`predict_sets`). If we did this on every request, every parse would pay a heavy startup cost.

**Why `skip_token_types={'\n'}`:** This is the answer to "where do skipped tokens get filtered?" The parser silently ignores newlines during shift operations — they exist only to help the lexer report line numbers in errors.

**What data is being changed:** A module-level `parser` reference is created, ready to be called.

**Defense answer:** *"The parser is constructed once at startup. The grammar and predict-set tables are loaded into memory and reused. Since LL(1) parsing is stateless across calls, this is safe and faster than rebuilding it per request."*

### 5.3 `/api/lex` — the lexical analysis endpoint

```python
@app.route('/api/lex', methods=['POST'])
def lexer_endpoint():
    try:
        data = request.get_json()

        if not data or 'source_code' not in data:
            return jsonify({'error': 'Missing source_code in request body'}), 400

        source_code = data['source_code']

        # Run the lexer
        tokens, errors = lex(source_code)

        # Convert tokens to serializable format
        token_list = []
        for token in tokens:
            token_list.append({
                'type': token.type,
                'value': _display_value(token.value),
                'line': token.line,
                'col': getattr(token, 'col', 0),
                'description': get_token_description(token.type, token.value)
            })

        return jsonify({
            'tokens': token_list,
            'errors': errors
        })

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500
```

**Block-by-block:**

1. `request.get_json()` parses the incoming HTTP body as JSON. The frontend sends `{"source_code": "<the text>"}`.
2. `if not data or 'source_code' not in data` is the **input-validation guard**. Returns HTTP 400 (Bad Request) if the request is malformed.
3. `tokens, errors = lex(source_code)` — calls the **lexer** layer. `lex` is the public function in `lexer.py` that internally constructs a `Lexer` and calls `make_tokens()`. It returns `(tokens, errors)` — both lists.
4. The `for token in tokens` loop **flattens** each `Token` object into a JSON-friendly dict. `getattr(token, 'col', 0)` defends against tokens that didn't get a column attribute (e.g., synthetic EOF tokens).
5. `get_token_description(token.type, token.value)` adds a human-readable label like "Integer Literal" for the IDE's lexeme table.
6. `return jsonify(...)` sends the result back to the browser.
7. `except Exception` is the **safety net** — any uncaught exception in the pipeline becomes an HTTP 500 with an error message instead of a server crash. This is crucial for demos: a buggy GAL program shouldn't take down the server.

**What data is being changed:** None on the server. The endpoint is read-only — it produces a response from the input.

**Defense answer:** *"The lex endpoint accepts source code in the request body, runs the lexer to produce a token stream, converts the tokens into JSON, and returns them. Any exception is caught and returned as a structured error so the IDE can display it cleanly."*

### 5.4 `/api/parse` — syntax analysis

```python
# First, run the lexer to get tokens
tokens, lex_errors = lex(source_code)
...
# Only run the parser if there are no lexical errors
if lex_errors:
    return jsonify({
        'success': False,
        'tokens': token_list,
        'errors': lex_errors,
        'stage': ['lexical'],
        'lexical_errors': True,
        'syntax_errors': False
    })

parse_success, parse_errors = parser.parse(tokens)
```

**The critical line:** *"Only run the parser if there are no lexical errors."* This is the **early-exit pattern** that runs through every endpoint. Each stage's input is the previous stage's clean output, so if the lexer failed, parsing meaningless tokens would just produce confusing additional errors. By short-circuiting, we tell the user exactly which stage is broken.

**`parser.parse(tokens)`** is the **legacy** parser entry that returns just `(success, errors)` — no AST. Used here because `/api/parse` only checks syntax, not structure.

**Defense answer:** *"This endpoint runs lex first, and only proceeds to parsing if the lexer reported no errors. If parsing fails, the response says `stage: ['syntax']` so the IDE highlights the right phase."*

### 5.5 `/api/semantic` — semantic analysis

```python
# Run the parser — validates syntax (LL1) then builds AST
parse_result = parser.parse_and_build(tokens)

# If syntax or AST construction failed, return errors
if not parse_result['success']:
    error_stage = parse_result.get('error_stage', 'syntax')
    return jsonify({
        'success': False,
        'tokens': token_list,
        'errors': parse_result['errors'],
        'warnings': [],
        'stage': error_stage
    })

# Run semantic analysis — tree-walking validation of the AST
semantic_result = validate_ast(parse_result['ast'], parse_result['symbol_table'])
```

**The key shift:** This endpoint uses **`parse_and_build`** (not just `parse`). `parse_and_build` does parsing **and** AST construction in one call. This is because some semantic errors are detected during AST construction itself (e.g., undeclared variables in expressions), so the parser's `error_stage` may already be `'semantic'` even though the parser called the failure.

**`validate_ast(ast, symbol_table)`** is a separate **tree-walking pass** that catches errors not visible during AST building (function-return-type mismatches, control-flow rules, etc.). It returns success/errors/warnings/symbol_table.

**Defense answer:** *"Semantic analysis happens in two places: some checks during AST construction (because the parser already knows the variable being declared), and some in `validate_ast` afterwards (because they need the full tree to be visible — like checking that a function actually returns a value of its declared type). The `error_stage` field tells the frontend which sub-phase complained."*

### 5.6 `/api/icg` — intermediate code generation

```python
# 4. Intermediate code generation
icg_result = generate_icg(tokens)
```

**Important:** ICG is generated from **tokens**, not from the AST. This is a deliberate choice — your ICG runs as a parallel pass over the token stream rather than walking the AST. This is fine because **the interpreter does NOT consume the ICG output**; ICG exists purely as a display artifact for the IDE's "Intermediate Code" tab.

**Defense answer:** *"Intermediate code generation runs as a parallel pass on the token stream after semantic analysis succeeds. Its only consumer is the IDE — the interpreter walks the AST directly. So ICG is a teaching/visualization layer, not a runtime layer."*

### 5.7 `/api/run` — synchronous execution endpoint

```python
collector = OutputCollector()
interp = Interpreter(socketio=collector)
try:
    interp.interpret(ast)
    return jsonify({'success': True, ..., 'output': collector.outputs})
except _InputNeeded:
    return jsonify({'success': False, ..., 'needs_input': True})
except InterpreterError as e:
    collector.outputs.append(f'Runtime Error: {e}')
    return jsonify({'success': False, ..., 'errors': [str(e)]})
```

**The clever part:** Instead of giving the interpreter a real Socket.IO emitter, we give it `OutputCollector`. The interpreter doesn't know the difference — it calls `.emit('output', ...)` exactly the same way. This is the **adapter pattern**, and it's what lets one `Interpreter` class serve both interactive (Socket.IO) and synchronous (HTTP) modes.

**The three exception layers:**
- `_InputNeeded` — program tried to call `water()`, so we tell the frontend "switch to interactive mode."
- `InterpreterError` — a clean runtime error from the interpreter (like division by zero). We append the message to the output list and report failure.
- `Exception` — anything unexpected. Reported as "Internal Error" so it's clear this was not the program's fault.

**Defense answer:** *"The synchronous run endpoint reuses the same Interpreter class as the live mode by swapping in an OutputCollector that captures output instead of streaming it. If the program needs input, we abort and tell the client to switch to the interactive Socket.IO flow."*

### 5.8 Socket.IO `run_code` — interactive execution

```python
@socketio.on('run_code')
def handle_run_code(data):
    sid = request.sid
    source_code = data.get('source_code', '')

    # 1. Lexical analysis
    tokens, lex_errors = lex(source_code)
    if lex_errors:
        for err in lex_errors:
            emit('output', {'output': f'Lexical Error: {err}'})
        emit('execution_complete', {'success': False, 'stage': 'lexical'})
        return
    emit('stage_complete', {'stage': 'lexical', 'success': True})

    # 2. Parse + AST
    parse_result = parser.parse_and_build(tokens)
    ...
    # 3. Semantic
    semantic_result = validate_ast(parse_result['ast'], parse_result['symbol_table'])
    ...
    # 4. Interpretation in background task
```

**Why a background task:** The interpreter may block on `water()` for tens of seconds. We must not block the WebSocket event loop while waiting, so we run the interpreter inside `socketio.start_background_task(run_interpreter)`.

**The cancellation block:**

```python
old_interp = interpreters.get(sid)
if old_interp and hasattr(old_interp, '_cancelled'):
    old_interp._cancelled = True
    for evt in list(old_interp.input_events.values()):
        try:
            evt.send(None)   # eventlet.event.Event uses .send()
        except (AttributeError, AssertionError):
            try:
                evt.set()
            except Exception:
                pass
```

This handles the case where the user clicks "Run" again while a previous program is still waiting on input. We:
1. Set `_cancelled = True` so the old interpreter knows to exit on its next checkpoint.
2. Unblock any pending input event so the old thread isn't stuck forever waiting for input that will never come.
3. The `try/except` chain handles both eventlet and threading flavors of `Event` because the codebase has used both at different times.

**Stage events:** After each successful stage, we emit `stage_complete` with the stage name. The frontend uses these to update the visual pipeline indicator.

**Defense answer:** *"The interactive run handler sends back stage_complete events as each stage finishes, so the IDE shows real-time progress. If the user runs the program again while it's still waiting for input, we cancel the old run cleanly so we don't leak interpreters."*

### 5.9 `capture_input` — receive input from the client

```python
@socketio.on('capture_input')
def handle_capture_input(data):
    sid = request.sid
    interp = interpreters.get(sid)
    if interp:
        var_name = data.get('var_name', '')
        input_value = data.get('input', '')
        interp.provide_input(var_name, input_value)
```

**What this does:** When the running program calls `water(varName)`, the interpreter blocks on `wait_for_input(var_name)` and the frontend shows an input box. When the user types and submits, the frontend emits `capture_input`, this handler receives it, looks up the right interpreter via session ID, and calls `interp.provide_input(...)` which unblocks the waiting interpreter.

**Defense answer:** *"Input flows back to the right interpreter via the session-keyed `interpreters` dictionary. The interpreter parks on an event; the frontend sends the typed value; we route it back and the interpreter resumes."*

### 5.10 Server startup

```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False') != 'True'
    print("Starting GAL Compiler Server...")
    ...
    socketio.run(app, host='0.0.0.0', port=port, debug=debug, allow_unsafe_werkzeug=True)
```

`host='0.0.0.0'` means the server is reachable from any network interface, not just localhost. `allow_unsafe_werkzeug=True` is required for newer Flask versions to run inside the eventlet WSGI server during development.

---

## 6. DEFENSE QUESTION PREPARATION

**Q: Why did you separate the compiler into stages with different endpoints?**

> "Each endpoint corresponds to a single phase of the compilation pipeline: lex, parse, semantic, ICG, run. This lets the IDE display the output of one phase at a time without forcing a full execution. It also means each phase can be tested in isolation. The endpoints share a strict early-exit pattern: each stage runs only if the previous one succeeded."

**Q: Where in `server.py` is token filtering done before parsing?**

> "Token filtering is configured at parser construction time, line 54: `skip_token_types={'\n'}`. The LL1Parser internally skips any token whose type is in that set during shift operations. We don't manually strip newlines from the token list — the parser handles it transparently."

**Q: How does the server distinguish a syntax error from a semantic error during parsing?**

> "When `parse_and_build` runs, it can fail with either a syntax error (the LL(1) table didn't accept the next token) or a semantic error caught during AST construction (e.g., a redeclared variable). The parser sets `error_stage` in its return value. The server reads that field on line 239 and 307 to label the response correctly."

**Q: What happens if the GAL program has a runtime error like division by zero?**

> "The interpreter raises an `InterpreterError`. In `/api/run` it's caught at line 428; in the Socket.IO `run_code` handler it's caught inside `run_interpreter` at line 531. We emit a `Runtime Error: …` line via the same output channel and an `execution_complete` event with `success: False`."

**Q: What if two users run programs at the same time?**

> "Each user has a unique Socket.IO session ID. The `interpreters` dictionary maps `sid → Interpreter`. Eventlet monkey-patching ensures that when one interpreter blocks on `water()`, the server keeps handling other users' requests. They don't share state."

**Q: Why does the interpreter accept a `socketio` argument but the synchronous `/api/run` endpoint passes an `OutputCollector` instead?**

> "Both implement the same `.emit(event, data)` interface. The `Interpreter` class doesn't care whether output is being streamed over WebSockets or collected into a list — that's the adapter pattern. It keeps the interpreter independent of the I/O layer."

**Q: If the lexer fails, why don't you still run the parser to find more errors?**

> "Because the parser would be reading tokens that may not represent the user's intent. If a quote was unclosed, half the file became one giant string-literal token, and parsing it would produce a flood of nonsense errors that hide the real problem. Stopping early gives the user one clear lexical error to fix."

**Q: Where does the AST get built? In the parser or in semantic?**

> "Both ways exist. The newer flow uses `parser.parse_and_build(tokens)` which validates syntax with the LL(1) table AND simultaneously calls into `GALsemantic.build_ast` to construct the tree. Then `validate_ast` runs as a separate tree-walking pass for checks that need the whole tree. This two-step model is why the server distinguishes `error_stage = 'syntax'` from `error_stage = 'semantic'` even though both can come from the same parser call."

**Q: What is `analyze_semantics` and why is it imported?**

> "It's the legacy entry point that runs lex→parse→AST→semantic in one call. We don't use it directly in the server anymore — we call `parse_and_build` and `validate_ast` separately so the IDE can report which sub-stage failed. The import remains for backwards compatibility with grading scripts and CLI tests."

**Q: How does the IDE know which stage failed?**

> "Every error response includes a `stage` field. The frontend reads it and highlights the matching pipeline indicator: lexical, syntax, semantic, icg, or execution. Each stage also emits a `stage_complete` Socket.IO event when it succeeds, so the UI animates progress in real time."

---

## 7. SIMPLE WALKTHROUGH EXAMPLE

Sample GAL code:

```
root() {
    seed age = 10;
    plant(age);
    reclaim;
}
```

How this code travels through `server.py`:

### Step 1 — Frontend → Server

The user clicks "Run" in the IDE. The frontend opens (or reuses) a Socket.IO connection and emits:

```
event: run_code
data: { source_code: "root() {\n    seed age = 10;\n    plant(age);\n    reclaim;\n}" }
```

This triggers `handle_run_code(data)` at line 461.

### Step 2 — Lexical Analysis

`tokens, lex_errors = lex(source_code)` is called.

The lexer produces a list of tokens roughly like:

```
root  (  )  {  \n  seed  id(age)  =  intlit(10)  ;  \n
plant ( id(age) ) ;  \n  reclaim ;  \n  }  EOF
```

`lex_errors` is empty (the code is well-formed).

The server emits `stage_complete` with `stage: 'lexical', success: true`.

### Step 3 — Parser + AST construction

`parse_result = parser.parse_and_build(tokens)`:

- The LL(1) parser walks the token list, consulting the predict-set table at each step. Newline tokens are skipped because of `skip_token_types={'\n'}`.
- For each grammar production matched, `parse_and_build` calls into `build_ast` to attach a node to the growing AST.
- The result is a `ProgramNode` with a child `FunctionDeclarationNode` (named `root`), which has children for the parameter list (empty), a body block containing a variable declaration `seed age = 10`, an output statement `plant(age)`, and a `reclaim` statement.

`stage_complete` with `stage: 'syntax'` is emitted.

### Step 4 — Semantic Analysis

`semantic_result = validate_ast(parse_result['ast'], parse_result['symbol_table'])`:

- Walks the AST.
- Confirms `age` is declared before use in `plant(age)`.
- Confirms `reclaim` is the last statement of `root()`.
- Confirms `10` is a valid `seed` (integer) literal.
- No errors. `stage_complete` with `stage: 'semantic'`.

### Step 5 — Interpretation in a background task

```python
def run_interpreter():
    session_emitter = SessionEmitter(socketio, sid)
    interp = Interpreter(socketio=session_emitter)
    interp._cancelled = False
    interpreters[sid] = interp
    interp.interpret(ast)
    if not interp._cancelled:
        socketio.emit('execution_complete', {'success': True, ...}, to=sid)
```

The interpreter walks the AST:
- Allocates `age = 10` in the local scope.
- For `plant(age)`, looks up `age` (gets `10`), calls `self.plant(10)`, which calls `socketio.emit('output', {'output': '10'})`. Because `socketio` here is actually `SessionEmitter`, the `emit` is routed to the originating browser session.
- For `reclaim`, raises `ReturnValue(None)` which terminates the function cleanly.

The browser receives an `output` event with `{output: "10"}` and prints `10` in the IDE's console pane. Then `execution_complete` arrives with `success: true`.

### Total round trip

```
Browser  → run_code event
Server   → lex → parse → semantic → spawn interpreter in green thread
Interp   → emit('output', '10')      → browser displays "10"
Interp   → returns                   → execution_complete event
Browser  → marks run as successful
```

---

## 8. DEFENSE-READY EXPLANATION (memorize this)

> "**`server.py` is the orchestrator of my GAL compiler.** It is built on Flask and Socket.IO with eventlet for cooperative concurrency. **It receives** GAL source code from the browser either as an HTTP POST or as a WebSocket `run_code` event. **It validates** the request, then drives the compilation pipeline strictly in order: lexer, parser with AST construction, semantic analyzer, intermediate code generator (display only), and finally the interpreter. **At each stage, if the stage produces errors, the server short-circuits, returns or emits the errors with the failing stage name, and stops.** **It passes the result of each stage to the next stage as a typed Python object** — tokens to the parser, the AST and symbol table to the semantic analyzer, the AST to the interpreter. **For interactive programs, it spawns the interpreter inside a green thread** so that calls to `water()` (input) park the program without blocking other users. **Output produced by `plant()` is streamed back to the browser via Socket.IO emit events.** **If the user reruns while a previous program is still waiting, the server cancels the old interpreter cleanly.** Every error and exception is wrapped so the server never crashes during a demo."

---

*Next file in the defense-prep series: `lexer.py` — tokens, errors, and how raw text becomes a token stream.*
