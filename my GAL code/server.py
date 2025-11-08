from __future__ import annotations

import os
import time
from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO

from GALalexer import lex


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder='.', static_url_path='')
socketio = SocketIO(app, cors_allowed_origins='*')


@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')


@app.route('/api/lex', methods=['POST'])
def api_lex():
    data = request.get_json(silent=True) or {}
    source = data.get('source_code', '')
    tokens, errors = lex(source)
    # Shape the response to match frontend expectation
    return jsonify({
        'tokens': [
            {
                'type': t.type,
                'value': t.value,
                'line': t.line
            } for t in tokens
        ],
        'errors': [str(e) for e in errors]
    })


@app.route('/api/semantic', methods=['POST'])
def api_semantic():
    # Semantic was removed from frontend; keep a stub returning not implemented if called directly
    return jsonify({'success': False, 'errors': ['Semantic analysis not available']}), 400


@app.route('/api/parse', methods=['POST'])
def api_parse():
    # Syntax was removed from frontend; keep a stub returning not implemented if called directly
    return jsonify({'success': False, 'errors': ['Syntax analysis not available']}), 400


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


if __name__ == '__main__':
    # Run dev server on port 5000 to match frontend Socket.IO URL
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
