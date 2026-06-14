# Three Machine Problems - Step-by-Step System Simulation

Generated: 2026-06-08 01:01:10

## A. Shared System Pipeline
| Step | Explanation |
|---|---|
| 1. User submits code | Frontend sends the full program to `/api/run`. `server.py` route starts at line 589; JSON is read at line 152; editor text is stored as `source_code` at line 164. |
| 2. Server calls lexer | `lex(source_code)` is called at `server.py` line 229; public lexer API is `scanner.py` line 2958. |
| 3. Lexer scans characters | `Lexer.__init__` line 42 stores the source at line 48; `advance()` line 60 moves `current_char`; `make_tokens()` line 74 loops at line 90. |
| 4. Parser checks CFG | `parse_and_build()` line 2224; `parse()` line 1141; stack starts at line 1162; production chosen at line 1222; terminals match at line 1343. |
| 5. Builder creates AST | Comments/newlines filtered at `parser.py` line 2252; AST built at line 2254; `build_ast()` begins at `builder.py` line 41. |
| 6. Semantic validates | `validate_ast()` is called from `server.py` line 402; wrapper is `analyzer.py` line 361; recursive walk is line 56. |
| 7. Interpreter executes | `Interpreter` is created at `server.py` line 663; `interp.interpret(ast)` runs at line 667; dispatcher is `interpreter.py` line 218; root call is created at line 410. |

## B. Key Code Snippets
### Server Run Pipeline
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
Main source -> lexer -> parser -> semantic -> interpreter path.

### Lexer Current Character Loop
Lines 42-95 in `Backend\lexer\scanner.py`
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
95:                 # to the identifier collector near the end of this alpha branch.
```
Shows source_code, current_char, advance(), make_tokens().

### Parser Stack Start
Lines 1141-1166 in `Backend\parser\parser.py`
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
```
Shows parse setup and stack.

### Parser Production Choice
Lines 1192-1226 in `Backend\parser\parser.py`
```python
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
```
Shows stack/lookahead production selection.

### Builder AST Start
Lines 41-65 in `Backend\parser\builder.py`
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
```
Shows AST root and symbol table reset.

### Semantic Walk
Lines 34-74 in `Backend\semantic\analyzer.py`
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
73:                 # AUTO: Calls `self._walk`.
74:                 self._walk(child)
```
Shows recursive validation.

### Interpreter Program Entry
Lines 218-413 in `Backend\interpreter\interpreter.py`
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
```
Shows dispatch and root call.

## MP1 - Function + Cultivate + Spring/Wither
### 1. Program
```gal
pollinate seed timesThree(seed n) {
    reclaim n * 3;
}
	
root() {
    seed value = 0;
	seed i;
    cultivate  (i = 1; i <= 4; i++) {
        value = timesThree(i);
        spring (value % 2 == 0) {
            plant("Even product:",value);
        } wither {
            plant("Odd  product:",value);
        }
    }

    reclaim;
}
```

### 2. Pipeline Result
| Stage | Result |
|---|---|
| Lexer | errors=[]; token_count=94 |
| Parser | parse_ok=True; errors=[] |
| Builder | success=True; errors=[] |
| Semantic | success=True; errors=[] |
| Interpreter | outputs=['Odd  product: 3', 'Even product: 6', 'Odd  product: 9', 'Even product: 12']; functions=['timesThree', 'root']; final_scopes=[{}] |

### 3. Step-by-Step Movement
| Step | What Happens |
|---|---|
| Lexer 1 | `pollinate` -> token at scanner line 646; `seed` -> line 812; `timesThree` -> identifier at line 1292. |
| Lexer 2 | `reclaim n * 3;` produces reclaim line 741, id, multiplication line 1690, intlit line 1451, semicolon. |
| Lexer 3 | `cultivate`, `spring`, `wither`, `plant` use scanner lines 274, 918, 1219, 584. Operators `<=`, `++`, `%`, `==` use lines 1954, 1897, 1540, 2004. |
| Parser | Parser accepts function definition first, then root. In root it accepts local declarations, cultivate, assignment, spring/wither, plant calls, and final reclaim. |
| Builder | `parse_function()` line 367 builds `timesThree/root`; `parse_for()` line 4590 builds cultivate; `parse_function_call()` line 3453 checks `timesThree(i)`; `parse_if()` line 4328 builds spring/wither. |
| Semantic | AST validation walks the tree. Cultivate enters loop context through `_check_ForLoop()` line 208. No errors. |
| Interpreter | `eval_program()` line 397 registers functions then calls root. `eval_for_loop()` line 2097 runs the loop. `eval_function_call()` line 1623 runs timesThree. `eval_if_statement()` line 2022 chooses spring/wither. `eval_print()` line 1436 emits output. |

### 4. Tokens By Source Line
| Source Line | Tokens Produced |
|---:|---|
| 1 | `pollinate:pollinate  \|  seed:seed  \|  id:timesThree  \|  (:(  \|  seed:seed  \|  id:n  \|  ):)  \|  {:{` |
| 2 | `reclaim:reclaim  \|  id:n  \|  *:*  \|  intlit:3  \|  ;:;` |
| 3 | `}:}` |
| 5 | `root:root  \|  (:(  \|  ):)  \|  {:{` |
| 6 | `seed:seed  \|  id:value  \|  =:=  \|  intlit:0  \|  ;:;` |
| 7 | `seed:seed  \|  id:i  \|  ;:;` |
| 8 | `cultivate:cultivate  \|  (:(  \|  id:i  \|  =:=  \|  intlit:1  \|  ;:;  \|  id:i  \|  <=:<=  \|  intlit:4  \|  ;:;  \|  id:i  \|  ++:++  \|  ):)  \|  {:{` |
| 9 | `id:value  \|  =:=  \|  id:timesThree  \|  (:(  \|  id:i  \|  ):)  \|  ;:;` |
| 10 | `spring:spring  \|  (:(  \|  id:value  \|  %:%  \|  intlit:2  \|  ==:==  \|  intlit:0  \|  ):)  \|  {:{` |
| 11 | `plant:plant  \|  (:(  \|  stringlit:"Even product:"  \|  ,:,  \|  id:value  \|  ):)  \|  ;:;` |
| 12 | `}:}  \|  wither:wither  \|  {:{` |
| 13 | `plant:plant  \|  (:(  \|  stringlit:"Odd  product:"  \|  ,:,  \|  id:value  \|  ):)  \|  ;:;` |
| 14 | `}:}` |
| 15 | `}:}` |
| 17 | `reclaim:reclaim  \|  ;:;` |
| 18 | `}:}` |

### 5. Runtime Trace
| Moment | State / Expression | Result |
|---|---|---|
| Before loop | value=0, i=0 | Declarations run. |
| Init | i=1 | cultivate initializer. |
| Iteration 1 | timesThree(1)=3; 3%2==0 false | prints Odd  product: 3; i becomes 2. |
| Iteration 2 | timesThree(2)=6; 6%2==0 true | prints Even product: 6; i becomes 3. |
| Iteration 3 | timesThree(3)=9; false | prints Odd  product: 9; i becomes 4. |
| Iteration 4 | timesThree(4)=12; true | prints Even product: 12; i becomes 5. |
| Stop | 5 <= 4 false | loop ends and reclaim exits root. |

### 6. Output
| # | plant() output |
|---:|---|
| 1 | `Odd  product: 3` |
| 2 | `Even product: 6` |
| 3 | `Odd  product: 9` |
| 4 | `Even product: 12` |

### 7. Full Token Table
| # | Line | Col | Type | Value |
|---:|---:|---:|---|---|
| 1 | 1 | 0 | `pollinate` | `pollinate` |
| 2 | 1 | 10 | `seed` | `seed` |
| 3 | 1 | 15 | `id` | `timesThree` |
| 4 | 1 | 25 | `(` | `(` |
| 5 | 1 | 26 | `seed` | `seed` |
| 6 | 1 | 31 | `id` | `n` |
| 7 | 1 | 32 | `)` | `)` |
| 8 | 1 | 34 | `{` | `{` |
| 9 | 1 | 35 | `<br>` | `\n` |
| 10 | 2 | 4 | `reclaim` | `reclaim` |
| 11 | 2 | 12 | `id` | `n` |
| 12 | 2 | 14 | `*` | `*` |
| 13 | 2 | 16 | `intlit` | `3` |
| 14 | 2 | 17 | `;` | `;` |
| 15 | 2 | 18 | `<br>` | `\n` |
| 16 | 3 | 0 | `}` | `}` |
| 17 | 3 | 1 | `<br>` | `\n` |
| 18 | 5 | 0 | `root` | `root` |
| 19 | 5 | 4 | `(` | `(` |
| 20 | 5 | 5 | `)` | `)` |
| 21 | 5 | 7 | `{` | `{` |
| 22 | 5 | 8 | `<br>` | `\n` |
| 23 | 6 | 4 | `seed` | `seed` |
| 24 | 6 | 9 | `id` | `value` |
| 25 | 6 | 15 | `=` | `=` |
| 26 | 6 | 17 | `intlit` | `0` |
| 27 | 6 | 18 | `;` | `;` |
| 28 | 6 | 19 | `<br>` | `\n` |
| 29 | 7 | 1 | `seed` | `seed` |
| 30 | 7 | 6 | `id` | `i` |
| 31 | 7 | 7 | `;` | `;` |
| 32 | 7 | 8 | `<br>` | `\n` |
| 33 | 8 | 4 | `cultivate` | `cultivate` |
| 34 | 8 | 15 | `(` | `(` |
| 35 | 8 | 16 | `id` | `i` |
| 36 | 8 | 18 | `=` | `=` |
| 37 | 8 | 20 | `intlit` | `1` |
| 38 | 8 | 21 | `;` | `;` |
| 39 | 8 | 23 | `id` | `i` |
| 40 | 8 | 25 | `<=` | `<=` |
| 41 | 8 | 28 | `intlit` | `4` |
| 42 | 8 | 29 | `;` | `;` |
| 43 | 8 | 31 | `id` | `i` |
| 44 | 8 | 32 | `++` | `++` |
| 45 | 8 | 34 | `)` | `)` |
| 46 | 8 | 36 | `{` | `{` |
| 47 | 8 | 37 | `<br>` | `\n` |
| 48 | 9 | 8 | `id` | `value` |
| 49 | 9 | 14 | `=` | `=` |
| 50 | 9 | 16 | `id` | `timesThree` |
| 51 | 9 | 26 | `(` | `(` |
| 52 | 9 | 27 | `id` | `i` |
| 53 | 9 | 28 | `)` | `)` |
| 54 | 9 | 29 | `;` | `;` |
| 55 | 9 | 30 | `<br>` | `\n` |
| 56 | 10 | 8 | `spring` | `spring` |
| 57 | 10 | 15 | `(` | `(` |
| 58 | 10 | 16 | `id` | `value` |
| 59 | 10 | 22 | `%` | `%` |
| 60 | 10 | 24 | `intlit` | `2` |
| 61 | 10 | 26 | `==` | `==` |
| 62 | 10 | 29 | `intlit` | `0` |
| 63 | 10 | 30 | `)` | `)` |
| 64 | 10 | 32 | `{` | `{` |
| 65 | 10 | 33 | `<br>` | `\n` |
| 66 | 11 | 12 | `plant` | `plant` |
| 67 | 11 | 17 | `(` | `(` |
| 68 | 11 | 18 | `stringlit` | `"Even product:"` |
| 69 | 11 | 33 | `,` | `,` |
| 70 | 11 | 34 | `id` | `value` |
| 71 | 11 | 39 | `)` | `)` |
| 72 | 11 | 40 | `;` | `;` |
| 73 | 11 | 41 | `<br>` | `\n` |
| 74 | 12 | 8 | `}` | `}` |
| 75 | 12 | 10 | `wither` | `wither` |
| 76 | 12 | 17 | `{` | `{` |
| 77 | 12 | 18 | `<br>` | `\n` |
| 78 | 13 | 12 | `plant` | `plant` |
| 79 | 13 | 17 | `(` | `(` |
| 80 | 13 | 18 | `stringlit` | `"Odd  product:"` |
| 81 | 13 | 33 | `,` | `,` |
| 82 | 13 | 34 | `id` | `value` |
| 83 | 13 | 39 | `)` | `)` |
| 84 | 13 | 40 | `;` | `;` |
| 85 | 13 | 41 | `<br>` | `\n` |
| 86 | 14 | 8 | `}` | `}` |
| 87 | 14 | 9 | `<br>` | `\n` |
| 88 | 15 | 4 | `}` | `}` |
| 89 | 15 | 5 | `<br>` | `\n` |
| 90 | 17 | 4 | `reclaim` | `reclaim` |
| 91 | 17 | 11 | `;` | `;` |
| 92 | 17 | 12 | `<br>` | `\n` |
| 93 | 18 | 0 | `}` | `}` |
| 94 | 18 | 0 | `EOF` | `` |

## MP2 - Temperature Spring/Bud/Wither
### 1. Program
```gal
root() {
    seed temperature = 50;

    // First check: Is it boiling?
    spring (temperature >= 50) {
        plant("Too hot! The water is boiling!");
    } 
        bud (temperature <= 0) {
        plant("Too cold! The water turned into ice!");
    } 
    wither {
        plant("The water is just right for watering.");
    }

    reclaim;
}
```

### 2. Pipeline Result
| Stage | Result |
|---|---|
| Lexer | errors=[]; token_count=61 |
| Parser | parse_ok=True; errors=[] |
| Builder | success=True; errors=[] |
| Semantic | success=True; errors=[] |
| Interpreter | outputs=['Too hot! The water is boiling!']; functions=['root']; final_scopes=[{}] |

### 3. Step-by-Step Movement
| Step | What Happens |
|---|---|
| Lexer 1 | `root`, `seed`, and `temperature` become root token line 773, seed token line 812, id line 1292. `50` becomes intlit line 1451. |
| Lexer 2 | Comment line becomes `comment` token at scanner line 2151. Parser skips it at line 1207, and builder removes it before AST at line 2252. |
| Lexer 3 | `spring`, `bud`, `wither` use scanner lines 918, 167, 1219. `>=` and `<=` use lines 2050, 1954. String literals use line 2726. |
| Parser | Parser accepts root, local declaration `seed temperature = 50;`, then spring block, optional bud, optional wither, and final reclaim. |
| Builder | `parse_variable()` line 575 builds temperature. `parse_if()` line 4328 builds one if-chain AST node for spring/bud/wither. |
| Semantic | Semantic walk sees valid comparison conditions, so no errors. |
| Interpreter | `eval_variable_declaration()` line 416 stores temperature=50. `eval_if_statement()` line 2022 evaluates `temperature >= 50`; `>=` branch is around line 1196. Since true, spring block prints and bud/wither are skipped. |

### 4. Tokens By Source Line
| Source Line | Tokens Produced |
|---:|---|
| 1 | `root:root  \|  (:(  \|  ):)  \|  {:{` |
| 2 | `seed:seed  \|  id:temperature  \|  =:=  \|  intlit:50  \|  ;:;` |
| 4 | `comment:// First check: Is it boiling?` |
| 5 | `spring:spring  \|  (:(  \|  id:temperature  \|  >=:>=  \|  intlit:50  \|  ):)  \|  {:{` |
| 6 | `plant:plant  \|  (:(  \|  stringlit:"Too hot! The water is boiling!"  \|  ):)  \|  ;:;` |
| 7 | `}:}` |
| 8 | `bud:bud  \|  (:(  \|  id:temperature  \|  <=:<=  \|  intlit:0  \|  ):)  \|  {:{` |
| 9 | `plant:plant  \|  (:(  \|  stringlit:"Too cold! The water turned into ice!"  \|  ):)  \|  ;:;` |
| 10 | `}:}` |
| 11 | `wither:wither  \|  {:{` |
| 12 | `plant:plant  \|  (:(  \|  stringlit:"The water is just right for watering."  \|  ):)  \|  ;:;` |
| 13 | `}:}` |
| 15 | `reclaim:reclaim  \|  ;:;` |
| 16 | `}:}` |

### 5. Runtime Trace
| Moment | State / Expression | Result |
|---|---|---|
| Declare | temperature=50 | stored in root scope. |
| Spring condition | 50 >= 50 -> true | spring block runs. |
| Output | Too hot! The water is boiling! | plant emits string. |
| Bud/wither | skipped | because spring already ran. |
| End | reclaim | root exits. |

### 6. Output
| # | plant() output |
|---:|---|
| 1 | `Too hot! The water is boiling!` |

### 7. Full Token Table
| # | Line | Col | Type | Value |
|---:|---:|---:|---|---|
| 1 | 1 | 0 | `root` | `root` |
| 2 | 1 | 4 | `(` | `(` |
| 3 | 1 | 5 | `)` | `)` |
| 4 | 1 | 7 | `{` | `{` |
| 5 | 1 | 8 | `<br>` | `\n` |
| 6 | 2 | 4 | `seed` | `seed` |
| 7 | 2 | 9 | `id` | `temperature` |
| 8 | 2 | 21 | `=` | `=` |
| 9 | 2 | 23 | `intlit` | `50` |
| 10 | 2 | 25 | `;` | `;` |
| 11 | 2 | 26 | `<br>` | `\n` |
| 12 | 4 | 4 | `comment` | `// First check: Is it boiling?` |
| 13 | 4 | 34 | `<br>` | `\n` |
| 14 | 5 | 4 | `spring` | `spring` |
| 15 | 5 | 11 | `(` | `(` |
| 16 | 5 | 12 | `id` | `temperature` |
| 17 | 5 | 24 | `>=` | `>=` |
| 18 | 5 | 27 | `intlit` | `50` |
| 19 | 5 | 29 | `)` | `)` |
| 20 | 5 | 31 | `{` | `{` |
| 21 | 5 | 32 | `<br>` | `\n` |
| 22 | 6 | 8 | `plant` | `plant` |
| 23 | 6 | 13 | `(` | `(` |
| 24 | 6 | 14 | `stringlit` | `"Too hot! The water is boiling!"` |
| 25 | 6 | 46 | `)` | `)` |
| 26 | 6 | 47 | `;` | `;` |
| 27 | 6 | 48 | `<br>` | `\n` |
| 28 | 7 | 4 | `}` | `}` |
| 29 | 7 | 6 | `<br>` | `\n` |
| 30 | 8 | 8 | `bud` | `bud` |
| 31 | 8 | 12 | `(` | `(` |
| 32 | 8 | 13 | `id` | `temperature` |
| 33 | 8 | 25 | `<=` | `<=` |
| 34 | 8 | 28 | `intlit` | `0` |
| 35 | 8 | 29 | `)` | `)` |
| 36 | 8 | 31 | `{` | `{` |
| 37 | 8 | 32 | `<br>` | `\n` |
| 38 | 9 | 8 | `plant` | `plant` |
| 39 | 9 | 13 | `(` | `(` |
| 40 | 9 | 14 | `stringlit` | `"Too cold! The water turned into ice!"` |
| 41 | 9 | 52 | `)` | `)` |
| 42 | 9 | 53 | `;` | `;` |
| 43 | 9 | 54 | `<br>` | `\n` |
| 44 | 10 | 4 | `}` | `}` |
| 45 | 10 | 6 | `<br>` | `\n` |
| 46 | 11 | 4 | `wither` | `wither` |
| 47 | 11 | 11 | `{` | `{` |
| 48 | 11 | 12 | `<br>` | `\n` |
| 49 | 12 | 8 | `plant` | `plant` |
| 50 | 12 | 13 | `(` | `(` |
| 51 | 12 | 14 | `stringlit` | `"The water is just right for watering."` |
| 52 | 12 | 53 | `)` | `)` |
| 53 | 12 | 54 | `;` | `;` |
| 54 | 12 | 55 | `<br>` | `\n` |
| 55 | 13 | 4 | `}` | `}` |
| 56 | 13 | 5 | `<br>` | `\n` |
| 57 | 15 | 4 | `reclaim` | `reclaim` |
| 58 | 15 | 11 | `;` | `;` |
| 59 | 15 | 12 | `<br>` | `\n` |
| 60 | 16 | 0 | `}` | `}` |
| 61 | 16 | 0 | `EOF` | `` |

## MP3 - Count Loop Odd/Even Output
### 1. Program
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

### 2. Pipeline Result
| Stage | Result |
|---|---|
| Lexer | errors=[]; token_count=59 |
| Parser | parse_ok=True; errors=[] |
| Builder | success=True; errors=[] |
| Semantic | success=True; errors=[] |
| Interpreter | outputs=['1', 'Bloom!', '3', 'Bloom!', '5']; functions=['root']; final_scopes=[{}] |

### 3. Step-by-Step Movement
| Step | What Happens |
|---|---|
| Lexer 1 | `root` line 773; `seed` line 812; `count` identifier line 1292. |
| Lexer 2 | `cultivate` line 274; `<=` line 1954; `++` line 1897; `%` line 1540; `==` line 2004; string `Bloom!` line 2726. |
| Parser | Parser accepts root, local declaration `seed count;`, cultivate header `count = 1; count <= 5; count++`, spring/wither body, and final reclaim. |
| Builder | `parse_for()` line 4590 builds the loop. `parse_if()` line 4328 builds spring/wither inside the loop. `parse_statement()` line 815 routes statements. |
| Semantic | `_check_ForLoop()` line 208 marks the loop context. No errors. |
| Interpreter | `eval_for_loop()` line 2097 runs init, condition, body, update. `count++` uses `eval_unaryop()` line 1778. `%` and `==` use binary op branches lines 1124 and 1150. |

### 4. Tokens By Source Line
| Source Line | Tokens Produced |
|---:|---|
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

### 5. Runtime Trace
| Moment | State / Expression | Result |
|---|---|---|
| Before loop | count=0 | default seed value. |
| Init | count=1 | cultivate initializer. |
| Iteration 1 | 1%2==0 false | prints 1; count becomes 2. |
| Iteration 2 | 2%2==0 true | prints Bloom!; count becomes 3. |
| Iteration 3 | 3%2==0 false | prints 3; count becomes 4. |
| Iteration 4 | 4%2==0 true | prints Bloom!; count becomes 5. |
| Iteration 5 | 5%2==0 false | prints 5; count becomes 6. |
| Stop | 6 <= 5 false | loop ends and reclaim exits root. |

### 6. Output
| # | plant() output |
|---:|---|
| 1 | `1` |
| 2 | `Bloom!` |
| 3 | `3` |
| 4 | `Bloom!` |
| 5 | `5` |

### 7. Full Token Table
| # | Line | Col | Type | Value |
|---:|---:|---:|---|---|
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
