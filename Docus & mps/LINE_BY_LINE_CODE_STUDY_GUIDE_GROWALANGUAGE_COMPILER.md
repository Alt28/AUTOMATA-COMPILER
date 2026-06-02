# Line-by-Line Code Study Guide of GrowALanguage Compiler

This file is a defense study guide. It explains the actual source code by exact file, line number, function, variable, and logic.

Project path: `C:\Users\clarence\Downloads\AUTOMATA-COMPILER-main (1)\AUTOMATA-COMPILER-main\my GAL code`

Generated: 2026-06-01 14:31

## How To Use This Guide

The compiler has very large files, especially `builder.py`, `parser.py`, and `interpreter.py`. So this guide explains the code line-by-line by important function or block. That means each section shows:

- exact source file and line numbers
- numbered source code snippet
- meaning of each important line or group of lines
- what input the code receives
- what output it returns
- what compiler stage depends on it

This is the best way to study the whole system without drowning in repeated helper lines.

## 0. Python Terms You Must Understand First

| Term | Meaning In Your Compiler |
|---|---|
| `self` | The current object. Example: inside `Lexer`, `self.current_char` means the current character owned by this lexer object. |
| `self.variable` | An instance variable. It keeps its value while the object is running. Example: `self.pos`, `self.source_code`, `self.current_char`. |
| `def function_name(...)` | Defines a function or method. Example: `def advance(self):` defines how the lexer moves forward. |
| `return` | Sends a result back to the caller. Example: `return tokens, errors`. |
| `list` | Ordered collection. Example: `tokens = []` stores generated token objects. |
| `dict` | Key-value collection. Example: `cfg` maps nonterminals to grammar productions. |
| `class` | Blueprint for objects. Example: `class Lexer:` creates lexer objects. |
| `append()` | Adds one item to the end of a list. Example: `tokens.append(Token(...))`. |
| `None` | Means no value. In the lexer, `current_char = None` means end of source code. |

Defense shortcut:

```text
`self.current_char` is not a random variable. It is the character currently being scanned by the Lexer object.
Every time `advance()` runs, the position moves forward and `self.current_char` changes to the next character.
```

## 1. Frontend To Backend Input Flow

### 1.1 Frontend Reads Editor Code

Source: `UI/main.js:1005-1035`

```javascript
1005:           window.runProgram = async function (options = {}) {
1006:             const silent = options.silent || false;
1007:             const sourceCode = editor.getValue();
1008: 
1009:             // Clear previous error highlights
1010:             if (window._clearErrorHighlights) window._clearErrorHighlights();
1011:             // Remove stale socket listeners
1012:             socket.removeAllListeners('execution_complete');
1013: 
1014:             // Populate the token table in the background (silent — no terminal writes)
1015:             await runLexer({ silent: true });
1016: 
1017:             // Reset status chips
1018:             const sl  = document.getElementById('status-lex');
1019:             const ss  = document.getElementById('status-syn');
1020:             const ssem = document.getElementById('status-sem');
1021:             const sexe = document.getElementById('status-exe');
1022:             if (sl)   { sl.classList.remove('ok','err');  sl.textContent = 'Lexical: —'; }
1023:             if (ss)   { ss.classList.remove('ok','err');  ss.textContent = 'Syntax: —'; }
1024:             if (ssem) { ssem.classList.remove('ok','err'); ssem.textContent = 'Semantic: —'; }
1025:             if (sexe) { sexe.classList.remove('ok','err'); sexe.textContent = 'Execution: —'; }
1026: 
1027:             // Check if program uses water() (needs interactive input via Socket.IO)
1028:             const needsInput = /\bwater\s*\(/.test(sourceCode);
1029: 
1030:             if (needsInput) {
1031:               runViaSocket(sourceCode, silent);
1032:             } else {
1033:               await runViaREST(sourceCode, silent);
1034:             }
1035:           };
```

| Lines | Meaning |
|---|---|
| 1005 | `window.runProgram` is the main frontend function for running code. |
| 1007 | `const sourceCode = editor.getValue();` gets the whole text from the Monaco editor. |
| 1010-1012 | Clears previous visual error highlights so old errors do not stay on screen. |
| 1014 | Runs the lexer silently to update the token table before execution. |
| 1026 | Checks if the code contains `water(...)`. This matters because `water()` needs interactive input. |
| 1028-1032 | If input is needed, use Socket.IO. Otherwise, use REST `/api/run`. |

### 1.2 Frontend Sends REST Request

Source: `UI/main.js:910-916`

```javascript
0910:           async function runViaREST(sourceCode, silent) {
0911:             try {
0912:               const resp = await fetch(`${API_BASE}/api/run`, {
0913:                 method: 'POST',
0914:                 headers: { 'Content-Type': 'application/json' },
0915:                 body: JSON.stringify({ source_code: sourceCode })
0916:               });
```

| Lines | Meaning |
|---|---|
| 910 | `runViaREST(sourceCode)` receives the full source program string. |
| 911 | Calls `fetch()` to send a POST request to `/api/run`. |
| 913 | Sends JSON, so Flask can read it with `request.get_json()`. |
| 915 | The key is `source_code`; the value is the full text from the editor. |

### 1.3 Backend Receives Source Code

Source: `Backend/server.py:323-384`

```python
0323: @app.route('/api/run', methods=['POST'])
0324: def run_endpoint():
0325:     try:
0326:         data = request.get_json()
0327:         if not data or 'source_code' not in data:
0328:             return jsonify({'error': 'Missing source_code in request body'}), 400
0329: 
0330:         source_code = data['source_code']
0331: 
0332:         tokens, lex_errors = lex(source_code)
0333:         if lex_errors:
0334:             return jsonify({
0335:                 'success': False,
0336:                 'stage': 'lexical',
0337:                 'output': [],
0338:                 'errors': lex_errors
0339:             })
0340: 
0341:         parse_result = parser.parse_and_build(tokens)
0342:         if not parse_result['success']:
0343:             error_stage = parse_result.get('error_stage', 'syntax')
0344:             return jsonify({
0345:                 'success': False,
0346:                 'stage': error_stage,
0347:                 'output': [],
0348:                 'errors': [str(e) for e in parse_result['errors']]
0349:             })
0350: 
0351:         semantic_result = validate_ast(parse_result['ast'], parse_result['symbol_table'])
0352:         if not semantic_result['success']:
0353:             return jsonify({
0354:                 'success': False,
0355:                 'stage': 'semantic',
0356:                 'output': [],
0357:                 'errors': [str(e) for e in semantic_result['errors']]
0358:             })
0359: 
0360:         ast = semantic_result['ast']
0361: 
0362:         collector = OutputCollector()
0363:         interp = Interpreter(socketio=collector)
0364:         try:
0365:             interp.interpret(ast)
0366:             return jsonify({
0367:                 'success': True,
0368:                 'stage': 'execution',
0369:                 'output': collector.outputs,
0370:                 'errors': []
0371:             })
0372:         except _InputNeeded:
0373:             return jsonify({
0374:                 'success': False,
0375:                 'stage': 'execution',
0376:                 'output': collector.outputs,
0377:                 'errors': ['Program requires interactive input (water())'],
0378:                 'needs_input': True
0379:             })
0380:         except InterpreterError as e:
0381:             collector.outputs.append(f'Runtime Error: {e}')
0382:             return jsonify({
0383:                 'success': False,
0384:                 'stage': 'execution',
```

| Lines | Meaning |
|---|---|
| 323 | `run_endpoint()` is the Flask route function for `/api/run`. |
| 325 | `data = request.get_json()` reads JSON sent by the frontend. |
| 326 | `source_code = data['source_code']` stores the whole program string in Python. |
| 340 | `tokens, lex_errors = lex(source_code)` sends the source to the lexer. |
| 341-344 | If lexer errors exist, the pipeline stops and returns lexical error JSON. |
| 348 | `parser.parse_and_build(tokens)` sends lexer tokens to the parser and AST builder. |
| 349-353 | If parsing fails, the pipeline stops and returns syntax/parse error JSON. |
| 359 | `validate_ast(ast)` performs semantic analysis after parsing succeeds. |
| 360-364 | If semantic errors exist, the pipeline stops and returns semantic error JSON. |
| 370-372 | Creates an `Interpreter` and executes the AST. |
| 377-384 | Returns final runtime output or runtime error to the frontend. |

## 2. Lexer Core: Character-by-Character Scanning

### 2.1 Lexer Initialization

Source: `Backend/lexer/scanner.py:18-27`

```python
0018: class Lexer:
0019:     def __init__(self, source_code): 
0020:         self.source_code = source_code.replace('\r', '')
0021:         self.pos = Position(-1, 1, -1)
0022:         self.current_char = None
0023:         self.advance()
0024: 
0025:     def advance(self):
0026:         self.pos.advance(self.current_char)
0027:         self.current_char = self.source_code[self.pos.index] if self.pos.index<len(self.source_code) else None
```

| Lines | Meaning |
|---|---|
| 18 | `class Lexer:` creates the scanner object type. |
| 19 | `__init__` runs automatically when `Lexer(source_code)` is created. |
| 20 | `source_code.replace('\r', '')` removes Windows carriage returns, keeping newline handling consistent. |
| 21 | `self.pos = Position(-1, 1, -1)` starts before the first character. Index and column are `-1` because `advance()` will move to 0. |
| 22 | `self.current_char = None` means no character is selected yet. |
| 23 | `self.advance()` immediately moves to the first source character. |
| 25-27 | `advance()` updates position, then sets `current_char` to the character at the new index. If past the end, it becomes `None`. |

Plain explanation:

```text
self.source_code = the whole code text
self.pos = where the lexer is currently located
self.current_char = the exact character the lexer is looking at right now
advance() = move one character forward
```

Example with `seed`:

| advance call | pos.index | current_char |
|---:|---:|---|
| before advance | -1 | None |
| 1st | 0 | `s` |
| 2nd | 1 | `e` |
| 3rd | 2 | `e` |
| 4th | 3 | `d` |
| 5th | 4 | None, because source ended |

### 2.2 Position Tracking

Source: `Backend/lexer/positions.py:3-21`

```python
0003: class Position:
0004: 
0005:     def __init__(self, index, ln, col=0):
0006:         self.index = index
0007:         self.ln = ln
0008:         self.col = col
0009: 
0010:     def advance(self, current_char):
0011:         self.index += 1
0012:         self.col += 1
0013: 
0014:         if current_char == '\n':
0015:             self.ln += 1
0016:             self.col = 0
0017: 
0018:         return self
0019: 
0020:     def copy(self):
0021:         return Position(self.index, self.ln, self.col)
```

| Lines | Meaning |
|---|---|
| 3-7 | `Position` stores filename, index, line number, and column number. |
| 9-11 | Every advance moves index and column forward. |
| 12-14 | If the previous character was newline, line number increases and column resets to 0. |
| 16-21 | `copy()` creates a snapshot of the current position. The lexer uses this as the starting position of a token. |

### 2.3 Main Lexer Loop

Source: `Backend/lexer/scanner.py:29-35`

```python
0029:     def make_tokens(self):
0030:         tokens = []
0031:         line = 1
0032:         errors = []
0033:         pos = self.pos.copy()
0034: 
0035:         while self.current_char != None:
```

| Lines | Meaning |
|---|---|
| 30 | `tokens = []` is where token objects are stored. |
| 31 | `line = 1` stores the current line counter used in many token creations. |
| 32 | `errors = []` stores lexical error objects. |
| 34 | `while self.current_char != None:` means keep scanning until the end of the source. |
| 35 | If the current character is alphabetic, the lexer enters reserved-word/identifier logic. |

### 2.4 Reserved Word Recognition: `root`

Source: `Backend/lexer/scanner.py:341-379`

```python
0341:                 elif self.current_char == "r":
0342:                     ident_str += self.current_char
0343:                     self.advance()
0344:                     if self.current_char == "e":
0345:                         ident_str += self.current_char
0346:                         self.advance()
0347:                         if self.current_char == "c":
0348:                             ident_str += self.current_char
0349:                             self.advance()
0350:                             if self.current_char == "l":
0351:                                 ident_str += self.current_char
0352:                                 self.advance()
0353:                                 if self.current_char == "a":
0354:                                     ident_str += self.current_char
0355:                                     self.advance()
0356:                                     if self.current_char == "i":
0357:                                         ident_str += self.current_char
0358:                                         self.advance()
0359:                                         if self.current_char == "m":
0360:                                             ident_str += self.current_char
0361:                                             self.advance()
0362:                                             if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim8:
0363:                                                 tokens.append(Token(TT_RW_RECLAIM, ident_str, line, pos.col))
0364:                                                 continue
0365:                                             elif self.current_char is not None and not self.current_char.isspace() and self.current_char not in delim8 and self.current_char not in ALPHANUM:
0366:                                                 errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
0367:                                                 self.advance()
0368:                                                 continue
0369:                     elif self.current_char == "o":
0370:                         ident_str += self.current_char
0371:                         self.advance()
0372:                         if self.current_char == "o":
0373:                             ident_str += self.current_char
0374:                             self.advance()
0375:                             if self.current_char == "t":
0376:                                 ident_str += self.current_char
0377:                                 self.advance()
0378:                                 if self.current_char is None or (self.current_char is not None and self.current_char.isspace()) or self.current_char in delim7:
0379:                                     tokens.append(Token(TT_RW_ROOT, ident_str, line, pos.col))
```

| Lines | Meaning |
|---|---|
| 341 | This branch runs when the first character collected is `r`. |
| 342-344 | Adds `r`, moves forward, checks if next character is `o`. |
| 345-348 | Adds first `o`, moves forward, checks if next character is second `o`. |
| 349-352 | Adds second `o`, moves forward, checks if next character is `t`. |
| 353-356 | Adds `t`, moves forward, now `ident_str` is `root`. |
| 357-358 | Checks if `root` is followed by end/space/valid root delimiter `(`. |
| 360-373 | If invalid delimiter exists after `root`, create lexical error. |
| 375 | If delimiter is valid, append `Token(TT_RW_ROOT, ident_str, line, pos.col)`. |
| 377 | `break` exits the alphabet branch because the token is finished. |

Example:

```gal
root()
```

Process:

| Character | ident_str after reading | What the lexer checks |
|---|---|---|
| `r` | `r` | maybe a word starting with r |
| `o` | `ro` | maybe `root` |
| `o` | `roo` | still maybe `root` |
| `t` | `root` | exact reserved word found |
| `(` | not added | valid delimiter, so token becomes `root` |

### 2.5 Fallback to Identifier

Source: `Backend/lexer/scanner.py:611-638`

```python
0611:                 maxIdentifierLength = 15
0612:                 while self.current_char is not None and self.current_char in ALPHANUM:
0613:                     ident_str += self.current_char
0614:                     self.advance()
0615: 
0616:                 if len(ident_str) > maxIdentifierLength:
0617:                     i = 0
0618:                     remaining = None
0619:                     while i < len(ident_str):
0620:                         if i + 15 <= len(ident_str):
0621:                             errors.append(LexicalError(pos, f"Identifier exceeds maximum length of {maxIdentifierLength} characters"))
0622:                             i += 15
0623:                         else:
0624:                             remaining = ident_str[i:]
0625:                             if self.current_char is None or self.current_char in idf_delim:
0626:                                 tokens.append(Token(TT_IDENTIFIER, remaining, line, pos.col))
0627:                             elif self.current_char is not None and self.current_char not in idf_delim:
0628:                                 errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after identifier"))
0629:                             break
0630:                     if remaining is None:
0631:                         last_chunk = ident_str[i - 15:] if i >= 15 else ident_str
0632:                         if self.current_char is None or self.current_char in idf_delim:
0633:                             tokens.append(Token(TT_IDENTIFIER, last_chunk, line, pos.col))
0634:                     continue
0635:                 else:
0636:                     if self.current_char is None or self.current_char in idf_delim:
0637:                         tokens.append(Token(TT_IDENTIFIER, ident_str, line, pos.col))
0638:                         continue
```

| Lines | Meaning |
|---|---|
| 611 | This block runs if the alphabet text was not accepted as a reserved word. |
| 613 | Identifier length limit is 15. |
| 614-615 | While the current character is alphanumeric, add it to `ident_str` and advance. |
| 616-628 | If the final identifier is too long, split/report length error. |
| 630 | `remaining = ident_str[i:]` gets the valid remaining identifier text after length handling. |
| 631-632 | If the next character is a valid identifier delimiter, append an `id` token. |
| 633-637 | If the next character is not a valid delimiter, create lexical error. |
| 638 | Break out because this lexeme is finished. |

Important example: `roof()`

```text
The lexer tries to match root.
It reads r, o, o.
Then it expects t, but sees f.
The reserved-word condition fails.
No token was appended yet, so Python naturally continues to the fallback identifier block.
The fallback while-loop collects f.
The final ident_str becomes roof.
Because the next character is (, and ( is valid in idf_delim, it creates Token(TT_IDENTIFIER, "roof", ...).
```

The code that collects `f` is:

```python
while self.current_char is not None and self.current_char in ALPHANUM:
    ident_str += self.current_char
    self.advance()
```

`self.current_char` is `f`, so `ident_str += self.current_char` changes `roo` into `roof`.

### 2.6 Number Literals

Source: `Backend/lexer/scanner.py:1171-1236`

```python
1171:                 ident_str = ""
1172:                 pos = self.pos.copy()
1173:                 integer_digit_count = 0
1174:                 fractional_digit_count = 0
1175:                 has_e = False
1176: 
1177:                 
1178:                 while self.current_char is not None and self.current_char in ZERODIGIT:
1179:                     integer_digit_count += 1
1180:                     ident_str += self.current_char
1181:                     self.advance()
1182: 
1183:                 if self.current_char == ".":
1184:                     if integer_digit_count > 15:
1185:                         integer_part = ident_str
1186:                         i = 0
1187:                         while i < len(integer_part):
1188:                             if i + 15 < len(integer_part):
1189:                                 errors.append(LexicalError(pos, f"Integer part of decimal exceeds maximum of 15 digits"))
1190:                                 i += 15
1191:                             else:
1192:                                 ident_str = integer_part[i:]
1193:                                 break
1194:                         else:
1195:                             ident_str = "0"
1196:                     dot_count = 1
1197:                     ident_str += self.current_char
1198:                     self.advance()
1199:                     
1200:                     if self.current_char is None or self.current_char not in ZERODIGIT:
1201:                         errors.append(LexicalError(pos, f"Invalid number '{ident_str}': decimal point must be followed by digits"))
1202:                         continue
1203:                     
1204:                     fractional_part = ""
1205:                     while self.current_char is not None and self.current_char in ZERODIGIT:
1206:                         fractional_digit_count += 1
1207:                         fractional_part += self.current_char
1208:                         self.advance()
1209:                     
1210:                     if fractional_digit_count > 8:
1211:                         i = 0
1212:                         final_fractional = ""
1213:                         while i < len(fractional_part):
1214:                             if i + 8 < len(fractional_part):
1215:                                 errors.append(LexicalError(pos, f"Fractional part exceeds maximum of 8 digits"))
1216:                                 i += 8
1217:                             else:
1218:                                 final_fractional = fractional_part[i:]
1219:                                 break
1220:                         ident_str += final_fractional
1221:                     else:
1222:                         ident_str += fractional_part
1223: 
1224:                 if dot_count == 0 and integer_digit_count > 8:
1225:                     i = 0
1226:                     remaining = None
1227:                     while i < len(ident_str):
1228:                         if i + 8 < len(ident_str):
1229:                             errors.append(LexicalError(pos, f"Integer exceeds maximum of 8 digits"))
1230:                             i += 8
1231:                         else:
1232:                             remaining = ident_str[i:]
1233:                             remaining = remaining.lstrip("0") or "0"
1234:                             tokens.append(Token(TT_INTEGERLIT, remaining, line, pos.col))
1235:                             break
1236:                     if remaining is None:
```

| Lines | Meaning |
|---|---|
| 1171 | Runs when current character is a digit. |
| 1173-1175 | Starts collecting number characters and saves starting position. |
| 1177-1182 | Collects all digits into `digits`. |
| 1184-1199 | If a dot appears, scan decimal part and validate decimal structure. |
| 1201-1214 | If the character after the number is another invalid digit/letter/dot pattern, create lexical error. |
| 1216-1227 | If there was no decimal point and delimiter is valid, append `intlit`. |
| 1228-1236 | If there is a decimal point and delimiter is valid, append `dblit`. |

### 2.7 String Literal

Source: `Backend/lexer/scanner.py:1334-1388`

```python
1334:             elif self.current_char == '"':
1335:                 string = ''
1336:                 pos = self.pos.copy()
1337:                 escape_character = False
1338:                 string += self.current_char
1339:                 self.advance()
1340: 
1341:                 escape_characters = {
1342:                     'n': '\n',
1343:                     't': '\t',
1344:                     '{': '\\{',
1345:                     '}': '\\}',
1346:                     '"': '"',
1347:                     '\\': '\\',
1348:                 }
1349: 
1350:                 has_string_error = False
1351:                 while self.current_char is not None and (self.current_char != '"' or escape_character):
1352:                     if escape_character:
1353:                         if self.current_char in escape_characters:
1354:                             string += escape_characters[self.current_char]
1355:                         else:
1356:                             errors.append(LexicalError(pos, f"Invalid escape sequence '\\{self.current_char}' in string literal"))
1357:                             has_string_error = True
1358:                         escape_character = False
1359:                     else:
1360:                         if self.current_char == '\\':
1361:                             escape_character = True
1362:                         elif self.current_char == '\n':
1363:                             break
1364:                         else:
1365:                             string += self.current_char
1366:                     self.advance()
1367: 
1368:                 if has_string_error:
1369:                     while self.current_char is not None and self.current_char != '"':
1370:                         self.advance()
1371:                     if self.current_char == '"':
1372:                         self.advance()
1373:                     continue
1374: 
1375:                 if self.current_char == '"':
1376:                     string += self.current_char
1377:                     self.advance()
1378:                 else:
1379:                     errors.append(LexicalError(pos, f"Missing closing '\"' for string literal"))
1380:                     continue
1381: 
1382:                 if self.current_char is not None and self.current_char not in delim23 and self.current_char not in space_delim:
1383:                     errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after string literal '{string}'"))
1384:                     self.advance()
1385:                     continue
1386:             
1387:                 tokens.append(Token(TT_STRINGLIT, string, line, pos.col))
1388:                 continue
```

| Lines | Meaning |
|---|---|
| 1334 | Runs when current character is double quote. |
| 1336-1341 | Initializes string buffer and moves past the opening quote. |
| 1343-1358 | Reads string contents until closing quote or end of file. Handles escape sequences. |
| 1360-1366 | If no closing quote exists, create lexical error. |
| 1368-1372 | If closing quote exists, include it and advance. |
| 1374-1386 | Check valid delimiter after string, then append `stringlit`. |

### 2.8 Character Literal

Source: `Backend/lexer/scanner.py:1390-1456`

```python
1390:             elif self.current_char == "'":
1391:                 string = ''
1392:                 char = ''
1393:                 pos = self.pos.copy()
1394:                 string += self.current_char
1395:                 self.advance()
1396:                 has_error = False
1397: 
1398:                 while self.current_char is not None and self.current_char in ' \t':
1399:                     string += self.current_char
1400:                     self.advance()
1401: 
1402:                 while self.current_char is not None and self.current_char != "'":
1403:                     if self.current_char == '\n':
1404:                         break
1405:                     elif self.current_char == '\\':
1406:                         string += self.current_char
1407:                         self.advance()
1408:                         if self.current_char is None:
1409:                             break
1410:                         
1411:                         if self.current_char in "'\\nt": 
1412:                             char += f"\\{self.current_char}"
1413:                             string += self.current_char
1414:                         else:
1415:                             errors.append(LexicalError(pos, f"Invalid escape sequence '\\{self.current_char}' in character literal"))
1416:                             has_error = True
1417:                             while self.current_char is not None and self.current_char != "'":
1418:                                 self.advance()
1419:                             if self.current_char == "'":
1420:                                 self.advance()
1421:                             break
1422:                     else:
1423:                         string += self.current_char
1424:                         char += self.current_char
1425:                     self.advance()
1426:                 
1427:                 while len(char) > 0 and char[-1] in ' \t':
1428:                     char = char[:-1]
1429: 
1430:                 if has_error:
1431:                     continue
1432: 
1433:                 if self.current_char == "'":
1434:                     string += self.current_char
1435:                     self.advance()
1436:                 else:
1437:                     errors.append(LexicalError(pos, f"Missing closing quote for character literal"))
1438:                     continue
1439: 
1440:                 if self.current_char is not None and self.current_char not in delim23 and self.current_char not in space_delim:
1441:                     errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{string}'"))
1442:                     self.advance()
1443:                     continue
1444: 
1445:                 inner = char.strip()
1446:                 if len(inner) == 0:
1447:                     string = "' '"
1448:                     inner = ' '
1449:                 elif inner.startswith('\\') and len(inner) == 2:
1450:                     pass
1451:                 elif len(inner) > 1:
1452:                     errors.append(LexicalError(pos, f"Character literal must contain exactly one character, found '{inner}'"))
1453:                     continue
1454: 
1455:                 tokens.append(Token(TT_CHARLIT, string, line, pos.col))
1456:                 continue
```

| Lines | Meaning |
|---|---|
| 1390 | Runs when current character is single quote. |
| 1392-1400 | Starts collecting character literal content. |
| 1402-1422 | Reads characters and escape sequences until closing quote. |
| 1424-1430 | Reports unclosed character literal. |
| 1432-1439 | Counts actual character length, allowing valid escapes. |
| 1441-1454 | Checks delimiter and appends `chrlit` if valid. |

### 2.9 Comments

Source: `Backend/lexer/scanner.py:1071-1106`

```python
1071:             elif self.current_char == "/":
1072:                 ident_str = self.current_char
1073:                 pos = self.pos.copy()
1074:                 self.advance()
1075:                 
1076:                 if self.current_char == "/":
1077:                     ident_str += self.current_char
1078:                     self.advance()
1079:                     while self.current_char is not None and self.current_char != "\n":
1080:                         ident_str += self.current_char
1081:                         self.advance()
1082:                     tokens.append(Token(TT_COMMENT, ident_str, line, pos.col))
1083:                     continue
1084: 
1085:                 elif self.current_char == "*":
1086:                     ident_str += self.current_char
1087:                     self.advance()
1088:                     found_close = False
1089:                     while self.current_char is not None:
1090:                         if self.current_char == "*" and self.pos.index + 1 < len(self.source_code) and self.source_code[self.pos.index + 1] == "/":
1091:                             ident_str += "*/"
1092:                             self.advance()
1093:                             self.advance()
1094:                             found_close = True
1095:                             break
1096:                         else:
1097:                             ident_str += self.current_char
1098:                             if self.current_char == "\n":
1099:                                 line += 1
1100:                             self.advance()
1101: 
1102:                     if not found_close:
1103:                         errors.append(LexicalError(pos, f"Missing closing '*/' after '{ident_str}'"))
1104:                         continue
1105:                     tokens.append(Token(TT_MCOMMENT, ident_str, line, pos.col))
1106:                     continue
```

| Lines | Meaning |
|---|---|
| 1071-1073 | When scanner sees `/`, it checks if next char creates comment or operator. |
| 1075-1084 | `//` comment: keep advancing until newline or end. |
| 1086-1106 | `/* ... */` comment: keep advancing until closing `*/`; error if not closed. |

### 2.10 Operator Example: `**=`

Source: `Backend/lexer/scanner.py:811-847`

```python
0811:             elif self.current_char == "*":
0812:                 ident_str = self.current_char
0813:                 pos = self.pos.copy()
0814:                 self.advance()
0815:                 if self.current_char == "*":
0816:                     ident_str += self.current_char
0817:                     self.advance()
0818:                     if self.current_char == "=":
0819:                         ident_str += self.current_char
0820:                         self.advance()
0821:                         if self.current_char is not None and self.current_char not in delim24:
0822:                             errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
0823:                             self.advance()
0824:                             continue
0825:                         tokens.append(Token(TT_EXPEQ, ident_str, line, pos.col))
0826:                         continue
0827:                     if self.current_char is not None and self.current_char not in delim24:
0828:                         errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
0829:                         self.advance()
0830:                         continue
0831:                     tokens.append(Token(TT_EXP, ident_str, line, pos.col))
0832:                     continue
0833:                 if self.current_char == "=":
0834:                     ident_str += self.current_char
0835:                     self.advance()
0836:                     if self.current_char is not None and self.current_char not in delim24:
0837:                         errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
0838:                         self.advance()
0839:                         continue
0840:                     tokens.append(Token(TT_MULTIEQ, ident_str, line, pos.col))
0841:                     continue
0842:                 if self.current_char is not None and self.current_char not in delim24:
0843:                     errors.append(LexicalError(pos, f"Invalid delimiter '{self.current_char}' after '{ident_str}'"))
0844:                     self.advance()
0845:                     continue
0846:                 tokens.append(Token(TT_MUL, ident_str, line, pos.col))
0847:                 continue
```

| Lines | Meaning |
|---|---|
| 811 | Runs when current character is `*`. |
| 813-815 | Starts symbol buffer with `*` and advances. |
| 817 | If next char is another `*`, it may be exponent operator. |
| 818-820 | Builds `**`. |
| 821-825 | If next char is `=`, builds `**=` and appends exponent-assignment token. |
| 826-832 | Otherwise, appends exponent token `**`. |
| 835-840 | If after first `*` is `=`, append `*=` token. |
| 842-846 | Otherwise, append normal multiplication token `*`. |

### 2.11 Lexer Wrapper Return

Source: `Backend/lexer/scanner.py:1502-1529`

```python
1502:         if self.current_char is None:
1503:             tokens.append(Token(TT_EOF, "", line, pos.col))
1504:         
1505:         return tokens, errors
1506: 
1507: 
1508: def run(source_code):
1509:     lexer = Lexer(source_code)
1510:     tokens, error = lexer.make_tokens()
1511:     return tokens, error
1512: 
1513: def lex(source_code):
1514:     lexer = Lexer(source_code)
1515:     tokens, errors = lexer.make_tokens()
1516: 
1517:     # Report lexical errors one at a time — only surface the first.
1518:     # The user fixes it, re-runs, and sees the next one (if any).
1519:     str_errors = []
1520:     if errors:
1521:         e = errors[0]
1522:         try:
1523:             if hasattr(e, 'as_string') and callable(getattr(e, 'as_string')):
1524:                 str_errors.append(e.as_string())
1525:             else:
1526:                 str_errors.append(str(e))
1527:         except Exception:
1528:             str_errors.append(str(e))
1529:     return tokens, str_errors
```

| Lines | Meaning |
|---|---|
| 1502-1505 | When scanning ends, append EOF token and return tokens/errors. |
| 1513 | `lex(source_code)` is the function imported by the server. |
| 1515 | Creates a `Lexer` object from the source string. |
| 1516 | Runs `make_tokens()` to scan all characters. |
| 1523-1528 | Converts lexical errors into strings. |
| 1529 | Returns token list and error list to the server. |

## 3. Tokens and Delimiters

### 3.1 Token Class

Source: `Backend/shared/tokens.py:86-92`

```python
0086: class Token:
0087:     """Represents a token with type, value, line number, and column number"""
0088: 
0089:     def __init__(self, type_, value=None, line=1, col=0):
0090:         self.type = type_    # Token type (e.g., TT_IDENTIFIER, TT_INTEGERLIT)
0091:         self.value = value   # Token text/value (e.g., "myVar", "42")
0092:         self.line = line     # Line number where token appears
```

| Lines | Meaning |
|---|---|
| 86 | `class Token:` defines the object used to store each token. |
| 87 | `type_` is the category, such as `seed`, `id`, `intlit`, or `;`. |
| 88 | `value` is the actual lexeme text, such as `x` or `10`. |
| 89 | `line` stores where the token appears. |
| 90 | `col` stores the starting column. |
| 92 | `__repr__` controls how tokens print during debugging. |

### 3.2 Token Constants

Source: `Backend/shared/tokens.py:3-80`

```python
0003: # --- Reserved Words (Keywords) ---
0004: TT_RW_WATER       = 'water'     # Input function - reads user input
0005: TT_RW_PLANT       = 'plant'     # Output function - prints to console
0006: TT_RW_SEED        = 'seed'      # Data Type - integer (int)
0007: TT_RW_LEAF        = 'leaf'      # Data Type - character (char)
0008: TT_RW_BRANCH      = 'branch'    # Data Type - boolean (true/false)
0009: TT_RW_TREE        = 'tree'      # Data Type - double/float
0010: TT_RW_SPRING      = 'spring'    # Conditional statement - if
0011: TT_RW_WITHER      = 'wither'    # Conditional statement - else
0012: TT_RW_BUD         = 'bud'       # Conditional statement - else-if
0013: TT_RW_HARVEST     = 'harvest'   # Switch statement
0014: TT_RW_GROW        = 'grow'      # Loop - while
0015: TT_RW_CULTIVATE   = 'cultivate' # Loop - for
0016: TT_RW_TEND        = 'tend'      # Loop - do-while
0017: TT_RW_EMPTY       = 'empty'     # Void return type
0018: TT_RW_PRUNE       = 'prune'     # Break statement - exit loop
0019: TT_RW_SKIP        = 'skip'      # Continue statement - skip to next iteration
0020: TT_RW_RECLAIM     = 'reclaim'   # Return statement - return from function
0021: TT_RW_ROOT        = 'root'      # Main function entry point
0022: TT_RW_POLLINATE   = 'pollinate' # Function declaration
0023: TT_RW_VARIETY     = 'variety'   # Case label in switch statement
0024: TT_RW_FERTILE     = 'fertile'   # Constant declaration
0025: TT_RW_SOIL        = 'soil'      # Default case in switch statement
0026: TT_RW_BUNDLE      = 'bundle'    # Struct definition
0027: TT_RW_VINE        = 'vine'      # String data type
0028: 
0029: # --- Operators & Symbols ---
0030: TT_IDENTIFIER = 'id'        # Variable/function names (e.g., myVar, calcTotal)
0031: TT_PLUS = '+'               # Addition operator
0032: TT_MINUS = '-'              # Subtraction operator
0033: TT_MUL = '*'                # Multiplication operator
0034: TT_DIV = '/'                # Division operator
0035: TT_MOD = '%'                # Modulo operator (remainder)
0036: TT_EXP = '**'               # Exponentiation operator (power)
0037: TT_EQ = '='                 # Assignment operator
0038: TT_EQTO = '=='              # Equality comparison operator
0039: TT_PLUSEQ = '+='            # Add and assign operator
0040: TT_MINUSEQ = '-='           # Subtract and assign operator
0041: TT_MULTIEQ = '*='           # Multiply and assign operator
0042: TT_DIVEQ = '/='             # Divide and assign operator
0043: TT_MODEQ = '%='             # Modulo and assign operator
0044: TT_EXPEQ = '**='            # Exponent and assign operator (x **= 2 → x = x ** 2)
0045: TT_CONCAT = '`'             # String concatenation operator
0046: TT_LPAREN = '('             # Left parenthesis
0047: TT_RPAREN = ')'             # Right parenthesis
0048: TT_SEMICOLON = ';'          # Statement terminator
0049: TT_COMMA = ','              # Separator (function args, array elements)
0050: TT_COLON = ':'              # Colon (used in switch cases)
0051: TT_BLOCK_START = '{'        # Block start (scope begin)
0052: TT_BLOCK_END = '}'          # Block end (scope close)
0053: TT_LT = '<'                 # Less than comparison
0054: TT_GT = '>'                 # Greater than comparison
0055: TT_LTEQ = '<='              # Less than or equal comparison
0056: TT_GTEQ = '>='              # Greater than or equal comparison
0057: TT_NOTEQ = '!='             # Not equal comparison
0058: TT_EOF = 'EOF'                  # End of file marker
0059: TT_AND = '&&'                   # Logical AND operator
0060: TT_OR = '||'                    # Logical OR operator
0061: TT_SINGLE_AND = '&'             # Invalid single ampersand
0062: TT_SINGLE_OR = '|'              # Invalid single pipe
0063: TT_NOT = '!'                    # Logical NOT operator
0064: TT_INCREMENT = '++'             # Increment operator (e.g., x++)
0065: TT_DECREMENT = '--'             # Decrement operator (e.g., x--)
0066: TT_LSQBR = '['                  # Left square bracket (array indexing)
0067: TT_RSQBR = ']'                  # Right square bracket
0068: TT_NEGATIVE = '~'               # Unary negation operator
0069: TT_MEMBER = 'member'            # Member token for struct access
0070: TT_INTEGERLIT = 'intlit'        # Integer literal token (e.g., 42, 100)
0071: TT_DOUBLELIT = 'dblit'         # Double/float literal token (e.g., 3.14, 2.5)
0072: TT_STRINGLIT = 'stringlit'      # String literal token (e.g., "hello")
0073: TT_CHARLIT = 'chrlit'           # Character literal token (e.g., 'a')
0074: TT_BOOLLIT_TRUE = 'sunshine'    # Boolean true literal
0075: TT_BOOLLIT_FALSE = 'frost'      # Boolean false literal
0076: TT_STRCTACCESS = '.'            # Struct member access operator
0077: TT_NL = '\n'                    # Newline token
0078: TT_DOT = '.'                    # Dot operator (struct access)
0079: TT_COMMENT = 'comment'          # Single-line comment (//...)
0080: TT_MCOMMENT = 'mcommentlit'     # Multi-line comment (/*...*/)
```

These constants prevent hardcoding random strings everywhere. Instead of writing `"seed"` many times, the lexer can use `TT_DT_INT = "seed"`. The parser receives these token types and compares them against CFG terminals.

### 3.3 Delimiter Sets

Source: `Backend/lexer/delimiters.py:1-60`

```python
0001: ZERO = '0'
0002: DIGIT = '123456789'
0003: ZERODIGIT = ZERO + DIGIT
0004: 
0005: LOW_ALPHA = 'abcdefghijklmnopqrstuvwxyz'
0006: UPPER_ALPHA = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
0007: ALPHA = LOW_ALPHA + UPPER_ALPHA
0008: ALPHANUM = ALPHA + ZERODIGIT + '_'
0009: 
0010: WHITESPACE = ' \t\n'
0011: EOF = None
0012: 
0013: statement_end_delim = set(ALPHA + WHITESPACE + '}') | {EOF}
0014: open_paren_delim = set(ALPHA + ZERODIGIT + WHITESPACE + '"' + "'" + '~' + '!' + '(' + ')')
0015: close_paren_delim = set(WHITESPACE) | {';', '{', ')', ',', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|', ']'}
0016: open_bracket_delim = set(ALPHA + ZERODIGIT + WHITESPACE + '~' + '!' + '(' + '"' + "'")
0017: close_bracket_delim = set(WHITESPACE) | {';', ',', ')', ']', '[', '.', '=', '+', '-', '*', '/', '%', '>', '<', '!', '&', '|'}
0018: block_start_delim = set(ALPHA + ZERODIGIT + WHITESPACE + '}/{"\'~!(')
0019: block_end_delim = set(ALPHA + ZERODIGIT + WHITESPACE + '};,)]')
0020: case_colon_delim = set(ALPHA + WHITESPACE + '}/')
0021: after_comma_delim = set(ALPHA + ZERODIGIT + WHITESPACE + '"' + "'" + '~' + '!' + '(' + '{')
0022: space_delim = {' ', '\t', '\n'}
0023: period_delim = {'.'}
0024: underscore_delim = {'_'}
0025: open_brack_delim = {'['}
0026: close_brack_delim = {']'}
0027: comma_delim = {','}
0028: delim1 = {'}'}
0029: delim2 = {':'}
0030: delim3 = {'{'}
0031: delim4 = {':', '('}
0032: delim5 = {'('}
0033: delim6 = {';', ',', '=', '>', '<', '!', '}', ')', '('}
0034: delim7 = {'('}
0035: delim8 = {';'}
0036: delim9 = set(ALPHA + '(' + ',' + ';' + ')')
0037: delim10 = {';', ')'}
0038: delim11 = set([LOW_ALPHA, ZERODIGIT, ']', '~'])
0039: delim12 = set(ALPHA + ZERODIGIT + ']' + '~')
0040: delim13 = {';', ')', '['}
0041: delim14 = set(ALPHA + ZERODIGIT + '"' + "'" + '{')
0042: delim15 = {'\n', ';', '}', ','}
0043: delim16 = set(ALPHANUM + ')' + '"' + '!' + '(' + '[' + '\'')
0044: delim17 = {'}', ';', ',', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|'}
0045: delim18 = {';', '{', ')', '&', '|', '+', '-', '*', '/', '%'}
0046: delim19 = {';', ',', '}', ')', '=', '>', '<', '!'}
0047: delim20 = set(ALPHA + ZERODIGIT + '"' + "'" + '{')
0048: delim21 = set(DIGIT)
0049: delim22 = {',', ';', '(', ')', '{', '[', ']'}
0050: delim23 = {';', ',', '}', ']', ')', ':', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|'}
0051: delim24 = set(ZERODIGIT + ALPHA + '~(' + ' \t\n')
0052: delim25 = set(ALPHANUM + ';) \t\n')
0053: delim26 = set(ZERODIGIT + ALPHA + '~(' + '"\'' + ' \t\n')
0054: idf_delim = {' ', ',', ';', '(', ')', '{', '}', '[', ']', ':', '+', '-', '*', '/', '%',
0055:              '>', '<', '=', '\t', '\n', '.', '"', "'"}
0056: whlnum_delim = {';', ' ', ',', '}', ']', ')', ':', '+', '-', '*', '/', '%', '=', '>', '<',
0057:                 '!', '&', '|', '\t', '\n'}
0058: decim_delim = {'}', ';', ',', '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|', ' ',
0059:                '\t', '\n', ')', ']'}
0060: comment_delim = set(ALPHANUM + ';+-*/%}{()' + '\n')
```

| Lines | Meaning |
|---|---|
| 1-8 | Defines character groups: letters, digits, zero digit, alphanumeric. |
| 13-20 | Defines general delimiter groups like whitespace, data-type delimiters, brackets, and string delimiters. |
| 22-53 | Defines numbered delimiter sets used by different reserved words/symbols. |
| 54 | `idf_delim` is valid next character after an identifier. |
| 55 | `whlnum_delim` is valid next character after an integer literal. |
| 56 | `decim_delim` is valid next character after a decimal literal. |
| 60 | `comment_delim` is for comment scanning. |

Delimiter defense shortcut:

```text
A token is the thing the parser receives.
A delimiter set is only a lexer validation rule for the next character.
For example, ++ is a token, but delim25 only checks what can legally come after ++.
```

### 3.4 Removed CGMA Names: `ts` and `taper`

The old CGMA-style names `ts` and `taper` were removed from the backend system.

What changed:

| Old Code Item | Current Status |
|---|---|
| `TaperNode` | Removed from `Backend/shared/ast_nodes.py`. |
| `TSNode` | Removed from `Backend/shared/ast_nodes.py`. |
| `eval_taper()` | Removed from `Backend/interpreter/interpreter.py`. |
| `eval_ts()` | Removed from `Backend/interpreter/interpreter.py`. |
| builder checks for `.taper` | Removed from `Backend/parser/builder.py`. |
| builder checks for `.ts` | Removed from `Backend/parser/builder.py`. |

Plain explanation:

```text
The lexer never treated ts or taper as reserved words.
Before cleanup, the builder gave them hidden special meaning when it saw id . ts or id . taper.
Now that hidden support is removed, so they behave like unsupported member access.
```

Recommended future names if the feature is added again:

```gal
seed size = arr.count;
leaf letters[3] = word.leaves;
```

Important: `.count` and `.leaves` are recommended names only. They are not implemented until backend support is added.

## 4. Parser Detailed Code Flow

### 4.1 Token View Normalization

Source: `Backend/parser/parser.py:13-34`

```python
0013: @dataclass(frozen=True)
0014: class _TokView:
0015:     type: str
0016:     value: str
0017:     line: int
0018:     col: int = 0
0019: 
0020: 
0021: def _as_tok(token: Any) -> _TokView:
0022:     if isinstance(token, Mapping):
0023:         return _TokView(
0024:             type=str(token.get("type", "")),
0025:             value=str(token.get("value", "")),
0026:             line=int(token.get("line", 0) or 0),
0027:             col=int(token.get("col", 0) or 0),
0028:         )
0029:     return _TokView(
0030:         type=str(getattr(token, "type", "")),
0031:         value=str(getattr(token, "value", "")),
0032:         line=int(getattr(token, "line", 0) or 0),
0033:         col=int(getattr(token, "col", 0) or 0),
0034:     )
```

| Lines | Meaning |
|---|---|
| 13-19 | `_TokView` is a simple normalized token format used by the parser. |
| 22-34 | `_as_tok()` converts real `Token` objects or dictionaries into `_TokView`. |
| 29-33 | If the token is a `Token` object, it reads `type`, `value`, `line`, and `col`. |

### 4.2 Parser Initialization

Source: `Backend/parser/parser.py:37-64`

```python
0037: class LL1Parser:
0038:     def __init__(
0039:         self,
0040:         cfg: Dict[str, List[List[str]]],
0041:         predict_sets: Dict[Tuple[str, Tuple[str, ...]], Set[str]],
0042:         first_sets: Dict[str, Set[str]],
0043:         *,
0044:         start_symbol: str = "<program>",
0045:         end_marker: str = "EOF",
0046:         epsilon_symbols: Iterable[str] = ("λ", "ε"),
0047:         skip_token_types: Optional[Set[str]] = None,
0048:         token_type_alias: Optional[Dict[str, str]] = None,
0049:     ):
0050:         self.cfg = cfg
0051:         self.predict_sets = predict_sets
0052:         self.first_sets = first_sets
0053: 
0054:         self.epsilon_symbols: Set[str] = set(epsilon_symbols)
0055:         self.start_symbol = start_symbol
0056:         self.end_marker = end_marker
0057: 
0058:         self.skip_token_types: Set[str] = set(skip_token_types or {"\n"})
0059:         self.token_type_alias = token_type_alias or {
0060:             'idf': 'id',
0061:             'dbllit': 'dblit',
0062:         }
0063:         
0064:         self.parsing_table: Dict[str, Dict[str, List[str]]] = self.construct_parsing_table()
```

| Lines | Meaning |
|---|---|
| 37 | `LL1Parser` is the main parser class. |
| 38-47 | Constructor receives CFG, PREDICT sets, FIRST sets, start symbol, EOF marker, and skip token types. |
| 48-53 | Stores grammar data into instance variables. |
| 54 | Defines aliases, for example newline token mapping. |
| 55 | Builds the LL(1) parsing table. |
| 56-64 | Creates state variables used for better error messages. |

### 4.3 Parsing Table

Source: `Backend/parser/parser.py:66-82`

```python
0066:     def construct_parsing_table(self) -> Dict[str, Dict[str, List[str]]]:
0067:         table: Dict[str, Dict[str, List[str]]] = {}
0068: 
0069:         for non_terminal, productions in self.cfg.items():
0070:             row: Dict[str, List[str]] = {}
0071:             for production in productions:
0072:                 key = (non_terminal, tuple(production))
0073:                 terms = self.predict_sets.get(key, set())
0074:                 for terminal in terms:
0075:                     if terminal in row and row[terminal] != production:
0076:                         raise ValueError(
0077:                             f"LL(1) conflict at {non_terminal} with lookahead {terminal}: "
0078:                             f"{row[terminal]} vs {production}"
0079:                         )
0080:                     row[terminal] = production
0081:             table[non_terminal] = row
0082:         return table
```

| Lines | Meaning |
|---|---|
| 67 | Creates empty dictionary for parsing table. |
| 68-69 | Loops through each nonterminal and its productions in the CFG. |
| 70 | Creates row for current nonterminal. |
| 71 | Gets the PREDICT set for the production. |
| 72-79 | For every terminal in the PREDICT set, store which production should be used. |
| 74-78 | If a table cell is already filled, that means LL(1) conflict. |
| 81-82 | Returns the completed parsing table. |

### 4.4 Main Parse Loop

Source: `Backend/parser/parser.py:614-715`

```python
0614:     def parse(self, tokens: Sequence[Any]) -> Tuple[bool, List[str]]:
0615:         toks = [_as_tok(t) for t in tokens]
0616:         toks = [_TokView(self._normalize_token_type(t.type), t.value, t.line, t.col) for t in toks]
0617:         toks = self._ensure_eof(toks)
0618: 
0619:         self._current_tokens = toks
0620: 
0621:         stack: List[str] = [self.end_marker, self.start_symbol]
0622:         index = 0
0623:         
0624:         current_var_type: Optional[str] = None
0625:         expecting_value_for_type: Optional[str] = None
0626: 
0627:         reclaim_seen_stack: List[bool] = []
0628: 
0629:         def current_token() -> _TokView:
0630:             nonlocal index
0631:             if index >= len(toks):
0632:                 last_line = toks[-1].line if toks else 1
0633:                 last_col = toks[-1].col if toks else 0
0634:                 return _TokView(self.end_marker, self.end_marker, last_line, last_col)
0635:             return toks[index]
0636: 
0637:         while stack:
0638:             top = stack[-1]
0639:             tok = current_token()
0640:             token_type = tok.type
0641:             token_value = tok.value
0642:             line = tok.line or 1
0643: 
0644:             if token_type in self.skip_token_types and top != token_type:
0645:                 index += 1
0646:                 continue
0647: 
0648:             if top in self.parsing_table:
0649:                 row = self.parsing_table[top]
0650:                 if token_type in row:
0651:                     production = row[token_type]
0652:                     
0653:                     if top == '<statement>' and token_type != '}' and reclaim_seen_stack and reclaim_seen_stack[-1]:
0654:                         return False, [f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}' after 'reclaim'. Expected: '}}'."]
0655: 
0656:                     if top == '<statement>' and token_type == '}':
0657:                         is_epsilon = (len(production) == 0 or (len(production) == 1 and production[0] in self.epsilon_symbols))
0658:                         if is_epsilon:
0659:                             lookback = index - 1
0660:                             while lookback >= 0 and toks[lookback].type in self.skip_token_types:
0661:                                 lookback -= 1
0662:                             
0663:                             if lookback >= 0 and toks[lookback].type == '{':
0664:                                 before_brace = lookback - 1
0665:                                 while before_brace >= 0 and toks[before_brace].type in self.skip_token_types:
0666:                                     before_brace -= 1
0667:                                 
0668:                                 if before_brace >= 0 and toks[before_brace].type == ')':
0669:                                     paren_depth = 1
0670:                                     paren_pos = before_brace - 1
0671:                                     while paren_pos >= 0 and paren_depth > 0:
0672:                                         if toks[paren_pos].type == ')':
0673:                                             paren_depth += 1
0674:                                         elif toks[paren_pos].type == '(':
0675:                                             paren_depth -= 1
0676:                                         paren_pos -= 1
0677:                                     
0678:                                     if paren_pos >= 0:
0679:                                         kw_pos = paren_pos
0680:                                         while kw_pos >= 0 and toks[kw_pos].type in self.skip_token_types:
0681:                                             kw_pos -= 1
0682:                                         
0683:                                         if kw_pos >= 0:
0684:                                             kw = toks[kw_pos]
0685:                                             conditional_keywords = {'spring', 'bud', 'wither', 'grow', 'cultivate', 'tend', 'harvest'}
0686:                                             if kw.type in conditional_keywords:
0687:                                                 return False, [f"SYNTAX error line {line} col {tok.col} Empty block after '{kw.value}' statement - at least one statement required"]
0688:                                 
0689:                                 elif before_brace >= 0 and toks[before_brace].type in {'wither', 'tend'}:
0690:                                     kw = toks[before_brace]
0691:                                     return False, [f"SYNTAX error line {line} col {tok.col} Empty block after '{kw.value}' statement - at least one statement required"]
0692:                     
0693:                     stack.pop()
0694: 
0695:                     if not (
0696:                         len(production) == 0
0697:                         or (len(production) == 1 and production[0] in self.epsilon_symbols)
0698:                     ):
0699:                         stack.extend(reversed(production))
0700:                     continue
0701: 
0702:                 expected = set(row.keys())
0703:                 
0704:                 if token_type in {'variety', 'soil'} and token_type not in expected:
0705:                     while index < len(toks) and toks[index].type != ';':
0706:                         if toks[index].type == 'prune':
0707:                             index += 1
0708:                             break
0709:                         index += 1
0710:                     if index < len(toks) and toks[index].type == ';':
0711:                         index += 1
0712:                     continue
0713: 
0714:                 error_msg = self._generate_helpful_error(top, token_type, token_value, line, tok.col, expected, index, toks)
0715:                 return False, [error_msg]
```

| Lines | Meaning |
|---|---|
| 615 | Converts token list into normalized `_TokView` tokens. |
| 618-620 | Ensures EOF exists at the end. |
| 624 | Initial stack is `[EOF, <program>]`. |
| 626 | `index = 0` means parser starts at the first token. |
| 627-631 | `current_token()` skips newline/comment tokens if configured. |
| 641-644 | If stack becomes empty, parsing is finished. |
| 646-664 | If top is EOF, check if current token is EOF. |
| 665 | If stack top is a nonterminal, use parsing table. |
| 666-669 | Get current lookahead token type. |
| 672-690 | If production exists, pop nonterminal and push production symbols in reverse order. |
| 702-715 | If no production exists, create syntax error and return failure. |

### 4.5 Terminal Match and Consume

Source: `Backend/parser/parser.py:717-760`

```python
0717:             if top == token_type:
0718:                 if token_type in {'seed', 'tree', 'leaf', 'branch', 'vine'}:
0719:                     current_var_type = token_type
0720:                     expecting_value_for_type = None
0721:                 
0722:                 elif token_type == '=' and current_var_type is not None:
0723:                     expecting_value_for_type = current_var_type
0724:                 
0725:                 elif expecting_value_for_type is not None and token_type in {'intlit', 'dblit', 'stringlit', 'chrlit', 'sunshine', 'frost', 'id'}:
0726:                     type_value_map = {
0727:                         'seed': {'intlit', 'dblit'},
0728:                         'tree': {'dblit', 'intlit'},
0729:                         'leaf': {'chrlit'},
0730:                         'branch': {'sunshine', 'frost'},
0731:                         'vine': {'stringlit'}
0732:                     }
0733:                     
0734:                     if token_type == 'id':
0735:                         expecting_value_for_type = None
0736:                         stack.pop()
0737:                         index += 1
0738:                         continue
0739:                     
0740:                     expected_value_types = type_value_map.get(expecting_value_for_type, set())
0741:                     
0742:                     if token_type not in expected_value_types:
0743:                         type_names = {
0744:                             'seed': 'integer (seed)',
0745:                             'tree': 'double (tree)',
0746:                             'leaf': 'character (leaf)',
0747:                             'branch': 'boolean (branch)',
0748:                             'vine': 'string (vine)'
0749:                         }
0750:                         value_type_names = {
0751:                             'intlit': 'integer',
0752:                             'dblit': 'double',
0753:                             'stringlit': 'string',
0754:                             'chrlit': 'character',
0755:                             'sunshine': 'boolean',
0756:                             'frost': 'boolean',
0757:                             'id': 'identifier'
0758:                         }
0759:                         
0760:                         declared_type = type_names.get(expecting_value_for_type, expecting_value_for_type)
```

| Lines | Meaning |
|---|---|
| 717 | If stack top is terminal and matches current token type, it is accepted. |
| 718 | Stores actual token for state/error tracking. |
| 719-760 | Updates parser state depending on important tokens like `pollinate`, `root`, braces, and declaration keywords. |
| Later in this block | After handling state, the parser pops the terminal and moves to next token. |

### 4.6 Parse and Build

Source: `Backend/parser/parser.py:1183-1240`

```python
1183:     def parse_and_build(self, tokens: Sequence[Any]):
1184:         syntax_ok, syntax_errors = self.parse(tokens)
1185:         if not syntax_ok:
1186:             first_err = syntax_errors[0] if syntax_errors else ""
1187:             stage = "semantic" if first_err.startswith("SEMANTIC error") else "syntax"
1188:             return {
1189:                 "success": False,
1190:                 "errors": syntax_errors,
1191:                 "ast": None,
1192:                 "symbol_table": {},
1193:                 "error_stage": stage,
1194:             }
1195: 
1196:         try:
1197:             filtered = [t for t in tokens if getattr(t, 'type', '') != '\n']
1198:             ast = _build_ast(filtered)
1199: 
1200:             st = {
1201:                 "variables": [
1202:                     {
1203:                         "name": name,
1204:                         "type": info["type"],
1205:                         "scope": "global",
1206:                         "is_list": info.get("is_list", False),
1207:                         "is_constant": info.get("is_fertile", False),
1208:                     }
1209:                     for name, info in _builder_st.variables.items()
1210:                 ],
1211:                 "functions": {
1212:                     name: {
1213:                         "return_type": info["return_type"],
1214:                         "params": [
1215:                             {
1216:                                 "type": p.children[0].value if p.children else "unknown",
1217:                                 "name": p.children[1].value if len(p.children) > 1 else "unknown",
1218:                             }
1219:                             for p in info["params"]
1220:                         ] if info["params"] else [],
1221:                     }
1222:                     for name, info in _builder_st.functions.items()
1223:                 },
1224:             }
1225: 
1226:             return {
1227:                 "success": True,
1228:                 "errors": [],
1229:                 "ast": ast,
1230:                 "symbol_table": st,
1231:             }
1232: 
1233:         except _SemanticError as e:
1234:             return {
1235:                 "success": False,
1236:                 "errors": [str(e)],
1237:                 "ast": None,
1238:                 "symbol_table": {},
1239:                 "error_stage": "semantic",
1240:             }
```

| Lines | Meaning |
|---|---|
| 1184 | Runs syntax parsing first. |
| 1185-1194 | If syntax fails, return error and no AST. |
| 1196-1198 | If syntax succeeds, remove newline tokens and call AST builder. |
| 1199-1205 | Return success, no errors, AST, and symbol table. |
| 1206-1240 | Catch semantic or unexpected builder errors and format them. |

Parser defense shortcut:

```text
The parser no longer reads characters. It reads token types.
It uses stack top plus current token lookahead to choose grammar production from the parsing table.
If the token matches the expected terminal, it consumes it and moves forward.
```

## 5. CFG, FIRST, FOLLOW, PREDICT Code

### 5.1 FIRST Set Function

Source: `Backend/cfg/grammar.py:13-48`

```python
0013: def compute_first(cfg):
0014:     first = defaultdict(set)
0015:     epsilon = EPSILON
0016: 
0017:     for lhs, productions in cfg.items():
0018:         for prod in productions:
0019:             if not prod:
0020:                 continue
0021:             if prod[0] == epsilon:
0022:                 first[lhs].add(epsilon)
0023:             elif prod[0] not in cfg:
0024:                 first[lhs].add(prod[0])
0025: 
0026:     changed = True
0027:     while changed:
0028:         changed = False
0029:         for lhs, productions in cfg.items():
0030:             for prod in productions:
0031:                 before = len(first[lhs])
0032: 
0033:                 for symbol in prod:
0034:                     if symbol in cfg:
0035:                         first[lhs] |= (first[symbol] - {epsilon})
0036:                         if epsilon not in first[symbol]:
0037:                             break
0038:                     else:
0039:                         if symbol != epsilon:
0040:                             first[lhs].add(symbol)
0041:                         break
0042:                 else:
0043:                     first[lhs].add(epsilon)
0044: 
0045:                 if len(first[lhs]) > before:
0046:                     changed = True
0047: 
0048:     return first
```

| Lines | Meaning |
|---|---|
| 13 | `compute_first(cfg)` receives the grammar dictionary. |
| 14 | Creates empty FIRST set for every nonterminal. |
| 16-17 | `first_of(symbol)` is a helper function. |
| 18-20 | If the symbol is a terminal, its FIRST set is itself. |
| 22-23 | If FIRST was already computed, return it. |
| 25-39 | Loops through productions and adds possible starting terminals. |
| 41-47 | Computes FIRST for all nonterminals. |
| 48 | Returns FIRST sets. |

### 5.2 FOLLOW Set Function

Source: `Backend/cfg/grammar.py:51-85`

```python
0051: def compute_follow(cfg, first):
0052:     follow = defaultdict(set)
0053:     epsilon = EPSILON
0054: 
0055:     start_symbol = next(iter(cfg))
0056:     follow[start_symbol].add("EOF")
0057: 
0058:     changed = True
0059:     while changed:
0060:         changed = False
0061:         for lhs, productions in cfg.items():
0062:             for prod in productions:
0063:                 for i, symbol in enumerate(prod):
0064:                     if symbol in cfg:
0065:                         before = len(follow[symbol])
0066: 
0067:                         j = i + 1
0068:                         while j < len(prod):
0069:                             next_symbol = prod[j]
0070:                             if next_symbol in cfg:
0071:                                 follow[symbol] |= (first[next_symbol] - {epsilon})
0072:                                 if epsilon not in first[next_symbol]:
0073:                                     break
0074:                             else:
0075:                                 if next_symbol != epsilon:
0076:                                     follow[symbol].add(next_symbol)
0077:                                 break
0078:                             j += 1
0079:                         else:
0080:                             follow[symbol] |= follow[lhs]
0081: 
0082:                         if len(follow[symbol]) > before:
0083:                             changed = True
0084: 
0085:     return follow
```

| Lines | Meaning |
|---|---|
| 51 | `compute_follow` receives CFG, FIRST sets, and start symbol. |
| 52 | Creates empty FOLLOW set for every nonterminal. |
| 53 | Adds EOF to FOLLOW of start symbol. |
| 56-83 | Repeats until no FOLLOW set changes. |
| 61-81 | When a nonterminal appears inside a production, add what can legally follow it. |
| 85 | Returns FOLLOW sets. |

### 5.3 PREDICT Set Function

Source: `Backend/cfg/grammar.py:88-119`

```python
0088: def compute_predict(cfg, first, follow):
0089:     predict = {}
0090:     epsilon = EPSILON
0091: 
0092:     for lhs, productions in cfg.items():
0093:         for prod in productions:
0094:             key = (lhs, tuple(prod))
0095:             predict[key] = set()
0096: 
0097:             if not prod or (len(prod) == 1 and prod[0] == epsilon):
0098:                 predict[key] = follow[lhs].copy()
0099:                 continue
0100: 
0101:             first_set = set()
0102:             for symbol in prod:
0103:                 if symbol in cfg:
0104:                     first_set |= (first[symbol] - {epsilon})
0105:                     if epsilon not in first[symbol]:
0106:                         break
0107:                 else:
0108:                     if symbol != epsilon:
0109:                         first_set.add(symbol)
0110:                     break
0111:             else:
0112:                 first_set.add(epsilon)
0113: 
0114:             if epsilon in first_set:
0115:                 predict[key] = (first_set - {epsilon}) | follow[lhs]
0116:             else:
0117:                 predict[key] = first_set
0118: 
0119:     return predict
```

| Lines | Meaning |
|---|---|
| 88 | `compute_predict` builds PREDICT sets from CFG, FIRST, and FOLLOW. |
| 91-94 | Loops through every production. |
| 96-110 | Computes FIRST of that production. |
| 112-116 | If production can become lambda, add FOLLOW of the nonterminal. |
| 117 | Stores the computed PREDICT set. |
| 119 | Returns all PREDICT sets. |

## 6. AST Builder and Semantic Checks

### 6.1 Builder Entry Point

Source: `Backend/parser/builder.py:21-32`

```python
0021: def build_ast(tokens):
0022:     root = ProgramNode()
0023:     symbol_table.variables = {}
0024:     symbol_table.functions = {}
0025:     symbol_table.scopes = [{}] 
0026:     symbol_table.function_variables = {}
0027:     symbol_table.bundle_types = {}
0028:     context_stack = []
0029:     index = 0
0030:     symbol_table.current_func_name = None
0031:     
0032:     while index < len(tokens):
```

| Lines | Meaning |
|---|---|
| 21 | `build_ast(tokens)` is called by `parse_and_build()` after syntax success. |
| 22 | Creates a builder `Parser` object. |
| 23 | Calls `parse_program()` to build the AST root. |
| 24-30 | Catches semantic errors and unexpected errors. |
| 32 | Returns AST and symbol table. |

### 6.2 Program-Level Build Flow

Source: `Backend/parser/builder.py:39-108`

```python
0039:         if tokens[index].value in {"seed", "tree", "vine", "leaf", "branch"}:
0040:             id_type = token.value
0041:             index += 1
0042:             if tokens[index].type != "id":
0043:                 raise SemanticError(f"Semantic Error: Invalid variable declaration.", token.line)
0044:             id_name = tokens[index].value
0045:             index += 1
0046:             node, index = parse_variable(tokens, index, id_name, id_type) 
0047: 
0048:             if node:
0049:                 root.add_child(node)
0050: 
0051:         elif tokens[index].value == "empty":
0052:             index += 1
0053:             if tokens[index].type == "id":
0054:                 func_name = tokens[index].value
0055:                 func_type = "empty"
0056:                 node, index = parse_function(tokens, index, func_name, func_type)
0057:             else:
0058:                 raise SemanticError(f"Semantic Error: Invalid function declaration.", tokens[index].line)
0059:             
0060:             if node:
0061:                 root.add_child(node)
0062:             
0063:         elif tokens[index].value in {"pollinate"}:
0064:             index += 1
0065:             if tokens[index].value in {"seed", "tree", "vine", "leaf", "branch", "empty"}:
0066:                 id_type = tokens[index].value
0067:                 index += 1
0068:                 if tokens[index].type != "id":
0069:                     raise SemanticError(f"Semantic Error: Invalid function declaration.", tokens[index].line)
0070:                 id_name = tokens[index].value
0071:                 index += 1
0072:                 node, index = parse_function(tokens, index, id_name, id_type)
0073: 
0074:                 if node:
0075:                     root.add_child(node)
0076: 
0077:             elif tokens[index].type == "id" and tokens[index].value in symbol_table.bundle_types:
0078:                 id_type = tokens[index].value
0079:                 index += 1
0080:                 if tokens[index].type != "id":
0081:                     raise SemanticError(f"Semantic Error: Invalid function declaration.", tokens[index].line)
0082:                 id_name = tokens[index].value
0083:                 index += 1
0084:                 node, index = parse_function(tokens, index, id_name, id_type)
0085: 
0086:                 if node:
0087:                     root.add_child(node)
0088: 
0089:             else: 
0090:                 raise SemanticError(f"Semantic Error: Expected data type for function declaration after 'pollinate'.", tokens[index].line)
0091: 
0092:         elif token.value == "fertile":
0093:             node, index = parse_fertile(tokens, index)
0094:             if node:
0095:                 root.add_child(node)
0096: 
0097:         elif token.value == "identifier":
0098:             if isinstance(symbol_table.lookup_variable(token.value), str):
0099:                 raise SemanticError(f"Semantic Error: Variable '{token.value}' used before declaration.", token.line)
0100:             raise SemanticError(f"Semantic Error: Invalid global statement.", token.line)
0101: 
0102:         elif token.value in {"root"}:
0103:             func_name = token.value
0104:             func_type = "empty"
0105:             node, index = parse_function(tokens, index, func_name, func_type)
0106: 
0107:             if node:
0108:                 root.add_child(node)
```

| Lines | Meaning |
|---|---|
| 39-46 | If token is a data type, parse variable declaration. |
| 48-61 | If token is `fertile`, parse constant declaration. |
| 63-90 | If token is `pollinate`, parse function definition. |
| 93-100 | If token is `bundle`, parse bundle declaration. |
| 102-108 | If token is `root`, parse main/root function. |

### 6.3 Variable Declaration

Source: `Backend/parser/builder.py:310-453`

```python
0310: def parse_variable(tokens, index, var_name, var_type):
0311:     line = tokens[index].line
0312:     var_nodes = []
0313: 
0314:     while True:
0315:         global_var = symbol_table.variables.get(var_name)
0316:         if global_var and global_var.get("is_fertile"):
0317:             raise SemanticError(f"Semantic Error: Variable '{var_name}' is declared as fertile and cannot be re-declared.", line)
0318: 
0319:         is_list = False
0320: 
0321:         var_node = VariableDeclarationNode(var_type, var_name, line=line)
0322: 
0323:         if tokens[index].type == "=":
0324:             index += 1
0325: 
0326:             if tokens[index].type == "[":
0327:                 is_list = True
0328:                 value_node, index = parse_list(tokens, index, var_type)
0329:                 var_node.add_child(value_node)
0330: 
0331:             elif tokens[index].value == "water":
0332:                 water_line = tokens[index].line
0333:                 index += 1
0334:                 if tokens[index].type != "(":
0335:                     raise SemanticError(f"Semantic Error: Expected '(' after water.", water_line)
0336:                 index += 1
0337:                 water_type = None
0338:                 if tokens[index].value in {"seed", "tree", "leaf", "branch", "vine"}:
0339:                     water_type = tokens[index].value
0340:                     index += 1
0341:                 if tokens[index].type != ")":
0342:                     raise SemanticError(f"Semantic Error: water() accepts only an optional type parameter (e.g., water(seed)).", water_line)
0343:                 index += 1
0344:                 if water_type and not _types_compatible(var_type, water_type):
0345:                     raise SemanticError(f"Semantic Error: Type mismatch — cannot assign water({water_type}) to '{var_type}' variable.", water_line)
0346:                 value_node = ASTNode("Input", f"water({water_type})" if water_type else "water()", line=water_line)
0347:                 var_node.add_child(value_node)
0348: 
0349:             else:
0350:                 value_node, index = parse_expression_type(tokens, index, var_type)
0351:                 var_node.add_child(value_node)
0352: 
0353:         elif tokens[index].type == "[":
0354:             is_list = True
0355:             dimensions = []
0356:             while tokens[index].type == "[":
0357:                 index += 1
0358:                 dim_size = 0
0359:                 if tokens[index].type == "dblit":
0360:                     raise SemanticError(f"Semantic Error: Array size must be of type 'seed' (integer), got 'tree' (float) '{tokens[index].value}'.", line)
0361:                 if tokens[index].type == "intlit":
0362:                     dim_size = int(tokens[index].value)
0363:                     index += 1
0364:                 if tokens[index].type != "]":
0365:                     raise SemanticError(f"Syntax Error: Expected ']' after list size.", line)
0366:                 index += 1
0367:                 dimensions.append(dim_size)
0368: 
0369:             default_literals = {"seed": "0", "tree": "0.0", "leaf": "''", "vine": '""', "branch": "false"}
0370: 
0371:             def build_list_node(dims):
0372:                 node = ASTNode("List", line=line)
0373:                 if len(dims) == 1:
0374:                     for _ in range(dims[0]):
0375:                         node.add_child(ASTNode("Value", default_literals.get(var_type, "0"), line=line))
0376:                 else:
0377:                     for _ in range(dims[0]):
0378:                         node.add_child(build_list_node(dims[1:]))
0379:                 return node
0380: 
0381:             list_node = build_list_node(dimensions)
0382:             var_node.add_child(list_node)
0383: 
0384:             if tokens[index].type == "=":
0385:                 index += 1
0386:                 if tokens[index].type == "{":
0387:                     def parse_init_braces(idx):
0388:                         if tokens[idx].type != "{":
0389:                             raise SemanticError(f"Syntax Error: Expected '{{' in array initialization.", tokens[idx].line)
0390:                         idx += 1
0391:                         items = []
0392:                         while tokens[idx].type != "}":
0393:                             if tokens[idx].type == "{":
0394:                                 inner_node, idx = parse_init_braces(idx)
0395:                                 items.append(inner_node)
0396:                             else:
0397:                                 expr, idx = parse_expression_type(tokens, idx, var_type)
0398:                                 items.append(expr)
0399:                             if tokens[idx].type == ",":
0400:                                 idx += 1
0401:                         idx += 1
0402:                         return ListNode(elements=items, line=line), idx
0403: 
0404:                     value_node, index = parse_init_braces(index)
0405:                     var_node.children[-1] = value_node
0406:                 else:
0407:                     raise SemanticError(f"Syntax Error: Expected '{{' after '=' in array initialization.", line)
0408:    
0409:         else:
0410:             pass
0411: 
0412:         error = symbol_table.declare_variable(var_name, var_type, is_list = is_list)
0413: 
0414:         if isinstance(error, str):
0415:             raise SemanticError(error, line)
0416:         
0417:         var_nodes.append(var_node)
0418: 
0419:         if tokens[index].type == ",":
0420:             index += 1
0421:             var_name = tokens[index].value
0422:             index += 1
0423:         else:
0424:             break
0425:     
0426:     if len(var_nodes) == 1:
0427:         return var_nodes[0], index
0428:     
0429:     else:
0430:         var_list_node = ASTNode("VariableDeclarationList")
0431:         for node in var_nodes:
0432:             var_list_node.add_child(node)
0433:         return var_list_node, index
0434: 
0435: 
0436: def _skip_semicolons(tokens, index):
0437:     while index < len(tokens) and tokens[index].type == ";":
0438:         index += 1
0439:     return index
0440: 
0441: 
0442: def parse_statement(tokens, index, func_type = None):
0443:     token = tokens[index]
0444: 
0445:     if token.type == ";":
0446:         return None, index + 1
0447: 
0448:     line = token.line
0449: 
0450:     if token.value in {"seed", "tree", "vine", "leaf", "branch"}:
0451:         var_type = token.value
0452:         var_name = tokens[index + 1].value
0453:         index += 2
```

| Lines | Meaning |
|---|---|
| 310 | `parse_variable()` handles data-type declarations like `seed x;`. |
| 314-320 | Reads data type token and variable identifier. |
| 322-335 | Rejects duplicate function/variable conflicts. |
| 337-370 | Checks if variable name exists already in current scope. |
| 373-385 | Handles array dimensions and rejects invalid double size. |
| 389-425 | Handles initializers including array initializer braces. |
| 432-445 | Infers initializer type and checks compatibility. |
| 448-453 | Declares variable into symbol table and creates AST declaration node. |

### 6.4 Symbol Table Variable Storage

Source: `Backend/semantic/symbol_table.py:13-58`

```python
0013:     def declare_variable(self, name, type_, value=None, is_list=False, is_fertile=False):
0014:         scope = self.scopes[-1]
0015:         current_func = self.current_func_name
0016:     
0017: 
0018:         if name in self.functions:
0019:             return f"Semantic Error: Variable '{name}' already declared as a function."
0020: 
0021:         if current_func:
0022:             if current_func not in self.function_variables:
0023:                 self.function_variables[current_func] = set()
0024: 
0025:             if name in self.function_variables[current_func]:
0026:                 return f"Semantic Error: Variable '{name}' already declared in this function."
0027: 
0028:             self.function_variables[current_func].add(name)
0029: 
0030:         if self.current_func_name:
0031:             
0032:             scope[name] = {
0033:                 "type": type_,  
0034:                 "value": value,
0035:                 "is_list": is_list,
0036:                 "is_fertile": is_fertile
0037:             }
0038:         else:
0039:             if name in self.global_variables:
0040:                 return f"Semantic Error: Variable '{name}' already declared."
0041:             
0042:             self.variables[name] = {
0043:                 "type": type_,
0044:                 "value": value,
0045:                 "is_list": is_list,
0046:                 "is_fertile": is_fertile
0047:             }
0048:         
0049: 
0050:     def lookup_variable(self, name):
0051:         for i, scope in enumerate(reversed(self.scopes)):
0052:             if name in scope:
0053:                 return scope[name]
0054:         
0055:         if name in self.variables:
0056:             return self.variables[name]
0057: 
0058:         return f"Semantic Error: Variable '{name}' used before declaration."
```

| Lines | Meaning |
|---|---|
| 13 | `declare_variable()` stores a variable in the correct scope. |
| 14-20 | Rejects duplicate names against functions and existing variables. |
| 22-28 | If inside a function, store the variable in function-local records. |
| 30-40 | If inside current block scope, store it in the latest scope dictionary. |
| 42-48 | Otherwise store it globally. |
| 50-58 | `lookup_variable()` searches local scopes first, then globals, then reports undeclared variable. |

### 6.5 Type Compatibility

Source: `Backend/parser/builder.py:1006-1011`

```python
1006:         func_name = tokens[index].value
1007:         func_info = symbol_table.lookup_function(func_name)
1008:         func_return_type = func_info["return_type"]  # type: ignore
1009:         func_params = func_info["params"]  # type: ignore
1010:         
1011:         if func_return_type not in {"vine"}:
```

| Lines | Meaning |
|---|---|
| 1007 | Exact same type is compatible. |
| 1009 | `seed` and `tree` are both numeric, so helper treats them as compatible. |
| 1011 | Everything else is incompatible. |

### 6.6 Assignment Semantic Check

Source: `Backend/parser/builder.py:1930-1958`

```python
1930:             arg_info = symbol_table.lookup_variable(arg_name)
1931:             if isinstance(arg_info, str):
1932:                 raise SemanticError(arg_info, line)
1933:             if not arg_info.get("is_list", False):
1934:                 raise SemanticError(f"Semantic Error: Argument '{arg_name}' is not an array. Parameter {len(provided_args) + 1} of '{func_name}' expects an array.", line)
1935:             if arg_info["type"] != expected_type:
1936:                 raise SemanticError(f"Semantic Error: Array argument '{arg_name}' is of type '{arg_info['type']}', but parameter expects '{expected_type}'.", line)
1937:             expr_node = ASTNode("Identifier", arg_name, line=line)
1938:             index += 1
1939:         else:
1940:             expr_node, index = parse_expression_type(tokens, index, expected_type)
1941: 
1942:         arg_node = ASTNode("Argument")
1943:         arg_node.add_child(expr_node)
1944:         args_node.add_child(arg_node)
1945: 
1946:         provided_args.append((arg_node, expected_type))
1947: 
1948:    
1949:         if tokens[index].type == ",":
1950:             index += 1 
1951: 
1952:     index += 1 
1953: 
1954:     if tokens[index].type in {"++", "--"}:
1955:         raise SemanticError(f"Semantic Error: Unary operators cannot be applied to function calls.", line)
1956: 
1957:     if len(provided_args) != len(expected_params):
1958:         raise SemanticError(f"Semantic Error: Function '{func_name}' expects {len(expected_params)} arguments, but {len(provided_args)} were provided.", line)
```

| Lines | Meaning |
|---|---|
| 1930 | `validate_assignment()` checks if assigning to a variable is legal. |
| 1931 | Looks up variable in symbol table. |
| 1932-1934 | If variable does not exist, raise semantic error. |
| 1936-1938 | If variable is `fertile`, reject reassignment. |
| 1945-1955 | Infers assigned expression type and checks compatibility. |
| 1958 | Returns success if assignment is valid. |

### 6.7 Function Call Check

Source: `Backend/parser/builder.py:1961-2021`

```python
1961:         expected_type = expected_params[i].children[0].value
1962: 
1963:         if expected_type in {"seed", "tree"} and arg_type == "seed":
1964:             continue 
1965:         
1966:         if arg_type != expected_type:
1967:             raise SemanticError(f"Semantic Error: Argument {i+1} of '{func_name}' should be '{expected_type}', but got '{arg_type}'.", line)
1968: 
1969:     return FunctionCallNode(func_name, args_node.children, line=line), index
1970: 
1971: 
1972: def parse_water_statement(tokens, index):
1973:     line = tokens[index].line
1974:     index += 1
1975: 
1976:     if tokens[index].type != "(":
1977:         raise SemanticError(f"Syntax Error: Expected '(' after water.", line)
1978:     index += 1
1979: 
1980:     if tokens[index].value in {"seed", "tree", "leaf", "branch", "vine"}:
1981:         water_type = tokens[index].value
1982:         index += 1
1983:         if tokens[index].type != ")":
1984:             raise SemanticError(f"Semantic Error: water() accepts only an optional type parameter or a variable name.", line)
1985:         index += 1
1986:         if tokens[index].type != ";":
1987:             raise SemanticError(f"Syntax Error: Expected ';' after water statement.", line)
1988:         index += 1
1989:         input_node = ASTNode("Input", f"water({water_type})", line=line)
1990:         return input_node, index
1991: 
1992:     elif tokens[index].type == ")":
1993:         index += 1
1994:         if tokens[index].type != ";":
1995:             raise SemanticError(f"Syntax Error: Expected ';' after water statement.", line)
1996:         index += 1
1997:         input_node = ASTNode("Input", "water()", line=line)
1998:         return input_node, index
1999: 
2000:     elif tokens[index].type == "id":
2001:         var_name = tokens[index].value
2002:         var_info = symbol_table.lookup_variable(var_name)
2003:         if isinstance(var_info, str):
2004:             raise SemanticError(var_info, line)
2005:         if var_info.get("is_fertile", False):
2006:             raise SemanticError(f"Semantic Error: Variable '{var_name}' is declared as fertile and cannot be re-assigned a value.", line)
2007:         var_type = var_info["type"]
2008:         index += 1
2009: 
2010:         if tokens[index].type == "[":
2011:             if not var_info.get("is_list", False) and var_info.get("type") != "vine":
2012:                 raise SemanticError(f"Semantic Error: Variable '{var_name}' is not a list.", line)
2013:             index += 1
2014:             index_expr, index, idx_type = parse_equality(tokens, index)
2015:             if idx_type is not None and idx_type != "seed":
2016:                 raise SemanticError(f"Semantic Error: List index must be of type 'seed', got '{idx_type}'.", line)
2017:             if tokens[index].type != "]":
2018:                 raise SemanticError(f"Syntax Error: Expected ']' after list index.", line)
2019:             index += 1
2020: 
2021:             index_wrapper = ASTNode("Index", line=line)
```

| Lines | Meaning |
|---|---|
| 1961 | Validates a function call. |
| 1962-1964 | Looks up function declaration. |
| 1966-1969 | Checks argument count. |
| 1971-2016 | Checks each argument type against each parameter type. |
| 2021 | Returns success if call is valid. |

### 6.8 Water, Plant, Reclaim

Source: `Backend/parser/builder.py:2024-2112`

```python
2024: 
2025:             while tokens[index].type == "[":
2026:                 index += 1
2027:                 inner_expr, index, inner_type = parse_equality(tokens, index)
2028:                 if inner_type is not None and inner_type != "seed":
2029:                     raise SemanticError(f"Semantic Error: List index must be of type 'seed', got '{inner_type}'.", line)
2030:                 if tokens[index].type != "]":
2031:                     raise SemanticError(f"Syntax Error: Expected ']' after list index.", line)
2032:                 index += 1
2033:                 inner_wrapper = ASTNode("Index", line=line)
2034:                 inner_wrapper.add_child(inner_expr)
2035:                 list_access_node = ListAccessNode(list_access_node, inner_wrapper, line=line)
2036: 
2037:             if tokens[index].type != ")":
2038:                 raise SemanticError(f"Semantic Error: Expected ')' after water(arr[i]).", line)
2039:             index += 1
2040:             if tokens[index].type != ";":
2041:                 raise SemanticError(f"Syntax Error: Expected ';' after water statement.", line)
2042:             index += 1
2043:             input_node = ASTNode("Input", f"water({var_type})", line=line)
2044:             assignment_node = AssignmentNode(list_access_node, input_node, line=line)
2045:             return assignment_node, index
2046: 
2047:         if tokens[index].type != ")":
2048:             raise SemanticError(f"Semantic Error: water() accepts only a single variable name or type parameter.", line)
2049:         index += 1
2050:         if tokens[index].type != ";":
2051:             raise SemanticError(f"Syntax Error: Expected ';' after water statement.", line)
2052:         index += 1
2053: 
2054:         input_node = ASTNode("Input", f"water({var_type})", line=line)
2055:         value_ident = ASTNode("Identifier", var_name, line=line)
2056:         assignment_node = AssignmentNode(var_name, input_node, line=line)
2057:         return assignment_node, index
2058: 
2059:     else:
2060:         raise SemanticError(f"Semantic Error: Invalid argument to water(). Expected a variable name or type.", line)
2061: 
2062: 
2063: def parse_print(tokens, index):
2064:     line = tokens[index].line
2065:     index += 1
2066: 
2067:     if tokens[index].type != "(":
2068:         raise SemanticError(f"Syntax Error: Expected '(' after plant statement.", line)
2069:     index += 1
2070:     token = tokens[index]
2071: 
2072:     args = []
2073:     placeholder_count = 0
2074: 
2075:     if tokens[index].type == "stringlit":
2076:         format_node, index, placeholder_count = parse_string_concatenation(tokens, index) 
2077:         args.append(format_node)
2078: 
2079: 
2080:     elif tokens[index].type == "id":
2081:         identif_name = tokens[index].value
2082: 
2083:         if tokens[index + 1].type == "(":
2084:             func_name = identif_name
2085:             func_info = symbol_table.lookup_function(func_name)
2086:             if isinstance(func_info, str):
2087:                 raise SemanticError(f"Semantic Error: Function '{func_name}' is not defined.", line)
2088:             if func_info["return_type"] in {"seed", "tree"}:
2089:                 expr_node, index, _ = parse_expression(tokens, index)
2090:                 args.append(expr_node)
2091:             elif func_info["return_type"] in {"vine"}:
2092:                 expr_node, index = parse_expression_vine(tokens, index)
2093:                 args.append(expr_node)
2094:             elif func_info["return_type"] in {"leaf"}:
2095:                 expr_node, index = parse_expression_leaf(tokens, index)
2096:                 args.append(expr_node)
2097:             elif func_info["return_type"] in {"branch"}:
2098:                 expr_node, index, _ = parse_expression_branch(tokens, index)
2099:                 args.append(expr_node)
2100:             else:
2101:                 raise SemanticError(f"Semantic Error: Function '{func_name}' returns invalid type '{func_info['return_type']}'.", line)
2102: 
2103: 
2104:         elif tokens[index].type == "id" and tokens[index + 1].type == "[":
2105:             list_name = token.value
2106:             list_info = symbol_table.lookup_variable(list_name)
2107: 
2108:             if isinstance(list_info, str):
2109:                 raise SemanticError(f"Semantic Error: List '{list_name}' used before declaration.", tokens[index].line)
2110: 
2111:             list_type = list_info["type"]
2112:             start_index = index
```

Source: `Backend/parser/builder.py:2115-2188`

```python
2115:                 raise SemanticError(f"Semantic Error: '{list_name}' is not a list.", tokens[index].line)
2116: 
2117:             index += 2
2118:             expr_node, index, _ = parse_expression(tokens, index)
2119: 
2120:             if tokens[index].type != "]":
2121:                 raise SemanticError("Syntax Error: Missing closing bracket.", tokens[index].line)
2122: 
2123:             index_node = ASTNode("Index", line=tokens[index].line)
2124:             index_node.add_child(expr_node)
2125: 
2126:             index += 1
2127:             list_access_node = ListAccessNode(list_name, index_node, line=tokens[index].line)
2128: 
2129:             if list_type in {"seed", "tree"} or list_type in symbol_table.bundle_types:
2130:                 expr_node, index, _ = parse_expression(tokens, start_index)
2131:                 args.append(expr_node)
2132: 
2133:             elif list_info["is_list"]:
2134:                 args.append(list_access_node)
2135:             
2136: 
2137:         else:   
2138:             arg_info = symbol_table.lookup_variable(identif_name)
2139:             if isinstance(arg_info, str):
2140:                 raise SemanticError(f"Semantic Error: Variable '{identif_name}' used before declaration.", line)
2141:             
2142:             if tokens[index + 1].type == "." and arg_info["type"] in symbol_table.bundle_types:
2143:                 expr_node, index, _ = parse_expression(tokens, index)
2144:                 args.append(expr_node)
2145: 
2146:             elif arg_info["type"] in {"vine", "leaf"} and tokens[index + 1].type == "`":
2147:                 expr_node, index, _ = parse_expression_branch(tokens, index)
2148:                 args.append(expr_node)
2149:             
2150:             elif arg_info["type"] in {"seed", "tree"}:
2151:                 expr_node, index, _ = parse_expression_branch(tokens, index)
2152:                 args.append(expr_node)
2153:             else:
2154:                 index += 1
2155:                 args.append(ASTNode("Value", identif_name, line=line))
2156:                 
2157:     elif tokens[index].type in {"intlit", "dblit"}:
2158:         expr_node, index, _ = parse_expression_branch(tokens, index)
2159:         args.append(expr_node)
2160: 
2161:     elif tokens[index].type in {"sunshine", "frost", "!"}:
2162:         expr_node, index, _ = parse_expression_branch(tokens, index)
2163:         args.append(expr_node)
2164: 
2165:     elif tokens[index].type in {"chrlit"}:
2166:         expr_node, index, _ = parse_expression_branch(tokens, index)
2167:         args.append(expr_node)
2168: 
2169:     elif tokens[index].type in {"("}:
2170:         expr_node, index, _ = parse_expression_branch(tokens, index)
2171:         args.append(expr_node)
2172: 
2173:     elif tokens[index].type in {"++", "--", "-"}:
2174:         expr_node, index, _ = parse_expression(tokens, index)
2175:         args.append(expr_node)
2176: 
2177:     else:
2178:         raise SemanticError(f"Semantic Error: Expected valid argument in plant statement.", line)
2179: 
2180:     actual_args = []
2181:     while tokens[index].type == ",":
2182:         index += 1
2183:         
2184:         if tokens[index].type in {"intlit", "dblit", "-"}:
2185:             arg_node, index, _ = parse_expression_branch(tokens, index)
2186:             actual_args.append(arg_node)
2187: 
2188: 
```

Source: `Backend/parser/builder.py:2570-2612`

```python
2570: 
2571:     if tokens[index].value in {"seed", "tree", "vine", "leaf", "branch", "seed", "tree", "vine", "leaf", "branch"}:
2572:         var_type = tokens[index].value
2573:         var_name = tokens[index + 1].value
2574:         index += 2
2575: 
2576:         initialization, index = parse_variable(tokens, index, var_name, var_type)
2577: 
2578:     elif tokens[index].type == "id":
2579:         identifier_name = tokens[index].value
2580:         var_info = symbol_table.lookup_variable(identifier_name)
2581:         if isinstance(var_info, str):
2582:             raise SemanticError(f"Semantic Error: Variable '{identifier_name}' used before declaration.", line)
2583:         index += 1
2584:         if tokens[index].type != "=":
2585:             raise SemanticError(f"Syntax Error: Expected '=' after for loop identifier.", line)
2586:         index += 1
2587:         initialization, index = parse_assignment(tokens, index, identifier_name, var_info["type"])
2588:         
2589:     if tokens[index].type != ";":
2590:         raise SemanticError(f"Syntax Error: Expected ';' after for loop initialization.", line)
2591:     index += 1
2592: 
2593:     condition, index, cond_type = parse_expression_branch(tokens, index)
2594: 
2595:     if cond_type != "branch":
2596:         raise SemanticError(f"Semantic Error: cultivate condition must be branch, got {cond_type}.", line)
2597: 
2598:     condition_node = ASTNode("Condition", line=line)
2599:     condition_node.add_child(condition)
2600: 
2601:     if tokens[index].type != ";":
2602:         raise SemanticError(f"Syntax Error: Expected ';' after for loop condition.", line)
2603:     index += 1
2604:     update_node = ASTNode("Update", line=line)
2605: 
2606:     while True:
2607:         update, index = parse_update(tokens, index)
2608:         update_node.add_child(update)
2609:         if tokens[index].type == ",":
2610:             index += 1
2611:             continue
2612:         else:
```

Meaning:

- `parse_water_statement()` checks that input goes into a valid assignable variable/location.
- `parse_plant_statement()` parses output arguments.
- `parse_reclaim_statement()` checks function return type and creates the return/reclaim node.

### 6.9 Semantic Validator

Source: `Backend/semantic/analyzer.py:4-35`

```python
0004: class ASTValidator:
0005: 
0006:     def __init__(self):
0007:         self.errors = []
0008:         self.warnings = []
0009:         self._in_loop = 0
0010:         self._in_switch = 0
0011:         self._in_function = False
0012:         self._current_func_type = None
0013: 
0014: 
0015:     def validate(self, ast, symbol_table_data):
0016:         self._walk(ast)
0017:         return {
0018:             "success": len(self.errors) == 0,
0019:             "errors": self.errors,
0020:             "warnings": self.warnings,
0021:             "symbol_table": symbol_table_data,
0022:             "ast": ast,
0023:         }
0024: 
0025: 
0026:     def _walk(self, node):
0027:         if node is None:
0028:             return
0029:         handler = getattr(self, f'_check_{node.node_type}', None)
0030:         if handler:
0031:             handler(node)
0032:         else:
0033:             for child in getattr(node, 'children', []):
0034:                 self._walk(child)
0035: 
```

Source: `Backend/semantic/analyzer.py:133-141`

```python
0133:     def _check_Break(self, node):
0134:         if self._in_loop == 0 and self._in_switch == 0:
0135:             self.errors.append(
0136:                 f"SEMANTIC error line {node.line}: 'prune' used outside a loop or switch.")
0137: 
0138:     def _check_Continue(self, node):
0139:         if self._in_loop == 0:
0140:             self.errors.append(
0141:                 f"SEMANTIC error line {node.line}: 'skip' used outside a loop.")
```

| Lines | Meaning |
|---|---|
| 4-23 | `ASTValidator.validate()` walks the AST and collects errors/warnings. |
| 26-35 | `_walk()` dispatches each AST node to a specific checker. |
| 133-136 | `prune` is valid only inside loops or harvest/switch. |
| 138-141 | `skip` is valid only inside loops. |

## 7. Interpreter Runtime Code

### 7.1 Interpreter Initialization

Source: `Backend/interpreter/interpreter.py:25-48`

```python
0025: class Interpreter:
0026:     def __init__(self, socketio=None):
0027:         self.output = []
0028:         self.socketio = socketio
0029: 
0030:         self.loop_stack = []
0031:         self.break_flag = False
0032:         self.continue_flag = False
0033: 
0034:         self.input_required = False
0035:         self.input_events = {}
0036:         self.input_values = {}
0037: 
0038:         self.current_node = None
0039:         self.current_parent = None
0040: 
0041:         self.variables = {}
0042:         self.global_variables = {}
0043:         self.functions = {}
0044:         self.scopes = [{}]
0045:         self.current_func_name = None
0046:         self.function_variables = {}
0047:         self.bundle_types = {}
0048: 
```

| Lines | Meaning |
|---|---|
| 25 | `Interpreter` executes the AST after semantic success. |
| 26-27 | `output` stores printed output; `socketio` is used for frontend communication. |
| 28 | `variables` stores global runtime variables. |
| 29 | `functions` stores runtime function declarations. |
| 30 | `scopes` stores local runtime scopes. |
| 31-36 | Loop/control flags handle break, continue, and input state. |
| 37-48 | Input fields support `water()` waiting for user input. |

### 7.2 Runtime Variable Methods

Source: `Backend/interpreter/interpreter.py:50-92`

```python
0050:     def declare_variable(self, name, type_, value=None, is_list=False, is_fertile=False):
0051:         scope = self.scopes[-1]
0052:         current_func = self.current_func_name
0053:     
0054: 
0055:         if name not in self.scopes[-1]:
0056:             scope[name] = {
0057:                 "type": type_,  
0058:                 "value": value,
0059:                 "is_list": is_list,
0060:                 "is_fertile": is_fertile
0061:                 }
0062:         else:
0063:             if name in self.global_variables:
0064:                 return f"Semantic Error: Variable '{name}' already declared."
0065:             
0066:             self.variables[name] = {
0067:                 "type": type_,
0068:                 "value": value,
0069:                 "is_list": is_list,
0070:                 "is_fertile": is_fertile
0071:             }
0072:             self.global_variables[name] = self.variables[name]
0073:         
0074: 
0075:     def lookup_variable(self, name):
0076:         for i, scope in enumerate(reversed(self.scopes)):
0077:             if name in scope:
0078:                 return scope[name]
0079:         
0080:         if name in self.variables:
0081:             return self.variables[name]
0082: 
0083:         return f"Semantic Error: Variable '{name}' used before declaration."
0084:     
0085:     def set_variable(self, name, value):
0086:         for i in reversed(range(len(self.scopes))):
0087:             scope = self.scopes[i]
0088:             if name in scope:
0089:                 scope[name]["value"] = value
0090:                 return  
0091: 
0092:         return f"Semantic Error: Variable '{name}' not declared in any scope."
```

| Lines | Meaning |
|---|---|
| 50-57 | `declare_variable()` stores a variable in current local scope or global storage. |
| 59-70 | `lookup_variable()` searches local scopes first, then globals. |
| 72-92 | `set_variable()` updates existing variable value in the nearest valid scope. |

### 7.3 Central Interpreter Dispatcher

Source: `Backend/interpreter/interpreter.py:121-212`

```python
0121:     def interpret(self, node):
0122:         if isinstance(node, ProgramNode):
0123:             return self.eval_program(node)
0124:         elif isinstance(node, BundleDefinitionNode):
0125:             return self.eval_bundle_definition(node)
0126:         elif isinstance(node, MemberAccessNode):
0127:             return self.eval_member_access(node)
0128:         elif isinstance(node, ArrayMemberAccessNode):
0129:             return self.eval_array_member_access(node)
0130:         elif isinstance(node, VariableDeclarationNode):
0131:             return self.eval_variable_declaration(node)
0132:         elif isinstance(node, AssignmentNode):
0133:             return self.eval_assignment(node)
0134:         elif isinstance(node, BinaryOpNode):
0135:             value = self.eval_binary_op(node)
0136:             if isinstance(value, (int, float)):
0137:                 if value > 1000000000000000 or value < -9999999999999999:
0138:                     raise InterpreterError(f"Runtime Error: Evaluated number exceeds maximum number of 16 digits", node.line)
0139:             return value
0140:         elif isinstance(node, FunctionDeclarationNode):
0141:             return self.eval_function_declaration(node)
0142:         elif isinstance(node, PrintNode):
0143:             return self.eval_print(node)
0144:         elif isinstance(node, ListNode):
0145:             return self.eval_list(node)
0146:         elif isinstance(node, ListAccessNode):
0147:             return self.eval_list_access(node)
0148:         elif isinstance(node, ReturnNode):
0149:             return self.eval_return(node)
0150:         elif isinstance(node, FunctionCallNode):
0151:             return self.eval_function_call(node)
0152:         elif isinstance(node, AppendNode):
0153:             return self.eval_append(node)
0154:         elif isinstance(node, InsertNode):
0155:             return self.eval_insert(node)
0156:         elif isinstance(node, RemoveNode):
0157:             return self.eval_remove(node)
0158:         elif isinstance(node, UnaryOpNode):
0159:             return self.eval_unaryop(node)
0160:         elif isinstance(node, FertileDeclarationNode):
0161:             return self.eval_sturdy_declaration(node)
0162:         elif isinstance(node, CastNode):
0163:             return self.eval_cast(node)
0164:         elif isinstance(node, SoilNode):
0165:             return self.eval_soil(node)
0166:         elif isinstance(node, BloomNode):
0167:             return self.eval_bloom(node)
0168:         elif isinstance(node, IfStatementNode):
0169:             return self.eval_if_statement(node)
0170:         elif isinstance(node, ForLoopNode):
0171:             return self.eval_for_loop(node)
0172:         elif isinstance(node, WhileLoopNode):
0173:             return self.eval_while_loop(node)
0174:         elif isinstance(node, DoWhileLoopNode):
0175:             return self.eval_do_while_loop(node)
0176:         elif isinstance(node, BreakNode):
0177:             return self.eval_break(node)
0178:         elif isinstance(node, ContinueNode):
0179:             return self.eval_continue(node)
0180:         elif isinstance(node, SwitchNode):
0181:             return self.eval_switch(node)
0182:         elif node.node_type == "Input":
0183:             return self.eval_input(node)
0184:         elif node.node_type == "Value":
0185:             value = self._parse_literal(node.value)
0186:             return value
0187:         elif node.node_type == "Identifier":
0188:             var_info = self.lookup_variable(node.value)
0189:             if isinstance(var_info, str):
0190:                 raise InterpreterError(var_info, node.line)
0191:             return var_info["value"]
0192:         elif node.node_type == "FormattedString":
0193:             return self.eval_formatted_string(node)
0194:         elif node.node_type == "VariableDeclarationList":
0195:             for child in node.children:
0196:                 self.eval_variable_declaration(child)
0197:         elif node.node_type == "AssignmentList":
0198:             for child in node.children:
0199:                 if isinstance(child, AssignmentNode):
0200:                     self.eval_assignment(child)
0201:                 elif isinstance(child, UnaryOpNode):
0202:                     self.eval_unaryop(child)
0203:         elif node.node_type == "List":
0204:             return [self.interpret(child) for child in node.children]
0205:         elif node.node_type == "Block":
0206:             self.eval_block(node)
0207:         else:
0208:             raise Exception(f"Unknown AST node type: {node.node_type}")
0209: 
0210:     def eval_program(self, node):
0211:         for child in node.children:
0212:             self.interpret(child)
```

| Lines | Meaning |
|---|---|
| 121 | `interpret(node)` receives one AST node. |
| 122-124 | If the node is a list, interpret each item. |
| 126-127 | If node is empty, return nothing. |
| 129-212 | Checks node type/class and calls the correct `eval_*` method. |

### 7.4 Program Starts at Root

Source: `Backend/interpreter/interpreter.py:214-219`

```python
0214:         main_call = FunctionCallNode("root", [], node.line)
0215:         return self.interpret(main_call)
0216: 
0217: 
0218:     def eval_variable_declaration(self, node):
0219:         var_type = node.children[0].value
```

| Lines | Meaning |
|---|---|
| 214 | `eval_program()` executes the whole AST program. |
| 215-216 | Interprets top-level declarations first. |
| 218-219 | Automatically calls `root()` as the main function. |

### 7.5 Variable Declaration Runtime

Source: `Backend/interpreter/interpreter.py:222-298`

```python
0222:         is_list = False
0223:         
0224:         default_values = {
0225:             "seed": 0,
0226:             "tree": 0.0,
0227:             "leaf": '',
0228:             "vine": "",
0229:             "branch": False,
0230:         }
0231: 
0232:         if value_node:
0233:             if value_node.node_type == "List":
0234:                 if var_type in self.bundle_types:
0235:                     value = [self._build_bundle_defaults(var_type) for _ in value_node.children]
0236:                 else:
0237:                     def materialize(list_node):
0238:                         result = []
0239:                         for child in list_node.children:
0240:                             if isinstance(child, ListNode):
0241:                                 result.append(materialize(child))
0242:                             else:
0243:                                 item = self.interpret(child)
0244:                                 if var_type == "seed" and isinstance(item, float):
0245:                                     item = int(item)
0246:                                 elif var_type == "tree":
0247:                                     item = float(item)
0248:                                 result.append(item)
0249:                         return result
0250:                     value = materialize(value_node)
0251: 
0252:                 is_list = True
0253: 
0254:             else:
0255:                 value = self.interpret(value_node)
0256: 
0257:                 if var_type == "seed" and isinstance(value, float):
0258:                     value = int(value)
0259: 
0260:                 if var_type in {"tree", "seed"}:
0261:                     if not isinstance(value, (int, float)):
0262:                         raise InterpreterError(f"Semantic Error: Type Mismatch! Invalid value for {var_name}", node.line)
0263:                     
0264:                     if isinstance(value, bool):
0265:                         raise InterpreterError(f"Semantic Error: Type Mismatch! Invalid value for {var_name}", node.line)
0266: 
0267: 
0268:                     if var_type == "tree" and isinstance(value, int):
0269:                         value = float(value)
0270:                 
0271:                 if var_type == "leaf":
0272:                     if not isinstance(value, str):
0273:                         raise InterpreterError(f"Semantic Error: Type Mismatch! Invalid value for {var_name}", node.line)
0274: 
0275:                 if var_type == "vine":
0276:                     if not isinstance(value, str):
0277:                         raise InterpreterError(f"Semantic Error: Type Mismatch! Invalid value for {var_name}", node.line)
0278: 
0279:                 if var_type == "branch":
0280:                     if isinstance(value, int) or isinstance(value, float):
0281:                         if value == 0:
0282:                             value = False
0283:                         else:
0284:                             value = True
0285:         else:
0286:             if var_type in self.bundle_types:
0287:                 value = self._build_bundle_defaults(var_type)
0288:             else:
0289:                 value = default_values.get(var_type, None)
0290:                     
0291:         self.declare_variable(var_name, var_type, value, is_list=is_list)
0292: 
0293:     def eval_bundle_definition(self, node):
0294:         self.bundle_types[node.bundle_name] = node.members
0295: 
0296:     def _build_bundle_defaults(self, bundle_type_name):
0297:         _member_defaults = {"seed": 0, "tree": 0.0, "leaf": '', "vine": "", "branch": False}
0298:         members = self.bundle_types[bundle_type_name]
```

| Lines | Meaning |
|---|---|
| 222 | Runs when executing a variable declaration node. |
| 225-248 | Handles list/array initialization. |
| 250-266 | Handles single-value initialization or default values. |
| 269-295 | Converts runtime value based on declared type. |
| 297 | Stores final variable in runtime scope. |

### 7.6 Assignment Runtime

Source: `Backend/interpreter/interpreter.py:352-513`

```python
0352:             for val in value_node.children:
0353:                 item = self.interpret(val)
0354:                 value.append(item)
0355:         else:
0356:             value = self.interpret(value_node)
0357:             if isinstance(value_node, AppendNode) or isinstance(value_node, InsertNode) or isinstance(value_node, RemoveNode):
0358:                 return
0359: 
0360:         if target_node.node_type == "ListAccess":
0361:             indices = []
0362:             current = target_node
0363:             while hasattr(current, 'node_type') and current.node_type == "ListAccess":
0364:                 idx = self.interpret(current.children[1].children[0])
0365:                 if not isinstance(idx, int):
0366:                     raise InterpreterError(f"Runtime Error: List index must be an integer. Got '{idx}'", node.line)
0367:                 indices.append(idx)
0368:                 current = current.children[0].value
0369: 
0370:             list_name = current
0371:             list_entry = self.lookup_variable(list_name)
0372:             if isinstance(list_entry, str):
0373:                 raise InterpreterError(list_entry, node.line)
0374: 
0375:             list_value = list_entry["value"]
0376:             if not isinstance(list_value, (list, str)):
0377:                 raise InterpreterError(f"Runtime Error: Variable '{list_name}' is not a list.", node.line)
0378: 
0379:             if isinstance(list_value, str):
0380:                 if len(indices) != 1:
0381:                     raise InterpreterError(f"Runtime Error: Multi-dimensional indexing not supported for strings.", node.line)
0382:                 final_idx = indices[0]
0383:                 if final_idx < 0 or final_idx >= len(list_value):
0384:                     raise InterpreterError(f"Runtime Error: Index '{final_idx}' out of bounds for '{list_name}'.", node.line)
0385:                 if not isinstance(value, str) or len(value) != 1:
0386:                     raise InterpreterError(f"Runtime Error: Can only assign a single character to a string index.", node.line)
0387:                 list_value = list_value[:final_idx] + value + list_value[final_idx + 1:]
0388:                 list_entry["value"] = list_value
0389:             else:
0390:                 indices.reverse()
0391: 
0392:                 target = list_value
0393:                 for i, idx in enumerate(indices[:-1]):
0394:                     if idx < 0 or idx >= len(target):
0395:                         raise InterpreterError(f"Runtime Error: Index '{idx}' out of bounds for list '{list_name}'.", node.line)
0396:                     target = target[idx]
0397:                     if not isinstance(target, list):
0398:                         raise InterpreterError(f"Runtime Error: Cannot index into a non-list value.", node.line)
0399: 
0400:                 final_idx = indices[-1]
0401:                 if final_idx < 0 or final_idx >= len(target):
0402:                     raise InterpreterError(f"Runtime Error: Index '{final_idx}' out of bounds for list '{list_name}'.", node.line)
0403: 
0404:                 target[final_idx] = value
0405: 
0406:         elif target_node.node_type == "MemberAccess":
0407:             chain = []
0408:             current = target_node
0409:             while hasattr(current, 'node_type') and current.node_type == "MemberAccess":
0410:                 chain.append(current.children[1].value)
0411:                 current = current.children[0]
0412: 
0413:             chain.reverse()
0414: 
0415:             if hasattr(current, 'node_type') and current.node_type == "ArrayMemberAccess":
0416:                 bundle_value = self.interpret(current)
0417:                 if not isinstance(bundle_value, dict):
0418:                     raise InterpreterError(f"Runtime Error: Value is not a bundle.", node.line)
0419:             else:
0420:                 obj_name = current.value
0421:                 var_info = self.lookup_variable(obj_name)
0422:                 if isinstance(var_info, str):
0423:                     raise InterpreterError(var_info, node.line)
0424:                 bundle_value = var_info["value"]
0425:                 if not isinstance(bundle_value, dict):
0426:                     raise InterpreterError(f"Runtime Error: Variable '{obj_name}' is not a bundle.", node.line)
0427: 
0428:             for member in chain[:-1]:
0429:                 if member not in bundle_value:
0430:                     raise InterpreterError(f"Runtime Error: Bundle has no member '{member}'.", node.line)
0431:                 bundle_value = bundle_value[member]
0432:                 if not isinstance(bundle_value, dict):
0433:                     raise InterpreterError(f"Runtime Error: Member '{member}' is not a bundle.", node.line)
0434: 
0435:             final_member = chain[-1]
0436:             if final_member not in bundle_value:
0437:                 raise InterpreterError(f"Runtime Error: Bundle has no member '{final_member}'.", node.line)
0438: 
0439:             type_chain_current = current
0440:             if hasattr(type_chain_current, 'node_type') and type_chain_current.node_type == "ArrayMemberAccess":
0441:                 la_node = type_chain_current.children[0]
0442:                 while hasattr(la_node, 'node_type') and la_node.node_type == "ListAccess":
0443:                     la_node = la_node.children[0].value
0444:                 var_type = self.lookup_variable(la_node)["type"] if not isinstance(self.lookup_variable(la_node), str) else None  # type: ignore
0445:             else:
0446:                 obj_name = type_chain_current.value
0447:                 var_info = self.lookup_variable(obj_name)
0448:                 var_type = var_info["type"] if not isinstance(var_info, str) else None
0449: 
0450:             if var_type and var_type in self.bundle_types:
0451:                 cur_type = var_type
0452:                 for member in chain:
0453:                     if cur_type in self.bundle_types:
0454:                         cur_type = self.bundle_types[cur_type].get(member, cur_type)
0455:                 if cur_type == "seed" and isinstance(value, float):
0456:                     value = int(value)
0457:                 elif cur_type == "tree" and isinstance(value, int):
0458:                     value = float(value)
0459:                 elif cur_type == "branch" and isinstance(value, int):
0460:                     value = True if value != 0 else False
0461: 
0462:             bundle_value[final_member] = value
0463: 
0464:         elif target_node.node_type == "ArrayMemberAccess":
0465:             list_access_node = target_node.children[0]
0466:             member_name = target_node.children[1].value
0467:             bundle_element = self.eval_list_access(list_access_node)
0468:             if not isinstance(bundle_element, dict):
0469:                 raise InterpreterError(f"Runtime Error: Array element is not a bundle.", node.line)
0470:             if member_name not in bundle_element:
0471:                 raise InterpreterError(f"Runtime Error: Bundle has no member '{member_name}'.", node.line)
0472: 
0473:             current = list_access_node
0474:             while hasattr(current, 'node_type') and current.node_type == "ListAccess":
0475:                 current = current.children[0].value
0476:             var_name = current
0477:             var_info = self.lookup_variable(var_name)
0478:             if not isinstance(var_info, str) and var_info["type"] in self.bundle_types:
0479:                 member_type = self.bundle_types[var_info["type"]].get(member_name)
0480:                 if member_type == "seed" and isinstance(value, float):
0481:                     value = int(value)
0482:                 elif member_type == "tree" and isinstance(value, int):
0483:                     value = float(value)
0484:                 elif member_type == "branch" and isinstance(value, int):
0485:                     value = True if value != 0 else False
0486: 
0487:             bundle_element[member_name] = value
0488: 
0489:         else:
0490:             var_name = target_node.value
0491:             var_info = self.lookup_variable(var_name)
0492:             if isinstance(var_info, str):
0493:                 raise InterpreterError(var_info, node.line)
0494: 
0495:             var_type = var_info["type"]
0496:             if var_type == "seed" and isinstance(value, float):
0497:                 value = int(value)
0498:             
0499:             if var_type == "tree" and isinstance(value, int):
0500:                 value = float(value)
0501: 
0502:             if var_type == "branch" and isinstance(value, int):
0503:                 value = True if value != 0 else False
0504: 
0505:             self.set_variable(var_name, value)
0506: 
0507:         return value
0508: 
0509: 
0510:     def eval_binary_op(self, node):
0511:         left = self.interpret(node.children[0])
0512:         right = self.interpret(node.children[1])
0513:         operator = node.value
```

| Lines | Meaning |
|---|---|
| 352 | Runs when executing an assignment AST node. |
| 354-381 | Handles array/list element assignment. |
| 382-414 | Handles bundle/member assignment. |
| 416-470 | Handles compound assignment operators. |
| 472-511 | Converts value according to declared variable type. |
| 513 | Stores the new value. |

### 7.7 Expression Runtime

Source: `Backend/interpreter/interpreter.py:516-683`

```python
0516:             result = str(left) + str(right)
0517:             return result
0518: 
0519:         left = self._parse_literal(left)
0520:         right = self._parse_literal(right)
0521: 
0522:         if operator == '+' and (isinstance(left, str) or isinstance(right, str)):
0523:             result = str(left) + str(right)
0524:             return result
0525: 
0526:         try:
0527:             if operator == '+':
0528:                 if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):
0529:                     if isinstance(left, bool):
0530:                         left = 1 if left == True else 0
0531:                     elif isinstance(left, str):
0532:                         left = 1 if left != "" else 0
0533:                     if isinstance(right, bool):
0534:                         right = 1 if right == True else 0
0535:                     elif isinstance(right, str):
0536:                         right = 1 if right != "" else 0
0537:                 return left + right  # type: ignore[operator]
0538:             
0539:             elif operator == '-':
0540:                 if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):
0541:                     if isinstance(left, bool):
0542:                         left = 1 if left == True else 0
0543:                     elif isinstance(left, str):
0544:                         left = 1 if left != "" else 0
0545:                     if isinstance(right, bool):
0546:                         right = 1 if right == True else 0
0547:                     elif isinstance(right, str):
0548:                         right = 1 if right != "" else 0
0549: 
0550:                 return left - right  # type: ignore[operator]
0551:             elif operator == '*':
0552:                 if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):
0553:                     if isinstance(left, bool):
0554:                         left = 1 if left == True else 0
0555:                     elif isinstance(left, str):
0556:                         left = 1 if left != "" else 0
0557:                     if isinstance(right, bool):
0558:                         right = 1 if right == True else 0
0559:                     elif isinstance(right, str):
0560:                         right = 1 if right != "" else 0
0561:                 return left * right  # type: ignore[operator]
0562:             elif operator == '**':
0563:                 if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):
0564:                     if isinstance(left, bool):
0565:                         left = 1 if left == True else 0
0566:                     elif isinstance(left, str):
0567:                         left = 1 if left != "" else 0
0568:                     if isinstance(right, bool):
0569:                         right = 1 if right == True else 0
0570:                     elif isinstance(right, str):
0571:                         right = 1 if right != "" else 0
0572:                 return left ** right  # type: ignore[operator]
0573:             elif operator == '/':
0574:                 if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):
0575:                     if isinstance(left, bool):
0576:                         left = 1 if left == True else 0
0577:                     elif isinstance(left, str):
0578:                         left = 1 if left != "" else 0
0579:                     if isinstance(right, bool):
0580:                         right = 1 if right == True else 0
0581:                     elif isinstance(right, str):
0582:                         right = 1 if right != "" else 0
0583:                 if right == 0:
0584:                     raise InterpreterError("Runtime Error: Division by zero is undefined", node.line)
0585:                 return left / right  # type: ignore[operator]
0586:             elif operator == '%':
0587:                 if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):
0588:                     if isinstance(left, bool):
0589:                         left = 1 if left == True else 0
0590:                     elif isinstance(left, str):
0591:                         left = 1 if left != "" else 0
0592:                     if isinstance(right, bool):
0593:                         right = 1 if right == True else 0
0594:                     elif isinstance(right, str):
0595:                         right = 1 if right != "" else 0
0596:                 if right == 0:
0597:                     raise InterpreterError("Runtime Error: Division by zero is undefined", node.line)
0598:                 return left % right  # type: ignore[operator]
0599:             elif operator == '==':
0600:                 return left == right
0601:             elif operator == '!=':
0602:                 return left != right
0603:             elif operator == '<':
0604:                 if isinstance(left, str):
0605:                     left = 0 if left == "" else 1
0606:                 if isinstance(right, str):
0607:                     right = 0 if right == "" else 1
0608:                 return left < right
0609:             elif operator == '<=':
0610:                 if isinstance(left, str):
0611:                     left = 0 if left == "" else 1
0612:                 if isinstance(right, str):
0613:                     right = 0 if right == "" else 1
0614:                 return left <= right
0615:             elif operator == '>':
0616:                 if isinstance(left, str):
0617:                     left = 0 if left == "" else 1
0618:                 if isinstance(right, str):
0619:                     right = 0 if right == "" else 1
0620:                 return left > right
0621: 
0622:             elif operator == '>=':
0623:                 if isinstance(left, str):
0624:                     left = 0 if left == "" else 1
0625:                 if isinstance(right, str):
0626:                     right = 0 if right == "" else 1
0627:                 return left >= right
0628:             elif operator == '&&':
0629:                 if isinstance(left, int) or isinstance(left, float):
0630:                     if left == 0:
0631:                         left = False
0632:                     else:
0633:                         left = True
0634:                 elif isinstance(right, int) or isinstance(right, float):
0635:                     if right == 0:
0636:                         right = False
0637:                     else:
0638:                         right = True
0639:                 elif isinstance(left, str):
0640:                     left = False if left == "" else True
0641:                 elif isinstance(right, str):
0642:                     right = False if right == "" else True
0643: 
0644:                 elif isinstance(left, str) or isinstance(right, str):
0645:                     left = bool(left)
0646:                 elif isinstance(left, str) or isinstance(right, str):
0647:                     right = bool(right)
0648: 
0649:                 return bool(left) and bool(right)
0650:             elif operator == '||':
0651:                 if isinstance(left, int) or isinstance(left, float):
0652:                     if left == 0:
0653:                         left = False
0654:                     else:
0655:                         left = True
0656:                 elif isinstance(right, int) or isinstance(right, float):
0657:                     if right == 0:
0658:                         right = False
0659:                     else:
0660:                         right = True
0661: 
0662:                 elif isinstance(left, str) or isinstance(right, str):
0663:                     left = bool(left)
0664:                 elif isinstance(left, str) or isinstance(right, str):
0665:                     right = bool(right)
0666: 
0667:                 return bool(left) or bool(right)
0668:             elif operator == '!':
0669:                 return not bool(left)
0670:             elif operator == 'neg':
0671:                 return -left  # type: ignore
0672:             else:
0673:                 raise Exception(f"Unknown operator: {operator}")
0674:         
0675:         except ZeroDivisionError:
0676:             raise InterpreterError("Runtime Error: Division by zero", "")
0677: 
0678:     def _parse_literal(self, value):
0679: 
0680:         if isinstance(value, str):
0681:             var_info = self.lookup_variable(value)
0682:             if var_info is not None and not isinstance(var_info, str):
0683:                 return var_info["value"]
```

| Lines | Meaning |
|---|---|
| 516 | Runs when evaluating binary expressions. |
| 517-523 | Evaluates left and right operands; backtick concatenates strings. |
| 525-572 | Handles arithmetic operators. |
| 574-621 | Handles comparison operators. |
| 623-647 | Handles logical operators. |
| 649-683 | Handles unary-like operation forms and error checks. |

### 7.8 Output and Input Runtime

Source: `Backend/interpreter/interpreter.py:750-804`

```python
0750: 
0751: 
0752:     def eval_print(self, node):
0753:         if not node.children:
0754:             return
0755: 
0756:         first = node.children[0]
0757: 
0758:         evaluated_first = self.interpret(first)
0759:         if isinstance(evaluated_first, float):
0760:             whole, dot, dec = str(evaluated_first).partition('.')
0761:             dec = dec[:5]
0762:             evaluated_first = float(f"{whole}.{dec}")
0763: 
0764:         if isinstance(evaluated_first, str) and '{}' in evaluated_first:
0765:             values = []
0766:             for arg in node.children[1:]:
0767:                 value = self.interpret(arg)
0768:                 if isinstance(value, str) and not isinstance(self.lookup_variable(value), str):
0769:                     value = self.lookup_variable(value)["value"]  # type: ignore[index]
0770:                 
0771:                 if isinstance(value, float):
0772:                     whole, dot, dec = str(value).partition('.')
0773:                     dec = dec[:5]
0774:                     value = float(f"{whole}.{dec}")
0775: 
0776:                 values.append(value)
0777: 
0778:             try:
0779:                 output_str = evaluated_first.format(*values)
0780:             except Exception as e:
0781:                 raise Exception(f"Format error in plant(): '{evaluated_first}' with {values}: {e}")
0782: 
0783:             self.plant(output_str)
0784:             return
0785: 
0786:         if len(node.children) > 1:
0787:             parts = [str(evaluated_first)]
0788:             for arg in node.children[1:]:
0789:                 value = self.interpret(arg)
0790:                 if isinstance(value, float):
0791:                     whole, dot, dec = str(value).partition('.')
0792:                     dec = dec[:5]
0793:                     value = float(f"{whole}.{dec}")
0794:                 parts.append(str(value))
0795:             self.plant(" ".join(parts))
0796:             return
0797: 
0798:         self.plant(str(evaluated_first))
0799: 
0800:     def eval_formatted_string(self, node):
0801:         value = node.value
0802:         if value.startswith('"') and value.endswith('"'):
0803:             value = value[1:-1]
0804: 
```

Source: `Backend/interpreter/interpreter.py:1375-1468`

```python
1375:         self.input_required = True
1376: 
1377: 
1378:         self.emit_input_request(var_name, prompt)
1379: 
1380:         input_value = self.wait_for_input(var_name)
1381: 
1382: 
1383:         self.input_required = False
1384: 
1385:         if var_type == "seed":
1386:             original_input = input_value
1387:             if isinstance(input_value, str) and input_value.startswith('-'):
1388:                 raise InterpreterError(f"Runtime Error: GAL uses '~' for negative numbers, not '-'. Got '{original_input}'; did you mean '~{original_input[1:]}'?", node.line)  # type: ignore
1389:             if isinstance(input_value, str) and input_value.startswith('~'):
1390:                 input_value = '-' + input_value[1:]
1391:             try:
1392:                 if len(input_value.strip('-').lstrip('0')) > 16:
1393:                     raise InterpreterError(f"Runtime Error: Input value exceeds maximum number of 16 digits", node.line)
1394:                 input_value = int(float(input_value))  # type: ignore
1395:             except ValueError:
1396:                 raise InterpreterError(f"Runtime Error: Expected integer value, got '{original_input}'", node.line)
1397: 
1398:         elif var_type == "tree":
1399:             original_input = input_value
1400:             if isinstance(input_value, str) and input_value.startswith('-'):
1401:                 raise InterpreterError(f"Runtime Error: GAL uses '~' for negative numbers, not '-'. Got '{original_input}'; did you mean '~{original_input[1:]}'?", node.line)  # type: ignore
1402:             if isinstance(input_value, str) and input_value.startswith('~'):
1403:                 input_value = '-' + input_value[1:]
1404:             try:
1405:                 if '.' in input_value:  # type: ignore
1406:                     integer_part, decimal_part = str(input_value).split('.')
1407:                     if len(integer_part.strip('-').lstrip('0')) > 16:
1408:                         raise InterpreterError(f"Runtime Error: Input value exceeds maximum number of 16 digits", node.line)
1409:                     if len(decimal_part.rstrip('0')) > 5:
1410:                         raise InterpreterError(f"Runtime Error: Input value exceeds maximum number of 5 decimal numbers", node.line)
1411: 
1412:                 else:
1413:                     if len(input_value.strip('-').lstrip('0')) > 16:
1414:                         raise InterpreterError(f"Runtime Error: Input value exceeds maximum number of 16 digits", node.line)
1415: 
1416:                 input_value = float(input_value)  # type: ignore
1417: 
1418: 
1419:             except ValueError:
1420:                 raise InterpreterError(f"Runtime Error: Expected float value, got '{original_input}'", node.line)
1421: 
1422:         elif var_type == "branch":
1423:             if input_value == "true" or input_value == "false":
1424:                 suggestion = "sunshine" if input_value == "true" else "frost"
1425:                 raise InterpreterError(f"Runtime Error: GAL uses 'sunshine' and 'frost' for booleans, not 'true'/'false'. Got '{input_value}'; did you mean '{suggestion}'?", node.line)
1426:             if input_value == "sunshine":
1427:                 input_value = True
1428:             elif input_value == "frost":
1429:                 input_value = False
1430:             else:
1431:                 raise InterpreterError(f"Runtime Error: expected branch value (sunshine/frost), got '{input_value}'", node.line)
1432:             
1433:         elif var_type == "leaf":
1434:             if len(input_value) != 1:  # type: ignore
1435:                 raise InterpreterError(f"Runtime Error: Expected a single character for leaf, got '{input_value}'", node.line)
1436:             input_value = str(input_value)
1437: 
1438:         elif var_type == "vine":
1439:             input_value = str(input_value)
1440: 
1441:         return input_value
1442: 
```

Meaning:

- `eval_print()` executes `plant(...)`.
- It evaluates every print argument, joins them, and emits output.
- `eval_input()` executes `water(...)`.
- It asks the frontend for input, waits for it, validates the input type, then stores the converted value.

### 7.9 Loops and Reclaim

Source: `Backend/interpreter/interpreter.py:1101-1192`

```python
1101:                             return
1102:                         
1103:                     elif elif_node.node_type == "ElseStatement":
1104:                         try:
1105:                             self.enter_scope()
1106:                             self.eval_block(elif_node.children[0])
1107:                         finally:
1108:                             self.exit_scope()
1109:                         return
1110: 
1111:                     current_node += 1
1112:         finally:
1113:             self.exit_scope()
1114: 
1115:         return None
1116:     
1117:     def eval_for_loop(self, node):
1118:         self.enter_loop('for')
1119:         self.enter_scope()
1120:         MAX_LOOP_ITERATIONS = 10000
1121:         LOOP_COUNTER = 0
1122: 
1123:         try:
1124:             instantiate_node = node.children[0]
1125: 
1126:             if isinstance(instantiate_node, VariableDeclarationNode):
1127:                 var_type = instantiate_node.children[0].value
1128:                 var_name = instantiate_node.children[1].value
1129:                 initial_value_node = self.interpret(instantiate_node.children[2])
1130:                 self.declare_variable(var_name, var_type, initial_value_node)
1131: 
1132:             elif isinstance(instantiate_node, AssignmentNode):
1133:                 var_name = instantiate_node.children[0].value
1134:                 initial_value_node = self.interpret(instantiate_node.children[1])
1135:                 self.lookup_variable(var_name)["value"] = initial_value_node  # type: ignore
1136: 
1137:             condition_node = node.children[1].children[0]
1138:             condition_result = self.interpret(condition_node)
1139: 
1140:             if not isinstance(condition_result, bool):
1141:                 raise InterpreterError(f"Runtime Error: Condition must be a boolean. Got '{condition_result}'", node.line)
1142: 
1143:             while condition_result:
1144:                 LOOP_COUNTER += 1
1145:                 if LOOP_COUNTER > MAX_LOOP_ITERATIONS:
1146:                     raise InterpreterError("Runtime Error: Infinite loop detected!", node.line)
1147: 
1148:                 
1149:                 self.eval_block(node.children[3])
1150: 
1151:                 if self.continue_flag:
1152:                     self.continue_flag = False  
1153: 
1154:                 if self.break_triggered():
1155:                     break
1156:                 
1157:                 for update_expr in node.children[2].children:
1158:                     self.interpret(update_expr)
1159: 
1160:                 condition_result = self.interpret(condition_node)
1161: 
1162:         finally:
1163:             self.exit_scope()
1164:             self.exit_loop()
1165: 
1166: 
1167:     def eval_while_loop(self, node):
1168:         self.enter_loop('while')
1169:         self.enter_scope()
1170:         MAX_LOOP_ITERATIONS = 10000
1171:         LOOP_COUNTER = 0
1172:         condition_node = node.children[0].children[0]
1173: 
1174:         try:
1175:             condition_result = self.interpret(condition_node)
1176: 
1177:             if not isinstance(condition_result, bool):
1178:                 raise InterpreterError(f"Runtime Error: Condition must be a boolean. Got '{condition_result}'", node.line)
1179: 
1180:             while condition_result:
1181:                 LOOP_COUNTER += 1
1182:                 if LOOP_COUNTER > MAX_LOOP_ITERATIONS:
1183:                     raise InterpreterError("Runtime Error: Infinite loop detected!", node.line)
1184: 
1185:                 block_node = node.children[1]
1186:                 self.eval_block(block_node)
1187: 
1188:                 if self.continue_flag:
1189:                     self.continue_flag = False
1190: 
1191:                 if self.break_triggered():
1192:                     break
```

Source: `Backend/interpreter/interpreter.py:857-899`

```python
0857:         function_name = node.value
0858:         args = [self.interpret(arg.children[0]) for arg in node.children]
0859: 
0860:         func_info = self.lookup_function(function_name)
0861:         if isinstance(func_info, str):
0862:             raise InterpreterError(func_info, node.line)
0863: 
0864:         expected_params = func_info["params"]
0865:         function_node = func_info["node"]
0866: 
0867:         if len(expected_params) != len(args):
0868:             raise InterpreterError(
0869:                 f"Runtime Error: Function '{function_name}' expects {len(expected_params)} argument(s), got {len(args)}.",
0870:                 node.line
0871:             )
0872:         
0873:         self.enter_scope()
0874:         
0875:         try:
0876:             for i, param in enumerate(expected_params):
0877:                 param_name = param["name"]
0878:                 param_type = param["type"]
0879:                 arg_value = args[i]
0880:                 is_list = param.get("is_list", False)
0881:                 self.declare_variable(param_name, param_type, arg_value, is_list=is_list)
0882: 
0883:             try:
0884:                 self.eval_block(function_node.children[2])
0885: 
0886:             except ReturnValue as ret:
0887:                 return ret.value
0888: 
0889:             return None
0890: 
0891:         finally:
0892:             self.exit_scope()
0893:             self.current_func_name = None
0894: 
0895: 
0896:     def eval_append(self, node):
0897:         list_name = node.parent.children[0].value
0898:         list_info = self.lookup_variable(list_name)
0899: 
```

Meaning:

- `eval_if()` handles `bud` / `wither` branches.
- `eval_for()` handles `cultivate`.
- `eval_return()` raises `ReturnValue`.
- `eval_function_call()` catches `ReturnValue`, so `reclaim` stops function execution properly.

## 8. Error Classes and How Errors Return To UI

### 8.1 Lexical Error

Source: `Backend/lexer/errors.py:3-11`

```python
0003: class LexicalError:
0004: 
0005:     def __init__(self, pos, details):
0006:         self.pos = pos
0007:         self.details = details
0008: 
0009:     def as_string(self):
0010:         self.details = self.details.replace('\n', '\\n')
0011:         return f"LEXICAL error line {self.pos.ln} col {self.pos.col} {self.details}"
```

### 8.2 Semantic Error

Source: `Backend/semantic/errors.py:6-12`

```python
0006: class SemanticError(Exception):
0007:     def __init__(self, message, line):
0008:         super().__init__(message)
0009:         clean = _REDUNDANT_PREFIX.sub('', str(message)).strip()
0010:         self.message = f"SEMANTIC error line {line}: {clean}"
0011: 
0012:     def __str__(self):
```

### 8.3 Runtime Error

Source: `Backend/interpreter/errors.py:6-27`

```python
0006: class ReturnValue(Exception):
0007: 
0008:     def __init__(self, value):
0009:         self.value = value
0010: 
0011: 
0012: class _CancelledError(Exception):
0013:     pass
0014: 
0015: 
0016: class InterpreterError(Exception):
0017: 
0018:     def __init__(self, message, line):
0019:         super().__init__(message)
0020:         clean = _REDUNDANT_PREFIX.sub('', str(message)).strip()
0021:         if line is not None and str(line) != "":
0022:             self.message = f"RUNTIME error line {line}: {clean}"
0023:         else:
0024:             self.message = clean
0025: 
0026:     def __str__(self):
0027:         return self.message
```

| Error Type | Detected By | Returned By Server |
|---|---|---|
| Lexical | `scanner.py` using `LexicalError` | `run_endpoint()` returns stage `lexical`. |
| Syntax | `parser.py` inside `LL1Parser.parse()` | `run_endpoint()` returns stage `parse` or `syntax`. |
| Semantic | `builder.py` or `analyzer.py` using `SemanticError` | `run_endpoint()` returns stage `semantic`. |
| Runtime | `interpreter.py` using `InterpreterError` | `run_endpoint()` returns stage `runtime`. |

## 9. Full Mini Simulation: `seed num = 10;`

This simulation shows how the code is processed through the lexer and later stages.

### 9.1 Lexer Simulation

Input:

```gal
seed num = 10;
```

| Step | current_char | Code Area | Result |
|---:|---|---|---|
| 1 | `s` | `scanner.py` alphabet branch | Lexer tries reserved words starting with `s`. |
| 2 | `s e e d` | reserved word check | `ident_str` becomes `seed`; token `seed` is appended. |
| 3 | space | whitespace branch | Lexer skips whitespace. |
| 4 | `n` | alphabet branch | Not a reserved word, fallback identifier loop collects `num`. |
| 5 | space | identifier delimiter check | Space is valid in `idf_delim`, so token `id` with value `num` is appended. |
| 6 | `=` | operator branch | Token `=` is appended. |
| 7 | `1` | number branch | Digit loop collects `10`; token `intlit` is appended. |
| 8 | `;` | semicolon branch | Token `;` is appended. |
| 9 | end | EOF append | Token `EOF` is appended. |

Final token sequence:

```text
seed id = intlit ; EOF
```

### 9.2 Parser Simulation

The parser does not see characters anymore. It sees:

```text
seed id = intlit ;
```

If this appears inside root local declaration, it matches:

```text
<local_declaration> -> <var_dec> ; <local_declaration>
<var_dec> -> <data_type> id <var_tail>
<data_type> -> seed
<var_tail> -> = <init_val>
<init_val> -> <expression>
<factor> -> intlit
```

### 9.3 Semantic Simulation

The builder/semantic stage checks:

| Check | Result |
|---|---|
| Is `num` already declared in same scope? | No, so allowed. |
| Is `10` compatible with `seed`? | Yes, `10` is `intlit`, so type is `seed`. |
| Should `num` be stored in symbol table? | Yes. |

### 9.4 Interpreter Simulation

At runtime:

| Step | Runtime Effect |
|---:|---|
| 1 | Interpreter evaluates initializer `10`. |
| 2 | Converts/stores value as seed integer. |
| 3 | Runtime scope stores `num = 10`. |

## 10. Quick Defense Script For Code-Level Questions

```text
Kapag tinanong po kung paano binabasa ng lexer yung code, ang sagot is:
Yung buong source code po ay pinapasa muna sa Lexer object. Pero hindi niya ito binabasa as one whole meaning agad. Meron siyang self.current_char, which means current character na tinitingnan niya. Every time na tatawag siya ng advance(), gagalaw yung position and mag-uupdate yung current_char.

For example, sa word na root, chine-check niya character by character kung r, then o, then o, then t. Kapag complete and valid yung delimiter after root, gagawa siya ng Token root.

Kapag hindi exact reserved word, like roof, hindi siya error agad. Magfa-fall back siya sa identifier block. Yung while loop na may ALPHANUM ang magko-collect ng remaining letters, kaya magiging identifier token yung roof.

After lexer, token list na ang pinapasa sa parser. Parser naman uses stack and PREDICT table. Hindi na raw characters ang binabasa niya, token types na.

After parser, builder creates AST and checks semantics using symbol table. Then kapag pasado, interpreter executes the AST and handles variables, expressions, plant output, water input, loops, and reclaim.
```