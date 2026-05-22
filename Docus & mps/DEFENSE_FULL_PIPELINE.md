# GAL Compiler Full Source-Code Defense Guide

Combined guide: server.py -> tokens/errors -> lexer -> parser -> AST -> semantic analyzer -> ICG -> interpreter.

# GAL Compiler  -  Defense-Prep Walkthrough

## File 1 of 7: `server.py`

This is the entry point of the entire GAL compiler system. Every panel question about "how does my system actually run a program" starts here.

---

## 1. FILE PURPOSE

`server.py` is the **HTTP and WebSocket server** of the GAL compiler. It is the bridge between the browser-based frontend (the IDE the user types code in) and the Python backend (lexer, parser, semantic analyzer, ICG, interpreter).

Its job is:

1. **Receive** GAL source code from the frontend (either as a one-shot HTTP POST, or as a `run_code` Socket.IO event for interactive runs).
2. **Drive the compiler pipeline** stage by stage, in this fixed order:
   `lex -> parse -> AST -> semantic -> (optionally) ICG -> interpret`.
3. **Stop at the first failing stage** and return a structured error response that tells the frontend *which* stage failed and *what* the errors were.
4. **Stream program output** back to the user in real time (via Socket.IO) when the program is actually running, and **collect input** from the user when the program calls `water()`.
5. **Serve the static UI** files (HTML/CSS/JS) so the whole thing works as one app.

Where it sits in the pipeline:

```
  Browser (UI/index.html)
      |  POST /api/lex, /api/parse, /api/semantic, /api/icg, /api/run
      |  WebSocket: run_code, capture_input
      v
  +----------- server.py --------------+
  |  Flask + Socket.IO + eventlet      |
  |                                    |
  |  Calls:                            |
  |    lexer.lex()                     |
  |    LL1Parser.parse() / .parse_and_build()
  |    GALsemantic.validate_ast()      |
  |    icg.generate_icg()              |
  |    GALinterpreter.Interpreter()    |
  +------------------------------------+
```

What depends on it: nothing inside the backend depends on `server.py`. Everything else (lexer, parser, etc.) is **library code** that `server.py` orchestrates. That separation is intentional  -  the lexer doesn't know it's running on a server, which means you could run the compiler from a CLI, a unit test, or a different web framework without modifying any of the language code.

---

## 2. IMPORTS / DEPENDENCIES

```python
import warnings
warnings.filterwarnings("ignore", message=".*RLock.*were not greened.*")

import eventlet
eventlet.monkey_patch()
```

- **`warnings.filterwarnings(...)`**  -  silences a cosmetic warning that `eventlet` emits during startup about thread locks. It's irrelevant to behavior; we just don't want it cluttering the console during a demo.
- **`eventlet`** + **`eventlet.monkey_patch()`**  -  this is the *cooperative concurrency* layer. `monkey_patch()` rewrites Python's standard library (sockets, threading, time) to use eventlet's green threads instead of OS threads. We need this because:
  - Socket.IO must support many simultaneous WebSocket connections without blocking.
  - When the interpreter calls `water()` and waits for input, it can't block the whole server  -  eventlet lets the server park that one request and keep handling others.
  - **If you remove these lines:** Socket.IO will silently fall back to a less reliable mode and `water()` may deadlock the server during a demo.

```python
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
```

- **`Flask`**  -  the web framework. `Flask(__name__, ...)` creates the app object that handles all HTTP routes.
- **`request`**  -  gives access to the incoming HTTP request body (used in every endpoint via `request.get_json()`).
- **`jsonify`**  -  builds JSON responses with the right `Content-Type` header.
- **`send_from_directory`**  -  serves the static UI files (HTML, CSS, JS, images) from the `UI/` folder.
- **`CORS`**  -  Cross-Origin Resource Sharing. Lets the browser frontend talk to the backend even if served from a different port during development.
- **`SocketIO, emit`**  -  bidirectional WebSocket support. `emit()` is what we use to push output back to the browser in real time during program execution.

```python
import os
from google import genai
```

- **`os`**  -  used for environment variables (e.g., `GEMINI_API_KEY`, `PORT`) and joining file paths.
- **`genai`**  -  Google Gemini SDK, used by the AI chat-helper feature (the `/api/chat` endpoint). This is **not part of the compiler**; it's an optional helper.

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
| `analyze_semantics` | Legacy entry point  -  runs the full lex->parse->semantic flow in one call | Semantic |
| `validate_ast` | Tree-walking semantic validator that runs **after** the parser has built the AST | Semantic |
| `generate_icg` | Produces three-address code (TAC) for display purposes | ICG |
| `Interpreter` | The tree-walking interpreter that actually runs the program | Execution |
| `InterpreterError, _CancelledError` | Custom exceptions raised during execution | Execution |
| `fallback_reply` | Rule-based AI helper response used when Gemini is unavailable | Helper (not pipeline) |

**`analyze_semantics` may be possibly unused at the server layer**  -  the server uses `validate_ast` instead, which is the newer two-step API (`parse_and_build` then `validate_ast`). The legacy `analyze_semantics` function is still imported but I do not see a direct call to it in this file. Mark this for verification before defense  -  it is harmless to leave imported.

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

Wraps the Flask app with CORS support and Socket.IO. `cors_allowed_origins="*"` means any browser can connect  -  fine for a local development tool, but you would tighten this in production.

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

- Building a parser involves loading the grammar dictionary (`cfg`) and the predict-set table  -  heavy work.
- The parser itself is **stateless** during parsing (each call to `parser.parse(tokens)` works on its own input), so it's safe to share across requests.
- `skip_token_types={'\n'}` is the **token-filtering rule**  -  the parser will silently skip newline tokens during parsing. Newlines are produced by the lexer for line tracking but they have no role in GAL grammar.

This single line answers a likely panel question: *"Where does the parser skip newlines?"*  -  right here.

```python
_prompt_path = os.path.join(os.path.dirname(__file__), 'gal_prompt.txt')
with open(_prompt_path, 'r', encoding='utf-8') as _f:
    GAL_SYSTEM_PROMPT = _f.read()

_gemini_client = None
_chat_sessions = {}
```

These globals belong to the AI chat-helper feature only  -  not the compiler. `GAL_SYSTEM_PROMPT` is the system prompt loaded from disk that teaches Gemini about the GAL language. `_chat_sessions` holds conversation history per session.

---

## 4. CLASSES AND FUNCTIONS

There are three classes/helpers and a long list of route handlers. I'll group them.

### Helper: `_display_value(val)`  -  lines 20-28

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

### Class: `SessionEmitter`  -  lines 38-45

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

**Why it exists:** The interpreter calls `self.socketio.emit('output', {...})` to print things. But the interpreter doesn't know which Socket.IO session it belongs to. By passing a `SessionEmitter(sio, sid)` to the interpreter constructor, the interpreter can call `.emit(...)` and the emitter handles the routing  -  guaranteeing output goes to the right user, not broadcast to everyone connected.

**Compiler stage:** Execution / runtime I/O.

### Class: `OutputCollector`  -  lines 347-358

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

**Why it exists:** The HTTP `/api/run` endpoint runs a program synchronously and returns all output in one response  -  it doesn't have a live Socket.IO connection to stream to. `OutputCollector` lets us reuse the same `Interpreter` class without changes. This is a classic **adapter pattern**.

**Edge case:** If the program calls `water()` (input), `OutputCollector` raises `_InputNeeded` to abort  -  because there's no way to deliver an interactive prompt over a one-shot HTTP request.

### Exception: `_InputNeeded`  -  lines 361-363

```python
class _InputNeeded(Exception):
    pass
```

A private sentinel exception used only inside this file, raised by `OutputCollector` and caught by `/api/run` to know that "this program needs input we can't provide here."

### Route handlers: `/`, `/<path>`, `/images/<path>`  -  lines 65-78

```python
@app.route('/')
def index():
    return send_from_directory('../UI', 'index.html')
```

These three routes serve the **frontend**  -  the IDE itself. When you visit `http://localhost:5000/`, this hands back `index.html` from the UI folder. The other two routes serve CSS, JS, and images.

### Route handler: `/api/lex`  -  lines 80-119

This is the **Lexical Analysis endpoint**. It runs the lexer and returns the tokens in JSON. This is what the IDE calls when the user clicks "Lex" or "Tokenize." Detailed explanation in section 5 below.

### Route handler: `/api/parse`  -  lines 121-182

The **Syntax Analysis endpoint**. Runs lex -> parse and returns success/errors. Detailed below.

### Route handler: `/api/semantic`  -  lines 192-263

The **Semantic Analysis endpoint**. Runs lex -> parse -> AST -> semantic and returns the symbol table. Detailed below.

### Route handler: `/api/icg`  -  lines 265-342

The **Intermediate Code Generation endpoint**. Runs lex -> parse -> semantic -> ICG and returns TAC instructions for display. Detailed below.

### Route handler: `/api/run`  -  lines 365-446

The **synchronous execution endpoint** (no Socket.IO needed). Runs the entire pipeline including the interpreter, returns all output in one HTTP response. Used for non-interactive programs.

### Socket.IO handlers: `connect`, `disconnect`, `run_code`, `capture_input`  -  lines 451-554

These power the **live, interactive execution** flow. Detailed below.

### Route handlers: `/api/chat`, `/api/chat/clear`  -  lines 578-659

The AI chat helper. Calls Google Gemini, falls back to a rule-based reply if no API key. **Not part of the compiler pipeline**  -  purely a learning aid for users.

### `if __name__ == '__main__':`  -  lines 662-675

The startup block. Reads the `PORT` env var, prints a banner showing each API endpoint, and runs the server on `0.0.0.0` so it's reachable from any browser on the local network.

---

## 5. LINE-BY-LINE / BLOCK-BY-BLOCK EXPLANATION

I'll cover the most important blocks. The four endpoints `/api/lex`, `/api/parse`, `/api/semantic`, `/api/run` and the Socket.IO `run_code` handler form the heart of the file  -  every panel question about pipeline order traces back to these.

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

**Why `skip_token_types={'\n'}`:** This is the answer to "where do skipped tokens get filtered?" The parser silently ignores newlines during shift operations  -  they exist only to help the lexer report line numbers in errors.

**What data is being changed:** A module-level `parser` reference is created, ready to be called.

**Defense answer:** *"The parser is constructed once at startup. The grammar and predict-set tables are loaded into memory and reused. Since LL(1) parsing is stateless across calls, this is safe and faster than rebuilding it per request."*

### 5.3 `/api/lex`  -  the lexical analysis endpoint

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
3. `tokens, errors = lex(source_code)`  -  calls the **lexer** layer. `lex` is the public function in `lexer.py` that internally constructs a `Lexer` and calls `make_tokens()`. It returns `(tokens, errors)`  -  both lists.
4. The `for token in tokens` loop **flattens** each `Token` object into a JSON-friendly dict. `getattr(token, 'col', 0)` defends against tokens that didn't get a column attribute (e.g., synthetic EOF tokens).
5. `get_token_description(token.type, token.value)` adds a human-readable label like "Integer Literal" for the IDE's lexeme table.
6. `return jsonify(...)` sends the result back to the browser.
7. `except Exception` is the **safety net**  -  any uncaught exception in the pipeline becomes an HTTP 500 with an error message instead of a server crash. This is crucial for demos: a buggy GAL program shouldn't take down the server.

**What data is being changed:** None on the server. The endpoint is read-only  -  it produces a response from the input.

**Defense answer:** *"The lex endpoint accepts source code in the request body, runs the lexer to produce a token stream, converts the tokens into JSON, and returns them. Any exception is caught and returned as a structured error so the IDE can display it cleanly."*

### 5.4 `/api/parse`  -  syntax analysis

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

**`parser.parse(tokens)`** is the **legacy** parser entry that returns just `(success, errors)`  -  no AST. Used here because `/api/parse` only checks syntax, not structure.

**Defense answer:** *"This endpoint runs lex first, and only proceeds to parsing if the lexer reported no errors. If parsing fails, the response says `stage: ['syntax']` so the IDE highlights the right phase."*

### 5.5 `/api/semantic`  -  semantic analysis

```python
# Run the parser  -  validates syntax (LL1) then builds AST
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

# Run semantic analysis  -  tree-walking validation of the AST
semantic_result = validate_ast(parse_result['ast'], parse_result['symbol_table'])
```

**The key shift:** This endpoint uses **`parse_and_build`** (not just `parse`). `parse_and_build` does parsing **and** AST construction in one call. This is because some semantic errors are detected during AST construction itself (e.g., undeclared variables in expressions), so the parser's `error_stage` may already be `'semantic'` even though the parser called the failure.

**`validate_ast(ast, symbol_table)`** is a separate **tree-walking pass** that catches errors not visible during AST building (function-return-type mismatches, control-flow rules, etc.). It returns success/errors/warnings/symbol_table.

**Defense answer:** *"Semantic analysis happens in two places: some checks during AST construction (because the parser already knows the variable being declared), and some in `validate_ast` afterwards (because they need the full tree to be visible  -  like checking that a function actually returns a value of its declared type). The `error_stage` field tells the frontend which sub-phase complained."*

### 5.6 `/api/icg`  -  intermediate code generation

```python
# 4. Intermediate code generation
icg_result = generate_icg(tokens)
```

**Important:** ICG is generated from **tokens**, not from the AST. This is a deliberate choice  -  your ICG runs as a parallel pass over the token stream rather than walking the AST. This is fine because **the interpreter does NOT consume the ICG output**; ICG exists purely as a display artifact for the IDE's "Intermediate Code" tab.

**Defense answer:** *"Intermediate code generation runs as a parallel pass on the token stream after semantic analysis succeeds. Its only consumer is the IDE  -  the interpreter walks the AST directly. So ICG is a teaching/visualization layer, not a runtime layer."*

### 5.7 `/api/run`  -  synchronous execution endpoint

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

**The clever part:** Instead of giving the interpreter a real Socket.IO emitter, we give it `OutputCollector`. The interpreter doesn't know the difference  -  it calls `.emit('output', ...)` exactly the same way. This is the **adapter pattern**, and it's what lets one `Interpreter` class serve both interactive (Socket.IO) and synchronous (HTTP) modes.

**The three exception layers:**
- `_InputNeeded`  -  program tried to call `water()`, so we tell the frontend "switch to interactive mode."
- `InterpreterError`  -  a clean runtime error from the interpreter (like division by zero). We append the message to the output list and report failure.
- `Exception`  -  anything unexpected. Reported as "Internal Error" so it's clear this was not the program's fault.

**Defense answer:** *"The synchronous run endpoint reuses the same Interpreter class as the live mode by swapping in an OutputCollector that captures output instead of streaming it. If the program needs input, we abort and tell the client to switch to the interactive Socket.IO flow."*

### 5.8 Socket.IO `run_code`  -  interactive execution

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

### 5.9 `capture_input`  -  receive input from the client

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

> "Token filtering is configured at parser construction time, line 54: `skip_token_types={'\n'}`. The LL1Parser internally skips any token whose type is in that set during shift operations. We don't manually strip newlines from the token list  -  the parser handles it transparently."

**Q: How does the server distinguish a syntax error from a semantic error during parsing?**

> "When `parse_and_build` runs, it can fail with either a syntax error (the LL(1) table didn't accept the next token) or a semantic error caught during AST construction (e.g., a redeclared variable). The parser sets `error_stage` in its return value. The server reads that field on line 239 and 307 to label the response correctly."

**Q: What happens if the GAL program has a runtime error like division by zero?**

> "The interpreter raises an `InterpreterError`. In `/api/run` it's caught at line 428; in the Socket.IO `run_code` handler it's caught inside `run_interpreter` at line 531. We emit a `Runtime Error: ...` line via the same output channel and an `execution_complete` event with `success: False`."

**Q: What if two users run programs at the same time?**

> "Each user has a unique Socket.IO session ID. The `interpreters` dictionary maps `sid -> Interpreter`. Eventlet monkey-patching ensures that when one interpreter blocks on `water()`, the server keeps handling other users' requests. They don't share state."

**Q: Why does the interpreter accept a `socketio` argument but the synchronous `/api/run` endpoint passes an `OutputCollector` instead?**

> "Both implement the same `.emit(event, data)` interface. The `Interpreter` class doesn't care whether output is being streamed over WebSockets or collected into a list  -  that's the adapter pattern. It keeps the interpreter independent of the I/O layer."

**Q: If the lexer fails, why don't you still run the parser to find more errors?**

> "Because the parser would be reading tokens that may not represent the user's intent. If a quote was unclosed, half the file became one giant string-literal token, and parsing it would produce a flood of nonsense errors that hide the real problem. Stopping early gives the user one clear lexical error to fix."

**Q: Where does the AST get built? In the parser or in semantic?**

> "Both ways exist. The newer flow uses `parser.parse_and_build(tokens)` which validates syntax with the LL(1) table AND simultaneously calls into `GALsemantic.build_ast` to construct the tree. Then `validate_ast` runs as a separate tree-walking pass for checks that need the whole tree. This two-step model is why the server distinguishes `error_stage = 'syntax'` from `error_stage = 'semantic'` even though both can come from the same parser call."

**Q: What is `analyze_semantics` and why is it imported?**

> "It's the legacy entry point that runs lex->parse->AST->semantic in one call. We don't use it directly in the server anymore  -  we call `parse_and_build` and `validate_ast` separately so the IDE can report which sub-stage failed. The import remains for backwards compatibility with grading scripts and CLI tests."

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

### Step 1  -  Frontend -> Server

The user clicks "Run" in the IDE. The frontend opens (or reuses) a Socket.IO connection and emits:

```
event: run_code
data: { source_code: "root() {\n    seed age = 10;\n    plant(age);\n    reclaim;\n}" }
```

This triggers `handle_run_code(data)` at line 461.

### Step 2  -  Lexical Analysis

`tokens, lex_errors = lex(source_code)` is called.

The lexer produces a list of tokens roughly like:

```
root  (  )  {  \n  seed  id(age)  =  intlit(10)  ;  \n
plant ( id(age) ) ;  \n  reclaim ;  \n  }  EOF
```

`lex_errors` is empty (the code is well-formed).

The server emits `stage_complete` with `stage: 'lexical', success: true`.

### Step 3  -  Parser + AST construction

`parse_result = parser.parse_and_build(tokens)`:

- The LL(1) parser walks the token list, consulting the predict-set table at each step. Newline tokens are skipped because of `skip_token_types={'\n'}`.
- For each grammar production matched, `parse_and_build` calls into `build_ast` to attach a node to the growing AST.
- The result is a `ProgramNode` with a child `FunctionDeclarationNode` (named `root`), which has children for the parameter list (empty), a body block containing a variable declaration `seed age = 10`, an output statement `plant(age)`, and a `reclaim` statement.

`stage_complete` with `stage: 'syntax'` is emitted.

### Step 4  -  Semantic Analysis

`semantic_result = validate_ast(parse_result['ast'], parse_result['symbol_table'])`:

- Walks the AST.
- Confirms `age` is declared before use in `plant(age)`.
- Confirms `reclaim` is the last statement of `root()`.
- Confirms `10` is a valid `seed` (integer) literal.
- No errors. `stage_complete` with `stage: 'semantic'`.

### Step 5  -  Interpretation in a background task

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
Browser  -> run_code event
Server   -> lex -> parse -> semantic -> spawn interpreter in green thread
Interp   -> emit('output', '10')      -> browser displays "10"
Interp   -> returns                   -> execution_complete event
Browser  -> marks run as successful
```

---

## 8. DEFENSE-READY EXPLANATION (memorize this)

> "**`server.py` is the orchestrator of my GAL compiler.** It is built on Flask and Socket.IO with eventlet for cooperative concurrency. **It receives** GAL source code from the browser either as an HTTP POST or as a WebSocket `run_code` event. **It validates** the request, then drives the compilation pipeline strictly in order: lexer, parser with AST construction, semantic analyzer, intermediate code generator (display only), and finally the interpreter. **At each stage, if the stage produces errors, the server short-circuits, returns or emits the errors with the failing stage name, and stops.** **It passes the result of each stage to the next stage as a typed Python object**  -  tokens to the parser, the AST and symbol table to the semantic analyzer, the AST to the interpreter. **For interactive programs, it spawns the interpreter inside a green thread** so that calls to `water()` (input) park the program without blocking other users. **Output produced by `plant()` is streamed back to the browser via Socket.IO emit events.** **If the user reruns while a previous program is still waiting, the server cancels the old interpreter cleanly.** Every error and exception is wrapped so the server never crashes during a demo."

---

*Next file in the defense-prep series: `lexer.py`  -  tokens, errors, and how raw text becomes a token stream.*


---

# GAL Compiler  -  Defense-Prep Walkthrough

## File 2 of 9: tokens / errors (the Token, Position, and LexicalError classes inside `lexer.py`)

These three classes are tiny but **they are the vocabulary the whole compiler speaks**. Every layer after the lexer  -  parser, AST builder, semantic, ICG, interpreter  -  consumes `Token` objects and produces typed errors. If a panel asks "how does your compiler represent a piece of source code?", the answer starts here.

---

## 1. FILE PURPOSE

These three classes (and the token-type constants and `get_token_description` helper that surround them) live inside `lexer.py` (lines 1-246, 252-297). They define **how a single character or word from the user's program is represented internally** so it can travel through the rest of the pipeline.

Where they fit:

```
Source code (a Python string)
        |
        v
   +----------+
   |  Lexer   |
   +----------+
        |  produces:
        v
  list[Token]  + list[LexicalError]
        |
        v
   +----------+
   |  Parser  | <--- reads Token.type to decide grammar action
   +----------+    reads Token.line/col for error messages
        |
        v
   +--------------+
   |  AST builder | <--- attaches Token.value and Token.line to AST nodes
   +--------------+
        |
        v
   semantic, ICG, interpreter  -  same Token references, never mutated
```

What depends on these classes:

| File | What it uses |
|---|---|
| `lexer.py` (the rest of it) | `Lexer.make_tokens()` builds `Token` instances |
| `Gal_Parser.py` | Reads `token.type` for LL(1) table lookup, `token.line/col` for syntax error messages |
| `GALsemantic.py` | Uses `token.value` for variable names, `token.line` for semantic errors |
| `icg.py` | Reads `token.type` to dispatch TAC emission |
| `GALinterpreter.py` | Reads `token.line` to attach line numbers to runtime errors |
| `server.py` | Uses `_display_value(token.value)` and `get_token_description(token.type, token.value)` to render the lexeme table for the IDE |

These classes are the **single source of truth** for what a token looks like. They are never subclassed and never extended.

---

## 2. IMPORTS / DEPENDENCIES

The token/error classes use **no imports of their own**  -  they are pure-Python data containers. The surrounding `lexer.py` imports nothing for them. That's deliberate:

- They are POPOs (plain old Python objects), so any other file can import them without dragging in third-party libraries.
- No JSON, no logging, no runtime configuration. Each `Token` is just four fields, each `LexicalError` is just two.

If a panel asks *"why are these classes so simple?"*: the answer is that **simplicity is the feature**. A token is just data. Behavior (how it's displayed, how it's serialized, how it's compared) lives in the layers that use the token  -  not on the token itself.

---

## 3. GLOBAL CONSTANTS / VARIABLES

This layer has **two flavors** of constants  -  character classes (used by the lexer to recognize tokens) and **token-type strings** (used by every later layer to identify what kind of token they're looking at).

### 3.1 Character-class constants (lines 11-19)

```python
ZERO = '0'
DIGIT = '123456789'
ZERODIGIT = ZERO + DIGIT          # '0123456789'

LOW_ALPHA = 'abcdefghijklmnopqrstuvwxyz'
UPPER_ALPHA = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
ALPHA = LOW_ALPHA + UPPER_ALPHA   # 'a-zA-Z'
ALPHANUM = ALPHA + ZERODIGIT + '_'
```

**Why two digit sets?** GAL identifiers may contain digits anywhere except the **first** character. So `DIGIT` (no zero) is used to validate the first digit of a number that should not have leading zeros, while `ZERODIGIT` is used for the rest.

**Why `ALPHANUM` includes underscore but `ALPHA` doesn't?** Because identifiers are `letter (letter|digit|_)*`  -  the first character must be a letter, so `ALPHA` is used to validate it; everything after that uses `ALPHANUM`. This matches Rule 3 in your GAL specification: *"Identifiers must start with a letter and may include letters, digits, and underscore."*

**Defense answer:** *"These are the alphabets the lexer uses to validate identifier and number formation. They directly mirror the regular definitions in our compiler proposal  -  `letter`, `digit`, `alphanumeric`."*

### 3.2 Delimiter sets (lines 25-52)

```python
space_delim = {' ', '\t', '\n'}
delim2 = {';', ':'}
delim3 = {'{'}
delim4 = {':', '('}
...
idf_delim = {' ', ',', ';', '(', ')', '{', '}', ...}
whlnum_delim = {';', ' ', ',', '}', ']', ')', ':', ...}
decim_delim = {'}', ';', ',', '+', '-', '*', '/', ...}
```

**What these are:** Each delimiter set lists the characters that may **legally come immediately after** a particular kind of token. The lexer uses them to detect things like `seedage` (where `seed` runs into `age` with no whitespace)  -  that's invalid because `seed` must be followed by whitespace, a paren, or punctuation, not by a letter.

**Why they're needed:** GAL's grammar is *delimiter-aware*. A keyword like `seed` is only a keyword if it's followed by something that lets the lexer know it ended; otherwise, `seedling` would be tokenized as the keyword `seed` followed by the identifier `ling`, which is a different mistake than what the user intended.

**Honest note for the defense:** A code review of `lexer.py` showed that **only some of these delimiter sets are actively used** (`space_delim`, `delim2`, `delim3`, `delim4`, `delim6`, `delim7`, `delim8`, `delim23`, `idf_delim`, `whlnum_delim`, `decim_delim` are referenced in scanning logic). The numbered ones from 9 through 22, plus 24 and `comment_delim`, are defined but not consumed by the current implementation. They are kept as documentation that mirrors the **regular-definition tables** in your compiler proposal  -  each numbered `delim` corresponds to one row of the proposal's "Regular Definition" section. Removing them would lose the proposal-to-code traceability, so they stay.

If asked: *"Some delimiter sets are kept for spec traceability  -  each name maps to a delim row in the GAL proposal document. The actively-used ones drive the scanner's lookahead checks; the others are kept as living documentation."*

### 3.3 Token-type constants (lines 60-133)

This is the **vocabulary list of the entire compiler**. Every token produced by the lexer has a `.type` field whose value is one of these strings. There are roughly 60 of them, grouped into:

**Reserved words (26):**

```python
TT_RW_WATER       = 'water'     TT_RW_PLANT       = 'plant'
TT_RW_SEED        = 'seed'      TT_RW_LEAF        = 'leaf'
TT_RW_BRANCH      = 'branch'    TT_RW_TREE        = 'tree'
TT_RW_VINE        = 'vine'      TT_RW_SPRING      = 'spring'
TT_RW_WITHER      = 'wither'    TT_RW_BUD         = 'bud'
TT_RW_HARVEST     = 'harvest'   TT_RW_GROW        = 'grow'
TT_RW_CULTIVATE   = 'cultivate' TT_RW_TEND        = 'tend'
TT_RW_EMPTY       = 'empty'     TT_RW_PRUNE       = 'prune'
TT_RW_SKIP        = 'skip'      TT_RW_RECLAIM     = 'reclaim'
TT_RW_ROOT        = 'root'      TT_RW_POLLINATE   = 'pollinate'
TT_RW_VARIETY     = 'variety'   TT_RW_FERTILE     = 'fertile'
TT_RW_SOIL        = 'soil'      TT_RW_BUNDLE      = 'bundle'
```

**Operators (arithmetic, assignment, comparison, logical, increment/decrement):**

```python
TT_PLUS = '+'         TT_MINUS = '-'        TT_MUL = '*'
TT_DIV = '/'          TT_MOD = '%'          TT_EQ = '='
TT_EQTO = '=='        TT_NOTEQ = '!='       TT_LT = '<'
TT_GT = '>'           TT_LTEQ = '<='        TT_GTEQ = '>='
TT_AND = '&&'         TT_OR = '||'          TT_NOT = '!'
TT_INCREMENT = '++'   TT_DECREMENT = '--'
TT_PLUSEQ = '+='      TT_MINUSEQ = '-='     TT_MULTIEQ = '*='
TT_DIVEQ = '/='       TT_MODEQ = '%='
TT_NEGATIVE = '~'     TT_CONCAT = '`'
```

**Punctuation:**

```python
TT_LPAREN = '('       TT_RPAREN = ')'
TT_BLOCK_START = '{'  TT_BLOCK_END = '}'
TT_LSQBR = '['        TT_RSQBR = ']'
TT_SEMICOLON = ';'    TT_COMMA = ','        TT_COLON = ':'
TT_DOT = '.'
```

**Identifiers, literals, special:**

```python
TT_IDENTIFIER     = 'id'        # any user-defined name
TT_INTEGERLIT     = 'intlit'    # 42, 100
TT_DOUBLELIT      = 'dbllit'    # 3.14
TT_STRINGLIT      = 'stringlit' # "hello"
TT_CHARLIT        = 'chrlit'    # 'a'
TT_BOOLLIT_TRUE   = 'sunshine'
TT_BOOLLIT_FALSE  = 'frost'
TT_EOF            = 'EOF'       # synthetic end-of-file marker
TT_NL             = '\n'        # newline (skipped during parsing)
```

**Why each constant has both a Python name and a string value:**

```python
TT_RW_SEED = 'seed'
```

The Python name `TT_RW_SEED` is what the lexer **writes** when emitting tokens. The string value `'seed'` is what every later layer **compares against**. The duplication looks odd, but it gives us:

- **Symbolic names** in the lexer for self-documenting code: `Token(TT_RW_SEED, ...)` reads better than `Token('seed', ...)`.
- **String comparisons** in the parser: when the LL(1) table says "expect token type `'seed'`", the parser does a fast string equality check. Strings are hashable and immutable in Python  -  perfect for being keys in the predict-set dictionary.

**Two important conventions:**

1. **Token type strings match the surface text for keywords.** `TT_RW_SEED = 'seed'`. So when the lexer sees the word `seed` in the source, the token's type is literally the string `'seed'`. This makes the parser's grammar definitions in `cfg.py` read like the GAL source itself.
2. **Token type strings for symbols are the symbol itself.** `TT_PLUS = '+'`. So `Token('+', '+', ...)` represents a literal `+`. This is consistent and easy to debug.

**Defense answer for "why is the type a string and not an enum?":** *"Strings are hashable, immutable, and easy to inspect. Our LL(1) parsing table uses token-type strings as dictionary keys  -  we use the string `'seed'` directly as a terminal in the grammar. Using an `enum` would force every comparison to go through the enum's value attribute, with no benefit. The token-type constants serve as a self-documenting catalogue."*

### 3.4 The known typo / token name discrepancy

The token-type constant for double literals is `TT_DOUBLELIT = 'dbllit'`. However, the parser internally uses the name `'dblit'` everywhere (in the grammar productions in `cfg.py`, in error filters in `Gal_Parser.py`).

**The bridge:** the parser's `LL1Parser` is configured with a `token_type_alias` map: `{'dbllit': 'dblit'}`. When it reads a token from the lexer with type `'dbllit'`, it normalizes it to `'dblit'` before comparing against the grammar.

**Why two names for one thing?** Historical reasons  -  the lexer settled on `'dbllit'` (one word, "double literal") and the grammar settled on `'dblit'` (shorter alternative). Rather than touch both, we keep the alias as a one-line bridge.

**For defense:** if a panelist sees this discrepancy: *"`dbllit` is the lexer's internal name; `dblit` is the grammar terminal. They are bridged by a single alias entry in the parser configuration. We documented this in our system-documentation file."*

---

## 4. CLASSES AND FUNCTIONS

### 4.1 `Position` class (lines 252-272)

```python
class Position:
    def __init__(self, index, ln, col=0):
        self.index = index
        self.ln = ln
        self.col = col

    def advance(self, current_char):
        self.index += 1
        self.col += 1
        if current_char == '\n':
            self.ln += 1
            self.col = 0
        return self

    def copy(self):
        return Position(self.index, self.ln, self.col)
```

**What it receives:** A character index, a line number (1-based), and an optional column number (0-based).

**What it returns / modifies:** The instance is mutated in-place by `advance()`; `copy()` returns a snapshot.

**Why it exists:** Errors must be reported with a precise location, e.g., *"Lexical error line 4 col 12: unclosed string literal"*. Without a position object, the lexer would have to track three separate counters everywhere.

**When it is called:**
- `Lexer.__init__` creates one: `self.pos = Position(-1, 1, -1)` (intentionally pre-first-char so the first `advance()` lands at index 0, line 1, col 0).
- `Lexer.advance` calls `self.pos.advance(self.current_char)` for every character read.
- Various scanners call `pos = self.pos.copy()` at the start of a multi-character token (e.g., the start of a string literal) so that if an error occurs, the error message points to the token's *start*, not its *end*.

**Stage:** Lexical (used during scanning).

**Errors handled:** None directly. It's a passive data tracker.

**Edge cases:**
- The constructor accepts `index=-1` so the lexer can call `advance()` once and land at the true first character. Calling `Position(0, 1, 0)` then `advance()` would skip the first character.
- When `\n` is consumed, the column resets to 0 *of the new line*, but the `\n` token itself is at col 0 of the new line. Tokens on the previous line that span past col 0 are reported correctly because we use `pos.copy()` at the token's *start*.

### 4.2 `LexicalError` class (lines 277-286)

```python
class LexicalError:
    def __init__(self, pos, details):
        self.pos = pos
        self.details = details

    def as_string(self):
        self.details = self.details.replace('\n', '\\n')
        return f"LEXICAL error line {self.pos.ln} col {self.pos.col} {self.details}"
```

**What it receives:** A `Position` snapshot (where the error occurred) and a string `details` describing what went wrong.

**What it returns:** Stores the data; `as_string()` formats a single human-readable line.

**Why it exists:** Lexical errors and runtime errors have different concerns. A lexical error must include *line and column*, must format consistently across the whole compiler, and must not stop the lexer (the lexer continues scanning so it can report multiple errors at once).

**When it is called:**
- Inside the lexer, whenever an invalid character or malformed token is detected: `errors.append(LexicalError(pos, "Invalid character '$'"))`.
- `as_string()` is called when assembling the final error list to send back via `server.py`.

**Edge case:** The `replace('\n', '\\n')` line escapes newlines in the error description so a single error never breaks across multiple lines of output. Note this **mutates `self.details`** the first time it's called; calling `as_string()` twice returns the same string. Harmless but technically a side effect  -  a defensible design choice for a single-shot error formatter.

**Defense answer for "why is this a class instead of just a string?":** *"Errors have two pieces of data: position and message. Wrapping them in a class lets us preserve both fields all the way to the IDE, where the frontend uses the line/column to highlight the exact source location. A flat string would lose the structured location."*

### 4.3 `Token` class (lines 291-297)

```python
class Token:
    def __init__(self, type_, value=None, line=1, col=0):
        self.type = type_    # e.g., 'seed', 'id', 'intlit', '+', '=='
        self.value = value   # actual text/value (e.g., 42, "myVar", "+")
        self.line = line     # line number where token starts
        self.col = col       # column number where token starts
```

**What it receives:** A type string (one of the `TT_*` constants), a value (the literal text or numeric/string value), a line number, and a column number.

**What it returns / modifies:** Just stores the four fields.

**Why it exists:** This is the **interface between every compiler stage**. Lexer produces them; parser/AST/semantic/ICG/interpreter consume them. By making the class minimal and immutable-by-convention (no setter methods), we guarantee that no later stage can accidentally rewrite a token's type or position.

**When it is called:** The lexer constructs `Token(...)` every time it finishes recognizing a lexeme. After construction, tokens are read but never reassigned.

**Stage:** Spans Lexical -> Syntax -> Semantic -> ICG -> Execution. Probably the most-used class in the codebase by reference count.

**Edge cases:**

- `value=None` is allowed because some tokens (notably `TT_EOF`) carry no payload.
- `line=1, col=0` defaults exist so synthetic tokens (created at parse time, not lex time) don't crash.
- The `Token` class has no `__repr__` or `__eq__`  -  comparisons elsewhere always use `token.type == 'seed'`. **This is intentional and not a bug.** If you added `__eq__`, careless comparisons like `token == 'seed'` would silently work and obscure the type-vs-value distinction.

**Defense answer for "why doesn't `Token` have a `__repr__`?":** *"Token comparisons are always done on specific fields  -  `token.type` for grammar matching, `token.value` for semantic checks, `token.line` for error reporting. Defining `__repr__` would tempt callers to print tokens directly and cross fields. The IDE rendering goes through `_display_value()` and `get_token_description()` instead, which gives controlled formatting."*

### 4.4 `get_token_description(token_type, value)` helper (lines 139-246)

```python
def get_token_description(token_type: str, value: str = '') -> str:
    """Returns a descriptive name for each token type"""
    if token_type == 'intlit' and isinstance(value, str) and value.startswith('~'):
        return 'negative integer'
    if token_type == 'dbllit' and isinstance(value, str) and value.startswith('~'):
        return 'negative float'
    descriptions = { 'water': 'Input Function', 'plant': 'Output Function',
                     'seed': 'Integer Type', ... }
    return descriptions.get(token_type, 'Unknown Token')
```

**What it receives:** A token type string and (optionally) the token's value.

**What it returns:** A human-readable label like `"Integer Type"`, `"While Loop"`, or `"Plus Operator"`.

**Why it exists:** The IDE displays a "Lexemes" table with three columns: lexeme (the text), token (the type), and type (the friendly description). The friendly description comes from this function.

**When it is called:** Inside `server.py` at every endpoint that returns tokens to the IDE: `/api/lex`, `/api/parse`, `/api/semantic`, `/api/icg`. Each token is enriched with `'description': get_token_description(token.type, token.value)` before being sent over the wire.

**Stage:** Display only  -  never used by parser/semantic/ICG/interpreter.

**Special handling for negative literals:** GAL writes negatives as `~5`, but the lexer emits them as `Token('intlit', '~5', ...)` (the type stays `'intlit'`, the value carries the `~`). When the IDE renders this, we want it labeled as **"negative integer"** to make the distinction clear in the lexeme table. The two `if` checks at the top of the function handle this.

**Defense answer:** *"This is purely a display function. It maps internal token types to user-facing labels for the lexeme view. It's never on the execution path."*

---

## 5. LINE-BY-LINE / BLOCK-BY-BLOCK EXPLANATION

### 5.1 `Position.__init__`

```python
def __init__(self, index, ln, col=0):
    self.index = index
    self.ln = ln
    self.col = col
```

**What this block does:** Stores three integers describing where in the source we are.

**Why this logic is needed:** Three coordinates are tracked, not just one, because:
- `index` (0-based character offset) is used internally by the lexer to slice the source string.
- `ln` (1-based line) and `col` (0-based column) are used in error messages, where humans count lines from 1.

**What data is being changed:** The new `Position` instance gets three field values.

**Defense answer:** *"`index` is for the lexer's bookkeeping; `ln` and `col` are for human-readable error messages. We separate them because the line/column are 1-based for humans but the index is 0-based for slicing."*

### 5.2 `Position.advance(current_char)`

```python
def advance(self, current_char):
    self.index += 1
    self.col += 1
    if current_char == '\n':
        self.ln += 1
        self.col = 0
    return self
```

**What this block does:** Moves the position forward by one character. If the character we just consumed was a newline, the line counter ticks up and the column resets.

**Why this logic is needed:** Without per-character advancement, line numbers in errors would be wrong. The crucial observation is the position is updated **based on the character we just consumed**, not on the next one. So when `\n` is the current char and we advance, the position now points to the **start of the new line**.

**What happens next:** The lexer reads the next character at `self.source_code[self.pos.index]`.

**Defense answer:** *"`advance()` is called once per character. It bumps the index and column. If the character was a newline, it increments the line and resets the column to 0 for the new line. This is how every error message in the compiler ultimately knows its line and column."*

### 5.3 `LexicalError.as_string()`

```python
def as_string(self):
    self.details = self.details.replace('\n', '\\n')
    return f"LEXICAL error line {self.pos.ln} col {self.pos.col} {self.details}"
```

**What this block does:** Formats the error as a single line, escaping any embedded newlines in the description.

**Why this logic is needed:** Errors are sometimes generated with multi-line context strings; we want them rendered as a single line in the IDE's error console.

**Edge case:** Calling `as_string()` twice mutates `self.details` once (first call replaces `\n`, second call has nothing to replace). This is harmless but technically not idempotent. *I would mark this as needs-verification if a panelist asks  -  it does not affect correctness.*

**Defense answer:** *"This produces the standard error string that the IDE displays in the error pane: `'LEXICAL error line 4 col 7: invalid character'`. The format is consistent across all error types so the frontend can parse and display it uniformly."*

### 5.4 The `Token` class

```python
class Token:
    def __init__(self, type_, value=None, line=1, col=0):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col
```

**What this block does:** Defines the data shape for every token in the compiler.

**Why this logic is needed:** Every later stage will read these four fields and only these four fields. There is no inheritance, no abstract method  -  just data.

**The trailing parameter pattern:** `type_` (with the trailing underscore) is named that way because `type` is a Python builtin and shadowing it in a constructor argument would cause subtle bugs if the class internals ever called `type(self.value)` later.

**Defense answer:** *"A token is just four fields: type, value, line, column. We deliberately keep it dumb. The behavior  -  display, comparison, parsing  -  happens in the layers that consume the token, not on the token itself. This separation lets the same `Token` class flow through all five compiler stages unchanged."*

### 5.5 The token-type constants (block view)

```python
TT_RW_SEED = 'seed'      # the word `seed` in source becomes Token('seed', 'seed', ...)
TT_PLUS = '+'            # the symbol `+` becomes Token('+', '+', ...)
TT_INTEGERLIT = 'intlit' # the digits `42` become Token('intlit', '42', ...)
TT_IDENTIFIER = 'id'     # the word `myVar` becomes Token('id', 'myVar', ...)
TT_EOF = 'EOF'           # synthetic end-of-input marker
```

**What this block does:** Establishes the 60-or-so distinct token types the compiler recognizes.

**Why this logic is needed:** Without these constants, the lexer would scatter raw string literals like `'seed'`, `'+'`, `'EOF'` throughout its body, and a typo in any one would silently break recognition. By naming them as Python constants, typos become `NameError`s the IDE catches immediately.

**Why the keywords are stored as themselves:** `TT_RW_SEED = 'seed'`, not `'KW_SEED'`. The benefit: when you read a `Token`, you can immediately see "oh this is the `seed` keyword" without needing a translation table. The cost: identifiers and keywords share a namespace of comparison strings, but since identifiers always have type `'id'` (never the keyword text), there's no collision.

**Defense answer:** *"The token-type system is the agreement between the lexer and every later stage. We use plain strings rather than enums for two reasons: hashability (needed for the LL(1) predict-set dictionary), and readability (the parser's grammar productions reference `'seed'` directly, which matches the source-language keyword)."*

---

## 6. DEFENSE QUESTION PREPARATION

**Q: Why do you have a separate `Position` class instead of just passing line/column integers around?**

> "Three reasons. First, the lexer copies positions when it begins a multi-character token  -  `pos = self.pos.copy()`  -  so an error message can point to the *start* of an unclosed string, not the end. A separate class makes that copy operation atomic. Second, every error in the system carries a position; centralizing it into one class means we change the format in one place. Third, we may extend it later (e.g., adding the file name when we support multi-file programs) without touching every call site."

**Q: Why doesn't `Token` have an `__eq__` or `__repr__`?**

> "Intentional. Token comparisons in our codebase are always against a specific field  -  `token.type == 'seed'`, never `token == something`. Defining `__eq__` would invite ambiguous comparisons that compare across fields. For display, we use `_display_value(token.value)` and `get_token_description(token.type, token.value)` so we have controlled formatting in the IDE."

**Q: How do you tell a keyword apart from an identifier?**

> "The lexer scans an alphanumeric run, then checks if the resulting string is in our keyword set. If yes, the token type is the keyword text itself (e.g., `'seed'`); if no, the token type is `'id'` and the identifier text becomes the value. So `seed` produces `Token('seed', 'seed', ...)` while `seedling` produces `Token('id', 'seedling', ...)`. This collision-free scheme works because the parser's grammar only accepts `'id'` where an identifier is expected, never a keyword string."

**Q: Why are token types strings, not an enum?**

> "Three reasons: hashability  -  they're keys in the LL(1) predict-set dictionary; mirror-readability  -  the grammar productions in `cfg.py` use the same strings as terminals, so the grammar reads like the source language; and zero overhead  -  no enum-attribute access on every comparison. The `TT_*` Python names act as a self-documenting catalogue."

**Q: What does the `~` prefix in a token's value mean?**

> "GAL uses `~` for negative literals. When the lexer sees `~5`, it produces `Token('intlit', '~5', ...)`  -  the type stays `intlit` (because it's still an integer), but the value carries the tilde. The interpreter's literal-parser detects the leading `~` and converts it to Python's `-` before computing. This design avoids needing a separate `unary minus` grammar production."

**Q: What is `LexicalError.as_string()` and where is it used?**

> "It produces the user-facing error string in our standard format: `LEXICAL error line N col M: details`. It's called when assembling the error list that `server.py` returns to the IDE. The format is consistent across the whole compiler  -  every layer's error type produces a similar string so the IDE can color and place them uniformly."

**Q: Why are some `delim` constants apparently unused?**

> "Each `delim` set corresponds one-to-one with a row in the regular-definition table from our compiler proposal. The actively-used ones drive lookahead checks in the scanner. The others are kept as **living documentation** that ties the implementation to the spec. Removing them would lose that traceability. They cost us nothing at runtime."

**Q: What happens if the same source text could match two different tokens (e.g., `==` and `=`)?**

> "This is the classic 'maximal munch' problem. We resolve it by ordering: the scanner checks the longer pattern first. When the current char is `=`, the lexer peeks at the next char. If the next is also `=`, we emit `==`; otherwise `=`. Same logic for `<=`, `>=`, `!=`, `&&`, `||`, `++`, `--`, `+=`, `-=`, `*=`, `/=`, `%=`. There are no ambiguous cases that survive the maximal-munch rule."

**Q: Could a malformed source crash the lexer?**

> "No. Every error path constructs a `LexicalError` and `continue`s scanning. The lexer never raises  -  it only collects errors into a list and returns them alongside whatever tokens it managed to recognize. Even an unclosed multi-line comment is recovered: we report the unclosed-comment error and treat everything from `/*` to EOF as comment text. The server then short-circuits the pipeline because `lex_errors` is non-empty."

---

## 7. SIMPLE WALKTHROUGH EXAMPLE

Sample code:

```
root() {
    seed age = 10;
    plant(age);
    reclaim;
}
```

How **tokens and errors** are produced:

The lexer scans this text and produces a list of `Token` objects. Here is the complete stream (with line and column hints):

| `type` | `value` | `line` | `col` |
|---|---|---|---|
| `'root'` | `'root'` | 1 | 0 |
| `'('` | `'('` | 1 | 4 |
| `')'` | `')'` | 1 | 5 |
| `'{'` | `'{'` | 1 | 7 |
| `'\n'` | `'\n'` | 1 | 8 |
| `'seed'` | `'seed'` | 2 | 4 |
| `'id'` | `'age'` | 2 | 9 |
| `'='` | `'='` | 2 | 13 |
| `'intlit'` | `'10'` | 2 | 15 |
| `';'` | `';'` | 2 | 17 |
| `'\n'` | `'\n'` | 2 | 18 |
| `'plant'` | `'plant'` | 3 | 4 |
| `'('` | `'('` | 3 | 9 |
| `'id'` | `'age'` | 3 | 10 |
| `')'` | `')'` | 3 | 13 |
| `';'` | `';'` | 3 | 14 |
| `'\n'` | `'\n'` | 3 | 15 |
| `'reclaim'` | `'reclaim'` | 4 | 4 |
| `';'` | `';'` | 4 | 11 |
| `'\n'` | `'\n'` | 4 | 12 |
| `'}'` | `'}'` | 5 | 0 |
| `'EOF'` | `''` | 5 | 1 |

A few observations:

- Keywords like `root`, `seed`, `plant`, `reclaim` carry their own keyword-string as the type AND the value.
- The identifier `age` has type `'id'`  -  same word `age` appears both in the declaration and the use, but each occurrence becomes a separate `Token` with its own line/column.
- `10` becomes `Token('intlit', '10', 2, 15)`. The value is the **string** `'10'` at this stage; the conversion to the Python integer `10` happens later in the interpreter.
- Newlines are emitted as `Token('\n', '\n', ...)` tokens. The parser is configured with `skip_token_types={'\n'}`, so it ignores these  -  but they exist in the stream so that the lexer's line counter advances and so that the lexer can use them as delimiters.
- The synthetic `EOF` token at the end has empty value and is produced by the lexer to mark "no more input."

`errors` is the empty list `[]` because this code is well-formed.

**If the user typed `seed age @ 10;` instead:** when the scanner sees `@`, it doesn't match any token rule. It builds:

```python
LexicalError(pos=Position(index=10, ln=2, col=8), details="Invalid character '@'")
```

...appends it to `errors`, calls `advance()` to skip past `@`, and continues scanning. The token list still contains everything before and after `@`, but `errors` is non-empty. `server.py` sees this and short-circuits the pipeline at the lexical stage.

---

## 8. DEFENSE-READY EXPLANATION (memorize this)

> "**The token and error layer is the foundation of the entire compiler.** It defines three classes: `Position`, which tracks index, line, and column for precise error reporting; `LexicalError`, which packages a position and a description into a structured error record; and `Token`, which is the four-field data carrier  -  type, value, line, column  -  that flows through every stage from the lexer to the interpreter. **It also defines roughly 60 token-type constants** that every later stage reads to identify what each token represents  -  keywords like `seed` and `pollinate`, operators like `+` and `==`, and meta-types like `id`, `intlit`, `dbllit`, `EOF`. **These constants are plain strings**, not enums, because they double as terminals in our LL(1) grammar and as keys in the parser's predict-set table  -  readability and hashability without enum overhead. **The `Token` class is intentionally minimal  -  no methods, no comparisons, no display logic**  -  so that the parser, semantic analyzer, ICG, and interpreter can read tokens cheaply and the IDE can render them uniformly via the helper `get_token_description`. **Errors and positions stay structured** all the way to the IDE so the frontend can highlight the exact line and column of any problem."

---

*Next file in the defense-prep series: `lexer.py` (the `Lexer` class itself)  -  character scanning, token recognition, every kind of literal, and how lexical errors are reported and recovered.*


---

# GAL Compiler  -  Defense-Prep Walkthrough

## File 3 of 9: `lexer.py`  -  the `Lexer` class itself

This is the **scanner** (lexical analyzer) of GAL. It is where raw character text becomes a stream of tokens. The file is large (~1900 lines) because GAL has 26 reserved words, 5 data types, ~20 operators, 5 literal kinds, two comment styles, and strict per-keyword delimiter rules. The entire file is built around **one big function**: `Lexer.make_tokens()`.

---

## 1. FILE PURPOSE

`lexer.py` performs **lexical analysis**  -  phase 1 of compilation. Its responsibilities:

1. Read the GAL source code character by character.
2. Group characters into **lexemes** and tag each with a **token type** (a `Token` object).
3. **Track line and column** so every token knows where it came from in the source.
4. **Detect lexical errors** (illegal characters, malformed numbers, unclosed strings/comments, bad delimiters) and produce `LexicalError` objects  -  without crashing.
5. **Skip whitespace and comments** entirely (they never become tokens).
6. **Recognize keywords vs identifiers** with a transition-diagram-style hand-written FSM, one branch per starting letter.
7. Emit a final `EOF` token so the parser knows when input ends.

Where it sits in the pipeline:

```
   Source code (Python string)
            |
            v
   +------------------+
   | Lexer (this file)|
   +------------------+
            |
   - tokens, errors --> server.py / parser
```

What depends on it:

| File | What it imports | When used |
|---|---|---|
| `server.py` | `lex`, `get_token_description` | Every API endpoint runs `lex(source_code)` first |
| `Gal_Parser.py` | (consumes tokens, doesn't import the lexer module) | Receives tokens to drive the LL(1) parser |
| `GALsemantic.py` | `Lexer` (for some tests) | Uses `analyze_semantics(tokens)` legacy path |
| `icg.py` | (consumes tokens) | Reads the same token stream to emit display TAC |

The lexer **does not** depend on anything other than the token/Position/error classes that live at the top of the same file. That makes it easy to test in isolation.

---

## 2. IMPORTS / DEPENDENCIES

**The lexer file has zero `import` statements.** Everything it needs  -  the character classes, the token-type constants, the `Position`, `LexicalError`, and `Token` classes  -  is defined in the same file (the part covered in defense file #2 of this series).

This is intentional. The lexer must be a pure data-processing function with no side effects beyond producing tokens. By avoiding imports, we guarantee:

- It can be unit-tested without setting up Flask, Socket.IO, or eventlet.
- It has no hidden global state from other modules.
- Removing or renaming any import in `server.py` cannot break tokenization.

**Defense answer:** *"The lexer is self-contained. The only data structures it uses are defined in the same file. This isolates the most-tested, most-critical phase of the compiler from runtime concerns."*

---

## 3. GLOBAL CONSTANTS / VARIABLES

The lexer relies on the constants defined at the top of `lexer.py` (these were covered in defense file #2). Briefly:

- **Character classes**  -  `ZERO`, `DIGIT`, `ZERODIGIT`, `LOW_ALPHA`, `UPPER_ALPHA`, `ALPHA`, `ALPHANUM`  -  used to test `if self.current_char in ALPHA:` etc.
- **Delimiter sets**  -  `space_delim`, `delim2` ... `delim24`, `idf_delim`, `whlnum_delim`, `decim_delim`  -  each one is the set of characters that may legally follow a particular kind of token. The actively-used ones (`space_delim`, `delim4`, `delim6`, `delim7`, `delim8`, `delim23`, `idf_delim`, `whlnum_delim`, `decim_delim`) drive lookahead checks in the scanner. The numbered ones are kept as 1-to-1 documentation mapping back to the GAL proposal's regular-definition table.
- **Token-type constants** (`TT_*`)  -  what each emitted `Token` is tagged with.

The `Lexer` instance itself owns three pieces of state:

```python
self.source_code   # the raw input string
self.pos           # a Position(index, line, col)  -  current scan location
self.current_char  # the character at self.pos.index, or None at EOF
```

That's it. No caches, no counters outside the loop. Everything else lives in local variables of `make_tokens()`.

---

## 4. CLASSES AND FUNCTIONS

This file exposes one class (`Lexer`) and two module-level functions (`run` and `lex`). The `Lexer` class has three methods.

### 4.1 `Lexer.__init__(source_code)` (lines 307-311)

```python
def __init__(self, source_code):
    self.source_code = source_code.replace('\r', '')
    self.pos = Position(-1, 1, -1)
    self.current_char = None
    self.advance()
```

**Receives:** the full GAL source code as a Python string.

**Returns / modifies:** populates the three instance fields and primes `current_char` to the first character of the source.

**Why it exists:** sets up scanner state. The `\r` strip handles Windows line endings (`\r\n`) so the rest of the lexer only ever has to consider `\n`.

**Why `Position(-1, 1, -1)`:** the position starts *before* the first character. The very first call to `self.advance()` will move it to index 0, line 1, column 0  -  the actual start of the source.

**Compiler stage:** Lexical (setup).

### 4.2 `Lexer.advance()` (lines 313-317)

```python
def advance(self):
    self.pos.advance(self.current_char)
    self.current_char = (
        self.source_code[self.pos.index]
        if self.pos.index < len(self.source_code) else None
    )
```

**Receives:** nothing.

**Returns / modifies:** `self.pos` is incremented (line/column updated based on the *previous* `current_char`); `self.current_char` is set to the next source character or `None` if past the end.

**Why it exists:** every scanner branch in `make_tokens` calls `self.advance()` to move forward by one character. Centralizing it ensures consistent line/column tracking.

**Edge case:** when EOF is reached, `self.current_char` becomes `None`. Every scanner branch checks `is not None` before reading.

### 4.3 `Lexer.make_tokens()` (lines 319-1832  -  the heart of the lexer)

```python
def make_tokens(self):
    tokens = []
    line = 1
    errors = []
    pos = self.pos.copy()
    while self.current_char != None:
        # ... one big if-elif-else over current_char ...
    if self.current_char is None:
        tokens.append(Token(TT_EOF, "", line, pos.col))
    return tokens, errors
```

**Receives:** nothing (operates on `self.source_code`).

**Returns:** the tuple `(tokens, errors)`  -  a list of `Token` objects and a list of `LexicalError` objects.

**Why it exists:** this is the scanner. Every character of the source goes through this loop exactly once. Each iteration recognizes one lexeme and emits at most one token (whitespace and comments emit nothing).

**Edge cases:**
- Empty source: the `while` loop never runs, EOF is appended, `(([EOF], [])` is returned.
- Source with only comments: tokens list contains only EOF.
- Source with only errors: tokens list may still contain valid tokens before/after each error.

**Defense framing:** *"Make_tokens is one big dispatch. The first character of each lexeme decides which branch to take. Inside each branch we keep reading characters as long as they belong to the current token, then emit it. Errors are collected  -  never raised  -  so we can report multiple problems in one pass."*

### 4.4 `run(source_code)` and `lex(source_code)` module-level helpers (lines 1838-1880)

```python
def run(source_code):
    """Legacy function - runs lexer and returns tokens and errors."""
    lexer = Lexer(source_code)
    return lexer.make_tokens()

def lex(source_code):
    """Main entry point for lexical analysis (used by server.py)."""
    lexer = Lexer(source_code)
    tokens, errors = lexer.make_tokens()
    str_errors = [e.as_string() if hasattr(e, 'as_string') else str(e)
                  for e in errors]
    return tokens, str_errors
```

**Why two:**

- `run()` is the **legacy** entry point (kept for older grading/test scripts that imported it). Returns raw `LexicalError` objects.
- `lex()` is the **production** entry point used by `server.py`. It additionally converts each error into its formatted string via `as_string()`, because the HTTP/JSON layer needs strings, not Python objects.

**Stage:** Lexical (public interface).

**Defense answer for "why two?":** *"`run` is kept for backwards compatibility with grading scripts. `lex` is what the server uses  -  it adds error-to-string conversion so the JSON response is ready to serialize."*

---

## 5. LINE-BY-LINE / BLOCK-BY-BLOCK EXPLANATION

The body of `make_tokens` is a huge `if ... elif ... elif ... else` chain. I'll walk the most important branches in the order they appear. Every branch follows the same pattern: detect the start character -> consume the lexeme -> emit a token (or an error) -> `continue` the loop.

### 5.1 The keyword/identifier scanner  -  letter-by-letter FSM (lines 338-940)

```python
if self.current_char in ALPHA:
    ident_str = ''
    pos = self.pos.copy()

    if self.current_char == "b":
        ident_str += self.current_char
        self.advance()
        if self.current_char == "r":  # branch
            ident_str += self.current_char
            self.advance()
            if self.current_char == "a":
                ...
                # eventually:
                if self.current_char is None or self.current_char in space_delim:
                    tokens.append(Token(TT_RW_BRANCH, ident_str, line, pos.col))
                    continue
        elif self.current_char == "u":
            ...  # bud / bundle
    elif self.current_char == "c":
        ...  # cultivate
    elif self.current_char == "e":
        ...  # empty
    elif self.current_char == "f":
        ...  # frost / fertile
    elif self.current_char == "g":
        ...  # grow
    # ... and so on for h, l, p, r, s, t, v, w
```

**What this block does:** Hand-written transition diagram. For each letter the source could start with that begins a GAL keyword, there is an explicit nested `if` chain that walks character-by-character down the keyword's spelling. If the chain completes AND the next character is a valid delimiter (space, `;`, `{`, etc.), a keyword `Token` is emitted.

**Why hand-written and not regex/dictionary?**

- **Visibility for the panel**: this is the implementation of the **transition diagrams** in the GAL compiler proposal. Each `if` chain corresponds to one DFA path in the spec. A panelist can point at any `if "h"` branch and it maps directly to the proposal's "harvest" transition diagram.
- **Per-keyword delimiter rules**: GAL is strict about what may come after each keyword. `bud` requires `:` or `(` to follow (delim4); `fertile` requires `;` (delim8); `plant` allows `;`, `(`, `,`, etc. (delim6). With a regex-based approach, this would all be a separate validation step. With the hand-written FSM, the delimiter check is in-line right where the keyword is recognized.
- **Identifier fallback**: if the chain breaks (e.g., `b` is followed by `e`, not `r` or `u`), control falls through to a generic "scan an identifier" loop that runs at the end of the block (lines 802-940 in the file). The result is `Token('id', ident_str, ...)`.

**Why the spec-derived scanner uses delimiter sets:**

```python
if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim4:
    tokens.append(Token(TT_RW_CULTIVATE, ident_str, line, pos.col))
    continue
elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim4 and self.current_char not in ALPHANUM:
    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
    self.advance()
    continue
```

This pattern repeats for every keyword. The two cases are:

1. **Valid delimiter** (`delim4` for `cultivate`)  -  emit the keyword token, continue.
2. **Invalid non-alphanumeric delimiter** (e.g., `cultivate$`)  -  report a delimiter error.

The third implicit case  -  character is alphanumeric  -  means the keyword spelling matched a *prefix* but the user actually typed a longer identifier (e.g., `cultivate1`). Control falls out of the keyword branch and into the generic identifier loop, which builds `Token('id', 'cultivate1')`.

**Defense answer:** *"The keyword scanner is a hand-written transition diagram, one branch per starting letter. This mirrors the FSMs documented in our compiler proposal. After spelling out each keyword, we check that the next character is a valid delimiter for that specific keyword  -  for example, `cultivate` may only be followed by `:`, `(`, or whitespace because it's a control-flow header. If the next character is alphanumeric instead, we treat the prefix as part of an identifier."*

### 5.2 The negative-literal scanner  -  `~` (lines 991-1049)

This is the most distinctive part of GAL  -  `~` is the negative sign.

```python
elif self.current_char == "~":  # Added for negative prefix
    ident_str = self.current_char
    pos = self.pos.copy()
    self.advance()

    # If ~ is directly followed by a digit, consume the number as a negative literal
    if self.current_char is not None and self.current_char in ZERODIGIT:
        # Read integer digits
        num_str = ""
        integer_digit_count = 0
        while self.current_char is not None and self.current_char in ZERODIGIT:
            integer_digit_count += 1
            num_str += self.current_char
            self.advance()

        # Check for decimal point (negative double)
        if self.current_char == ".":
            ...
            tokens.append(Token(TT_DOUBLELIT, ident_str, line, pos.col))
            continue
        else:
            # Negative integer
            if integer_digit_count > 8:
                errors.append(LexicalError(pos, f"Integer exceeds maximum of 8 digits"))
                continue
            num_str = num_str.lstrip("0") or "0"
            ident_str = "~" + num_str
            tokens.append(Token(TT_INTEGERLIT, ident_str, line, pos.col))
            continue

    # ~ not followed by a digit: emit as negate operator
    elif self.current_char is None or self.current_char in ALPHANUM + ' \t\n':
        tokens.append(Token(TT_NEGATIVE, ident_str, line, pos.col))
        continue
    else:
        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'."))
        self.advance()
        continue
```

**What this block does:** The lexer treats `~` two different ways depending on what comes next:

1. **`~` followed by a digit** (e.g., `~5`, `~3.14`)  -  fold the sign into a literal token. The result is a single `Token('intlit', '~5', ...)` or `Token('dbllit', '~3.14', ...)`. The `~` stays in the value string so the interpreter can recognize it later and emit a real negative number.
2. **`~` followed by an identifier or a paren** (e.g., `~x`, `~(a + b)`)  -  emit a separate `Token('~', '~', ...)` (the `TT_NEGATIVE` operator). The parser's grammar treats this as a unary minus prefix on an expression.

**Why both behaviors:** for literals, folding the sign at lex time means the parser never needs a "unary minus" production in front of every integer or double  -  the literal already carries the sign. For variables, we *can't* fold because the value isn't known yet, so we keep the operator as a separate token.

**Defense answer:** *"GAL uses `~` for negation. The lexer pre-folds `~5` into a single negative integer literal at scan time, but emits `~` as a separate operator token when it precedes an identifier. This avoids a unary-minus production in the grammar for the literal case."*

### 5.3 Maximal-munch operator scanners (lines 1051-1283)

```python
elif self.current_char == "!":
    ident_str = self.current_char
    pos = self.pos.copy()
    self.advance()
    if self.current_char == "=":
        ident_str += self.current_char
        self.advance()
        tokens.append(Token(TT_NOTEQ, ident_str, line, pos.col))
        continue
    else:
        tokens.append(Token(TT_NOT, ident_str, line, pos.col))
        continue
```

**Pattern:** when the current character could start either a 1-char or a 2-char operator (e.g., `!` could be NOT or `!=`), we read the first char, **peek** at the next, and decide:

- If the next char extends the operator -> emit the longer token.
- Otherwise -> emit the shorter token.

This is **maximal munch**  -  the classic lexer rule "always grab the longest valid token."

**Operators handled this way:**

| Single | Double | Triple-extended |
|---|---|---|
| `!` | `!=` |  -  |
| `=` | `==` | `===` is detected by the parser as `==` followed by `=` (we deliberately don't make a `TT_TRIPLEEQ` token; the parser issues a friendlier error) |
| `<` | `<=` |  -  |
| `>` | `>=` |  -  |
| `+` | `++`, `+=` |  -  |
| `-` | `--`, `-=` |  -  |
| `*` | `**`, `*=` |  -  |
| `/` | `/=`, also `//` (single-line comment), `/*` (multi-line comment) |  -  |
| `%` | `%=` |  -  |
| `&` | `&&` |  -  (single `&` is captured as `TT_SINGLE_AND` so the parser can flag it as invalid) |
| `\|` | `\|\|` |  -  (single `\|` is captured as `TT_SINGLE_OR`) |

**Why we emit `TT_SINGLE_AND` and `TT_SINGLE_OR`:** if the user writes `a & b`, the lexer doesn't crash  -  it produces a token with type `&`. The parser's grammar has no rule that accepts `&` alone, so it produces the error *"Invalid operator '&'. Did you mean '&&'?"*. By passing it through as a token, error reporting happens at the layer that knows the most context.

**Defense answer for maximal munch:** *"For multi-character operators we use the maximal-munch rule. We read one character, peek the next, and if together they form a longer operator we emit the longer token. This is what a textbook lexer does and resolves all ambiguity between e.g. `=` (assignment) and `==` (equality)."*

**Defense answer for `&` and `|`:** *"We tokenize single ampersand and single pipe as `TT_SINGLE_AND` and `TT_SINGLE_OR`  -  token types that the parser explicitly does not accept. This means the user gets a syntax error at the parser layer with the full grammar context, instead of a misleading lexical error."*

### 5.4 Newline, tab, space  -  whitespace handling (lines 1286-1313)

```python
elif self.current_char == '\n':
    pos = self.pos.copy()
    if tokens and tokens[-1].type != TT_NL:
        tokens.append(Token(TT_NL, "\\n", line, pos.col))
    while self.current_char == '\t' or self.current_char == ' ' or self.current_char == '\n':
        if self.current_char == '\t' or self.current_char == ' ':
            self.advance()
        else:
            line += 1
            self.advance()
    continue

elif self.current_char == '\t':
    ident_str = self.current_char
    pos = self.pos.copy()
    while self.current_char == '\t':
        self.advance()
    continue

elif self.current_char == ' ':
    ident_str = self.current_char
    pos = self.pos.copy()
    self.advance()
    while self.current_char == ' ':
        self.advance()
    continue
```

**What this block does:**

- A single `\n` token is emitted to mark the end of a logical line, but **only if** the last token wasn't already a `\n`  -  this collapses multiple consecutive blank lines into one newline token.
- The inner `while` loop advances past *all* contiguous whitespace (spaces, tabs, newlines), so the next iteration of the outer loop starts at a real character.
- For tabs and spaces alone, the consumed whitespace is discarded entirely (no token emitted).

**Why emit `TT_NL` tokens at all when the parser is configured to skip them?** Because the lexer's *line counter* depends on counting newlines. The token is also useful for error recovery and for the IDE's lexeme view. The parser is configured with `skip_token_types={'\n'}` so it transparently ignores them during parsing.

**Why the `if tokens and tokens[-1].type != TT_NL` guard:** Prevents a sequence like `\n\n\n\n` from emitting four `TT_NL` tokens  -  only one is needed.

**Defense answer:** *"Whitespace is consumed but not emitted as tokens, except newlines. Newlines are emitted exactly once per logical line break so the parser's line tracking and the IDE's lexeme view stay accurate. The parser is configured to skip newline tokens during shift operations."*

### 5.5 Forward slash  -  division, comments, and divide-assign (lines 1318-1370)

```python
elif self.current_char == "/":
    ident_str = self.current_char
    pos = self.pos.copy()
    self.advance()

    if self.current_char == "/":  # Single-line comment: // comment text
        ident_str += self.current_char
        self.advance()
        while self.current_char is not None and self.current_char != "\n":
            ident_str += self.current_char
            self.advance()
        continue

    elif self.current_char == "*":  # Multi-line comment: /* ... */
        ident_str += self.current_char
        self.advance()
        found_close = False
        while self.current_char is not None:
            if self.current_char == "*" and self.pos.index + 1 < len(self.source_code) and self.source_code[self.pos.index + 1] == "/":
                ident_str += "*/"
                self.advance()
                self.advance()
                found_close = True
                break
            else:
                ident_str += self.current_char
                if self.current_char == "\n":
                    line += 1
                self.advance()
        if not found_close:
            errors.append(LexicalError(pos, f"Missing closing '*/' after '{ident_str}'"))
            continue
        continue

    elif self.current_char == "=":
        ident_str += self.current_char
        self.advance()
        tokens.append(Token(TT_DIVEQ, ident_str, line, pos.col))
        continue

    else:
        ...
        tokens.append(Token(TT_DIV, ident_str, line, pos.col))
        continue
```

**What this block does:** the `/` character is a four-way fork:

1. `//`  -  single-line comment. Consume everything up to (but not including) the next newline. **Comments are NOT emitted as tokens**  -  they vanish from the token stream entirely.
2. `/*`  -  multi-line comment. Consume characters until `*/` is found, tracking line numbers internally. If EOF is reached before `*/`, report *"Missing closing '*/'"*.
3. `/=`  -  divide-assign operator.
4. Plain `/`  -  division operator.

**Why comments don't become tokens:** they have zero meaning to the parser or any later stage. Suppressing them at the lexer level keeps every later layer simpler.

**Multi-line comment edge case  -  line counting:** because a `/* ... */` block can span many lines, we explicitly increment `line` whenever we consume a newline inside the comment. Otherwise error messages after a multi-line comment would point at the wrong line.

**Defense answer:** *"The forward slash has four meanings  -  comment, multi-line comment, divide-assign, division. We resolve them by peeking at the next character. Comments are consumed but never emitted; they don't reach the parser. Unclosed multi-line comments produce a lexical error with the position of the opening `/*`."*

### 5.6 Number scanner  -  integers and doubles (lines 1418-1625)

```python
elif self.current_char in ZERODIGIT:
    dot_count = 0
    ident_str = ""
    pos = self.pos.copy()
    integer_digit_count = 0
    fractional_digit_count = 0

    # Read all digits before decimal point
    while self.current_char is not None and self.current_char in ZERODIGIT:
        integer_digit_count += 1
        ident_str += self.current_char
        self.advance()

    # Check for decimal point (converts to double/float)
    if self.current_char == ".":
        # ... read fractional part ...
        # ... validate digit limits ...
        tokens.append(Token(TT_DOUBLELIT, ident_str, line, pos.col))
        continue

    # No decimal point  -  emit as integer
    if integer_digit_count > 8:
        # Process integer part in chunks of 8: each chunk beyond the valid last <=8 digits is an error
        ...
    tokens.append(Token(TT_INTEGERLIT, remaining, line, pos.col))
    continue
```

**What this block does:** When the current char is a digit (0-9):

1. Read all consecutive digits  -  the integer part.
2. If the next character is `.`, this is a double  -  read the fractional part too.
3. Validate against GAL's digit limits:
   - **Integer (`seed`)**: max 8 digits.
   - **Double (`tree`)**: max 15 digits before decimal, max 8 digits after.
4. Format the value (strip leading zeros from integer part, drop trailing zeros from fractional part, ensure at least one fractional digit).
5. Emit `TT_INTEGERLIT` or `TT_DOUBLELIT`.

**Edge case  -  leading zero stripping:**

```python
remaining = remaining.lstrip("0") or "0"
```

The `or "0"` is a Python idiom: if `lstrip("0")` returns the empty string (i.e., the input was all zeros like `"0000"`), keep one zero so the number isn't lost.

**Edge case  -  trailing zero handling on doubles:**

```python
fractional_part = (parts[1] if len(parts) > 1 else "").rstrip("0") or "0"
if fractional_part == "0":
    num_str = f"{integer_part}.0"
else:
    num_str = f"{integer_part}.{fractional_part}"
```

`3.140` becomes `3.14`; `3.000` becomes `3.0` (we always keep at least one zero after the decimal so it's still recognizable as a double). This keeps display consistent.

**Defense answer:** *"The number scanner reads all consecutive digits, then checks for a decimal point. We enforce the digit limits documented in the GAL specification  -  8 digits for integers, 15 left and 8 right for doubles. We also normalize the displayed value: strip leading zeros, drop trailing zeros after the decimal but keep at least one."*

### 5.7 String literal scanner  -  `"..."` (lines 1631-1692)

```python
elif self.current_char == '"':
    string = ''
    pos = self.pos.copy()
    escape_character = False
    string += self.current_char  # opening quote
    self.advance()

    escape_characters = {
        'n': '\n', 't': '\t',
        '{': '\\{', '}': '\\}',
        '"': '"', '\\': '\\',
    }

    has_string_error = False
    while self.current_char is not None and (self.current_char != '"' or escape_character):
        if escape_character:
            if self.current_char in escape_characters:
                string += escape_characters[self.current_char]
            else:
                errors.append(LexicalError(pos, f"Invalid escape sequence '\\{self.current_char}'..."))
                has_string_error = True
            escape_character = False
        else:
            if self.current_char == '\\':
                escape_character = True
            elif self.current_char == '\n':
                break  # newline ends the string (unclosed)
            else:
                string += self.current_char
        self.advance()

    if self.current_char == '"':
        string += self.current_char
        self.advance()
    else:
        errors.append(LexicalError(pos, f"Missing closing '\"' for string literal"))
        continue

    tokens.append(Token(TT_STRINGLIT, string, line, pos.col))
    continue
```

**What this block does:**

1. Consume the opening `"`.
2. Read characters until the closing `"`. The `escape_character` flag tracks whether the next character is an escape continuation.
3. Recognized escapes: `\n`, `\t`, `\{`, `\}`, `\"`, `\\`. Anything else triggers an *"Invalid escape sequence"* error.
4. A literal newline (not preceded by `\`) inside a string ends the string scan; if the next char is not `"`, the string is unclosed.
5. Emit `TT_STRINGLIT` whose `value` is the **fully-parsed text** including the quotes (the parser/interpreter peel the quotes off later).

**Why escape sequences are processed at the lexer:** the value stored in the token is the **real** string (with `\n` already converted to a newline char). This matches how C compilers do it  -  the lexer is the single point that handles escapes, so every later stage sees the actual text the user intended.

**Defense answer:** *"String literals are scanned with a small state machine that tracks whether the next character is part of an escape sequence. Recognized escapes are `\\n`, `\\t`, `\\{`, `\\}`, `\\\"`, `\\\\`. Unclosed strings produce a lexical error with the position of the opening quote so the IDE can highlight the right place."*

### 5.8 Character literal scanner  -  `'a'` (lines 1698-1777)

```python
elif self.current_char == "'":
    string = ''
    char = ''
    pos = self.pos.copy()
    string += self.current_char
    self.advance()
    has_error = False

    while self.current_char is not None and self.current_char != "'":
        if self.current_char == '\n':
            break
        elif self.current_char == '\\':
            string += self.current_char
            self.advance()
            if self.current_char in "'\\nt":
                char += f"\\{self.current_char}"
                string += self.current_char
            else:
                errors.append(LexicalError(pos, f"Invalid escape sequence..."))
                has_error = True
                break
        else:
            string += self.current_char
            char += self.current_char
        self.advance()

    if self.current_char == "'":
        string += self.current_char
        self.advance()
    else:
        errors.append(LexicalError(pos, f"Missing closing quote..."))
        continue

    inner = char.strip()
    if len(inner) == 0:
        # Empty char literal '' defaults to a space character
        ...
    elif len(inner) > 1:
        errors.append(LexicalError(pos, f"Character literal must contain exactly one character..."))
        continue

    tokens.append(Token(TT_CHARLIT, string, line, pos.col))
    continue
```

**What this block does:** Like strings, but enforces **exactly one character** between the quotes. Multi-char content like `'AB'` is rejected with *"Character literal must contain exactly one character"*.

**Special cases:**
- Empty `''` is treated as a space character (defensive default).
- Escape sequences `\n`, `\t`, `\\`, `\'` are accepted and treated as one character.
- Newline inside the literal ends scanning; reported as unclosed.

**Defense answer:** *"A character literal is exactly one character (or one escape sequence) inside single quotes. We share the escape logic with strings but require length 1. Empty `''` defaults to space because some legacy programs rely on this."*

### 5.9 Backtick  -  concatenation operator (lines 1779-1789)

```python
elif self.current_char == '`':
    pos = self.pos.copy()
    ident_str = self.current_char
    self.advance()
    if self.current_char is not None and self.current_char not in set(ALPHANUM + '(~!"\' ' + '\t' + '\n'):
        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
        self.advance()
        continue
    tokens.append(Token(TT_CONCAT, ident_str, line, pos.col))
    continue
```

**What this block does:** GAL uses backtick `` ` `` as the **string-concatenation** operator (where most languages would use `+` or `..`). It's a single-character token. The delimiter check ensures the next character is something that could legally start an operand (an identifier, a literal, a paren, etc.).

**Defense answer:** *"GAL uses backtick as the concatenation operator. We chose it because the `+` symbol is reserved for arithmetic and using a distinct character makes string-vs-number context obvious to the reader."*

### 5.10 The catch-all `else`  -  illegal characters (lines 1791-1826)

```python
else:
    pos = self.pos.copy()
    char = self.current_char

    if char == '_':
        # Underscore at start of identifier  -  special error
        ...
        if temp_str in reserved_words:
            errors.append(LexicalError(pos, f"Reserved word cannot start with a symbol: '_{temp_str}'"))
        else:
            errors.append(LexicalError(pos, f"Identifiers cannot start with a symbol: '_...'"))
        ...
        continue
    else:
        self.advance()
        errors.append(LexicalError(pos, f"Illegal Character '{char}'"))
        continue
```

**What this block does:** if no branch above matched, the character is illegal. We emit a lexical error and skip past the bad character so scanning can continue.

**Special case for `_`:** GAL identifiers must start with a letter, not an underscore. If the user wrote `_water`, we want to give a more helpful error than "illegal character"  -  we peek ahead, check if the rest of the word is a reserved word, and emit a clearer message: *"Reserved word cannot start with a symbol: '_water'"*.

**Defense answer:** *"The default branch reports any character we don't recognize as an illegal-character lexical error. We have a special path for leading underscore because that's a common typo where the user expected an identifier; we tell them specifically that identifiers must start with a letter."*

### 5.11 EOF handling and return (lines 1828-1832)

```python
if self.current_char is None:
    tokens.append(Token(TT_EOF, "", line, pos.col))

return tokens, errors
```

**What this block does:** after the main `while` loop ends (EOF reached), append a synthetic `TT_EOF` token. This is critical  -  the parser's LL(1) table uses `EOF` as the end-marker terminal. Without this token, the parser would not know when to stop.

**Defense answer:** *"The lexer always appends an EOF token at the end of input. The parser is configured with `end_marker='EOF'` and uses this synthetic token to know when valid input has ended."*

---

## 6. DEFENSE QUESTION PREPARATION

**Q: Why is the keyword scanner hand-written instead of using regex or a dictionary?**

> "Three reasons. First, it directly mirrors the transition diagrams in our compiler proposal  -  each `if` chain is one DFA path, so a panel can trace the implementation back to the spec. Second, GAL has per-keyword delimiter rules (e.g., `cultivate` requires `:` or `(` to follow)  -  a regex approach would need a separate validator. Third, the hand-written FSM cleanly falls through to the generic identifier loop when a keyword prefix doesn't complete  -  `seedling` is recognized as one identifier, not as `seed` + `ling`."

**Q: How does the lexer distinguish `seed` (keyword) from `seedy` (identifier)?**

> "After spelling out the keyword `seed`, the next character must be a valid delimiter  -  whitespace, `;`, `(`, etc. If the next character is alphanumeric (`y` in `seedy`), the FSM exits and control falls through to the generic identifier loop, which builds an `id` token whose value is `seedy`. So `seedy` is one identifier token, not two."

**Q: Why does `~` produce two different kinds of tokens?**

> "When `~` is followed by a digit, we fold the sign into the literal at lex time  -  the result is a single `intlit` or `dbllit` token whose value carries the `~`. When `~` is followed by an identifier or paren, we emit a separate `~` operator token. This means the parser doesn't need a unary-minus production for literals  -  they already arrive negated. For variables, the parser uses the `~` token as a unary prefix in expressions."

**Q: Why are comments stripped at the lexer instead of just turned into tokens that the parser ignores?**

> "Comments have no semantic role anywhere in the compiler. Carrying them through as tokens would complicate every later stage. Stripping at lex time is cleanest. We do still track line numbers carefully through multi-line comments so error messages stay accurate."

**Q: How does the lexer recover from errors? Does it stop on the first one?**

> "It never stops. Every error path appends a `LexicalError` to the errors list, calls `self.advance()` to skip past the bad character, and `continue`s the loop. This way the user sees all lexical errors in one pass instead of fixing them one at a time."

**Q: How does the lexer handle Windows line endings?**

> "In the constructor we strip `\\r` from the source: `source_code.replace('\\r', '')`. After that, the rest of the lexer only ever has to consider `\\n` for line endings. This is a defensive normalization that prevents Windows users from seeing wrong line counts."

**Q: What is maximal munch, and where do you apply it?**

> "Maximal munch is the lexer rule 'always read the longest valid token.' We apply it to every multi-character operator: `=` vs `==`, `<` vs `<=`, `+` vs `++` vs `+=`, etc. Each branch peeks at the next character and emits the longer token if applicable, otherwise the shorter one. There are no ambiguous cases that survive."

**Q: What happens if a string literal is unclosed at end of file?**

> "We detect this in the main while loop: `while self.current_char is not None and (self.current_char != '\"' or escape_character)`. If we exit the loop and `self.current_char` is `None` (EOF) or `\\n` (newline), we emit `LexicalError(pos, 'Missing closing \"...')` with the position of the *opening* quote. The lexer then returns. The parser doesn't run because the server short-circuits on lexical errors."

**Q: Why does the lexer enforce digit limits like 8 digits for integers?**

> "These are documented constraints in the GAL specification. An 8-digit cap means the user cannot accidentally write `9999999999999` and overflow the runtime's 32-bit integer logic. The lexer enforces them up front so the user gets a clear error pointing at the bad number, rather than a confusing arithmetic-overflow at runtime."

**Q: Why are there two functions  -  `run` and `lex`?**

> "`run` is a legacy entry point kept for backward compatibility with grading scripts. `lex` is the production entry used by `server.py`  -  it does the same scanning but additionally converts each `LexicalError` object to its formatted string via `as_string()`, because the JSON layer needs strings, not objects."

---

## 7. SIMPLE WALKTHROUGH EXAMPLE

Sample source:

```
root() {
    seed age = 10;
    plant(age);
    reclaim;
}
```

How the lexer scans this character by character:

| Step | `pos` | `current_char` | Branch entered | Output |
|---|---|---|---|---|
| 1 | (0,1,0) | `r` | `current_char in ALPHA` -> `r` branch -> spell `root` | `Token('root', 'root', 1, 0)` |
| 2 | (4,1,4) | `(` | `current_char == "("` | `Token('(', '(', 1, 4)` |
| 3 | (5,1,5) | `)` | `current_char == ")"` | `Token(')', ')', 1, 5)` |
| 4 | (6,1,6) | ` ` | `current_char == ' '` -> consume whitespace | (no token) |
| 5 | (7,1,7) | `{` | `current_char == "{"` | `Token('{', '{', 1, 7)` |
| 6 | (8,1,8) | `\n` | `current_char == '\n'` | `Token('\n', '\\n', 1, 8)` |
| 7 | (9,2,0) | ` ` | space-skip loop | (no token) |
| 8 | (13,2,4) | `s` | `s` branch -> spell `seed` | `Token('seed', 'seed', 2, 4)` |
| 9 | (17,2,8) | ` ` | whitespace | (no token) |
| 10 | (18,2,9) | `a` | `a` is not a keyword start letter -> identifier loop | `Token('id', 'age', 2, 9)` |
| 11 | (21,2,12) | ` ` | whitespace | (no token) |
| 12 | (22,2,13) | `=` | `=` branch -> next char is `space`, not `=` -> assignment | `Token('=', '=', 2, 13)` |
| 13 | (23,2,14) | ` ` | whitespace | (no token) |
| 14 | (24,2,15) | `1` | digit branch -> read `10` | `Token('intlit', '10', 2, 15)` |
| 15 | (26,2,17) | `;` | `;` branch | `Token(';', ';', 2, 17)` |
| 16 | (27,2,18) | `\n` | newline | `Token('\n', '\\n', 2, 18)` |
| 17 | ... | ... | continues for `plant(age);`, `reclaim;`, `}` | ... |
| last | EOF | `None` | loop ends | `Token('EOF', '', 5, 1)` |

The final `(tokens, errors)` returned to the caller:

- `tokens` is the list above (22 tokens including 4 newlines and EOF).
- `errors` is `[]` because the source is well-formed.

If instead the user typed `seed age = 10@;` (with an illegal `@`):

| Step | `current_char` | Action |
|---|---|---|
| ... | `1` then `0` | digit loop builds `10` |
| | `@` | next char isn't `.`, isn't whitespace, isn't a valid delimiter for an integer; the digit branch's delimiter check at line 1418's exit triggers -> `LexicalError(pos, "Invalid delimiter '@' after '10'")`. Lexer advances past `@` and continues. |
| | `;` | normal `;` token emitted |

The result is the same token list as the valid case, but `errors` contains one entry. The server sees `errors` is non-empty and short-circuits the pipeline at the lexical stage.

---

## 8. DEFENSE-READY EXPLANATION (memorize this)

> "**`lexer.py` is the scanner of my compiler.** **It receives** GAL source code as a Python string. **It walks the source character by character** in one pass, dispatching each character to the correct scanner branch  -  keywords, identifiers, numbers, strings, characters, operators, comments, or whitespace. **It produces** a list of `Token` objects with type, value, line, and column, plus a list of `LexicalError` objects for any problems it finds. **It never raises an exception**  -  every error is collected and the scanner advances past the bad character so we can report multiple errors in one pass. **Keywords are recognized via a hand-written transition diagram** that mirrors the FSMs in our compiler proposal. **The `~` character is special**: when it precedes a digit we fold it into a negative literal at scan time; when it precedes an identifier we emit it as a separate negation operator. **Multi-character operators use the maximal-munch rule**  -  we always emit the longest valid token. **Comments are consumed but not emitted**; they vanish from the token stream entirely. **Whitespace is skipped except for newlines**, which we emit once per logical line break so the parser can track lines. **The lexer always appends a synthetic EOF token at the end** so the parser knows when input ends. **It exposes two functions to the rest of the system**  -  `run` (legacy, returns raw error objects) and `lex` (production, returns string-formatted errors for JSON serialization)."

---

*Next file in the defense-prep series: `cfg.py` and `Gal_Parser.py`  -  the LL(1) grammar and the table-driven parser.*


---

# File 4 of 7: Parser, AST, Semantic, ICG, and Interpreter

This section continues the defense guide after `server.py`, tokens/errors, and `lexer.py`. It covers the rest of the backend compiler pipeline up to execution.

Compiler path covered here:

```text
lexer tokens -> cfg.py grammar -> Gal_Parser.py LL(1) parser -> GALsemantic.py AST builder -> GALsemantic.py semantic validator -> icg.py TAC generator -> GALinterpreter.py execution
```

Important implementation note:

- `GALsemantic.py` is not only semantic analysis. In this codebase, it also defines AST node classes and contains the AST builder.
- `icg.py` currently generates intermediate code from the validated token stream, not from the AST.
- The GAL PDF says arrays start at index 1. The current interpreter uses Python-style index checks and access, so list/vine runtime indexing is 0-based. This is a mismatch to disclose.

---

## A. Backend/cfg.py

### 1. FILE PURPOSE

`cfg.py` stores the context-free grammar and computes the FIRST, FOLLOW, and PREDICT sets used by the LL(1) parser.

It fits between lexer and parser:

```text
tokens from lexer.py + grammar sets from cfg.py -> LL1Parser in Gal_Parser.py
```

`server.py` does not directly parse the grammar. It imports `cfg`, `first_sets`, and `predict_sets`, then passes them into `LL1Parser`.

### 2. IMPORTS / DEPENDENCIES

Code:

```python
import sys
from collections import defaultdict
```

Explanation:

- `sys` is used to reconfigure console encoding on Windows.
- `defaultdict` is used for grammar sets so each non-terminal can collect terminals without manually initializing every set.
- If `defaultdict` is removed, FIRST/FOLLOW computation would need manual dictionary initialization.

### 3. GLOBAL CONSTANTS / VARIABLES

Code:

```python
EPSILON = "lambda symbol in source"
cfg = {...}
first_sets = compute_first(cfg)
follow_sets = compute_follow(cfg, first_sets)
predict_sets = compute_predict(cfg, first_sets, follow_sets)
```

Explanation:

- `EPSILON` represents an empty production.
- `cfg` is the grammar dictionary.
- `first_sets` stores what terminals can begin each non-terminal.
- `follow_sets` stores what terminals can legally follow each non-terminal.
- `predict_sets` stores the final LL(1) decision sets.
- If `predict_sets` is wrong, the parser will choose the wrong production or report syntax errors incorrectly.

### 4. CLASSES AND FUNCTIONS

`compute_first(cfg)`

- Input: grammar dictionary.
- Output: FIRST set dictionary.
- Stage: parser preparation.
- Purpose: Know which terminals can start each grammar rule.

`compute_follow(cfg, first)`

- Input: grammar and FIRST sets.
- Output: FOLLOW set dictionary.
- Stage: parser preparation.
- Purpose: Know what can appear after a non-terminal, especially when epsilon is possible.

`compute_predict(cfg, first, follow)`

- Input: grammar, FIRST, FOLLOW.
- Output: PREDICT set dictionary.
- Stage: parser preparation.
- Purpose: Build the LL(1) production-selection data.

### 5. LINE-BY-LINE / BLOCK-BY-BLOCK EXPLANATION

Code:

```python
def compute_first(cfg):
    first = defaultdict(set)
    epsilon = EPSILON
```

Explanation:

- Defines the FIRST computation function.
- `first` maps each non-terminal to a set of starting terminals.
- `epsilon` stores the empty-production symbol locally for readability.

Code:

```python
for lhs, productions in cfg.items():
    for prod in productions:
        if not prod:
            continue
        if prod[0] == epsilon:
            first[lhs].add(epsilon)
        elif prod[0] not in cfg:
            first[lhs].add(prod[0])
```

Explanation:

- Loops through every grammar rule.
- `lhs` is the non-terminal on the left side.
- `prod` is one right-side production.
- Empty productions are skipped.
- If the production directly starts with epsilon, epsilon is added.
- If the first symbol is a terminal, that terminal is added.
- This is the first pass before recursive dependencies are resolved.

Code:

```python
changed = True
while changed:
    changed = False
```

Explanation:

- FIRST sets depend on one another, so one pass is not enough.
- The loop repeats until no FIRST set changes.
- This is a fixed-point algorithm.

Code:

```python
if symbol in cfg:
    first[lhs] |= (first[symbol] - {epsilon})
    if epsilon not in first[symbol]:
        break
else:
    if symbol != epsilon:
        first[lhs].add(symbol)
    break
```

Explanation:

- If a production symbol is a non-terminal, copy its FIRST set into the current rule.
- Epsilon is excluded first because epsilon does not consume input.
- If that non-terminal cannot become epsilon, stop scanning the production.
- If the symbol is terminal, add it and stop.

### 6. DEFENSE QUESTIONS

Q: Why do you need FIRST and FOLLOW sets?

A: They turn the grammar into parser decisions. FIRST tells what can start a rule, and FOLLOW helps decide when an empty production is allowed.

Q: Why use PREDICT sets?

A: PREDICT sets tell the LL(1) parser exactly which production to use based on the current non-terminal and one lookahead token.

### 7. MEMORIZED EXPLANATION

`cfg.py` is the grammar preparation file. It stores the GAL grammar and computes FIRST, FOLLOW, and PREDICT sets. The parser uses those sets to choose grammar productions during LL(1) parsing.

---

## B. Backend/Gal_Parser.py

### 1. FILE PURPOSE

`Gal_Parser.py` performs syntax analysis using LL(1) parsing. It also bridges syntax analysis to AST construction through `parse_and_build()`.

Pipeline position:

```text
tokens -> parser.parse() -> syntax result
tokens -> parser.parse_and_build() -> syntax result + AST + symbol table
```

### 2. IMPORTS / DEPENDENCIES

Code:

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple
```

Explanation:

- Future annotations simplify type hints.
- `dataclass` is used for normalized token views.
- `typing` makes parser inputs and outputs clearer.

Code:

```python
from GALsemantic import (
    build_ast as _build_ast,
    symbol_table as _builder_st,
    SemanticError as _SemanticError,
)
```

Explanation:

- `_build_ast` is called after syntax succeeds.
- `_builder_st` is read after AST construction to serialize variables/functions.
- `_SemanticError` catches AST-building errors.
- This is why AST construction is connected to the parser even though AST node classes live in `GALsemantic.py`.

### 3. GLOBAL CONSTANTS / VARIABLES

No major global parser object is created here. The parser instance is created in `server.py`.

### 4. CLASSES AND FUNCTIONS

`_TokView`

- Input: normalized token data.
- Purpose: Give the parser a consistent token format.

`_as_tok(token)`

- Input: token object or dictionary.
- Returns: `_TokView`.
- Purpose: Make parser reusable from lexer objects or JSON-like dictionaries.

`LL1Parser.__init__`

- Receives grammar, FIRST sets, PREDICT sets, start symbol, EOF marker, skip token types, aliases.
- Builds the parsing table.

`construct_parsing_table()`

- Receives no external input except parser state.
- Returns LL(1) table.
- Detects LL(1) conflicts.

`parse(tokens)`

- Input: token sequence.
- Returns: `(success, errors)`.
- Stage: syntax analysis.

`parse_and_build(tokens)`

- Input: token sequence.
- Returns: dictionary with `success`, `errors`, `ast`, and `symbol_table`.
- Stage: syntax + AST construction.

### 5. LINE-BY-LINE / BLOCK-BY-BLOCK EXPLANATION

Code:

```python
@dataclass(frozen=True)
class _TokView:
    type: str
    value: str
    line: int
    col: int = 0
```

Explanation:

- `_TokView` is a read-only token representation.
- The parser only needs token type, value, line, and column.
- `frozen=True` means parser logic cannot accidentally mutate token data.

Code:

```python
def _as_tok(token):
    if isinstance(token, Mapping):
        return _TokView(...)
    return _TokView(...)
```

Explanation:

- If the input token is a dictionary, fields are read with `.get()`.
- If it is a lexer `Token` object, fields are read with `getattr()`.
- This protects the parser from depending on only one token representation.

Code:

```python
class LL1Parser:
    def __init__(self, cfg, predict_sets, first_sets, *, start_symbol="<program>", end_marker="EOF", epsilon_symbols=(...), skip_token_types=None, token_type_alias=None):
        self.cfg = cfg
        self.predict_sets = predict_sets
        self.first_sets = first_sets
```

Explanation:

- Defines the parser class.
- Receives grammar and parsing sets from `cfg.py`.
- Stores start symbol and EOF marker.
- Allows skipped token types such as newline.
- Allows token aliases when lexer names and grammar names differ.

Code:

```python
self.skip_token_types = set(skip_token_types or {"\n"})
self.token_type_alias = token_type_alias or {
    'idf': 'id',
    'dbllit': 'dblit',
}
self.parsing_table = self.construct_parsing_table()
```

Explanation:

- Newline is skipped by default.
- Token aliases handle naming inconsistencies.
- The parsing table is built immediately when the parser is constructed.

Code:

```python
def construct_parsing_table(self):
    table = {}
    for non_terminal, productions in self.cfg.items():
        row = {}
```

Explanation:

- Creates the LL(1) table.
- Each non-terminal gets one row.

Code:

```python
key = (non_terminal, tuple(production))
terms = self.predict_sets.get(key, set())
for terminal in terms:
    if terminal in row and row[terminal] != production:
        raise ValueError(...)
    row[terminal] = production
```

Explanation:

- Looks up the PREDICT set for that production.
- For each lookahead terminal, stores which production to use.
- If two productions claim the same lookahead, that is an LL(1) conflict.

Code:

```python
def parse(self, tokens):
    toks = [_as_tok(t) for t in tokens]
    toks = [_TokView(self._normalize_token_type(t.type), t.value, t.line, t.col) for t in toks]
    toks = self._ensure_eof(toks)
```

Explanation:

- Converts tokens into parser view objects.
- Normalizes token type names.
- Ensures EOF exists.

Code:

```python
stack = [self.end_marker, self.start_symbol]
index = 0
```

Explanation:

- LL(1) parsing uses a stack.
- EOF is bottom marker.
- `<program>` is the first grammar symbol to expand.
- `index` points to the current input token.

Code:

```python
while stack:
    top = stack[-1]
    tok = current_token()
    token_type = tok.type
```

Explanation:

- Main parser loop.
- `top` is the grammar symbol currently being matched or expanded.
- `tok` is the current lookahead token.

Code:

```python
if token_type in self.skip_token_types and top != token_type:
    index += 1
    continue
```

Explanation:

- Skips newline tokens.
- This is the skipped token filtering requested in the defense prompt.
- It lets the lexer keep newlines while the parser ignores them.

Code:

```python
if top in self.parsing_table:
    row = self.parsing_table[top]
    if token_type in row:
        production = row[token_type]
```

Explanation:

- If `top` is a non-terminal, the parser uses the parsing table.
- The lookahead token chooses one production.

Code:

```python
stack.pop()
if production is not epsilon:
    stack.extend(reversed(production))
continue
```

Explanation:

- Removes the non-terminal.
- Pushes the right-hand side of the chosen production.
- Uses reverse order because stacks process last-in-first-out.

Code:

```python
expected = set(row.keys())
error_msg = self._generate_helpful_error(...)
return False, [error_msg]
```

Explanation:

- If no production matches, syntax fails.
- The parser generates a helpful message with expected tokens.

Code:

```python
if top == token_type:
    ...
```

Explanation:

- If the stack top is a terminal and equals the current token type, the parser consumes the token.
- This is a successful match.

Code:

```python
elif expecting_value_for_type is not None and token_type in {...}:
    type_value_map = {...}
```

Explanation:

- The parser includes extra validation for simple declaration assignments.
- This is partially semantic checking inside the parser for better immediate messages.
- Full semantic validation still happens later through `validate_ast()`.

Code:

```python
def parse_and_build(self, tokens):
    syntax_ok, syntax_errors = self.parse(tokens)
    if not syntax_ok:
        return {"success": False, "errors": syntax_errors, "ast": None, "symbol_table": {}}
```

Explanation:

- `parse_and_build()` starts by running syntax validation.
- If syntax fails, AST construction is skipped.
- This protects AST builder from invalid token order.

Code:

```python
filtered = [t for t in tokens if getattr(t, 'type', '') != '\n']
ast = _build_ast(filtered)
```

Explanation:

- Removes newline tokens before AST construction.
- Calls `build_ast()` from `GALsemantic.py`.

Code:

```python
st = {
    "variables": [...],
    "functions": {...},
}
```

Explanation:

- Converts the AST builder's symbol table into a JSON-friendly dictionary.
- Returned to server and frontend.

Code:

```python
except _SemanticError as e:
    return {"success": False, "errors": [str(e)], "ast": None, "symbol_table": {}, "error_stage": "semantic"}
```

Explanation:

- AST builder can detect semantic-like errors while building.
- The parser reports those as semantic-stage errors, not pure syntax errors.

### 6. DEFENSE QUESTIONS

Q: Why does the parser skip newline tokens?

A: The lexer emits newlines for display and accurate lines, but grammar matching should not depend on formatting. So the parser skips `\n`.

Q: Why does `parse_and_build()` parse first before building AST?

A: AST construction assumes valid structure. Parsing first prevents invalid syntax from creating a broken tree.

Q: Why are there semantic checks inside the parser?

A: Some checks are added for clearer early diagnostics, but the full semantic pass still runs after AST construction.

### 7. WALKTHROUGH EXAMPLE

For:

```gal
root() {
    seed age = 10;
    plant(age);
    reclaim;
}
```

The parser matches the grammar for `root`, parameter parentheses, function body, declaration, print statement, reclaim statement, closing brace, and EOF.

### 8. MEMORIZED EXPLANATION

`Gal_Parser.py` validates GAL syntax using LL(1) parsing. It uses the grammar and PREDICT sets from `cfg.py`, skips newline tokens, reports syntax errors, and only after successful parsing does it call the AST builder.

---

## C. Backend/GALsemantic.py: AST Nodes and AST Builder

### 1. FILE PURPOSE

`GALsemantic.py` has two responsibilities:

1. It defines AST node classes and builds the AST from validated tokens.
2. It validates the AST semantically.

This section covers the AST-building part first.

### 2. IMPORTS / DEPENDENCIES

Code:

```python
import re
```

Explanation:

- Used for pattern checks inside semantic parsing/validation.
- If removed, regex-based validation would fail where used.

### 3. GLOBAL CONSTANTS / VARIABLES

Important state:

- `symbol_table`: records variables, functions, scopes, and bundle types during AST construction.
- `context_stack`: helps know whether parser is inside loop/switch-like contexts.

Important warning:

- Because `symbol_table` is shared state, `build_ast()` resets it at the start of each compilation.

### 4. CLASSES AND FUNCTIONS

`SemanticError`

- Exception class for line-numbered semantic/syntax messages.

`ASTNode`

- Base class for all AST nodes.

AST subclasses include:

- `ProgramNode`
- `VariableDeclarationNode`
- `AssignmentNode`
- `BinaryOpNode`
- `FunctionDeclarationNode`
- `FunctionCallNode`
- `IfStatementNode`
- `ForLoopNode`
- `WhileLoopNode`
- `DoWhileLoopNode`
- `PrintNode`
- `ReturnNode`
- `SwitchNode`
- `ListNode`
- `ListAccessNode`
- `MemberAccessNode`
- `BundleDefinitionNode`

`SymbolTable`

- Tracks declarations and scopes during AST construction.

`build_ast(tokens)`

- Entry point for AST construction.

`parse_function(...)`

- Builds function declaration nodes for `root()` and `pollinate` functions.

`parse_statement(...)`

- Dispatches statements based on token type/value.

### 5. LINE-BY-LINE / BLOCK-BY-BLOCK EXPLANATION

Code:

```python
class ASTNode:
    def __init__(self, node_type, value=None, line=None):
        self.node_type = node_type
        self.value = value
        self.children = []
        self.parent = None
        self.line = line
```

Explanation:

- All AST nodes share this structure.
- `node_type` tells what kind of construct it is.
- `value` stores things like identifier names, literal values, or operators.
- `children` store nested syntax structure.
- `parent` gives reverse navigation.
- `line` supports error reporting.

Code:

```python
def add_child(self, child):
    child.parent = self
    self.children.append(child)
```

Explanation:

- Adds a child node.
- Also records the parent pointer.
- Parent pointers are used later, especially by interpreter input handling.

Code:

```python
class VariableDeclarationNode(ASTNode):
    def __init__(self, var_type, var_name, value=None, line=None):
        super().__init__("VariableDeclaration", line=line)
        self.add_child(ASTNode("Type", var_type, line=line))
        self.add_child(ASTNode("Identifier", var_name, line=line))
        if value:
            self.add_child(value)
```

Explanation:

- Represents declarations like `seed age = 10;`.
- Child 0 is type.
- Child 1 is identifier.
- Optional child 2 is initializer.
- The interpreter relies on this exact child order.

Code:

```python
class FunctionDeclarationNode(ASTNode):
    def __init__(self, return_type, name, params, line=None):
        super().__init__("FunctionDeclaration", name, line=line)
        self.add_child(ASTNode("ReturnType", return_type, line=line))
        self.add_child(params)
```

Explanation:

- Represents both `root()` and `pollinate` functions.
- Function name is stored in `value`.
- Return type and parameter list are children.
- The function body block is added later.

Code:

```python
class SymbolTable:
    def __init__(self):
        self.variables = {}
        self.global_variables = {}
        self.functions = {}
        self.scopes = [{}]
        self.current_func_name = None
        self.function_variables = {}
        self.bundle_types = {}
```

Explanation:

- Tracks declared names during AST construction.
- `variables` stores global variables.
- `functions` stores function declarations.
- `scopes` tracks local scopes.
- `current_func_name` tells whether we are inside a function.
- `function_variables` detects duplicate local variables.
- `bundle_types` stores struct-like definitions.

Code:

```python
def declare_variable(self, name, type_, value=None, is_list=False, is_fertile=False):
    scope = self.scopes[-1]
    current_func = self.current_func_name
```

Explanation:

- Declares a variable in the active scope.
- Uses the current function name to distinguish locals from globals.
- Stores whether the variable is an array/list or constant.

Code:

```python
if name in self.functions:
    return f"Semantic Error: Variable '{name}' already declared as a function."
```

Explanation:

- Prevents a variable from reusing a function name.
- This is a semantic rule because the name is lexically valid but invalid in context.

Code:

```python
def lookup_variable(self, name):
    for scope in reversed(self.scopes):
        if name in scope:
            return scope[name]
    if name in self.variables:
        return self.variables[name]
    return f"Semantic Error: Variable '{name}' used before declaration."
```

Explanation:

- Searches local scope first, then globals.
- Supports normal scoping behavior.
- Reports declaration-before-use errors.

Code:

```python
def build_ast(tokens):
    root = ProgramNode()
    symbol_table.variables = {}
    symbol_table.functions = {}
    symbol_table.scopes = [{}]
    symbol_table.function_variables = {}
    symbol_table.bundle_types = {}
    index = 0
```

Explanation:

- Creates the AST root.
- Resets old compiler state.
- Begins token scanning at index 0.
- Resetting matters because the server may compile many programs in one run.

Code:

```python
while index < len(tokens):
    token = tokens[index]
```

Explanation:

- Main AST-building loop.
- Reads top-level program constructs: global declarations, `pollinate`, `bundle`, and `root`.

Code:

```python
if tokens[index].value in {"seed", "tree", "vine", "leaf", "branch"}:
    id_type = token.value
    index += 1
    if tokens[index].type != "id":
        raise SemanticError(...)
    id_name = tokens[index].value
    index += 1
    node, index = parse_variable(tokens, index, id_name, id_type)
```

Explanation:

- Handles top-level variable declarations.
- Reads data type then identifier.
- Delegates initializer/list handling to `parse_variable()`.

Code:

```python
elif tokens[index].value in {"pollinate"}:
    index += 1
    if tokens[index].value in {"seed", "tree", "vine", "leaf", "branch", "empty"}:
        id_type = tokens[index].value
        index += 1
        id_name = tokens[index].value
        index += 1
        node, index = parse_function(tokens, index, id_name, id_type)
```

Explanation:

- Handles user-defined function declarations.
- `pollinate` must be followed by return type.
- Then function name is read.
- `parse_function()` handles parameters and body.

Code:

```python
elif token.value in {"root"}:
    func_name = token.value
    func_type = "empty"
    node, index = parse_function(tokens, index, func_name, func_type)
```

Explanation:

- Handles the main entry point.
- `root()` is treated as an empty-return function.
- Later, the interpreter explicitly calls `root()`.

Code:

```python
elif token.value == "bundle":
    bundle_name = tokens[index + 1].value
    members = {}
```

Explanation:

- Handles bundle/struct definitions.
- Collects member fields and stores the type definition.

Code:

```python
def parse_function(tokens, index, func_name, func_type):
    symbol_table.current_func_name = func_name
```

Explanation:

- Begins function parsing.
- Sets current function context so local declarations go into function scope.

Code:

```python
if func_name in {"root"}:
    symbol_table.enter_scope()
    index += 1
    if tokens[index].type == "(":
        index += 1
        if tokens[index].type != ")":
            raise SemanticError(...)
```

Explanation:

- Special handling for `root()`.
- Enters a local scope for root body.
- Requires empty parameter list.
- Rejects `root(seed x)` because root should not receive parameters.

Code:

```python
while tokens[index].type != ")":
    if tokens[index].value in {"seed", "tree", "vine", "leaf", "branch", "empty"}:
        param_type = tokens[index].value
        ...
        params_node.add_child(param_node)
        symbol_table.declare_variable(param_name, param_type, is_list=is_list)
```

Explanation:

- Parses pollinate function parameters.
- Builds parameter AST nodes.
- Declares each parameter in the function's local scope.

Code:

```python
while tokens[index].type != "}":
    stmt, index = parse_statement(tokens, index, func_type)
    if stmt:
        block_node.add_child(stmt)
        if _contains_return(stmt):
            has_any_return = True
```

Explanation:

- Parses statements inside the function body.
- Adds them to a block node.
- Tracks whether `reclaim` appears.

Code:

```python
if (func_type != "empty" and not all_paths) and func_name not in {"root"}:
    raise SemanticError(...)
```

Explanation:

- Non-empty functions must return a value on all paths.
- This enforces `reclaim value;` for functions like `pollinate seed add(...)`.

Code:

```python
if not has_any_return:
    if func_name == "root":
        raise SemanticError("root() must end with 'reclaim;'", line)
```

Explanation:

- Enforces required termination in `root()`.
- This matches the GAL specification.

Code:

```python
def parse_statement(tokens, index, func_type=None):
    token = tokens[index]
    if token.type == ";":
        return None, index + 1
```

Explanation:

- Dispatches individual statements.
- Ignores stray semicolons safely.

Code:

```python
if token.value in {"seed", "tree", "vine", "leaf", "branch"}:
    var_type = token.value
    var_name = tokens[index + 1].value
    node, index = parse_variable(tokens, index, var_name, var_type)
```

Explanation:

- Handles local variable declarations.
- Produces a `VariableDeclarationNode` or declaration list node.

Code:

```python
elif token.type == "id" and tokens[index + 1].type == "(":
    func_name = token.value
    error = symbol_table.lookup_function(func_name)
    func_call_node, index = parse_function_call(...)
```

Explanation:

- Detects function calls.
- Checks that the function exists.
- Builds a function call AST node.

### 6. DEFENSE QUESTIONS

Q: Why does `GALsemantic.py` build the AST?

A: In this implementation, AST node definitions and AST building are grouped with semantic logic. The parser calls it only after syntax succeeds.

Q: Why reset the symbol table in `build_ast()`?

A: The server can compile multiple programs. Resetting prevents old variables/functions from leaking into a new compilation.

Q: Why store parent links in AST nodes?

A: Parent links help when a node needs context. For example, the interpreter checks where an input node appears to determine the target variable and type.

### 7. WALKTHROUGH EXAMPLE

For:

```gal
seed age = 10;
plant(age);
reclaim;
```

The AST block contains:

```text
VariableDeclaration(Type seed, Identifier age, Value 10)
PrintStatement(Value age)
Return
```

### 8. MEMORIZED EXPLANATION

`GALsemantic.py` defines the AST structure and builds the tree from validated tokens. It also uses a symbol table to record declarations, scopes, functions, and bundles while building that tree.

---

## D. Backend/GALsemantic.py: Semantic Analyzer

### 1. FILE PURPOSE

After the AST is built, the semantic analyzer walks the tree and validates meaning. It checks context and structure that grammar alone cannot fully guarantee.

Examples of semantic concerns:

- Is `prune` inside a loop or switch?
- Is `skip` inside a loop?
- Is a declaration structurally complete?
- Does a function have valid return structure?
- Are blocks and expressions well formed?

### 2. CLASSES AND FUNCTIONS

`ASTValidator`

- Input: AST and serialized symbol table.
- Output: dictionary containing success, errors, warnings, symbol table, and AST.
- Stage: semantic analysis.

`validate_ast(ast, symbol_table_data)`

- Public API used by `server.py`.
- Creates a validator and returns validation result.

### 3. LINE-BY-LINE / BLOCK-BY-BLOCK EXPLANATION

Code:

```python
class ASTValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self._in_loop = 0
        self._in_switch = 0
        self._in_function = False
        self._current_func_type = None
```

Explanation:

- `errors` stores semantic errors.
- `warnings` stores non-fatal notices.
- `_in_loop` tracks loop nesting.
- `_in_switch` tracks harvest/switch nesting.
- `_in_function` tracks function context.
- `_current_func_type` tracks expected return type while walking a function.

Code:

```python
def validate(self, ast, symbol_table_data):
    self._walk(ast)
    return {
        "success": len(self.errors) == 0,
        "errors": self.errors,
        "warnings": self.warnings,
        "symbol_table": symbol_table_data,
        "ast": ast,
    }
```

Explanation:

- Starts validation by walking the AST root.
- Success is true only when no errors were collected.
- Returns the AST again so later stages can use the validated tree.

Code:

```python
def _walk(self, node):
    if node is None:
        return
    handler = getattr(self, f'_check_{node.node_type}', None)
    if handler:
        handler(node)
    else:
        for child in getattr(node, 'children', []):
            self._walk(child)
```

Explanation:

- This is recursive tree walking.
- It looks for a method named after the node type, such as `_check_FunctionDeclaration`.
- If a specific handler exists, it uses it.
- Otherwise, it walks all children by default.

Code:

```python
def _check_FunctionDeclaration(self, node):
    if not node.value:
        self.errors.append("Function declaration missing name")
    prev_in_func = self._in_function
    prev_func_type = self._current_func_type
    self._in_function = True
    if node.children:
        self._current_func_type = node.children[0].value
```

Explanation:

- Verifies the function has a name.
- Saves previous context before entering this function.
- Sets current function information while walking the body.

Code:

```python
for child in node.children:
    self._walk(child)
self._in_function = prev_in_func
self._current_func_type = prev_func_type
```

Explanation:

- Walks return type, parameters, and body.
- Restores previous context afterward.
- This prevents one function's context from leaking into another.

Code:

```python
def _check_ForLoop(self, node):
    self._in_loop += 1
    for child in node.children:
        self._walk(child)
    self._in_loop -= 1
```

Explanation:

- Marks that validation is inside a loop.
- Validates all loop children.
- Decrements loop depth afterward.

Code:

```python
def _check_Switch(self, node):
    self._in_switch += 1
    for child in node.children:
        self._walk(child)
    self._in_switch -= 1
```

Explanation:

- Marks that validation is inside a `harvest` switch.
- Needed because `prune` is valid inside a switch.

Code:

```python
def _check_Break(self, node):
    if self._in_loop == 0 and self._in_switch == 0:
        self.errors.append("'prune' used outside a loop or switch")
```

Explanation:

- `prune` is only valid in loops or harvest/switch blocks.
- If there is no loop or switch context, it is a semantic error.

Code:

```python
def _check_Continue(self, node):
    if self._in_loop == 0:
        self.errors.append("'skip' used outside a loop")
```

Explanation:

- `skip` only makes sense inside loops.
- Using it elsewhere is syntactically possible but semantically wrong.

Code:

```python
def validate_ast(ast, symbol_table_data):
    validator = ASTValidator()
    return validator.validate(ast, symbol_table_data)
```

Explanation:

- This is the public function called by `server.py`.
- It creates a fresh validator for every compilation.
- It returns a dictionary that the server can send as JSON.

### 4. DEFENSE QUESTIONS

Q: Why validate semantics after AST construction?

A: The AST gives structured meaning. It is easier to validate loops, functions, returns, and nested statements after syntax is organized as a tree.

Q: Why use counters like `_in_loop` instead of booleans?

A: Loops can be nested. A counter correctly handles multiple levels of nesting.

Q: Why collect errors instead of immediately throwing?

A: The validator can gather semantic issues in a structured result and return them to the frontend.

### 5. MEMORIZED EXPLANATION

`validate_ast()` is the semantic validation phase. It walks the AST and checks context-sensitive rules, such as whether `prune` and `skip` are used in valid locations and whether AST structures are complete.

---

## E. Backend/icg.py

### 1. FILE PURPOSE

`icg.py` generates intermediate code, specifically three-address code or TAC. This is a lower-level representation of the program.

Pipeline position:

```text
validated token stream -> generate_icg() -> TAC list + TAC text
```

Important implementation detail:

- The ICG module reads tokens directly.
- The server validates lexer, parser, AST, and semantic stages before calling ICG.

### 2. IMPORTS / DEPENDENCIES

Code:

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
```

Explanation:

- Future annotations support cleaner type hints.
- `dataclass` is used for token views and TAC instructions.
- `typing` documents the structures passed around.
- `field` appears possibly unused in this file; do not remove during defense unless verified.

### 3. GLOBAL CONSTANTS / VARIABLES

Code:

```python
GAL_TYPE_MAP = {
    "seed": "int",
    "tree": "float",
    "leaf": "char",
    "branch": "bool",
    "vine": "string",
    "empty": "void",
}
DATA_TYPE_TOKENS = set(GAL_TYPE_MAP.keys())
ASSIGN_OPS = {"=", "+=", "-=", "*=", "/=", "%="}
```

Explanation:

- `GAL_TYPE_MAP` converts GAL type names into conventional intermediate-code type names.
- `DATA_TYPE_TOKENS` lets the generator quickly ask whether a token is a type.
- `ASSIGN_OPS` lists assignment operators that ICG can translate.

### 4. CLASSES AND FUNCTIONS

`_Tok`

- Normalized token view for ICG.

`_as_tok(raw)`

- Converts lexer tokens or dictionaries into `_Tok`.

`TACInstruction`

- Represents one intermediate instruction with `op`, `arg1`, `arg2`, and `result`.

`ICGenerator`

- Main class that reads tokens and emits TAC.

`generate_icg(tokens)`

- Public API used by `server.py`.

### 5. LINE-BY-LINE / BLOCK-BY-BLOCK EXPLANATION

Code:

```python
@dataclass(frozen=True)
class _Tok:
    type: str
    value: str
    line: int
    col: int = 0
```

Explanation:

- Gives ICG a stable token format.
- Prevents ICG from depending on the exact lexer `Token` class.

Code:

```python
@dataclass
class TACInstruction:
    op: str
    arg1: Optional[str] = None
    arg2: Optional[str] = None
    result: Optional[str] = None
```

Explanation:

- Stores one TAC instruction.
- `op` is the operation.
- `arg1` and `arg2` are operands.
- `result` is destination or label depending on the instruction.

Code:

```python
def __str__(self):
    if self.op == "LABEL":
        return f"{self.result}:"
    if self.op == "GOTO":
        return f"goto {self.result}"
    if self.op == "PRINT":
        return f"print {self.arg1}"
```

Explanation:

- Converts TAC objects into human-readable TAC text.
- This is what `/api/icg` can display in the frontend.

Code:

```python
class ICGenerator:
    def __init__(self, tokens):
        self.tokens = self._prepare(tokens)
        self.pos = 0
        self.code = []
        self.errors = []
        self._temp_counter = 0
        self._label_counter = 0
```

Explanation:

- Prepares tokens by normalizing and skipping newlines.
- `pos` tracks current token index.
- `code` stores generated instructions.
- `errors` stores ICG errors.
- Counters generate temporary names and labels.

Code:

```python
def _prepare(self, raw_tokens):
    toks = []
    for t in raw_tokens:
        tv = _as_tok(t)
        if tv.type == "\n":
            continue
        toks.append(tv)
```

Explanation:

- Filters newline tokens, similar to parser and AST builder.
- ICG does not need newline tokens to generate code.

Code:

```python
if not toks or toks[-1].type != "EOF":
    toks.append(_Tok("EOF", "EOF", last_line))
```

Explanation:

- Ensures the token stream has EOF.
- EOF prevents reading beyond the input.

Code:

```python
def _emit(self, op, arg1=None, arg2=None, result=None):
    self.code.append(TACInstruction(op, arg1, arg2, result))
```

Explanation:

- Central helper for creating TAC.
- Every declaration, expression, loop, and statement uses this to append instructions.

Code:

```python
def _new_temp(self):
    name = f"t{self._temp_counter}"
    self._temp_counter += 1
    return name
```

Explanation:

- Generates temporary variables like `t0`, `t1`.
- Used for intermediate expression results.

Code:

```python
def _new_label(self):
    name = f"L{self._label_counter}"
    self._label_counter += 1
    return name
```

Explanation:

- Generates labels like `L0`, `L1`.
- Used for jumps in loops and conditionals.

Code:

```python
def generate(self):
    try:
        self._program()
    except Exception as exc:
        self.errors.append(f"ICG internal error: {exc}")
    return self.code, self.errors
```

Explanation:

- Starts generating TAC from the whole program.
- Catches unexpected generator failures.
- Returns generated code and errors.

Code:

```python
def _program(self):
    self._global_declaration()
    self._function_definition()
    self._expect("root")
    self._expect("(")
    self._expect(")")
    self._expect("{")
    self._emit("FUNC", "root")
```

Explanation:

- Follows GAL program structure.
- Handles globals and pollinate functions before `root`.
- Emits a TAC function start for root.

Code:

```python
self._declaration()
self._statement()
```

Explanation:

- Emits declarations first.
- Emits executable statements next.
- Mirrors the GAL rule that local declarations come before statements.

Code:

```python
if self._peek().type == "reclaim":
    self._advance()
    if self._peek().type != ";":
        val = self._expression()
        self._emit("RETURN", val)
    else:
        self._emit("RETURN")
```

Explanation:

- Converts `reclaim;` or `reclaim expression;` into TAC return.
- For `root()`, return usually has no value.

Code:

```python
def _simple_stmt(self):
    if tok.type == "id":
        self._id_stmt()
    elif tok.type in ("water", "plant"):
        self._io_stmt()
    elif tok.type == "spring":
        self._conditional_stmt()
    elif tok.type in ("grow", "cultivate", "tend"):
        self._loop_stmt()
```

Explanation:

- Dispatches based on statement starter token.
- Each GAL construct has its own TAC generation path.

Code:

```python
if op_tok.type == "=":
    self._emit("=", rhs, None, lhs)
else:
    base_op = op_tok.type[0]
    tmp = self._new_temp()
    self._emit(base_op, lhs, rhs, tmp)
    self._emit("=", tmp, None, lhs)
```

Explanation:

- Assignment becomes one TAC instruction.
- Compound assignment becomes operation plus assignment.
- Example: `x += y` becomes `t0 = x + y`, then `x = t0`.

Code:

```python
def _while_loop(self):
    start_label = self._new_label()
    end_label = self._new_label()
    self._emit("LABEL", None, None, start_label)
    cond = self._expression()
    self._emit("IFFALSE", cond, None, end_label)
    self._statement()
    self._emit("GOTO", None, None, start_label)
    self._emit("LABEL", None, None, end_label)
```

Explanation:

- `grow` loop is translated into labels and jumps.
- If condition is false, jump to end.
- After body, jump back to start.

Code:

```python
def _expression(self):
    return self._logic_or()
```

Explanation:

- Expression generation starts at the lowest precedence level.
- Deeper functions handle logical, relational, arithmetic, and factor parsing.

Code:

```python
def generate_icg(tokens):
    gen = ICGenerator(tokens)
    code, errors = gen.generate()
    tac_dicts = [instr.to_dict() for instr in code]
    tac_text = "\n".join(str(instr) for instr in code)
    return {...}
```

Explanation:

- Public API called by `server.py`.
- Creates a generator, runs it, converts instructions to JSON-friendly dictionaries and readable text.

### 6. DEFENSE QUESTIONS

Q: Why have ICG if the interpreter can run the AST?

A: ICG shows an intermediate compiler representation. It can be used for future optimization or target-code generation, while the interpreter is for immediate execution.

Q: Why use temporary variables?

A: TAC breaks complex expressions into simple operations with at most two operands.

Q: Why use labels?

A: Loops and conditionals need jump targets. Labels represent those targets.

### 7. WALKTHROUGH EXAMPLE

For the sample program, ICG output is:

```text
func root:
declare age : int
age = 10
print age
return
endfunc
```

### 8. MEMORIZED EXPLANATION

`icg.py` converts validated GAL tokens into three-address code. It emits declarations, assignments, labels, jumps, input/output, function calls, and returns. It is separate from execution because it represents the compiler's intermediate form.

---

## F. Backend/GALinterpreter.py

### 1. FILE PURPOSE

`GALinterpreter.py` is the execution engine. It walks the validated AST and performs the actual program behavior.

Pipeline position:

```text
validated AST -> Interpreter.interpret(ast) -> runtime output / input / errors
```

### 2. IMPORTS / DEPENDENCIES

Code:

```python
from GALsemantic import (ProgramNode, VariableDeclarationNode, AssignmentNode, ...)
import threading
import sys
sys.setrecursionlimit(10000)
```

Explanation:

- Imports AST node classes so the interpreter can identify node types.
- `threading` is fallback support for input waiting.
- `sys.setrecursionlimit(10000)` allows deeper recursive interpretation/function calls.

Code:

```python
try:
    import eventlet.event as _ev
    _USE_EVENTLET = True
except ImportError:
    _USE_EVENTLET = False
```

Explanation:

- Uses eventlet events when available.
- Eventlet lets `water()` wait without blocking the whole Socket.IO server.
- Falls back to threading events if eventlet is unavailable.

### 3. GLOBAL CONSTANTS / VARIABLES

There are no major global compiler constants here. The runtime state is inside each `Interpreter` object:

- variables
- functions
- scopes
- bundle types
- input events
- output socket
- loop flags

### 4. CLASSES AND FUNCTIONS

`ReturnValue`

- Internal exception used to implement `reclaim`.
- Carries return value out of a function body.

`_CancelledError`

- Raised when a previous interpreter is cancelled by a new run.

`InterpreterError`

- Runtime error with line-numbered message.

`Interpreter`

- Main runtime class.
- Executes AST nodes.
- Stores variables, functions, scopes, bundle types, loop flags, and input state.

### 5. LINE-BY-LINE / BLOCK-BY-BLOCK EXPLANATION

Code:

```python
class Interpreter:
    def __init__(self, socketio=None):
        self.output = []
        self.loop_stack = []
        self.break_flag = False
        self.continue_flag = False
        self.input_required = False
        self.socketio = socketio
```

Explanation:

- Creates one runtime environment.
- `output` stores printed output in compatibility paths.
- `loop_stack`, `break_flag`, and `continue_flag` implement `prune` and `skip`.
- `input_required` marks whether `water()` is waiting.
- `socketio` receives output and input events.

Code:

```python
self.input_events = {}
self.input_values = {}
self.variables = {}
self.global_variables = {}
self.functions = {}
self.scopes = [{}]
self.current_func_name = None
self.function_variables = {}
self.bundle_types = {}
```

Explanation:

- `input_events` stores waiting input requests.
- `input_values` stores input that arrived early.
- `variables` and `global_variables` store runtime values.
- `functions` stores function declarations.
- `scopes` models local scope stack.
- `bundle_types` stores struct-like type definitions.

Code:

```python
def declare_variable(self, name, type_, value=None, is_list=False, is_fertile=False):
    scope = self.scopes[-1]
    if name not in self.scopes[-1]:
        scope[name] = {
            "type": type_,
            "value": value,
            "is_list": is_list,
            "is_fertile": is_fertile
        }
```

Explanation:

- Stores a variable in the current runtime scope.
- Keeps type, value, array/list flag, and constant flag.

Code:

```python
def lookup_variable(self, name):
    for scope in reversed(self.scopes):
        if name in scope:
            return scope[name]
    if name in self.variables:
        return self.variables[name]
    return f"Semantic Error: Variable '{name}' used before declaration."
```

Explanation:

- Searches from innermost scope outward.
- Falls back to global variables.
- Returns an error string if variable does not exist.

Code:

```python
def interpret(self, node):
    if isinstance(node, ProgramNode):
        return self.eval_program(node)
    elif isinstance(node, VariableDeclarationNode):
        return self.eval_variable_declaration(node)
    elif isinstance(node, AssignmentNode):
        return self.eval_assignment(node)
```

Explanation:

- This is the main AST dispatcher.
- Each node type is routed to the correct evaluator.
- This is how the interpreter walks and executes the AST.

Code:

```python
elif node.node_type == "Identifier":
    var_info = self.lookup_variable(node.value)
    if isinstance(var_info, str):
        raise InterpreterError(var_info, node.line)
    return var_info["value"]
```

Explanation:

- Identifier evaluation means reading the current runtime value.
- If the variable is missing, execution stops with an error.

Code:

```python
def eval_program(self, node):
    for child in node.children:
        self.interpret(child)
    main_call = FunctionCallNode("root", [], node.line)
    return self.interpret(main_call)
```

Explanation:

- First registers global declarations, bundles, and functions.
- Then creates a call to `root()`.
- This implements GAL's entry point rule.

Code:

```python
def eval_variable_declaration(self, node):
    var_type = node.children[0].value
    var_name = node.children[1].value
    value_node = node.children[2] if len(node.children) > 2 else None
```

Explanation:

- Reads type, name, and optional initializer from AST children.
- The interpreter relies on the AST layout created by `VariableDeclarationNode`.

Code:

```python
default_values = {
    "seed": 0,
    "tree": 0.0,
    "leaf": '',
    "vine": "",
    "branch": False,
}
```

Explanation:

- Provides default values for declarations without initializers.
- Example: `seed x;` becomes `x = 0` at runtime.

Code:

```python
if value_node:
    value = self.interpret(value_node)
    if var_type == "seed" and isinstance(value, float):
        value = int(value)
else:
    value = default_values.get(var_type, None)
```

Explanation:

- If there is an initializer, evaluate it.
- If the variable is `seed` and value is float, convert to int.
- If there is no initializer, use default value.

Code:

```python
self.declare_variable(var_name, var_type, value, is_list=is_list)
```

Explanation:

- Stores the variable in the current runtime scope.
- After this line, later statements can access the variable.

Code:

```python
def eval_assignment(self, node):
    target_node = node.children[0]
    value_node = node.children[1]
    value = self.interpret(value_node)
```

Explanation:

- Evaluates the right-hand side first.
- Then assigns it to the target.
- The target can be a normal variable, list element, or bundle member.

Code:

```python
if target_node.node_type == "ListAccess":
    indices = []
    current = target_node
    while current.node_type == "ListAccess":
        idx = self.interpret(current.children[1].children[0])
        if not isinstance(idx, int):
            raise InterpreterError(...)
        indices.append(idx)
```

Explanation:

- Handles assignment to array/list elements.
- Evaluates each index expression.
- Requires indexes to be integers.

Code:

```python
if final_idx < 0 or final_idx >= len(target):
    raise InterpreterError("Index out of bounds", node.line)
target[final_idx] = value
```

Explanation:

- Performs runtime bounds check.
- Writes the new value.
- Current implementation uses 0-based indexing. This differs from the GAL PDF's 1-based rule.

Code:

```python
def eval_binary_op(self, node):
    left = self.interpret(node.children[0])
    right = self.interpret(node.children[1])
    operator = node.value
```

Explanation:

- Evaluates both operands recursively.
- Reads the operator from the AST node.

Code:

```python
if operator == '`':
    result = str(left) + str(right)
    return result
```

Explanation:

- Implements GAL string concatenation using backtick.
- Converts both operands to string.

Code:

```python
elif operator == '/':
    if right == 0:
        raise InterpreterError("Runtime Error: Division by zero is undefined", node.line)
    return left / right
```

Explanation:

- Executes division.
- Checks division by zero at runtime because actual values are known only during execution.

Code:

```python
def eval_block(self, block_node):
    for statement in block_node.children:
        self.interpret(statement)
        if self.break_triggered():
            return
        if self.continue_flag:
            return
```

Explanation:

- Executes statements in source order.
- Stops block execution if `prune` or `skip` changes control flow.

Code:

```python
def plant(self, value):
    self.socketio.emit('output', {'output': str(value)})
```

Explanation:

- Implements output.
- The interpreter emits to whatever socket-like object it was given.
- In Socket.IO mode, output goes live to the frontend.
- In REST mode, `OutputCollector` catches it.

Code:

```python
def eval_return(self, node):
    value = self.interpret(node.children[0]) if node.children else None
    raise ReturnValue(value)
```

Explanation:

- Implements `reclaim`.
- Raises `ReturnValue` to immediately exit the current function.
- Carries return value if present.

Code:

```python
def eval_function_call(self, node):
    function_name = node.value
    args = [self.interpret(arg.children[0]) for arg in node.children]
    func_info = self.lookup_function(function_name)
```

Explanation:

- Evaluates function call arguments.
- Looks up the function declaration.

Code:

```python
self.enter_scope()
try:
    for i, param in enumerate(expected_params):
        self.declare_variable(param_name, param_type, arg_value, is_list=is_list)
    self.eval_block(function_node.children[2])
except ReturnValue as ret:
    return ret.value
finally:
    self.exit_scope()
```

Explanation:

- Function call creates a new local scope.
- Parameters become local variables.
- Function body executes.
- `ReturnValue` captures `reclaim`.
- Scope is cleaned up after the call.

Code:

```python
def provide_input(self, var_name, input_value):
    evt = self.input_events.get(var_name)
    if evt is None:
        self.input_values[var_name] = input_value
        return
```

Explanation:

- Receives input from `server.py`.
- If interpreter is not waiting yet, stores the value.
- Prevents lost input.

Code:

```python
def wait_for_input(self, var_name):
    if var_name in self.input_values:
        return self.input_values.pop(var_name)
```

Explanation:

- If input already arrived, returns it immediately.
- Otherwise waits for eventlet/threading event.

Code:

```python
def eval_input(self, node):
    parent_node = node.parent
    if isinstance(parent_node, VariableDeclarationNode):
        var_name = parent_node.children[1].value
        var_type = parent_node.children[0].value
```

Explanation:

- Figures out where `water()` is being used.
- If it is inside a declaration, the target variable and type come from the parent declaration.

Code:

```python
self.emit_input_request(var_name, prompt)
input_value = self.wait_for_input(var_name)
```

Explanation:

- Tells the frontend input is needed.
- Waits until the user responds.

Code:

```python
if var_type == "seed":
    if input_value.startswith('-'):
        raise InterpreterError("GAL uses '~' for negative numbers", node.line)
    if input_value.startswith('~'):
        input_value = '-' + input_value[1:]
    input_value = int(float(input_value))
```

Explanation:

- Converts input string to integer.
- Enforces GAL negative syntax using `~` instead of `-`.
- Raises runtime error if conversion fails.

### 6. DEFENSE QUESTIONS

Q: Why execute the AST instead of tokens?

A: Tokens are flat. The AST already shows program structure, so execution can naturally follow blocks, expressions, functions, and control flow.

Q: Why does `reclaim` use an exception?

A: A return must immediately exit the current function, even from nested blocks. `ReturnValue` carries the return value out cleanly.

Q: How does `plant()` output reach the frontend?

A: The interpreter calls `self.socketio.emit('output', ...)`. In live mode this is Socket.IO; in REST mode it is an `OutputCollector`.

Q: How does `water()` work?

A: The interpreter emits an input request, waits on an event, and `server.py` later calls `provide_input()` when the frontend sends user input.

Q: What array indexing issue should you mention?

A: The GAL document says arrays are 1-based, but the interpreter currently checks `index < 0` and accesses `list_value[index]`, so runtime behavior is 0-based.

### 7. WALKTHROUGH EXAMPLE

For:

```gal
root() {
    seed age = 10;
    plant(age);
    reclaim;
}
```

Execution steps:

1. `eval_program()` registers declarations and functions.
2. It creates a `FunctionCallNode("root", [])`.
3. `eval_function_call()` enters a scope for root.
4. `eval_variable_declaration()` stores `age` as a `seed` with value `10`.
5. `eval_print()` reads `age` and emits `10`.
6. `eval_return()` raises `ReturnValue(None)`.
7. The function call catches return and exits.
8. `server.py` returns output to frontend.

### 8. MEMORIZED EXPLANATION

`GALinterpreter.py` is the runtime engine. It walks the AST, stores variables in scopes, registers functions, evaluates expressions, executes loops and conditionals, handles `plant()` output, handles `water()` input, and uses `ReturnValue` to implement `reclaim`.

---

# Final Full-Pipeline Defense Explanation

`server.py` receives source code from the frontend. It sends the raw text to `lexer.py`, which converts characters into tokens and reports lexical errors. Those tokens go to `Gal_Parser.py`, which uses the grammar and PREDICT sets from `cfg.py` to validate syntax with LL(1) parsing. If syntax succeeds, `parse_and_build()` calls the AST builder in `GALsemantic.py`. The AST builder creates structured nodes and a symbol table. Then `validate_ast()` walks the AST for semantic checks. If the user requests ICG, `icg.py` generates three-address code. If the user runs the program, `GALinterpreter.py` walks the AST, calls `root()`, executes declarations, statements, expressions, functions, loops, `plant()`, `water()`, and `reclaim`, then sends the output back through the server.

# Common Panel Questions For The Whole System

Q: Why did you separate the compiler into files?

A: Each file represents a compiler responsibility. Lexer handles characters, parser handles grammar, AST/semantic handles meaning, ICG handles intermediate representation, and interpreter handles execution.

Q: What happens if lexical analysis fails?

A: The server stops immediately and returns lexical errors. Parser does not run because invalid tokens would make syntax analysis unreliable.

Q: What happens if syntax analysis fails?

A: AST construction does not happen. The server returns syntax errors from the parser.

Q: What happens if semantic analysis fails?

A: ICG and interpreter are skipped. The server returns semantic errors.

Q: What happens if runtime execution fails?

A: The interpreter raises `InterpreterError`; `server.py` catches it and sends a runtime error to the frontend.

Q: Why is `root()` called by the interpreter instead of just executing top to bottom?

A: Top-level declarations and function definitions must be registered first. Actual program execution begins at `root()`, as required by the GAL specification.

Q: What is one known implementation/spec mismatch?

A: The GAL PDF specifies 1-based arrays, but the current interpreter uses 0-based indexing for lists/vines. That should be acknowledged honestly during defense.
