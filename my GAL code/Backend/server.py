from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from lexer import lex

app = Flask(__name__, static_folder='../UI', static_url_path='')
CORS(app)

@app.route('/')
def index():
    """Serve the main HTML file"""
    return send_from_directory('../UI', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files (CSS, JS, images, etc.)"""
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
                'value': token.value if token.value is not None else '',
                'line': token.line
            })
        
        return jsonify({
            'tokens': token_list,
            'errors': errors
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
        'message': 'GAL Lexer Server is running'
    })

if __name__ == '__main__':
    print("Starting GAL Lexer Server...")
    print("Server running at http://localhost:5000")
    print("API endpoint: POST http://localhost:5000/api/lex")
    app.run(host='0.0.0.0', port=5000, debug=True)
