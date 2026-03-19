import warnings
warnings.filterwarnings("ignore", message=".*RLock.*were not greened.*")

import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os, threading
from google import genai
from lexer import lex, get_token_description
from Gal_Parser import LL1Parser
from cfg import cfg, first_sets, predict_sets
from GALsemantic import analyze_semantics, validate_ast
from icg import generate_icg
from GALinterpreter import Interpreter, InterpreterError
from gal_fallback import fallback_reply

def _display_value(val):
    """Escape special chars in token values for safe display (like C's repr)."""
    if val is None:
        return ''
    s = str(val)
    s = s.replace('\n', '\\n')
    s = s.replace('\t', '\\t')
    s = s.replace('\r', '\\r')
    return s

app = Flask(__name__, static_folder='../UI', static_url_path='')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Store interpreter instances per session for input handling
interpreters = {}


class SessionEmitter:
    """Wrapper around SocketIO that always emits to a specific client session."""
    def __init__(self, sio, sid):
        self._sio = sio
        self._sid = sid

    def emit(self, event, data=None, **kwargs):
        self._sio.emit(event, data, to=self._sid, **kwargs)

# Initialize the parser once at startup
parser = LL1Parser(
    cfg=cfg,
    predict_sets=predict_sets,
    first_sets=first_sets,
    start_symbol="<program>",
    end_marker="EOF",
    skip_token_types={'\n'}  # Skip newline tokens
)

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

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'GAL Compiler Server is running'
    })

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


# ─── REST endpoint for program execution (no Socket.IO needed) ────

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


class _InputNeeded(Exception):
    """Raised by OutputCollector to abort REST execution when water() is called."""
    pass

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


# ─── Socket.IO events for program execution ───────────────────────

@socketio.on('connect')
def handle_connect():
    pass

@socketio.on('disconnect')
def handle_disconnect():
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
            evt.set()

    def run_interpreter():
        try:
            session_emitter = SessionEmitter(socketio, sid)
            interp = Interpreter(socketio=session_emitter)
            interp._cancelled = False
            interpreters[sid] = interp
            interp.interpret(ast)
            socketio.emit('execution_complete', {'success': True, 'stage': 'execution'}, to=sid)
        except InterpreterError as e:
            socketio.emit('output', {'output': f'Runtime Error: {e}'}, to=sid)
            socketio.emit('execution_complete', {'success': False, 'stage': 'execution'}, to=sid)
        except Exception as e:
            socketio.emit('output', {'output': f'Internal Error: {e}'}, to=sid)
            socketio.emit('execution_complete', {'success': False, 'stage': 'execution'}, to=sid)
        finally:
            # Only remove ourselves — don't remove a newer interpreter
            if interpreters.get(sid) is interp:
                interpreters.pop(sid, None)

    socketio.start_background_task(run_interpreter)

@socketio.on('capture_input')
def handle_capture_input(data):
    """Receive input from the client and forward to the waiting interpreter."""
    sid = request.sid
    interp = interpreters.get(sid)
    if interp:
        var_name = data.get('var_name', '')
        input_value = data.get('input', '')
        interp.provide_input(var_name, input_value)


# ─── AI Chat Helper (Google Gemini) ─────────────────────────────

_prompt_path = os.path.join(os.path.dirname(__file__), 'gal_prompt.txt')
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
        last_error = None
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
    socketio.run(app, host='0.0.0.0', port=port, debug=debug, allow_unsafe_werkzeug=True)
