# ============================================================================
# GAL COMPILER SERVER - HTTP + WebSocket entry point
# ============================================================================
# This is the orchestrator of the entire compiler. It exposes Flask routes
# for each compiler stage (lex / parse / semantic / icg / run) and Socket.IO
# events for interactive program execution. Every request flows through:
#
#     source code -> lexer -> parser+AST -> semantic -> ICG -> interpreter
#
# Each stage short-circuits on failure so the user sees the FIRST stage that
# rejected their code, not a flood of cascading errors.
# ============================================================================

# ============================================================================
# WARNING SUPPRESSION + EVENTLET BOOTSTRAP
# Eventlet provides cooperative concurrency so Socket.IO can park a request
# (e.g. waiting on water() input) without blocking the whole server.
# monkey_patch() must run BEFORE flask/socketio are imported.
# ============================================================================
import warnings
warnings.filterwarnings("ignore", message=".*RLock.*were not greened.*")

import eventlet
eventlet.monkey_patch()

# ============================================================================
# IMPORTS - Flask web framework + every layer of the GAL compiler
# ============================================================================
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
from google import genai                                       # AI chat helper (optional)
from lexer import lex, get_token_description                   # Stage 1: Lexical
from parser import LL1Parser                                   # Stage 2: Syntax (LL(1))
from cfg import cfg, first_sets, predict_sets                  # Grammar + parse table
from parser.builder import analyze_semantics                   # Stage 3a: legacy entry
from semantic import validate_ast                              # Stage 3b: Semantic validator
from icg import generate_icg                                   # Stage 4: ICG (display)
from interpreter import Interpreter, InterpreterError, _CancelledError      # Stage 5: Run
from ai import fallback_reply                                  # Rule-based AI fallback


# ============================================================================
# DISPLAY HELPER - Escapes control characters so token values are safe
# to embed in JSON responses for the IDE's lexeme table.
# ============================================================================
def _display_value(val):
    """Escape special chars in token values for safe display (like C's repr)."""
    if val is None:
        return ''
    s = str(val)
    s = s.replace('\n', '\\n')
    s = s.replace('\t', '\\t')
    s = s.replace('\r', '\\r')
    return s


# ============================================================================
# FLASK APP INITIALIZATION
# ============================================================================
app = Flask(__name__, static_folder='../UI', static_url_path='')
CORS(app)                                                       # Allow browser frontend on any origin (dev)
socketio = SocketIO(app, cors_allowed_origins="*")              # WebSocket layer for live program execution

# Per-session interpreter registry (sid -> Interpreter instance).
# One user can only have one program running at a time; new runs cancel the old.
interpreters = {}


# ============================================================================
# SESSION EMITTER - Routes interpreter output to the originating browser
# session instead of broadcasting to every connected client.
# ============================================================================
class SessionEmitter:
    """Wrapper around SocketIO that always emits to a specific client session."""
    def __init__(self, sio, sid):
        self._sio = sio                                         # the global SocketIO instance
        self._sid = sid                                         # this client's session ID

    def emit(self, event, data=None, **kwargs):
        # Always 'to=sid' so output goes to one user, never broadcast
        self._sio.emit(event, data, to=self._sid, **kwargs)


# ============================================================================
# PARSER SINGLETON - Built once at startup; the LL(1) parser is stateless
# across calls so this instance is shared by every request.
# ============================================================================
parser = LL1Parser(
    cfg=cfg,                            # Grammar productions
    predict_sets=predict_sets,          # Pre-computed parse table
    first_sets=first_sets,              # FIRST sets (for error recovery hints)
    start_symbol="<program>",           # Top of the GAL grammar
    end_marker="EOF",                   # Matches the synthetic EOF token from the lexer
    skip_token_types={'\n'}             # Newlines are filtered before the parser sees them
)

# ============================================================================
# STATIC FILE SERVING - Serves the IDE's HTML/CSS/JS/images so the whole app
# works as a single deployable. The no-cache header prevents stale UI during
# development.
# ============================================================================
@app.after_request
def add_no_cache(response):
    """Prevent browser from caching static files during development."""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/')
def index():
    """Serve the main HTML file"""
    return send_from_directory('../UI', 'index.html')

@app.route('/images/<path:filename>')
def serve_images(filename):
    """Serve image files from root images folder"""
    return send_from_directory('../images', filename)

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files (CSS, JS, etc.) from UI folder"""
    return send_from_directory('../UI', path)


# ============================================================================
# API ENDPOINT: /api/lex  - LEXICAL ANALYSIS (stage 1 only)
# Returns the token stream and any lexical errors. Used by the IDE's
# "Lexemes" tab to display the token table.
# ============================================================================
@app.route('/api/lex', methods=['POST'])
def lexer_endpoint():
    """
    API endpoint for lexical analysis
    Expects JSON: {"source_code": "your GAL code here"}
    Returns JSON: {"tokens": [...], "errors": [...]}
    """
    try:
        data = request.get_json()
        
        if not data or 'source_code' not in data:
            return jsonify({
                'error': 'Missing source_code in request body'
            }), 400
        
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
        return jsonify({
            'error': f'Server error: {str(e)}'
        }), 500

# ============================================================================
# API ENDPOINT: /api/parse  - LEX + SYNTAX ANALYSIS
# Runs the lexer and (only if no lex errors) the LL(1) parser.
# Short-circuits at the first failing stage and labels the response with
# the failing stage so the IDE can highlight the right phase indicator.
# ============================================================================
@app.route('/api/parse', methods=['POST'])
def parser_endpoint():
    """
    API endpoint for syntax analysis (parsing)
    Expects JSON: {"source_code": "your GAL code here"}
    Returns JSON: {"success": true/false, "tokens": [...], "errors": [...]}
    """
    try:
        data = request.get_json()
        
        if not data or 'source_code' not in data:
            return jsonify({
                'error': 'Missing source_code in request body'
            }), 400
        
        source_code = data['source_code']
        
        # First, run the lexer to get tokens
        tokens, lex_errors = lex(source_code)
        
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
        
        # Determine which stages have errors
        stages = []
        if parse_errors:
            stages.append('syntax')
        
        return jsonify({
            'success': parse_success,
            'tokens': token_list,
            'errors': parse_errors,
            'stage': stages if stages else ['success'],
            'lexical_errors': False,
            'syntax_errors': len(parse_errors) > 0
        })
    
    except Exception as e:
        return jsonify({
            'error': f'Server error: {str(e)}'
        }), 500

# ============================================================================
# API ENDPOINT: /api/health  - liveness check (used by deployment tools)
# ============================================================================
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'GAL Compiler Server is running'
    })


# ============================================================================
# API ENDPOINT: /api/semantic  - LEX + PARSE + AST + SEMANTIC ANALYSIS
# Uses the parser's two-step API: parse_and_build (syntax + AST construction)
# then validate_ast (tree-walking semantic checks). Distinguishes between
# 'syntax' and 'semantic' error stages even though both come from the parser.
# ============================================================================
@app.route('/api/semantic', methods=['POST'])
def semantic_endpoint():
    """
    API endpoint for semantic analysis
    Expects JSON: {"source_code": "your GAL code here"}
    Returns JSON: {"success": true/false, "errors": [...], "warnings": [...], "symbol_table": {...}}
    """
    try:
        data = request.get_json()
        
        if not data or 'source_code' not in data:
            return jsonify({
                'error': 'Missing source_code in request body'
            }), 400
        
        source_code = data['source_code']
        
        # First, run the lexer to get tokens
        tokens, lex_errors = lex(source_code)
        
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
        
        # If there are lexical errors, return them without semantic analysis
        if lex_errors:
            return jsonify({
                'success': False,
                'tokens': token_list,
                'errors': lex_errors,
                'warnings': [],
                'stage': 'lexical'
            })
        
        # Run the parser — validates syntax (LL1) then builds AST
        parse_result = parser.parse_and_build(tokens)
        
        # If syntax or AST construction failed, return errors
        if not parse_result['success']:
            # Distinguish semantic errors caught during AST building
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
        
        return jsonify({
            'success': semantic_result['success'],
            'tokens': token_list,
            'errors': semantic_result['errors'],
            'warnings': semantic_result['warnings'],
            'symbol_table': semantic_result['symbol_table'],
            'stage': 'semantic'
        })
    
    except Exception as e:
        return jsonify({
            'error': f'Server error: {str(e)}'
        }), 500

# ============================================================================
# API ENDPOINT: /api/icg  - LEX + PARSE + SEMANTIC + ICG (display only)
# ICG produces three-address code (TAC) for the IDE's "Intermediate Code"
# tab. The interpreter does NOT consume this output; it walks the AST directly.
# So ICG is a teaching/visualization layer, not a runtime layer.
# ============================================================================
@app.route('/api/icg', methods=['POST'])
def icg_endpoint():
    """
    API endpoint for intermediate code generation.
    Runs lexer → parser → semantic → ICG pipeline.
    Expects JSON: {"source_code": "your GAL code here"}
    Returns JSON with TAC instructions.
    """
    try:
        data = request.get_json()

        if not data or 'source_code' not in data:
            return jsonify({
                'error': 'Missing source_code in request body'
            }), 400

        source_code = data['source_code']

        # 1. Lexical analysis
        tokens, lex_errors = lex(source_code)

        token_list = []
        for token in tokens:
            token_list.append({
                'type': token.type,
                'value': _display_value(token.value),
                'line': token.line,
                'col': getattr(token, 'col', 0),
                'description': get_token_description(token.type, token.value)
            })

        if lex_errors:
            return jsonify({
                'success': False,
                'tokens': token_list,
                'errors': lex_errors,
                'stage': 'lexical'
            })

        # 2. Syntax analysis + AST construction (parser builds AST)
        parse_result = parser.parse_and_build(tokens)
        if not parse_result['success']:
            error_stage = parse_result.get('error_stage', 'syntax')
            return jsonify({
                'success': False,
                'tokens': token_list,
                'errors': parse_result['errors'],
                'stage': error_stage
            })

        # 3. Semantic analysis — tree-walking validation of the AST
        semantic_result = validate_ast(parse_result['ast'], parse_result['symbol_table'])
        if not semantic_result['success']:
            return jsonify({
                'success': False,
                'tokens': token_list,
                'errors': semantic_result['errors'],
                'warnings': semantic_result['warnings'],
                'stage': 'semantic'
            })

        # 4. Intermediate code generation
        icg_result = generate_icg(tokens)

        return jsonify({
            'success': icg_result['success'],
            'tokens': token_list,
            'tac': icg_result['tac'],
            'tac_text': icg_result['tac_text'],
            'errors': icg_result['errors'],
            'warnings': semantic_result.get('warnings', []),
            'stage': 'icg'
        })

    except Exception as e:
        return jsonify({
            'error': f'Server error: {str(e)}'
        }), 500


# ============================================================================
# SYNCHRONOUS EXECUTION (no Socket.IO required)
#
# OutputCollector is an adapter — same .emit() interface as SessionEmitter,
# but instead of streaming output via WebSocket it captures it in a list.
# This is the adapter pattern: one Interpreter class, two delivery modes.
# ============================================================================

class OutputCollector:
    """Drop-in replacement for SessionEmitter that collects output in a list."""
    def __init__(self):
        self.outputs = []                 # Accumulated plant() output strings
        self.needs_input = False          # Flips to True if program calls water()

    def emit(self, event, data=None, **kwargs):
        if event == 'output' and data:
            # Accumulate normal plant() output
            self.outputs.append(data.get('output', ''))
        elif event == 'input_required':
            # No interactive channel here -> abort the interpreter so the
            # client can switch to the Socket.IO flow that supports input.
            self.needs_input = True
            raise _InputNeeded()


class _InputNeeded(Exception):
    """Raised by OutputCollector to abort REST execution when water() is called."""
    pass


# ============================================================================
# API ENDPOINT: /api/run  - One-shot execution returning all output at once.
# Used for non-interactive programs (no water() calls). For interactive runs,
# the client uses the Socket.IO 'run_code' event below.
# ============================================================================
@app.route('/api/run', methods=['POST'])
def run_endpoint():
    """Run a GAL program synchronously and return all output."""
    try:
        data = request.get_json()
        if not data or 'source_code' not in data:
            return jsonify({'error': 'Missing source_code in request body'}), 400

        source_code = data['source_code']

        # 1. Lex
        tokens, lex_errors = lex(source_code)
        if lex_errors:
            return jsonify({
                'success': False,
                'stage': 'lexical',
                'output': [],
                'errors': lex_errors
            })

        # 2. Parse + build AST (parser builds the AST)
        parse_result = parser.parse_and_build(tokens)
        if not parse_result['success']:
            error_stage = parse_result.get('error_stage', 'syntax')
            return jsonify({
                'success': False,
                'stage': error_stage,
                'output': [],
                'errors': [str(e) for e in parse_result['errors']]
            })

        # 3. Semantic — tree-walking validation of the AST
        semantic_result = validate_ast(parse_result['ast'], parse_result['symbol_table'])
        if not semantic_result['success']:
            return jsonify({
                'success': False,
                'stage': 'semantic',
                'output': [],
                'errors': [str(e) for e in semantic_result['errors']]
            })

        ast = semantic_result['ast']

        # 4. Interpret
        collector = OutputCollector()
        interp = Interpreter(socketio=collector)
        try:
            interp.interpret(ast)
            return jsonify({
                'success': True,
                'stage': 'execution',
                'output': collector.outputs,
                'errors': []
            })
        except _InputNeeded:
            # Program called water() — return partial output and flag
            return jsonify({
                'success': False,
                'stage': 'execution',
                'output': collector.outputs,
                'errors': ['Program requires interactive input (water())'],
                'needs_input': True
            })
        except InterpreterError as e:
            collector.outputs.append(f'Runtime Error: {e}')
            return jsonify({
                'success': False,
                'stage': 'execution',
                'output': collector.outputs,
                'errors': [str(e)]
            })
        except Exception as e:
            collector.outputs.append(f'Internal Error: {e}')
            return jsonify({
                'success': False,
                'stage': 'execution',
                'output': collector.outputs,
                'errors': [str(e)]
            })

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


# ============================================================================
# SOCKET.IO INTERACTIVE EXECUTION
#
# This path supports water() input. The interpreter runs in a green thread
# (eventlet) so it can park while waiting for input without blocking the
# server. Output is streamed back via 'output' events as plant() fires.
# ============================================================================

@socketio.on('connect')
def handle_connect():
    # No setup needed — interpreter is created lazily on first 'run_code'.
    pass

@socketio.on('disconnect')
def handle_disconnect():
    # Drop the user's interpreter so memory doesn't leak across reconnects.
    sid = request.sid
    interpreters.pop(sid, None)

@socketio.on('run_code')
def handle_run_code(data):
    """
    Run a GAL program through lex → parse → semantic → interpreter.
    Program output is sent back via 'output' events.
    """
    sid = request.sid
    source_code = data.get('source_code', '')

    # 1. Lexical analysis
    tokens, lex_errors = lex(source_code)
    if lex_errors:
        for err in lex_errors:
            emit('output', {'output': f'Lexical Error: {err}'})
        emit('execution_complete', {'success': False, 'stage': 'lexical'})
        return

    # Notify client that lexical analysis passed
    emit('stage_complete', {'stage': 'lexical', 'success': True})

    # 2. Syntax analysis + AST construction (parser builds AST)
    parse_result = parser.parse_and_build(tokens)
    if not parse_result['success']:
        error_stage = parse_result.get('error_stage', 'syntax')
        for err in parse_result['errors']:
            emit('output', {'output': f'{err}'})
        emit('execution_complete', {'success': False, 'stage': error_stage})
        return

    # Notify client that syntax analysis passed
    emit('stage_complete', {'stage': 'syntax', 'success': True})

    # 3. Semantic analysis — tree-walking validation of the AST
    semantic_result = validate_ast(parse_result['ast'], parse_result['symbol_table'])
    if not semantic_result['success']:
        for err in semantic_result['errors']:
            emit('output', {'output': f'{err}'})
        emit('execution_complete', {'success': False, 'stage': 'semantic'})
        return

    # Notify client that semantic analysis passed
    emit('stage_complete', {'stage': 'semantic', 'success': True})

    ast = semantic_result['ast']

    # 4. Interpretation — run in background task for input support
    # Cancel any previously-running interpreter for this session
    old_interp = interpreters.get(sid)
    if old_interp and hasattr(old_interp, '_cancelled'):
        old_interp._cancelled = True
        # Unblock any pending wait_for_input so the old thread can exit
        for evt in list(old_interp.input_events.values()):
            try:
                evt.send(None)   # eventlet.event.Event uses .send()
            except (AttributeError, AssertionError):
                try:
                    evt.set()    # threading.Event fallback
                except Exception:
                    pass

    def run_interpreter():
        try:
            session_emitter = SessionEmitter(socketio, sid)
            interp = Interpreter(socketio=session_emitter)
            interp._cancelled = False
            interpreters[sid] = interp
            interp.interpret(ast)
            if not interp._cancelled:
                socketio.emit('execution_complete', {'success': True, 'stage': 'execution'}, to=sid)
        except _CancelledError:
            pass  # Old interpreter was cancelled by a new run — exit silently
        except InterpreterError as e:
            if not getattr(interp, '_cancelled', False):
                socketio.emit('output', {'output': f'Runtime Error: {e}'}, to=sid)
                socketio.emit('execution_complete', {'success': False, 'stage': 'execution'}, to=sid)
        except Exception as e:
            if not getattr(interp, '_cancelled', False):
                socketio.emit('output', {'output': f'Internal Error: {e}'}, to=sid)
                socketio.emit('execution_complete', {'success': False, 'stage': 'execution'}, to=sid)
        finally:
            # Only remove ourselves — don't remove a newer interpreter
            if interpreters.get(sid) is interp:
                interpreters.pop(sid, None)

    socketio.start_background_task(run_interpreter)

# ============================================================================
# SOCKET.IO INPUT CHANNEL - When a running program calls water(), the
# interpreter parks on an event. The frontend prompts the user, sends back
# 'capture_input', and this handler routes the value to the right interpreter.
# ============================================================================
@socketio.on('capture_input')
def handle_capture_input(data):
    """Receive input from the client and forward to the waiting interpreter."""
    sid = request.sid
    interp = interpreters.get(sid)
    if interp:
        var_name = data.get('var_name', '')
        input_value = data.get('input', '')
        # Unblock the parked interpreter so execution resumes
        interp.provide_input(var_name, input_value)


# ============================================================================
# AI CHAT HELPER (Google Gemini)
# Optional learning aid — answers user questions about GAL syntax. Falls
# back to a rule-based reply if no GEMINI_API_KEY is set or the API fails.
# This is NOT part of the compiler pipeline.
# ============================================================================

# Load the system prompt that teaches Gemini how to talk about GAL
_prompt_path = os.path.join(os.path.dirname(__file__), 'ai', 'prompt.txt')
with open(_prompt_path, 'r', encoding='utf-8') as _f:
    GAL_SYSTEM_PROMPT = _f.read()



# Initialize Gemini client — requires GEMINI_API_KEY env var
_gemini_client = None
_chat_sessions = {}  # sid -> list of message dicts

def _get_gemini_client():
    global _gemini_client
    if _gemini_client is None:
        api_key = os.environ.get('GEMINI_API_KEY', '')
        if not api_key:
            return None
        _gemini_client = genai.Client(api_key=api_key)
    return _gemini_client

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """AI chat helper endpoint using Google Gemini."""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message in request body'}), 400

        user_message = data['message']
        session_id = data.get('session_id', 'default')
        editor_code = data.get('editor_code', '')

        client = _get_gemini_client()
        if client is None:
            # No API key — use fallback
            fb_reply = fallback_reply(user_message)
            return jsonify({'reply': fb_reply, 'mode': 'fallback'})

        # Build/get conversation history for this session
        if session_id not in _chat_sessions:
            _chat_sessions[session_id] = []
        history = _chat_sessions[session_id]

        # Include editor code as context if provided
        full_message = user_message
        if editor_code.strip():
            full_message = f"[Current code in editor]:\n```\n{editor_code}\n```\n\nUser question: {user_message}"

        history.append({'role': 'user', 'parts': [{'text': full_message}]})

        # Keep history manageable (last 20 messages)
        if len(history) > 20:
            history[:] = history[-20:]

        # Try multiple models in case one has quota available
        models_to_try = ['gemini-2.5-flash', 'gemini-2.5-flash-lite', 'gemini-2.0-flash', 'gemini-2.0-flash-lite']
        last_error: Exception = RuntimeError("No Gemini models were available to try")
        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=history,
                    config=genai.types.GenerateContentConfig(
                        system_instruction=GAL_SYSTEM_PROMPT,
                        temperature=0.3,
                        max_output_tokens=4096,
                    ),
                )
                break  # success
            except Exception as model_err:
                last_error = model_err
                err_msg = str(model_err)
                # Retry-worthy errors: quota, availability, or auth (same key fails for all models)
                if '429' not in err_msg and 'RESOURCE_EXHAUSTED' not in err_msg and '503' not in err_msg and 'UNAVAILABLE' not in err_msg and '403' not in err_msg and 'PERMISSION_DENIED' not in err_msg:
                    raise  # unexpected error, don't retry
                continue
        else:
            raise last_error  # all models failed

        reply = response.text or 'No response generated.'

        history.append({'role': 'model', 'parts': [{'text': reply}]})

        return jsonify({'reply': reply, 'mode': 'ai'})

    except Exception as e:
        # All Gemini models failed — use rule-based fallback
        try:
            fb_reply = fallback_reply(user_message)
            return jsonify({'reply': fb_reply, 'mode': 'fallback'})
        except Exception:
            pass  # fallback itself failed, return original error
        err_str = str(e)
        return jsonify({'error': f'Chat error: {err_str}'}), 500

@app.route('/api/chat/clear', methods=['POST'])
def chat_clear_endpoint():
    """Clear chat history for a session."""
    data = request.get_json() or {}
    session_id = data.get('session_id', 'default')
    _chat_sessions.pop(session_id, None)
    return jsonify({'success': True})


# ============================================================================
# SERVER STARTUP - Reads PORT/DEBUG env vars, prints a banner listing every
# endpoint, then hands the app to eventlet's WSGI server.
# host='0.0.0.0' makes the server reachable from any network interface,
# not just localhost.
# ============================================================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False') != 'True'

    print("Starting GAL Compiler Server...")
    print(f"Server running at http://0.0.0.0:{port}")
    print("API endpoints:")
    print(f"  - POST http://localhost:{port}/api/lex (Lexical Analysis)")
    print(f"  - POST http://localhost:{port}/api/parse (Syntax Analysis)")
    print(f"  - POST http://localhost:{port}/api/semantic (Semantic Analysis)")
    print(f"  - POST http://localhost:{port}/api/icg (Intermediate Code Generation)")
    print(f"  - POST http://localhost:{port}/api/chat (AI Chat Helper)")
    print(f"  - Socket.IO: run_code (Execute Program)")
    # allow_unsafe_werkzeug=True is needed when running inside eventlet during dev
    socketio.run(app, host='0.0.0.0', port=port, debug=debug, allow_unsafe_werkzeug=True)
