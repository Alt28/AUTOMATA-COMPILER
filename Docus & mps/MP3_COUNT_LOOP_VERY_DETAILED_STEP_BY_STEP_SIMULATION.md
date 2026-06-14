# MP3 - Count Loop Odd/Even Output - Very Detailed Step-by-Step Simulation

Generated: 2026-06-08 01:34:52

## Program Purpose
This program shows a cultivate loop using an existing variable, a comparison condition, postfix increment, modulo/equality condition, and alternating spring/wither output.

## Source Program
```gal
root() {
	seed count;
    cultivate ( count = 1; count <= 5; count++) {
        spring (count % 2  == 0) {
            plant("Bloom!");
        } wither {
            plant(count);
        }
    }

    reclaim;
}
```

## 1. Full System Pipeline For This MP
| Stage | Detailed Explanation |
|---|---|
| Input | Backend `/api/run` receives the whole editor text. `server.py` line 152 reads JSON, and line 164 stores the code in `source_code`. |
| Lexer | `server.py` line 229 calls `lex(source_code)`. Lexer setup is in `scanner.py` line 42; `advance()` is line 60; `make_tokens()` is line 74. |
| Parser | `parser.parse_and_build(tokens)` is called at `server.py` line 380. `parse()` starts at `parser.py` line 1141; the stack starts at line 1162. |
| Builder | After syntax succeeds, comments/newlines are filtered at `parser.py` line 2252, and `_build_ast(filtered)` is called at line 2254. `build_ast()` starts at `builder.py` line 41. |
| Semantic | `validate_ast()` is called at `server.py` line 402. Semantic wrapper is `analyzer.py` line 361; recursive walk is line 56. |
| Interpreter | `Interpreter` is created at `server.py` line 663; execution starts with `interp.interpret(ast)` at line 667. Dispatcher is `interpreter.py` line 218. |

## 2. Actual Run Results
| Stage | Actual Result |
|---|---|
| Lexer | errors=[]; token_count=59 |
| Parser | parse_ok=True; errors=[] |
| Builder | success=True; errors=[] |
| Semantic | success=True; errors=[]; warnings=[] |
| Interpreter | outputs=['1', 'Bloom!', '3', 'Bloom!', '5']; functions=['root']; final_scopes=[{}] |

## 3. Source Line Meaning
| Line | Code | Meaning |
|---|---|---|
| 1 | `root() {` | Main function header. Interpreter automatically calls root after registering functions. |
| 2 | `	seed count;` | Variable declaration. Builder creates a VariableDeclarationNode; interpreter creates runtime variable storage. |
| 3 | `    cultivate ( count = 1; count <= 5; count++) {` | For-loop style statement: initializer, condition, update, and block. |
| 4 | `        spring (count % 2  == 0) {` | If branch. Interpreter runs this block when condition is true. |
| 5 | `            plant("Bloom!");` | Output statement. Interpreter evaluates arguments and emits text. |
| 6 | `        } wither {` | Program structure line scanned by lexer and checked by parser. |
| 7 | `            plant(count);` | Output statement. Interpreter evaluates arguments and emits text. |
| 8 | `        }` | Block closing brace. |
| 9 | `    }` | Block closing brace. |
| 10 | `` | Blank line used only for spacing. |
| 11 | `    reclaim;` | Return/end statement. Interpreter exits the current function. |
| 12 | `}` | Block closing brace. |

## 4. Lexer Stage - Detailed Explanation
1. `root` becomes a root reserved word token at scanner.py line 773.
2. `seed count;` produces seed at line 812 and identifier `count` at line 1292.
3. `cultivate` is tokenized at scanner.py line 274.
4. The loop condition `count <= 5` uses the `<=` token at scanner.py line 1954.
5. The update `count++` uses the increment token at scanner.py line 1897.
6. The spring condition uses `%` at scanner.py line 1540 and `==` at line 2004.
7. `Bloom!` is tokenized as a string literal at scanner.py line 2726.

## 5. Parser Stage - Detailed Explanation
1. Parser matches root and local declaration `seed count;`.
2. It sees `cultivate` and parses the header as initializer, condition, and update.
3. Initializer is `count = 1`.
4. Condition is `count <= 5`.
5. Update is `count++`.
6. Inside the loop block, parser accepts spring/wither with condition `count % 2 == 0`.
7. Root ends with required `reclaim;`.

## 6. Builder / AST Stage - Detailed Explanation
1. `parse_variable()` at builder.py line 575 builds the `count` declaration.
2. `parse_for()` at line 4590 builds the cultivate loop node.
3. `parse_if()` at line 4328 builds the spring/wither node inside the loop.
4. The expression `count % 2 == 0` becomes nested BinaryOpNodes.

## 7. Semantic Stage - Detailed Explanation
1. Semantic validation checks that `count` is declared before being assigned, compared, incremented, and printed.
2. The cultivate condition `count <= 5` is valid because it returns branch/boolean.
3. The spring condition `count % 2 == 0` is valid because `%` produces a number and `==` produces branch/boolean.
4. `_check_ForLoop()` at analyzer.py line 208 marks loop context. No semantic errors are found.

## 8. Interpreter Stage - Detailed Explanation
1. `eval_variable_declaration()` at interpreter.py line 416 creates `count`. Because it has no initializer, seed default is 0.
2. `eval_for_loop()` at line 2097 runs the cultivate flow.
3. The initializer assigns `count = 1` before the first loop check.
4. `count <= 5` uses `eval_binary_op()` line 968 and the `<=` branch at line 1171.
5. `count % 2 == 0` uses modulo branch line 1124 and equality branch line 1150.
6. `eval_if_statement()` at line 2022 chooses spring for even values and wither for odd values.
7. `count++` uses `eval_unaryop()` at line 1778 after each loop body.
8. `eval_print()` at line 1436 emits either `Bloom!` or the numeric count.

## 9. Runtime Trace
| Moment | State / Expression | Result |
|---|---|---|
| Declare | count = 0 | Default seed value. |
| Init | count = 1 | cultivate initializer. |
| Iteration 1 | 1 <= 5 true; 1 % 2 == 0 false | wither prints `1`; count becomes 2. |
| Iteration 2 | 2 <= 5 true; 2 % 2 == 0 true | spring prints `Bloom!`; count becomes 3. |
| Iteration 3 | 3 <= 5 true; 3 % 2 == 0 false | wither prints `3`; count becomes 4. |
| Iteration 4 | 4 <= 5 true; 4 % 2 == 0 true | spring prints `Bloom!`; count becomes 5. |
| Iteration 5 | 5 <= 5 true; 5 % 2 == 0 false | wither prints `5`; count becomes 6. |
| Stop | 6 <= 5 false | Loop exits and root reclaims. |

## 10. Tokens By Source Line
| Source Line | Tokens Produced |
|---|---|
| 1 | `root:root  \|  (:(  \|  ):)  \|  {:{` |
| 2 | `seed:seed  \|  id:count  \|  ;:;` |
| 3 | `cultivate:cultivate  \|  (:(  \|  id:count  \|  =:=  \|  intlit:1  \|  ;:;  \|  id:count  \|  <=:<=  \|  intlit:5  \|  ;:;  \|  id:count  \|  ++:++  \|  ):)  \|  {:{` |
| 4 | `spring:spring  \|  (:(  \|  id:count  \|  %:%  \|  intlit:2  \|  ==:==  \|  intlit:0  \|  ):)  \|  {:{` |
| 5 | `plant:plant  \|  (:(  \|  stringlit:"Bloom!"  \|  ):)  \|  ;:;` |
| 6 | `}:}  \|  wither:wither  \|  {:{` |
| 7 | `plant:plant  \|  (:(  \|  id:count  \|  ):)  \|  ;:;` |
| 8 | `}:}` |
| 9 | `}:}` |
| 11 | `reclaim:reclaim  \|  ;:;` |
| 12 | `}:}` |

## 11. AST Shape Summary
```text
- Program
  - FunctionDeclaration value=root
    - ReturnType value=empty
    - Parameters
    - Block
      - VariableDeclaration line=2
        - Type value=seed line=2
        - Identifier value=count line=2
      - ForLoop line=3
        - Assignment line=3
        - Condition line=3
        - Update line=3
        - Block line=3
      - Return line=11
```

## 12. Final Output
| # | Output |
|---|---|
| 1 | `1` |
| 2 | `Bloom!` |
| 3 | `3` |
| 4 | `Bloom!` |
| 5 | `5` |

## 13. Full Token Table
| # | Line | Col | Token Type | Value |
|---|---|---|---|---|
| 1 | 1 | 0 | `root` | `root` |
| 2 | 1 | 4 | `(` | `(` |
| 3 | 1 | 5 | `)` | `)` |
| 4 | 1 | 7 | `{` | `{` |
| 5 | 1 | 8 | `<br>` | `\n` |
| 6 | 2 | 1 | `seed` | `seed` |
| 7 | 2 | 6 | `id` | `count` |
| 8 | 2 | 11 | `;` | `;` |
| 9 | 2 | 12 | `<br>` | `\n` |
| 10 | 3 | 4 | `cultivate` | `cultivate` |
| 11 | 3 | 14 | `(` | `(` |
| 12 | 3 | 16 | `id` | `count` |
| 13 | 3 | 22 | `=` | `=` |
| 14 | 3 | 24 | `intlit` | `1` |
| 15 | 3 | 25 | `;` | `;` |
| 16 | 3 | 27 | `id` | `count` |
| 17 | 3 | 33 | `<=` | `<=` |
| 18 | 3 | 36 | `intlit` | `5` |
| 19 | 3 | 37 | `;` | `;` |
| 20 | 3 | 39 | `id` | `count` |
| 21 | 3 | 44 | `++` | `++` |
| 22 | 3 | 46 | `)` | `)` |
| 23 | 3 | 48 | `{` | `{` |
| 24 | 3 | 49 | `<br>` | `\n` |
| 25 | 4 | 8 | `spring` | `spring` |
| 26 | 4 | 15 | `(` | `(` |
| 27 | 4 | 16 | `id` | `count` |
| 28 | 4 | 22 | `%` | `%` |
| 29 | 4 | 24 | `intlit` | `2` |
| 30 | 4 | 27 | `==` | `==` |
| 31 | 4 | 30 | `intlit` | `0` |
| 32 | 4 | 31 | `)` | `)` |
| 33 | 4 | 33 | `{` | `{` |
| 34 | 4 | 34 | `<br>` | `\n` |
| 35 | 5 | 12 | `plant` | `plant` |
| 36 | 5 | 17 | `(` | `(` |
| 37 | 5 | 18 | `stringlit` | `"Bloom!"` |
| 38 | 5 | 26 | `)` | `)` |
| 39 | 5 | 27 | `;` | `;` |
| 40 | 5 | 28 | `<br>` | `\n` |
| 41 | 6 | 8 | `}` | `}` |
| 42 | 6 | 10 | `wither` | `wither` |
| 43 | 6 | 17 | `{` | `{` |
| 44 | 6 | 18 | `<br>` | `\n` |
| 45 | 7 | 12 | `plant` | `plant` |
| 46 | 7 | 17 | `(` | `(` |
| 47 | 7 | 18 | `id` | `count` |
| 48 | 7 | 23 | `)` | `)` |
| 49 | 7 | 24 | `;` | `;` |
| 50 | 7 | 25 | `<br>` | `\n` |
| 51 | 8 | 8 | `}` | `}` |
| 52 | 8 | 9 | `<br>` | `\n` |
| 53 | 9 | 4 | `}` | `}` |
| 54 | 9 | 5 | `<br>` | `\n` |
| 55 | 11 | 4 | `reclaim` | `reclaim` |
| 56 | 11 | 11 | `;` | `;` |
| 57 | 11 | 12 | `<br>` | `\n` |
| 58 | 12 | 0 | `}` | `}` |
| 59 | 12 | 0 | `EOF` | `` |

## 14. Important Code Snippets

### Server Pipeline
Lines 589-675 in `Backend\server.py`
```python
589: @app.route('/api/run', methods=['POST'])
590: # AUTO: Defines function `run_endpoint`.
591: def run_endpoint():
592:     # AUTO: Starts protected code that can catch errors.
593:     try:
594:         # LINE: Read JSON request body sent by the frontend.
595:         data = request.get_json()
596:         # LINE: Reject request if editor source code is missing.
597:         if not data or 'source_code' not in data:
598:             # AUTO: Returns this result to the caller.
599:             return jsonify({'error': 'Missing source_code in request body'}), 400
600: 
601:         # LINE: Store the full editor text in source_code.
602:         source_code = data['source_code']
603: 
604:         # LINE: Stage 1, scan source code into lexer tokens.
605:         tokens, lex_errors = lex(source_code)
606:         # LINE: Stop pipeline if lexer found invalid characters/delimiters.
607:         if lex_errors:
608:             # AUTO: Returns this result to the caller.
609:             return jsonify({
610:                 # AUTO: Executes this statement.
611:                 'success': False,
612:                 # AUTO: Executes this statement.
613:                 'stage': 'lexical',
614:                 # AUTO: Executes this statement.
615:                 'output': [],
616:                 # AUTO: Executes this statement.
617:                 'errors': lex_errors
618:             # AUTO: Closes the current grouped code/data.
619:             })
620: 
621:         # LINE: Stage 2, parse tokens and build AST if syntax is valid.
622:         parse_result = parser.parse_and_build(tokens)
623:         # LINE: Stop pipeline if syntax or builder semantic checks failed.
624:         if not parse_result['success']:
625:             # AUTO: Sets `error_stage`.
626:             error_stage = parse_result.get('error_stage', 'syntax')
627:             # AUTO: Returns this result to the caller.
628:             return jsonify({
629:                 # AUTO: Executes this statement.
630:                 'success': False,
631:                 # AUTO: Executes this statement.
632:                 'stage': error_stage,
633:                 # AUTO: Executes this statement.
634:                 'output': [],
635:                 # AUTO: Executes this statement.
636:                 'errors': [str(e) for e in parse_result['errors']]
637:             # AUTO: Closes the current grouped code/data.
638:             })
639: 
640:         # LINE: Stage 3, validate AST semantic rules.
641:         semantic_result = validate_ast(parse_result['ast'], parse_result['symbol_table'])
642:         # LINE: Stop pipeline if semantic analyzer found errors.
643:         if not semantic_result['success']:
644:             # AUTO: Returns this result to the caller.
645:             return jsonify({
646:                 # AUTO: Executes this statement.
647:                 'success': False,
648:                 # AUTO: Executes this statement.
649:                 'stage': 'semantic',
650:                 # AUTO: Executes this statement.
651:                 'output': [],
652:                 # AUTO: Executes this statement.
653:                 'errors': [str(e) for e in semantic_result['errors']]
654:             # AUTO: Closes the current grouped code/data.
655:             })
656: 
657:         # LINE: Get the validated AST for execution.
658:         ast = semantic_result['ast']
659: 
660:         # LINE: Collector captures plant() output for non-socket /api/run.
661:         collector = OutputCollector()
662:         # LINE: Create interpreter and give it the collector as output target.
663:         interp = Interpreter(socketio=collector)
664:         # AUTO: Starts protected code that can catch errors.
665:         try:
666:             # LINE: Stage 4, execute ProgramNode through interpreter.
667:             interp.interpret(ast)
668:             # LINE: Return successful runtime output to frontend.
669:             return jsonify({
670:                 # AUTO: Executes this statement.
671:                 'success': True,
672:                 # AUTO: Executes this statement.
673:                 'stage': 'execution',
674:                 # AUTO: Executes this statement.
675:                 'output': collector.outputs,
```
Controls the whole compile/run flow.

### Lexer `current_char` Flow
Lines 42-94 in `Backend\lexer\scanner.py`
```python
42:     def __init__(self, source_code): 
43:         # GUIDE: Normalize Windows newlines so line/column tracking is consistent.
44:         # source_code is the full text from the editor. The lexer does not
45:         # understand the whole program at once; it scans this string one
46:         # character at a time.
47:         # LINE: Store the editor text and remove '\r' so Windows line endings are stable.
48:         self.source_code = source_code.replace('\r', '')
49: 
50:         # Position starts before the first character. Calling advance() below
51:         # moves it to index 0 and loads the first current_char.
52:         # LINE: Start before the first character so advance() loads index 0.
53:         self.pos = Position(-1, 1, -1)
54:         # LINE: current_char holds the one character currently being scanned.
55:         self.current_char = None
56:         # LINE: Move to the first character of source_code.
57:         self.advance()
58: 
59:     # AUTO: Defines function `advance`.
60:     def advance(self):
61:         # GUIDE: Move one character forward and update Position before reading again.
62:         # self.current_char is the character being processed right now.
63:         # self.pos stores index, line, and column for that character.
64:         # LINE: Update index, line, and column using the previous character.
65:         self.pos.advance(self.current_char)
66: 
67:         # If the index is still inside source_code, load the next character.
68:         # If the index already passed the text length, current_char becomes None,
69:         # which means the lexer reached end of file.
70:         # LINE: Load the next character, or set None when the source is finished.
71:         self.current_char = self.source_code[self.pos.index] if self.pos.index<len(self.source_code) else None
72: 
73:     # AUTO: Defines function `make_tokens`.
74:     def make_tokens(self):
75:         # GUIDE: Main finite-state scan; each branch recognizes one token family.
76:         # tokens collects successful Token objects.
77:         # errors collects LexicalError objects if a character/token is invalid.
78:         # LINE: tokens is the output list sent to parser and lexeme table.
79:         tokens = []
80:         # LINE: line stores the source line number for each token.
81:         line = 1
82:         # LINE: errors stores lexical errors found while scanning.
83:         errors = []
84:         # LINE: pos remembers where the current token starts.
85:         pos = self.pos.copy()
86: 
87:         # This loop continues until advance() reaches the end and sets
88:         # current_char to None.
89:         # LINE: Main scanner loop; one token is built each pass.
90:         while self.current_char != None:
91: 
92:             # AUTO: Checks this condition.
93:             if self.current_char in ALPHA:
94:                 # GUIDE: Reserved words are checked first; unfinished matches fall back
```
Shows source storage, position, current_char, advance, and token loop.

### Parser Stack Flow
Lines 1141-1348 in `Backend\parser\parser.py`
```python
1141:     def parse(self, tokens: Sequence[Any]) -> Tuple[bool, List[str]]:
1142:         # GUIDE: Main LL(1) stack algorithm; compare grammar symbols on the stack
1143:         # with the current lookahead token, then expand or consume.
1144:         # Convert incoming Token objects into the parser's simple _TokView form.
1145:         # LINE: Convert lexer Token objects into the parser's lightweight token view.
1146:         toks = [_as_tok(t) for t in tokens]
1147: 
1148:         # Normalize token names so lexer aliases still match grammar terminals.
1149:         # LINE: Rename token types if lexer name and grammar name differ.
1150:         toks = [_TokView(self._normalize_token_type(t.type), t.value, t.line, t.col) for t in toks]
1151: 
1152:         # Make sure the parser always has an EOF marker to know when to stop.
1153:         # LINE: Ensure EOF exists so the parsing loop has a stopping token.
1154:         toks = self._ensure_eof(toks)
1155: 
1156:         # LINE: Keep current tokens for helper error messages.
1157:         self._current_tokens = toks
1158: 
1159:         # Stack starts with EOF at the bottom and <program> on top. The parser
1160:         # repeatedly expands the top grammar symbol until the stack is empty.
1161:         # LINE: Start with EOF at bottom and <program> as the first rule to expand.
1162:         stack: List[str] = [self.end_marker, self.start_symbol]
1163:         # LINE: index points to the current lookahead token in toks.
1164:         index = 0
1165:         
1166:         # LINE: Track declaration type to make simple literal mismatch messages clearer.
1167:         current_var_type: Optional[str] = None
1168:         # LINE: Becomes seed/tree/etc after '=' while parsing declarations.
1169:         expecting_value_for_type: Optional[str] = None
1170: 
1171:         # LINE: Tracks whether reclaim already appeared inside each block.
1172:         reclaim_seen_stack: List[bool] = []
1173: 
1174:         # AUTO: Defines function `current_token`.
1175:         def current_token() -> _TokView:
1176:             # Lookahead token: the parser decides what to do using only this
1177:             # current token type, which is the LL(1) idea.
1178:             # AUTO: Uses a variable from an outer function scope.
1179:             nonlocal index
1180:             # LINE: If index passed the stream, pretend the lookahead is EOF.
1181:             if index >= len(toks):
1182:                 # AUTO: Sets `last_line`.
1183:                 last_line = toks[-1].line if toks else 1
1184:                 # AUTO: Sets `last_col`.
1185:                 last_col = toks[-1].col if toks else 0
1186:                 # AUTO: Returns this result to the caller.
1187:                 return _TokView(self.end_marker, self.end_marker, last_line, last_col)
1188:             # LINE: Return the token currently being compared with the stack top.
1189:             return toks[index]
1190: 
1191:         # LINE: Keep parsing until every grammar symbol in the stack is handled.
1192:         while stack:
1193:             # top is the grammar symbol we need to match/expand.
1194:             # tok is the current input token from the lexer.
1195:             # LINE: Read the top grammar symbol and the current lookahead token.
1196:             top = stack[-1]
1197:             # AUTO: Sets `tok`.
1198:             tok = current_token()
1199:             # AUTO: Sets `token_type`.
1200:             token_type = tok.type
1201:             # AUTO: Sets `token_value`.
1202:             token_value = tok.value
1203:             # AUTO: Sets `line`.
1204:             line = tok.line or 1
1205: 
1206:             # LINE: Ignore comments/newlines when the grammar is not asking for them.
1207:             if token_type in self.skip_token_types and top != token_type:
1208:                 # AUTO: Adds into `index`.
1209:                 index += 1
1210:                 # AUTO: Skips to the next loop iteration.
1211:                 continue
1212: 
1213:             # LINE: Non-terminal case, such as <program> or <statement>.
1214:             if top in self.parsing_table:
1215:                 # Non-terminal case: use parsing_table[top][lookahead] to pick
1216:                 # the correct production from the CFG.
1217:                 # LINE: Get the parse-table row for this non-terminal.
1218:                 row = self.parsing_table[top]
1219:                 # LINE: If lookahead exists in this row, we know which production to use.
1220:                 if token_type in row:
1221:                     # LINE: Select the CFG production predicted by this lookahead token.
1222:                     production = row[token_type]
1223:                     
1224:                     # AUTO: Checks this condition.
1225:                     if top == '<statement>' and token_type != '}' and reclaim_seen_stack and reclaim_seen_stack[-1]:
1226:                         # AUTO: Returns this result to the caller.
1227:                         return False, [f"SYNTAX error line {line} col {tok.col} Unexpected token '{token_value}' after 'reclaim'. Expected: '}}'."]
1228: 
1229:                     # AUTO: Checks this condition.
1230:                     if top == '<statement>' and token_type == '}':
1231:                         # AUTO: Calls `=`.
1232:                         is_epsilon = (len(production) == 0 or (len(production) == 1 and production[0] in self.epsilon_symbols))
1233:                         # AUTO: Checks this condition.
1234:                         if is_epsilon:
1235:                             # AUTO: Sets `lookback`.
1236:                             lookback = index - 1
1237:                             # AUTO: Repeats while this condition is true.
1238:                             while lookback >= 0 and toks[lookback].type in self.skip_token_types:
1239:                                 # AUTO: Subtracts from `lookback`.
1240:                                 lookback -= 1
1241:                             
1242:                             # AUTO: Checks this condition.
1243:                             if lookback >= 0 and toks[lookback].type == '{':
1244:                                 # AUTO: Sets `before_brace`.
1245:                                 before_brace = lookback - 1
1246:                                 # AUTO: Repeats while this condition is true.
1247:                                 while before_brace >= 0 and toks[before_brace].type in self.skip_token_types:
1248:                                     # AUTO: Subtracts from `before_brace`.
1249:                                     before_brace -= 1
1250:                                 
1251:                                 # AUTO: Checks this condition.
1252:                                 if before_brace >= 0 and toks[before_brace].type == ')':
1253:                                     # AUTO: Sets `paren_depth`.
1254:                                     paren_depth = 1
1255:                                     # AUTO: Sets `paren_pos`.
1256:                                     paren_pos = before_brace - 1
1257:                                     # AUTO: Repeats while this condition is true.
1258:                                     while paren_pos >= 0 and paren_depth > 0:
1259:                                         # AUTO: Checks this condition.
1260:                                         if toks[paren_pos].type == ')':
1261:                                             # AUTO: Adds into `paren_depth`.
1262:                                             paren_depth += 1
1263:                                         # AUTO: Checks the next alternate condition.
1264:                                         elif toks[paren_pos].type == '(':
1265:                                             # AUTO: Subtracts from `paren_depth`.
1266:                                             paren_depth -= 1
1267:                                         # AUTO: Subtracts from `paren_pos`.
1268:                                         paren_pos -= 1
1269:                                     
1270:                                     # AUTO: Checks this condition.
1271:                                     if paren_pos >= 0:
1272:                                         # AUTO: Sets `kw_pos`.
1273:                                         kw_pos = paren_pos
1274:                                         # AUTO: Repeats while this condition is true.
1275:                                         while kw_pos >= 0 and toks[kw_pos].type in self.skip_token_types:
1276:                                             # AUTO: Subtracts from `kw_pos`.
1277:                                             kw_pos -= 1
1278:                                         
1279:                                         # AUTO: Checks this condition.
1280:                                         if kw_pos >= 0:
1281:                                             # AUTO: Sets `kw`.
1282:                                             kw = toks[kw_pos]
1283:                                             # AUTO: Sets `conditional_keywords`.
1284:                                             conditional_keywords = {'spring', 'bud', 'wither', 'grow', 'cultivate', 'tend', 'harvest'}
1285:                                             # AUTO: Checks this condition.
1286:                                             if kw.type in conditional_keywords:
1287:                                                 # AUTO: Returns this result to the caller.
1288:                                                 return False, [f"SYNTAX error line {line} col {tok.col} Empty block after '{kw.value}' statement - at least one statement required"]
1289:                                 
1290:                                 # AUTO: Checks the next alternate condition.
1291:                                 elif before_brace >= 0 and toks[before_brace].type in {'wither', 'tend'}:
1292:                                     # AUTO: Sets `kw`.
1293:                                     kw = toks[before_brace]
1294:                                     # AUTO: Returns this result to the caller.
1295:                                     return False, [f"SYNTAX error line {line} col {tok.col} Empty block after '{kw.value}' statement - at least one statement required"]
1296:                     
1297:                     # LINE: Remove the non-terminal before replacing it with its production.
1298:                     stack.pop()
1299: 
1300:                     # AUTO: Checks this condition.
1301:                     if not (
1302:                         # AUTO: Executes this statement.
1303:                         len(production) == 0
1304:                         # AUTO: Calls `or`.
1305:                         or (len(production) == 1 and production[0] in self.epsilon_symbols)
1306:                     # AUTO: Closes the current grouped code/data.
1307:                     ):
1308:                         # Push production in reverse so the leftmost grammar
1309:                         # symbol is processed next.
1310:                         # LINE: Push RHS in reverse so the first RHS symbol becomes stack top.
1311:                         stack.extend(reversed(production))
1312:                     # AUTO: Skips to the next loop iteration.
1313:                     continue
1314: 
1315:                 # LINE: If lookahead is not in row, parser knows this is a syntax error.
1316:                 expected = set(row.keys())
1317:                 
1318:                 # AUTO: Checks this condition.
1319:                 if token_type in {'variety', 'soil'} and token_type not in expected:
1320:                     # AUTO: Repeats while this condition is true.
1321:                     while index < len(toks) and toks[index].type != ';':
1322:                         # AUTO: Checks this condition.
1323:                         if toks[index].type == 'prune':
1324:                             # AUTO: Adds into `index`.
1325:                             index += 1
1326:                             # AUTO: Stops the nearest loop.
1327:                             break
1328:                         # AUTO: Adds into `index`.
1329:                         index += 1
1330:                     # AUTO: Checks this condition.
1331:                     if index < len(toks) and toks[index].type == ';':
1332:                         # AUTO: Adds into `index`.
1333:                         index += 1
1334:                     # AUTO: Skips to the next loop iteration.
1335:                     continue
1336: 
1337:                 # LINE: Create a friendly expected-token message and stop parsing.
1338:                 error_msg = self._generate_helpful_error(top, token_type, token_value, line, tok.col, expected, index, toks)
1339:                 # AUTO: Returns this result to the caller.
1340:                 return False, [error_msg]
1341: 
1342:             # LINE: Terminal case, such as seed, id, ;, (, or =.
1343:             if top == token_type:
1344:                 # Terminal case: grammar expected the same token type the lexer
1345:                 # produced, so consume it by popping stack and moving index.
1346:                 # LINE: Remember declared type when consuming a data-type token.
1347:                 if token_type in {'seed', 'tree', 'leaf', 'branch', 'vine'}:
1348:                     # AUTO: Sets `current_var_type`.
```
Shows LL(1) stack, lookahead, production choice, and terminal matching.

### Builder Entry
Lines 41-76 in `Backend\parser\builder.py`
```python
41: def build_ast(tokens):
42:     # GUIDE: Entry point after syntax success; reset compiler state, then build the
43:     # ProgramNode from globals, pollinate functions, and root().
44:     # root is the top AST node. Every global declaration/function/root becomes
45:     # a child of this ProgramNode.
46:     # LINE: Create the main AST container that will hold the whole program.
47:     root = ProgramNode()
48: 
49:     # Reset symbol table state so each compile/run starts clean.
50:     # LINE: Clear global variables from any previous run.
51:     symbol_table.variables = {}
52:     # LINE: Clear stored functions from any previous run.
53:     symbol_table.functions = {}
54:     # LINE: Reset scope stack to one global scope.
55:     symbol_table.scopes = [{}] 
56:     # LINE: Clear per-function variable records.
57:     symbol_table.function_variables = {}
58:     # LINE: Clear bundle/struct type definitions.
59:     symbol_table.bundle_types = {}
60:     # LINE: Reset builder context tracking.
61:     context_stack = []
62:     # LINE: index points to the current token being converted to AST.
63:     index = 0
64:     # LINE: No function is active before parsing top-level code.
65:     symbol_table.current_func_name = None
66:     
67:     # LINE: Walk through all tokens until EOF/global parsing is finished.
68:     while index < len(tokens):
69:         # token is the current token being converted into an AST construct.
70:         # index moves forward as each parse_* helper consumes tokens.
71:         # LINE: Read the current token at this index.
72:         token = tokens[index]
73: 
74:         # LINE: Ignore extra semicolons at global level.
75:         if token.type == ";":
76:             # AUTO: Adds into `index`.
```
Shows AST root creation and token-to-AST loop.

### Semantic Walk
Lines 34-72 in `Backend\semantic\analyzer.py`
```python
34:     def validate(self, ast, symbol_table_data):
35:         # Start walking from the ProgramNode. Every checker can add messages
36:         # into self.errors; no errors means semantic validation succeeds.
37:         # LINE: Begin recursive semantic walk from the AST root.
38:         self._walk(ast)
39:         # LINE: Return validation result plus errors/warnings/symbol table.
40:         return {
41:             # LINE: success is true only when no semantic errors were collected.
42:             "success": len(self.errors) == 0,
43:             # AUTO: Executes this statement.
44:             "errors": self.errors,
45:             # AUTO: Executes this statement.
46:             "warnings": self.warnings,
47:             # AUTO: Executes this statement.
48:             "symbol_table": symbol_table_data,
49:             # AUTO: Executes this statement.
50:             "ast": ast,
51:         # AUTO: Closes the current grouped code/data.
52:         }
53: 
54: 
55:     # AUTO: Defines function `_walk`.
56:     def _walk(self, node):
57:         # GUIDE: Dynamic dispatch; Program calls _check_Program, Break calls
58:         # _check_Break, and unknown node types simply recurse into children.
59:         # LINE: Nothing to check for missing/empty AST node.
60:         if node is None:
61:             # AUTO: Returns this result to the caller.
62:             return
63:         # LINE: Find checker method based on node type, like _check_Break.
64:         handler = getattr(self, f'_check_{node.node_type}', None)
65:         # LINE: If checker exists, run that specific semantic rule.
66:         if handler:
67:             # AUTO: Calls `handler`.
68:             handler(node)
69:         # AUTO: Runs when previous condition did not pass.
70:         else:
71:             # LINE: Otherwise keep walking through this node's children.
72:             for child in getattr(node, 'children', []):
```
Shows final AST validation logic.

### Interpreter Program Entry
Lines 218-415 in `Backend\interpreter\interpreter.py`
```python
218:     def interpret(self, node):
219:         # GUIDE: Central runtime dispatcher; each AST node class is sent to its
220:         # matching eval_* method. This is where execution branches by node type.
221:         # LINE: ProgramNode means start the whole program execution.
222:         if isinstance(node, ProgramNode):
223:             # AUTO: Returns this result to the caller.
224:             return self.eval_program(node)
225:         # LINE: BundleDefinitionNode registers a bundle/struct type.
226:         elif isinstance(node, BundleDefinitionNode):
227:             # AUTO: Returns this result to the caller.
228:             return self.eval_bundle_definition(node)
229:         # LINE: MemberAccessNode reads obj.member.
230:         elif isinstance(node, MemberAccessNode):
231:             # AUTO: Returns this result to the caller.
232:             return self.eval_member_access(node)
233:         # LINE: ArrayMemberAccessNode reads arr[i].member.
234:         elif isinstance(node, ArrayMemberAccessNode):
235:             # AUTO: Returns this result to the caller.
236:             return self.eval_array_member_access(node)
237:         # LINE: VariableDeclarationNode creates a variable at runtime.
238:         elif isinstance(node, VariableDeclarationNode):
239:             # AUTO: Returns this result to the caller.
240:             return self.eval_variable_declaration(node)
241:         # LINE: AssignmentNode updates a variable/list/member value.
242:         elif isinstance(node, AssignmentNode):
243:             # AUTO: Returns this result to the caller.
244:             return self.eval_assignment(node)
245:         # LINE: BinaryOpNode evaluates operators like +, -, *, /, ==, &&.
246:         elif isinstance(node, BinaryOpNode):
247:             # AUTO: Sets `value`.
248:             value = self.eval_binary_op(node)
249:             # LINE: Guard against numbers larger than GAL's numeric limit.
250:             if isinstance(value, (int, float)):
251:                 # AUTO: Checks this condition.
252:                 if value > 1000000000000000 or value < -9999999999999999:
253:                     # AUTO: Stops this flow by raising an error.
254:                     raise InterpreterError(f"Runtime Error: Evaluated number exceeds maximum number of 16 digits", node.line)
255:             # AUTO: Returns this result to the caller.
256:             return value
257:         # LINE: FunctionDeclarationNode is saved, not executed immediately.
258:         elif isinstance(node, FunctionDeclarationNode):
259:             # AUTO: Returns this result to the caller.
260:             return self.eval_function_declaration(node)
261:         # LINE: PrintNode executes plant().
262:         elif isinstance(node, PrintNode):
263:             # AUTO: Returns this result to the caller.
264:             return self.eval_print(node)
265:         # LINE: ListNode builds an array/list value.
266:         elif isinstance(node, ListNode):
267:             # AUTO: Returns this result to the caller.
268:             return self.eval_list(node)
269:         # LINE: ListAccessNode reads arr[index].
270:         elif isinstance(node, ListAccessNode):
271:             # AUTO: Returns this result to the caller.
272:             return self.eval_list_access(node)
273:         # LINE: ReturnNode executes reclaim.
274:         elif isinstance(node, ReturnNode):
275:             # AUTO: Returns this result to the caller.
276:             return self.eval_return(node)
277:         # LINE: FunctionCallNode executes root(), gcd(), or another function call.
278:         elif isinstance(node, FunctionCallNode):
279:             # AUTO: Returns this result to the caller.
280:             return self.eval_function_call(node)
281:         # AUTO: Checks the next alternate condition.
282:         elif isinstance(node, AppendNode):
283:             # AUTO: Returns this result to the caller.
284:             return self.eval_append(node)
285:         # AUTO: Checks the next alternate condition.
286:         elif isinstance(node, InsertNode):
287:             # AUTO: Returns this result to the caller.
288:             return self.eval_insert(node)
289:         # AUTO: Checks the next alternate condition.
290:         elif isinstance(node, RemoveNode):
291:             # AUTO: Returns this result to the caller.
292:             return self.eval_remove(node)
293:         # AUTO: Checks the next alternate condition.
294:         elif isinstance(node, UnaryOpNode):
295:             # AUTO: Returns this result to the caller.
296:             return self.eval_unaryop(node)
297:         # AUTO: Checks the next alternate condition.
298:         elif isinstance(node, FertileDeclarationNode):
299:             # AUTO: Returns this result to the caller.
300:             return self.eval_sturdy_declaration(node)
301:         # AUTO: Checks the next alternate condition.
302:         elif isinstance(node, CastNode):
303:             # AUTO: Returns this result to the caller.
304:             return self.eval_cast(node)
305:         # AUTO: Checks the next alternate condition.
306:         elif isinstance(node, SoilNode):
307:             # AUTO: Returns this result to the caller.
308:             return self.eval_soil(node)
309:         # AUTO: Checks the next alternate condition.
310:         elif isinstance(node, BloomNode):
311:             # AUTO: Returns this result to the caller.
312:             return self.eval_bloom(node)
313:         # AUTO: Checks the next alternate condition.
314:         elif isinstance(node, IfStatementNode):
315:             # AUTO: Returns this result to the caller.
316:             return self.eval_if_statement(node)
317:         # AUTO: Checks the next alternate condition.
318:         elif isinstance(node, ForLoopNode):
319:             # AUTO: Returns this result to the caller.
320:             return self.eval_for_loop(node)
321:         # AUTO: Checks the next alternate condition.
322:         elif isinstance(node, WhileLoopNode):
323:             # AUTO: Returns this result to the caller.
324:             return self.eval_while_loop(node)
325:         # AUTO: Checks the next alternate condition.
326:         elif isinstance(node, DoWhileLoopNode):
327:             # AUTO: Returns this result to the caller.
328:             return self.eval_do_while_loop(node)
329:         # AUTO: Checks the next alternate condition.
330:         elif isinstance(node, BreakNode):
331:             # AUTO: Returns this result to the caller.
332:             return self.eval_break(node)
333:         # AUTO: Checks the next alternate condition.
334:         elif isinstance(node, ContinueNode):
335:             # AUTO: Returns this result to the caller.
336:             return self.eval_continue(node)
337:         # AUTO: Checks the next alternate condition.
338:         elif isinstance(node, SwitchNode):
339:             # AUTO: Returns this result to the caller.
340:             return self.eval_switch(node)
341:         # AUTO: Checks the next alternate condition.
342:         elif node.node_type == "Input":
343:             # LINE: Input node executes water().
344:             return self.eval_input(node)
345:         # AUTO: Checks the next alternate condition.
346:         elif node.node_type == "Value":
347:             # LINE: Value node converts a literal token into a Python value.
348:             value = self._parse_literal(node.value)
349:             # AUTO: Returns this result to the caller.
350:             return value
351:         # AUTO: Checks the next alternate condition.
352:         elif node.node_type == "Identifier":
353:             # LINE: Identifier reads the stored value of a variable.
354:             var_info = self.lookup_variable(node.value)
355:             # AUTO: Checks this condition.
356:             if isinstance(var_info, str):
357:                 # AUTO: Stops this flow by raising an error.
358:                 raise InterpreterError(var_info, node.line)
359:             # AUTO: Returns this result to the caller.
360:             return var_info["value"]
361:         # AUTO: Checks the next alternate condition.
362:         elif node.node_type == "FormattedString":
363:             # LINE: FormattedString removes quotes and decodes escapes.
364:             return self.eval_formatted_string(node)
365:         # AUTO: Checks the next alternate condition.
366:         elif node.node_type == "VariableDeclarationList":
367:             # LINE: Declare each variable inside a grouped declaration list.
368:             for child in node.children:
369:                 # AUTO: Calls `self.eval_variable_declaration`.
370:                 self.eval_variable_declaration(child)
371:         # AUTO: Checks the next alternate condition.
372:         elif node.node_type == "AssignmentList":
373:             # LINE: Execute each assignment/update inside a grouped assignment list.
374:             for child in node.children:
375:                 # AUTO: Checks this condition.
376:                 if isinstance(child, AssignmentNode):
377:                     # AUTO: Calls `self.eval_assignment`.
378:                     self.eval_assignment(child)
379:                 # AUTO: Checks the next alternate condition.
380:                 elif isinstance(child, UnaryOpNode):
381:                     # AUTO: Calls `self.eval_unaryop`.
382:                     self.eval_unaryop(child)
383:         # AUTO: Checks the next alternate condition.
384:         elif node.node_type == "List":
385:             # LINE: Evaluate every list child and return a Python list.
386:             return [self.interpret(child) for child in node.children]
387:         # AUTO: Checks the next alternate condition.
388:         elif node.node_type == "Block":
389:             # LINE: Execute a block of statements in order.
390:             self.eval_block(node)
391:         # AUTO: Runs when previous condition did not pass.
392:         else:
393:             # LINE: Unknown AST node means builder/interpreter are out of sync.
394:             raise Exception(f"Unknown AST node type: {node.node_type}")
395: 
396:     # AUTO: Defines function `eval_program`.
397:     def eval_program(self, node):
398:         # GUIDE: First register top-level declarations/functions, then call root().
399:         # LINE: Visit each top-level child under ProgramNode.
400:         for child in node.children:
401:             # Top-level children are usually FunctionDeclarationNode, bundle
402:             # definitions, and global declarations. Function declarations are
403:             # stored, not executed yet.
404:             # LINE: This saves function declarations or executes global declarations.
405:             self.interpret(child)
406: 
407:         # After registration, create a fake function call node for root().
408:         # This is how the interpreter starts the user's main program.
409:         # LINE: Create a runtime call equivalent to root().
410:         main_call = FunctionCallNode("root", [], node.line)
411:         # LINE: Dispatch that root() call through interpret() like any other call.
412:         return self.interpret(main_call)
413: 
414: 
415:     # AUTO: Defines function `eval_variable_declaration`.
```
Shows dispatcher and automatic root call.