# Semantic Line-by-Line Review Guide

Generated: 2026-06-07 17:18:02

## 1. Purpose
Semantic analysis checks meaning after lexical and syntax rules pass. In this system, semantic work is split into two parts: `parser/builder.py` catches many declaration/type errors while building the AST, then `semantic/analyzer.py` walks the finished AST for final checks such as prune/skip placement.

## 2. Semantic Files
| File | Lines | Role |
|---|---:|---|
| `Backend/semantic/analyzer.py` | 365 | Final AST validation pass. |
| `Backend/semantic/symbol_table.py` | 173 | Stores variables, functions, scopes, bundles. |
| `Backend/semantic/errors.py` | 22 | Formats SemanticError messages. |
| `Backend/parser/builder.py` | 5794 | Builds AST and performs early semantic checks. |
| `Backend/server.py` | 1095 | Calls semantic validation in the compile/run pipeline. |

## 3. Important Semantic Lines
| Concept | File | Line | Explanation |
|---|---|---:|---|
| Server semantic endpoint | `server.py` | 322 | Receives /api/semantic request. |
| Server source_code | `server.py` | 164 | Stores editor source. |
| Server lex stage | `server.py` | 229 | Creates lexer tokens before semantics. |
| Server parse/build stage | `server.py` | 380 | Syntax check plus early semantic checks in builder.py. |
| Server final semantic call | `server.py` | 402 | Calls final AST validator. |
| Builder imports SemanticError | `builder.py` | 15 | Builder raises semantic errors while making AST. |
| Builder symbol table instance | `builder.py` | 33 | Global builder symbol table for declarations/functions. |
| Builder AST entry | `builder.py` | 41 | Builds ProgramNode and performs early semantic checks. |
| Builder reset variables | `builder.py` | 51 | Clears state for each compile/run. |
| Builder parse variable | `builder.py` | 575 | Checks variable declarations, arrays, water assignments. |
| Builder type compatibility | `builder.py` | 1797 | Central helper for compatible type assignment. |
| Builder expression type | `builder.py` | 1811 | Infers expression result type. |
| Builder assignment | `builder.py` | 2838 | Checks assignment target and value. |
| Builder function call | `builder.py` | 3453 | Checks function existence/arguments. |
| Builder return/reclaim | `builder.py` | 4514 | Checks reclaim value against function return type. |
| Builder condition spring | `builder.py` | 4328 | Checks spring/bud conditions are branch. |
| Builder cultivate | `builder.py` | 4590 | Checks cultivate init/condition/update. |
| Analyzer class | `analyzer.py` | 13 | Final AST semantic validation class. |
| Analyzer validate | `analyzer.py` | 34 | Walks AST and returns semantic result. |
| Analyzer dynamic walk | `analyzer.py` | 56 | Dispatches to _check_NodeType. |
| Analyzer loop context | `analyzer.py` | 208 | Allows prune/skip inside loops. |
| Analyzer prune check | `analyzer.py` | 255 | Rejects prune outside loop/switch. |
| Analyzer skip check | `analyzer.py` | 265 | Rejects skip outside loop. |
| Analyzer validate_ast wrapper | `analyzer.py` | 361 | Public semantic API imported by server.py. |
| Symbol declare variable | `symbol_table.py` | 23 | Stores variable metadata and detects duplicates. |
| Symbol lookup variable | `symbol_table.py` | 87 | Finds variable or reports used before declaration. |
| Symbol declare function | `symbol_table.py` | 118 | Stores function signatures. |
| SemanticError class | `errors.py` | 9 | Formats semantic error messages. |

## 4. Semantic Classes and Functions
| File | Kind | Name | Lines | Purpose |
|---|---|---|---:|---|
| `Backend\semantic\analyzer.py` | ClassDef | `ASTValidator` | 13-358 | Final AST walker/validator. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator.__init__` | 16-30 | Initializes error lists and context flags. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator.validate` | 34-52 | Runs validation and returns result dict. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._walk` | 56-74 | Recursive dynamic dispatch through AST nodes. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_Program` | 78-82 | Semantic support/checker function. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_VariableDeclaration` | 85-95 | Semantic support/checker function. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_VariableDeclarationList` | 98-102 | Semantic support/checker function. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_SturdyDeclaration` | 105-115 | Semantic support/checker function. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_FunctionDeclaration` | 118-142 | Semantic support/checker function. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_FunctionCall` | 145-149 | Semantic support/checker function. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_Assignment` | 152-156 | Semantic support/checker function. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_AssignmentList` | 159-163 | Semantic support/checker function. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_BinaryOp` | 166-170 | Semantic support/checker function. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_UnaryOp` | 173-177 | Semantic support/checker function. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_Block` | 180-184 | Semantic support/checker function. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_IfStatement` | 187-191 | Semantic support/checker function. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_ElseIfStatement` | 194-198 | Semantic support/checker function. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_ElseStatement` | 201-205 | Semantic support/checker function. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_ForLoop` | 208-218 | Tracks loop context for cultivate. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_WhileLoop` | 221-230 | Tracks loop context for grow. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_DoWhileLoop` | 233-241 | Semantic support/checker function. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_Switch` | 244-252 | Tracks harvest/switch context. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_Break` | 255-262 | Rejects prune outside loop/switch. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_Continue` | 265-272 | Rejects skip outside loop. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_Return` | 275-279 | Semantic support/checker function. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_PrintStatement` | 282-286 | Semantic support/checker function. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_Condition` | 289-293 | Semantic support/checker function. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_Update` | 296-300 | Semantic support/checker function. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_List` | 303-307 | Semantic support/checker function. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_ListAccess` | 310-314 | Semantic support/checker function. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_TypeCast` | 317-321 | Semantic support/checker function. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_MemberAccess` | 324-328 | Semantic support/checker function. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_BundleDefinition` | 331-337 | Semantic support/checker function. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_Append` | 340-344 | Semantic support/checker function. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_Insert` | 347-351 | Semantic support/checker function. |
| `Backend\semantic\analyzer.py` | method | `ASTValidator._check_Remove` | 354-358 | Semantic support/checker function. |
| `Backend\semantic\analyzer.py` | FunctionDef | `validate_ast` | 361-365 | Public wrapper imported by server.py. |
| `Backend\semantic\symbol_table.py` | ClassDef | `SymbolTable` | 4-171 | Stores declarations and scope state. |
| `Backend\semantic\symbol_table.py` | method | `SymbolTable.__init__` | 6-20 | Semantic support/checker function. |
| `Backend\semantic\symbol_table.py` | method | `SymbolTable.declare_variable` | 23-83 | Declares variable and checks duplicates. |
| `Backend\semantic\symbol_table.py` | method | `SymbolTable.lookup_variable` | 87-101 | Finds variable or returns used-before-declaration error. |
| `Backend\semantic\symbol_table.py` | method | `SymbolTable.set_variable` | 104-115 | Semantic support/checker function. |
| `Backend\semantic\symbol_table.py` | method | `SymbolTable.declare_function` | 118-124 | Stores function signature. |
| `Backend\semantic\symbol_table.py` | method | `SymbolTable.lookup_function` | 127-133 | Semantic support/checker function. |
| `Backend\semantic\symbol_table.py` | method | `SymbolTable.enter_scope` | 137-139 | Semantic support/checker function. |
| `Backend\semantic\symbol_table.py` | method | `SymbolTable.exit_scope` | 143-157 | Semantic support/checker function. |
| `Backend\semantic\symbol_table.py` | method | `SymbolTable.debug_scopes` | 161-171 | Semantic support/checker function. |
| `Backend\semantic\errors.py` | ClassDef | `SemanticError` | 9-22 | Formats semantic exception text. |
| `Backend\semantic\errors.py` | method | `SemanticError.__init__` | 11-17 | Semantic support/checker function. |
| `Backend\semantic\errors.py` | method | `SemanticError.__str__` | 20-22 | Semantic support/checker function. |

## 5. Builder Semantic Check Map
| Check | File/Line | Logic | Invalid Example |
|---|---|---|---|
| Duplicate variable | `symbol_table.py:43` | If a name already exists in the current function scope, return duplicate declaration error. | `seed x; seed x;` |
| Undeclared variable | `symbol_table.py:33` | lookup_variable returns used-before-declaration error when no scope has the name. | `x = 5;` |
| Function duplicate/name conflict | `builder.py:375` | parse_function checks if the function name is already declared. | `pollinate seed f(){ reclaim 1; } pollinate seed f(){ reclaim 2; }` |
| Parameter checking | `builder.py:3453` | parse_function_call verifies function exists and argument rules match stored params. | `timesThree("bad");` |
| Array size integer | `builder.py:667` | Array/list size cannot be tree/double when declaration expects seed/int size. | `seed arr[2.5];` |
| Fertile constant assignment | `builder.py:992` | Assignments check is_fertile before modifying variable. | `fertile seed x = 1; x = 2;` |
| Type compatibility | `builder.py:1797` | Helper decides if assignment/expression result can fit target type. | `seed x = "hello";` |
| spring/bud condition branch | `builder.py:4347` | parse_if requires conditional expression to evaluate to branch. | `spring (5) { plant("x"); }` |
| cultivate condition branch | `builder.py:4650` | parse_for requires the loop condition to be branch. | `cultivate (i=0; 5; i++) { plant(i); }` |
| grow condition branch | `builder.py:5087` | parse_while requires the grow condition to be branch. | `grow (1) { plant("x"); }` |
| reclaim return type | `builder.py:4532` | parse_return compares reclaim expression type with current function return type. | `pollinate seed f(){ reclaim "x"; }` |
| bundle member existence | `builder.py:1020` | Member access checks that the bundle type contains the member name. | `student.age if age is not a member` |
| prune outside loop/switch | `analyzer.py:255` | ASTValidator rejects Break node when _in_loop and _in_switch are zero. | `root(){ prune; reclaim; }` |
| skip outside loop | `analyzer.py:265` | ASTValidator rejects Continue node when _in_loop is zero. | `root(){ skip; reclaim; }` |

## 6. Key Code Blocks
### Server Semantic Pipeline
Lines 620-646 in `Backend\server.py`
```python
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
```
The run endpoint performs lexing, parse/build, then semantic validation before execution.

### Semantic Endpoint
Lines 320-418 in `Backend\server.py`
```python
320: @app.route('/api/semantic', methods=['POST'])
321: # AUTO: Defines function `semantic_endpoint`.
322: def semantic_endpoint():
323:     # AUTO: Starts protected code that can catch errors.
324:     try:
325:         # AUTO: Sets `data`.
326:         data = request.get_json()
327:         
328:         # AUTO: Checks this condition.
329:         if not data or 'source_code' not in data:
330:             # AUTO: Returns this result to the caller.
331:             return jsonify({
332:                 # AUTO: Executes this statement.
333:                 'error': 'Missing source_code in request body'
334:             # AUTO: Closes the current grouped code/data.
335:             }), 400
336:         
337:         # AUTO: Sets `source_code`.
338:         source_code = data['source_code']
339:         
340:         # AUTO: Sets `tokens, lex_errors`.
341:         tokens, lex_errors = lex(source_code)
342:         
343:         # AUTO: Sets `token_list`.
344:         token_list = []
345:         # AUTO: Starts a loop over these values.
346:         for token in tokens:
347:             # AUTO: Appends a value to a list.
348:             token_list.append({
349:                 # AUTO: Executes this statement.
350:                 'type': token.type,
351:                 # AUTO: Calls `_display_value`.
352:                 'value': _display_value(token.value),
353:                 # AUTO: Executes this statement.
354:                 'line': token.line,
355:                 # AUTO: Calls `getattr`.
356:                 'col': getattr(token, 'col', 0),
357:                 # AUTO: Calls `get_token_description`.
358:                 'description': get_token_description(token.type, token.value)
359:             # AUTO: Closes the current grouped code/data.
360:             })
361:         
362:         # AUTO: Checks this condition.
363:         if lex_errors:
364:             # AUTO: Returns this result to the caller.
365:             return jsonify({
366:                 # AUTO: Executes this statement.
367:                 'success': False,
368:                 # AUTO: Executes this statement.
369:                 'tokens': token_list,
370:                 # AUTO: Executes this statement.
371:                 'errors': lex_errors,
372:                 # AUTO: Executes this statement.
373:                 'warnings': [],
374:                 # AUTO: Executes this statement.
375:                 'stage': 'lexical'
376:             # AUTO: Closes the current grouped code/data.
377:             })
378:         
379:         # AUTO: Sets `parse_result`.
380:         parse_result = parser.parse_and_build(tokens)
381:         
382:         # AUTO: Checks this condition.
383:         if not parse_result['success']:
384:             # AUTO: Sets `error_stage`.
385:             error_stage = parse_result.get('error_stage', 'syntax')
386:             # AUTO: Returns this result to the caller.
387:             return jsonify({
388:                 # AUTO: Executes this statement.
389:                 'success': False,
390:                 # AUTO: Executes this statement.
391:                 'tokens': token_list,
392:                 # AUTO: Executes this statement.
393:                 'errors': parse_result['errors'],
394:                 # AUTO: Executes this statement.
395:                 'warnings': [],
396:                 # AUTO: Executes this statement.
397:                 'stage': error_stage
398:             # AUTO: Closes the current grouped code/data.
399:             })
400:         
401:         # AUTO: Sets `semantic_result`.
402:         semantic_result = validate_ast(parse_result['ast'], parse_result['symbol_table'])
403:         
404:         # AUTO: Returns this result to the caller.
405:         return jsonify({
406:             # AUTO: Executes this statement.
407:             'success': semantic_result['success'],
408:             # AUTO: Executes this statement.
409:             'tokens': token_list,
410:             # AUTO: Executes this statement.
411:             'errors': semantic_result['errors'],
412:             # AUTO: Executes this statement.
413:             'warnings': semantic_result['warnings'],
414:             # AUTO: Executes this statement.
415:             'symbol_table': semantic_result['symbol_table'],
416:             # AUTO: Executes this statement.
417:             'stage': 'semantic'
418:         # AUTO: Closes the current grouped code/data.
```
The /api/semantic endpoint returns tokens, errors, warnings, and symbol table.

### Builder AST Entry
Lines 40-72 in `Backend\parser\builder.py`
```python
40: # AUTO: Defines function `build_ast`.
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
```
Builds ProgramNode, resets symbol table, then consumes tokens into AST.

### Symbol Table Declare Variable
Lines 23-83 in `Backend\semantic\symbol_table.py`
```python
23:     def declare_variable(self, name, type_, value=None, is_list=False, is_fertile=False):
24:         # AUTO: Sets `scope`.
25:         scope = self.scopes[-1]
26:         # AUTO: Sets `current_func`.
27:         current_func = self.current_func_name
28:     
29: 
30:         # AUTO: Checks this condition.
31:         if name in self.functions:
32:             # AUTO: Returns this result to the caller.
33:             return f"Semantic Error: Variable '{name}' already declared as a function."
34: 
35:         # AUTO: Checks this condition.
36:         if current_func:
37:             # AUTO: Checks this condition.
38:             if current_func not in self.function_variables:
39:                 # AUTO: Sets `self.function_variables[current_func]`.
40:                 self.function_variables[current_func] = set()
41: 
42:             # AUTO: Checks this condition.
43:             if name in self.function_variables[current_func]:
44:                 # AUTO: Returns this result to the caller.
45:                 return f"Semantic Error: Variable '{name}' already declared in this function."
46: 
47:             # AUTO: Calls `self.function_variables[current_func].add`.
48:             self.function_variables[current_func].add(name)
49: 
50:         # AUTO: Checks this condition.
51:         if self.current_func_name:
52:             
53:             # AUTO: Sets `scope[name]`.
54:             scope[name] = {
55:                 # AUTO: Executes this statement.
56:                 "type": type_,  
57:                 # AUTO: Executes this statement.
58:                 "value": value,
59:                 # AUTO: Executes this statement.
60:                 "is_list": is_list,
61:                 # AUTO: Executes this statement.
62:                 "is_fertile": is_fertile
63:             # AUTO: Closes the current grouped code/data.
64:             }
65:         # AUTO: Runs when previous condition did not pass.
66:         else:
67:             # AUTO: Checks this condition.
68:             if name in self.global_variables:
69:                 # AUTO: Returns this result to the caller.
70:                 return f"Semantic Error: Variable '{name}' already declared."
71:             
72:             # AUTO: Sets `self.variables[name]`.
73:             self.variables[name] = {
74:                 # AUTO: Executes this statement.
75:                 "type": type_,
76:                 # AUTO: Executes this statement.
77:                 "value": value,
78:                 # AUTO: Executes this statement.
79:                 "is_list": is_list,
80:                 # AUTO: Executes this statement.
81:                 "is_fertile": is_fertile
82:             # AUTO: Closes the current grouped code/data.
83:             }
```
Stores variable metadata and detects duplicate names.

### Symbol Table Lookup Variable
Lines 87-101 in `Backend\semantic\symbol_table.py`
```python
87:     def lookup_variable(self, name):
88:         # AUTO: Starts a loop over these values.
89:         for i, scope in enumerate(reversed(self.scopes)):
90:             # AUTO: Checks this condition.
91:             if name in scope:
92:                 # AUTO: Returns this result to the caller.
93:                 return scope[name]
94:         
95:         # AUTO: Checks this condition.
96:         if name in self.variables:
97:             # AUTO: Returns this result to the caller.
98:             return self.variables[name]
99: 
100:         # AUTO: Returns this result to the caller.
101:         return f"Semantic Error: Variable '{name}' used before declaration."
```
Searches scopes then globals; returns used-before-declaration error if missing.

### ASTValidator Validate And Walk
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
Starts semantic validation and recursively dispatches by node type.

### Loop/Switch Context Checks
Lines 208-272 in `Backend\semantic\analyzer.py`
```python
208:     def _check_ForLoop(self, node):
209:         # Enter loop context so prune/skip inside this block are legal.
210:         # LINE: Increase loop depth before checking cultivate body.
211:         self._in_loop += 1
212:         # AUTO: Starts a loop over these values.
213:         for child in node.children:
214:             # AUTO: Calls `self._walk`.
215:             self._walk(child)
216:         # Leave loop context after all nested children are checked.
217:         # LINE: Decrease loop depth after cultivate body is checked.
218:         self._in_loop -= 1
219: 
220:     # AUTO: Defines function `_check_WhileLoop`.
221:     def _check_WhileLoop(self, node):
222:         # Same context rule as cultivate: grow allows prune/skip inside.
223:         # LINE: Increase loop depth before checking grow body.
224:         self._in_loop += 1
225:         # AUTO: Starts a loop over these values.
226:         for child in node.children:
227:             # AUTO: Calls `self._walk`.
228:             self._walk(child)
229:         # LINE: Decrease loop depth after grow body.
230:         self._in_loop -= 1
231: 
232:     # AUTO: Defines function `_check_DoWhileLoop`.
233:     def _check_DoWhileLoop(self, node):
234:         # AUTO: Adds into `self._in_loop`.
235:         self._in_loop += 1
236:         # AUTO: Starts a loop over these values.
237:         for child in node.children:
238:             # AUTO: Calls `self._walk`.
239:             self._walk(child)
240:         # AUTO: Subtracts from `self._in_loop`.
241:         self._in_loop -= 1
242: 
243:     # AUTO: Defines function `_check_Switch`.
244:     def _check_Switch(self, node):
245:         # LINE: harvest/variety context allows prune inside switch cases.
246:         self._in_switch += 1
247:         # AUTO: Starts a loop over these values.
248:         for child in node.children:
249:             # AUTO: Calls `self._walk`.
250:             self._walk(child)
251:         # LINE: Leave switch context after all cases are checked.
252:         self._in_switch -= 1
253: 
254:     # AUTO: Defines function `_check_Break`.
255:     def _check_Break(self, node):
256:         # prune is valid only while the walker is inside a loop or harvest.
257:         # LINE: If no loop/switch context, prune is illegal.
258:         if self._in_loop == 0 and self._in_switch == 0:
259:             # AUTO: Appends a value to a list.
260:             self.errors.append(
261:                 # AUTO: Executes this statement.
262:                 f"SEMANTIC error line {node.line}: 'prune' used outside a loop or switch.")
263: 
264:     # AUTO: Defines function `_check_Continue`.
265:     def _check_Continue(self, node):
266:         # skip is valid only while the walker is inside a loop.
267:         # LINE: If no loop context, skip is illegal.
268:         if self._in_loop == 0:
269:             # AUTO: Appends a value to a list.
270:             self.errors.append(
271:                 # AUTO: Executes this statement.
272:                 f"SEMANTIC error line {node.line}: 'skip' used outside a loop.")
```
Tracks loop/switch depth and rejects prune/skip outside valid context.

### SemanticError Formatting
Lines 9-22 in `Backend\semantic\errors.py`
```python
9: class SemanticError(Exception):
10:     # AUTO: Defines function `__init__`.
11:     def __init__(self, message, line):
12:         # AUTO: Calls `super`.
13:         super().__init__(message)
14:         # AUTO: Sets `clean`.
15:         clean = _REDUNDANT_PREFIX.sub('', str(message)).strip()
16:         # AUTO: Sets `self.message`.
17:         self.message = f"SEMANTIC error line {line}: {clean}"
18: 
19:     # AUTO: Defines function `__str__`.
20:     def __str__(self):
21:         # AUTO: Returns this result to the caller.
22:         return self.message
```
Cleans duplicate prefixes and formats final error text.

## 7. Sample Program Used For Semantic Walkthrough
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

Semantic result: `validate_ast() -> success=True, errors=[], warnings=[]`
AST summary: `AST root node_type=Program, top-level children=2`

## 8. Symbol Table From Sample
| Kind | Name | Type/Return | Scope/Params | Is List | Is Fertile |
|---|---|---|---|---|---|
| function | timesThree | seed | seed n |  |  |

## 9. Semantic Simulation Step-by-Step
| Step | Phase | Exact Process |
|---:|---|---|
| 1 | Editor sends source_code to server.py | `server.py` line 164: source code is stored before analysis. |
| 2 | Lexer runs first | `server.py` line 229: semantic never runs if lexical errors exist. |
| 3 | Parser + builder runs second | `server.py` line 380: syntax is checked, then builder creates AST and performs early semantic checks. |
| 4 | builder.py resets state | `builder.py` line 51: old variables/functions/scopes are cleared. |
| 5 | builder.py declares functions/variables | `builder.py` line 328 handles pollinate/root; line 575 handles declarations. |
| 6 | symbol table stores declarations | `symbol_table.py` line 23: each variable is saved with type/value/is_list/is_fertile. |
| 7 | sample function timesThree is saved | The builder stores `timesThree` as a function returning seed with one seed parameter n. |
| 8 | root declarations are saved | The builder saves `value` as seed and `i` as seed, then checks loop and if statements. |
| 9 | function call is checked | `builder.py` line 3453: `timesThree(i)` is checked against the stored function signature. |
| 10 | condition type is checked | `builder.py` line 4347: `value % 2 == 0` must become branch because spring needs true/false. |
| 11 | final AST validation runs | `analyzer.py` line 361: `validate_ast(ast, symbol_table)` creates ASTValidator. |
| 12 | AST walk starts | `analyzer.py` line 56: dynamic dispatch calls checkers like _check_ForLoop and _check_Break. |
| 13 | loop context is tracked | `analyzer.py` line 208: _in_loop increments while inside cultivate. |
| 14 | semantic result returns | `analyzer.py` line 361: success/errors/warnings/symbol table go back to server. |

## 10. Line-by-Line: analyzer.py
| Line | Code | Explanation |
|---:|---|---|
| 1 | `"""Final AST validation pass for GAL.` | Module documentation string explaining the semantic file purpose. |
| 2 | `` | Blank spacing line. |
| 3 | `builder.py already catches many declaration/type issues while creating the AST.` | Semantic support logic. |
| 4 | `This validator walks the finished AST and checks rules that are easier to see` | Semantic support logic. |
| 5 | `from the tree structure, such as prune/skip placement.` | Imports dependency used by semantic checking. |
| 6 | `"""` | Module documentation string explaining the semantic file purpose. |
| 7 | `` | Blank spacing line. |
| 8 | `# AUTO: Imports names from another module.` | Comment/guideline in the current code. |
| 9 | `from semantic.errors import SemanticError` | Imports dependency used by semantic checking. |
| 10 | `` | Blank spacing line. |
| 11 | `` | Blank spacing line. |
| 12 | `# AUTO: Defines class `ASTValidator`.` | Comment/guideline in the current code. |
| 13 | `class ASTValidator:` | Defines the final AST semantic validator. |
| 14 | `` | Blank spacing line. |
| 15 | `    # AUTO: Defines function `__init__`.` | Comment/guideline in the current code. |
| 16 | `    def __init__(self):` | Initializes object state. |
| 17 | `        # GUIDE: Context counters tell checks if they are inside a loop,` | Comment/guideline in the current code. |
| 18 | `        # switch, or function while walking nested AST nodes.` | Comment/guideline in the current code. |
| 19 | `        # AUTO: Sets `self.errors`.` | Comment/guideline in the current code. |
| 20 | `        self.errors = []` | Stores or updates semantic state. |
| 21 | `        # AUTO: Sets `self.warnings`.` | Comment/guideline in the current code. |
| 22 | `        self.warnings = []` | Stores or updates semantic state. |
| 23 | `        # AUTO: Sets `self._in_loop`.` | Comment/guideline in the current code. |
| 24 | `        self._in_loop = 0` | Stores or updates semantic state. |
| 25 | `        # AUTO: Sets `self._in_switch`.` | Comment/guideline in the current code. |
| 26 | `        self._in_switch = 0` | Stores or updates semantic state. |
| 27 | `        # AUTO: Sets `self._in_function`.` | Comment/guideline in the current code. |
| 28 | `        self._in_function = False` | Stores or updates semantic state. |
| 29 | `        # AUTO: Sets `self._current_func_type`.` | Comment/guideline in the current code. |
| 30 | `        self._current_func_type = None` | Stores or updates semantic state. |
| 31 | `` | Blank spacing line. |
| 32 | `` | Blank spacing line. |
| 33 | `    # AUTO: Defines function `validate`.` | Comment/guideline in the current code. |
| 34 | `    def validate(self, ast, symbol_table_data):` | Starts final AST validation and returns success/errors/warnings. |
| 35 | `        # Start walking from the ProgramNode. Every checker can add messages` | Comment/guideline in the current code. |
| 36 | `        # into self.errors; no errors means semantic validation succeeds.` | Comment/guideline in the current code. |
| 37 | `        # LINE: Begin recursive semantic walk from the AST root.` | Comment/guideline in the current code. |
| 38 | `        self._walk(ast)` | Semantic support logic. |
| 39 | `        # LINE: Return validation result plus errors/warnings/symbol table.` | Comment/guideline in the current code. |
| 40 | `        return {` | Returns result to caller. |
| 41 | `            # LINE: success is true only when no semantic errors were collected.` | Comment/guideline in the current code. |
| 42 | `            "success": len(self.errors) == 0,` | Stores or updates semantic state. |
| 43 | `            # AUTO: Executes this statement.` | Comment/guideline in the current code. |
| 44 | `            "errors": self.errors,` | Semantic support logic. |
| 45 | `            # AUTO: Executes this statement.` | Comment/guideline in the current code. |
| 46 | `            "warnings": self.warnings,` | Semantic support logic. |
| 47 | `            # AUTO: Executes this statement.` | Comment/guideline in the current code. |
| 48 | `            "symbol_table": symbol_table_data,` | Semantic support logic. |
| 49 | `            # AUTO: Executes this statement.` | Comment/guideline in the current code. |
| 50 | `            "ast": ast,` | Semantic support logic. |
| 51 | `        # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current code. |
| 52 | `        }` | Closes Python grouping/list/dict/call. |
| 53 | `` | Blank spacing line. |
| 54 | `` | Blank spacing line. |
| 55 | `    # AUTO: Defines function `_walk`.` | Comment/guideline in the current code. |
| 56 | `    def _walk(self, node):` | Starts recursive AST walker with dynamic checker dispatch. |
| 57 | `        # GUIDE: Dynamic dispatch; Program calls _check_Program, Break calls` | Comment/guideline in the current code. |
| 58 | `        # _check_Break, and unknown node types simply recurse into children.` | Comment/guideline in the current code. |
| 59 | `        # LINE: Nothing to check for missing/empty AST node.` | Comment/guideline in the current code. |
| 60 | `        if node is None:` | Checks a semantic condition. |
| 61 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in the current code. |
| 62 | `            return` | Semantic support logic. |
| 63 | `        # LINE: Find checker method based on node type, like _check_Break.` | Comment/guideline in the current code. |
| 64 | `        handler = getattr(self, f'_check_{node.node_type}', None)` | Finds checker method based on node.node_type. |
| 65 | `        # LINE: If checker exists, run that specific semantic rule.` | Comment/guideline in the current code. |
| 66 | `        if handler:` | Checks a semantic condition. |
| 67 | `            # AUTO: Calls `handler`.` | Comment/guideline in the current code. |
| 68 | `            handler(node)` | Runs the matched node-specific checker. |
| 69 | `        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current code. |
| 70 | `        else:` | Fallback branch. |
| 71 | `            # LINE: Otherwise keep walking through this node's children.` | Comment/guideline in the current code. |
| 72 | `            for child in getattr(node, 'children', []):` | Loops through children/symbols. |
| 73 | `                # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 74 | `                self._walk(child)` | Recursively validates a child AST node. |
| 75 | `` | Blank spacing line. |
| 76 | `` | Blank spacing line. |
| 77 | `    # AUTO: Defines function `_check_Program`.` | Comment/guideline in the current code. |
| 78 | `    def _check_Program(self, node):` | Starts a node-specific semantic checker. |
| 79 | `        # LINE: ProgramNode validates by checking each top-level child.` | Comment/guideline in the current code. |
| 80 | `        for child in node.children:` | Loops through children/symbols. |
| 81 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 82 | `            self._walk(child)` | Recursively validates a child AST node. |
| 83 | `` | Blank spacing line. |
| 84 | `    # AUTO: Defines function `_check_VariableDeclaration`.` | Comment/guideline in the current code. |
| 85 | `    def _check_VariableDeclaration(self, node):` | Starts a node-specific semantic checker. |
| 86 | `        # LINE: VariableDeclaration must at least contain type and name.` | Comment/guideline in the current code. |
| 87 | `        if len(node.children) < 2:` | Checks a semantic condition. |
| 88 | `            # AUTO: Appends a value to a list.` | Comment/guideline in the current code. |
| 89 | `            self.errors.append(` | Adds a semantic error message to the result list. |
| 90 | `                # AUTO: Executes this statement.` | Comment/guideline in the current code. |
| 91 | `                f"SEMANTIC error line {node.line}: Malformed variable declaration.")` | Semantic support logic. |
| 92 | `        # LINE: Continue validating initializer/children.` | Comment/guideline in the current code. |
| 93 | `        for child in node.children:` | Loops through children/symbols. |
| 94 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 95 | `            self._walk(child)` | Recursively validates a child AST node. |
| 96 | `` | Blank spacing line. |
| 97 | `    # AUTO: Defines function `_check_VariableDeclarationList`.` | Comment/guideline in the current code. |
| 98 | `    def _check_VariableDeclarationList(self, node):` | Starts a node-specific semantic checker. |
| 99 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current code. |
| 100 | `        for child in node.children:` | Loops through children/symbols. |
| 101 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 102 | `            self._walk(child)` | Recursively validates a child AST node. |
| 103 | `` | Blank spacing line. |
| 104 | `    # AUTO: Defines function `_check_SturdyDeclaration`.` | Comment/guideline in the current code. |
| 105 | `    def _check_SturdyDeclaration(self, node):` | Starts a node-specific semantic checker. |
| 106 | `        # AUTO: Checks this condition.` | Comment/guideline in the current code. |
| 107 | `        if len(node.children) < 3:` | Checks a semantic condition. |
| 108 | `            # AUTO: Appends a value to a list.` | Comment/guideline in the current code. |
| 109 | `            self.errors.append(` | Adds a semantic error message to the result list. |
| 110 | `                # AUTO: Executes this statement.` | Comment/guideline in the current code. |
| 111 | `                f"SEMANTIC error line {node.line}: Fertile declaration must have type, name, and value.")` | Semantic support logic. |
| 112 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current code. |
| 113 | `        for child in node.children:` | Loops through children/symbols. |
| 114 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 115 | `            self._walk(child)` | Recursively validates a child AST node. |
| 116 | `` | Blank spacing line. |
| 117 | `    # AUTO: Defines function `_check_FunctionDeclaration`.` | Comment/guideline in the current code. |
| 118 | `    def _check_FunctionDeclaration(self, node):` | Starts a node-specific semantic checker. |
| 119 | `        # LINE: FunctionDeclaration must have a function name in node.value.` | Comment/guideline in the current code. |
| 120 | `        if not node.value:` | Checks a semantic condition. |
| 121 | `            # AUTO: Appends a value to a list.` | Comment/guideline in the current code. |
| 122 | `            self.errors.append(` | Adds a semantic error message to the result list. |
| 123 | `                # AUTO: Executes this statement.` | Comment/guideline in the current code. |
| 124 | `                f"SEMANTIC error line {node.line}: Function declaration missing name.")` | Semantic support logic. |
| 125 | `        # LINE: Save previous function context before entering this function.` | Comment/guideline in the current code. |
| 126 | `        prev_in_func = self._in_function` | Stores or updates semantic state. |
| 127 | `        # AUTO: Sets `prev_func_type`.` | Comment/guideline in the current code. |
| 128 | `        prev_func_type = self._current_func_type` | Stores or updates semantic state. |
| 129 | `        # LINE: Mark validator as currently inside a function.` | Comment/guideline in the current code. |
| 130 | `        self._in_function = True` | Stores or updates semantic state. |
| 131 | `        # AUTO: Checks this condition.` | Comment/guideline in the current code. |
| 132 | `        if node.children:` | Checks a semantic condition. |
| 133 | `            # LINE: First child stores return type.` | Comment/guideline in the current code. |
| 134 | `            self._current_func_type = node.children[0].value` | Stores or updates semantic state. |
| 135 | `        # LINE: Validate parameters/body/children inside the function.` | Comment/guideline in the current code. |
| 136 | `        for child in node.children:` | Loops through children/symbols. |
| 137 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 138 | `            self._walk(child)` | Recursively validates a child AST node. |
| 139 | `        # LINE: Restore previous context after leaving function.` | Comment/guideline in the current code. |
| 140 | `        self._in_function = prev_in_func` | Stores or updates semantic state. |
| 141 | `        # AUTO: Sets `self._current_func_type`.` | Comment/guideline in the current code. |
| 142 | `        self._current_func_type = prev_func_type` | Stores or updates semantic state. |
| 143 | `` | Blank spacing line. |
| 144 | `    # AUTO: Defines function `_check_FunctionCall`.` | Comment/guideline in the current code. |
| 145 | `    def _check_FunctionCall(self, node):` | Starts a node-specific semantic checker. |
| 146 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current code. |
| 147 | `        for child in node.children:` | Loops through children/symbols. |
| 148 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 149 | `            self._walk(child)` | Recursively validates a child AST node. |
| 150 | `` | Blank spacing line. |
| 151 | `    # AUTO: Defines function `_check_Assignment`.` | Comment/guideline in the current code. |
| 152 | `    def _check_Assignment(self, node):` | Starts a node-specific semantic checker. |
| 153 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current code. |
| 154 | `        for child in node.children:` | Loops through children/symbols. |
| 155 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 156 | `            self._walk(child)` | Recursively validates a child AST node. |
| 157 | `` | Blank spacing line. |
| 158 | `    # AUTO: Defines function `_check_AssignmentList`.` | Comment/guideline in the current code. |
| 159 | `    def _check_AssignmentList(self, node):` | Starts a node-specific semantic checker. |
| 160 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current code. |
| 161 | `        for child in node.children:` | Loops through children/symbols. |
| 162 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 163 | `            self._walk(child)` | Recursively validates a child AST node. |
| 164 | `` | Blank spacing line. |
| 165 | `    # AUTO: Defines function `_check_BinaryOp`.` | Comment/guideline in the current code. |
| 166 | `    def _check_BinaryOp(self, node):` | Starts a node-specific semantic checker. |
| 167 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current code. |
| 168 | `        for child in node.children:` | Loops through children/symbols. |
| 169 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 170 | `            self._walk(child)` | Recursively validates a child AST node. |
| 171 | `` | Blank spacing line. |
| 172 | `    # AUTO: Defines function `_check_UnaryOp`.` | Comment/guideline in the current code. |
| 173 | `    def _check_UnaryOp(self, node):` | Starts a node-specific semantic checker. |
| 174 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current code. |
| 175 | `        for child in node.children:` | Loops through children/symbols. |
| 176 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 177 | `            self._walk(child)` | Recursively validates a child AST node. |
| 178 | `` | Blank spacing line. |
| 179 | `    # AUTO: Defines function `_check_Block`.` | Comment/guideline in the current code. |
| 180 | `    def _check_Block(self, node):` | Starts a node-specific semantic checker. |
| 181 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current code. |
| 182 | `        for child in node.children:` | Loops through children/symbols. |
| 183 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 184 | `            self._walk(child)` | Recursively validates a child AST node. |
| 185 | `` | Blank spacing line. |
| 186 | `    # AUTO: Defines function `_check_IfStatement`.` | Comment/guideline in the current code. |
| 187 | `    def _check_IfStatement(self, node):` | Starts a node-specific semantic checker. |
| 188 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current code. |
| 189 | `        for child in node.children:` | Loops through children/symbols. |
| 190 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 191 | `            self._walk(child)` | Recursively validates a child AST node. |
| 192 | `` | Blank spacing line. |
| 193 | `    # AUTO: Defines function `_check_ElseIfStatement`.` | Comment/guideline in the current code. |
| 194 | `    def _check_ElseIfStatement(self, node):` | Starts a node-specific semantic checker. |
| 195 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current code. |
| 196 | `        for child in node.children:` | Loops through children/symbols. |
| 197 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 198 | `            self._walk(child)` | Recursively validates a child AST node. |
| 199 | `` | Blank spacing line. |
| 200 | `    # AUTO: Defines function `_check_ElseStatement`.` | Comment/guideline in the current code. |
| 201 | `    def _check_ElseStatement(self, node):` | Starts a node-specific semantic checker. |
| 202 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current code. |
| 203 | `        for child in node.children:` | Loops through children/symbols. |
| 204 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 205 | `            self._walk(child)` | Recursively validates a child AST node. |
| 206 | `` | Blank spacing line. |
| 207 | `    # AUTO: Defines function `_check_ForLoop`.` | Comment/guideline in the current code. |
| 208 | `    def _check_ForLoop(self, node):` | Starts a node-specific semantic checker. |
| 209 | `        # Enter loop context so prune/skip inside this block are legal.` | Comment/guideline in the current code. |
| 210 | `        # LINE: Increase loop depth before checking cultivate body.` | Comment/guideline in the current code. |
| 211 | `        self._in_loop += 1` | Marks that validation is now inside a loop. |
| 212 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current code. |
| 213 | `        for child in node.children:` | Loops through children/symbols. |
| 214 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 215 | `            self._walk(child)` | Recursively validates a child AST node. |
| 216 | `        # Leave loop context after all nested children are checked.` | Comment/guideline in the current code. |
| 217 | `        # LINE: Decrease loop depth after cultivate body is checked.` | Comment/guideline in the current code. |
| 218 | `        self._in_loop -= 1` | Leaves loop context after checking loop body. |
| 219 | `` | Blank spacing line. |
| 220 | `    # AUTO: Defines function `_check_WhileLoop`.` | Comment/guideline in the current code. |
| 221 | `    def _check_WhileLoop(self, node):` | Starts a node-specific semantic checker. |
| 222 | `        # Same context rule as cultivate: grow allows prune/skip inside.` | Comment/guideline in the current code. |
| 223 | `        # LINE: Increase loop depth before checking grow body.` | Comment/guideline in the current code. |
| 224 | `        self._in_loop += 1` | Marks that validation is now inside a loop. |
| 225 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current code. |
| 226 | `        for child in node.children:` | Loops through children/symbols. |
| 227 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 228 | `            self._walk(child)` | Recursively validates a child AST node. |
| 229 | `        # LINE: Decrease loop depth after grow body.` | Comment/guideline in the current code. |
| 230 | `        self._in_loop -= 1` | Leaves loop context after checking loop body. |
| 231 | `` | Blank spacing line. |
| 232 | `    # AUTO: Defines function `_check_DoWhileLoop`.` | Comment/guideline in the current code. |
| 233 | `    def _check_DoWhileLoop(self, node):` | Starts a node-specific semantic checker. |
| 234 | `        # AUTO: Adds into `self._in_loop`.` | Comment/guideline in the current code. |
| 235 | `        self._in_loop += 1` | Marks that validation is now inside a loop. |
| 236 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current code. |
| 237 | `        for child in node.children:` | Loops through children/symbols. |
| 238 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 239 | `            self._walk(child)` | Recursively validates a child AST node. |
| 240 | `        # AUTO: Subtracts from `self._in_loop`.` | Comment/guideline in the current code. |
| 241 | `        self._in_loop -= 1` | Leaves loop context after checking loop body. |
| 242 | `` | Blank spacing line. |
| 243 | `    # AUTO: Defines function `_check_Switch`.` | Comment/guideline in the current code. |
| 244 | `    def _check_Switch(self, node):` | Starts a node-specific semantic checker. |
| 245 | `        # LINE: harvest/variety context allows prune inside switch cases.` | Comment/guideline in the current code. |
| 246 | `        self._in_switch += 1` | Marks that validation is now inside harvest/switch context. |
| 247 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current code. |
| 248 | `        for child in node.children:` | Loops through children/symbols. |
| 249 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 250 | `            self._walk(child)` | Recursively validates a child AST node. |
| 251 | `        # LINE: Leave switch context after all cases are checked.` | Comment/guideline in the current code. |
| 252 | `        self._in_switch -= 1` | Leaves harvest/switch context. |
| 253 | `` | Blank spacing line. |
| 254 | `    # AUTO: Defines function `_check_Break`.` | Comment/guideline in the current code. |
| 255 | `    def _check_Break(self, node):` | Starts a node-specific semantic checker. |
| 256 | `        # prune is valid only while the walker is inside a loop or harvest.` | Comment/guideline in the current code. |
| 257 | `        # LINE: If no loop/switch context, prune is illegal.` | Comment/guideline in the current code. |
| 258 | `        if self._in_loop == 0 and self._in_switch == 0:` | Checks if skip/prune is illegally outside a loop. |
| 259 | `            # AUTO: Appends a value to a list.` | Comment/guideline in the current code. |
| 260 | `            self.errors.append(` | Adds a semantic error message to the result list. |
| 261 | `                # AUTO: Executes this statement.` | Comment/guideline in the current code. |
| 262 | `                f"SEMANTIC error line {node.line}: 'prune' used outside a loop or switch.")` | Semantic support logic. |
| 263 | `` | Blank spacing line. |
| 264 | `    # AUTO: Defines function `_check_Continue`.` | Comment/guideline in the current code. |
| 265 | `    def _check_Continue(self, node):` | Starts a node-specific semantic checker. |
| 266 | `        # skip is valid only while the walker is inside a loop.` | Comment/guideline in the current code. |
| 267 | `        # LINE: If no loop context, skip is illegal.` | Comment/guideline in the current code. |
| 268 | `        if self._in_loop == 0:` | Checks if skip/prune is illegally outside a loop. |
| 269 | `            # AUTO: Appends a value to a list.` | Comment/guideline in the current code. |
| 270 | `            self.errors.append(` | Adds a semantic error message to the result list. |
| 271 | `                # AUTO: Executes this statement.` | Comment/guideline in the current code. |
| 272 | `                f"SEMANTIC error line {node.line}: 'skip' used outside a loop.")` | Semantic support logic. |
| 273 | `` | Blank spacing line. |
| 274 | `    # AUTO: Defines function `_check_Return`.` | Comment/guideline in the current code. |
| 275 | `    def _check_Return(self, node):` | Starts a node-specific semantic checker. |
| 276 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current code. |
| 277 | `        for child in node.children:` | Loops through children/symbols. |
| 278 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 279 | `            self._walk(child)` | Recursively validates a child AST node. |
| 280 | `` | Blank spacing line. |
| 281 | `    # AUTO: Defines function `_check_PrintStatement`.` | Comment/guideline in the current code. |
| 282 | `    def _check_PrintStatement(self, node):` | Starts a node-specific semantic checker. |
| 283 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current code. |
| 284 | `        for child in node.children:` | Loops through children/symbols. |
| 285 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 286 | `            self._walk(child)` | Recursively validates a child AST node. |
| 287 | `` | Blank spacing line. |
| 288 | `    # AUTO: Defines function `_check_Condition`.` | Comment/guideline in the current code. |
| 289 | `    def _check_Condition(self, node):` | Starts a node-specific semantic checker. |
| 290 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current code. |
| 291 | `        for child in node.children:` | Loops through children/symbols. |
| 292 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 293 | `            self._walk(child)` | Recursively validates a child AST node. |
| 294 | `` | Blank spacing line. |
| 295 | `    # AUTO: Defines function `_check_Update`.` | Comment/guideline in the current code. |
| 296 | `    def _check_Update(self, node):` | Starts a node-specific semantic checker. |
| 297 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current code. |
| 298 | `        for child in node.children:` | Loops through children/symbols. |
| 299 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 300 | `            self._walk(child)` | Recursively validates a child AST node. |
| 301 | `` | Blank spacing line. |
| 302 | `    # AUTO: Defines function `_check_List`.` | Comment/guideline in the current code. |
| 303 | `    def _check_List(self, node):` | Starts a node-specific semantic checker. |
| 304 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current code. |
| 305 | `        for child in node.children:` | Loops through children/symbols. |
| 306 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 307 | `            self._walk(child)` | Recursively validates a child AST node. |
| 308 | `` | Blank spacing line. |
| 309 | `    # AUTO: Defines function `_check_ListAccess`.` | Comment/guideline in the current code. |
| 310 | `    def _check_ListAccess(self, node):` | Starts a node-specific semantic checker. |
| 311 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current code. |
| 312 | `        for child in node.children:` | Loops through children/symbols. |
| 313 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 314 | `            self._walk(child)` | Recursively validates a child AST node. |
| 315 | `` | Blank spacing line. |
| 316 | `    # AUTO: Defines function `_check_TypeCast`.` | Comment/guideline in the current code. |
| 317 | `    def _check_TypeCast(self, node):` | Starts a node-specific semantic checker. |
| 318 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current code. |
| 319 | `        for child in node.children:` | Loops through children/symbols. |
| 320 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 321 | `            self._walk(child)` | Recursively validates a child AST node. |
| 322 | `` | Blank spacing line. |
| 323 | `    # AUTO: Defines function `_check_MemberAccess`.` | Comment/guideline in the current code. |
| 324 | `    def _check_MemberAccess(self, node):` | Starts a node-specific semantic checker. |
| 325 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current code. |
| 326 | `        for child in node.children:` | Loops through children/symbols. |
| 327 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 328 | `            self._walk(child)` | Recursively validates a child AST node. |
| 329 | `` | Blank spacing line. |
| 330 | `    # AUTO: Defines function `_check_BundleDefinition`.` | Comment/guideline in the current code. |
| 331 | `    def _check_BundleDefinition(self, node):` | Starts a node-specific semantic checker. |
| 332 | `        # AUTO: Checks this condition.` | Comment/guideline in the current code. |
| 333 | `        if not node.bundle_name:` | Checks a semantic condition. |
| 334 | `            # AUTO: Appends a value to a list.` | Comment/guideline in the current code. |
| 335 | `            self.errors.append(` | Adds a semantic error message to the result list. |
| 336 | `                # AUTO: Executes this statement.` | Comment/guideline in the current code. |
| 337 | `                f"SEMANTIC error line {node.line}: Bundle definition missing name.")` | Semantic support logic. |
| 338 | `` | Blank spacing line. |
| 339 | `    # AUTO: Defines function `_check_Append`.` | Comment/guideline in the current code. |
| 340 | `    def _check_Append(self, node):` | Starts a node-specific semantic checker. |
| 341 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current code. |
| 342 | `        for child in node.children:` | Loops through children/symbols. |
| 343 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 344 | `            self._walk(child)` | Recursively validates a child AST node. |
| 345 | `` | Blank spacing line. |
| 346 | `    # AUTO: Defines function `_check_Insert`.` | Comment/guideline in the current code. |
| 347 | `    def _check_Insert(self, node):` | Starts a node-specific semantic checker. |
| 348 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current code. |
| 349 | `        for child in node.children:` | Loops through children/symbols. |
| 350 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 351 | `            self._walk(child)` | Recursively validates a child AST node. |
| 352 | `` | Blank spacing line. |
| 353 | `    # AUTO: Defines function `_check_Remove`.` | Comment/guideline in the current code. |
| 354 | `    def _check_Remove(self, node):` | Starts a node-specific semantic checker. |
| 355 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current code. |
| 356 | `        for child in node.children:` | Loops through children/symbols. |
| 357 | `            # AUTO: Calls `self._walk`.` | Comment/guideline in the current code. |
| 358 | `            self._walk(child)` | Recursively validates a child AST node. |
| 359 | `` | Blank spacing line. |
| 360 | `# AUTO: Defines function `validate_ast`.` | Comment/guideline in the current code. |
| 361 | `def validate_ast(ast, symbol_table_data):` | Public wrapper used by server.py. |
| 362 | `    # LINE: Create a fresh validator for this compile/run.` | Comment/guideline in the current code. |
| 363 | `    validator = ASTValidator()` | Stores or updates semantic state. |
| 364 | `    # LINE: Run validator and return its result.` | Comment/guideline in the current code. |
| 365 | `    return validator.validate(ast, symbol_table_data)` | Returns result to caller. |

## 11. Line-by-Line: symbol_table.py
| Line | Code | Explanation |
|---:|---|---|
| 1 | `` | Blank spacing line. |
| 2 | `` | Blank spacing line. |
| 3 | `# AUTO: Defines class `SymbolTable`.` | Comment/guideline in the current code. |
| 4 | `class SymbolTable:` | Defines storage for variables, functions, scopes, and bundle types. |
| 5 | `    # AUTO: Defines function `__init__`.` | Comment/guideline in the current code. |
| 6 | `    def __init__(self):` | Initializes object state. |
| 7 | `        # AUTO: Sets `self.variables`.` | Comment/guideline in the current code. |
| 8 | `        self.variables = {}` | Stores or updates semantic state. |
| 9 | `        # AUTO: Sets `self.global_variables`.` | Comment/guideline in the current code. |
| 10 | `        self.global_variables = {}` | Stores or updates semantic state. |
| 11 | `        # AUTO: Sets `self.functions`.` | Comment/guideline in the current code. |
| 12 | `        self.functions = {}` | Stores or updates semantic state. |
| 13 | `        # AUTO: Sets `self.scopes`.` | Comment/guideline in the current code. |
| 14 | `        self.scopes = [{}]` | Stores or updates semantic state. |
| 15 | `        # AUTO: Sets `self.current_func_name`.` | Comment/guideline in the current code. |
| 16 | `        self.current_func_name = None` | Stores or updates semantic state. |
| 17 | `        # AUTO: Sets `self.function_variables`.` | Comment/guideline in the current code. |
| 18 | `        self.function_variables = {}` | Stores or updates semantic state. |
| 19 | `        # AUTO: Sets `self.bundle_types`.` | Comment/guideline in the current code. |
| 20 | `        self.bundle_types = {}` | Stores or updates semantic state. |
| 21 | `` | Blank spacing line. |
| 22 | `    # AUTO: Defines function `declare_variable`.` | Comment/guideline in the current code. |
| 23 | `    def declare_variable(self, name, type_, value=None, is_list=False, is_fertile=False):` | Stores a variable in the current symbol-table scope. |
| 24 | `        # AUTO: Sets `scope`.` | Comment/guideline in the current code. |
| 25 | `        scope = self.scopes[-1]` | Stores or updates semantic state. |
| 26 | `        # AUTO: Sets `current_func`.` | Comment/guideline in the current code. |
| 27 | `        current_func = self.current_func_name` | Stores or updates semantic state. |
| 28 | `    ` | Blank spacing line. |
| 29 | `` | Blank spacing line. |
| 30 | `        # AUTO: Checks this condition.` | Comment/guideline in the current code. |
| 31 | `        if name in self.functions:` | Rejects variable name that conflicts with a function. |
| 32 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in the current code. |
| 33 | `            return f"Semantic Error: Variable '{name}' already declared as a function."` | Returns a semantic error string to caller. |
| 34 | `` | Blank spacing line. |
| 35 | `        # AUTO: Checks this condition.` | Comment/guideline in the current code. |
| 36 | `        if current_func:` | Checks a semantic condition. |
| 37 | `            # AUTO: Checks this condition.` | Comment/guideline in the current code. |
| 38 | `            if current_func not in self.function_variables:` | Checks a semantic condition. |
| 39 | `                # AUTO: Sets `self.function_variables[current_func]`.` | Comment/guideline in the current code. |
| 40 | `                self.function_variables[current_func] = set()` | Stores or updates semantic state. |
| 41 | `` | Blank spacing line. |
| 42 | `            # AUTO: Checks this condition.` | Comment/guideline in the current code. |
| 43 | `            if name in self.function_variables[current_func]:` | Checks a semantic condition. |
| 44 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current code. |
| 45 | `                return f"Semantic Error: Variable '{name}' already declared in this function."` | Returns a semantic error string to caller. |
| 46 | `` | Blank spacing line. |
| 47 | `            # AUTO: Calls `self.function_variables[current_func].add`.` | Comment/guideline in the current code. |
| 48 | `            self.function_variables[current_func].add(name)` | Semantic support logic. |
| 49 | `` | Blank spacing line. |
| 50 | `        # AUTO: Checks this condition.` | Comment/guideline in the current code. |
| 51 | `        if self.current_func_name:` | Checks a semantic condition. |
| 52 | `            ` | Blank spacing line. |
| 53 | `            # AUTO: Sets `scope[name]`.` | Comment/guideline in the current code. |
| 54 | `            scope[name] = {` | Stores or updates semantic state. |
| 55 | `                # AUTO: Executes this statement.` | Comment/guideline in the current code. |
| 56 | `                "type": type_,  ` | Semantic support logic. |
| 57 | `                # AUTO: Executes this statement.` | Comment/guideline in the current code. |
| 58 | `                "value": value,` | Semantic support logic. |
| 59 | `                # AUTO: Executes this statement.` | Comment/guideline in the current code. |
| 60 | `                "is_list": is_list,` | Semantic support logic. |
| 61 | `                # AUTO: Executes this statement.` | Comment/guideline in the current code. |
| 62 | `                "is_fertile": is_fertile` | Semantic support logic. |
| 63 | `            # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current code. |
| 64 | `            }` | Closes Python grouping/list/dict/call. |
| 65 | `        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current code. |
| 66 | `        else:` | Fallback branch. |
| 67 | `            # AUTO: Checks this condition.` | Comment/guideline in the current code. |
| 68 | `            if name in self.global_variables:` | Rejects duplicate global variable names. |
| 69 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current code. |
| 70 | `                return f"Semantic Error: Variable '{name}' already declared."` | Returns a semantic error string to caller. |
| 71 | `            ` | Blank spacing line. |
| 72 | `            # AUTO: Sets `self.variables[name]`.` | Comment/guideline in the current code. |
| 73 | `            self.variables[name] = {` | Stores or updates semantic state. |
| 74 | `                # AUTO: Executes this statement.` | Comment/guideline in the current code. |
| 75 | `                "type": type_,` | Semantic support logic. |
| 76 | `                # AUTO: Executes this statement.` | Comment/guideline in the current code. |
| 77 | `                "value": value,` | Semantic support logic. |
| 78 | `                # AUTO: Executes this statement.` | Comment/guideline in the current code. |
| 79 | `                "is_list": is_list,` | Semantic support logic. |
| 80 | `                # AUTO: Executes this statement.` | Comment/guideline in the current code. |
| 81 | `                "is_fertile": is_fertile` | Semantic support logic. |
| 82 | `            # AUTO: Closes the current grouped code/data.` | Comment/guideline in the current code. |
| 83 | `            }` | Closes Python grouping/list/dict/call. |
| 84 | `        ` | Blank spacing line. |
| 85 | `` | Blank spacing line. |
| 86 | `    # AUTO: Defines function `lookup_variable`.` | Comment/guideline in the current code. |
| 87 | `    def lookup_variable(self, name):` | Searches scopes/global table for a variable. |
| 88 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current code. |
| 89 | `        for i, scope in enumerate(reversed(self.scopes)):` | Loops through children/symbols. |
| 90 | `            # AUTO: Checks this condition.` | Comment/guideline in the current code. |
| 91 | `            if name in scope:` | Checks if variable exists in one scope. |
| 92 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in the current code. |
| 93 | `                return scope[name]` | Returns found variable metadata. |
| 94 | `        ` | Blank spacing line. |
| 95 | `        # AUTO: Checks this condition.` | Comment/guideline in the current code. |
| 96 | `        if name in self.variables:` | Checks a semantic condition. |
| 97 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in the current code. |
| 98 | `            return self.variables[name]` | Returns result to caller. |
| 99 | `` | Blank spacing line. |
| 100 | `        # AUTO: Returns this result to the caller.` | Comment/guideline in the current code. |
| 101 | `        return f"Semantic Error: Variable '{name}' used before declaration."` | Returns a semantic error string to caller. |
| 102 | `    ` | Blank spacing line. |
| 103 | `    # AUTO: Defines function `set_variable`.` | Comment/guideline in the current code. |
| 104 | `    def set_variable(self, name, value):` | Updates a variable value in current scope. |
| 105 | `        # AUTO: Sets `current_scope`.` | Comment/guideline in the current code. |
| 106 | `        current_scope = self.scopes[-1]` | Stores or updates semantic state. |
| 107 | `` | Blank spacing line. |
| 108 | `        # AUTO: Checks this condition.` | Comment/guideline in the current code. |
| 109 | `        if name in current_scope:` | Checks a semantic condition. |
| 110 | `            # AUTO: Sets `current_scope[name]["value"]`.` | Comment/guideline in the current code. |
| 111 | `            current_scope[name]["value"] = value` | Stores or updates semantic state. |
| 112 | `        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in the current code. |
| 113 | `        else:` | Fallback branch. |
| 114 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in the current code. |
| 115 | `            return f"Semantic Error: Variable '{name}' not declared in the current scope."` | Returns a semantic error string to caller. |
| 116 | `` | Blank spacing line. |
| 117 | `    # AUTO: Defines function `declare_function`.` | Comment/guideline in the current code. |
| 118 | `    def declare_function(self, name, return_type, params, node=None):` | Stores a function signature/node. |
| 119 | `        # AUTO: Checks this condition.` | Comment/guideline in the current code. |
| 120 | `        if name in self.functions:` | Rejects variable name that conflicts with a function. |
| 121 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in the current code. |
| 122 | `            return f"Semantic Error: Function '{name}' already declared."` | Returns a semantic error string to caller. |
| 123 | `        # AUTO: Sets `self.functions[name]`.` | Comment/guideline in the current code. |
| 124 | `        self.functions[name] = {"return_type": return_type, "params": params, "node": node}` | Stores or updates semantic state. |
| 125 | `` | Blank spacing line. |
| 126 | `    # AUTO: Defines function `lookup_function`.` | Comment/guideline in the current code. |
| 127 | `    def lookup_function(self, name):` | Finds a declared function. |
| 128 | `        # AUTO: Checks this condition.` | Comment/guideline in the current code. |
| 129 | `        if name in self.functions:` | Rejects variable name that conflicts with a function. |
| 130 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in the current code. |
| 131 | `            return self.functions[name]` | Returns result to caller. |
| 132 | `        # AUTO: Returns this result to the caller.` | Comment/guideline in the current code. |
| 133 | `        return f"Semantic Error: Function '{name}' is not defined."` | Returns a semantic error string to caller. |
| 134 | `    ` | Blank spacing line. |
| 135 | `` | Blank spacing line. |
| 136 | `    # AUTO: Defines function `enter_scope`.` | Comment/guideline in the current code. |
| 137 | `    def enter_scope(self):` | Pushes a new scope for nested blocks/functions. |
| 138 | `        # AUTO: Appends a value to a list.` | Comment/guideline in the current code. |
| 139 | `        self.scopes.append({})` | Semantic support logic. |
| 140 | `        ` | Blank spacing line. |
| 141 | `` | Blank spacing line. |
| 142 | `    # AUTO: Defines function `exit_scope`.` | Comment/guideline in the current code. |
| 143 | `    def exit_scope(self):` | Pops current scope when leaving a block/function. |
| 144 | `        # AUTO: Checks this condition.` | Comment/guideline in the current code. |
| 145 | `        if len(self.scopes) > 1:` | Checks a semantic condition. |
| 146 | `            # AUTO: Removes and returns an item.` | Comment/guideline in the current code. |
| 147 | `            self.scopes.pop()` | Semantic support logic. |
| 148 | `        ` | Blank spacing line. |
| 149 | `        # AUTO: Checks this condition.` | Comment/guideline in the current code. |
| 150 | `        if self.current_func_name:` | Checks a semantic condition. |
| 151 | `            # AUTO: Sets `current_func`.` | Comment/guideline in the current code. |
| 152 | `            current_func = self.current_func_name` | Stores or updates semantic state. |
| 153 | `` | Blank spacing line. |
| 154 | `            # AUTO: Checks this condition.` | Comment/guideline in the current code. |
| 155 | `            if current_func in self.function_variables:` | Checks a semantic condition. |
| 156 | `                # AUTO: Calls `self.function_variables[current_func].clear`.` | Comment/guideline in the current code. |
| 157 | `                self.function_variables[current_func].clear()` | Semantic support logic. |
| 158 | `` | Blank spacing line. |
| 159 | `` | Blank spacing line. |
| 160 | `    # AUTO: Defines function `debug_scopes`.` | Comment/guideline in the current code. |
| 161 | `    def debug_scopes(self):` | Prints symbol table scopes for debugging. |
| 162 | `        # AUTO: Calls `print`.` | Comment/guideline in the current code. |
| 163 | `        print("\n====== SYMBOL TABLE DEBUG ======")` | Stores or updates semantic state. |
| 164 | `        # AUTO: Calls `print`.` | Comment/guideline in the current code. |
| 165 | `        print("🔹 Local Scopes (Stacked from Global to Inner Scope):")` | Semantic support logic. |
| 166 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in the current code. |
| 167 | `        for i, scope in enumerate(self.scopes):` | Loops through children/symbols. |
| 168 | `            # AUTO: Calls `print`.` | Comment/guideline in the current code. |
| 169 | `            print(f"  Scope {i}: {scope}")` | Semantic support logic. |
| 170 | `        # AUTO: Calls `print`.` | Comment/guideline in the current code. |
| 171 | `        print("================================\n")` | Stores or updates semantic state. |
| 172 | `` | Blank spacing line. |
| 173 | `` | Blank spacing line. |

## 12. Line-by-Line: errors.py
| Line | Code | Explanation |
|---:|---|---|
| 1 | `# AUTO: Imports a module used by this file.` | Comment/guideline in the current code. |
| 2 | `import re` | Imports dependency used by semantic checking. |
| 3 | `` | Blank spacing line. |
| 4 | `# AUTO: Sets `_REDUNDANT_PREFIX`.` | Comment/guideline in the current code. |
| 5 | `_REDUNDANT_PREFIX = re.compile(r'^(Semantic Error\|Syntax Error\|Type Mismatch\|Runtime Error)\s*:?\s*', re.IGNORECASE)` | Regular expression removes duplicate error prefixes. |
| 6 | `` | Blank spacing line. |
| 7 | `` | Blank spacing line. |
| 8 | `# AUTO: Defines class `SemanticError`.` | Comment/guideline in the current code. |
| 9 | `class SemanticError(Exception):` | Defines custom exception used for semantic error messages. |
| 10 | `    # AUTO: Defines function `__init__`.` | Comment/guideline in the current code. |
| 11 | `    def __init__(self, message, line):` | Initializes object state. |
| 12 | `        # AUTO: Calls `super`.` | Comment/guideline in the current code. |
| 13 | `        super().__init__(message)` | Initializes base Exception with the message. |
| 14 | `        # AUTO: Sets `clean`.` | Comment/guideline in the current code. |
| 15 | `        clean = _REDUNDANT_PREFIX.sub('', str(message)).strip()` | Regular expression removes duplicate error prefixes. |
| 16 | `        # AUTO: Sets `self.message`.` | Comment/guideline in the current code. |
| 17 | `        self.message = f"SEMANTIC error line {line}: {clean}"` | Stores final formatted semantic error text. |
| 18 | `` | Blank spacing line. |
| 19 | `    # AUTO: Defines function `__str__`.` | Comment/guideline in the current code. |
| 20 | `    def __str__(self):` | Semantic support logic. |
| 21 | `        # AUTO: Returns this result to the caller.` | Comment/guideline in the current code. |
| 22 | `        return self.message` | Returns result to caller. |