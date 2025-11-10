from __future__ import annotations

import os
import time
from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Simplify: use the working scanner in lexer.py directly for stability
try:
    from lexer import lex as BASE_LEX  # type: ignore
    ACTIVE_LEXER_NAME = 'lexer.py'
except Exception as e:  # last resort fallback to a simple_lexer implementation if present
    try:
        from simple_lexer import lex as BASE_LEX  # type: ignore
        ACTIVE_LEXER_NAME = 'simple_lexer'
    except Exception:
        raise RuntimeError(f'No usable lexer found: {e}')

app = Flask(__name__, static_folder='.', static_url_path='')
socketio = SocketIO(app, cors_allowed_origins='*')


@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')


@app.route('/api/lex', methods=['POST'])
def api_lex():
    data = request.get_json(silent=True) or {}
    source = data.get('source_code', '')
    try:
        print(f"API_LEX: received source len={len(source)} head={repr(source[:40])}")
    except Exception:
        pass
    tokens, errors = BASE_LEX(source)
    # Shape the response to match frontend expectation
    resp = {
        'tokens': [
            {
                'type': t.type,
                'value': t.value,
                'line': t.line
            } for t in tokens
        ],
        'errors': [str(e) for e in errors],
        'meta': {
            'lexer': ACTIVE_LEXER_NAME,
            'tokenCount': len(tokens),
            'errorCount': len(errors),
            'previewTypes': [t.type for t in tokens[:8]],
            'sourceLen': len(source)
        }
    }
    return jsonify(resp)


# Syntax and semantic analysis have been removed; only lexical API remains.


@app.route('/api/output', methods=['POST'])
def api_output():
    data = request.get_json(silent=True) or {}
    source = data.get('source_code', '')

    # For now, simulate program execution and stream a couple of lines
    socketio.emit('output', {'output': 'Program started...'})
    time.sleep(0.1)
    socketio.emit('output', {'output': f'Source length: {len(source)} chars'})
    time.sleep(0.1)
    socketio.emit('output', {'output': 'Program finished.'})

    return jsonify({'success': True})

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    # Run dev server on port 5000 to match frontend Socket.IO URL
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
