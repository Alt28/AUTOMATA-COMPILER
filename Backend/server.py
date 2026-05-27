
# WARNING SUPPRESSION + EVENTLET BOOTSTRAP
import warnings
warnings.filterwarnings("ignore", message=".*RLock.*were not greened.*")

import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
from google import genai
from lexer import lex, get_token_description
from parser import LL1Parser
from cfg import cfg, first_sets, predict_sets
from parser.builder import analyze_semantics
from semantic import validate_ast
from icg import generate_icg
from interpreter import Interpreter, InterpreterError, _CancelledError
from ai import fallback_reply


def _display_value(val):
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

interpreters = {}


class SessionEmitter:
    def __init__(self, sio, sid):
        self._sio = sio
        self._sid = sid

    def emit(self, event, data=None, **kwargs):
        self._sio.emit(event, data, to=self._sid, **kwargs)


parser = LL1Parser(
    cfg=cfg,
    predict_sets=predict_sets,
    first_sets=first_sets,
    start_symbol="<program>",
    end_marker="EOF",
    skip_token_types={'\n', 'comment', 'mcommentlit'}
)

@app.after_request
def add_no_cache(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/')
def index():
    return send_from_directory('../UI', 'index.html')

@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory('../images', filename)

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../UI', path)


@app.route('/api/lex', methods=['POST'])
def lexer_endpoint():
    try:
        data = request.get_json()
        
        if not data or 'source_code' not in data:
            return jsonify({
                'error': 'Missing source_code in request body'
            }), 400
        
        source_code = data['source_code']
        
        tokens, errors = lex(source_code)
        
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
    try:
        data = request.get_json()
        
        if not data or 'source_code' not in data:
            return jsonify({
                'error': 'Missing source_code in request body'
            }), 400
        
        source_code = data['source_code']
        
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
                'stage': ['lexical'],
                'lexical_errors': True,
                'syntax_errors': False
            })

        parse_success, parse_errors = parser.parse(tokens)
        
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
    return jsonify({
        'status': 'healthy',
        'message': 'GAL Compiler Server is running'
    })


@app.route('/api/semantic', methods=['POST'])
def semantic_endpoint():
    try:
        data = request.get_json()
        
        if not data or 'source_code' not in data:
            return jsonify({
                'error': 'Missing source_code in request body'
            }), 400
        
        source_code = data['source_code']
        
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
                'warnings': [],
                'stage': 'lexical'
            })
        
        parse_result = parser.parse_and_build(tokens)
        
        if not parse_result['success']:
            error_stage = parse_result.get('error_stage', 'syntax')
            return jsonify({
                'success': False,
                'tokens': token_list,
                'errors': parse_result['errors'],
                'warnings': [],
                'stage': error_stage
            })
        
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
    try:
        data = request.get_json()

        if not data or 'source_code' not in data:
            return jsonify({
                'error': 'Missing source_code in request body'
            }), 400

        source_code = data['source_code']

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

        parse_result = parser.parse_and_build(tokens)
        if not parse_result['success']:
            error_stage = parse_result.get('error_stage', 'syntax')
            return jsonify({
                'success': False,
                'tokens': token_list,
                'errors': parse_result['errors'],
                'stage': error_stage
            })

        semantic_result = validate_ast(parse_result['ast'], parse_result['symbol_table'])
        if not semantic_result['success']:
            return jsonify({
                'success': False,
                'tokens': token_list,
                'errors': semantic_result['errors'],
                'warnings': semantic_result['warnings'],
                'stage': 'semantic'
            })

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


class OutputCollector:
    def __init__(self):
        self.outputs = []
        self.needs_input = False

    def emit(self, event, data=None, **kwargs):
        if event == 'output' and data:
            self.outputs.append(data.get('output', ''))
        elif event == 'input_required':
            self.needs_input = True
            raise _InputNeeded()


class _InputNeeded(Exception):
    pass


@app.route('/api/run', methods=['POST'])
def run_endpoint():
    try:
        data = request.get_json()
        if not data or 'source_code' not in data:
            return jsonify({'error': 'Missing source_code in request body'}), 400

        source_code = data['source_code']

        tokens, lex_errors = lex(source_code)
        if lex_errors:
            return jsonify({
                'success': False,
                'stage': 'lexical',
                'output': [],
                'errors': lex_errors
            })

        parse_result = parser.parse_and_build(tokens)
        if not parse_result['success']:
            error_stage = parse_result.get('error_stage', 'syntax')
            return jsonify({
                'success': False,
                'stage': error_stage,
                'output': [],
                'errors': [str(e) for e in parse_result['errors']]
            })

        semantic_result = validate_ast(parse_result['ast'], parse_result['symbol_table'])
        if not semantic_result['success']:
            return jsonify({
                'success': False,
                'stage': 'semantic',
                'output': [],
                'errors': [str(e) for e in semantic_result['errors']]
            })

        ast = semantic_result['ast']

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


@socketio.on('connect')
def handle_connect():
    pass

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    interpreters.pop(sid, None)

@socketio.on('run_code')
def handle_run_code(data):
    sid = request.sid
    source_code = data.get('source_code', '')

    tokens, lex_errors = lex(source_code)
    if lex_errors:
        for err in lex_errors:
            emit('output', {'output': f'Lexical Error: {err}'})
        emit('execution_complete', {'success': False, 'stage': 'lexical'})
        return

    emit('stage_complete', {'stage': 'lexical', 'success': True})

    parse_result = parser.parse_and_build(tokens)
    if not parse_result['success']:
        error_stage = parse_result.get('error_stage', 'syntax')
        for err in parse_result['errors']:
            emit('output', {'output': f'{err}'})
        emit('execution_complete', {'success': False, 'stage': error_stage})
        return

    emit('stage_complete', {'stage': 'syntax', 'success': True})

    semantic_result = validate_ast(parse_result['ast'], parse_result['symbol_table'])
    if not semantic_result['success']:
        for err in semantic_result['errors']:
            emit('output', {'output': f'{err}'})
        emit('execution_complete', {'success': False, 'stage': 'semantic'})
        return

    emit('stage_complete', {'stage': 'semantic', 'success': True})

    ast = semantic_result['ast']

    old_interp = interpreters.get(sid)
    if old_interp and hasattr(old_interp, '_cancelled'):
        old_interp._cancelled = True
        for evt in list(old_interp.input_events.values()):
            try:
                evt.send(None)
            except (AttributeError, AssertionError):
                try:
                    evt.set()
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
            pass
        except InterpreterError as e:
            if not getattr(interp, '_cancelled', False):
                socketio.emit('output', {'output': f'Runtime Error: {e}'}, to=sid)
                socketio.emit('execution_complete', {'success': False, 'stage': 'execution'}, to=sid)
        except Exception as e:
            if not getattr(interp, '_cancelled', False):
                socketio.emit('output', {'output': f'Internal Error: {e}'}, to=sid)
                socketio.emit('execution_complete', {'success': False, 'stage': 'execution'}, to=sid)
        finally:
            if interpreters.get(sid) is interp:
                interpreters.pop(sid, None)

    socketio.start_background_task(run_interpreter)

@socketio.on('capture_input')
def handle_capture_input(data):
    sid = request.sid
    interp = interpreters.get(sid)
    if interp:
        var_name = data.get('var_name', '')
        input_value = data.get('input', '')
        interp.provide_input(var_name, input_value)


_prompt_path = os.path.join(os.path.dirname(__file__), 'ai', 'prompt.txt')
with open(_prompt_path, 'r', encoding='utf-8') as _f:
    GAL_SYSTEM_PROMPT = _f.read()


_gemini_client = None
_chat_sessions = {}

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
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message in request body'}), 400

        user_message = data['message']
        session_id = data.get('session_id', 'default')
        editor_code = data.get('editor_code', '')

        client = _get_gemini_client()
        if client is None:
            fb_reply = fallback_reply(user_message)
            return jsonify({'reply': fb_reply, 'mode': 'fallback'})

        if session_id not in _chat_sessions:
            _chat_sessions[session_id] = []
        history = _chat_sessions[session_id]

        full_message = user_message
        if editor_code.strip():
            full_message = f"[Current code in editor]:\n```\n{editor_code}\n```\n\nUser question: {user_message}"

        history.append({'role': 'user', 'parts': [{'text': full_message}]})

        if len(history) > 20:
            history[:] = history[-20:]

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
                break
            except Exception as model_err:
                last_error = model_err
                err_msg = str(model_err)
                if '429' not in err_msg and 'RESOURCE_EXHAUSTED' not in err_msg and '503' not in err_msg and 'UNAVAILABLE' not in err_msg and '403' not in err_msg and 'PERMISSION_DENIED' not in err_msg:
                    raise
                continue
        else:
            raise last_error

        reply = response.text or 'No response generated.'

        history.append({'role': 'model', 'parts': [{'text': reply}]})

        return jsonify({'reply': reply, 'mode': 'ai'})

    except Exception as e:
        try:
            fb_reply = fallback_reply(user_message)
            return jsonify({'reply': fb_reply, 'mode': 'fallback'})
        except Exception:
            pass
        err_str = str(e)
        return jsonify({'error': f'Chat error: {err_str}'}), 500

@app.route('/api/chat/clear', methods=['POST'])
def chat_clear_endpoint():
    data = request.get_json() or {}
    session_id = data.get('session_id', 'default')
    _chat_sessions.pop(session_id, None)
    return jsonify({'success': True})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False') == 'True'

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
