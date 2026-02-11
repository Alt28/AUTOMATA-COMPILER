from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from lexer import lex, get_token_description
from Gal_Parser import LL1Parser
from cfg import cfg, first_sets, predict_sets
from semantic import analyze_semantics

app = Flask(__name__, static_folder='../UI', static_url_path='')
CORS(app)

# Initialize the parser once at startup
parser = LL1Parser(
    cfg=cfg,
    predict_sets=predict_sets,
    first_sets=first_sets,
    start_symbol="<program>",
    end_marker="EOF",
    skip_token_types={'\n'}  # Skip newline tokens
)

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
                'value': token.value if token.value is not None else '',
                'line': token.line,
                'col': getattr(token, 'col', 0),
                'description': get_token_description(token.type)
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
                'value': token.value if token.value is not None else '',
                'line': token.line,
                'col': getattr(token, 'col', 0),
                'description': get_token_description(token.type)
            })
        
        # Run the parser on the tokens (even if there are lexical errors)
        parse_success, parse_errors = parser.parse(tokens)
        
        # Combine lexical and syntax errors
        all_errors = lex_errors + parse_errors
        
        # Determine which stages have errors
        stages = []
        if lex_errors:
            stages.append('lexical')
        if parse_errors:
            stages.append('syntax')
        
        return jsonify({
            'success': parse_success and not lex_errors,
            'tokens': token_list,
            'errors': all_errors,
            'stage': stages if stages else ['success'],
            'lexical_errors': len(lex_errors) > 0,
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
                'value': token.value if token.value is not None else '',
                'line': token.line,
                'col': getattr(token, 'col', 0),
                'description': get_token_description(token.type)
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False') != 'True'
    
    print("Starting GAL Compiler Server...")
    print(f"Server running at http://0.0.0.0:{port}")
    print("API endpoints:")
    print(f"  - POST http://localhost:{port}/api/lex (Lexical Analysis)")
    print(f"  - POST http://localhost:{port}/api/parse (Syntax Analysis)")
    print(f"  - POST http://localhost:{port}/api/semantic (Semantic Analysis)")
    app.run(host='0.0.0.0', port=port, debug=debug)
