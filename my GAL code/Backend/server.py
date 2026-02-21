from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os, threading
from lexer import lex, get_token_description
from Gal_Parser import LL1Parser
from cfg import cfg, first_sets, predict_sets
from GALsemantic import analyze_semantics
from icg import generate_icg
from GALinterpreter import Interpreter, InterpreterError

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
        
        # Run the parser on the tokens
        parse_success, parse_errors = parser.parse(tokens)
        
        # If there are syntax errors, return them without semantic analysis
        if not parse_success or parse_errors:
            return jsonify({
                'success': False,
                'tokens': token_list,
                'errors': parse_errors,
                'warnings': [],
                'stage': 'syntax'
            })
        
        # Run semantic analysis
        semantic_result = analyze_semantics(tokens)
        
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

        # 2. Syntax analysis
        parse_success, parse_errors = parser.parse(tokens)
        if not parse_success or parse_errors:
            return jsonify({
                'success': False,
                'tokens': token_list,
                'errors': parse_errors,
                'stage': 'syntax'
            })

        # 3. Semantic analysis
        semantic_result = analyze_semantics(tokens)
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
                'output': ['Lexical Error: ' + e for e in lex_errors],
                'errors': lex_errors
            })

        # 2. Parse
        parse_success, parse_errors = parser.parse(tokens)
        if not parse_success or parse_errors:
            return jsonify({
                'success': False,
                'stage': 'syntax',
                'output': [str(e) for e in parse_errors],
                'errors': [str(e) for e in parse_errors]
            })

        # 3. Semantic
        semantic_result = analyze_semantics(tokens)
        if not semantic_result['success']:
            return jsonify({
                'success': False,
                'stage': 'semantic',
                'output': [str(e) for e in semantic_result['errors']],
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

    # 2. Syntax analysis
    parse_success, parse_errors = parser.parse(tokens)
    if not parse_success or parse_errors:
        for err in parse_errors:
            emit('output', {'output': f'{err}'})
        emit('execution_complete', {'success': False, 'stage': 'syntax'})
        return

    # 3. Semantic analysis
    semantic_result = analyze_semantics(tokens)
    if not semantic_result['success']:
        for err in semantic_result['errors']:
            emit('output', {'output': f'{err}'})
        emit('execution_complete', {'success': False, 'stage': 'semantic'})
        return

    ast = semantic_result['ast']

    # 4. Interpretation — run in background task for input support
    def run_interpreter():
        try:
            session_emitter = SessionEmitter(socketio, sid)
            interp = Interpreter(socketio=session_emitter)
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
    print(f"  - Socket.IO: run_code (Execute Program)")
    socketio.run(app, host='0.0.0.0', port=port, debug=debug, allow_unsafe_werkzeug=True)
