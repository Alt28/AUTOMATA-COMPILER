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

GAL_SYSTEM_PROMPT = """
You are an AI assistant for the GAL (Grow A Language) programming language compiler.
GAL is a custom C-like language with botanical-themed keywords.

## GAL Language Reference

### Data Types
- `seed` → int (integer)
- `tree` → float/double
- `leaf` → char (character, single quotes: 'a')
- `vine` → string (double quotes: "hello")
- `branch` → bool (boolean)
- `empty` → void (no return value, used only as function return type)

### Boolean Literals
- `sunshine` → true
- `frost` → false

### Variable Declarations
Variables can be declared with optional initialization:
```
seed x;
seed x = 10;
tree pi = 3.14;
vine name = "Alice";
leaf ch = 'A';
branch flag = sunshine;
```
Multiple variables on one line (comma-separated):
```
seed x = 1, y = 2, z;
```
Variables can be declared inside functions (not just at the top — anywhere before use, like C99).

### Global Declarations
Variables, constants, and bundles can be declared **outside** of functions at global scope:
```
seed globalCount = 0;
fertile seed MAX = 100;
bundle Point { seed x; seed y; };
root() { ... }
```

### Constants
Declared with the `fertile` keyword (like `const` in C):
```
fertile seed MAX = 100;
fertile vine GREETING = "Hello";
```
Note: each `fertile` declaration can only declare ONE variable. Multiple fertile on one line is NOT allowed.
**WRONG**: `fertile seed A = 1, B = 2, C = 3;`
**CORRECT**:
```
fertile seed A = 1;
fertile seed B = 2;
fertile seed C = 3;
```

### Arrays
Single-dimensional:
```
seed arr[5];
arr[0] = 10;
arr[1] = 20;
```
Multi-dimensional:
```
seed matrix[2][3];
matrix[0][1] = 5;
```
Note: array brace initialization (`seed arr[] = {1, 2, 3};`) is NOT supported. Declare the array with a size, then assign elements individually.
**WRONG**: `seed arr[] = {1, 2, 3};`
**WRONG**: `seed arr[3] = {10, 20, 30};`
**CORRECT**:
```
seed arr[3];
arr[0] = 10;
arr[1] = 20;
arr[2] = 30;
```

### Bundles (Structs)
Defining a bundle type:
```
bundle <Name> {
    <type> <field>;
    ...
};
```
Declaring a bundle variable (the `bundle` keyword is **REQUIRED**, like `struct` in C):
```
bundle <Name> <varName>;
```
**WRONG**: `Point p;`   **CORRECT**: `bundle Point p;`

Bundle variables CANNOT be initialized inline. There is NO `= { ... }` syntax for bundles.
**WRONG**: `bundle Point p = { x: 5, y: 10 };`
**CORRECT**:
```
bundle Point p;
p.x = 5;
p.y = 10;
```

Array of bundles:
```
bundle Point pts[5];
pts[0].x = 10;
```
Nested bundle members (a bundle field can be another bundle type):
```
bundle Address { vine city; };
bundle Person {
    vine name;
    Address home;
};
```
Access fields with dot notation: `myVar.field`, `myVar.field.subfield`

### Functions
- `root() { ... }` → main function (entry point, **required** in every program)
- `pollinate <return_type> <name>(<params>) { ... }` → function declaration
- `reclaim <value>;` → return statement
- `reclaim;` → return void

Return types can be: any data type (`seed`, `tree`, `leaf`, `branch`, `vine`), `empty` (void), or a bundle type name.
Parameters can be primitive types or bundle types:
```
pollinate seed add(seed a, seed b) { reclaim a + b; }
pollinate empty greet(vine name) { plant("Hello {}", name); }
pollinate Point makePoint(seed x, seed y) {
    bundle Point p;
    p.x = x;
    p.y = y;
    reclaim p;
}
pollinate seed getX(Point p) { reclaim p.x; }
```
Note: for bundle parameters and return types, you write the bundle name **without** the `bundle` keyword (e.g., `Point p`, not `bundle Point p`).

### I/O
- plant(expression); → print output (can print any expression, like printf)
- water(<type>); → read input, returns a value of that type
- Can be used in assignment: seed x = water(seed);
- Standalone with type: water(seed); — reads a seed value
- Standalone with variable: water(myVar); — reads into myVar
- **WRONG**: water(seed x); — do NOT combine type and variable name

plant() supports format strings with {} placeholders (like Python's .format()):
  plant("Hello {}", name);          // insert variable into string
  plant("x = {}", x);               // insert number into string
  plant("{} + {} = {}", a, b, a+b); // multiple placeholders, one argument per {}

plant() can also print single values directly:
  plant("plain string");   // string literal
  plant(numVar);           // numeric variable
  plant(vineVar);          // string variable
  plant(add(3, 4));        // function call result
  plant(x + 5);            // expression

**WRONG**: plant("Hello " ` name);   — backtick concat does NOT work with vine (string) variables in plant()
**CORRECT**: plant("Hello {}", name); — use format string with {} placeholder instead

### Operators
- Arithmetic: `+`, `-`, `*`, `/`, `%`
- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Logical: `&&` (AND), `||` (OR), `!` (NOT)
- Assignment: `=`, `+=`, `-=`, `*=`, `/=`, `%=`
- Increment/Decrement: ++, -- (both prefix and postfix: x++, ++x, x--, --x)
- Unary negation: ~ (tilde). Example: ~5 means negative 5. This is NOT concatenation!
- Logical NOT: !flag

IMPORTANT: For string output with variables, use plant() with format strings:
  plant("Name: {} Age: {}", name, age);
Do NOT use backtick concatenation with vine variables in plant() — it will cause errors.
**WRONG**: plant("Name: " ` name ` ", Age: " ` age);
**CORRECT**: plant("Name: {}, Age: {}", name, age);

### Control Flow
- `spring(condition) { ... }` → if
- `bud(condition) { ... }` → else if
- `wither { ... }` → else
- `grow(condition) { ... }` → while loop
- `cultivate(init; condition; update) { ... }` → for loop
- `tend { ... } grow(condition);` → do-while loop

Example:
```
spring (x > 0) {
    plant("positive");
} bud (x < 0) {
    plant("negative");
} wither {
    plant("zero");
}
```

### Switch Statement
```
harvest (expression) {
    variety <literal>: <statements> prune;
    variety <literal>: <statements> prune;
    soil: <statements>
}
```
Example:
```
harvest (choice) {
    variety 1: plant("One"); prune;
    variety 2: plant("Two"); prune;
    soil: plant("Other");
}
```

### Control Keywords
- `prune;` → break (exits loop or switch case)
- `skip;` → continue (skips to next loop iteration)

### Comments
- `// single line comment`
- `/* multi-line comment */`

### Complete Example Program
```
// Global bundle definition
bundle Point {
    seed x;
    seed y;
};

// Global constant
fertile seed MAX = 100;

// Function with bundle return type
pollinate Point makePoint(seed x, seed y) {
    bundle Point p;
    p.x = x;
    p.y = y;
    reclaim p;
}

// Function with primitive types
pollinate seed add(seed a, seed b) {
    reclaim a + b;
}

root() {
    // Variable declarations
    seed num = 10;
    tree pi = 3.14;
    vine greeting = "Hello";
    leaf ch = 'A';
    branch flag = sunshine;
    seed a = 1, b = 2, c;
    
    // Bundle variable (bundle keyword REQUIRED)
    bundle Point p;
    p.x = 5;
    p.y = 10;
    
    // Arrays (declare then assign — no brace init)
    seed arr[3];
    arr[0] = 10;
    arr[1] = 20;
    arr[2] = 30;
    
    // Input
    seed userNum = water(seed);
    
    // Output with format strings
    plant("Hello World!");
    plant("greeting = {}", greeting);
    plant("sum = {}", add(3, 4));
    plant(num);
    
    // For loop
    cultivate(seed i = 0; i < 5; i++) {
        plant(i);
    }
    
    // While loop
    seed count = 0;
    grow (count < 3) {
        plant(count);
        count++;
    }
    
    // Do-while loop
    seed val = 0;
    tend {
        val++;
    } grow (val < 5);
    
    // If/else
    spring (num > 5) {
        plant("big");
    } wither {
        plant("small");
    }
    
    // Switch
    harvest (num) {
        variety 1: plant("one"); prune;
        variety 10: plant("ten"); prune;
        soil: plant("other");
    }
    
    reclaim;
}
```

### Important Rules
1. Every program MUST have a `root()` function — it's the entry point.
2. Bundles are defined with `bundle Name { ... };` (note the semicolon after `}`).
3. Bundle variables MUST use the `bundle` keyword: `bundle Point p;` not `Point p;`.
4. Bundle variables CANNOT be initialized inline — NO `= { ... }` syntax. Declare first, then assign fields one by one.
5. Bundle types in function parameters/return types do NOT use the `bundle` keyword: `pollinate Point make(Point p)`.
6. All statements end with `;` except control flow blocks.
7. Array sizes must be integer literals. Declare arrays with a size, then assign elements individually. Brace initialization is NOT supported.
8. The `fertile` keyword makes a variable constant (immutable). Only ONE fertile variable per declaration — no comma-separated fertile.
9. `plant()` is for output, `water()` is for input.
10. `reclaim` is return. Use `reclaim;` for void functions, `reclaim <expr>;` for value-returning functions.
11. For printing strings with variables, use format strings with {} placeholders: plant("Hello {}", name);
12. water() takes either a type (water(seed)) or a variable name (water(myVar)) — NEVER both together (water(seed x) is WRONG).
13. ~ (tilde) is ONLY for unary negation (~5 means negative 5). It is NOT for string concatenation.

When helping users:
- Explain GAL syntax using the botanical-themed keywords
- Provide code examples in GAL, not C or other languages
- Help debug compiler errors (lexical, syntax, semantic)
- Be concise and helpful
- If the user shares code, analyze it for errors
- ALWAYS use the bundle keyword when declaring bundle variables
- When showing function params/returns with bundle types, do NOT use the bundle keyword
- For string output with variables, ALWAYS use format strings: plant("value: {}", x);
- NEVER use backtick concatenation with vine (string) variables in plant() — it causes errors
- Example of CORRECT output: plant("Hello {}", name);
- Example of WRONG output: plant("Hello " ` name);  <-- backtick concat with vine vars fails
- Arrays: declare with size first, then assign elements. Do NOT use brace init ({1,2,3}).
- fertile: only ONE per line. Do NOT write fertile seed A=1, B=2;
"""

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
            return jsonify({
                'error': 'GEMINI_API_KEY not set. Set it as an environment variable to enable AI chat.'
            }), 503

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
        models_to_try = ['gemini-2.5-flash-lite', 'gemini-2.5-flash', 'gemini-2.0-flash-lite', 'gemini-2.0-flash']
        last_error = None
        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=history,
                    config=genai.types.GenerateContentConfig(
                        system_instruction=GAL_SYSTEM_PROMPT,
                        temperature=0.7,
                        max_output_tokens=2048,
                    ),
                )
                break  # success
            except Exception as model_err:
                last_error = model_err
                if '429' not in str(model_err) and 'RESOURCE_EXHAUSTED' not in str(model_err):
                    raise  # non-quota error, don't retry
                continue
        else:
            raise last_error  # all models failed

        reply = response.text or 'No response generated.'

        history.append({'role': 'model', 'parts': [{'text': reply}]})

        return jsonify({'reply': reply})

    except Exception as e:
        err_str = str(e)
        if 'RESOURCE_EXHAUSTED' in err_str or '429' in err_str:
            return jsonify({
                'error': 'API quota exceeded. Your Gemini API key may not have the free tier enabled. '
                         'Go to aistudio.google.com/apikey and create a new key in a new project.'
            }), 429
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
