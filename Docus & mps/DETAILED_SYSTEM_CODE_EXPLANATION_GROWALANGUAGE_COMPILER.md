# Detailed System Code Explanation of GrowALanguage Compiler

Prepared for compiler defense. This document is based on the current source code in `C:\Users\clarence\Downloads\AUTOMATA-COMPILER-main (1)\AUTOMATA-COMPILER-main\my GAL code`.

Generated: 2026-06-01 14:31

## 1. System Overview

The GrowALanguage compiler is a web-based compiler pipeline. The user writes GrowALanguage code in the editor, the frontend sends the source code to the Flask backend, and the backend processes it through lexical analysis, syntax analysis, semantic analysis, and runtime execution.

| Stage | Main Files | Main Classes / Functions | Main Responsibility |
|---|---|---|---|
| Code editor and frontend input | `UI/index.html`, `UI/main.js` | `runCode()`, `runProgram()`, `runViaREST()`, `runViaSocket()` | Reads the text from the Monaco editor and sends it to the backend API. |
| Server routing | `Backend/server.py` | `lexer_endpoint()`, `parser_endpoint()`, `semantic_endpoint()`, `run_endpoint()`, `handle_run_code()` | Receives source code and controls which compiler stages run. |
| Scanner / lexer | `Backend/lexer/scanner.py` | `Lexer`, `Lexer.make_tokens()`, `Lexer.advance()`, `lex()` | Reads source code character by character and produces tokens or lexical errors. |
| Tokens | `Backend/shared/tokens.py` | `Token`, token constants, `get_token_description()` | Defines token types and token object structure. |
| Delimiters | `Backend/lexer/delimiters.py` | `idf_delim`, `whlnum_delim`, `decim_delim`, `delim24`, `delim25`, etc. | Defines valid next characters after lexemes. |
| Parser / CFG | `Backend/parser/parser.py`, `Backend/cfg/grammar.py` | `LL1Parser`, `parse()`, `parse_and_build()`, `cfg`, `predict_sets` | Checks token order using LL(1) grammar, FIRST, FOLLOW, and PREDICT sets. |
| AST builder | `Backend/parser/builder.py` | `build_ast()`, `Parser` class methods | Converts tokens into AST nodes and performs many static checks. |
| Semantic analyzer | `Backend/semantic/analyzer.py`, `Backend/semantic/symbol_table.py` | `validate_ast()`, `ASTValidator`, `SymbolTable` | Checks meaning: declarations, scope, types, break/continue context, and related rules. |
| Runtime / interpreter | `Backend/interpreter/interpreter.py` | `Interpreter`, `interpret()`, `eval_*()` methods | Executes the AST, stores variables, runs loops/functions, and produces output. |
| Error handling | `Backend/lexer/errors.py`, `Backend/semantic/errors.py`, `Backend/interpreter/errors.py`, `Backend/parser/parser.py` | `LexicalError`, `SemanticError`, `InterpreterError`, syntax error dictionaries | Builds error messages returned to the UI. |

High-level flow:

```text
Editor source code
  -> Frontend JavaScript reads editor.getValue()
  -> Flask server receives source_code
  -> Lexer scans characters and returns tokens
  -> Parser checks tokens using CFG and PREDICT table
  -> AST builder builds syntax tree
  -> Semantic analyzer checks meaning and rules
  -> Interpreter executes AST
  -> Server returns output/errors to frontend
  -> UI displays output/errors
```

## 2. Input Flow from Editor

The system receives the whole source code string from the editor, but the lexer processes that string one character at a time. The frontend first stores the editor content in a JavaScript variable, sends it as JSON, and the Flask route stores it in a Python variable named `source_code`.

### 2.1 Editor Reads the Source Code

Source: `UI/main.js:1005-1035`

Code:
```javascript
          window.runProgram = async function (options = {}) {
            const silent = options.silent || false;
            const sourceCode = editor.getValue();

            // Clear previous error highlights
            if (window._clearErrorHighlights) window._clearErrorHighlights();
            // Remove stale socket listeners
            socket.removeAllListeners('execution_complete');

            // Populate the token table in the background (silent — no terminal writes)
            await runLexer({ silent: true });

            // Reset status chips
            const sl  = document.getElementById('status-lex');
            const ss  = document.getElementById('status-syn');
            const ssem = document.getElementById('status-sem');
            const sexe = document.getElementById('status-exe');
            if (sl)   { sl.classList.remove('ok','err');  sl.textContent = 'Lexical: —'; }
            if (ss)   { ss.classList.remove('ok','err');  ss.textContent = 'Syntax: —'; }
            if (ssem) { ssem.classList.remove('ok','err'); ssem.textContent = 'Semantic: —'; }
            if (sexe) { sexe.classList.remove('ok','err'); sexe.textContent = 'Execution: —'; }

            // Check if program uses water() (needs interactive input via Socket.IO)
            const needsInput = /\bwater\s*\(/.test(sourceCode);

            if (needsInput) {
              runViaSocket(sourceCode, silent);
            } else {
              await runViaREST(sourceCode, silent);
            }
          };
```

Explanation:
- `editor.getValue()` reads all text currently written in the editor.
- The result is stored in the JavaScript variable `sourceCode`.
- The frontend first runs a silent lexer check.
- If the code contains `water(...)`, the frontend uses Socket.IO because input requires interactive communication.
- If the code has no `water(...)`, the frontend uses a normal REST request.

### 2.2 REST Run Request

Source: `UI/main.js:910-916`

Code:
```javascript
          async function runViaREST(sourceCode, silent) {
            try {
              const resp = await fetch(`${API_BASE}/api/run`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ source_code: sourceCode })
              });
```

Explanation:
- `runViaREST(sourceCode)` sends the complete source string to `POST /api/run`.
- The JSON body uses the key `source_code`.
- The backend route that receives this is `run_endpoint()` in `Backend/server.py`.

### 2.3 Backend Receives the Source Code

Source: `Backend/server.py:323-384`

Code:
```python
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
```

Explanation:
- `run_endpoint()` receives JSON from the frontend using `request.get_json()`.
- `source_code = data['source_code']` stores the full program text.
- The server calls `lex(source_code)` first.
- If lexical errors exist, the route immediately returns a lexical error response.
- If lexing succeeds, the server calls `parser.parse_and_build(tokens)`.
- If parsing and AST building succeed, the server calls `validate_ast(ast)`.
- If semantic analysis succeeds, the server creates `Interpreter(socketio=collector)` and executes the AST.

## 3. Scanner / Lexer Detailed Explanation

The lexer is the first compiler stage. Its job is not to understand the whole program yet. Its job is to convert raw characters into meaningful tokens such as `seed`, `id`, `=`, `intlit`, `;`, `plant`, and `EOF`.

### 3.1 Lexer Object Initialization and `current_char`

Source: `Backend/lexer/scanner.py:18-27`

Code:
```python
class Lexer:
    def __init__(self, source_code): 
        self.source_code = source_code.replace('\r', '')
        self.pos = Position(-1, 1, -1)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.source_code[self.pos.index] if self.pos.index<len(self.source_code) else None
```

Explanation:
- `self.source_code` holds the complete source code string.
- `self.pos` is a `Position` object that tracks index, line number, and column.
- `self.current_char` stores the character currently being scanned.
- `self.advance()` moves the lexer to the first character.

Example:

```gal
seed num = 10;
```

At the start:

| Variable | Meaning | Example Value |
|---|---|---|
| `source_code` | Full input text | `seed num = 10;` |
| `pos.index` | Current character index | `0` after first advance |
| `pos.ln` | Current line number | `1` |
| `pos.col` | Current column number | `0` |
| `current_char` | Character being checked | `s` |

### 3.2 How `advance()` and Position Tracking Work

Source: `Backend/lexer/positions.py:3-21`

Code:
```python
class Position:

    def __init__(self, index, ln, col=0):
        self.index = index
        self.ln = ln
        self.col = col

    def advance(self, current_char):
        self.index += 1
        self.col += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.index, self.ln, self.col)
```

Explanation:
- `Position.advance()` increments the character index and column.
- If the previous character was newline, it increments the line number and resets column to 0.
- This is why lexical, syntax, semantic, and runtime errors can show line and column information.

### 3.3 Main Tokenizing Loop

Source: `Backend/lexer/scanner.py:29-35`

Code:
```python
    def make_tokens(self):
        tokens = []
        line = 1
        errors = []
        pos = self.pos.copy()

        while self.current_char != None:
```

Explanation:
- `make_tokens()` creates two lists: `tokens` and `errors`.
- `tokens` stores successful token objects.
- `errors` stores lexical errors.
- The loop continues while `self.current_char` is not `None`.
- `None` means the lexer reached the end of the source code.

### 3.4 Reserved Words Are Checked First

Source: `Backend/lexer/scanner.py:341-379`

Code:
```python
                elif self.current_char == "r":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char == "e":
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "c":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "l":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char == "a":
                                    ident_str += self.current_char
                                    self.advance()
                                    if self.current_char == "i":
                                        ident_str += self.current_char
                                        self.advance()
                                        if self.current_char == "m":
                                            ident_str += self.current_char
                                            self.advance()
                                            if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim8:
                                                tokens.append(Token(TT_RW_RECLAIM, ident_str, line, pos.col))
                                                continue
                                            elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim8 and self.current_char not in ALPHANUM:
                                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                                                self.advance()
                                                continue
                    elif self.current_char == "o":
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char == "o":
                            ident_str += self.current_char
                            self.advance()
                            if self.current_char == "t":
                                ident_str += self.current_char
                                self.advance()
                                if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim7:
                                    tokens.append(Token(TT_RW_ROOT, ident_str, line, pos.col))
```

Explanation:
- When the lexer sees `r`, it tries to match `root`.
- If the next characters are exactly `o`, `o`, `t`, and the delimiter after `root` is valid, it appends `Token(TT_RW_ROOT, ident_str, line, pos.col)`.
- If the word is not exactly a reserved word, the lexer falls back to identifier scanning.

Example:

```gal
root() {
```

Token output:

| Lexeme | Token Type |
|---|---|
| `root` | `root` |
| `(` | `(` |
| `)` | `)` |
| `{` | `{` |

### 3.5 How a Wrong Reserved Word Becomes an Identifier

Source: `Backend/lexer/scanner.py:611-638`

Code:
```python
                maxIdentifierLength = 15
                while self.current_char is not None and self.current_char in ALPHANUM:
                    ident_str += self.current_char
                    self.advance()

                if len(ident_str) > maxIdentifierLength:
                    i = 0
                    remaining = None
                    while i < len(ident_str):
                        if i + 15 <= len(ident_str):
                            errors.append(LexicalError(pos, f"Identifier exceeds maximum length of {maxIdentifierLength} characters"))
                            i += 15
                        else:
                            remaining = ident_str[i:]
                            if self.current_char is None or self.current_char in idf_delim:
                                tokens.append(Token(TT_IDENTIFIER, remaining, line, pos.col))
                            elif self.current_char is not None and self.current_char not in idf_delim:
                                errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after identifier"))
                            break
                    if remaining is None:
                        last_chunk = ident_str[i - 15:] if i >= 15 else ident_str
                        if self.current_char is None or self.current_char in idf_delim:
                            tokens.append(Token(TT_IDENTIFIER, last_chunk, line, pos.col))
                    continue
                else:
                    if self.current_char is None or self.current_char in idf_delim:
                        tokens.append(Token(TT_IDENTIFIER, ident_str, line, pos.col))
                        continue
```

Explanation:
- If the user writes `roof()` instead of `root()`, the nested `root` check fails when the lexer expects `t` but sees `f`.
- There is no separate `false` branch needed. After the reserved-word checks fail, Python continues to the fallback identifier block.
- `ident_str` already contains the characters collected so far, for example `roo`.
- The fallback `while` loop collects the remaining alphanumeric characters.
- In `roof`, `self.current_char` is `f` when fallback begins, so the loop appends `f`.
- The final `ident_str` becomes `roof`.
- If the next character after `roof` is valid according to `idf_delim`, the lexer appends an identifier token.

Step-by-step:

| Step | `current_char` | `ident_str` | What Happens |
|---:|---|---|---|
| 1 | `r` | `r` | Lexer enters alphabet branch. |
| 2 | `o` | `ro` | Still trying to match `root`. |
| 3 | `o` | `roo` | Still trying to match `root`. |
| 4 | `f` | `roo` | Expected `t`, but got `f`; reserved-word path fails. |
| 5 | `f` | `roof` | Fallback identifier loop collects `f`. |
| 6 | `(` | `roof` | `(` is valid delimiter, so token becomes `id`. |

### 3.6 Integer and Double Literals

Source: `Backend/lexer/scanner.py:1171-1236`

Code:
```python
                ident_str = ""
                pos = self.pos.copy()
                integer_digit_count = 0
                fractional_digit_count = 0
                has_e = False

                
                while self.current_char is not None and self.current_char in ZERODIGIT:
                    integer_digit_count += 1
                    ident_str += self.current_char
                    self.advance()

                if self.current_char == ".":
                    if integer_digit_count > 15:
                        integer_part = ident_str
                        i = 0
                        while i < len(integer_part):
                            if i + 15 < len(integer_part):
                                errors.append(LexicalError(pos, f"Integer part of decimal exceeds maximum of 15 digits"))
                                i += 15
                            else:
                                ident_str = integer_part[i:]
                                break
                        else:
                            ident_str = "0"
                    dot_count = 1
                    ident_str += self.current_char
                    self.advance()
                    
                    if self.current_char is None or self.current_char not in ZERODIGIT:
                        errors.append(LexicalError(pos, f"Invalid number '{ident_str}': decimal point must be followed by digits"))
                        continue
                    
                    fractional_part = ""
                    while self.current_char is not None and self.current_char in ZERODIGIT:
                        fractional_digit_count += 1
                        fractional_part += self.current_char
                        self.advance()
                    
                    if fractional_digit_count > 8:
                        i = 0
                        final_fractional = ""
                        while i < len(fractional_part):
                            if i + 8 < len(fractional_part):
                                errors.append(LexicalError(pos, f"Fractional part exceeds maximum of 8 digits"))
                                i += 8
                            else:
                                final_fractional = fractional_part[i:]
                                break
                        ident_str += final_fractional
                    else:
                        ident_str += fractional_part

                if dot_count == 0 and integer_digit_count > 8:
                    i = 0
                    remaining = None
                    while i < len(ident_str):
                        if i + 8 < len(ident_str):
                            errors.append(LexicalError(pos, f"Integer exceeds maximum of 8 digits"))
                            i += 8
                        else:
                            remaining = ident_str[i:]
                            remaining = remaining.lstrip("0") or "0"
                            tokens.append(Token(TT_INTEGERLIT, remaining, line, pos.col))
                            break
                    if remaining is None:
```

Explanation:
- When `current_char` is a digit, the lexer collects digits into `digits`.
- If it sees `.`, it switches to decimal scanning and counts decimal points.
- If the number has no decimal point, it creates an `intlit` token.
- If it has one decimal point with digits after it, it creates a `dblit` token.
- If it sees invalid characters after a number, it creates a lexical error.

Example:

```gal
seed x = 10;
tree y = 2.5;
```

Token output:

| Lexeme | Token Type |
|---|---|
| `10` | `intlit` |
| `2.5` | `dblit` |

### 3.7 String Literals

Source: `Backend/lexer/scanner.py:1334-1388`

Code:
```python
            elif self.current_char == '"':
                string = ''
                pos = self.pos.copy()
                escape_character = False
                string += self.current_char
                self.advance()

                escape_characters = {
                    'n': '\n',
                    't': '\t',
                    '{': '\\{',
                    '}': '\\}',
                    '"': '"',
                    '\\': '\\',
                }

                has_string_error = False
                while self.current_char is not None and (self.current_char != '"' or escape_character):
                    if escape_character:
                        if self.current_char in escape_characters:
                            string += escape_characters[self.current_char]
                        else:
                            errors.append(LexicalError(pos, f"Invalid escape sequence '\\{self.current_char}' in string literal"))
                            has_string_error = True
                        escape_character = False
                    else:
                        if self.current_char == '\\':
                            escape_character = True
                        elif self.current_char == '\n':
                            break
                        else:
                            string += self.current_char
                    self.advance()

                if has_string_error:
                    while self.current_char is not None and self.current_char != '"':
                        self.advance()
                    if self.current_char == '"':
                        self.advance()
                    continue

                if self.current_char == '"':
                    string += self.current_char
                    self.advance()
                else:
                    errors.append(LexicalError(pos, f"Missing closing '\"' for string literal"))
                    continue

                if self.current_char is not None and self.current_char not in delim23 and self.current_char not in space_delim:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after string literal '{string}'"))
                    self.advance()
                    continue
            
                tokens.append(Token(TT_STRINGLIT, string, line, pos.col))
                continue
```

Explanation:
- A string starts with double quote `"`.
- The lexer keeps reading characters until it finds the closing double quote.
- Escape sequences such as `\n` are handled by checking `escaped`.
- If the closing quote is missing, the lexer creates a lexical error.
- If the character after the string is not a valid delimiter, it also creates a lexical error.
- The CFG does not contain separate quotation mark terminals because the lexer turns the whole quoted text into one `stringlit` token.

### 3.8 Character Literals

Source: `Backend/lexer/scanner.py:1390-1456`

Code:
```python
            elif self.current_char == "'":
                string = ''
                char = ''
                pos = self.pos.copy()
                string += self.current_char
                self.advance()
                has_error = False

                while self.current_char is not None and self.current_char in ' \t':
                    string += self.current_char
                    self.advance()

                while self.current_char is not None and self.current_char != "'":
                    if self.current_char == '\n':
                        break
                    elif self.current_char == '\\':
                        string += self.current_char
                        self.advance()
                        if self.current_char is None:
                            break
                        
                        if self.current_char in "'\\nt": 
                            char += f"\\{self.current_char}"
                            string += self.current_char
                        else:
                            errors.append(LexicalError(pos, f"Invalid escape sequence '\\{self.current_char}' in character literal"))
                            has_error = True
                            while self.current_char is not None and self.current_char != "'":
                                self.advance()
                            if self.current_char == "'":
                                self.advance()
                            break
                    else:
                        string += self.current_char
                        char += self.current_char
                    self.advance()
                
                while len(char) > 0 and char[-1] in ' \t':
                    char = char[:-1]

                if has_error:
                    continue

                if self.current_char == "'":
                    string += self.current_char
                    self.advance()
                else:
                    errors.append(LexicalError(pos, f"Missing closing quote for character literal"))
                    continue

                if self.current_char is not None and self.current_char not in delim23 and self.current_char not in space_delim:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{string}'"))
                    self.advance()
                    continue

                inner = char.strip()
                if len(inner) == 0:
                    string = "' '"
                    inner = ' '
                elif inner.startswith('\\') and len(inner) == 2:
                    pass
                elif len(inner) > 1:
                    errors.append(LexicalError(pos, f"Character literal must contain exactly one character, found '{inner}'"))
                    continue

                tokens.append(Token(TT_CHARLIT, string, line, pos.col))
                continue
```

Explanation:
- A character literal starts with single quote `'`.
- It must contain exactly one character, or one supported escaped character.
- If it has more than one character, the lexer creates a lexical error.
- If the closing quote is missing, the lexer creates a lexical error.

### 3.9 Comments

Source: `Backend/lexer/scanner.py:1071-1106`

Code:
```python
            elif self.current_char == "/":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                
                if self.current_char == "/":
                    ident_str += self.current_char
                    self.advance()
                    while self.current_char is not None and self.current_char != "\n":
                        ident_str += self.current_char
                        self.advance()
                    tokens.append(Token(TT_COMMENT, ident_str, line, pos.col))
                    continue

                elif self.current_char == "*":
                    ident_str += self.current_char
                    self.advance()
                    found_close = False
                    while self.current_char is not None:
                        if self.current_char == "*" and self.pos.index + 1 < len(self.source_code) and self.source_code[self.pos.index + 1] == "/":
                            ident_str += "*/"
                            self.advance()
                            self.advance()
                            found_close = True
                            break
                        else:
                            ident_str += self.current_char
                            if self.current_char == "\n":
                                line += 1
                            self.advance()

                    if not found_close:
                        errors.append(LexicalError(pos, f"Missing closing '*/' after '{ident_str}'"))
                        continue
                    tokens.append(Token(TT_MCOMMENT, ident_str, line, pos.col))
                    continue
```

Explanation:
- `//` starts a single-line comment.
- `/* ... */` starts a multi-line comment.
- The lexer tokenizes comments as `comment` or `mcommentlit`.
- The LL(1) parser is configured to skip comment tokens during syntax checking.

Implementation note: syntax parsing skips comment tokens. The AST-building phase filters newline tokens, so comments should be kept away from places where the builder is strict unless the builder also handles them.

### 3.10 Operators and Reserved Symbols

Source: `Backend/lexer/scanner.py:811-847`

Code:
```python
            elif self.current_char == "*":
                ident_str = self.current_char
                pos = self.pos.copy()
                self.advance()
                if self.current_char == "*":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char == "=":
                        ident_str += self.current_char
                        self.advance()
                        if self.current_char is not None and self.current_char not in delim24:
                            errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                            self.advance()
                            continue
                        tokens.append(Token(TT_EXPEQ, ident_str, line, pos.col))
                        continue
                    if self.current_char is not None and self.current_char not in delim24:
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        self.advance()
                        continue
                    tokens.append(Token(TT_EXP, ident_str, line, pos.col))
                    continue
                if self.current_char == "=":
                    ident_str += self.current_char
                    self.advance()
                    if self.current_char is not None and self.current_char not in delim24:
                        errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                        self.advance()
                        continue
                    tokens.append(Token(TT_MULTIEQ, ident_str, line, pos.col))
                    continue
                if self.current_char is not None and self.current_char not in delim24:
                    errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
                    self.advance()
                    continue
                tokens.append(Token(TT_MUL, ident_str, line, pos.col))
                continue
```

Explanation:
- This block recognizes `*`, `*=`, `**`, and `**=`.
- The scanner looks ahead by calling `advance()` after seeing `*`.
- If the next character is another `*`, it may become exponent `**` or exponent assignment `**=`.
- If the next character is `=`, it becomes multiplication assignment `*=`.

More operator groups:

| Operator Group | File Logic |
|---|---|
| plus, increment, plus-equals | `Backend/lexer/scanner.py:921-963` |
| minus, decrement, minus-equals | `Backend/lexer/scanner.py:645-672` |
| equals and equality | `Backend/lexer/scanner.py:987-1013` |
| logical not and not-equal | `Backend/lexer/scanner.py:729-750` |
| modulo and modulo-equals | `Backend/lexer/scanner.py:752-770` |
| slash, slash-equals, comments | `Backend/lexer/scanner.py:1071-1106` |
| grouping and braces | `Backend/lexer/scanner.py:789-917` |
| backtick concatenation | `Backend/lexer/scanner.py:1458-1467` |

### 3.11 Invalid Delimiters

Source: `Backend/lexer/scanner.py:631-637`

Code:
```python
                        last_chunk = ident_str[i - 15:] if i >= 15 else ident_str
                        if self.current_char is None or self.current_char in idf_delim:
                            tokens.append(Token(TT_IDENTIFIER, last_chunk, line, pos.col))
                    continue
                else:
                    if self.current_char is None or self.current_char in idf_delim:
                        tokens.append(Token(TT_IDENTIFIER, ident_str, line, pos.col))
```

Explanation:
- If `self.current_char` is `None` or is inside `idf_delim`, the identifier is valid.
- If the next character is not inside `idf_delim`, a lexical error is added.

Example:

```gal
root(){ seed x@; reclaim; }
```

Error:

```text
LEXICAL error line 1 col 13 Invalid delimiter '@' after 'x'
```

### 3.12 End of File and Lexer Return Value

Source: `Backend/lexer/scanner.py:1502-1529`

Code:
```python
        if self.current_char is None:
            tokens.append(Token(TT_EOF, "", line, pos.col))
        
        return tokens, errors


def run(source_code):
    lexer = Lexer(source_code)
    tokens, error = lexer.make_tokens()
    return tokens, error

def lex(source_code):
    lexer = Lexer(source_code)
    tokens, errors = lexer.make_tokens()

    # Report lexical errors one at a time — only surface the first.
    # The user fixes it, re-runs, and sees the next one (if any).
    str_errors = []
    if errors:
        e = errors[0]
        try:
            if hasattr(e, 'as_string') and callable(getattr(e, 'as_string')):
                str_errors.append(e.as_string())
            else:
                str_errors.append(str(e))
        except Exception:
            str_errors.append(str(e))
    return tokens, str_errors
```

Explanation:
- At the end of scanning, the lexer appends an EOF token.
- `lex(source_code)` is the public function used by the server.
- It creates a `Lexer`, calls `make_tokens()`, converts lexical errors into strings, and returns `(tokens, errors)`.

## 4. Tokens Explanation

Tokens are defined in `Backend/shared/tokens.py`. A token is a small object that stores what lexeme was found, what kind of token it is, and where it appeared.

### 4.1 Token Class

Source: `Backend/shared/tokens.py:86-92`

Code:
```python
class Token:
    """Represents a token with type, value, line number, and column number"""

    def __init__(self, type_, value=None, line=1, col=0):
        self.type = type_    # Token type (e.g., TT_IDENTIFIER, TT_INTEGERLIT)
        self.value = value   # Token text/value (e.g., "myVar", "42")
        self.line = line     # Line number where token appears
```

Explanation:
- `type` stores the token category, such as `seed`, `id`, `intlit`, or `;`.
- `value` stores the original lexeme text.
- `line` stores the line number.
- `col` stores the column number.

### 4.2 Major Token Groups

Source: `Backend/shared/tokens.py:3-80`

Code:
```python
# --- Reserved Words (Keywords) ---
TT_RW_WATER       = 'water'     # Input function - reads user input
TT_RW_PLANT       = 'plant'     # Output function - prints to console
TT_RW_SEED        = 'seed'      # Data Type - integer (int)
TT_RW_LEAF        = 'leaf'      # Data Type - character (char)
TT_RW_BRANCH      = 'branch'    # Data Type - boolean (true/false)
TT_RW_TREE        = 'tree'      # Data Type - double/float
TT_RW_SPRING      = 'spring'    # Conditional statement - if
TT_RW_WITHER      = 'wither'    # Conditional statement - else
TT_RW_BUD         = 'bud'       # Conditional statement - else-if
TT_RW_HARVEST     = 'harvest'   # Switch statement
TT_RW_GROW        = 'grow'      # Loop - while
TT_RW_CULTIVATE   = 'cultivate' # Loop - for
TT_RW_TEND        = 'tend'      # Loop - do-while
TT_RW_EMPTY       = 'empty'     # Void return type
TT_RW_PRUNE       = 'prune'     # Break statement - exit loop
TT_RW_SKIP        = 'skip'      # Continue statement - skip to next iteration
TT_RW_RECLAIM     = 'reclaim'   # Return statement - return from function
TT_RW_ROOT        = 'root'      # Main function entry point
TT_RW_POLLINATE   = 'pollinate' # Function declaration
TT_RW_VARIETY     = 'variety'   # Case label in switch statement
TT_RW_FERTILE     = 'fertile'   # Constant declaration
TT_RW_SOIL        = 'soil'      # Default case in switch statement
TT_RW_BUNDLE      = 'bundle'    # Struct definition
TT_RW_VINE        = 'vine'      # String data type

# --- Operators & Symbols ---
TT_IDENTIFIER = 'id'        # Variable/function names (e.g., myVar, calcTotal)
TT_PLUS = '+'               # Addition operator
TT_MINUS = '-'              # Subtraction operator
TT_MUL = '*'                # Multiplication operator
TT_DIV = '/'                # Division operator
TT_MOD = '%'                # Modulo operator (remainder)
TT_EXP = '**'               # Exponentiation operator (power)
TT_EQ = '='                 # Assignment operator
TT_EQTO = '=='              # Equality comparison operator
TT_PLUSEQ = '+='            # Add and assign operator
TT_MINUSEQ = '-='           # Subtract and assign operator
TT_MULTIEQ = '*='           # Multiply and assign operator
TT_DIVEQ = '/='             # Divide and assign operator
TT_MODEQ = '%='             # Modulo and assign operator
TT_EXPEQ = '**='            # Exponent and assign operator (x **= 2 → x = x ** 2)
TT_CONCAT = '`'             # String concatenation operator
TT_LPAREN = '('             # Left parenthesis
TT_RPAREN = ')'             # Right parenthesis
TT_SEMICOLON = ';'          # Statement terminator
TT_COMMA = ','              # Separator (function args, array elements)
TT_COLON = ':'              # Colon (used in switch cases)
TT_BLOCK_START = '{'        # Block start (scope begin)
TT_BLOCK_END = '}'          # Block end (scope close)
TT_LT = '<'                 # Less than comparison
TT_GT = '>'                 # Greater than comparison
TT_LTEQ = '<='              # Less than or equal comparison
TT_GTEQ = '>='              # Greater than or equal comparison
TT_NOTEQ = '!='             # Not equal comparison
TT_EOF = 'EOF'                  # End of file marker
TT_AND = '&&'                   # Logical AND operator
TT_OR = '||'                    # Logical OR operator
TT_SINGLE_AND = '&'             # Invalid single ampersand
TT_SINGLE_OR = '|'              # Invalid single pipe
TT_NOT = '!'                    # Logical NOT operator
TT_INCREMENT = '++'             # Increment operator (e.g., x++)
TT_DECREMENT = '--'             # Decrement operator (e.g., x--)
TT_LSQBR = '['                  # Left square bracket (array indexing)
TT_RSQBR = ']'                  # Right square bracket
TT_NEGATIVE = '~'               # Unary negation operator
TT_MEMBER = 'member'            # Member token for struct access
TT_INTEGERLIT = 'intlit'        # Integer literal token (e.g., 42, 100)
TT_DOUBLELIT = 'dblit'         # Double/float literal token (e.g., 3.14, 2.5)
TT_STRINGLIT = 'stringlit'      # String literal token (e.g., "hello")
TT_CHARLIT = 'chrlit'           # Character literal token (e.g., 'a')
TT_BOOLLIT_TRUE = 'sunshine'    # Boolean true literal
TT_BOOLLIT_FALSE = 'frost'      # Boolean false literal
TT_STRCTACCESS = '.'            # Struct member access operator
TT_NL = '\n'                    # Newline token
TT_DOT = '.'                    # Dot operator (struct access)
TT_COMMENT = 'comment'          # Single-line comment (//...)
TT_MCOMMENT = 'mcommentlit'     # Multi-line comment (/*...*/)
```

| Token Group | Examples | Meaning |
|---|---|---|
| Reserved words | `seed`, `tree`, `root`, `plant`, `water`, `reclaim` | Language keywords. |
| Identifiers | `x`, `sum`, `studentName` | User-defined names. |
| Literals | `intlit`, `dblit`, `stringlit`, `chrlit`, `sunshine`, `frost` | Constant values. |
| Operators | `=`, `+=`, `+`, `**`, `==`, `&&`, `!` | Computation and logic symbols. |
| Punctuation | `;`, `,`, `(`, `)`, `[`, `]`, `{`, `}` | Structure and grouping symbols. |
| EOF | `EOF` | Marks the end of the token list. |

Example source:

```gal
seed x = 10;
```

Token sequence:

| Lexeme | Token Type | Value |
|---|---|---|
| `seed` | `seed` | `seed` |
| `x` | `id` | `x` |
| `=` | `=` | `=` |
| `10` | `intlit` | `10` |
| `;` | `;` | `;` |
| end | `EOF` | empty |

## 5. Delimiters Explanation

A delimiter set is not the same as a token. A reserved symbol token is an actual token that goes to the parser. A delimiter set is only used by the lexer to check if the character after a lexeme is valid.

### 5.1 Delimiter Definitions

Source: `Backend/lexer/delimiters.py:1-60`

Code:
```python
ZERO = '0'
DIGIT = '123456789'
ZERODIGIT = ZERO + DIGIT

LOW_ALPHA = 'abcdefghijklmnopqrstuvwxyz'
UPPER_ALPHA = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
ALPHA = LOW_ALPHA + UPPER_ALPHA
ALPHANUM = ALPHA + ZERODIGIT + '_'

WHITESPACE = ' \t\n'
EOF = None

statement_end_delim = set(ALPHA + WHITESPACE + '}') | {EOF}
open_paren_delim = set(ALPHA + ZERODIGIT + WHITESPACE + '"' + "'" + '~' + '!' + '(' + ')')
close_paren_delim = set(WHITESPACE) | {';', '{', ')', ',', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|', ']'}
open_bracket_delim = set(ALPHA + ZERODIGIT + WHITESPACE + '~' + '!' + '(' + '"' + "'")
close_bracket_delim = set(WHITESPACE) | {';', ',', ')', ']', '[', '.', '=', '+', '-', '*', '/', '%', '>', '<', '!', '&', '|'}
block_start_delim = set(ALPHA + ZERODIGIT + WHITESPACE + '}/{"\'~!(')
block_end_delim = set(ALPHA + ZERODIGIT + WHITESPACE + '};,)]')
case_colon_delim = set(ALPHA + WHITESPACE + '}/')
after_comma_delim = set(ALPHA + ZERODIGIT + WHITESPACE + '"' + "'" + '~' + '!' + '(' + '{')
space_delim = {' ', '\t', '\n'}
period_delim = {'.'}
underscore_delim = {'_'}
open_brack_delim = {'['}
close_brack_delim = {']'}
comma_delim = {','}
delim1 = {'}'}
delim2 = {':'}
delim3 = {'{'}
delim4 = {':', '('}
delim5 = {'('}
delim6 = {';', ',', '=', '>', '<', '!', '}', ')', '('}
delim7 = {'('}
delim8 = {';'}
delim9 = set(ALPHA + '(' + ',' + ';' + ')')
delim10 = {';', ')'}
delim11 = set([LOW_ALPHA, ZERODIGIT, ']', '~'])
delim12 = set(ALPHA + ZERODIGIT + ']' + '~')
delim13 = {';', ')', '['}
delim14 = set(ALPHA + ZERODIGIT + '"' + "'" + '{')
delim15 = {'\n', ';', '}', ','}
delim16 = set(ALPHANUM + ')' + '"' + '!' + '(' + '[' + '\'')
delim17 = {'}', ';', ',', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|'}
delim18 = {';', '{', ')', '&', '|', '+', '-', '*', '/', '%'}
delim19 = {';', ',', '}', ')', '=', '>', '<', '!'}
delim20 = set(ALPHA + ZERODIGIT + '"' + "'" + '{')
delim21 = set(DIGIT)
delim22 = {',', ';', '(', ')', '{', '[', ']'}
delim23 = {';', ',', '}', ']', ')', ':', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|'}
delim24 = set(ZERODIGIT + ALPHA + '~(' + ' \t\n')
delim25 = set(ALPHANUM + ';) \t\n')
delim26 = set(ZERODIGIT + ALPHA + '~(' + '"\'' + ' \t\n')
idf_delim = {' ', ',', ';', '(', ')', '{', '}', '[', ']', ':', '+', '-', '*', '/', '%',
             '>', '<', '=', '\t', '\n', '.', '"', "'"}
whlnum_delim = {';', ' ', ',', '}', ']', ')', ':', '+', '-', '*', '/', '%', '=', '>', '<',
                '!', '&', '|', '\t', '\n'}
decim_delim = {'}', ';', ',', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|', ' ',
               '\t', '\n', ')', ']'}
comment_delim = set(ALPHANUM + ';+-*/%}{()' + '\n')
```

| Delimiter Set | Contains / Purpose | Example Valid | Example Invalid |
|---|---|---|---|
| `idf_delim` | Valid characters after identifiers. Includes spaces, semicolon, operators, brackets, quotes, and similar boundaries. | `seed x;` | `seed x@;` |
| `whlnum_delim` | Valid characters after integer literals. | `seed x = 10;` | `seed x = 10a;` |
| `decim_delim` | Valid characters after double literals. | `tree y = 2.5;` | `tree y = 2.5a;` |
| `comment_delim` | Characters allowed while scanning comments. | `// hello` | depends on comment form |
| `delim24` | Used for binary/assignment operators where another operand may follow. | `x + y` | operator followed by invalid punctuation |
| `delim25` | Used after increment/decrement style operators and some arithmetic operators. | `x++;` | `x++@` |
| `delim26` | Used after logical not `!`, allowing identifiers, literals, unary signs, quotes, and whitespace. | `!ready` | `!@` |

Difference:
- Reserved symbol token: a real token sent to the parser, such as `++`.
- Delimiter set: a validation set used only by the lexer.
- Valid next character: the character that is allowed to appear immediately after a lexeme.

## 6. Parser Explanation

The parser checks if the token sequence follows the CFG. Your parser is an LL(1) stack-based parser.

### 6.1 Parser Setup in the Server

Source: `Backend/server.py:50-57`

Code:
```python
parser = LL1Parser(
    cfg=cfg,
    predict_sets=predict_sets,
    first_sets=first_sets,
    start_symbol="<program>",
    end_marker="EOF",
    skip_token_types={'\n', 'comment', 'mcommentlit'}
)
```

### 6.2 Parser Class Initialization

Source: `Backend/parser/parser.py:37-64`

Code:
```python
class LL1Parser:
    def __init__(
        self,
        cfg: Dict[str, List[List[str]]],
        predict_sets: Dict[Tuple[str, Tuple[str, ...]], Set[str]],
        first_sets: Dict[str, Set[str]],
        *,
        start_symbol: str = "<program>",
        end_marker: str = "EOF",
        epsilon_symbols: Iterable[str] = ("λ", "ε"),
        skip_token_types: Optional[Set[str]] = None,
        token_type_alias: Optional[Dict[str, str]] = None,
    ):
        self.cfg = cfg
        self.predict_sets = predict_sets
        self.first_sets = first_sets

        self.epsilon_symbols: Set[str] = set(epsilon_symbols)
        self.start_symbol = start_symbol
        self.end_marker = end_marker

        self.skip_token_types: Set[str] = set(skip_token_types or {"\n"})
        self.token_type_alias = token_type_alias or {
            'idf': 'id',
            'dbllit': 'dblit',
        }
        
        self.parsing_table: Dict[str, Dict[str, List[str]]] = self.construct_parsing_table()
```

Explanation:
- `self.cfg` stores all grammar productions.
- `self.predict_sets` stores the terminals that choose each production.
- `self.start_symbol` is `<program>`.
- `self.end_marker` is `EOF`.
- `self.parsing_table` is built from the PREDICT sets.

### 6.3 Parsing Table Construction

Source: `Backend/parser/parser.py:66-82`

Code:
```python
    def construct_parsing_table(self) -> Dict[str, Dict[str, List[str]]]:
        table: Dict[str, Dict[str, List[str]]] = {}

        for non_terminal, productions in self.cfg.items():
            row: Dict[str, List[str]] = {}
            for production in productions:
                key = (non_terminal, tuple(production))
                terms = self.predict_sets.get(key, set())
                for terminal in terms:
                    if terminal in row and row[terminal] != production:
                        raise ValueError(
                            f"LL(1) conflict at {non_terminal} with lookahead {terminal}: "
                            f"{row[terminal]} vs {production}"
                        )
                    row[terminal] = production
            table[non_terminal] = row
        return table
```

### 6.4 Main Stack-Based Parsing Algorithm

Source: `Backend/parser/parser.py:614-715`

Code:
```python
    def parse(self, tokens: Sequence[Any]) -> Tuple[bool, List[str]]:
        toks = [_as_tok(t) for t in tokens]
        toks = [_TokView(self._normalize_token_type(t.type), t.value, t.line, t.col) for t in toks]
        toks = self._ensure_eof(toks)

        self._current_tokens = toks

        stack: List[str] = [self.end_marker, self.start_symbol]
        index = 0
        
        current_var_type: Optional[str] = None
        expecting_value_for_type: Optional[str] = None

        reclaim_seen_stack: List[bool] = []

        def current_token() -> _TokView:
            nonlocal index
            if index >= len(toks):
                last_line = toks[-1].line if toks else 1
                last_col = toks[-1].col if toks else 0
                return _TokView(self.end_marker, self.end_marker, last_line, last_col)
            return toks[index]

        while stack:
            top = stack[-1]
            tok = current_token()
            token_type = tok.type
            token_value = tok.value
            line = tok.line or 1

            if token_type in self.skip_token_types and top != token_type:
                index += 1
                continue

            if top in self.parsing_table:
                row = self.parsing_table[top]
                if token_type in row:
                    production = row[token_type]
                    
                    if top == '<statement>' and token_type != '}' and reclaim_seen_stack and reclaim_seen_stack[-1]:
                        return False, [f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}' after 'reclaim'. Expected: '}}'."]

                    if top == '<statement>' and token_type == '}':
                        is_epsilon = (len(production) == 0 or (len(production) == 1 and production[0] in self.epsilon_symbols))
                        if is_epsilon:
                            lookback = index - 1
                            while lookback >= 0 and toks[lookback].type in self.skip_token_types:
                                lookback -= 1
                            
                            if lookback >= 0 and toks[lookback].type == '{':
                                before_brace = lookback - 1
                                while before_brace >= 0 and toks[before_brace].type in self.skip_token_types:
                                    before_brace -= 1
                                
                                if before_brace >= 0 and toks[before_brace].type == ')':
                                    paren_depth = 1
                                    paren_pos = before_brace - 1
                                    while paren_pos >= 0 and paren_depth > 0:
                                        if toks[paren_pos].type == ')':
                                            paren_depth += 1
                                        elif toks[paren_pos].type == '(':
                                            paren_depth -= 1
                                        paren_pos -= 1
                                    
                                    if paren_pos >= 0:
                                        kw_pos = paren_pos
                                        while kw_pos >= 0 and toks[kw_pos].type in self.skip_token_types:
                                            kw_pos -= 1
                                        
                                        if kw_pos >= 0:
                                            kw = toks[kw_pos]
                                            conditional_keywords = {'spring', 'bud', 'wither', 'grow', 'cultivate', 'tend', 'harvest'}
                                            if kw.type in conditional_keywords:
                                                return False, [f"SYNTAX error line {line} col {tok.col} Empty block after '{kw.value}' statement - at least one statement required"]
                                
                                elif before_brace >= 0 and toks[before_brace].type in {'wither', 'tend'}:
                                    kw = toks[before_brace]
                                    return False, [f"SYNTAX error line {line} col {tok.col} Empty block after '{kw.value}' statement - at least one statement required"]
                    
                    stack.pop()

                    if not (
                        len(production) == 0
                        or (len(production) == 1 and production[0] in self.epsilon_symbols)
                    ):
                        stack.extend(reversed(production))
                    continue

                expected = set(row.keys())
                
                if token_type in {'variety', 'soil'} and token_type not in expected:
                    while index < len(toks) and toks[index].type != ';':
                        if toks[index].type == 'prune':
                            index += 1
                            break
                        index += 1
                    if index < len(toks) and toks[index].type == ';':
                        index += 1
                    continue

                error_msg = self._generate_helpful_error(top, token_type, token_value, line, tok.col, expected, index, toks)
                return False, [error_msg]
```

Explanation:
- The stack starts as `[EOF, <program>]`.
- The parser looks at the top of the stack and the current token.
- If the top is a nonterminal, it uses `self.parsing_table[top][lookahead]` to choose a production.
- It pops the nonterminal and pushes the chosen production in reverse order.
- If the top is a terminal and it matches the current token, the parser consumes the token.
- If no production matches or the terminal does not match, it returns a syntax error.

### 6.5 AST Build After Syntax Success

Source: `Backend/parser/parser.py:1183-1240`

Code:
```python
    def parse_and_build(self, tokens: Sequence[Any]):
        syntax_ok, syntax_errors = self.parse(tokens)
        if not syntax_ok:
            first_err = syntax_errors[0] if syntax_errors else ""
            stage = "semantic" if first_err.startswith("SEMANTIC error") else "syntax"
            return {
                "success": False,
                "errors": syntax_errors,
                "ast": None,
                "symbol_table": {},
                "error_stage": stage,
            }

        try:
            filtered = [t for t in tokens if getattr(t, 'type', '') != '\n']
            ast = _build_ast(filtered)

            st = {
                "variables": [
                    {
                        "name": name,
                        "type": info["type"],
                        "scope": "global",
                        "is_list": info.get("is_list", False),
                        "is_constant": info.get("is_fertile", False),
                    }
                    for name, info in _builder_st.variables.items()
                ],
                "functions": {
                    name: {
                        "return_type": info["return_type"],
                        "params": [
                            {
                                "type": p.children[0].value if p.children else "unknown",
                                "name": p.children[1].value if len(p.children) > 1 else "unknown",
                            }
                            for p in info["params"]
                        ] if info["params"] else [],
                    }
                    for name, info in _builder_st.functions.items()
                },
            }

            return {
                "success": True,
                "errors": [],
                "ast": ast,
                "symbol_table": st,
            }

        except _SemanticError as e:
            return {
                "success": False,
                "errors": [str(e)],
                "ast": None,
                "symbol_table": {},
                "error_stage": "semantic",
            }
```

Explanation:
- `parse_and_build(tokens)` first calls `self.parse(tokens)`.
- If syntax fails, it returns syntax errors.
- If syntax succeeds, it filters newline tokens and calls `_build_ast(filtered)` from `Backend/parser/builder.py`.
- The builder returns the AST and symbol table.

### 6.6 Sample Parser Flow

Sample code:

```gal
root() {
    seed x = 10;
    reclaim;
}
```

Important CFG path:

```text
<program>
  -> <global_declaration> <function_definition> root ( ) { <local_declaration> <body_statement> reclaim ; }
<global_declaration>
  -> lambda
<function_definition>
  -> lambda
<local_declaration>
  -> <var_dec> ; <local_declaration>
<var_dec>
  -> <data_type> id <var_tail>
<data_type>
  -> seed
<body_statement>
  -> lambda
```

The current aligned grammar requires local declarations before body statements, similar to old-style C structure.

## 7. CFG, FIRST, FOLLOW, and PREDICT Explanation

CFG means Context-Free Grammar. In your system it is stored as a Python dictionary named `cfg` in `Backend/cfg/grammar.py`. The keys are nonterminals such as `<program>` and `<expression>`. The values are possible productions.

### 7.1 Program and Declaration Productions

Source: `Backend/cfg/grammar.py:122-155`

Code:
```python
cfg = {
    "<program>": [
        [
            "<global_declaration>",
            "<function_definition>",
            "root",
            "(",
            ")",
            "{",
            "<local_declaration>",
            "<body_statement>",
            "reclaim",
            ";",
            "}",
        ]
    ],

    "<global_declaration>": [
        ["bundle", "id", "<bundle_or_var>", "<global_declaration>"],
        ["<data_type>", "id", "<array_dec>", "<var_value>", ";", "<global_declaration>"],
        ["fertile", "<data_type>", "id", "=", "<init_val>", "<const_next>", ";", "<global_declaration>"],
        [EPSILON],
    ],

    "<bundle_or_var>": [
        ["{", "<bundle_members>", "}", ";"],
        ["<bundle_mem_dec>", ";"],
    ],

    "<local_declaration>": [
        ["<var_dec>", ";", "<local_declaration>"],
        ["<const_dec>", ";", "<local_declaration>"],
        [EPSILON],
    ],
```

### 7.2 FIRST, FOLLOW, and PREDICT Computation

Source: `Backend/cfg/grammar.py:13-119`

Code:
```python
def compute_first(cfg):
    first = defaultdict(set)
    epsilon = EPSILON

    for lhs, productions in cfg.items():
        for prod in productions:
            if not prod:
                continue
            if prod[0] == epsilon:
                first[lhs].add(epsilon)
            elif prod[0] not in cfg:
                first[lhs].add(prod[0])

    changed = True
    while changed:
        changed = False
        for lhs, productions in cfg.items():
            for prod in productions:
                before = len(first[lhs])

                for symbol in prod:
                    if symbol in cfg:
                        first[lhs] |= (first[symbol] - {epsilon})
                        if epsilon not in first[symbol]:
                            break
                    else:
                        if symbol != epsilon:
                            first[lhs].add(symbol)
                        break
                else:
                    first[lhs].add(epsilon)

                if len(first[lhs]) > before:
                    changed = True

    return first


def compute_follow(cfg, first):
    follow = defaultdict(set)
    epsilon = EPSILON

    start_symbol = next(iter(cfg))
    follow[start_symbol].add("EOF")

    changed = True
    while changed:
        changed = False
        for lhs, productions in cfg.items():
            for prod in productions:
                for i, symbol in enumerate(prod):
                    if symbol in cfg:
                        before = len(follow[symbol])

                        j = i + 1
                        while j < len(prod):
                            next_symbol = prod[j]
                            if next_symbol in cfg:
                                follow[symbol] |= (first[next_symbol] - {epsilon})
                                if epsilon not in first[next_symbol]:
                                    break
                            else:
                                if next_symbol != epsilon:
                                    follow[symbol].add(next_symbol)
                                break
                            j += 1
                        else:
                            follow[symbol] |= follow[lhs]

                        if len(follow[symbol]) > before:
                            changed = True

    return follow


def compute_predict(cfg, first, follow):
    predict = {}
    epsilon = EPSILON

    for lhs, productions in cfg.items():
        for prod in productions:
            key = (lhs, tuple(prod))
            predict[key] = set()

            if not prod or (len(prod) == 1 and prod[0] == epsilon):
                predict[key] = follow[lhs].copy()
                continue

            first_set = set()
            for symbol in prod:
                if symbol in cfg:
                    first_set |= (first[symbol] - {epsilon})
                    if epsilon not in first[symbol]:
                        break
                else:
                    if symbol != epsilon:
                        first_set.add(symbol)
                    break
            else:
                first_set.add(epsilon)

            if epsilon in first_set:
                predict[key] = (first_set - {epsilon}) | follow[lhs]
            else:
                predict[key] = first_set

    return predict
```

| Set | Purpose |
|---|---|
| FIRST | Tells which token can start a nonterminal or production. |
| FOLLOW | Tells which token can legally appear after a nonterminal. |
| PREDICT | Tells the LL(1) parser which production to use for a lookahead token. |

Example for `plant("hello");`:

```text
<io_stmt> -> plant ( <arguments> ) ;
<arguments> -> <expression> <arg_next>
<expression> -> <assignment_expression>
<assignment_expression> -> <logic_or>
<factor> -> stringlit
```

Important: `"hello"` is handled by the lexer as one `stringlit` token. The CFG does not need separate quote terminals.

### 7.3 Expression Grammar

Source: `Backend/cfg/grammar.py:518-631`

Code:
```python
    "<expression>": [
        ["<assignment_expression>"],
    ],

    "<assignment_expression>": [
        ["<logic_or>", "<assignment_expression_next>"],
    ],

    "<assignment_expression_next>": [
        ["<assign_op>", "<assignment_expression>"],
        [EPSILON],
    ],

    "<logic_or>": [
        ["<logic_and>", "<logic_or_next>"],
    ],

    "<logic_or_next>": [
        ["||", "<logic_and>", "<logic_or_next>"],
        [EPSILON],
    ],

    "<logic_and>": [
        ["<relational>", "<logic_and_next>"],
    ],

    "<logic_and_next>": [
        ["&&", "<relational>", "<logic_and_next>"],
        [EPSILON],
    ],

    "<relational>": [
        ["<arithmetic>", "<relational_next>"],
    ],

    "<relational_next>": [
        ["<relational_op>", "<arithmetic>"],
        [EPSILON],
    ],

    "<relational_op>": [
        [">"],
        ["<"],
        [">="],
        ["<="],
        ["=="],
        ["!="],
    ],

    "<arithmetic>": [
        ["<term>", "<arithmetic_next>"],
    ],

    "<arithmetic_next>": [
        ["+", "<term>", "<arithmetic_next>"],
        ["-", "<term>", "<arithmetic_next>"],
        ["`", "<term>", "<arithmetic_next>"],
        [EPSILON],
    ],


    "<term>": [
        ["<power>", "<term_next>"],
    ],

    "<term_next>": [
        ["*", "<power>", "<term_next>"],
        ["/", "<power>", "<term_next>"],
        ["%", "<power>", "<term_next>"],
        [EPSILON],
    ],

    "<power>": [
        ["<factor>", "<power_next>"],
    ],

    "<power_next>": [
        ["**", "<power>"],
        [EPSILON],
    ],

    "<factor>": [
        ["(", "<paren_expr>"],
        ["<unary_op>", "<factor>"],
        ["id", "<factor_id_next>"],
        ["<literal>"],
    ],

    "<literal>": [
        ["intlit"],
        ["dblit"],
        ["chrlit"],
        ["stringlit"],
        ["sunshine"],
        ["frost"],
    ],

    "<paren_expr>": [
        ["<data_type>", ")", "<factor>"],
        ["<expression>", ")"],
    ],
    
    "<unary_op>": [
        ["~"],
        ["!"],
    ],

    "<factor_id_next>": [
        ["<array_access>", "<post_array_access>"],
        ["<struct_access>"],
        ["(", "<arguments>", ")"],
        [EPSILON],
    ],
}
```

Expression order:

```text
assignment expression
  -> logical OR
  -> logical AND
  -> equality / relational
  -> arithmetic addition and subtraction
  -> multiplication / division / modulo
  -> exponent
  -> unary or factor
```

This gives operator precedence. For example, `x + y * 2` parses multiplication before addition.

## 8. Semantic Analyzer Explanation

Semantic analysis checks meaning, not just token order. In this project, semantic checks are distributed across the AST builder, symbol table, and semantic validator.

### 8.1 Symbol Table

Source: `Backend/semantic/symbol_table.py:3-58`

Code:
```python
class SymbolTable:
    def __init__(self):
        self.variables = {}
        self.global_variables = {}
        self.functions = {}
        self.scopes = [{}]
        self.current_func_name = None
        self.function_variables = {}
        self.bundle_types = {}

    def declare_variable(self, name, type_, value=None, is_list=False, is_fertile=False):
        scope = self.scopes[-1]
        current_func = self.current_func_name
    

        if name in self.functions:
            return f"Semantic Error: Variable '{name}' already declared as a function."

        if current_func:
            if current_func not in self.function_variables:
                self.function_variables[current_func] = set()

            if name in self.function_variables[current_func]:
                return f"Semantic Error: Variable '{name}' already declared in this function."

            self.function_variables[current_func].add(name)

        if self.current_func_name:
            
            scope[name] = {
                "type": type_,  
                "value": value,
                "is_list": is_list,
                "is_fertile": is_fertile
            }
        else:
            if name in self.global_variables:
                return f"Semantic Error: Variable '{name}' already declared."
            
            self.variables[name] = {
                "type": type_,
                "value": value,
                "is_list": is_list,
                "is_fertile": is_fertile
            }
        

    def lookup_variable(self, name):
        for i, scope in enumerate(reversed(self.scopes)):
            if name in scope:
                return scope[name]
        
        if name in self.variables:
            return self.variables[name]

        return f"Semantic Error: Variable '{name}' used before declaration."
```

Explanation:
- `variables` stores global variables.
- `scopes` stores local scopes.
- `functions` stores function declarations.
- `bundle_types` stores struct-like bundle definitions.
- `declare_variable()` detects duplicate variables.
- `lookup_variable()` detects undeclared variables.

### 8.2 Variable Declaration and Duplicate Identifier Checking

Source: `Backend/parser/builder.py:310-370`

Code:
```python
def parse_variable(tokens, index, var_name, var_type):
    line = tokens[index].line
    var_nodes = []

    while True:
        global_var = symbol_table.variables.get(var_name)
        if global_var and global_var.get("is_fertile"):
            raise SemanticError(f"Semantic Error: Variable '{var_name}' is declared as fertile and cannot be re-declared.", line)

        is_list = False

        var_node = VariableDeclarationNode(var_type, var_name, line=line)

        if tokens[index].type == "=":
            index += 1

            if tokens[index].type == "[":
                is_list = True
                value_node, index = parse_list(tokens, index, var_type)
                var_node.add_child(value_node)

            elif tokens[index].value == "water":
                water_line = tokens[index].line
                index += 1
                if tokens[index].type != "(":
                    raise SemanticError(f"Semantic Error: Expected '(' after water.", water_line)
                index += 1
                water_type = None
                if tokens[index].value in {"seed", "tree", "leaf", "branch", "vine"}:
                    water_type = tokens[index].value
                    index += 1
                if tokens[index].type != ")":
                    raise SemanticError(f"Semantic Error: water() accepts only an optional type parameter (e.g., water(seed)).", water_line)
                index += 1
                if water_type and not _types_compatible(var_type, water_type):
                    raise SemanticError(f"Semantic Error: Type mismatch — cannot assign water({water_type}) to '{var_type}' variable.", water_line)
                value_node = ASTNode("Input", f"water({water_type})" if water_type else "water()", line=water_line)
                var_node.add_child(value_node)

            else:
                value_node, index = parse_expression_type(tokens, index, var_type)
                var_node.add_child(value_node)

        elif tokens[index].type == "[":
            is_list = True
            dimensions = []
            while tokens[index].type == "[":
                index += 1
                dim_size = 0
                if tokens[index].type == "dblit":
                    raise SemanticError(f"Semantic Error: Array size must be of type 'seed' (integer), got 'tree' (float) '{tokens[index].value}'.", line)
                if tokens[index].type == "intlit":
                    dim_size = int(tokens[index].value)
                    index += 1
                if tokens[index].type != "]":
                    raise SemanticError(f"Syntax Error: Expected ']' after list size.", line)
                index += 1
                dimensions.append(dim_size)

            default_literals = {"seed": "0", "tree": "0.0", "leaf": "''", "vine": '""', "branch": "false"}

```

Valid:

```gal
root(){
    seed x = 10;
    reclaim;
}
```

Invalid:

```gal
root(){
    seed x = 10;
    seed x = 20;
    reclaim;
}
```

Logic:
- `parse_variable()` collects the data type and identifier.
- It checks whether the name conflicts with a function or existing variable through the symbol table.
- If duplicate, it raises `SemanticError`.

### 8.3 Array Size Checking

Source: `Backend/parser/builder.py:373-385`

Code:
```python
                if len(dims) == 1:
                    for _ in range(dims[0]):
                        node.add_child(ASTNode("Value", default_literals.get(var_type, "0"), line=line))
                else:
                    for _ in range(dims[0]):
                        node.add_child(build_list_node(dims[1:]))
                return node

            list_node = build_list_node(dimensions)
            var_node.add_child(list_node)

            if tokens[index].type == "=":
                index += 1
```

Valid: `seed arr[3];`

Invalid: `seed arr[2.5];`

Logic:
- The builder expects an integer literal between brackets.
- If the dimension token is `dblit`, it raises a semantic error.
- This aligns the rule that array size must be an integer.

### 8.4 Type Compatibility

Source: `Backend/parser/builder.py:1006-1011`

Code:
```python
        func_name = tokens[index].value
        func_info = symbol_table.lookup_function(func_name)
        func_return_type = func_info["return_type"]  # type: ignore
        func_params = func_info["params"]  # type: ignore
        
        if func_return_type not in {"vine"}:
```

Explanation:
- Exact type matches are allowed.
- `seed` and `tree` are treated as compatible numeric types in this helper.
- Other mismatches produce semantic errors.

Invalid example:

```gal
root(){ seed x = "hello"; reclaim; }
```

Error:

```text
SEMANTIC error line 1 col 17 Type mismatch: cannot assign string value '"hello"' to integer (seed) variable
```

### 8.5 Assignment and Fertile Constant Reassignment

Source: `Backend/parser/builder.py:1930-1958`

Code:
```python
            arg_info = symbol_table.lookup_variable(arg_name)
            if isinstance(arg_info, str):
                raise SemanticError(arg_info, line)
            if not arg_info.get("is_list", False):
                raise SemanticError(f"Semantic Error: Argument '{arg_name}' is not an array. Parameter {len(provided_args) + 1} of '{func_name}' expects an array.", line)
            if arg_info["type"] != expected_type:
                raise SemanticError(f"Semantic Error: Array argument '{arg_name}' is of type '{arg_info['type']}', but parameter expects '{expected_type}'.", line)
            expr_node = ASTNode("Identifier", arg_name, line=line)
            index += 1
        else:
            expr_node, index = parse_expression_type(tokens, index, expected_type)

        arg_node = ASTNode("Argument")
        arg_node.add_child(expr_node)
        args_node.add_child(arg_node)

        provided_args.append((arg_node, expected_type))

   
        if tokens[index].type == ",":
            index += 1 

    index += 1 

    if tokens[index].type in {"++", "--"}:
        raise SemanticError(f"Semantic Error: Unary operators cannot be applied to function calls.", line)

    if len(provided_args) != len(expected_params):
        raise SemanticError(f"Semantic Error: Function '{func_name}' expects {len(expected_params)} arguments, but {len(provided_args)} were provided.", line)
```

Logic:
- The builder looks up the variable.
- If the variable is marked `is_fertile`, reassignment is rejected.
- It also checks that the assigned expression type is compatible with the variable type.

### 8.6 Function Call Parameter Checking

Source: `Backend/parser/builder.py:1961-2021`

Code:
```python
        expected_type = expected_params[i].children[0].value

        if expected_type in {"seed", "tree"} and arg_type == "seed":
            continue 
        
        if arg_type != expected_type:
            raise SemanticError(f"Semantic Error: Argument {i+1} of '{func_name}' should be '{expected_type}', but got '{arg_type}'.", line)

    return FunctionCallNode(func_name, args_node.children, line=line), index


def parse_water_statement(tokens, index):
    line = tokens[index].line
    index += 1

    if tokens[index].type != "(":
        raise SemanticError(f"Syntax Error: Expected '(' after water.", line)
    index += 1

    if tokens[index].value in {"seed", "tree", "leaf", "branch", "vine"}:
        water_type = tokens[index].value
        index += 1
        if tokens[index].type != ")":
            raise SemanticError(f"Semantic Error: water() accepts only an optional type parameter or a variable name.", line)
        index += 1
        if tokens[index].type != ";":
            raise SemanticError(f"Syntax Error: Expected ';' after water statement.", line)
        index += 1
        input_node = ASTNode("Input", f"water({water_type})", line=line)
        return input_node, index

    elif tokens[index].type == ")":
        index += 1
        if tokens[index].type != ";":
            raise SemanticError(f"Syntax Error: Expected ';' after water statement.", line)
        index += 1
        input_node = ASTNode("Input", "water()", line=line)
        return input_node, index

    elif tokens[index].type == "id":
        var_name = tokens[index].value
        var_info = symbol_table.lookup_variable(var_name)
        if isinstance(var_info, str):
            raise SemanticError(var_info, line)
        if var_info.get("is_fertile", False):
            raise SemanticError(f"Semantic Error: Variable '{var_name}' is declared as fertile and cannot be re-assigned a value.", line)
        var_type = var_info["type"]
        index += 1

        if tokens[index].type == "[":
            if not var_info.get("is_list", False) and var_info.get("type") != "vine":
                raise SemanticError(f"Semantic Error: Variable '{var_name}' is not a list.", line)
            index += 1
            index_expr, index, idx_type = parse_equality(tokens, index)
            if idx_type is not None and idx_type != "seed":
                raise SemanticError(f"Semantic Error: List index must be of type 'seed', got '{idx_type}'.", line)
            if tokens[index].type != "]":
                raise SemanticError(f"Syntax Error: Expected ']' after list index.", line)
            index += 1

            index_wrapper = ASTNode("Index", line=line)
```

Logic:
- The builder verifies that the called function exists.
- It checks argument count.
- It checks each argument type against the declared parameter type.
- It also handles array/list parameter compatibility.

### 8.7 Water Input Checking

Source: `Backend/parser/builder.py:2024-2112`

Code:
```python

            while tokens[index].type == "[":
                index += 1
                inner_expr, index, inner_type = parse_equality(tokens, index)
                if inner_type is not None and inner_type != "seed":
                    raise SemanticError(f"Semantic Error: List index must be of type 'seed', got '{inner_type}'.", line)
                if tokens[index].type != "]":
                    raise SemanticError(f"Syntax Error: Expected ']' after list index.", line)
                index += 1
                inner_wrapper = ASTNode("Index", line=line)
                inner_wrapper.add_child(inner_expr)
                list_access_node = ListAccessNode(list_access_node, inner_wrapper, line=line)

            if tokens[index].type != ")":
                raise SemanticError(f"Semantic Error: Expected ')' after water(arr[i]).", line)
            index += 1
            if tokens[index].type != ";":
                raise SemanticError(f"Syntax Error: Expected ';' after water statement.", line)
            index += 1
            input_node = ASTNode("Input", f"water({var_type})", line=line)
            assignment_node = AssignmentNode(list_access_node, input_node, line=line)
            return assignment_node, index

        if tokens[index].type != ")":
            raise SemanticError(f"Semantic Error: water() accepts only a single variable name or type parameter.", line)
        index += 1
        if tokens[index].type != ";":
            raise SemanticError(f"Syntax Error: Expected ';' after water statement.", line)
        index += 1

        input_node = ASTNode("Input", f"water({var_type})", line=line)
        value_ident = ASTNode("Identifier", var_name, line=line)
        assignment_node = AssignmentNode(var_name, input_node, line=line)
        return assignment_node, index

    else:
        raise SemanticError(f"Semantic Error: Invalid argument to water(). Expected a variable name or type.", line)


def parse_print(tokens, index):
    line = tokens[index].line
    index += 1

    if tokens[index].type != "(":
        raise SemanticError(f"Syntax Error: Expected '(' after plant statement.", line)
    index += 1
    token = tokens[index]

    args = []
    placeholder_count = 0

    if tokens[index].type == "stringlit":
        format_node, index, placeholder_count = parse_string_concatenation(tokens, index) 
        args.append(format_node)


    elif tokens[index].type == "id":
        identif_name = tokens[index].value

        if tokens[index + 1].type == "(":
            func_name = identif_name
            func_info = symbol_table.lookup_function(func_name)
            if isinstance(func_info, str):
                raise SemanticError(f"Semantic Error: Function '{func_name}' is not defined.", line)
            if func_info["return_type"] in {"seed", "tree"}:
                expr_node, index, _ = parse_expression(tokens, index)
                args.append(expr_node)
            elif func_info["return_type"] in {"vine"}:
                expr_node, index = parse_expression_vine(tokens, index)
                args.append(expr_node)
            elif func_info["return_type"] in {"leaf"}:
                expr_node, index = parse_expression_leaf(tokens, index)
                args.append(expr_node)
            elif func_info["return_type"] in {"branch"}:
                expr_node, index, _ = parse_expression_branch(tokens, index)
                args.append(expr_node)
            else:
                raise SemanticError(f"Semantic Error: Function '{func_name}' returns invalid type '{func_info['return_type']}'.", line)


        elif tokens[index].type == "id" and tokens[index + 1].type == "[":
            list_name = token.value
            list_info = symbol_table.lookup_variable(list_name)

            if isinstance(list_info, str):
                raise SemanticError(f"Semantic Error: List '{list_name}' used before declaration.", tokens[index].line)

            list_type = list_info["type"]
            start_index = index
```

Logic:
- `water()` must target a declared variable or valid assignable location.
- The builder checks if the target variable exists.
- It rejects invalid targets based on the grammar and symbol table.

### 8.8 Reclaim / Return Checking

Source: `Backend/parser/builder.py:2570-2612`

Code:
```python

    if tokens[index].value in {"seed", "tree", "vine", "leaf", "branch", "seed", "tree", "vine", "leaf", "branch"}:
        var_type = tokens[index].value
        var_name = tokens[index + 1].value
        index += 2

        initialization, index = parse_variable(tokens, index, var_name, var_type)

    elif tokens[index].type == "id":
        identifier_name = tokens[index].value
        var_info = symbol_table.lookup_variable(identifier_name)
        if isinstance(var_info, str):
            raise SemanticError(f"Semantic Error: Variable '{identifier_name}' used before declaration.", line)
        index += 1
        if tokens[index].type != "=":
            raise SemanticError(f"Syntax Error: Expected '=' after for loop identifier.", line)
        index += 1
        initialization, index = parse_assignment(tokens, index, identifier_name, var_info["type"])
        
    if tokens[index].type != ";":
        raise SemanticError(f"Syntax Error: Expected ';' after for loop initialization.", line)
    index += 1

    condition, index, cond_type = parse_expression_branch(tokens, index)

    if cond_type != "branch":
        raise SemanticError(f"Semantic Error: cultivate condition must be branch, got {cond_type}.", line)

    condition_node = ASTNode("Condition", line=line)
    condition_node.add_child(condition)

    if tokens[index].type != ";":
        raise SemanticError(f"Syntax Error: Expected ';' after for loop condition.", line)
    index += 1
    update_node = ASTNode("Update", line=line)

    while True:
        update, index = parse_update(tokens, index)
        update_node.add_child(update)
        if tokens[index].type == ",":
            index += 1
            continue
        else:
```

Logic:
- `reclaim` is the return statement.
- The builder checks if the return value matches the current function return type.
- In `root()`, the aligned grammar requires final `reclaim;`.

### 8.9 Struct / Bundle Checking

Source: `Backend/parser/builder.py:110-145`

Code:
```python
        elif token.value == "bundle":
            bundle_name = tokens[index + 1].value
            index += 2

            if tokens[index].type == "{":
                index += 1
                members = {}
                while tokens[index].type != "}":
                    if tokens[index].value in {"seed", "tree", "vine", "leaf", "branch"}:
                        member_type = tokens[index].value
                        member_name = tokens[index + 1].value
                        if member_name in members:
                            raise SemanticError(f"Semantic Error: Duplicate member '{member_name}' in bundle '{bundle_name}'.", tokens[index].line)
                        members[member_name] = member_type
                        index += 2
                        if tokens[index].type == ";":
                            index += 1
                    elif tokens[index].type == "id" and tokens[index].value in symbol_table.bundle_types:
                        member_type = tokens[index].value
                        member_name = tokens[index + 1].value
                        if member_name in members:
                            raise SemanticError(f"Semantic Error: Duplicate member '{member_name}' in bundle '{bundle_name}'.", tokens[index].line)
                        members[member_name] = member_type
                        index += 2
                        if tokens[index].type == ";":
                            index += 1
                    else:
                        raise SemanticError(f"Semantic Error: Invalid member type '{tokens[index].value}' in bundle definition.", tokens[index].line)
                index += 1

                if bundle_name in symbol_table.bundle_types:
                    raise SemanticError(f"Semantic Error: Bundle type '{bundle_name}' already defined.", token.line)

                symbol_table.bundle_types[bundle_name] = members
                node = BundleDefinitionNode(bundle_name, members, line=token.line)
                root.add_child(node)
```

Logic:
- Bundle declarations are stored in `symbol_table.bundle_types`.
- Duplicate member names are rejected.
- Bundle instance declarations and member access are later checked through builder methods and interpreter member access logic.

### 8.10 Scope Checking

Source: `Backend/semantic/symbol_table.py:79-85`

Code:
```python
    def enter_scope(self):
        self.scopes.append({})
        

    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()
```

### 8.11 Extra Semantic Validator Checks

Source: `Backend/semantic/analyzer.py:4-35`

Code:
```python
class ASTValidator:

    def __init__(self):
        self.errors = []
        self.warnings = []
        self._in_loop = 0
        self._in_switch = 0
        self._in_function = False
        self._current_func_type = None


    def validate(self, ast, symbol_table_data):
        self._walk(ast)
        return {
            "success": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "symbol_table": symbol_table_data,
            "ast": ast,
        }


    def _walk(self, node):
        if node is None:
            return
        handler = getattr(self, f'_check_{node.node_type}', None)
        if handler:
            handler(node)
        else:
            for child in getattr(node, 'children', []):
                self._walk(child)

```

Source: `Backend/semantic/analyzer.py:133-141`

Code:
```python
    def _check_Break(self, node):
        if self._in_loop == 0 and self._in_switch == 0:
            self.errors.append(
                f"SEMANTIC error line {node.line}: 'prune' used outside a loop or switch.")

    def _check_Continue(self, node):
        if self._in_loop == 0:
            self.errors.append(
                f"SEMANTIC error line {node.line}: 'skip' used outside a loop.")
```

Explanation:
- After the AST is built, `validate_ast(ast)` walks the AST.
- It checks rules such as `prune` only inside loops or harvest/switch, and `skip` only inside loops.

## 9. Runtime / Execution Explanation

After parsing and semantic analysis succeed, the system interprets the AST.

### 9.1 Interpreter Initialization

Source: `Backend/interpreter/interpreter.py:25-48`

Code:
```python
class Interpreter:
    def __init__(self, socketio=None):
        self.output = []
        self.socketio = socketio

        self.loop_stack = []
        self.break_flag = False
        self.continue_flag = False

        self.input_required = False
        self.input_events = {}
        self.input_values = {}

        self.current_node = None
        self.current_parent = None

        self.variables = {}
        self.global_variables = {}
        self.functions = {}
        self.scopes = [{}]
        self.current_func_name = None
        self.function_variables = {}
        self.bundle_types = {}

```

### 9.2 Central Dispatch

Source: `Backend/interpreter/interpreter.py:121-212`

Code:
```python
    def interpret(self, node):
        if isinstance(node, ProgramNode):
            return self.eval_program(node)
        elif isinstance(node, BundleDefinitionNode):
            return self.eval_bundle_definition(node)
        elif isinstance(node, MemberAccessNode):
            return self.eval_member_access(node)
        elif isinstance(node, ArrayMemberAccessNode):
            return self.eval_array_member_access(node)
        elif isinstance(node, VariableDeclarationNode):
            return self.eval_variable_declaration(node)
        elif isinstance(node, AssignmentNode):
            return self.eval_assignment(node)
        elif isinstance(node, BinaryOpNode):
            value = self.eval_binary_op(node)
            if isinstance(value, (int, float)):
                if value > 1000000000000000 or value < -9999999999999999:
                    raise InterpreterError(f"Runtime Error: Evaluated number exceeds maximum number of 16 digits", node.line)
            return value
        elif isinstance(node, FunctionDeclarationNode):
            return self.eval_function_declaration(node)
        elif isinstance(node, PrintNode):
            return self.eval_print(node)
        elif isinstance(node, ListNode):
            return self.eval_list(node)
        elif isinstance(node, ListAccessNode):
            return self.eval_list_access(node)
        elif isinstance(node, ReturnNode):
            return self.eval_return(node)
        elif isinstance(node, FunctionCallNode):
            return self.eval_function_call(node)
        elif isinstance(node, AppendNode):
            return self.eval_append(node)
        elif isinstance(node, InsertNode):
            return self.eval_insert(node)
        elif isinstance(node, RemoveNode):
            return self.eval_remove(node)
        elif isinstance(node, UnaryOpNode):
            return self.eval_unaryop(node)
        elif isinstance(node, FertileDeclarationNode):
            return self.eval_sturdy_declaration(node)
        elif isinstance(node, CastNode):
            return self.eval_cast(node)
        elif isinstance(node, SoilNode):
            return self.eval_soil(node)
        elif isinstance(node, BloomNode):
            return self.eval_bloom(node)
        elif isinstance(node, IfStatementNode):
            return self.eval_if_statement(node)
        elif isinstance(node, ForLoopNode):
            return self.eval_for_loop(node)
        elif isinstance(node, WhileLoopNode):
            return self.eval_while_loop(node)
        elif isinstance(node, DoWhileLoopNode):
            return self.eval_do_while_loop(node)
        elif isinstance(node, BreakNode):
            return self.eval_break(node)
        elif isinstance(node, ContinueNode):
            return self.eval_continue(node)
        elif isinstance(node, SwitchNode):
            return self.eval_switch(node)
        elif node.node_type == "Input":
            return self.eval_input(node)
        elif node.node_type == "Value":
            value = self._parse_literal(node.value)
            return value
        elif node.node_type == "Identifier":
            var_info = self.lookup_variable(node.value)
            if isinstance(var_info, str):
                raise InterpreterError(var_info, node.line)
            return var_info["value"]
        elif node.node_type == "FormattedString":
            return self.eval_formatted_string(node)
        elif node.node_type == "VariableDeclarationList":
            for child in node.children:
                self.eval_variable_declaration(child)
        elif node.node_type == "AssignmentList":
            for child in node.children:
                if isinstance(child, AssignmentNode):
                    self.eval_assignment(child)
                elif isinstance(child, UnaryOpNode):
                    self.eval_unaryop(child)
        elif node.node_type == "List":
            return [self.interpret(child) for child in node.children]
        elif node.node_type == "Block":
            self.eval_block(node)
        else:
            raise Exception(f"Unknown AST node type: {node.node_type}")

    def eval_program(self, node):
        for child in node.children:
            self.interpret(child)
```

Explanation:
- `interpret(node)` receives an AST node.
- It checks the node class or `node_type`.
- It calls the matching `eval_*` method.
- Example: `PrintNode` calls `eval_print()`, `AssignmentNode` calls `eval_assignment()`.

### 9.3 Program Execution Starts at `root`

Source: `Backend/interpreter/interpreter.py:214-219`

Code:
```python
        main_call = FunctionCallNode("root", [], node.line)
        return self.interpret(main_call)


    def eval_variable_declaration(self, node):
        var_type = node.children[0].value
```

Explanation:
- The interpreter first registers top-level declarations and functions.
- Then it automatically calls `root()`.
- This makes `root()` the required main function.

### 9.4 Runtime Variable Storage

Source: `Backend/interpreter/interpreter.py:50-92`

Code:
```python
    def declare_variable(self, name, type_, value=None, is_list=False, is_fertile=False):
        scope = self.scopes[-1]
        current_func = self.current_func_name
    

        if name not in self.scopes[-1]:
            scope[name] = {
                "type": type_,  
                "value": value,
                "is_list": is_list,
                "is_fertile": is_fertile
                }
        else:
            if name in self.global_variables:
                return f"Semantic Error: Variable '{name}' already declared."
            
            self.variables[name] = {
                "type": type_,
                "value": value,
                "is_list": is_list,
                "is_fertile": is_fertile
            }
            self.global_variables[name] = self.variables[name]
        

    def lookup_variable(self, name):
        for i, scope in enumerate(reversed(self.scopes)):
            if name in scope:
                return scope[name]
        
        if name in self.variables:
            return self.variables[name]

        return f"Semantic Error: Variable '{name}' used before declaration."
    
    def set_variable(self, name, value):
        for i in reversed(range(len(self.scopes))):
            scope = self.scopes[i]
            if name in scope:
                scope[name]["value"] = value
                return  

        return f"Semantic Error: Variable '{name}' not declared in any scope."
```

### 9.5 Variable Declaration Runtime Logic

Source: `Backend/interpreter/interpreter.py:222-298`

Code:
```python
        is_list = False
        
        default_values = {
            "seed": 0,
            "tree": 0.0,
            "leaf": '',
            "vine": "",
            "branch": False,
        }

        if value_node:
            if value_node.node_type == "List":
                if var_type in self.bundle_types:
                    value = [self._build_bundle_defaults(var_type) for _ in value_node.children]
                else:
                    def materialize(list_node):
                        result = []
                        for child in list_node.children:
                            if isinstance(child, ListNode):
                                result.append(materialize(child))
                            else:
                                item = self.interpret(child)
                                if var_type == "seed" and isinstance(item, float):
                                    item = int(item)
                                elif var_type == "tree":
                                    item = float(item)
                                result.append(item)
                        return result
                    value = materialize(value_node)

                is_list = True

            else:
                value = self.interpret(value_node)

                if var_type == "seed" and isinstance(value, float):
                    value = int(value)

                if var_type in {"tree", "seed"}:
                    if not isinstance(value, (int, float)):
                        raise InterpreterError(f"Semantic Error: Type Mismatch! Invalid value for {var_name}", node.line)
                    
                    if isinstance(value, bool):
                        raise InterpreterError(f"Semantic Error: Type Mismatch! Invalid value for {var_name}", node.line)


                    if var_type == "tree" and isinstance(value, int):
                        value = float(value)
                
                if var_type == "leaf":
                    if not isinstance(value, str):
                        raise InterpreterError(f"Semantic Error: Type Mismatch! Invalid value for {var_name}", node.line)

                if var_type == "vine":
                    if not isinstance(value, str):
                        raise InterpreterError(f"Semantic Error: Type Mismatch! Invalid value for {var_name}", node.line)

                if var_type == "branch":
                    if isinstance(value, int) or isinstance(value, float):
                        if value == 0:
                            value = False
                        else:
                            value = True
        else:
            if var_type in self.bundle_types:
                value = self._build_bundle_defaults(var_type)
            else:
                value = default_values.get(var_type, None)
                    
        self.declare_variable(var_name, var_type, value, is_list=is_list)

    def eval_bundle_definition(self, node):
        self.bundle_types[node.bundle_name] = node.members

    def _build_bundle_defaults(self, bundle_type_name):
        _member_defaults = {"seed": 0, "tree": 0.0, "leaf": '', "vine": "", "branch": False}
        members = self.bundle_types[bundle_type_name]
```

### 9.6 Expression Evaluation

Source: `Backend/interpreter/interpreter.py:516-683`

Code:
```python
            result = str(left) + str(right)
            return result

        left = self._parse_literal(left)
        right = self._parse_literal(right)

        if operator == '+' and (isinstance(left, str) or isinstance(right, str)):
            result = str(left) + str(right)
            return result

        try:
            if operator == '+':
                if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):
                    if isinstance(left, bool):
                        left = 1 if left == True else 0
                    elif isinstance(left, str):
                        left = 1 if left != "" else 0
                    if isinstance(right, bool):
                        right = 1 if right == True else 0
                    elif isinstance(right, str):
                        right = 1 if right != "" else 0
                return left + right  # type: ignore[operator]
            
            elif operator == '-':
                if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):
                    if isinstance(left, bool):
                        left = 1 if left == True else 0
                    elif isinstance(left, str):
                        left = 1 if left != "" else 0
                    if isinstance(right, bool):
                        right = 1 if right == True else 0
                    elif isinstance(right, str):
                        right = 1 if right != "" else 0

                return left - right  # type: ignore[operator]
            elif operator == '*':
                if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):
                    if isinstance(left, bool):
                        left = 1 if left == True else 0
                    elif isinstance(left, str):
                        left = 1 if left != "" else 0
                    if isinstance(right, bool):
                        right = 1 if right == True else 0
                    elif isinstance(right, str):
                        right = 1 if right != "" else 0
                return left * right  # type: ignore[operator]
            elif operator == '**':
                if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):
                    if isinstance(left, bool):
                        left = 1 if left == True else 0
                    elif isinstance(left, str):
                        left = 1 if left != "" else 0
                    if isinstance(right, bool):
                        right = 1 if right == True else 0
                    elif isinstance(right, str):
                        right = 1 if right != "" else 0
                return left ** right  # type: ignore[operator]
            elif operator == '/':
                if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):
                    if isinstance(left, bool):
                        left = 1 if left == True else 0
                    elif isinstance(left, str):
                        left = 1 if left != "" else 0
                    if isinstance(right, bool):
                        right = 1 if right == True else 0
                    elif isinstance(right, str):
                        right = 1 if right != "" else 0
                if right == 0:
                    raise InterpreterError("Runtime Error: Division by zero is undefined", node.line)
                return left / right  # type: ignore[operator]
            elif operator == '%':
                if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):
                    if isinstance(left, bool):
                        left = 1 if left == True else 0
                    elif isinstance(left, str):
                        left = 1 if left != "" else 0
                    if isinstance(right, bool):
                        right = 1 if right == True else 0
                    elif isinstance(right, str):
                        right = 1 if right != "" else 0
                if right == 0:
                    raise InterpreterError("Runtime Error: Division by zero is undefined", node.line)
                return left % right  # type: ignore[operator]
            elif operator == '==':
                return left == right
            elif operator == '!=':
                return left != right
            elif operator == '<':
                if isinstance(left, str):
                    left = 0 if left == "" else 1
                if isinstance(right, str):
                    right = 0 if right == "" else 1
                return left < right
            elif operator == '<=':
                if isinstance(left, str):
                    left = 0 if left == "" else 1
                if isinstance(right, str):
                    right = 0 if right == "" else 1
                return left <= right
            elif operator == '>':
                if isinstance(left, str):
                    left = 0 if left == "" else 1
                if isinstance(right, str):
                    right = 0 if right == "" else 1
                return left > right

            elif operator == '>=':
                if isinstance(left, str):
                    left = 0 if left == "" else 1
                if isinstance(right, str):
                    right = 0 if right == "" else 1
                return left >= right
            elif operator == '&&':
                if isinstance(left, int) or isinstance(left, float):
                    if left == 0:
                        left = False
                    else:
                        left = True
                elif isinstance(right, int) or isinstance(right, float):
                    if right == 0:
                        right = False
                    else:
                        right = True
                elif isinstance(left, str):
                    left = False if left == "" else True
                elif isinstance(right, str):
                    right = False if right == "" else True

                elif isinstance(left, str) or isinstance(right, str):
                    left = bool(left)
                elif isinstance(left, str) or isinstance(right, str):
                    right = bool(right)

                return bool(left) and bool(right)
            elif operator == '||':
                if isinstance(left, int) or isinstance(left, float):
                    if left == 0:
                        left = False
                    else:
                        left = True
                elif isinstance(right, int) or isinstance(right, float):
                    if right == 0:
                        right = False
                    else:
                        right = True

                elif isinstance(left, str) or isinstance(right, str):
                    left = bool(left)
                elif isinstance(left, str) or isinstance(right, str):
                    right = bool(right)

                return bool(left) or bool(right)
            elif operator == '!':
                return not bool(left)
            elif operator == 'neg':
                return -left  # type: ignore
            else:
                raise Exception(f"Unknown operator: {operator}")
        
        except ZeroDivisionError:
            raise InterpreterError("Runtime Error: Division by zero", "")

    def _parse_literal(self, value):

        if isinstance(value, str):
            var_info = self.lookup_variable(value)
            if var_info is not None and not isinstance(var_info, str):
                return var_info["value"]
```

### 9.7 `plant()` Output

Source: `Backend/interpreter/interpreter.py:750-804`

Code:
```python


    def eval_print(self, node):
        if not node.children:
            return

        first = node.children[0]

        evaluated_first = self.interpret(first)
        if isinstance(evaluated_first, float):
            whole, dot, dec = str(evaluated_first).partition('.')
            dec = dec[:5]
            evaluated_first = float(f"{whole}.{dec}")

        if isinstance(evaluated_first, str) and '{}' in evaluated_first:
            values = []
            for arg in node.children[1:]:
                value = self.interpret(arg)
                if isinstance(value, str) and not isinstance(self.lookup_variable(value), str):
                    value = self.lookup_variable(value)["value"]  # type: ignore[index]
                
                if isinstance(value, float):
                    whole, dot, dec = str(value).partition('.')
                    dec = dec[:5]
                    value = float(f"{whole}.{dec}")

                values.append(value)

            try:
                output_str = evaluated_first.format(*values)
            except Exception as e:
                raise Exception(f"Format error in plant(): '{evaluated_first}' with {values}: {e}")

            self.plant(output_str)
            return

        if len(node.children) > 1:
            parts = [str(evaluated_first)]
            for arg in node.children[1:]:
                value = self.interpret(arg)
                if isinstance(value, float):
                    whole, dot, dec = str(value).partition('.')
                    dec = dec[:5]
                    value = float(f"{whole}.{dec}")
                parts.append(str(value))
            self.plant(" ".join(parts))
            return

        self.plant(str(evaluated_first))

    def eval_formatted_string(self, node):
        value = node.value
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]

```

Explanation:
- `eval_print()` evaluates each argument.
- It joins multiple arguments with spaces.
- It appends or emits output through Socket.IO or REST collector.

Example:

```gal
plant("Sum: ", sum, "\n");
```

Runtime output in the current system:

```text
Sum:  15 \n
```

The extra spacing happens because multiple `plant` arguments are joined with spaces.

### 9.8 `water()` Input

Source: `Backend/interpreter/interpreter.py:1375-1468`

Code:
```python
        self.input_required = True


        self.emit_input_request(var_name, prompt)

        input_value = self.wait_for_input(var_name)


        self.input_required = False

        if var_type == "seed":
            original_input = input_value
            if isinstance(input_value, str) and input_value.startswith('-'):
                raise InterpreterError(f"Runtime Error: GAL uses '~' for negative numbers, not '-'. Got '{original_input}'; did you mean '~{original_input[1:]}'?", node.line)  # type: ignore
            if isinstance(input_value, str) and input_value.startswith('~'):
                input_value = '-' + input_value[1:]
            try:
                if len(input_value.strip('-').lstrip('0')) > 16:
                    raise InterpreterError(f"Runtime Error: Input value exceeds maximum number of 16 digits", node.line)
                input_value = int(float(input_value))  # type: ignore
            except ValueError:
                raise InterpreterError(f"Runtime Error: Expected integer value, got '{original_input}'", node.line)

        elif var_type == "tree":
            original_input = input_value
            if isinstance(input_value, str) and input_value.startswith('-'):
                raise InterpreterError(f"Runtime Error: GAL uses '~' for negative numbers, not '-'. Got '{original_input}'; did you mean '~{original_input[1:]}'?", node.line)  # type: ignore
            if isinstance(input_value, str) and input_value.startswith('~'):
                input_value = '-' + input_value[1:]
            try:
                if '.' in input_value:  # type: ignore
                    integer_part, decimal_part = str(input_value).split('.')
                    if len(integer_part.strip('-').lstrip('0')) > 16:
                        raise InterpreterError(f"Runtime Error: Input value exceeds maximum number of 16 digits", node.line)
                    if len(decimal_part.rstrip('0')) > 5:
                        raise InterpreterError(f"Runtime Error: Input value exceeds maximum number of 5 decimal numbers", node.line)

                else:
                    if len(input_value.strip('-').lstrip('0')) > 16:
                        raise InterpreterError(f"Runtime Error: Input value exceeds maximum number of 16 digits", node.line)

                input_value = float(input_value)  # type: ignore


            except ValueError:
                raise InterpreterError(f"Runtime Error: Expected float value, got '{original_input}'", node.line)

        elif var_type == "branch":
            if input_value == "true" or input_value == "false":
                suggestion = "sunshine" if input_value == "true" else "frost"
                raise InterpreterError(f"Runtime Error: GAL uses 'sunshine' and 'frost' for booleans, not 'true'/'false'. Got '{input_value}'; did you mean '{suggestion}'?", node.line)
            if input_value == "sunshine":
                input_value = True
            elif input_value == "frost":
                input_value = False
            else:
                raise InterpreterError(f"Runtime Error: expected branch value (sunshine/frost), got '{input_value}'", node.line)
            
        elif var_type == "leaf":
            if len(input_value) != 1:  # type: ignore
                raise InterpreterError(f"Runtime Error: Expected a single character for leaf, got '{input_value}'", node.line)
            input_value = str(input_value)

        elif var_type == "vine":
            input_value = str(input_value)

        return input_value

```

Explanation:
- `eval_input()` determines which variable receives input.
- It emits an input request to the frontend.
- It waits for the frontend response.
- It converts the input based on the target variable type.
- Invalid input raises `InterpreterError`.

### 9.9 Loops and Conditionals

Source: `Backend/interpreter/interpreter.py:1101-1142`

Code:
```python
                            return
                        
                    elif elif_node.node_type == "ElseStatement":
                        try:
                            self.enter_scope()
                            self.eval_block(elif_node.children[0])
                        finally:
                            self.exit_scope()
                        return

                    current_node += 1
        finally:
            self.exit_scope()

        return None
    
    def eval_for_loop(self, node):
        self.enter_loop('for')
        self.enter_scope()
        MAX_LOOP_ITERATIONS = 10000
        LOOP_COUNTER = 0

        try:
            instantiate_node = node.children[0]

            if isinstance(instantiate_node, VariableDeclarationNode):
                var_type = instantiate_node.children[0].value
                var_name = instantiate_node.children[1].value
                initial_value_node = self.interpret(instantiate_node.children[2])
                self.declare_variable(var_name, var_type, initial_value_node)

            elif isinstance(instantiate_node, AssignmentNode):
                var_name = instantiate_node.children[0].value
                initial_value_node = self.interpret(instantiate_node.children[1])
                self.lookup_variable(var_name)["value"] = initial_value_node  # type: ignore

            condition_node = node.children[1].children[0]
            condition_result = self.interpret(condition_node)

            if not isinstance(condition_result, bool):
                raise InterpreterError(f"Runtime Error: Condition must be a boolean. Got '{condition_result}'", node.line)

```

Source: `Backend/interpreter/interpreter.py:1144-1192`

Code:
```python
                LOOP_COUNTER += 1
                if LOOP_COUNTER > MAX_LOOP_ITERATIONS:
                    raise InterpreterError("Runtime Error: Infinite loop detected!", node.line)

                
                self.eval_block(node.children[3])

                if self.continue_flag:
                    self.continue_flag = False  

                if self.break_triggered():
                    break
                
                for update_expr in node.children[2].children:
                    self.interpret(update_expr)

                condition_result = self.interpret(condition_node)

        finally:
            self.exit_scope()
            self.exit_loop()


    def eval_while_loop(self, node):
        self.enter_loop('while')
        self.enter_scope()
        MAX_LOOP_ITERATIONS = 10000
        LOOP_COUNTER = 0
        condition_node = node.children[0].children[0]

        try:
            condition_result = self.interpret(condition_node)

            if not isinstance(condition_result, bool):
                raise InterpreterError(f"Runtime Error: Condition must be a boolean. Got '{condition_result}'", node.line)

            while condition_result:
                LOOP_COUNTER += 1
                if LOOP_COUNTER > MAX_LOOP_ITERATIONS:
                    raise InterpreterError("Runtime Error: Infinite loop detected!", node.line)

                block_node = node.children[1]
                self.eval_block(block_node)

                if self.continue_flag:
                    self.continue_flag = False

                if self.break_triggered():
                    break
```

### 9.10 `reclaim` Stops Function Execution

Source: `Backend/interpreter/interpreter.py:857-899`

Code:
```python
        function_name = node.value
        args = [self.interpret(arg.children[0]) for arg in node.children]

        func_info = self.lookup_function(function_name)
        if isinstance(func_info, str):
            raise InterpreterError(func_info, node.line)

        expected_params = func_info["params"]
        function_node = func_info["node"]

        if len(expected_params) != len(args):
            raise InterpreterError(
                f"Runtime Error: Function '{function_name}' expects {len(expected_params)} argument(s), got {len(args)}.",
                node.line
            )
        
        self.enter_scope()
        
        try:
            for i, param in enumerate(expected_params):
                param_name = param["name"]
                param_type = param["type"]
                arg_value = args[i]
                is_list = param.get("is_list", False)
                self.declare_variable(param_name, param_type, arg_value, is_list=is_list)

            try:
                self.eval_block(function_node.children[2])

            except ReturnValue as ret:
                return ret.value

            return None

        finally:
            self.exit_scope()
            self.current_func_name = None


    def eval_append(self, node):
        list_name = node.parent.children[0].value
        list_info = self.lookup_variable(list_name)

```

Explanation:
- `eval_return()` raises `ReturnValue` as a control signal.
- `eval_function_call()` catches `ReturnValue` and returns its value to the caller.
- This is how `reclaim` stops a function body early.

## 10. Error Handling Explanation

Errors are detected at different compiler stages. Each stage stops the pipeline if it fails.

| Error Type | Detected In | Error Class / Format | Example |
|---|---|---|---|
| Lexical error | `Backend/lexer/scanner.py` | `LexicalError` | Invalid delimiter, invalid identifier, unclosed string. |
| Syntax error | `Backend/parser/parser.py` | dictionary with `type: SYNTAX` | Missing semicolon, unexpected token. |
| Semantic error | `Backend/parser/builder.py`, `Backend/semantic/analyzer.py` | `SemanticError` | Undeclared variable, type mismatch, duplicate declaration. |
| Runtime error | `Backend/interpreter/interpreter.py` | `InterpreterError` | Array out of bounds, division by zero during execution. |

### 10.1 Lexical Error Class

Source: `Backend/lexer/errors.py:3-11`

Code:
```python
class LexicalError:

    def __init__(self, pos, details):
        self.pos = pos
        self.details = details

    def as_string(self):
        self.details = self.details.replace('\n', '\\n')
        return f"LEXICAL error line {self.pos.ln} col {self.pos.col} {self.details}"
```

Example invalid identifier:

```gal
root(){ seed 1x; reclaim; }
```

Error:

```text
LEXICAL error line 1 col 13 Identifiers cannot start with a number: '1x...'
```

Example invalid delimiter:

```gal
root(){ seed x@; reclaim; }
```

Error:

```text
LEXICAL error line 1 col 13 Invalid delimiter '@' after 'x'
```

### 10.2 Syntax Error

Detected in `LL1Parser.parse()` when the current token does not match the expected terminal or no CFG production matches the lookahead.

Example:

```gal
root(){ seed x = 10 reclaim; }
```

Error:

```text
SYNTAX error line 1 col 20 Unexpected token 'reclaim'. Expected: semicolon or expression continuation tokens
```

### 10.3 Semantic Error Class

Source: `Backend/semantic/errors.py:6-12`

Code:
```python
class SemanticError(Exception):
    def __init__(self, message, line):
        super().__init__(message)
        clean = _REDUNDANT_PREFIX.sub('', str(message)).strip()
        self.message = f"SEMANTIC error line {line}: {clean}"

    def __str__(self):
```

Example undeclared variable:

```gal
root(){ x = 1; reclaim; }
```

Error:

```text
SEMANTIC error line 1: Variable 'x' used before declaration.
```

Example type mismatch:

```gal
root(){ seed x = "hello"; reclaim; }
```

Error:

```text
SEMANTIC error line 1 col 17 Type mismatch: cannot assign string value '"hello"' to integer (seed) variable
```

### 10.4 Runtime Error Class

Source: `Backend/interpreter/errors.py:6-27`

Code:
```python
class ReturnValue(Exception):

    def __init__(self, value):
        self.value = value


class _CancelledError(Exception):
    pass


class InterpreterError(Exception):

    def __init__(self, message, line):
        super().__init__(message)
        clean = _REDUNDANT_PREFIX.sub('', str(message)).strip()
        if line is not None and str(line) != "":
            self.message = f"RUNTIME error line {line}: {clean}"
        else:
            self.message = clean

    def __str__(self):
        return self.message
```

Example array out of bounds:

```gal
root(){ seed a[2] = {1,2}; plant(a[3]); reclaim; }
```

Error:

```text
RUNTIME error line 1: Index '3' out of bounds for 'a'.
```

### 10.5 Sending Errors Back to Frontend

Errors are returned by Flask routes as JSON. Example:

```json
{
  "stage": "semantic",
  "error": "SEMANTIC error line 1: Variable 'x' used before declaration.",
  "output": ""
}
```

The frontend displays the returned `error` or `output` inside the output panel.

## 11. Full Example Walkthrough

Sample code:

```gal
root() {
    seed x = 10;
    seed y = 5;
    seed sum;

    sum = x + y;

    plant("Sum: ", sum, "\n");

    reclaim;
}
```

### A. Source Code Input

The user writes the code in the Monaco editor. The frontend stores it in `sourceCode` through `editor.getValue()` and sends it to `/api/run` as `source_code`.

### B. Lexer Scanning

The lexer receives the whole source string, but scans it character by character using `current_char` and `advance()`.

### C. Token List Generated

This token table was generated from the current system pipeline.

| Lexeme | Token Type | Value | Line | Column |
|---|---|---|---:|---:|
| `root` | `root` | `root` | 1 | 0 |
| `(` | `(` | `(` | 1 | 4 |
| `)` | `)` | `)` | 1 | 5 |
| `{` | `{` | `{` | 1 | 7 |
| `\n` | `newline` | `\n` | 1 | 8 |
| `seed` | `seed` | `seed` | 2 | 4 |
| `x` | `id` | `x` | 2 | 9 |
| `=` | `=` | `=` | 2 | 11 |
| `10` | `intlit` | `10` | 2 | 13 |
| `;` | `;` | `;` | 2 | 15 |
| `seed` | `seed` | `seed` | 3 | 4 |
| `y` | `id` | `y` | 3 | 9 |
| `=` | `=` | `=` | 3 | 11 |
| `5` | `intlit` | `5` | 3 | 13 |
| `;` | `;` | `;` | 3 | 14 |
| `seed` | `seed` | `seed` | 4 | 4 |
| `sum` | `id` | `sum` | 4 | 9 |
| `;` | `;` | `;` | 4 | 12 |
| `sum` | `id` | `sum` | 6 | 4 |
| `=` | `=` | `=` | 6 | 8 |
| `x` | `id` | `x` | 6 | 10 |
| `+` | `+` | `+` | 6 | 12 |
| `y` | `id` | `y` | 6 | 14 |
| `;` | `;` | `;` | 6 | 15 |
| `plant` | `plant` | `plant` | 8 | 4 |
| `(` | `(` | `(` | 8 | 9 |
| `"Sum: "` | `stringlit` | `"Sum: "` | 8 | 10 |
| `,` | `,` | `,` | 8 | 17 |
| `sum` | `id` | `sum` | 8 | 19 |
| `,` | `,` | `,` | 8 | 22 |
| `"\n"` | `stringlit` | `"\n"` | 8 | 24 |
| `)` | `)` | `)` | 8 | 28 |
| `;` | `;` | `;` | 8 | 29 |
| `reclaim` | `reclaim` | `reclaim` | 10 | 4 |
| `;` | `;` | `;` | 10 | 11 |
| `}` | `}` | `}` | 11 | 0 |
| `` | `EOF` | `` | 11 | 0 |

### D. Parser Checking With CFG

Important derivation:

```text
<program>
  -> <global_declaration> <function_definition> root ( ) { <local_declaration> <body_statement> reclaim ; }
<local_declaration>
  -> <var_dec> ; <local_declaration>
  -> seed id <var_tail> ; <local_declaration>
  -> seed id = <init_val> ; <local_declaration>
<body_statement>
  -> <non_reclaim_stmt> <body_statement>
  -> <id_stmt> <body_statement>
  -> id <id_next> <id_stmt_tail> <body_statement>
  -> id = <expression> ; <body_statement>
  -> <non_reclaim_stmt> <body_statement>
  -> <io_stmt> <body_statement>
  -> plant ( <arguments> ) ; <body_statement>
<body_statement>
  -> lambda
```

### E. Semantic Checking

| Check | Result |
|---|---|
| `x`, `y`, and `sum` are declared before use | Passed |
| `x` and `y` are `seed` integers | Passed |
| `sum = x + y` assigns numeric result to `seed` | Passed |
| `plant("Sum: ", sum, "\n")` uses valid output arguments | Passed |
| `reclaim;` exists at the end of root | Passed |

### F. Runtime Execution

| Step | Action | Runtime Effect |
|---:|---|---|
| 1 | Enter `root()` | New function scope is created. |
| 2 | `seed x = 10;` | Store `x` as seed value `10`. |
| 3 | `seed y = 5;` | Store `y` as seed value `5`. |
| 4 | `seed sum;` | Store `sum` as seed default value `0`. |
| 5 | `sum = x + y;` | Evaluate `10 + 5`, store `sum = 15`. |
| 6 | `plant("Sum: ", sum, "\n");` | Output text and value. |
| 7 | `reclaim;` | Stop root function execution. |

Runtime variable table while inside `root()`:

| Variable | Type | Value |
|---|---|---:|
| `x` | `seed` | `10` |
| `y` | `seed` | `5` |
| `sum` | `seed` | `15` |

### G. Final Output

Actual current-system output:

```text
Sum:  15 \n
```

## 12. Code-Level Explanation Format

For defense, use this format whenever explaining an important code block:

```text
Code:
[paste the exact code snippet]

Explanation:
- What this code does
- When it runs
- What input it receives
- What output it returns
- What part of the compiler depends on it
```

Source: `Backend/lexer/scanner.py:1513-1529`

Code:
```python
def lex(source_code):
    lexer = Lexer(source_code)
    tokens, errors = lexer.make_tokens()

    # Report lexical errors one at a time — only surface the first.
    # The user fixes it, re-runs, and sees the next one (if any).
    str_errors = []
    if errors:
        e = errors[0]
        try:
            if hasattr(e, 'as_string') and callable(getattr(e, 'as_string')):
                str_errors.append(e.as_string())
            else:
                str_errors.append(str(e))
        except Exception:
            str_errors.append(str(e))
    return tokens, str_errors
```

Explanation:
- This code is the public lexer entry point.
- It runs whenever the server calls `lex(source_code)`.
- It receives the full source code string.
- It returns the generated token list and lexical error list.
- The parser depends on the tokens returned by this function.

## 13. Defense Script Section

Use this short Taglish explanation during defense:

```text
Sa system namin, unang nangyayari is kinukuha muna ng frontend yung code na nilagay ng user sa editor gamit yung editor.getValue(). Then ipinapasa siya sa backend Flask server as source_code.

Pagdating sa backend, unang stage is lexer. Yung lexer hindi niya agad iniintindi yung buong program as meaning. Binabasa niya muna yung source code character by character gamit yung current_char and advance(). Habang nagbabasa siya, kino-convert niya yung raw text into tokens, like seed, id, intlit, equals, semicolon, plant, and EOF.

After lexing, yung token list pinapasa sa parser. Yung parser namin is LL(1), so gumagamit siya ng CFG, FIRST, FOLLOW, and PREDICT sets. May stack siya, then tinitingnan niya yung current token or lookahead para malaman kung anong production rule ang gagamitin. Kapag hindi tugma yung token sa grammar, syntax error ang lalabas.

Kapag pasado sa syntax, bubuo naman yung builder ng AST. Then semantic checking happens. Dito chine-check kung declared ba yung variables, tama ba yung type, may duplicate ba, valid ba yung array size, tama ba yung function call arguments, and valid ba yung reclaim.

Kapag pasado lahat, interpreter naman yung tatakbo. Yung interpreter ang nag-e-execute ng AST. Siya yung nag-i-store ng variables sa scopes, nag-e-evaluate ng expressions, nagpapatakbo ng loops and conditionals, nagha-handle ng plant output, and nagre-request ng input kapag may water().

Kung may error sa kahit anong stage, titigil yung pipeline doon. For example lexical error kapag invalid character, syntax error kapag mali grammar, semantic error kapag undeclared variable or type mismatch, and runtime error kapag execution problem like array out of bounds. Then yung error message ibabalik ng server sa frontend para makita ng user sa output panel.
```

## 14. Formatting Requirements Checklist

This document is prepared as a PDF-ready technical explanation. It includes:

- Clear numbered sections.
- Tables for pipeline, tokens, delimiters, semantic checks, and runtime variables.
- Code snippets from the actual Python and JavaScript files.
- Exact file names, class names, function names, and variable names.
- A full example walkthrough from editor input to final output.
- A defense script in simple Taglish.

## Appendix C. Deep Code Trace With Exact Line References

This appendix is added for defense questions that ask, "What exact code runs next?"

### C.1 Server Receives Code Before Lexing

Exact flow:

| Step | File and Lines | Code Object | What Happens |
|---:|---|---|---|
| 1 | `UI/main.js:1005-1035` | `runProgram()` | Gets the full editor text using `editor.getValue()` and stores it in `sourceCode`. |
| 2 | `UI/main.js:910-916` | `runViaREST(sourceCode)` | Sends JSON body `{ source_code: sourceCode }` to `/api/run`. |
| 3 | `Backend/server.py:323-384` | `run_endpoint()` | Reads `data = request.get_json()` then stores `source_code = data['source_code']`. |
| 4 | `Backend/server.py:340` | `lex(source_code)` | Passes the full source string to the lexer. |

Key point: the server passes the whole source code string, but the lexer reads it one character at a time.

### C.2 Lexer Reserved Word Process

Example:

```gal
root()
```

Exact flow:

| Step | File and Lines | Code Object | What Happens |
|---:|---|---|---|
| 1 | `Backend/lexer/scanner.py:18-27` | `Lexer.__init__()` and `advance()` | Stores the source in `self.source_code`, creates `self.pos`, sets `self.current_char`, then moves to the first character. |
| 2 | `Backend/lexer/scanner.py:29-35` | `make_tokens()` | Starts the main `while self.current_char != None` loop. |
| 3 | `Backend/lexer/scanner.py:37-40` | alphabet branch | Because `current_char` is `r`, the lexer enters the alphabet/reserved-word path and starts `ident_str`. |
| 4 | `Backend/lexer/scanner.py:341-379` | `root` nested check | Checks `r -> o -> o -> t`, then checks if the next character is valid for `root`, usually `(`. |
| 5 | `Backend/lexer/scanner.py:375` | `tokens.append(...)` | Appends `Token(TT_RW_ROOT, ident_str, line, pos.col)`. |

Important variables:

| Variable | Meaning |
|---|---|
| `self.current_char` | The character currently being checked. Example: `r`, then `o`, then `o`, then `t`. |
| `ident_str` | The word being built. Example: `r`, `ro`, `roo`, `root`. |
| `pos` | Copy of the starting position of the lexeme, used for token line/column. |
| `tokens` | List where successful tokens are stored. |

### C.3 Lexer Fallback From Reserved Word to Identifier

Example:

```gal
roof()
```

Exact flow:

| Step | File and Lines | Code Object | What Happens |
|---:|---|---|---|
| 1 | `Backend/lexer/scanner.py:341-367` | `root` attempt | The lexer collects `r`, `o`, `o`. |
| 2 | `Backend/lexer/scanner.py:368` | `if self.current_char == "t":` | This condition is false because the current character is `f`. |
| 3 | `Backend/lexer/scanner.py:611-638` | identifier fallback | Since the reserved-word path did not append a token, the code continues to the fallback identifier block. |
| 4 | `Backend/lexer/scanner.py:614-615` | `while self.current_char is not None and self.current_char in ALPHANUM:` | The loop collects the remaining character `f`, so `ident_str` becomes `roof`. |
| 5 | `Backend/lexer/scanner.py:631-632` | delimiter check and token append | If the next character is valid, such as `(`, the lexer appends `Token(TT_IDENTIFIER, ident_str, line, pos.col)`. |

Why there is no `else false` code:

```text
Python does not need a special false program here.
If the nested reserved-word condition fails and no token is appended,
execution naturally continues to the fallback identifier code below it.
```

### C.4 Lexer Passes Tokens Back to the Server

Exact flow:

| Step | File and Lines | Code Object | What Happens |
|---:|---|---|---|
| 1 | `Backend/lexer/scanner.py:1502-1505` | EOF append and return | Adds `Token(TT_EOF, "", line, pos.col)` and returns `tokens, errors`. |
| 2 | `Backend/lexer/scanner.py:1513-1529` | `lex(source_code)` | Creates `Lexer(source_code)`, calls `make_tokens()`, converts lexical errors to strings, and returns tokens/errors. |
| 3 | `Backend/server.py:340-344` | `run_endpoint()` | If `lex_errors` exists, returns a lexical error immediately. Otherwise proceeds to parsing. |

### C.5 Parser Detailed Process After Lexer

Exact flow:

| Step | File and Lines | Code Object | What Happens |
|---:|---|---|---|
| 1 | `Backend/server.py:348` | `parser.parse_and_build(tokens)` | Sends the token list to the parser. |
| 2 | `Backend/parser/parser.py:1183-1191` | `parse_and_build()` | Calls `self.parse(tokens)` first for syntax checking. |
| 3 | `Backend/parser/parser.py:614-626` | `parse()` setup | Converts tokens into `_TokView`, creates stack `[EOF, <program>]`, and starts reading lookahead tokens. |
| 4 | `Backend/parser/parser.py:665-698` | nonterminal expansion | If stack top is a nonterminal, uses `self.parsing_table[top][token_type]` to choose a production. |
| 5 | `Backend/parser/parser.py:717-860` | terminal matching | If stack top is a terminal and matches the current token, consumes token by increasing `index`. |
| 6 | `Backend/parser/parser.py:702-715` and `863-1181` | syntax error creation | If no production or terminal mismatch occurs, creates a detailed syntax error. |
| 7 | `Backend/parser/parser.py:1196-1198` | builder call | After syntax success, filters newline tokens and calls `_build_ast(filtered)`. |

Parser defense sentence:

```text
After lexing, the parser does not read raw characters anymore.
It reads token types. It compares the current lookahead token with the LL(1)
PREDICT table to know which grammar production to use.
```

### C.6 CFG and PREDICT Decision Code

Exact flow:

| Step | File and Lines | Code Object | What Happens |
|---:|---|---|---|
| 1 | `Backend/cfg/grammar.py:122-631` | `cfg` dictionary | Stores productions such as `<program>`, `<statement>`, and `<expression>`. |
| 2 | `Backend/cfg/grammar.py:13-48` | `compute_first()` | Computes FIRST sets from the grammar. |
| 3 | `Backend/cfg/grammar.py:51-85` | `compute_follow()` | Computes FOLLOW sets from the grammar. |
| 4 | `Backend/cfg/grammar.py:88-119` | `compute_predict()` | Combines FIRST and FOLLOW to produce PREDICT sets. |
| 5 | `Backend/parser/parser.py:66-82` | `construct_parsing_table()` | Converts PREDICT sets into the parser table. |

### C.7 Semantic Process After Parser

Exact flow:

| Step | File and Lines | Code Object | What Happens |
|---:|---|---|---|
| 1 | `Backend/parser/parser.py:1196-1198` | `_build_ast(filtered)` | Builds AST using `Backend/parser/builder.py`. |
| 2 | `Backend/parser/builder.py:21-32` | `build_ast(tokens)` | Creates the builder parser, starts parsing, and returns AST plus symbol table. |
| 3 | `Backend/parser/builder.py:310-453` | `parse_variable()` | Handles variable declarations and declaration-related semantic checks. |
| 4 | `Backend/semantic/symbol_table.py:13-48` | `declare_variable()` | Stores variables and catches duplicates. |
| 5 | `Backend/semantic/symbol_table.py:50-58` | `lookup_variable()` | Finds variables or reports undeclared identifiers. |
| 6 | `Backend/server.py:359` | `validate_ast(ast)` | Runs the semantic validator after AST build. |
| 7 | `Backend/semantic/analyzer.py:4-23` | `ASTValidator.validate()` | Walks the AST and collects semantic errors/warnings. |
| 8 | `Backend/semantic/analyzer.py:133-141` | `_check_Break()` / `_check_Continue()` | Checks `prune` and `skip` context rules. |

Semantic defense sentence:

```text
Semantic analysis checks meaning. The grammar may say a statement shape is valid,
but semantic analysis checks if variables exist, types match, constants are not reassigned,
arrays are valid, and control statements are used in the correct place.
```

### C.8 Interpreter Process After Semantic Success

Exact flow:

| Step | File and Lines | Code Object | What Happens |
|---:|---|---|---|
| 1 | `Backend/server.py:370` | `Interpreter(socketio=collector)` | Creates the runtime interpreter. |
| 2 | `Backend/server.py:372` | `interpreter.interpret(ast)` | Starts execution using the AST. |
| 3 | `Backend/interpreter/interpreter.py:121-212` | `interpret(node)` | Dispatches AST nodes to matching `eval_*` methods. |
| 4 | `Backend/interpreter/interpreter.py:214-219` | `eval_program()` | Registers top-level declarations and automatically calls `root()`. |
| 5 | `Backend/interpreter/interpreter.py:50-92` | variable runtime methods | Stores, looks up, and updates runtime variables. |
| 6 | `Backend/interpreter/interpreter.py:516-683` | `eval_binary()` | Evaluates arithmetic, relational, logical, and concatenation expressions. |
| 7 | `Backend/interpreter/interpreter.py:750-804` | `eval_print()` | Handles `plant()` output. |
| 8 | `Backend/interpreter/interpreter.py:1375-1468` | `eval_input()` | Handles `water()` interactive input. |
| 9 | `Backend/interpreter/interpreter.py:857-899` | `eval_return()` / function call | Uses `ReturnValue` to stop function execution when `reclaim` runs. |

Interpreter defense sentence:

```text
The interpreter does not check grammar anymore. At this point, the code is already
valid. The interpreter walks the AST and performs the actual actions: assign values,
evaluate expressions, execute loops, print output, and request input.
```


## Appendix A. Important File Interaction Map

```text
UI/main.js or UI/index.html
  -> sends source_code to Backend/server.py
Backend/server.py
  -> calls Backend/lexer/scanner.py lex(source_code)
Backend/lexer/scanner.py
  -> returns Token objects from Backend/shared/tokens.py
Backend/server.py
  -> calls LL1Parser.parse_and_build(tokens)
Backend/parser/parser.py
  -> uses Backend/cfg/grammar.py cfg and predict_sets
Backend/parser/parser.py
  -> calls Backend/parser/builder.py build_ast(tokens)
Backend/parser/builder.py
  -> uses Backend/shared/ast_nodes.py and Backend/semantic/symbol_table.py
Backend/server.py
  -> calls Backend/semantic/analyzer.py validate_ast(ast)
Backend/server.py
  -> calls Backend/interpreter/interpreter.py Interpreter.interpret(ast)
Backend/interpreter/interpreter.py
  -> returns output or InterpreterError
Backend/server.py
  -> sends JSON output/error to frontend
```

## Appendix B. Common Defense Questions and Direct Answers

| Question | Short Answer |
|---|---|
| Does the lexer scan the whole code at once? | The server passes the whole string to the lexer, but the lexer processes it one character at a time using `current_char` and `advance()`. |
| Where does `roof` become an identifier instead of `root`? | In `Backend/lexer/scanner.py`, after reserved-word matching fails, the fallback identifier loop collects remaining alphanumeric characters and appends `Token(TT_IDENTIFIER, ident_str, ...)`. |
| Why are quotes not in the CFG? | Because the lexer converts the whole quoted text into one `stringlit` token before parsing. |
| What chooses the CFG production? | The LL(1) parser uses the current lookahead token and the PREDICT set in `self.parsing_table`. |
| What catches undeclared variables? | `SymbolTable.lookup_variable()` and builder semantic checks raise `SemanticError`. |
| What executes the program? | `Interpreter.interpret(ast)` dispatches AST nodes to `eval_*` methods and automatically calls `root()`. |
| How is output displayed? | `plant()` becomes a `PrintNode`, `eval_print()` emits output, the server returns it as JSON, and the frontend displays it. |

## Appendix D. Removed CGMA Built-In Names

The old CGMA-style names `ts` and `taper` are no longer part of the backend compiler system.

Current system behavior:

| Old Name | Current Status | Why |
|---|---|---|
| `ts` / `.ts` | Removed | It came from the CGMA reference material, not the GrowALanguage reserved-word set. |
| `taper` / `.taper` | Removed | It came from the CGMA reference material, not the GrowALanguage reserved-word set. |

Important implementation note:
- These names are not lexer reserved words.
- The previous hidden builder/interpreter support was removed.
- The backend now has no `TaperNode`, `TSNode`, `eval_taper()`, or `eval_ts()` logic.

Recommended future GAL-style names, if this feature is added later:

| Feature | Recommended GAL Name | Example |
|---|---|---|
| array/string size | `.count` | `seed size = arr.count;` |
| split vine into leaf characters | `.leaves` | `leaf letters[3] = word.leaves;` |

These recommended names are documentation guidance only unless the backend is updated to implement them.

## Appendix E. Concrete Source Code Logic Notes

This section explains the main non-lexer source files more directly. It is meant for defense questions like "what does this file really do line by line?" or "how does the data move from this function to the next one?"

### E.1 `Backend/server.py` Route Logic

The server is the coordinator. It does not tokenize, parse, or execute by itself. Instead, it receives source code from the frontend and calls each compiler stage in order.

Source: `Backend/server.py:323-384`

Code:
```python
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
```

Concrete logic:

| Code Part | What It Means | Why It Matters |
|---|---|---|
| `@app.route('/api/run', methods=['POST'])` | Connects the `/api/run` URL to the Python function below it. | This is the endpoint used when the user presses Run without interactive input. |
| `def run_endpoint():` | Function that handles a run request. | This is the backend entry point for full compilation and execution. |
| `data = request.get_json()` | Reads the JSON body sent by JavaScript. | This is how Python receives the editor text. |
| `source_code = data['source_code']` | Stores the user program in a Python variable. | This exact variable is passed to the lexer. |
| `tokens, lex_errors = lex(source_code)` | Calls the lexer. | The raw string becomes a token list. |
| `if lex_errors:` | Checks if lexing failed. | The pipeline stops early for lexical errors. |
| `parse_result = parser.parse_and_build(tokens)` | Calls syntax parser and AST builder. | Tokens become an AST if grammar and builder checks pass. |
| `sem_result = validate_ast(ast, symbol_table)` | Runs semantic validation. | Checks meaning after syntax succeeds. |
| `Interpreter(socketio=collector)` | Creates runtime executor. | The interpreter will execute the AST and collect `plant()` output. |
| `interpreter.interpret(ast)` | Executes the program. | This is where actual runtime behavior happens. |
| `return jsonify(...)` | Sends output or error back to frontend. | The UI displays this response in the output panel. |

Important defense sentence:

```text
The server is the controller of the compiler pipeline. It receives source_code, then calls lexer, parser/builder, semantic validator, and interpreter. If any stage returns an error, the server stops and returns that error to the frontend.
```

### E.2 `OutputCollector` Logic

`OutputCollector` is used by the REST execution route so `plant()` output can be collected without needing a real Socket.IO client.

Source: `Backend/server.py:306-316`

Code:
```python
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
```

Concrete logic:

| Code Part | What It Means |
|---|---|
| `self.outputs = []` | Stores every output string produced during execution. |
| `emit(self, event, data=None)` | Mimics the Socket.IO `emit()` method. |
| `if event == 'output'` | Only output events are collected as printed output. |
| `self.outputs.append(...)` | Saves the output text so `/api/run` can return it as JSON. |

This is why the same interpreter can work for both REST execution and Socket.IO execution.

### E.3 `Backend/parser/parser.py` LL(1) Logic

The parser uses a stack. It does not read characters. It reads token types from the lexer.

Source: `Backend/parser/parser.py:614-715`

Code:
```python
    def parse(self, tokens: Sequence[Any]) -> Tuple[bool, List[str]]:
        toks = [_as_tok(t) for t in tokens]
        toks = [_TokView(self._normalize_token_type(t.type), t.value, t.line, t.col) for t in toks]
        toks = self._ensure_eof(toks)

        self._current_tokens = toks

        stack: List[str] = [self.end_marker, self.start_symbol]
        index = 0
        
        current_var_type: Optional[str] = None
        expecting_value_for_type: Optional[str] = None

        reclaim_seen_stack: List[bool] = []

        def current_token() -> _TokView:
            nonlocal index
            if index >= len(toks):
                last_line = toks[-1].line if toks else 1
                last_col = toks[-1].col if toks else 0
                return _TokView(self.end_marker, self.end_marker, last_line, last_col)
            return toks[index]

        while stack:
            top = stack[-1]
            tok = current_token()
            token_type = tok.type
            token_value = tok.value
            line = tok.line or 1

            if token_type in self.skip_token_types and top != token_type:
                index += 1
                continue

            if top in self.parsing_table:
                row = self.parsing_table[top]
                if token_type in row:
                    production = row[token_type]
                    
                    if top == '<statement>' and token_type != '}' and reclaim_seen_stack and reclaim_seen_stack[-1]:
                        return False, [f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}' after 'reclaim'. Expected: '}}'."]

                    if top == '<statement>' and token_type == '}':
                        is_epsilon = (len(production) == 0 or (len(production) == 1 and production[0] in self.epsilon_symbols))
                        if is_epsilon:
                            lookback = index - 1
                            while lookback >= 0 and toks[lookback].type in self.skip_token_types:
                                lookback -= 1
                            
                            if lookback >= 0 and toks[lookback].type == '{':
                                before_brace = lookback - 1
                                while before_brace >= 0 and toks[before_brace].type in self.skip_token_types:
                                    before_brace -= 1
                                
                                if before_brace >= 0 and toks[before_brace].type == ')':
                                    paren_depth = 1
                                    paren_pos = before_brace - 1
                                    while paren_pos >= 0 and paren_depth > 0:
                                        if toks[paren_pos].type == ')':
                                            paren_depth += 1
                                        elif toks[paren_pos].type == '(':
                                            paren_depth -= 1
                                        paren_pos -= 1
                                    
                                    if paren_pos >= 0:
                                        kw_pos = paren_pos
                                        while kw_pos >= 0 and toks[kw_pos].type in self.skip_token_types:
                                            kw_pos -= 1
                                        
                                        if kw_pos >= 0:
                                            kw = toks[kw_pos]
                                            conditional_keywords = {'spring', 'bud', 'wither', 'grow', 'cultivate', 'tend', 'harvest'}
                                            if kw.type in conditional_keywords:
                                                return False, [f"SYNTAX error line {line} col {tok.col} Empty block after '{kw.value}' statement - at least one statement required"]
                                
                                elif before_brace >= 0 and toks[before_brace].type in {'wither', 'tend'}:
                                    kw = toks[before_brace]
                                    return False, [f"SYNTAX error line {line} col {tok.col} Empty block after '{kw.value}' statement - at least one statement required"]
                    
                    stack.pop()

                    if not (
                        len(production) == 0
                        or (len(production) == 1 and production[0] in self.epsilon_symbols)
                    ):
                        stack.extend(reversed(production))
                    continue

                expected = set(row.keys())
                
                if token_type in {'variety', 'soil'} and token_type not in expected:
                    while index < len(toks) and toks[index].type != ';':
                        if toks[index].type == 'prune':
                            index += 1
                            break
                        index += 1
                    if index < len(toks) and toks[index].type == ';':
                        index += 1
                    continue

                error_msg = self._generate_helpful_error(top, token_type, token_value, line, tok.col, expected, index, toks)
                return False, [error_msg]
```

Concrete logic:

| Variable | Meaning |
|---|---|
| `toks` | Normalized token list. Every token has `type`, `value`, `line`, and `col`. |
| `stack` | Parser work list. Starts with `EOF` and `<program>`. |
| `index` | Current position in the token list. |
| `current_token()` | Helper that returns the next non-skipped token. |
| `top` | Top symbol of the parser stack. Can be a terminal or nonterminal. |
| `token_type` | Current lookahead token type. |
| `row = self.parsing_table.get(top)` | Gets possible productions for the current nonterminal. |
| `production = row.get(token_type)` | Chooses the grammar production using the lookahead token. |

Decision logic:

| Situation | Parser Action |
|---|---|
| `top` is a nonterminal and PREDICT has a production | Pop `top`, push the selected production in reverse. |
| `top` is a terminal and matches current token | Pop terminal and move `index` to the next token. |
| No production exists for lookahead | Return syntax error. |
| Terminal does not match current token | Return syntax error. |

Example:

```text
Stack top: <program>
Current token: root
Parser checks parsing_table["<program>"]["root"]
It finds the <program> production and pushes its symbols onto the stack.
```

Defense sentence:

```text
The parser is table-driven. The current token does not directly call a function. Instead, the parser uses stack top plus lookahead token to find the correct grammar production in the parsing table.
```

### E.4 `Backend/parser/builder.py` AST Build Logic

After the LL(1) parser accepts the token order, the builder reads the same tokens again to create AST nodes and perform many semantic checks.

Source: `Backend/parser/builder.py:21-32`

Code:
```python
def build_ast(tokens):
    root = ProgramNode()
    symbol_table.variables = {}
    symbol_table.functions = {}
    symbol_table.scopes = [{}] 
    symbol_table.function_variables = {}
    symbol_table.bundle_types = {}
    context_stack = []
    index = 0
    symbol_table.current_func_name = None
    
    while index < len(tokens):
```

Source: `Backend/parser/builder.py:39-108`

Code:
```python
        if tokens[index].value in {"seed", "tree", "vine", "leaf", "branch"}:
            id_type = token.value
            index += 1
            if tokens[index].type != "id":
                raise SemanticError(f"Semantic Error: Invalid variable declaration.", token.line)
            id_name = tokens[index].value
            index += 1
            node, index = parse_variable(tokens, index, id_name, id_type) 

            if node:
                root.add_child(node)

        elif tokens[index].value == "empty":
            index += 1
            if tokens[index].type == "id":
                func_name = tokens[index].value
                func_type = "empty"
                node, index = parse_function(tokens, index, func_name, func_type)
            else:
                raise SemanticError(f"Semantic Error: Invalid function declaration.", tokens[index].line)
            
            if node:
                root.add_child(node)
            
        elif tokens[index].value in {"pollinate"}:
            index += 1
            if tokens[index].value in {"seed", "tree", "vine", "leaf", "branch", "empty"}:
                id_type = tokens[index].value
                index += 1
                if tokens[index].type != "id":
                    raise SemanticError(f"Semantic Error: Invalid function declaration.", tokens[index].line)
                id_name = tokens[index].value
                index += 1
                node, index = parse_function(tokens, index, id_name, id_type)

                if node:
                    root.add_child(node)

            elif tokens[index].type == "id" and tokens[index].value in symbol_table.bundle_types:
                id_type = tokens[index].value
                index += 1
                if tokens[index].type != "id":
                    raise SemanticError(f"Semantic Error: Invalid function declaration.", tokens[index].line)
                id_name = tokens[index].value
                index += 1
                node, index = parse_function(tokens, index, id_name, id_type)

                if node:
                    root.add_child(node)

            else: 
                raise SemanticError(f"Semantic Error: Expected data type for function declaration after 'pollinate'.", tokens[index].line)

        elif token.value == "fertile":
            node, index = parse_fertile(tokens, index)
            if node:
                root.add_child(node)

        elif token.value == "identifier":
            if isinstance(symbol_table.lookup_variable(token.value), str):
                raise SemanticError(f"Semantic Error: Variable '{token.value}' used before declaration.", token.line)
            raise SemanticError(f"Semantic Error: Invalid global statement.", token.line)

        elif token.value in {"root"}:
            func_name = token.value
            func_type = "empty"
            node, index = parse_function(tokens, index, func_name, func_type)

            if node:
                root.add_child(node)
```

Concrete logic:

| Code Part | What It Means |
|---|---|
| `build_ast(tokens)` | Entry point called by `parse_and_build()`. |
| `parser = Parser(tokens)` | Creates a builder parser object that will walk through tokens. |
| `ast = parser.parse_program()` | Starts building the AST from the program level. |
| `symbol_table` | Stores declarations discovered while building. |
| `parse_program()` | Looks at top-level tokens and decides if each part is a variable, constant, bundle, function, or root. |

Important difference from the LL(1) parser:

```text
LL(1) parser checks if token order is allowed by CFG.
Builder creates meaning: declarations, assignments, function nodes, bundle nodes, and output/input nodes.
```

### E.5 `parse_statement()` Routing Logic

`parse_statement()` is the builder's dispatcher for statements inside functions and root.

Source: `Backend/parser/builder.py:442-520`

Code:
```python
def parse_statement(tokens, index, func_type = None):
    token = tokens[index]

    if token.type == ";":
        return None, index + 1

    line = token.line

    if token.value in {"seed", "tree", "vine", "leaf", "branch"}:
        var_type = token.value
        var_name = tokens[index + 1].value
        index += 2

        node, index = parse_variable(tokens, index, var_name, var_type)
        return node, index
    
    
    elif token.value == "fertile":
        node, index = parse_fertile(tokens, index)
        return node, index

    elif token.value == "bundle":
        bundle_type_name = tokens[index + 1].value
        if bundle_type_name not in symbol_table.bundle_types:
            raise SemanticError(f"Semantic Error: Bundle type '{bundle_type_name}' is not defined.", token.line)
        var_name = tokens[index + 2].value
        index += 3

        members = symbol_table.bundle_types[bundle_type_name]
        _defaults = {"seed": 0, "tree": 0.0, "leaf": '', "vine": "", "branch": False}

        if tokens[index].type == "[":
            index += 1
            if tokens[index].type == "dblit":
                raise SemanticError(f"Semantic Error: Array size must be of type 'seed' (integer), got 'tree' (float) '{tokens[index].value}'.", token.line)
            array_size = 0
            if tokens[index].type == "intlit":
                array_size = int(tokens[index].value)
                index += 1
            if tokens[index].type != "]":
                raise SemanticError(f"Syntax Error: Expected ']' after array size.", token.line)
            index += 1

            list_node = ASTNode("List", line=token.line)
            for _ in range(array_size):
                bundle_val_node = ASTNode("BundleDefault", line=token.line)
                list_node.add_child(bundle_val_node)

            error = symbol_table.declare_variable(var_name, bundle_type_name, is_list=True)
            if isinstance(error, str):
                raise SemanticError(error, token.line)

            node = VariableDeclarationNode(bundle_type_name, var_name, line=token.line)
            node.add_child(list_node)
            return node, index
        else:
            bundle_value = {name: _defaults.get(typ, None) for name, typ in members.items()}

            error = symbol_table.declare_variable(var_name, bundle_type_name, value=bundle_value)
            if isinstance(error, str):
                raise SemanticError(error, token.line)

            node = VariableDeclarationNode(bundle_type_name, var_name, line=token.line)
            return node, index

    elif token.type == "id" and tokens[index + 1].type == "(":
        if tokens[index + 1].type == "(":
            func_name = token.value
            error = symbol_table.lookup_function(func_name)
            if isinstance(error, str):
                error = symbol_table.lookup_function(func_name)
                raise SemanticError(error, token.line)
            func_type = symbol_table.lookup_function(func_name)["return_type"]  # type: ignore
            func_params = symbol_table.lookup_function(func_name)["params"]  # type: ignore
            func_call_node, index = parse_function_call(tokens, index, func_name, func_type, func_params)
            return func_call_node, index
        
    elif token.type == "id" or tokens[index].type in {"++", "--"}: 
        assignments_node = ASTNode("AssignmentList")
```

Concrete logic:

| Token Seen | Builder Decision |
|---|---|
| data type like `seed`, `tree`, `vine` | Parse a variable declaration. |
| `fertile` | Parse a constant declaration. |
| `id` | Could be assignment, function call, array access, member access, increment, or list operation. |
| `plant` | Parse output statement. |
| `water` | Parse input statement. |
| `spring` | Parse conditional statement. |
| `cultivate`, `grow`, `tend` | Parse loop statement. |
| `harvest` | Parse switch-like statement. |
| `reclaim` | Parse return statement. |

The function is called repeatedly while building a block. Each successful parse returns:

```text
(node, new_index)
```

`node` is the AST node that represents the statement. `new_index` tells the builder where to continue reading tokens.

### E.6 `parse_variable()` Declaration Logic

This function handles declarations such as `seed x = 10;`, `tree y;`, `vine name = "GAL";`, and arrays.

Source: `Backend/parser/builder.py:310-390`

Code:
```python
def parse_variable(tokens, index, var_name, var_type):
    line = tokens[index].line
    var_nodes = []

    while True:
        global_var = symbol_table.variables.get(var_name)
        if global_var and global_var.get("is_fertile"):
            raise SemanticError(f"Semantic Error: Variable '{var_name}' is declared as fertile and cannot be re-declared.", line)

        is_list = False

        var_node = VariableDeclarationNode(var_type, var_name, line=line)

        if tokens[index].type == "=":
            index += 1

            if tokens[index].type == "[":
                is_list = True
                value_node, index = parse_list(tokens, index, var_type)
                var_node.add_child(value_node)

            elif tokens[index].value == "water":
                water_line = tokens[index].line
                index += 1
                if tokens[index].type != "(":
                    raise SemanticError(f"Semantic Error: Expected '(' after water.", water_line)
                index += 1
                water_type = None
                if tokens[index].value in {"seed", "tree", "leaf", "branch", "vine"}:
                    water_type = tokens[index].value
                    index += 1
                if tokens[index].type != ")":
                    raise SemanticError(f"Semantic Error: water() accepts only an optional type parameter (e.g., water(seed)).", water_line)
                index += 1
                if water_type and not _types_compatible(var_type, water_type):
                    raise SemanticError(f"Semantic Error: Type mismatch — cannot assign water({water_type}) to '{var_type}' variable.", water_line)
                value_node = ASTNode("Input", f"water({water_type})" if water_type else "water()", line=water_line)
                var_node.add_child(value_node)

            else:
                value_node, index = parse_expression_type(tokens, index, var_type)
                var_node.add_child(value_node)

        elif tokens[index].type == "[":
            is_list = True
            dimensions = []
            while tokens[index].type == "[":
                index += 1
                dim_size = 0
                if tokens[index].type == "dblit":
                    raise SemanticError(f"Semantic Error: Array size must be of type 'seed' (integer), got 'tree' (float) '{tokens[index].value}'.", line)
                if tokens[index].type == "intlit":
                    dim_size = int(tokens[index].value)
                    index += 1
                if tokens[index].type != "]":
                    raise SemanticError(f"Syntax Error: Expected ']' after list size.", line)
                index += 1
                dimensions.append(dim_size)

            default_literals = {"seed": "0", "tree": "0.0", "leaf": "''", "vine": '""', "branch": "false"}

            def build_list_node(dims):
                node = ASTNode("List", line=line)
                if len(dims) == 1:
                    for _ in range(dims[0]):
                        node.add_child(ASTNode("Value", default_literals.get(var_type, "0"), line=line))
                else:
                    for _ in range(dims[0]):
                        node.add_child(build_list_node(dims[1:]))
                return node

            list_node = build_list_node(dimensions)
            var_node.add_child(list_node)

            if tokens[index].type == "=":
                index += 1
                if tokens[index].type == "{":
                    def parse_init_braces(idx):
                        if tokens[idx].type != "{":
                            raise SemanticError(f"Syntax Error: Expected '{{' in array initialization.", tokens[idx].line)
                        idx += 1
```

Concrete logic:

| Step | Logic |
|---:|---|
| 1 | Read the declared type, such as `seed`. |
| 2 | Read the identifier name, such as `x`. |
| 3 | Check if the name conflicts with an existing function or variable. |
| 4 | If `[` appears, parse array dimension and reject invalid double sizes. |
| 5 | If `=` appears, parse initializer expression or initializer list. |
| 6 | Infer initializer type and compare it to declared type. |
| 7 | Store the variable in the symbol table. |
| 8 | Return a `VariableDeclarationNode`. |

This is why this code catches duplicate identifiers and type mismatch during building, before runtime.

### E.7 `parse_factor()` Expression Atom Logic

`parse_factor()` handles the smallest parts of expressions: literals, identifiers, grouped expressions, function calls, list access, and member access.

Source: `Backend/parser/builder.py:1352-1438`

Code:
```python
def parse_factor(tokens, index):
    token = tokens[index]

    if token.type == "(" and tokens[index + 1].value in {"seed", "tree", "leaf", "branch", "vine"}:
        node, index, cast_type = parse_cast(tokens, index)
        return node, index, cast_type

    if token.type == "(":
        index += 1
        node, index, inner_type = parse_expression_branch(tokens, index)
        if tokens[index].type != ")":
            raise SemanticError("Syntax Error: Missing closing parenthesis.", token.line)
        index += 1  
        return node, index, inner_type
    
    if token.type in {"intlit", "dblit", "chrlit", "stringlit", "sunshine", "frost"}:
        node = ASTNode("Value", token.value)
        index += 1
        return node, index, infer_literal_type(token.type)

    if token.value == "water":
        raise SemanticError(f"Semantic Error: water() is an I/O statement, not an expression. It cannot be used inside an expression.", token.line)

    if token.type == "id" and tokens[index + 1].type == "(":
        func_name = token.value
        func_info = symbol_table.lookup_function(func_name)
        if isinstance(func_info, str):
            raise SemanticError(f"Semantic Error: Function '{func_name}' is not declared.", token.line)
        func_return_type = func_info["return_type"]
        func_params = func_info["params"]
        node, index = parse_function_call(tokens, index, func_name, func_return_type, func_params)

        return node, index, func_return_type

    elif (
        tokens[index].type == "id" and
        tokens[index + 1].type == "." and
        tokens[index + 2].value in ("wilt", "bloom")
    ):
        func_name = tokens[index + 2].value
        identifier = tokens[index].value

        identifier_info = symbol_table.lookup_variable(identifier)
        if isinstance(identifier_info, str):
            raise SemanticError(f"Semantic Error: Variable '{identifier}' used before declaration.", token.line)

        if identifier_info["type"] != "vine":
            raise SemanticError(f"Semantic Error: {func_name}() can only be used on vine (string) variables, but '{identifier}' is of type {identifier_info['type']}.", token.line)

        index += 3

        if func_name == "wilt":
            node = SoilNode(identifier, line=token.line)
        else:
            node = BloomNode(identifier, line=token.line)
        return node, index, "vine"

    elif (
        tokens[index].type == "id" and
        tokens[index + 1].type == "."
    ):
        obj_name = tokens[index].value
        member_name = tokens[index + 2].value

        var_info = symbol_table.lookup_variable(obj_name)
        if isinstance(var_info, str):
            raise SemanticError(f"Semantic Error: Variable '{obj_name}' used before declaration.", token.line)

        var_type = var_info["type"]
        if var_type not in symbol_table.bundle_types:
            raise SemanticError(f"Semantic Error: Variable '{obj_name}' is not a bundle type.", token.line)

        bundle_members = symbol_table.bundle_types[var_type]
        if member_name not in bundle_members:
            raise SemanticError(f"Semantic Error: Bundle type '{var_type}' has no member '{member_name}'.", token.line)

        member_type = bundle_members[member_name]
        index += 3
        node = MemberAccessNode(obj_name, member_name, line=token.line)

        while index < len(tokens) and tokens[index].type == "." and member_type in symbol_table.bundle_types:
            next_member = tokens[index + 1].value
            nested_members = symbol_table.bundle_types[member_type]
            if next_member not in nested_members:
                raise SemanticError(f"Semantic Error: Bundle type '{member_type}' has no member '{next_member}'.", token.line)
            member_type = nested_members[next_member]
            node = MemberAccessNode(node, next_member, line=token.line)
```

Concrete logic:

| Token Pattern | Meaning |
|---|---|
| `(` expression `)` | Parenthesized expression. |
| `intlit`, `dblit`, `chrlit`, `stringlit`, `sunshine`, `frost` | Literal value. |
| `id (` | Function call. |
| `id . wilt` or `id . bloom` | Supported vine member operation. |
| `id . id` | Bundle member access, only valid if the left identifier has bundle type. |
| `id [` | Array or vine indexing. |
| plain `id` | Variable value. |

Because `ts` and `taper` were removed, `arr.ts` and `c.taper` no longer have hidden special handling. They fall into the normal `id . id` member-access path and fail unless the left side is a real bundle with that member.

### E.8 `Backend/semantic/symbol_table.py` Logic

The symbol table is the compiler's memory during semantic checking. It remembers what names exist and what they mean.

Source: `Backend/semantic/symbol_table.py:13-58`

Code:
```python
    def declare_variable(self, name, type_, value=None, is_list=False, is_fertile=False):
        scope = self.scopes[-1]
        current_func = self.current_func_name
    

        if name in self.functions:
            return f"Semantic Error: Variable '{name}' already declared as a function."

        if current_func:
            if current_func not in self.function_variables:
                self.function_variables[current_func] = set()

            if name in self.function_variables[current_func]:
                return f"Semantic Error: Variable '{name}' already declared in this function."

            self.function_variables[current_func].add(name)

        if self.current_func_name:
            
            scope[name] = {
                "type": type_,  
                "value": value,
                "is_list": is_list,
                "is_fertile": is_fertile
            }
        else:
            if name in self.global_variables:
                return f"Semantic Error: Variable '{name}' already declared."
            
            self.variables[name] = {
                "type": type_,
                "value": value,
                "is_list": is_list,
                "is_fertile": is_fertile
            }
        

    def lookup_variable(self, name):
        for i, scope in enumerate(reversed(self.scopes)):
            if name in scope:
                return scope[name]
        
        if name in self.variables:
            return self.variables[name]

        return f"Semantic Error: Variable '{name}' used before declaration."
```

Concrete logic:

| Function | Purpose |
|---|---|
| `declare_variable()` | Adds a variable to the current scope or global scope. |
| `lookup_variable()` | Searches current local scopes first, then global variables. |
| duplicate checks | Prevent declaring the same variable/function name in invalid places. |
| `is_list` | Records whether the variable is an array/list. |
| `is_fertile` | Records whether the variable is constant and cannot be reassigned. |

Defense sentence:

```text
The symbol table is how the compiler knows if an identifier was declared before use. Without it, the parser could accept the grammar but the compiler would not know whether a variable actually exists.
```

### E.9 `Backend/semantic/analyzer.py` Logic

The semantic analyzer walks the AST after the builder has created it.

Source: `Backend/semantic/analyzer.py:4-35`

Code:
```python
class ASTValidator:

    def __init__(self):
        self.errors = []
        self.warnings = []
        self._in_loop = 0
        self._in_switch = 0
        self._in_function = False
        self._current_func_type = None


    def validate(self, ast, symbol_table_data):
        self._walk(ast)
        return {
            "success": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "symbol_table": symbol_table_data,
            "ast": ast,
        }


    def _walk(self, node):
        if node is None:
            return
        handler = getattr(self, f'_check_{node.node_type}', None)
        if handler:
            handler(node)
        else:
            for child in getattr(node, 'children', []):
                self._walk(child)

```

Source: `Backend/semantic/analyzer.py:133-141`

Code:
```python
    def _check_Break(self, node):
        if self._in_loop == 0 and self._in_switch == 0:
            self.errors.append(
                f"SEMANTIC error line {node.line}: 'prune' used outside a loop or switch.")

    def _check_Continue(self, node):
        if self._in_loop == 0:
            self.errors.append(
                f"SEMANTIC error line {node.line}: 'skip' used outside a loop.")
```

Concrete logic:

| Code Part | Meaning |
|---|---|
| `validate(ast, symbol_table_data)` | Starts semantic validation. |
| `self._walk(ast)` | Recursively visits every AST node. |
| `getattr(self, f'_check_{node.node_type}', None)` | Dynamically finds a checker method based on node type. |
| `_check_Break()` | Ensures `prune` is inside a loop or harvest/switch. |
| `_check_Continue()` | Ensures `skip` is inside a loop. |

This file is a second semantic safety pass. The builder catches many type/declaration errors. The analyzer catches AST-level rules such as invalid control-flow usage.

### E.10 `Backend/interpreter/interpreter.py` Runtime Logic

The interpreter executes the AST. It no longer checks grammar. It performs actions.

Source: `Backend/interpreter/interpreter.py:121-212`

Code:
```python
    def interpret(self, node):
        if isinstance(node, ProgramNode):
            return self.eval_program(node)
        elif isinstance(node, BundleDefinitionNode):
            return self.eval_bundle_definition(node)
        elif isinstance(node, MemberAccessNode):
            return self.eval_member_access(node)
        elif isinstance(node, ArrayMemberAccessNode):
            return self.eval_array_member_access(node)
        elif isinstance(node, VariableDeclarationNode):
            return self.eval_variable_declaration(node)
        elif isinstance(node, AssignmentNode):
            return self.eval_assignment(node)
        elif isinstance(node, BinaryOpNode):
            value = self.eval_binary_op(node)
            if isinstance(value, (int, float)):
                if value > 1000000000000000 or value < -9999999999999999:
                    raise InterpreterError(f"Runtime Error: Evaluated number exceeds maximum number of 16 digits", node.line)
            return value
        elif isinstance(node, FunctionDeclarationNode):
            return self.eval_function_declaration(node)
        elif isinstance(node, PrintNode):
            return self.eval_print(node)
        elif isinstance(node, ListNode):
            return self.eval_list(node)
        elif isinstance(node, ListAccessNode):
            return self.eval_list_access(node)
        elif isinstance(node, ReturnNode):
            return self.eval_return(node)
        elif isinstance(node, FunctionCallNode):
            return self.eval_function_call(node)
        elif isinstance(node, AppendNode):
            return self.eval_append(node)
        elif isinstance(node, InsertNode):
            return self.eval_insert(node)
        elif isinstance(node, RemoveNode):
            return self.eval_remove(node)
        elif isinstance(node, UnaryOpNode):
            return self.eval_unaryop(node)
        elif isinstance(node, FertileDeclarationNode):
            return self.eval_sturdy_declaration(node)
        elif isinstance(node, CastNode):
            return self.eval_cast(node)
        elif isinstance(node, SoilNode):
            return self.eval_soil(node)
        elif isinstance(node, BloomNode):
            return self.eval_bloom(node)
        elif isinstance(node, IfStatementNode):
            return self.eval_if_statement(node)
        elif isinstance(node, ForLoopNode):
            return self.eval_for_loop(node)
        elif isinstance(node, WhileLoopNode):
            return self.eval_while_loop(node)
        elif isinstance(node, DoWhileLoopNode):
            return self.eval_do_while_loop(node)
        elif isinstance(node, BreakNode):
            return self.eval_break(node)
        elif isinstance(node, ContinueNode):
            return self.eval_continue(node)
        elif isinstance(node, SwitchNode):
            return self.eval_switch(node)
        elif node.node_type == "Input":
            return self.eval_input(node)
        elif node.node_type == "Value":
            value = self._parse_literal(node.value)
            return value
        elif node.node_type == "Identifier":
            var_info = self.lookup_variable(node.value)
            if isinstance(var_info, str):
                raise InterpreterError(var_info, node.line)
            return var_info["value"]
        elif node.node_type == "FormattedString":
            return self.eval_formatted_string(node)
        elif node.node_type == "VariableDeclarationList":
            for child in node.children:
                self.eval_variable_declaration(child)
        elif node.node_type == "AssignmentList":
            for child in node.children:
                if isinstance(child, AssignmentNode):
                    self.eval_assignment(child)
                elif isinstance(child, UnaryOpNode):
                    self.eval_unaryop(child)
        elif node.node_type == "List":
            return [self.interpret(child) for child in node.children]
        elif node.node_type == "Block":
            self.eval_block(node)
        else:
            raise Exception(f"Unknown AST node type: {node.node_type}")

    def eval_program(self, node):
        for child in node.children:
            self.interpret(child)
```

Concrete logic:

| Code Part | Meaning |
|---|---|
| `interpret(node)` | Main dispatcher for runtime execution. |
| `isinstance(node, ProgramNode)` | If the node is a program, run the program. |
| `VariableDeclarationNode` | Create runtime variable storage. |
| `AssignmentNode` | Update runtime variable value. |
| `PrintNode` | Execute `plant()`. |
| `InputNode` | Execute `water()`. |
| `FunctionCallNode` | Call a function such as `root()`. |
| loop/if nodes | Execute control flow. |

Defense sentence:

```text
The interpreter is a dispatcher. It receives an AST node, checks what kind of node it is, then calls the matching eval method.
```

### E.11 Runtime Variables, Assignment, and Expressions

Source: `Backend/interpreter/interpreter.py:50-92`

Code:
```python
    def declare_variable(self, name, type_, value=None, is_list=False, is_fertile=False):
        scope = self.scopes[-1]
        current_func = self.current_func_name
    

        if name not in self.scopes[-1]:
            scope[name] = {
                "type": type_,  
                "value": value,
                "is_list": is_list,
                "is_fertile": is_fertile
                }
        else:
            if name in self.global_variables:
                return f"Semantic Error: Variable '{name}' already declared."
            
            self.variables[name] = {
                "type": type_,
                "value": value,
                "is_list": is_list,
                "is_fertile": is_fertile
            }
            self.global_variables[name] = self.variables[name]
        

    def lookup_variable(self, name):
        for i, scope in enumerate(reversed(self.scopes)):
            if name in scope:
                return scope[name]
        
        if name in self.variables:
            return self.variables[name]

        return f"Semantic Error: Variable '{name}' used before declaration."
    
    def set_variable(self, name, value):
        for i in reversed(range(len(self.scopes))):
            scope = self.scopes[i]
            if name in scope:
                scope[name]["value"] = value
                return  

        return f"Semantic Error: Variable '{name}' not declared in any scope."
```

Source: `Backend/interpreter/interpreter.py:346-430`

Code:
```python
    def eval_assignment(self, node):
        target_node = node.children[0]
        value_node = node.children[1]

        if value_node.node_type == "List":
            value = []
            for val in value_node.children:
                item = self.interpret(val)
                value.append(item)
        else:
            value = self.interpret(value_node)
            if isinstance(value_node, AppendNode) or isinstance(value_node, InsertNode) or isinstance(value_node, RemoveNode):
                return

        if target_node.node_type == "ListAccess":
            indices = []
            current = target_node
            while hasattr(current, 'node_type') and current.node_type == "ListAccess":
                idx = self.interpret(current.children[1].children[0])
                if not isinstance(idx, int):
                    raise InterpreterError(f"Runtime Error: List index must be an integer. Got '{idx}'", node.line)
                indices.append(idx)
                current = current.children[0].value

            list_name = current
            list_entry = self.lookup_variable(list_name)
            if isinstance(list_entry, str):
                raise InterpreterError(list_entry, node.line)

            list_value = list_entry["value"]
            if not isinstance(list_value, (list, str)):
                raise InterpreterError(f"Runtime Error: Variable '{list_name}' is not a list.", node.line)

            if isinstance(list_value, str):
                if len(indices) != 1:
                    raise InterpreterError(f"Runtime Error: Multi-dimensional indexing not supported for strings.", node.line)
                final_idx = indices[0]
                if final_idx < 0 or final_idx >= len(list_value):
                    raise InterpreterError(f"Runtime Error: Index '{final_idx}' out of bounds for '{list_name}'.", node.line)
                if not isinstance(value, str) or len(value) != 1:
                    raise InterpreterError(f"Runtime Error: Can only assign a single character to a string index.", node.line)
                list_value = list_value[:final_idx] + value + list_value[final_idx + 1:]
                list_entry["value"] = list_value
            else:
                indices.reverse()

                target = list_value
                for i, idx in enumerate(indices[:-1]):
                    if idx < 0 or idx >= len(target):
                        raise InterpreterError(f"Runtime Error: Index '{idx}' out of bounds for list '{list_name}'.", node.line)
                    target = target[idx]
                    if not isinstance(target, list):
                        raise InterpreterError(f"Runtime Error: Cannot index into a non-list value.", node.line)

                final_idx = indices[-1]
                if final_idx < 0 or final_idx >= len(target):
                    raise InterpreterError(f"Runtime Error: Index '{final_idx}' out of bounds for list '{list_name}'.", node.line)

                target[final_idx] = value

        elif target_node.node_type == "MemberAccess":
            chain = []
            current = target_node
            while hasattr(current, 'node_type') and current.node_type == "MemberAccess":
                chain.append(current.children[1].value)
                current = current.children[0]

            chain.reverse()

            if hasattr(current, 'node_type') and current.node_type == "ArrayMemberAccess":
                bundle_value = self.interpret(current)
                if not isinstance(bundle_value, dict):
                    raise InterpreterError(f"Runtime Error: Value is not a bundle.", node.line)
            else:
                obj_name = current.value
                var_info = self.lookup_variable(obj_name)
                if isinstance(var_info, str):
                    raise InterpreterError(var_info, node.line)
                bundle_value = var_info["value"]
                if not isinstance(bundle_value, dict):
                    raise InterpreterError(f"Runtime Error: Variable '{obj_name}' is not a bundle.", node.line)

            for member in chain[:-1]:
                if member not in bundle_value:
                    raise InterpreterError(f"Runtime Error: Bundle has no member '{member}'.", node.line)
```

Source: `Backend/interpreter/interpreter.py:510-585`

Code:
```python
    def eval_binary_op(self, node):
        left = self.interpret(node.children[0])
        right = self.interpret(node.children[1])
        operator = node.value

        if operator == '`':
            result = str(left) + str(right)
            return result

        left = self._parse_literal(left)
        right = self._parse_literal(right)

        if operator == '+' and (isinstance(left, str) or isinstance(right, str)):
            result = str(left) + str(right)
            return result

        try:
            if operator == '+':
                if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):
                    if isinstance(left, bool):
                        left = 1 if left == True else 0
                    elif isinstance(left, str):
                        left = 1 if left != "" else 0
                    if isinstance(right, bool):
                        right = 1 if right == True else 0
                    elif isinstance(right, str):
                        right = 1 if right != "" else 0
                return left + right  # type: ignore[operator]
            
            elif operator == '-':
                if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):
                    if isinstance(left, bool):
                        left = 1 if left == True else 0
                    elif isinstance(left, str):
                        left = 1 if left != "" else 0
                    if isinstance(right, bool):
                        right = 1 if right == True else 0
                    elif isinstance(right, str):
                        right = 1 if right != "" else 0

                return left - right  # type: ignore[operator]
            elif operator == '*':
                if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):
                    if isinstance(left, bool):
                        left = 1 if left == True else 0
                    elif isinstance(left, str):
                        left = 1 if left != "" else 0
                    if isinstance(right, bool):
                        right = 1 if right == True else 0
                    elif isinstance(right, str):
                        right = 1 if right != "" else 0
                return left * right  # type: ignore[operator]
            elif operator == '**':
                if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):
                    if isinstance(left, bool):
                        left = 1 if left == True else 0
                    elif isinstance(left, str):
                        left = 1 if left != "" else 0
                    if isinstance(right, bool):
                        right = 1 if right == True else 0
                    elif isinstance(right, str):
                        right = 1 if right != "" else 0
                return left ** right  # type: ignore[operator]
            elif operator == '/':
                if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):
                    if isinstance(left, bool):
                        left = 1 if left == True else 0
                    elif isinstance(left, str):
                        left = 1 if left != "" else 0
                    if isinstance(right, bool):
                        right = 1 if right == True else 0
                    elif isinstance(right, str):
                        right = 1 if right != "" else 0
                if right == 0:
                    raise InterpreterError("Runtime Error: Division by zero is undefined", node.line)
                return left / right  # type: ignore[operator]
```

Concrete runtime flow:

| Runtime Action | Function | Logic |
|---|---|---|
| Declare variable | `declare_variable()` | Store name, type, value, list flag, and fertile flag in current scope. |
| Read variable | `lookup_variable()` | Search local scopes from newest to oldest, then global variables. |
| Assign variable | `eval_assignment()` | Evaluate right side, convert/check value, then update target variable. |
| Evaluate expression | `eval_binary_op()` | Evaluate left and right nodes, then apply operator such as `+`, `*`, `==`, `&&`, or backtick. |

Example:

```gal
sum = x + y;
```

Runtime logic:

```text
1. eval_assignment() receives AssignmentNode.
2. It interprets the right side BinaryOpNode.
3. eval_binary_op() looks up x and y.
4. It computes x + y.
5. eval_assignment() stores the result into sum.
```

### E.12 Function Call and Reclaim Logic

Source: `Backend/interpreter/interpreter.py:856-899`

Code:
```python
    def eval_function_call(self, node):
        function_name = node.value
        args = [self.interpret(arg.children[0]) for arg in node.children]

        func_info = self.lookup_function(function_name)
        if isinstance(func_info, str):
            raise InterpreterError(func_info, node.line)

        expected_params = func_info["params"]
        function_node = func_info["node"]

        if len(expected_params) != len(args):
            raise InterpreterError(
                f"Runtime Error: Function '{function_name}' expects {len(expected_params)} argument(s), got {len(args)}.",
                node.line
            )
        
        self.enter_scope()
        
        try:
            for i, param in enumerate(expected_params):
                param_name = param["name"]
                param_type = param["type"]
                arg_value = args[i]
                is_list = param.get("is_list", False)
                self.declare_variable(param_name, param_type, arg_value, is_list=is_list)

            try:
                self.eval_block(function_node.children[2])

            except ReturnValue as ret:
                return ret.value

            return None

        finally:
            self.exit_scope()
            self.current_func_name = None


    def eval_append(self, node):
        list_name = node.parent.children[0].value
        list_info = self.lookup_variable(list_name)

```

Concrete logic:

| Code Part | Meaning |
|---|---|
| `eval_function_call()` | Finds the function declaration at runtime. |
| argument binding | Evaluates arguments and stores them as parameter variables in a new scope. |
| `self.eval_block(...)` | Runs the function body statement by statement. |
| `ReturnValue` exception | Internal signal used by `reclaim` to stop the function body. |
| `finally: self.exit_scope()` | Ensures local variables are removed after the function ends. |

This is why `reclaim` can immediately stop a function even if there are more statements after it.

### E.13 `plant()` and `water()` Runtime Logic

Source: `Backend/interpreter/interpreter.py:752-804`

Code:
```python
    def eval_print(self, node):
        if not node.children:
            return

        first = node.children[0]

        evaluated_first = self.interpret(first)
        if isinstance(evaluated_first, float):
            whole, dot, dec = str(evaluated_first).partition('.')
            dec = dec[:5]
            evaluated_first = float(f"{whole}.{dec}")

        if isinstance(evaluated_first, str) and '{}' in evaluated_first:
            values = []
            for arg in node.children[1:]:
                value = self.interpret(arg)
                if isinstance(value, str) and not isinstance(self.lookup_variable(value), str):
                    value = self.lookup_variable(value)["value"]  # type: ignore[index]
                
                if isinstance(value, float):
                    whole, dot, dec = str(value).partition('.')
                    dec = dec[:5]
                    value = float(f"{whole}.{dec}")

                values.append(value)

            try:
                output_str = evaluated_first.format(*values)
            except Exception as e:
                raise Exception(f"Format error in plant(): '{evaluated_first}' with {values}: {e}")

            self.plant(output_str)
            return

        if len(node.children) > 1:
            parts = [str(evaluated_first)]
            for arg in node.children[1:]:
                value = self.interpret(arg)
                if isinstance(value, float):
                    whole, dot, dec = str(value).partition('.')
                    dec = dec[:5]
                    value = float(f"{whole}.{dec}")
                parts.append(str(value))
            self.plant(" ".join(parts))
            return

        self.plant(str(evaluated_first))

    def eval_formatted_string(self, node):
        value = node.value
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]

```

Source: `Backend/interpreter/interpreter.py:1348-1440`

Code:
```python
    def eval_input(self, node):
        parent_node = node.parent
        if isinstance(parent_node, VariableDeclarationNode):
            var_name = parent_node.children[1].value
            var_type = parent_node.children[0].value
        
        elif isinstance(parent_node, AssignmentNode):
            target = parent_node.children[0]
            if isinstance(target, ListAccessNode):
                current = target
                while hasattr(current, 'node_type') and current.node_type == "ListAccess":
                    current = current.children[0].value
                var_name = current if isinstance(current, str) else str(current)
                var_type = self.lookup_variable(var_name)["type"]  # type: ignore
            else:
                var_name = target.value
                var_type = self.lookup_variable(var_name)["type"]  # type: ignore

        else:
            var_name = "_input"
            if node.value and "(" in node.value:
                inner = node.value.split("(")[1].rstrip(")")
                var_type = inner if inner in {"seed", "tree", "leaf", "branch", "vine"} else "vine"
            else:
                var_type = "vine"

        prompt = f"Input for {var_name}: "
        self.input_required = True


        self.emit_input_request(var_name, prompt)

        input_value = self.wait_for_input(var_name)


        self.input_required = False

        if var_type == "seed":
            original_input = input_value
            if isinstance(input_value, str) and input_value.startswith('-'):
                raise InterpreterError(f"Runtime Error: GAL uses '~' for negative numbers, not '-'. Got '{original_input}'; did you mean '~{original_input[1:]}'?", node.line)  # type: ignore
            if isinstance(input_value, str) and input_value.startswith('~'):
                input_value = '-' + input_value[1:]
            try:
                if len(input_value.strip('-').lstrip('0')) > 16:
                    raise InterpreterError(f"Runtime Error: Input value exceeds maximum number of 16 digits", node.line)
                input_value = int(float(input_value))  # type: ignore
            except ValueError:
                raise InterpreterError(f"Runtime Error: Expected integer value, got '{original_input}'", node.line)

        elif var_type == "tree":
            original_input = input_value
            if isinstance(input_value, str) and input_value.startswith('-'):
                raise InterpreterError(f"Runtime Error: GAL uses '~' for negative numbers, not '-'. Got '{original_input}'; did you mean '~{original_input[1:]}'?", node.line)  # type: ignore
            if isinstance(input_value, str) and input_value.startswith('~'):
                input_value = '-' + input_value[1:]
            try:
                if '.' in input_value:  # type: ignore
                    integer_part, decimal_part = str(input_value).split('.')
                    if len(integer_part.strip('-').lstrip('0')) > 16:
                        raise InterpreterError(f"Runtime Error: Input value exceeds maximum number of 16 digits", node.line)
                    if len(decimal_part.rstrip('0')) > 5:
                        raise InterpreterError(f"Runtime Error: Input value exceeds maximum number of 5 decimal numbers", node.line)

                else:
                    if len(input_value.strip('-').lstrip('0')) > 16:
                        raise InterpreterError(f"Runtime Error: Input value exceeds maximum number of 16 digits", node.line)

                input_value = float(input_value)  # type: ignore


            except ValueError:
                raise InterpreterError(f"Runtime Error: Expected float value, got '{original_input}'", node.line)

        elif var_type == "branch":
            if input_value == "true" or input_value == "false":
                suggestion = "sunshine" if input_value == "true" else "frost"
                raise InterpreterError(f"Runtime Error: GAL uses 'sunshine' and 'frost' for booleans, not 'true'/'false'. Got '{input_value}'; did you mean '{suggestion}'?", node.line)
            if input_value == "sunshine":
                input_value = True
            elif input_value == "frost":
                input_value = False
            else:
                raise InterpreterError(f"Runtime Error: expected branch value (sunshine/frost), got '{input_value}'", node.line)
            
        elif var_type == "leaf":
            if len(input_value) != 1:  # type: ignore
                raise InterpreterError(f"Runtime Error: Expected a single character for leaf, got '{input_value}'", node.line)
            input_value = str(input_value)

        elif var_type == "vine":
            input_value = str(input_value)

```

Concrete logic:

| Feature | Runtime Function | Logic |
|---|---|---|
| `plant()` | `eval_print()` | Evaluates all print arguments and emits output text. |
| multiple plant arguments | `eval_print()` | Joins evaluated arguments with spaces. |
| `water()` | `eval_input()` | Requests input, waits for the frontend response, validates type, and stores converted value. |
| REST output | `OutputCollector.emit()` | Collects `output` events into a Python list. |
| Socket output | Socket.IO `emit()` | Sends live output/input events to the UI. |

This explains why output/errors are visible in the frontend output panel after execution.