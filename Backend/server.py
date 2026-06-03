"""HTTP and Socket.IO entry point for the GAL compiler.

Pipeline from the UI:
source code -> lexer -> LL(1) parser/AST builder -> semantic validator -> interpreter.
"""

# Eventlet must be patched before Flask-SocketIO starts using sockets.
# AUTO: Imports a module used by this file.
import warnings
# AUTO: Sets `warnings.filterwarnings("ignore", message`.
warnings.filterwarnings("ignore", message=".*RLock.*were not greened.*")

# AUTO: Imports a module used by this file.
import eventlet
# AUTO: Calls `eventlet.monkey_patch`.
eventlet.monkey_patch()

# AUTO: Imports names from another module.
from flask import Flask, request, jsonify, send_from_directory
# AUTO: Imports names from another module.
from flask_cors import CORS
# AUTO: Imports names from another module.
from flask_socketio import SocketIO, emit
# AUTO: Imports a module used by this file.
import os
# AUTO: Imports names from another module.
from google import genai
# AUTO: Imports names from another module.
from lexer import lex, get_token_description
# AUTO: Imports names from another module.
from parser import LL1Parser
# AUTO: Imports names from another module.
from cfg import cfg, first_sets, predict_sets
# AUTO: Imports names from another module.
from parser.builder import analyze_semantics
# AUTO: Imports names from another module.
from semantic import validate_ast
# AUTO: Imports names from another module.
from icg import generate_icg
# AUTO: Imports names from another module.
from interpreter import Interpreter, InterpreterError, _CancelledError
# AUTO: Imports names from another module.
from ai import fallback_reply


# AUTO: Defines function `_display_value`.
def _display_value(val):
    # AUTO: Checks this condition.
    if val is None:
        # AUTO: Returns this result to the caller.
        return ''
    # AUTO: Sets `s`.
    s = str(val)
    # AUTO: Sets `s`.
    s = s.replace('\n', '\\n')
    # AUTO: Sets `s`.
    s = s.replace('\t', '\\t')
    # AUTO: Sets `s`.
    s = s.replace('\r', '\\r')
    # AUTO: Returns this result to the caller.
    return s


# AUTO: Sets `app`.
app = Flask(__name__, static_folder='../UI', static_url_path='')
# AUTO: Calls `CORS`.
CORS(app)
# AUTO: Sets `socketio`.
socketio = SocketIO(app, cors_allowed_origins="*")

# AUTO: Sets `interpreters`.
interpreters = {}


# AUTO: Defines class `SessionEmitter`.
class SessionEmitter:
    # AUTO: Defines function `__init__`.
    def __init__(self, sio, sid):
        # AUTO: Sets `self._sio`.
        self._sio = sio
        # AUTO: Sets `self._sid`.
        self._sid = sid

    # AUTO: Defines function `emit`.
    def emit(self, event, data=None, **kwargs):
        # AUTO: Sets `self._sio.emit(event, data, to`.
        self._sio.emit(event, data, to=self._sid, **kwargs)


# AUTO: Sets `parser`.
parser = LL1Parser(
    # AUTO: Sets `cfg`.
    cfg=cfg,
    # AUTO: Sets `predict_sets`.
    predict_sets=predict_sets,
    # AUTO: Sets `first_sets`.
    first_sets=first_sets,
    # AUTO: Sets `start_symbol`.
    start_symbol="<program>",
    # AUTO: Sets `end_marker`.
    end_marker="EOF",
    # AUTO: Sets `skip_token_types`.
    skip_token_types={'\n', 'comment', 'mcommentlit'}
# AUTO: Closes the current grouped code/data.
)


# GUIDE: Browser/cache setup for local testing.
# AUTO: Attaches this decorator to the next function/class.
@app.after_request
# AUTO: Defines function `add_no_cache`.
def add_no_cache(response):
    # AUTO: Sets `response.headers['Cache-Control']`.
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    # AUTO: Sets `response.headers['Pragma']`.
    response.headers['Pragma'] = 'no-cache'
    # AUTO: Sets `response.headers['Expires']`.
    response.headers['Expires'] = '0'
    # AUTO: Returns this result to the caller.
    return response

# AUTO: Attaches this decorator to the next function/class.
@app.route('/')
# AUTO: Defines function `index`.
def index():
    # AUTO: Returns this result to the caller.
    return send_from_directory('../UI', 'index.html')

# AUTO: Attaches this decorator to the next function/class.
@app.route('/images/<path:filename>')
# AUTO: Defines function `serve_images`.
def serve_images(filename):
    # AUTO: Returns this result to the caller.
    return send_from_directory('../images', filename)

# AUTO: Attaches this decorator to the next function/class.
@app.route('/<path:path>')
# AUTO: Defines function `serve_static`.
def serve_static(path):
    # AUTO: Returns this result to the caller.
    return send_from_directory('../UI', path)


# GUIDE: Lexer stage endpoint used by the lexeme table and Lexer run mode.
# AUTO: Attaches this decorator to the next function/class.
@app.route('/api/lex', methods=['POST'])
# AUTO: Defines function `lexer_endpoint`.
def lexer_endpoint():
    # AUTO: Starts protected code that can catch errors.
    try:
        # AUTO: Sets `data`.
        data = request.get_json()
        
        # AUTO: Checks this condition.
        if not data or 'source_code' not in data:
            # AUTO: Returns this result to the caller.
            return jsonify({
                # AUTO: Executes this statement.
                'error': 'Missing source_code in request body'
            # AUTO: Closes the current grouped code/data.
            }), 400
        
        # AUTO: Sets `source_code`.
        source_code = data['source_code']
        
        # AUTO: Sets `tokens, errors`.
        tokens, errors = lex(source_code)
        
        # AUTO: Sets `token_list`.
        token_list = []
        # AUTO: Starts a loop over these values.
        for token in tokens:
            # AUTO: Appends a value to a list.
            token_list.append({
                # AUTO: Executes this statement.
                'type': token.type,
                # AUTO: Calls `_display_value`.
                'value': _display_value(token.value),
                # AUTO: Executes this statement.
                'line': token.line,
                # AUTO: Calls `getattr`.
                'col': getattr(token, 'col', 0),
                # AUTO: Calls `get_token_description`.
                'description': get_token_description(token.type, token.value)
            # AUTO: Closes the current grouped code/data.
            })
        
        # AUTO: Returns this result to the caller.
        return jsonify({
            # AUTO: Executes this statement.
            'tokens': token_list,
            # AUTO: Executes this statement.
            'errors': errors
        # AUTO: Closes the current grouped code/data.
        })
    
    # AUTO: Handles the matching error case.
    except Exception as e:
        # AUTO: Returns this result to the caller.
        return jsonify({
            # AUTO: Executes this statement.
            'error': f'Server error: {str(e)}'
        # AUTO: Closes the current grouped code/data.
        }), 500

# GUIDE: Syntax stage endpoint; tokenizes first, then checks tokens with CFG.
# AUTO: Attaches this decorator to the next function/class.
@app.route('/api/parse', methods=['POST'])
# AUTO: Defines function `parser_endpoint`.
def parser_endpoint():
    # AUTO: Starts protected code that can catch errors.
    try:
        # AUTO: Sets `data`.
        data = request.get_json()
        
        # AUTO: Checks this condition.
        if not data or 'source_code' not in data:
            # AUTO: Returns this result to the caller.
            return jsonify({
                # AUTO: Executes this statement.
                'error': 'Missing source_code in request body'
            # AUTO: Closes the current grouped code/data.
            }), 400
        
        # AUTO: Sets `source_code`.
        source_code = data['source_code']
        
        # AUTO: Sets `tokens, lex_errors`.
        tokens, lex_errors = lex(source_code)
        
        # AUTO: Sets `token_list`.
        token_list = []
        # AUTO: Starts a loop over these values.
        for token in tokens:
            # AUTO: Appends a value to a list.
            token_list.append({
                # AUTO: Executes this statement.
                'type': token.type,
                # AUTO: Calls `_display_value`.
                'value': _display_value(token.value),
                # AUTO: Executes this statement.
                'line': token.line,
                # AUTO: Calls `getattr`.
                'col': getattr(token, 'col', 0),
                # AUTO: Calls `get_token_description`.
                'description': get_token_description(token.type, token.value)
            # AUTO: Closes the current grouped code/data.
            })
        
        # AUTO: Checks this condition.
        if lex_errors:
            # AUTO: Returns this result to the caller.
            return jsonify({
                # AUTO: Executes this statement.
                'success': False,
                # AUTO: Executes this statement.
                'tokens': token_list,
                # AUTO: Executes this statement.
                'errors': lex_errors,
                # AUTO: Executes this statement.
                'stage': ['lexical'],
                # AUTO: Executes this statement.
                'lexical_errors': True,
                # AUTO: Executes this statement.
                'syntax_errors': False
            # AUTO: Closes the current grouped code/data.
            })

        # AUTO: Sets `parse_success, parse_errors`.
        parse_success, parse_errors = parser.parse(tokens)
        
        # AUTO: Sets `stages`.
        stages = []
        # AUTO: Checks this condition.
        if parse_errors:
            # AUTO: Appends a value to a list.
            stages.append('syntax')
        
        # AUTO: Returns this result to the caller.
        return jsonify({
            # AUTO: Executes this statement.
            'success': parse_success,
            # AUTO: Executes this statement.
            'tokens': token_list,
            # AUTO: Executes this statement.
            'errors': parse_errors,
            # AUTO: Executes this statement.
            'stage': stages if stages else ['success'],
            # AUTO: Executes this statement.
            'lexical_errors': False,
            # AUTO: Executes this statement.
            'syntax_errors': len(parse_errors) > 0
        # AUTO: Closes the current grouped code/data.
        })
    
    # AUTO: Handles the matching error case.
    except Exception as e:
        # AUTO: Returns this result to the caller.
        return jsonify({
            # AUTO: Executes this statement.
            'error': f'Server error: {str(e)}'
        # AUTO: Closes the current grouped code/data.
        }), 500

# AUTO: Attaches this decorator to the next function/class.
@app.route('/api/health', methods=['GET'])
# AUTO: Defines function `health_check`.
def health_check():
    # AUTO: Returns this result to the caller.
    return jsonify({
        # AUTO: Executes this statement.
        'status': 'healthy',
        # AUTO: Executes this statement.
        'message': 'GAL Compiler Server is running'
    # AUTO: Closes the current grouped code/data.
    })


# AUTO: Attaches this decorator to the next function/class.
@app.route('/api/semantic', methods=['POST'])
# AUTO: Defines function `semantic_endpoint`.
def semantic_endpoint():
    # AUTO: Starts protected code that can catch errors.
    try:
        # AUTO: Sets `data`.
        data = request.get_json()
        
        # AUTO: Checks this condition.
        if not data or 'source_code' not in data:
            # AUTO: Returns this result to the caller.
            return jsonify({
                # AUTO: Executes this statement.
                'error': 'Missing source_code in request body'
            # AUTO: Closes the current grouped code/data.
            }), 400
        
        # AUTO: Sets `source_code`.
        source_code = data['source_code']
        
        # AUTO: Sets `tokens, lex_errors`.
        tokens, lex_errors = lex(source_code)
        
        # AUTO: Sets `token_list`.
        token_list = []
        # AUTO: Starts a loop over these values.
        for token in tokens:
            # AUTO: Appends a value to a list.
            token_list.append({
                # AUTO: Executes this statement.
                'type': token.type,
                # AUTO: Calls `_display_value`.
                'value': _display_value(token.value),
                # AUTO: Executes this statement.
                'line': token.line,
                # AUTO: Calls `getattr`.
                'col': getattr(token, 'col', 0),
                # AUTO: Calls `get_token_description`.
                'description': get_token_description(token.type, token.value)
            # AUTO: Closes the current grouped code/data.
            })
        
        # AUTO: Checks this condition.
        if lex_errors:
            # AUTO: Returns this result to the caller.
            return jsonify({
                # AUTO: Executes this statement.
                'success': False,
                # AUTO: Executes this statement.
                'tokens': token_list,
                # AUTO: Executes this statement.
                'errors': lex_errors,
                # AUTO: Executes this statement.
                'warnings': [],
                # AUTO: Executes this statement.
                'stage': 'lexical'
            # AUTO: Closes the current grouped code/data.
            })
        
        # AUTO: Sets `parse_result`.
        parse_result = parser.parse_and_build(tokens)
        
        # AUTO: Checks this condition.
        if not parse_result['success']:
            # AUTO: Sets `error_stage`.
            error_stage = parse_result.get('error_stage', 'syntax')
            # AUTO: Returns this result to the caller.
            return jsonify({
                # AUTO: Executes this statement.
                'success': False,
                # AUTO: Executes this statement.
                'tokens': token_list,
                # AUTO: Executes this statement.
                'errors': parse_result['errors'],
                # AUTO: Executes this statement.
                'warnings': [],
                # AUTO: Executes this statement.
                'stage': error_stage
            # AUTO: Closes the current grouped code/data.
            })
        
        # AUTO: Sets `semantic_result`.
        semantic_result = validate_ast(parse_result['ast'], parse_result['symbol_table'])
        
        # AUTO: Returns this result to the caller.
        return jsonify({
            # AUTO: Executes this statement.
            'success': semantic_result['success'],
            # AUTO: Executes this statement.
            'tokens': token_list,
            # AUTO: Executes this statement.
            'errors': semantic_result['errors'],
            # AUTO: Executes this statement.
            'warnings': semantic_result['warnings'],
            # AUTO: Executes this statement.
            'symbol_table': semantic_result['symbol_table'],
            # AUTO: Executes this statement.
            'stage': 'semantic'
        # AUTO: Closes the current grouped code/data.
        })
    
    # AUTO: Handles the matching error case.
    except Exception as e:
        # AUTO: Returns this result to the caller.
        return jsonify({
            # AUTO: Executes this statement.
            'error': f'Server error: {str(e)}'
        # AUTO: Closes the current grouped code/data.
        }), 500

# AUTO: Attaches this decorator to the next function/class.
@app.route('/api/icg', methods=['POST'])
# AUTO: Defines function `icg_endpoint`.
def icg_endpoint():
    # AUTO: Starts protected code that can catch errors.
    try:
        # AUTO: Sets `data`.
        data = request.get_json()

        # AUTO: Checks this condition.
        if not data or 'source_code' not in data:
            # AUTO: Returns this result to the caller.
            return jsonify({
                # AUTO: Executes this statement.
                'error': 'Missing source_code in request body'
            # AUTO: Closes the current grouped code/data.
            }), 400

        # AUTO: Sets `source_code`.
        source_code = data['source_code']

        # AUTO: Sets `tokens, lex_errors`.
        tokens, lex_errors = lex(source_code)

        # AUTO: Sets `token_list`.
        token_list = []
        # AUTO: Starts a loop over these values.
        for token in tokens:
            # AUTO: Appends a value to a list.
            token_list.append({
                # AUTO: Executes this statement.
                'type': token.type,
                # AUTO: Calls `_display_value`.
                'value': _display_value(token.value),
                # AUTO: Executes this statement.
                'line': token.line,
                # AUTO: Calls `getattr`.
                'col': getattr(token, 'col', 0),
                # AUTO: Calls `get_token_description`.
                'description': get_token_description(token.type, token.value)
            # AUTO: Closes the current grouped code/data.
            })

        # AUTO: Checks this condition.
        if lex_errors:
            # AUTO: Returns this result to the caller.
            return jsonify({
                # AUTO: Executes this statement.
                'success': False,
                # AUTO: Executes this statement.
                'tokens': token_list,
                # AUTO: Executes this statement.
                'errors': lex_errors,
                # AUTO: Executes this statement.
                'stage': 'lexical'
            # AUTO: Closes the current grouped code/data.
            })

        # AUTO: Sets `parse_result`.
        parse_result = parser.parse_and_build(tokens)
        # AUTO: Checks this condition.
        if not parse_result['success']:
            # AUTO: Sets `error_stage`.
            error_stage = parse_result.get('error_stage', 'syntax')
            # AUTO: Returns this result to the caller.
            return jsonify({
                # AUTO: Executes this statement.
                'success': False,
                # AUTO: Executes this statement.
                'tokens': token_list,
                # AUTO: Executes this statement.
                'errors': parse_result['errors'],
                # AUTO: Executes this statement.
                'stage': error_stage
            # AUTO: Closes the current grouped code/data.
            })

        # AUTO: Sets `semantic_result`.
        semantic_result = validate_ast(parse_result['ast'], parse_result['symbol_table'])
        # AUTO: Checks this condition.
        if not semantic_result['success']:
            # AUTO: Returns this result to the caller.
            return jsonify({
                # AUTO: Executes this statement.
                'success': False,
                # AUTO: Executes this statement.
                'tokens': token_list,
                # AUTO: Executes this statement.
                'errors': semantic_result['errors'],
                # AUTO: Executes this statement.
                'warnings': semantic_result['warnings'],
                # AUTO: Executes this statement.
                'stage': 'semantic'
            # AUTO: Closes the current grouped code/data.
            })

        # AUTO: Sets `icg_result`.
        icg_result = generate_icg(tokens)

        # AUTO: Returns this result to the caller.
        return jsonify({
            # AUTO: Executes this statement.
            'success': icg_result['success'],
            # AUTO: Executes this statement.
            'tokens': token_list,
            # AUTO: Executes this statement.
            'tac': icg_result['tac'],
            # AUTO: Executes this statement.
            'tac_text': icg_result['tac_text'],
            # AUTO: Executes this statement.
            'errors': icg_result['errors'],
            # AUTO: Calls `semantic_result.get`.
            'warnings': semantic_result.get('warnings', []),
            # AUTO: Executes this statement.
            'stage': 'icg'
        # AUTO: Closes the current grouped code/data.
        })

    # AUTO: Handles the matching error case.
    except Exception as e:
        # AUTO: Returns this result to the caller.
        return jsonify({
            # AUTO: Executes this statement.
            'error': f'Server error: {str(e)}'
        # AUTO: Closes the current grouped code/data.
        }), 500


# AUTO: Defines class `OutputCollector`.
class OutputCollector:
    # AUTO: Defines function `__init__`.
    def __init__(self):
        # AUTO: Sets `self.outputs`.
        self.outputs = []
        # AUTO: Sets `self.needs_input`.
        self.needs_input = False

    # AUTO: Defines function `emit`.
    def emit(self, event, data=None, **kwargs):
        # AUTO: Checks this condition.
        if event == 'output' and data:
            # AUTO: Appends a value to a list.
            self.outputs.append(data.get('output', ''))
        # AUTO: Checks the next alternate condition.
        elif event == 'input_required':
            # AUTO: Sets `self.needs_input`.
            self.needs_input = True
            # AUTO: Stops this flow by raising an error.
            raise _InputNeeded()


# AUTO: Defines class `_InputNeeded`.
class _InputNeeded(Exception):
    # AUTO: Does nothing for this required block.
    pass


# GUIDE: Full non-interactive compiler pipeline from source code to output.
# AUTO: Attaches this decorator to the next function/class.
@app.route('/api/run', methods=['POST'])
# AUTO: Defines function `run_endpoint`.
def run_endpoint():
    # AUTO: Starts protected code that can catch errors.
    try:
        # LINE: Read JSON request body sent by the frontend.
        data = request.get_json()
        # LINE: Reject request if editor source code is missing.
        if not data or 'source_code' not in data:
            # AUTO: Returns this result to the caller.
            return jsonify({'error': 'Missing source_code in request body'}), 400

        # LINE: Store the full editor text in source_code.
        source_code = data['source_code']

        # LINE: Stage 1, scan source code into lexer tokens.
        tokens, lex_errors = lex(source_code)
        # LINE: Stop pipeline if lexer found invalid characters/delimiters.
        if lex_errors:
            # AUTO: Returns this result to the caller.
            return jsonify({
                # AUTO: Executes this statement.
                'success': False,
                # AUTO: Executes this statement.
                'stage': 'lexical',
                # AUTO: Executes this statement.
                'output': [],
                # AUTO: Executes this statement.
                'errors': lex_errors
            # AUTO: Closes the current grouped code/data.
            })

        # LINE: Stage 2, parse tokens and build AST if syntax is valid.
        parse_result = parser.parse_and_build(tokens)
        # LINE: Stop pipeline if syntax or builder semantic checks failed.
        if not parse_result['success']:
            # AUTO: Sets `error_stage`.
            error_stage = parse_result.get('error_stage', 'syntax')
            # AUTO: Returns this result to the caller.
            return jsonify({
                # AUTO: Executes this statement.
                'success': False,
                # AUTO: Executes this statement.
                'stage': error_stage,
                # AUTO: Executes this statement.
                'output': [],
                # AUTO: Executes this statement.
                'errors': [str(e) for e in parse_result['errors']]
            # AUTO: Closes the current grouped code/data.
            })

        # LINE: Stage 3, validate AST semantic rules.
        semantic_result = validate_ast(parse_result['ast'], parse_result['symbol_table'])
        # LINE: Stop pipeline if semantic analyzer found errors.
        if not semantic_result['success']:
            # AUTO: Returns this result to the caller.
            return jsonify({
                # AUTO: Executes this statement.
                'success': False,
                # AUTO: Executes this statement.
                'stage': 'semantic',
                # AUTO: Executes this statement.
                'output': [],
                # AUTO: Executes this statement.
                'errors': [str(e) for e in semantic_result['errors']]
            # AUTO: Closes the current grouped code/data.
            })

        # LINE: Get the validated AST for execution.
        ast = semantic_result['ast']

        # LINE: Collector captures plant() output for non-socket /api/run.
        collector = OutputCollector()
        # LINE: Create interpreter and give it the collector as output target.
        interp = Interpreter(socketio=collector)
        # AUTO: Starts protected code that can catch errors.
        try:
            # LINE: Stage 4, execute ProgramNode through interpreter.
            interp.interpret(ast)
            # LINE: Return successful runtime output to frontend.
            return jsonify({
                # AUTO: Executes this statement.
                'success': True,
                # AUTO: Executes this statement.
                'stage': 'execution',
                # AUTO: Executes this statement.
                'output': collector.outputs,
                # AUTO: Executes this statement.
                'errors': []
            # AUTO: Closes the current grouped code/data.
            })
        # AUTO: Handles the matching error case.
        except _InputNeeded:
            # LINE: Non-interactive endpoint cannot continue if water() needs input.
            return jsonify({
                # AUTO: Executes this statement.
                'success': False,
                # AUTO: Executes this statement.
                'stage': 'execution',
                # AUTO: Executes this statement.
                'output': collector.outputs,
                # AUTO: Executes this statement.
                'errors': ['Program requires interactive input (water())'],
                # AUTO: Executes this statement.
                'needs_input': True
            # AUTO: Closes the current grouped code/data.
            })
        # AUTO: Handles the matching error case.
        except InterpreterError as e:
            # LINE: Runtime error from interpreter, such as division by zero.
            collector.outputs.append(f'Runtime Error: {e}')
            # AUTO: Returns this result to the caller.
            return jsonify({
                # AUTO: Executes this statement.
                'success': False,
                # AUTO: Executes this statement.
                'stage': 'execution',
                # AUTO: Executes this statement.
                'output': collector.outputs,
                # AUTO: Executes this statement.
                'errors': [str(e)]
            # AUTO: Closes the current grouped code/data.
            })
        # AUTO: Handles the matching error case.
        except Exception as e:
            # LINE: Unexpected server/interpreter exception.
            collector.outputs.append(f'Internal Error: {e}')
            # AUTO: Returns this result to the caller.
            return jsonify({
                # AUTO: Executes this statement.
                'success': False,
                # AUTO: Executes this statement.
                'stage': 'execution',
                # AUTO: Executes this statement.
                'output': collector.outputs,
                # AUTO: Executes this statement.
                'errors': [str(e)]
            # AUTO: Closes the current grouped code/data.
            })

    # AUTO: Handles the matching error case.
    except Exception as e:
        # LINE: Last-resort server error response.
        return jsonify({'error': f'Server error: {str(e)}'}), 500


# AUTO: Attaches this decorator to the next function/class.
@socketio.on('connect')
# AUTO: Defines function `handle_connect`.
def handle_connect():
    # AUTO: Does nothing for this required block.
    pass

# AUTO: Attaches this decorator to the next function/class.
@socketio.on('disconnect')
# AUTO: Defines function `handle_disconnect`.
def handle_disconnect():
    # AUTO: Sets `sid`.
    sid = request.sid
    # AUTO: Removes and returns an item.
    interpreters.pop(sid, None)

# AUTO: Attaches this decorator to the next function/class.
@socketio.on('run_code')
# AUTO: Defines function `handle_run_code`.
def handle_run_code(data):
    # LINE: sid identifies the browser session running this code.
    sid = request.sid
    # LINE: Read current editor source from Socket.IO payload.
    source_code = data.get('source_code', '')

    # LINE: Stage 1, lex source code.
    tokens, lex_errors = lex(source_code)
    # LINE: Send lexical errors directly to the terminal output.
    if lex_errors:
        # AUTO: Starts a loop over these values.
        for err in lex_errors:
            # AUTO: Calls `emit`.
            emit('output', {'output': f'Lexical Error: {err}'})
        # AUTO: Calls `emit`.
        emit('execution_complete', {'success': False, 'stage': 'lexical'})
        # AUTO: Returns this result to the caller.
        return

    # LINE: Notify frontend that lexical stage passed.
    emit('stage_complete', {'stage': 'lexical', 'success': True})

    # LINE: Stage 2, parse and build AST.
    parse_result = parser.parse_and_build(tokens)
    # LINE: Stop if syntax/builder failed.
    if not parse_result['success']:
        # AUTO: Sets `error_stage`.
        error_stage = parse_result.get('error_stage', 'syntax')
        # AUTO: Starts a loop over these values.
        for err in parse_result['errors']:
            # AUTO: Calls `emit`.
            emit('output', {'output': f'{err}'})
        # AUTO: Calls `emit`.
        emit('execution_complete', {'success': False, 'stage': error_stage})
        # AUTO: Returns this result to the caller.
        return

    # LINE: Notify frontend that syntax stage passed.
    emit('stage_complete', {'stage': 'syntax', 'success': True})

    # LINE: Stage 3, semantic validation.
    semantic_result = validate_ast(parse_result['ast'], parse_result['symbol_table'])
    # LINE: Stop if semantic validation failed.
    if not semantic_result['success']:
        # AUTO: Starts a loop over these values.
        for err in semantic_result['errors']:
            # AUTO: Calls `emit`.
            emit('output', {'output': f'{err}'})
        # AUTO: Calls `emit`.
        emit('execution_complete', {'success': False, 'stage': 'semantic'})
        # AUTO: Returns this result to the caller.
        return

    # LINE: Notify frontend that semantic stage passed.
    emit('stage_complete', {'stage': 'semantic', 'success': True})

    # LINE: Save validated AST before execution.
    ast = semantic_result['ast']

    # LINE: Cancel any previous interpreter still waiting/running for this session.
    old_interp = interpreters.get(sid)
    # AUTO: Checks this condition.
    if old_interp and hasattr(old_interp, '_cancelled'):
        # AUTO: Sets `old_interp._cancelled`.
        old_interp._cancelled = True
        # AUTO: Starts a loop over these values.
        for evt in list(old_interp.input_events.values()):
            # AUTO: Starts protected code that can catch errors.
            try:
                # AUTO: Calls `evt.send`.
                evt.send(None)
            # AUTO: Handles the matching error case.
            except (AttributeError, AssertionError):
                # AUTO: Starts protected code that can catch errors.
                try:
                    # AUTO: Calls `evt.set`.
                    evt.set()
                # AUTO: Handles the matching error case.
                except Exception:
                    # AUTO: Does nothing for this required block.
                    pass

    # Runs in the background so water() can pause and receive browser input.
    # AUTO: Defines function `run_interpreter`.
    def run_interpreter():
        # AUTO: Starts protected code that can catch errors.
        try:
            # LINE: Emitter sends plant()/water() events to this browser session only.
            session_emitter = SessionEmitter(socketio, sid)
            # LINE: Create one interpreter instance for this run.
            interp = Interpreter(socketio=session_emitter)
            # LINE: Runtime cancellation flag used when rerunning code.
            interp._cancelled = False
            # LINE: Store interpreter so capture_input can find it later.
            interpreters[sid] = interp
            # LINE: Execute the validated AST.
            interp.interpret(ast)
            # LINE: Tell UI execution completed if run was not cancelled.
            if not interp._cancelled:
                # AUTO: Sets `socketio.emit('execution_complete', {'success': True, 'stage': 'execution'}, to`.
                socketio.emit('execution_complete', {'success': True, 'stage': 'execution'}, to=sid)
        # AUTO: Handles the matching error case.
        except _CancelledError:
            # AUTO: Does nothing for this required block.
            pass
        # AUTO: Handles the matching error case.
        except InterpreterError as e:
            # LINE: Send runtime errors to the output panel.
            if not getattr(interp, '_cancelled', False):
                # AUTO: Sets `socketio.emit('output', {'output': f'Runtime Error: {e}'}, to`.
                socketio.emit('output', {'output': f'Runtime Error: {e}'}, to=sid)
                # AUTO: Sets `socketio.emit('execution_complete', {'success': False, 'stage': 'execution'}, to`.
                socketio.emit('execution_complete', {'success': False, 'stage': 'execution'}, to=sid)
        # AUTO: Handles the matching error case.
        except Exception as e:
            # LINE: Send unexpected internal errors to the output panel.
            if not getattr(interp, '_cancelled', False):
                # AUTO: Sets `socketio.emit('output', {'output': f'Internal Error: {e}'}, to`.
                socketio.emit('output', {'output': f'Internal Error: {e}'}, to=sid)
                # AUTO: Sets `socketio.emit('execution_complete', {'success': False, 'stage': 'execution'}, to`.
                socketio.emit('execution_complete', {'success': False, 'stage': 'execution'}, to=sid)
        # AUTO: Runs cleanup code no matter what happened.
        finally:
            # LINE: Remove finished interpreter from active session map.
            if interpreters.get(sid) is interp:
                # AUTO: Removes and returns an item.
                interpreters.pop(sid, None)

    # LINE: Start interpreter in background so UI remains responsive.
    socketio.start_background_task(run_interpreter)

# AUTO: Attaches this decorator to the next function/class.
@socketio.on('capture_input')
# AUTO: Defines function `handle_capture_input`.
def handle_capture_input(data):
    # LINE: Identify which browser session sent the water() answer.
    sid = request.sid
    # LINE: Find that session's waiting interpreter.
    interp = interpreters.get(sid)
    # AUTO: Checks this condition.
    if interp:
        # LINE: Get variable name and input value from frontend payload.
        var_name = data.get('var_name', '')
        # AUTO: Sets `input_value`.
        input_value = data.get('input', '')
        # LINE: Resume the interpreter waiting inside eval_input().
        interp.provide_input(var_name, input_value)


# AUTO: Sets `_prompt_path`.
_prompt_path = os.path.join(os.path.dirname(__file__), 'ai', 'prompt.txt')
# AUTO: Opens a managed resource/context.
with open(_prompt_path, 'r', encoding='utf-8') as _f:
    # AUTO: Sets `GAL_SYSTEM_PROMPT`.
    GAL_SYSTEM_PROMPT = _f.read()


# AUTO: Sets `_gemini_client`.
_gemini_client = None
# AUTO: Sets `_chat_sessions`.
_chat_sessions = {}

# AUTO: Defines function `_get_gemini_client`.
def _get_gemini_client():
    # AUTO: Uses a module-level variable inside this function.
    global _gemini_client
    # AUTO: Checks this condition.
    if _gemini_client is None:
        # AUTO: Sets `api_key`.
        api_key = os.environ.get('GEMINI_API_KEY', '')
        # AUTO: Checks this condition.
        if not api_key:
            # AUTO: Returns this result to the caller.
            return None
        # AUTO: Sets `_gemini_client`.
        _gemini_client = genai.Client(api_key=api_key)
    # AUTO: Returns this result to the caller.
    return _gemini_client

# AUTO: Attaches this decorator to the next function/class.
@app.route('/api/chat', methods=['POST'])
# AUTO: Defines function `chat_endpoint`.
def chat_endpoint():
    # AUTO: Starts protected code that can catch errors.
    try:
        # AUTO: Sets `data`.
        data = request.get_json()
        # AUTO: Checks this condition.
        if not data or 'message' not in data:
            # AUTO: Returns this result to the caller.
            return jsonify({'error': 'Missing message in request body'}), 400

        # AUTO: Sets `user_message`.
        user_message = data['message']
        # AUTO: Sets `session_id`.
        session_id = data.get('session_id', 'default')
        # AUTO: Sets `editor_code`.
        editor_code = data.get('editor_code', '')

        # AUTO: Sets `client`.
        client = _get_gemini_client()
        # AUTO: Checks this condition.
        if client is None:
            # AUTO: Sets `fb_reply`.
            fb_reply = fallback_reply(user_message)
            # AUTO: Returns this result to the caller.
            return jsonify({'reply': fb_reply, 'mode': 'fallback'})

        # AUTO: Checks this condition.
        if session_id not in _chat_sessions:
            # AUTO: Sets `_chat_sessions[session_id]`.
            _chat_sessions[session_id] = []
        # AUTO: Sets `history`.
        history = _chat_sessions[session_id]

        # AUTO: Sets `full_message`.
        full_message = user_message
        # AUTO: Checks this condition.
        if editor_code.strip():
            # AUTO: Sets `full_message`.
            full_message = f"[Current code in editor]:\n```\n{editor_code}\n```\n\nUser question: {user_message}"

        # AUTO: Appends a value to a list.
        history.append({'role': 'user', 'parts': [{'text': full_message}]})

        # AUTO: Checks this condition.
        if len(history) > 20:
            # AUTO: Sets `history[:]`.
            history[:] = history[-20:]

        # AUTO: Sets `models_to_try`.
        models_to_try = ['gemini-2.5-flash', 'gemini-2.5-flash-lite', 'gemini-2.0-flash', 'gemini-2.0-flash-lite']
        # AUTO: Sets `last_error: Exception`.
        last_error: Exception = RuntimeError("No Gemini models were available to try")
        # AUTO: Starts a loop over these values.
        for model_name in models_to_try:
            # AUTO: Starts protected code that can catch errors.
            try:
                # AUTO: Sets `response`.
                response = client.models.generate_content(
                    # AUTO: Sets `model`.
                    model=model_name,
                    # AUTO: Sets `contents`.
                    contents=history,
                    # AUTO: Sets `config`.
                    config=genai.types.GenerateContentConfig(
                        # AUTO: Sets `system_instruction`.
                        system_instruction=GAL_SYSTEM_PROMPT,
                        # AUTO: Sets `temperature`.
                        temperature=0.3,
                        # AUTO: Sets `max_output_tokens`.
                        max_output_tokens=4096,
                    # AUTO: Closes the current grouped code/data.
                    ),
                # AUTO: Closes the current grouped code/data.
                )
                # AUTO: Stops the nearest loop.
                break
            # AUTO: Handles the matching error case.
            except Exception as model_err:
                # AUTO: Sets `last_error`.
                last_error = model_err
                # AUTO: Sets `err_msg`.
                err_msg = str(model_err)
                # AUTO: Checks this condition.
                if '429' not in err_msg and 'RESOURCE_EXHAUSTED' not in err_msg and '503' not in err_msg and 'UNAVAILABLE' not in err_msg and '403' not in err_msg and 'PERMISSION_DENIED' not in err_msg:
                    # AUTO: Executes this statement.
                    raise
                # AUTO: Skips to the next loop iteration.
                continue
        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Stops this flow by raising an error.
            raise last_error

        # AUTO: Sets `reply`.
        reply = response.text or 'No response generated.'

        # AUTO: Appends a value to a list.
        history.append({'role': 'model', 'parts': [{'text': reply}]})

        # AUTO: Returns this result to the caller.
        return jsonify({'reply': reply, 'mode': 'ai'})

    # AUTO: Handles the matching error case.
    except Exception as e:
        # AUTO: Starts protected code that can catch errors.
        try:
            # AUTO: Sets `fb_reply`.
            fb_reply = fallback_reply(user_message)
            # AUTO: Returns this result to the caller.
            return jsonify({'reply': fb_reply, 'mode': 'fallback'})
        # AUTO: Handles the matching error case.
        except Exception:
            # AUTO: Does nothing for this required block.
            pass
        # AUTO: Sets `err_str`.
        err_str = str(e)
        # AUTO: Returns this result to the caller.
        return jsonify({'error': f'Chat error: {err_str}'}), 500

# AUTO: Attaches this decorator to the next function/class.
@app.route('/api/chat/clear', methods=['POST'])
# AUTO: Defines function `chat_clear_endpoint`.
def chat_clear_endpoint():
    # AUTO: Sets `data`.
    data = request.get_json() or {}
    # AUTO: Sets `session_id`.
    session_id = data.get('session_id', 'default')
    # AUTO: Removes and returns an item.
    _chat_sessions.pop(session_id, None)
    # AUTO: Returns this result to the caller.
    return jsonify({'success': True})


# AUTO: Checks this condition.
if __name__ == '__main__':
    # AUTO: Sets `port`.
    port = int(os.environ.get('PORT', 5000))
    # AUTO: Executes this statement.
    debug = os.environ.get('DEBUG', 'False') == 'True'

    # AUTO: Calls `print`.
    print("Starting GAL Compiler Server...")
    # AUTO: Calls `print`.
    print(f"Server running at http://0.0.0.0:{port}")
    # AUTO: Calls `print`.
    print("API endpoints:")
    # AUTO: Calls `print`.
    print(f"  - POST http://localhost:{port}/api/lex (Lexical Analysis)")
    # AUTO: Calls `print`.
    print(f"  - POST http://localhost:{port}/api/parse (Syntax Analysis)")
    # AUTO: Calls `print`.
    print(f"  - POST http://localhost:{port}/api/semantic (Semantic Analysis)")
    # AUTO: Calls `print`.
    print(f"  - POST http://localhost:{port}/api/icg (Intermediate Code Generation)")
    # AUTO: Calls `print`.
    print(f"  - POST http://localhost:{port}/api/chat (AI Chat Helper)")
    # AUTO: Calls `print`.
    print(f"  - Socket.IO: run_code (Execute Program)")
    # AUTO: Sets `socketio.run(app, host`.
    socketio.run(app, host='0.0.0.0', port=port, debug=debug, allow_unsafe_werkzeug=True)
