# Interpreter Line-by-Line Review Guide

Generated: 2026-06-07 17:22:11

## 1. Purpose
The interpreter executes the validated AST. It does not check grammar anymore. It receives AST nodes and uses `interpret()` as a dispatcher to call the correct `eval_*` method. It stores runtime variables in scopes, stores functions, runs loops/conditionals, handles `reclaim`, sends `plant()` output, and waits for `water()` input when needed.

## 2. Runtime Files
| File | Lines | Role |
|---|---:|---|
| `Backend/interpreter/interpreter.py` | 2689 | Main runtime interpreter. |
| `Backend/interpreter/errors.py` | 55 | Runtime control/error classes. |
| `Backend/server.py` | 1095 | Creates interpreter after semantic success. |

## 3. Important Interpreter Lines
| Concept | File | Line | Explanation |
|---|---|---:|---|
| Server creates interpreter | `server.py` | 663 | After semantic success, server creates Interpreter. |
| Server executes AST | `server.py` | 667 | Calls interp.interpret(ast). |
| Interpreter class | `interpreter.py` | 48 | Runtime engine for AST nodes. |
| Runtime state init | `interpreter.py` | 50 | Creates output list, socketio, scopes, functions, loop flags, input storage. |
| Declare variable | `interpreter.py` | 96 | Stores runtime variable info in current scope. |
| Lookup variable | `interpreter.py` | 141 | Reads variable metadata from scope stack. |
| Set variable | `interpreter.py` | 158 | Updates existing variable value. |
| Declare function | `interpreter.py` | 175 | Stores function metadata and body node. |
| Interpret dispatcher | `interpreter.py` | 218 | Routes each AST node type to eval_* method. |
| Program execution | `interpreter.py` | 397 | Registers top-level declarations then calls root(). |
| Variable declaration eval | `interpreter.py` | 416 | Creates runtime variable with initializer/default. |
| Assignment eval | `interpreter.py` | 658 | Evaluates RHS and writes target variable/list/member. |
| Binary operation eval | `interpreter.py` | 968 | Evaluates arithmetic, comparison, logical, concatenation operators. |
| Function declaration eval | `interpreter.py` | 1369 | Registers function; does not run it yet. |
| Block eval | `interpreter.py` | 1405 | Runs statements in order until return/break/continue. |
| plant output eval | `interpreter.py` | 1436 | Evaluates plant args and emits output to UI. |
| reclaim eval | `interpreter.py` | 1614 | Raises ReturnValue to leave current function. |
| Function call eval | `interpreter.py` | 1623 | Evaluates args, enters scope, binds params, runs function body. |
| If statement eval | `interpreter.py` | 2022 | Runs spring/bud/wither branch based on condition result. |
| For loop eval | `interpreter.py` | 2097 | Runs cultivate initialization, condition, body, and update. |
| While loop eval | `interpreter.py` | 2188 | Runs grow while condition remains true. |
| Input eval | `interpreter.py` | 2514 | Handles water() interactive input. |
| InterpreterError class | `errors.py` | 24 | Formats runtime errors. |
| ReturnValue class | `errors.py` | 9 | Carries reclaim return value through nested blocks. |

## 4. Interpreter Classes and Functions
| File | Kind | Name | Lines | Purpose |
|---|---|---|---:|---|
| `Backend\interpreter\interpreter.py` | ClassDef | `Interpreter` | 48-2688 | Runtime execution engine for AST nodes. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.__init__` | 50-92 | Initializes output, socketio, scopes, functions, input and loop state. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.declare_variable` | 96-137 | Adds runtime variable metadata to current scope. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.lookup_variable` | 141-155 | Searches variable scopes from inner to outer. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.set_variable` | 158-171 | Updates an existing runtime variable. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.declare_function` | 175-181 | Stores a function declaration for later call. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.lookup_function` | 184-190 | Finds a saved function. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.enter_scope` | 194-196 | Pushes a local scope. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.exit_scope` | 200-214 | Pops local scope and clears function variable tracking. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.interpret` | 218-394 | Central dispatcher from AST node type to eval_* method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_program` | 397-412 | Registers top-level declarations and calls root(). |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_variable_declaration` | 416-557 | Creates variable values and default values. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_bundle_definition` | 560-562 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter._build_bundle_defaults` | 565-583 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_member_access` | 586-622 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_array_member_access` | 625-641 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_sturdy_declaration` | 644-654 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_assignment` | 658-964 | Executes assignments to variables, lists, and members. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_binary_op` | 968-1301 | Executes arithmetic/comparison/logical/string operators. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter._parse_literal` | 1304-1365 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_function_declaration` | 1369-1402 | Registers function signature and AST body. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_block` | 1405-1419 | Runs block statements in order. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.plant` | 1423-1425 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.plant_out` | 1428-1432 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_print` | 1436-1521 | Executes plant output. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_formatted_string` | 1524-1547 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_list` | 1551-1565 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_list_access` | 1569-1610 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_return` | 1614-1619 | Executes reclaim using ReturnValue. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_function_call` | 1623-1699 | Runs function calls with scopes and parameters. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_append` | 1703-1714 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_insert` | 1718-1744 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_remove` | 1748-1775 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_unaryop` | 1778-1964 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_cast` | 1967-2000 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_soil` | 2004-2010 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_bloom` | 2013-2019 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_if_statement` | 2022-2094 | Executes spring/bud/wither. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_for_loop` | 2097-2184 | Executes cultivate. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_while_loop` | 2188-2245 | Executes grow. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_do_while_loop` | 2249-2299 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_break` | 2303-2311 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.trigger_break` | 2314-2316 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.break_triggered` | 2319-2321 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.enter_loop` | 2324-2330 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.exit_loop` | 2333-2341 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_continue` | 2344-2352 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.continue_triggered` | 2355-2357 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.trigger_continue` | 2360-2362 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_switch` | 2366-2442 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.emit_input_request` | 2446-2448 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.provide_input` | 2451-2469 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.wait_for_input` | 2472-2511 | Runtime support/evaluator method. |
| `Backend\interpreter\interpreter.py` | method | `Interpreter.eval_input` | 2514-2688 | Executes water input handling. |
| `Backend\interpreter\errors.py` | ClassDef | `ReturnValue` | 9-14 | Internal exception carrying reclaim result. |
| `Backend\interpreter\errors.py` | method | `ReturnValue.__init__` | 12-14 | Runtime support/evaluator method. |
| `Backend\interpreter\errors.py` | ClassDef | `_CancelledError` | 18-20 | Runtime support/evaluator method. |
| `Backend\interpreter\errors.py` | ClassDef | `InterpreterError` | 24-44 | Runtime error formatter. |
| `Backend\interpreter\errors.py` | method | `InterpreterError.__init__` | 27-39 | Runtime support/evaluator method. |
| `Backend\interpreter\errors.py` | method | `InterpreterError.__str__` | 42-44 | Runtime support/evaluator method. |
| `Backend\interpreter\errors.py` | ClassDef | `InterpreterInputRequest` | 48-55 | Signals that water() needs user input. |
| `Backend\interpreter\errors.py` | method | `InterpreterInputRequest.__init__` | 51-55 | Runtime support/evaluator method. |

## 5. Key Code Blocks
### Server Runtime Handoff
Lines 640-668 in `Backend\server.py`
```python
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
```
After semantic validation succeeds, server creates Interpreter and executes the AST.

### Interpreter Runtime State
Lines 48-92 in `Backend\interpreter\interpreter.py`
```python
48: class Interpreter:
49:     # AUTO: Defines function `__init__`.
50:     def __init__(self, socketio=None):
51:         # GUIDE: Output and Socket.IO are how plant() and water() communicate with UI.
52:         # LINE: Stores output text generated by plant().
53:         self.output = []
54:         # LINE: Holds the UI/emitter object used to send output/input events.
55:         self.socketio = socketio
56: 
57:         # GUIDE: Loop state is used by prune/skip and infinite-loop protection.
58:         # LINE: Tracks active loops so prune/skip know if they are allowed.
59:         self.loop_stack = []
60:         # LINE: Becomes True when prune should stop a loop.
61:         self.break_flag = False
62:         # LINE: Becomes True when skip should jump to the next loop iteration.
63:         self.continue_flag = False
64: 
65:         # GUIDE: Input state lets water() pause until the UI sends a value.
66:         # LINE: True while water() is waiting for user input.
67:         self.input_required = False
68:         # LINE: Stores wait objects for interactive water() calls.
69:         self.input_events = {}
70:         # LINE: Stores input values received from the UI.
71:         self.input_values = {}
72: 
73:         # LINE: Optional current AST node pointer for runtime context.
74:         self.current_node = None
75:         # LINE: Optional parent AST node pointer for runtime context.
76:         self.current_parent = None
77: 
78:         # GUIDE: Runtime symbol storage. scopes[-1] is current active scope.
79:         # LINE: Older/global variable map kept for compatibility.
80:         self.variables = {}
81:         # LINE: Stores variables declared globally.
82:         self.global_variables = {}
83:         # LINE: Stores declared functions by name.
84:         self.functions = {}
85:         # LINE: Scope stack; the last dictionary is the current active scope.
86:         self.scopes = [{}]
87:         # LINE: Name of the function currently executing.
88:         self.current_func_name = None
89:         # LINE: Per-function variable tracking storage.
90:         self.function_variables = {}
91:         # LINE: Stores bundle/struct type definitions.
92:         self.bundle_types = {}
```
Constructor initializes output, socketio, loop flags, input state, variables, scopes, and functions.

### Variable Storage Helpers
Lines 96-171 in `Backend\interpreter\interpreter.py`
```python
96:     def declare_variable(self, name, type_, value=None, is_list=False, is_fertile=False):
97:         # LINE: Use the current top scope for this declaration.
98:         scope = self.scopes[-1]
99:         # LINE: Remember current function name if needed for future tracking.
100:         current_func = self.current_func_name
101:     
102: 
103:         # LINE: If name is not in current scope, create a new runtime variable entry.
104:         if name not in self.scopes[-1]:
105:             # AUTO: Sets `scope[name]`.
106:             scope[name] = {
107:                 # LINE: Store GAL type such as seed/tree/vine.
108:                 "type": type_,  
109:                 # LINE: Store the current runtime value.
110:                 "value": value,
111:                 # LINE: Mark whether this variable is an array/list.
112:                 "is_list": is_list,
113:                 # LINE: Mark whether this variable is fertile/constant.
114:                 "is_fertile": is_fertile
115:                 # AUTO: Closes the current grouped code/data.
116:                 }
117:         # AUTO: Runs when previous condition did not pass.
118:         else:
119:             # LINE: Duplicate global declaration is a semantic error.
120:             if name in self.global_variables:
121:                 # AUTO: Returns this result to the caller.
122:                 return f"Semantic Error: Variable '{name}' already declared."
123:             
124:             # LINE: Compatibility path for older global storage.
125:             self.variables[name] = {
126:                 # AUTO: Executes this statement.
127:                 "type": type_,
128:                 # AUTO: Executes this statement.
129:                 "value": value,
130:                 # AUTO: Executes this statement.
131:                 "is_list": is_list,
132:                 # AUTO: Executes this statement.
133:                 "is_fertile": is_fertile
134:             # AUTO: Closes the current grouped code/data.
135:             }
136:             # AUTO: Sets `self.global_variables[name]`.
137:             self.global_variables[name] = self.variables[name]
138:         
139: 
140:     # AUTO: Defines function `lookup_variable`.
141:     def lookup_variable(self, name):
142:         # LINE: Search from inner scope to outer scope so locals override globals.
143:         for i, scope in enumerate(reversed(self.scopes)):
144:             # AUTO: Checks this condition.
145:             if name in scope:
146:                 # LINE: Return the variable info dictionary once found.
147:                 return scope[name]
148:         
149:         # LINE: Fallback to older variable map if not found in scopes.
150:         if name in self.variables:
151:             # AUTO: Returns this result to the caller.
152:             return self.variables[name]
153: 
154:         # LINE: Returning a string means caller should raise an error.
155:         return f"Semantic Error: Variable '{name}' used before declaration."
156:     
157:     # AUTO: Defines function `set_variable`.
158:     def set_variable(self, name, value):
159:         # LINE: Search all scopes from inner to outer for assignment target.
160:         for i in reversed(range(len(self.scopes))):
161:             # AUTO: Sets `scope`.
162:             scope = self.scopes[i]
163:             # AUTO: Checks this condition.
164:             if name in scope:
165:                 # LINE: Update only the stored value, not type/list/fertile metadata.
166:                 scope[name]["value"] = value
167:                 # AUTO: Returns this result to the caller.
168:                 return  
169: 
170:         # LINE: Assignment target was never declared.
171:         return f"Semantic Error: Variable '{name}' not declared in any scope."
```
declare_variable, lookup_variable, and set_variable manage runtime variable state.

### Main Dispatcher
Lines 218-394 in `Backend\interpreter\interpreter.py`
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
```
interpret() checks the AST node class/type and routes to the matching eval_* method.

### Program Entry
Lines 397-412 in `Backend\interpreter\interpreter.py`
```python
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
```
eval_program registers top-level functions and calls root().

### Variable Declaration Runtime
Lines 416-557 in `Backend\interpreter\interpreter.py`
```python
416:     def eval_variable_declaration(self, node):
417:         # GUIDE: Creates a runtime variable entry, using either an initializer value
418:         # or a default value based on the GAL data type.
419:         # LINE: First child stores the declared type, like seed/tree/vine.
420:         var_type = node.children[0].value
421:         # LINE: Second child stores the variable name.
422:         var_name = node.children[1].value
423:         # LINE: Third child is optional initializer, like = 10 or = water(seed).
424:         value_node = node.children[2] if len(node.children) > 2 else None
425:         # LINE: Starts false and becomes true for array/list initializers.
426:         is_list = False
427:         
428:         # LINE: Default runtime values when there is no initializer.
429:         default_values = {
430:             # If a variable has no initializer, these are the runtime defaults.
431:             # AUTO: Executes this statement.
432:             "seed": 0,
433:             # AUTO: Executes this statement.
434:             "tree": 0.0,
435:             # AUTO: Executes this statement.
436:             "leaf": '',
437:             # AUTO: Executes this statement.
438:             "vine": "",
439:             # AUTO: Executes this statement.
440:             "branch": False,
441:         # AUTO: Closes the current grouped code/data.
442:         }
443: 
444:         # LINE: If initializer exists, evaluate it before declaring the variable.
445:         if value_node:
446:             # There is an initializer, so evaluate the initializer AST node now.
447:             # LINE: List initializer means array/list value.
448:             if value_node.node_type == "List":
449:                 # Array/list initializer: evaluate each element and store a
450:                 # Python list as the runtime value.
451:                 # AUTO: Checks this condition.
452:                 if var_type in self.bundle_types:
453:                     # AUTO: Sets `value`.
454:                     value = [self._build_bundle_defaults(var_type) for _ in value_node.children]
455:                 # AUTO: Runs when previous condition did not pass.
456:                 else:
457:                     # AUTO: Defines function `materialize`.
458:                     def materialize(list_node):
459:                         # LINE: Convert nested ListNode AST into Python list.
460:                         result = []
461:                         # AUTO: Starts a loop over these values.
462:                         for child in list_node.children:
463:                             # LINE: Recursively handle nested array values.
464:                             if isinstance(child, ListNode):
465:                                 # AUTO: Appends a value to a list.
466:                                 result.append(materialize(child))
467:                             # AUTO: Runs when previous condition did not pass.
468:                             else:
469:                                 # LINE: Evaluate normal element expression/literal.
470:                                 item = self.interpret(child)
471:                                 # AUTO: Checks this condition.
472:                                 if var_type == "seed" and isinstance(item, float):
473:                                     # AUTO: Sets `item`.
474:                                     item = int(item)
475:                                 # AUTO: Checks the next alternate condition.
476:                                 elif var_type == "tree":
477:                                     # AUTO: Sets `item`.
478:                                     item = float(item)
479:                                 # AUTO: Appends a value to a list.
480:                                 result.append(item)
481:                         # AUTO: Returns this result to the caller.
482:                         return result
483:                     # LINE: Store the materialized Python list as the variable value.
484:                     value = materialize(value_node)
485: 
486:                 # LINE: Mark this declaration as a list/array.
487:                 is_list = True
488: 
489:             # AUTO: Runs when previous condition did not pass.
490:             else:
491:                 # Normal initializer such as seed x = 10 or vine s = "hi".
492:                 # LINE: Evaluate the initializer expression.
493:                 value = self.interpret(value_node)
494: 
495:                 # LINE: Convert tree-like float into seed integer if needed.
496:                 if var_type == "seed" and isinstance(value, float):
497:                     # AUTO: Sets `value`.
498:                     value = int(value)
499: 
500:                 # LINE: seed/tree only accept numeric values.
501:                 if var_type in {"tree", "seed"}:
502:                     # AUTO: Checks this condition.
503:                     if not isinstance(value, (int, float)):
504:                         # AUTO: Stops this flow by raising an error.
505:                         raise InterpreterError(f"Semantic Error: Type Mismatch! Invalid value for {var_name}", node.line)
506:                     
507:                     # LINE: Prevent branch/boolean from being treated as a number.
508:                     if isinstance(value, bool):
509:                         # AUTO: Stops this flow by raising an error.
510:                         raise InterpreterError(f"Semantic Error: Type Mismatch! Invalid value for {var_name}", node.line)
511: 
512: 
513:                     # LINE: tree stores integer initializer as float.
514:                     if var_type == "tree" and isinstance(value, int):
515:                         # AUTO: Sets `value`.
516:                         value = float(value)
517:                 
518:                 # LINE: leaf must receive a string-like character value.
519:                 if var_type == "leaf":
520:                     # AUTO: Checks this condition.
521:                     if not isinstance(value, str):
522:                         # AUTO: Stops this flow by raising an error.
523:                         raise InterpreterError(f"Semantic Error: Type Mismatch! Invalid value for {var_name}", node.line)
524: 
525:                 # LINE: vine must receive a string value.
526:                 if var_type == "vine":
527:                     # AUTO: Checks this condition.
528:                     if not isinstance(value, str):
529:                         # AUTO: Stops this flow by raising an error.
530:                         raise InterpreterError(f"Semantic Error: Type Mismatch! Invalid value for {var_name}", node.line)
531: 
532:                 # LINE: branch can convert 0/1 numeric-style values into bool.
533:                 if var_type == "branch":
534:                     # AUTO: Checks this condition.
535:                     if isinstance(value, int) or isinstance(value, float):
536:                         # AUTO: Checks this condition.
537:                         if value == 0:
538:                             # AUTO: Sets `value`.
539:                             value = False
540:                         # AUTO: Runs when previous condition did not pass.
541:                         else:
542:                             # AUTO: Sets `value`.
543:                             value = True
544:         # AUTO: Runs when previous condition did not pass.
545:         else:
546:             # No initializer, so use a default value based on type.
547:             # LINE: Bundle variables get default member dictionaries.
548:             if var_type in self.bundle_types:
549:                 # AUTO: Sets `value`.
550:                 value = self._build_bundle_defaults(var_type)
551:             # AUTO: Runs when previous condition did not pass.
552:             else:
553:                 # LINE: Built-in types get their default value from default_values.
554:                 value = default_values.get(var_type, None)
555:         
556:         # LINE: Save the variable into the current runtime scope.            
557:         self.declare_variable(var_name, var_type, value, is_list=is_list)
```
Creates variables with default or initialized values.

### Assignment Runtime
Lines 658-724 in `Backend\interpreter\interpreter.py`
```python
658:     def eval_assignment(self, node):
659:         # GUIDE: Assignments evaluate RHS first, then write into a variable,
660:         # array element, or bundle member target.
661:         # LINE: Left child is the assignment target.
662:         target_node = node.children[0]
663:         # LINE: Right child is the value/expression being assigned.
664:         value_node = node.children[1]
665: 
666:         # LINE: RHS list means assign an array/list value.
667:         if value_node.node_type == "List":
668:             # RHS is an array/list value.
669:             # AUTO: Sets `value`.
670:             value = []
671:             # AUTO: Starts a loop over these values.
672:             for val in value_node.children:
673:                 # LINE: Evaluate each list item before storing.
674:                 item = self.interpret(val)
675:                 # AUTO: Appends a value to a list.
676:                 value.append(item)
677:         # AUTO: Runs when previous condition did not pass.
678:         else:
679:             # RHS is an expression, literal, function call, water(), etc.
680:             # LINE: Evaluate the right side first, such as a + b or water(seed).
681:             value = self.interpret(value_node)
682:             # AUTO: Checks this condition.
683:             if isinstance(value_node, AppendNode) or isinstance(value_node, InsertNode) or isinstance(value_node, RemoveNode):
684:                 # LINE: append/insert/remove already changed the list themselves.
685:                 return
686: 
687:         # LINE: If target is arr[index], write into a list element.
688:         if target_node.node_type == "ListAccess":
689:             # Assignment into an array/list element, e.g. arr[i] = value.
690:             # LINE: Collect indexes for arr[i] or nested arr[i][j].
691:             indices = []
692:             # LINE: Start from the ListAccess target node.
693:             current = target_node
694:             # LINE: Walk nested ListAccess nodes from outside to inside.
695:             while hasattr(current, 'node_type') and current.node_type == "ListAccess":
696:                 # LINE: Evaluate the index expression inside brackets.
697:                 idx = self.interpret(current.children[1].children[0])
698:                 # LINE: Index must be an integer.
699:                 if not isinstance(idx, int):
700:                     # AUTO: Stops this flow by raising an error.
701:                     raise InterpreterError(f"Runtime Error: List index must be an integer. Got '{idx}'", node.line)
702:                 # LINE: Store the index for later navigation.
703:                 indices.append(idx)
704:                 # LINE: Move toward the base list name.
705:                 current = current.children[0].value
706: 
707:             # LINE: current now holds the base list variable name.
708:             list_name = current
709:             # LINE: Look up the list variable.
710:             list_entry = self.lookup_variable(list_name)
711:             # AUTO: Checks this condition.
712:             if isinstance(list_entry, str):
713:                 # AUTO: Stops this flow by raising an error.
714:                 raise InterpreterError(list_entry, node.line)
715: 
716:             # LINE: Get the actual list/string value.
717:             list_value = list_entry["value"]
718:             # LINE: Target must be a list or string.
719:             if not isinstance(list_value, (list, str)):
720:                 # AUTO: Stops this flow by raising an error.
721:                 raise InterpreterError(f"Runtime Error: Variable '{list_name}' is not a list.", node.line)
722: 
723:             # LINE: String index assignment path.
724:             if isinstance(list_value, str):
```
Begins assignment handling by evaluating target and value.

### Binary Operator Runtime
Lines 968-1048 in `Backend\interpreter\interpreter.py`
```python
968:     def eval_binary_op(self, node):
969:         # GUIDE: Binary operations evaluate left/right child expressions before
970:         # applying arithmetic, comparison, logical, or concat behavior.
971:         # Example AST for x + y:
972:         # left child = Identifier(x), right child = Identifier(y), value = "+"
973:         # LINE: Evaluate the left operand first.
974:         left = self.interpret(node.children[0])
975:         # LINE: Evaluate the right operand second.
976:         right = self.interpret(node.children[1])
977:         # LINE: node.value stores the actual operator symbol.
978:         operator = node.value
979: 
980:         # LINE: Backtick is GAL string concatenation.
981:         if operator == '`':
982:             # GAL string concat operator.
983:             # AUTO: Sets `result`.
984:             result = str(left) + str(right)
985:             # AUTO: Returns this result to the caller.
986:             return result
987: 
988:         # Convert token/literal strings like "10", "~5", "sunshine" into Python
989:         # values like 10, -5, True before applying the operator.
990:         # LINE: Convert left literal text into Python int/float/bool/string if needed.
991:         left = self._parse_literal(left)
992:         # LINE: Convert right literal text into Python int/float/bool/string if needed.
993:         right = self._parse_literal(right)
994: 
995:         # LINE: Plus with any string becomes concatenation.
996:         if operator == '+' and (isinstance(left, str) or isinstance(right, str)):
997:             # AUTO: Sets `result`.
998:             result = str(left) + str(right)
999:             # AUTO: Returns this result to the caller.
1000:             return result
1001: 
1002:         # AUTO: Starts protected code that can catch errors.
1003:         try:
1004:             # LINE: Choose operation based on the operator stored in the AST node.
1005:             if operator == '+':
1006:                 # Numeric addition. If both operands are non-numeric, convert
1007:                 # truthy/empty values into numbers first.
1008:                 # AUTO: Checks this condition.
1009:                 if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):
1010:                     # AUTO: Checks this condition.
1011:                     if isinstance(left, bool):
1012:                         # AUTO: Executes this statement.
1013:                         left = 1 if left == True else 0
1014:                     # AUTO: Checks the next alternate condition.
1015:                     elif isinstance(left, str):
1016:                         # AUTO: Executes this statement.
1017:                         left = 1 if left != "" else 0
1018:                     # AUTO: Checks this condition.
1019:                     if isinstance(right, bool):
1020:                         # AUTO: Executes this statement.
1021:                         right = 1 if right == True else 0
1022:                     # AUTO: Checks the next alternate condition.
1023:                     elif isinstance(right, str):
1024:                         # AUTO: Executes this statement.
1025:                         right = 1 if right != "" else 0
1026:                 # AUTO: Returns this result to the caller.
1027:                 return left + right  # type: ignore[operator]
1028:             
1029:             # AUTO: Checks the next alternate condition.
1030:             elif operator == '-':
1031:                 # LINE: Subtraction path.
1032:                 if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):
1033:                     # AUTO: Checks this condition.
1034:                     if isinstance(left, bool):
1035:                         # AUTO: Executes this statement.
1036:                         left = 1 if left == True else 0
1037:                     # AUTO: Checks the next alternate condition.
1038:                     elif isinstance(left, str):
1039:                         # AUTO: Executes this statement.
1040:                         left = 1 if left != "" else 0
1041:                     # AUTO: Checks this condition.
1042:                     if isinstance(right, bool):
1043:                         # AUTO: Executes this statement.
1044:                         right = 1 if right == True else 0
1045:                     # AUTO: Checks the next alternate condition.
1046:                     elif isinstance(right, str):
1047:                         # AUTO: Executes this statement.
1048:                         right = 1 if right != "" else 0
```
Evaluates left/right operands and selected operator.

### Function Declaration Runtime
Lines 1369-1402 in `Backend\interpreter\interpreter.py`
```python
1369:     def eval_function_declaration(self, node):
1370:         # GUIDE: Function declarations are registered, not executed immediately.
1371:         # The saved body runs later when a FunctionCallNode is interpreted.
1372:         # LINE: First child stores function return type.
1373:         return_type = node.children[0].value
1374:         # LINE: Second child stores the parameter list node.
1375:         parameters_node = node.children[1]
1376:         # LINE: node.value stores the function name.
1377:         func_name = node.value
1378: 
1379:         # LINE: Collect parameters into simple dictionaries.
1380:         params = []
1381:         # AUTO: Checks this condition.
1382:         if parameters_node and len(parameters_node.children) > 0:
1383:             # AUTO: Starts a loop over these values.
1384:             for param in parameters_node.children:
1385:                 # LINE: Parameter nodes must have the expected AST shape.
1386:                 if not hasattr(param, 'node_type') or param.node_type != 'Parameter':
1387:                     # AUTO: Stops this flow by raising an error.
1388:                     raise Exception(f"Invalid parameter: {param.value}")
1389:                 # LINE: First parameter child is type.
1390:                 param_type = param.children[0].value
1391:                 # LINE: Second parameter child is name.
1392:                 param_name = param.children[1].value
1393:                 # LINE: Detect array/list parameter marker.
1394:                 is_list = any(child.node_type == "ArrayParam" for child in param.children)
1395:                 # LINE: Save this parameter metadata.
1396:                 params.append({"name": param_name, "type": param_type, "is_list": is_list})
1397: 
1398:         # LINE: Register the function in self.functions for later calls.
1399:         self.declare_function(func_name, return_type, params, node)
1400: 
1401:         # LINE: Declaration itself produces no runtime value.
1402:         return None
```
Registers function metadata and body for later calls.

### Function Call Runtime
Lines 1623-1699 in `Backend\interpreter\interpreter.py`
```python
1623:     def eval_function_call(self, node):
1624:         # GUIDE: Function call flow; evaluate args, enter scope, bind params,
1625:         # run the saved body, then leave the scope.
1626:         # LINE: node.value is the function name being called.
1627:         function_name = node.value
1628: 
1629:         # Evaluate all actual arguments before entering the called function.
1630:         # Example: gcd(a, b) becomes [value_of_a, value_of_b].
1631:         # LINE: Evaluate every argument expression before binding parameters.
1632:         args = [self.interpret(arg.children[0]) for arg in node.children]
1633: 
1634:         # Look up the function saved earlier by eval_function_declaration().
1635:         # LINE: Fetch function metadata from self.functions.
1636:         func_info = self.lookup_function(function_name)
1637:         # AUTO: Checks this condition.
1638:         if isinstance(func_info, str):
1639:             # AUTO: Stops this flow by raising an error.
1640:             raise InterpreterError(func_info, node.line)
1641: 
1642:         # LINE: Expected parameter list saved during declaration.
1643:         expected_params = func_info["params"]
1644:         # LINE: FunctionDeclarationNode containing the function body.
1645:         function_node = func_info["node"]
1646: 
1647:         # LINE: Argument count must match parameter count.
1648:         if len(expected_params) != len(args):
1649:             # AUTO: Stops this flow by raising an error.
1650:             raise InterpreterError(
1651:                 # AUTO: Executes this statement.
1652:                 f"Runtime Error: Function '{function_name}' expects {len(expected_params)} argument(s), got {len(args)}.",
1653:                 # AUTO: Executes this statement.
1654:                 node.line
1655:             # AUTO: Closes the current grouped code/data.
1656:             )
1657:         
1658:         # LINE: Enter a new local function scope.
1659:         self.enter_scope()
1660:         
1661:         # AUTO: Starts protected code that can catch errors.
1662:         try:
1663:             # LINE: Bind each argument value to its parameter variable.
1664:             for i, param in enumerate(expected_params):
1665:                 # Bind each argument value to its parameter name in the new
1666:                 # function scope. Example: parameter "a" receives 48.
1667:                 # AUTO: Sets `param_name`.
1668:                 param_name = param["name"]
1669:                 # AUTO: Sets `param_type`.
1670:                 param_type = param["type"]
1671:                 # AUTO: Sets `arg_value`.
1672:                 arg_value = args[i]
1673:                 # AUTO: Sets `is_list`.
1674:                 is_list = param.get("is_list", False)
1675:                 # LINE: Parameters are stored like local variables.
1676:                 self.declare_variable(param_name, param_type, arg_value, is_list=is_list)
1677: 
1678:             # AUTO: Starts protected code that can catch errors.
1679:             try:
1680:                 # Execute the function body block. If reclaim runs inside,
1681:                 # eval_return raises ReturnValue and jumps to the except below.
1682:                 # LINE: Run the saved function body.
1683:                 self.eval_block(function_node.children[2])
1684: 
1685:             # AUTO: Handles the matching error case.
1686:             except ReturnValue as ret:
1687:                 # The reclaim value becomes the function call result.
1688:                 # LINE: Return reclaim's value to the caller.
1689:                 return ret.value
1690: 
1691:             # LINE: If no reclaim value happened, function returns None.
1692:             return None
1693: 
1694:         # AUTO: Runs cleanup code no matter what happened.
1695:         finally:
1696:             # LINE: Always leave the function scope even if an error/reclaim happens.
1697:             self.exit_scope()
1698:             # LINE: Clear active function marker.
1699:             self.current_func_name = None
```
Evaluates arguments, enters scope, binds parameters, runs body, catches reclaim.

### plant Runtime
Lines 1436-1521 in `Backend\interpreter\interpreter.py`
```python
1436:     def eval_print(self, node):
1437:         # GUIDE: plant() evaluates args, applies optional {} formatting, and
1438:         # emits the final text to the UI terminal.
1439:         # LINE: plant() with no arguments prints nothing.
1440:         if not node.children:
1441:             # AUTO: Returns this result to the caller.
1442:             return
1443: 
1444:         # LINE: First plant argument can be normal text or a format string.
1445:         first = node.children[0]
1446: 
1447:         # LINE: Evaluate the first argument.
1448:         evaluated_first = self.interpret(first)
1449:         # AUTO: Checks this condition.
1450:         if isinstance(evaluated_first, float):
1451:             # LINE: Limit displayed float decimals to 5 digits.
1452:             whole, dot, dec = str(evaluated_first).partition('.')
1453:             # AUTO: Sets `dec`.
1454:             dec = dec[:5]
1455:             # AUTO: Sets `evaluated_first`.
1456:             evaluated_first = float(f"{whole}.{dec}")
1457: 
1458:         # LINE: If first string has {}, use Python format with remaining args.
1459:         if isinstance(evaluated_first, str) and '{}' in evaluated_first:
1460:             # AUTO: Sets `values`.
1461:             values = []
1462:             # AUTO: Starts a loop over these values.
1463:             for arg in node.children[1:]:
1464:                 # LINE: Evaluate each format value.
1465:                 value = self.interpret(arg)
1466:                 # AUTO: Checks this condition.
1467:                 if isinstance(value, str) and not isinstance(self.lookup_variable(value), str):
1468:                     # AUTO: Sets `value`.
1469:                     value = self.lookup_variable(value)["value"]  # type: ignore[index]
1470:                 
1471:                 # AUTO: Checks this condition.
1472:                 if isinstance(value, float):
1473:                     # AUTO: Sets `whole, dot, dec`.
1474:                     whole, dot, dec = str(value).partition('.')
1475:                     # AUTO: Sets `dec`.
1476:                     dec = dec[:5]
1477:                     # AUTO: Sets `value`.
1478:                     value = float(f"{whole}.{dec}")
1479: 
1480:                 # AUTO: Appends a value to a list.
1481:                 values.append(value)
1482: 
1483:             # AUTO: Starts protected code that can catch errors.
1484:             try:
1485:                 # LINE: Replace {} placeholders with evaluated values.
1486:                 output_str = evaluated_first.format(*values)
1487:             # AUTO: Handles the matching error case.
1488:             except Exception as e:
1489:                 # AUTO: Stops this flow by raising an error.
1490:                 raise Exception(f"Format error in plant(): '{evaluated_first}' with {values}: {e}")
1491: 
1492:             # LINE: Send formatted output to UI.
1493:             self.plant(output_str)
1494:             # AUTO: Returns this result to the caller.
1495:             return
1496: 
1497:         # LINE: Multiple plant args without {} are joined with spaces.
1498:         if len(node.children) > 1:
1499:             # AUTO: Sets `parts`.
1500:             parts = [str(evaluated_first)]
1501:             # AUTO: Starts a loop over these values.
1502:             for arg in node.children[1:]:
1503:                 # LINE: Evaluate each extra plant argument.
1504:                 value = self.interpret(arg)
1505:                 # AUTO: Checks this condition.
1506:                 if isinstance(value, float):
1507:                     # AUTO: Sets `whole, dot, dec`.
1508:                     whole, dot, dec = str(value).partition('.')
1509:                     # AUTO: Sets `dec`.
1510:                     dec = dec[:5]
1511:                     # AUTO: Sets `value`.
1512:                     value = float(f"{whole}.{dec}")
1513:                 # AUTO: Appends a value to a list.
1514:                 parts.append(str(value))
1515:             # LINE: Output the combined text.
1516:             self.plant(" ".join(parts))
1517:             # AUTO: Returns this result to the caller.
1518:             return
1519: 
1520:         # LINE: Single plant argument output path.
1521:         self.plant(str(evaluated_first))
```
Evaluates plant arguments, formatting, and sends output.

### reclaim Runtime
Lines 1614-1619 in `Backend\interpreter\interpreter.py`
```python
1614:     def eval_return(self, node):
1615:         # GUIDE: reclaim jumps out of the current function by raising ReturnValue.
1616:         # LINE: Evaluate reclaim value if present; root usually has none.
1617:         value = self.interpret(node.children[0]) if node.children else None
1618:         # LINE: Raise ReturnValue so nested blocks immediately exit the function.
1619:         raise ReturnValue(value)
```
Raises ReturnValue to leave function immediately.

### spring/bud/wither Runtime
Lines 2022-2094 in `Backend\interpreter\interpreter.py`
```python
2022:     def eval_if_statement(self, node):
2023:         # LINE: Evaluate spring condition from first child.
2024:         condition_result = self.interpret(node.children[0].children[0])
2025:         # LINE: Create local scope for this if/else chain.
2026:         self.enter_scope()
2027: 
2028: 
2029:         # AUTO: Starts protected code that can catch errors.
2030:         try:
2031:             # LINE: If spring condition is True, run spring block.
2032:             if condition_result:
2033:                 # AUTO: Calls `self.eval_block`.
2034:                 self.eval_block(node.children[1])
2035:             
2036:             # AUTO: Runs when previous condition did not pass.
2037:             else:
2038:                 # LINE: Start checking children after spring condition/block.
2039:                 current_node = 2
2040:                 # LINE: Walk bud/wither nodes until one runs or list ends.
2041:                 while current_node < len(node.children):
2042:                     
2043:                     # LINE: Current child can be ElseIfStatement or ElseStatement.
2044:                     elif_node = node.children[current_node]
2045: 
2046:                     # LINE: bud condition path.
2047:                     if elif_node.node_type == "ElseIfStatement":
2048:                         # LINE: Evaluate bud condition.
2049:                         elif_condition_result = self.interpret(elif_node.children[0].children[0])
2050: 
2051:                         # LINE: bud condition must be branch/bool.
2052:                         if not isinstance(elif_condition_result, bool):
2053:                             # AUTO: Stops this flow by raising an error.
2054:                             raise InterpreterError(f"Runtime Error: Condition must be a boolean. Got '{condition_result}'", node.line)
2055:                         
2056:                         # LINE: If bud is true, run its block and stop the chain.
2057:                         if elif_condition_result:
2058:                             # AUTO: Starts protected code that can catch errors.
2059:                             try:
2060:                                 # LINE: bud block gets its own local scope.
2061:                                 self.enter_scope()
2062:                                 # LINE: Execute bud block.
2063:                                 self.eval_block(elif_node.children[1])
2064:                             # AUTO: Runs cleanup code no matter what happened.
2065:                             finally:
2066:                                 # LINE: Leave bud local scope.
2067:                                 self.exit_scope()
2068:                             # AUTO: Returns this result to the caller.
2069:                             return
2070:                         
2071:                     # LINE: wither/else path.
2072:                     elif elif_node.node_type == "ElseStatement":
2073:                         # AUTO: Starts protected code that can catch errors.
2074:                         try:
2075:                             # LINE: wither block gets its own local scope.
2076:                             self.enter_scope()
2077:                             # LINE: Execute wither block.
2078:                             self.eval_block(elif_node.children[0])
2079:                         # AUTO: Runs cleanup code no matter what happened.
2080:                         finally:
2081:                             # LINE: Leave wither local scope.
2082:                             self.exit_scope()
2083:                         # AUTO: Returns this result to the caller.
2084:                         return
2085: 
2086:                     # LINE: Move to next bud/wither child.
2087:                     current_node += 1
2088:         # AUTO: Runs cleanup code no matter what happened.
2089:         finally:
2090:             # LINE: Always leave spring chain scope.
2091:             self.exit_scope()
2092: 
2093:         # LINE: If no block ran, return no value.
2094:         return None
```
Evaluates conditions and runs the chosen block.

### cultivate Runtime
Lines 2097-2184 in `Backend\interpreter\interpreter.py`
```python
2097:     def eval_for_loop(self, node):
2098:         # GUIDE: cultivate flow; initialize once, check condition, run block,
2099:         # apply update expressions, then repeat.
2100:         # LINE: Mark that execution is inside a cultivate loop.
2101:         self.enter_loop('for')
2102:         # LINE: Create loop-local scope.
2103:         self.enter_scope()
2104:         # LINE: Safety limit to prevent infinite loops.
2105:         MAX_LOOP_ITERATIONS = 10000
2106:         # LINE: Counts how many loop iterations already ran.
2107:         LOOP_COUNTER = 0
2108: 
2109:         # AUTO: Starts protected code that can catch errors.
2110:         try:
2111:             # LINE: First child is the initializer part of cultivate.
2112:             instantiate_node = node.children[0]
2113: 
2114:             # AUTO: Checks this condition.
2115:             if isinstance(instantiate_node, VariableDeclarationNode):
2116:                 # First part of cultivate: seed i = 0
2117:                 # AUTO: Sets `var_type`.
2118:                 var_type = instantiate_node.children[0].value
2119:                 # AUTO: Sets `var_name`.
2120:                 var_name = instantiate_node.children[1].value
2121:                 # AUTO: Sets `initial_value_node`.
2122:                 initial_value_node = self.interpret(instantiate_node.children[2])
2123:                 # AUTO: Calls `self.declare_variable`.
2124:                 self.declare_variable(var_name, var_type, initial_value_node)
2125: 
2126:             # AUTO: Checks the next alternate condition.
2127:             elif isinstance(instantiate_node, AssignmentNode):
2128:                 # First part of cultivate: i = 0
2129:                 # AUTO: Sets `var_name`.
2130:                 var_name = instantiate_node.children[0].value
2131:                 # AUTO: Sets `initial_value_node`.
2132:                 initial_value_node = self.interpret(instantiate_node.children[1])
2133:                 # AUTO: Sets `self.lookup_variable(var_name)["value"]`.
2134:                 self.lookup_variable(var_name)["value"] = initial_value_node  # type: ignore
2135: 
2136:             # LINE: Second child is the loop condition.
2137:             condition_node = node.children[1].children[0]
2138:             # Second part of cultivate: evaluate condition such as i <= n.
2139:             # LINE: Evaluate condition before the first iteration.
2140:             condition_result = self.interpret(condition_node)
2141: 
2142:             # LINE: Loop condition must evaluate to branch/bool.
2143:             if not isinstance(condition_result, bool):
2144:                 # AUTO: Stops this flow by raising an error.
2145:                 raise InterpreterError(f"Runtime Error: Condition must be a boolean. Got '{condition_result}'", node.line)
2146: 
2147:             # LINE: Keep running while condition is sunshine/True.
2148:             while condition_result:
2149:                 # AUTO: Adds into `LOOP_COUNTER`.
2150:                 LOOP_COUNTER += 1
2151:                 # AUTO: Checks this condition.
2152:                 if LOOP_COUNTER > MAX_LOOP_ITERATIONS:
2153:                     # AUTO: Stops this flow by raising an error.
2154:                     raise InterpreterError("Runtime Error: Infinite loop detected!", node.line)
2155: 
2156:                 # LINE: Execute the loop body block.
2157:                 self.eval_block(node.children[3])
2158: 
2159:                 # AUTO: Checks this condition.
2160:                 if self.continue_flag:
2161:                     # LINE: skip clears here before updates/next condition.
2162:                     self.continue_flag = False  
2163: 
2164:                 # AUTO: Checks this condition.
2165:                 if self.break_triggered():
2166:                     # LINE: prune stops the loop immediately.
2167:                     break
2168:                 
2169:                 # LINE: Run update expressions after each iteration.
2170:                 for update_expr in node.children[2].children:
2171:                     # Third part of cultivate: apply update such as i++.
2172:                     # AUTO: Dispatches an AST node for execution.
2173:                     self.interpret(update_expr)
2174: 
2175:                 # Re-check the loop condition for the next iteration.
2176:                 # LINE: Re-evaluate condition to decide if loop continues.
2177:                 condition_result = self.interpret(condition_node)
2178: 
2179:         # AUTO: Runs cleanup code no matter what happened.
2180:         finally:
2181:             # LINE: Always remove loop scope after loop ends/errors.
2182:             self.exit_scope()
2183:             # LINE: Always clear loop tracking after loop ends/errors.
2184:             self.exit_loop()
```
Runs for-loop init, condition, body, update, and loop cleanup.

### water Runtime
Lines 2514-2688 in `Backend\interpreter\interpreter.py`
```python
2514:     def eval_input(self, node):
2515:         # GUIDE: water() finds target variable/type from parent node, asks the
2516:         # UI for a value, then converts that value before assignment.
2517:         # LINE: Parent tells whether water() is declaration, assignment, or expression.
2518:         parent_node = node.parent
2519:         # LINE: Case seed n = water(seed);
2520:         if isinstance(parent_node, VariableDeclarationNode):
2521:             # Case: seed n = water(seed);
2522:             # AUTO: Sets `var_name`.
2523:             var_name = parent_node.children[1].value
2524:             # AUTO: Sets `var_type`.
2525:             var_type = parent_node.children[0].value
2526:         
2527:         # LINE: Case water(n); or n = water(seed);
2528:         elif isinstance(parent_node, AssignmentNode):
2529:             # Case: water(n); or n = water(seed);
2530:             # AUTO: Sets `target`.
2531:             target = parent_node.children[0]
2532:             # LINE: Array input target path like arr[i].
2533:             if isinstance(target, ListAccessNode):
2534:                 # AUTO: Sets `current`.
2535:                 current = target
2536:                 # AUTO: Repeats while this condition is true.
2537:                 while hasattr(current, 'node_type') and current.node_type == "ListAccess":
2538:                     # AUTO: Sets `current`.
2539:                     current = current.children[0].value
2540:                 # AUTO: Sets `var_name`.
2541:                 var_name = current if isinstance(current, str) else str(current)
2542:                 # AUTO: Sets `var_type`.
2543:                 var_type = self.lookup_variable(var_name)["type"]  # type: ignore
2544:             # AUTO: Runs when previous condition did not pass.
2545:             else:
2546:                 # LINE: Simple variable input target path.
2547:                 var_name = target.value
2548:                 # AUTO: Sets `var_type`.
2549:                 var_type = self.lookup_variable(var_name)["type"]  # type: ignore
2550: 
2551:         # AUTO: Runs when previous condition did not pass.
2552:         else:
2553:             # Case: water(seed) used directly as an expression.
2554:             # LINE: Expression water() has no variable target, so use temporary name.
2555:             var_name = "_input"
2556:             # AUTO: Checks this condition.
2557:             if node.value and "(" in node.value:
2558:                 # LINE: Extract requested input type from water(seed/tree/etc.).
2559:                 inner = node.value.split("(")[1].rstrip(")")
2560:                 # AUTO: Sets `var_type`.
2561:                 var_type = inner if inner in {"seed", "tree", "leaf", "branch", "vine"} else "vine"
2562:             # AUTO: Runs when previous condition did not pass.
2563:             else:
2564:                 # LINE: Plain water() defaults to vine/string input.
2565:                 var_type = "vine"
2566: 
2567:         # LINE: Prompt text sent to UI.
2568:         prompt = f"Input for {var_name}: "
2569:         # LINE: Mark interpreter as waiting for input.
2570:         self.input_required = True
2571: 
2572: 
2573:         # Ask the UI/browser for input and wait until capture_input sends it.
2574:         # LINE: Send input_required event to frontend.
2575:         self.emit_input_request(var_name, prompt)
2576: 
2577:         # LINE: Pause execution until frontend sends input.
2578:         input_value = self.wait_for_input(var_name)
2579: 
2580: 
2581:         # LINE: Mark input wait as finished.
2582:         self.input_required = False
2583: 
2584:         # LINE: Convert user text into seed integer when needed.
2585:         if var_type == "seed":
2586:             # AUTO: Sets `original_input`.
2587:             original_input = input_value
2588:             # AUTO: Checks this condition.
2589:             if isinstance(input_value, str) and input_value.startswith('-'):
2590:                 # AUTO: Stops this flow by raising an error.
2591:                 raise InterpreterError(f"Runtime Error: GAL uses '~' for negative numbers, not '-'. Got '{original_input}'; did you mean '~{original_input[1:]}'?", node.line)  # type: ignore
2592:             # AUTO: Checks this condition.
2593:             if isinstance(input_value, str) and input_value.startswith('~'):
2594:                 # AUTO: Sets `input_value`.
2595:                 input_value = '-' + input_value[1:]
2596:             # AUTO: Starts protected code that can catch errors.
2597:             try:
2598:                 # AUTO: Checks this condition.
2599:                 if len(input_value.strip('-').lstrip('0')) > 16:
2600:                     # AUTO: Stops this flow by raising an error.
2601:                     raise InterpreterError(f"Runtime Error: Input value exceeds maximum number of 16 digits", node.line)
2602:                 # AUTO: Sets `input_value`.
2603:                 input_value = int(float(input_value))  # type: ignore
2604:             # AUTO: Handles the matching error case.
2605:             except ValueError:
2606:                 # AUTO: Stops this flow by raising an error.
2607:                 raise InterpreterError(f"Runtime Error: Expected integer value, got '{original_input}'", node.line)
2608: 
2609:         # AUTO: Checks the next alternate condition.
2610:         elif var_type == "tree":
2611:             # AUTO: Sets `original_input`.
2612:             original_input = input_value
2613:             # AUTO: Checks this condition.
2614:             if isinstance(input_value, str) and input_value.startswith('-'):
2615:                 # AUTO: Stops this flow by raising an error.
2616:                 raise InterpreterError(f"Runtime Error: GAL uses '~' for negative numbers, not '-'. Got '{original_input}'; did you mean '~{original_input[1:]}'?", node.line)  # type: ignore
2617:             # AUTO: Checks this condition.
2618:             if isinstance(input_value, str) and input_value.startswith('~'):
2619:                 # AUTO: Sets `input_value`.
2620:                 input_value = '-' + input_value[1:]
2621:             # AUTO: Starts protected code that can catch errors.
2622:             try:
2623:                 # AUTO: Checks this condition.
2624:                 if '.' in input_value:  # type: ignore
2625:                     # AUTO: Sets `integer_part, decimal_part`.
2626:                     integer_part, decimal_part = str(input_value).split('.')
2627:                     # AUTO: Checks this condition.
2628:                     if len(integer_part.strip('-').lstrip('0')) > 16:
2629:                         # AUTO: Stops this flow by raising an error.
2630:                         raise InterpreterError(f"Runtime Error: Input value exceeds maximum number of 16 digits", node.line)
2631:                     # AUTO: Checks this condition.
2632:                     if len(decimal_part.rstrip('0')) > 5:
2633:                         # AUTO: Stops this flow by raising an error.
2634:                         raise InterpreterError(f"Runtime Error: Input value exceeds maximum number of 5 decimal numbers", node.line)
2635: 
2636:                 # AUTO: Runs when previous condition did not pass.
2637:                 else:
2638:                     # AUTO: Checks this condition.
2639:                     if len(input_value.strip('-').lstrip('0')) > 16:
2640:                         # AUTO: Stops this flow by raising an error.
2641:                         raise InterpreterError(f"Runtime Error: Input value exceeds maximum number of 16 digits", node.line)
2642: 
2643:                 # AUTO: Sets `input_value`.
2644:                 input_value = float(input_value)  # type: ignore
2645: 
2646: 
2647:             # AUTO: Handles the matching error case.
2648:             except ValueError:
2649:                 # AUTO: Stops this flow by raising an error.
2650:                 raise InterpreterError(f"Runtime Error: Expected float value, got '{original_input}'", node.line)
2651: 
2652:         # AUTO: Checks the next alternate condition.
2653:         elif var_type == "branch":
2654:             # AUTO: Checks this condition.
2655:             if input_value == "true" or input_value == "false":
2656:                 # AUTO: Executes this statement.
2657:                 suggestion = "sunshine" if input_value == "true" else "frost"
2658:                 # AUTO: Stops this flow by raising an error.
2659:                 raise InterpreterError(f"Runtime Error: GAL uses 'sunshine' and 'frost' for booleans, not 'true'/'false'. Got '{input_value}'; did you mean '{suggestion}'?", node.line)
2660:             # AUTO: Checks this condition.
2661:             if input_value == "sunshine":
2662:                 # AUTO: Sets `input_value`.
2663:                 input_value = True
2664:             # AUTO: Checks the next alternate condition.
2665:             elif input_value == "frost":
2666:                 # AUTO: Sets `input_value`.
2667:                 input_value = False
2668:             # AUTO: Runs when previous condition did not pass.
2669:             else:
2670:                 # AUTO: Stops this flow by raising an error.
2671:                 raise InterpreterError(f"Runtime Error: expected branch value (sunshine/frost), got '{input_value}'", node.line)
2672:             
2673:         # AUTO: Checks the next alternate condition.
2674:         elif var_type == "leaf":
2675:             # AUTO: Checks this condition.
2676:             if len(input_value) != 1:  # type: ignore
2677:                 # AUTO: Stops this flow by raising an error.
2678:                 raise InterpreterError(f"Runtime Error: Expected a single character for leaf, got '{input_value}'", node.line)
2679:             # AUTO: Sets `input_value`.
2680:             input_value = str(input_value)
2681: 
2682:         # AUTO: Checks the next alternate condition.
2683:         elif var_type == "vine":
2684:             # AUTO: Sets `input_value`.
2685:             input_value = str(input_value)
2686: 
2687:         # AUTO: Returns this result to the caller.
2688:         return input_value
```
Handles water() input requests and value conversion.

### Runtime Error Classes
Lines 9-55 in `Backend\interpreter\errors.py`
```python
9: class ReturnValue(Exception):
10: 
11:     # AUTO: Defines function `__init__`.
12:     def __init__(self, value):
13:         # AUTO: Sets `self.value`.
14:         self.value = value
15: 
16: 
17: # AUTO: Defines class `_CancelledError`.
18: class _CancelledError(Exception):
19:     # AUTO: Does nothing for this required block.
20:     pass
21: 
22: 
23: # AUTO: Defines class `InterpreterError`.
24: class InterpreterError(Exception):
25: 
26:     # AUTO: Defines function `__init__`.
27:     def __init__(self, message, line):
28:         # AUTO: Calls `super`.
29:         super().__init__(message)
30:         # AUTO: Sets `clean`.
31:         clean = _REDUNDANT_PREFIX.sub('', str(message)).strip()
32:         # AUTO: Checks this condition.
33:         if line is not None and str(line) != "":
34:             # AUTO: Sets `self.message`.
35:             self.message = f"RUNTIME error line {line}: {clean}"
36:         # AUTO: Runs when previous condition did not pass.
37:         else:
38:             # AUTO: Sets `self.message`.
39:             self.message = clean
40: 
41:     # AUTO: Defines function `__str__`.
42:     def __str__(self):
43:         # AUTO: Returns this result to the caller.
44:         return self.message
45: 
46: 
47: # AUTO: Defines class `InterpreterInputRequest`.
48: class InterpreterInputRequest(Exception):
49: 
50:     # AUTO: Defines function `__init__`.
51:     def __init__(self, prompt, line):
52:         # AUTO: Sets `self.prompt`.
53:         self.prompt = prompt
54:         # AUTO: Sets `self.line`.
55:         self.line = line
```
ReturnValue, InterpreterError, and input request classes.

## 6. Sample Program Used For Runtime Walkthrough
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

Runtime result: `interpret(ast) -> None; outputs=['Odd  product: 3', 'Even product: 6', 'Odd  product: 9', 'Even product: 12']`
Final stored functions: `['timesThree', 'root']`
Final scopes after root exits: `[{}]`

## 7. Runtime Output
| # | Output emitted by plant() |
|---:|---|
| 1 | `Odd  product: 3` |
| 2 | `Even product: 6` |
| 3 | `Odd  product: 9` |
| 4 | `Even product: 12` |

## 8. Runtime Variable Trace
| Moment | Name | Value | Explanation |
|---|---|---|---|
| Before root call | functions | timesThree, root | Both saved by eval_program; no root statements executed yet. |
| Root declaration | value | 0 | seed default/initializer value. |
| Root declaration | i | 0 | seed default because no initializer. |
| For init | i | 1 | cultivate init assignment. |
| Iteration 1 | value | 3 | timesThree(1) returns 3; wither branch prints odd. |
| Iteration 2 | value | 6 | timesThree(2) returns 6; spring branch prints even. |
| Iteration 3 | value | 9 | timesThree(3) returns 9; wither branch prints odd. |
| Iteration 4 | value | 12 | timesThree(4) returns 12; spring branch prints even. |
| After loop | i | 5 | Condition i <= 4 fails, loop stops. |
| After reclaim | scopes | [{}] | Function scope is popped by finally in eval_function_call. |

## 9. Interpreter Simulation Step-by-Step
| Step | Phase | Exact Process |
|---:|---|---|
| 1 | Server already finished lexer/parser/semantic | `server.py` line 663: creates `interp = Interpreter(socketio=collector)` after semantic success. |
| 2 | Server starts runtime | `server.py` line 667: calls `interp.interpret(ast)`. The AST root is a ProgramNode. |
| 3 | Dispatcher sees ProgramNode | `interpreter.py` line 222: `interpret()` routes to `eval_program(node)`. |
| 4 | eval_program registers functions | `interpreter.py` line 368: visits top-level children. Function declarations are saved, not executed yet. |
| 5 | timesThree is saved | `interpreter.py` line 1369: stores return type seed, parameter seed n, and function body in `self.functions`. |
| 6 | root is saved | The root FunctionDeclarationNode is also stored in `self.functions`. |
| 7 | eval_program creates root call | `interpreter.py` line 410: creates `FunctionCallNode("root", [], node.line)`. |
| 8 | root function call starts | `interpreter.py` line 1623: looks up root, enters a new scope, then runs root body. |
| 9 | Declare value | `interpreter.py` line 416: `seed value = 0;` creates value as seed with value 0. |
| 10 | Declare i | `seed i;` has no initializer, so it uses default seed value 0. |
| 11 | cultivate starts | `interpreter.py` line 2097: evaluates init `i = 1`, then condition `i <= 4`. |
| 12 | Loop iteration 1 | `i=1`; `timesThree(1)` enters function scope with `n=1`, returns `1*3=3`; condition `3 % 2 == 0` is false, so wither prints `Odd  product: 3`. |
| 13 | Loop iteration 2 | `i++` makes i=2; `timesThree(2)` returns 6; spring condition true, so prints `Even product: 6`. |
| 14 | Loop iteration 3 | `i=3`; function returns 9; condition false, so prints `Odd  product: 9`. |
| 15 | Loop iteration 4 | `i=4`; function returns 12; condition true, so prints `Even product: 12`. |
| 16 | Loop stops | `i++` makes i=5; condition `i <= 4` becomes false, so cultivate exits. |
| 17 | reclaim ends root | `interpreter.py` line 1614: raises ReturnValue(None), caught by eval_function_call, then root scope exits. |
| 18 | Runtime ends | Final emitted outputs: Odd  product: 3, Even product: 6, Odd  product: 9, Even product: 12 |

## 10. Line-by-Line: interpreter.py
| Line | Code | Explanation |
|---:|---|---|
| 1 | `` | Blank spacing line. |
| 2 | `"""Runtime interpreter for the GAL AST.` | Module documentation string explaining runtime purpose. |
| 3 | `` | Blank spacing line. |
| 4 | `After lexer, parser, and semantic validation succeed, server.py calls` | Runtime support logic. |
| 5 | `Interpreter.interpret(ast). This file executes AST nodes and stores runtime` | Runtime support logic. |
| 6 | `state such as variables, functions, scopes, loop flags, and output.` | Runtime support logic. |
| 7 | `"""` | Module documentation string explaining runtime purpose. |
| 8 | `` | Blank spacing line. |
| 9 | `# AUTO: Imports names from another module.` | Comment/guideline in current code. |
| 10 | `from shared.ast_nodes import *` | Imports dependency used during runtime execution. |
| 11 | `` | Blank spacing line. |
| 12 | `# AUTO: Imports a module used by this file.` | Comment/guideline in current code. |
| 13 | `import threading` | Imports dependency used during runtime execution. |
| 14 | `# AUTO: Imports a module used by this file.` | Comment/guideline in current code. |
| 15 | `import sys` | Imports dependency used during runtime execution. |
| 16 | `` | Blank spacing line. |
| 17 | `# AUTO: Calls `sys.setrecursionlimit`.` | Comment/guideline in current code. |
| 18 | `sys.setrecursionlimit(10000)` | Allows deeper recursive function calls/AST walking before Python stops recursion. |
| 19 | `` | Blank spacing line. |
| 20 | `# AUTO: Starts protected code that can catch errors.` | Comment/guideline in current code. |
| 21 | `try:` | Starts protected block for optional runtime dependency or error handling. |
| 22 | `    # AUTO: Imports a module used by this file.` | Comment/guideline in current code. |
| 23 | `    import eventlet.event as _ev` | Imports dependency used during runtime execution. |
| 24 | `    # AUTO: Sets `_USE_EVENTLET`.` | Comment/guideline in current code. |
| 25 | `    _USE_EVENTLET = True` | Stores or updates runtime state/value. |
| 26 | `# AUTO: Handles the matching error case.` | Comment/guideline in current code. |
| 27 | `except ImportError:` | Handles the matching runtime/import error case. |
| 28 | `    # AUTO: Sets `_USE_EVENTLET`.` | Comment/guideline in current code. |
| 29 | `    _USE_EVENTLET = False` | Stores or updates runtime state/value. |
| 30 | `` | Blank spacing line. |
| 31 | `` | Blank spacing line. |
| 32 | `# AUTO: Imports names from another module.` | Comment/guideline in current code. |
| 33 | `from semantic.errors import SemanticError  # noqa: F401 - some runtime checks raise it` | Imports dependency used during runtime execution. |
| 34 | `# AUTO: Imports names from another module.` | Comment/guideline in current code. |
| 35 | `from interpreter.errors import (  # noqa: F401 - runtime-specific error classes` | Imports dependency used during runtime execution. |
| 36 | `    # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 37 | `    ReturnValue,` | Runtime support logic. |
| 38 | `    # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 39 | `    _CancelledError,` | Runtime support logic. |
| 40 | `    # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 41 | `    InterpreterError,` | Runtime support logic. |
| 42 | `    # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 43 | `    InterpreterInputRequest,` | Runtime support logic. |
| 44 | `# AUTO: Closes the current grouped code/data.` | Comment/guideline in current code. |
| 45 | `)` | Closes Python grouping/list/dict/call. |
| 46 | `` | Blank spacing line. |
| 47 | `# AUTO: Defines class `Interpreter`.` | Comment/guideline in current code. |
| 48 | `class Interpreter:` | Defines the GAL runtime interpreter. |
| 49 | `    # AUTO: Defines function `__init__`.` | Comment/guideline in current code. |
| 50 | `    def __init__(self, socketio=None):` | Initializes object state. |
| 51 | `        # GUIDE: Output and Socket.IO are how plant() and water() communicate with UI.` | Comment/guideline in current code. |
| 52 | `        # LINE: Stores output text generated by plant().` | Comment/guideline in current code. |
| 53 | `        self.output = []` | Stores or updates runtime state/value. |
| 54 | `        # LINE: Holds the UI/emitter object used to send output/input events.` | Comment/guideline in current code. |
| 55 | `        self.socketio = socketio` | Stores or updates runtime state/value. |
| 56 | `` | Blank spacing line. |
| 57 | `        # GUIDE: Loop state is used by prune/skip and infinite-loop protection.` | Comment/guideline in current code. |
| 58 | `        # LINE: Tracks active loops so prune/skip know if they are allowed.` | Comment/guideline in current code. |
| 59 | `        self.loop_stack = []` | Stores or updates runtime state/value. |
| 60 | `        # LINE: Becomes True when prune should stop a loop.` | Comment/guideline in current code. |
| 61 | `        self.break_flag = False` | Stores or updates runtime state/value. |
| 62 | `        # LINE: Becomes True when skip should jump to the next loop iteration.` | Comment/guideline in current code. |
| 63 | `        self.continue_flag = False` | Stores or updates runtime state/value. |
| 64 | `` | Blank spacing line. |
| 65 | `        # GUIDE: Input state lets water() pause until the UI sends a value.` | Comment/guideline in current code. |
| 66 | `        # LINE: True while water() is waiting for user input.` | Comment/guideline in current code. |
| 67 | `        self.input_required = False` | Stores or updates runtime state/value. |
| 68 | `        # LINE: Stores wait objects for interactive water() calls.` | Comment/guideline in current code. |
| 69 | `        self.input_events = {}` | Stores or updates runtime state/value. |
| 70 | `        # LINE: Stores input values received from the UI.` | Comment/guideline in current code. |
| 71 | `        self.input_values = {}` | Stores or updates runtime state/value. |
| 72 | `` | Blank spacing line. |
| 73 | `        # LINE: Optional current AST node pointer for runtime context.` | Comment/guideline in current code. |
| 74 | `        self.current_node = None` | Stores or updates runtime state/value. |
| 75 | `        # LINE: Optional parent AST node pointer for runtime context.` | Comment/guideline in current code. |
| 76 | `        self.current_parent = None` | Stores or updates runtime state/value. |
| 77 | `` | Blank spacing line. |
| 78 | `        # GUIDE: Runtime symbol storage. scopes[-1] is current active scope.` | Comment/guideline in current code. |
| 79 | `        # LINE: Older/global variable map kept for compatibility.` | Comment/guideline in current code. |
| 80 | `        self.variables = {}` | Stores or updates runtime state/value. |
| 81 | `        # LINE: Stores variables declared globally.` | Comment/guideline in current code. |
| 82 | `        self.global_variables = {}` | Stores or updates runtime state/value. |
| 83 | `        # LINE: Stores declared functions by name.` | Comment/guideline in current code. |
| 84 | `        self.functions = {}` | Stores or updates runtime state/value. |
| 85 | `        # LINE: Scope stack; the last dictionary is the current active scope.` | Comment/guideline in current code. |
| 86 | `        self.scopes = [{}]` | Stores or updates runtime state/value. |
| 87 | `        # LINE: Name of the function currently executing.` | Comment/guideline in current code. |
| 88 | `        self.current_func_name = None` | Stores or updates runtime state/value. |
| 89 | `        # LINE: Per-function variable tracking storage.` | Comment/guideline in current code. |
| 90 | `        self.function_variables = {}` | Stores or updates runtime state/value. |
| 91 | `        # LINE: Stores bundle/struct type definitions.` | Comment/guideline in current code. |
| 92 | `        self.bundle_types = {}` | Stores or updates runtime state/value. |
| 93 | `` | Blank spacing line. |
| 94 | `` | Blank spacing line. |
| 95 | `    # AUTO: Defines function `declare_variable`.` | Comment/guideline in current code. |
| 96 | `    def declare_variable(self, name, type_, value=None, is_list=False, is_fertile=False):` | Starts runtime variable declaration helper. |
| 97 | `        # LINE: Use the current top scope for this declaration.` | Comment/guideline in current code. |
| 98 | `        scope = self.scopes[-1]` | Stores or updates runtime state/value. |
| 99 | `        # LINE: Remember current function name if needed for future tracking.` | Comment/guideline in current code. |
| 100 | `        current_func = self.current_func_name` | Stores or updates runtime state/value. |
| 101 | `    ` | Blank spacing line. |
| 102 | `` | Blank spacing line. |
| 103 | `        # LINE: If name is not in current scope, create a new runtime variable entry.` | Comment/guideline in current code. |
| 104 | `        if name not in self.scopes[-1]:` | Checks a runtime condition. |
| 105 | `            # AUTO: Sets `scope[name]`.` | Comment/guideline in current code. |
| 106 | `            scope[name] = {` | Stores or updates runtime state/value. |
| 107 | `                # LINE: Store GAL type such as seed/tree/vine.` | Comment/guideline in current code. |
| 108 | `                "type": type_,  ` | Runtime support logic. |
| 109 | `                # LINE: Store the current runtime value.` | Comment/guideline in current code. |
| 110 | `                "value": value,` | Runtime support logic. |
| 111 | `                # LINE: Mark whether this variable is an array/list.` | Comment/guideline in current code. |
| 112 | `                "is_list": is_list,` | Runtime support logic. |
| 113 | `                # LINE: Mark whether this variable is fertile/constant.` | Comment/guideline in current code. |
| 114 | `                "is_fertile": is_fertile` | Runtime support logic. |
| 115 | `                # AUTO: Closes the current grouped code/data.` | Comment/guideline in current code. |
| 116 | `                }` | Closes Python grouping/list/dict/call. |
| 117 | `        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 118 | `        else:` | Fallback runtime branch. |
| 119 | `            # LINE: Duplicate global declaration is a semantic error.` | Comment/guideline in current code. |
| 120 | `            if name in self.global_variables:` | Checks a runtime condition. |
| 121 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 122 | `                return f"Semantic Error: Variable '{name}' already declared."` | Returns runtime value/result to caller. |
| 123 | `            ` | Blank spacing line. |
| 124 | `            # LINE: Compatibility path for older global storage.` | Comment/guideline in current code. |
| 125 | `            self.variables[name] = {` | Stores or updates runtime state/value. |
| 126 | `                # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 127 | `                "type": type_,` | Runtime support logic. |
| 128 | `                # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 129 | `                "value": value,` | Runtime support logic. |
| 130 | `                # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 131 | `                "is_list": is_list,` | Runtime support logic. |
| 132 | `                # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 133 | `                "is_fertile": is_fertile` | Runtime support logic. |
| 134 | `            # AUTO: Closes the current grouped code/data.` | Comment/guideline in current code. |
| 135 | `            }` | Closes Python grouping/list/dict/call. |
| 136 | `            # AUTO: Sets `self.global_variables[name]`.` | Comment/guideline in current code. |
| 137 | `            self.global_variables[name] = self.variables[name]` | Stores or updates runtime state/value. |
| 138 | `        ` | Blank spacing line. |
| 139 | `` | Blank spacing line. |
| 140 | `    # AUTO: Defines function `lookup_variable`.` | Comment/guideline in current code. |
| 141 | `    def lookup_variable(self, name):` | Starts runtime variable lookup helper. |
| 142 | `        # LINE: Search from inner scope to outer scope so locals override globals.` | Comment/guideline in current code. |
| 143 | `        for i, scope in enumerate(reversed(self.scopes)):` | Loops through AST children/items. |
| 144 | `            # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 145 | `            if name in scope:` | Checks a runtime condition. |
| 146 | `                # LINE: Return the variable info dictionary once found.` | Comment/guideline in current code. |
| 147 | `                return scope[name]` | Returns runtime value/result to caller. |
| 148 | `        ` | Blank spacing line. |
| 149 | `        # LINE: Fallback to older variable map if not found in scopes.` | Comment/guideline in current code. |
| 150 | `        if name in self.variables:` | Checks a runtime condition. |
| 151 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 152 | `            return self.variables[name]` | Returns runtime value/result to caller. |
| 153 | `` | Blank spacing line. |
| 154 | `        # LINE: Returning a string means caller should raise an error.` | Comment/guideline in current code. |
| 155 | `        return f"Semantic Error: Variable '{name}' used before declaration."` | Returns runtime value/result to caller. |
| 156 | `    ` | Blank spacing line. |
| 157 | `    # AUTO: Defines function `set_variable`.` | Comment/guideline in current code. |
| 158 | `    def set_variable(self, name, value):` | Starts runtime assignment helper. |
| 159 | `        # LINE: Search all scopes from inner to outer for assignment target.` | Comment/guideline in current code. |
| 160 | `        for i in reversed(range(len(self.scopes))):` | Loops through AST children/items. |
| 161 | `            # AUTO: Sets `scope`.` | Comment/guideline in current code. |
| 162 | `            scope = self.scopes[i]` | Stores or updates runtime state/value. |
| 163 | `            # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 164 | `            if name in scope:` | Checks a runtime condition. |
| 165 | `                # LINE: Update only the stored value, not type/list/fertile metadata.` | Comment/guideline in current code. |
| 166 | `                scope[name]["value"] = value` | Stores or updates runtime state/value. |
| 167 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 168 | `                return  ` | Runtime support logic. |
| 169 | `` | Blank spacing line. |
| 170 | `        # LINE: Assignment target was never declared.` | Comment/guideline in current code. |
| 171 | `        return f"Semantic Error: Variable '{name}' not declared in any scope."` | Returns runtime value/result to caller. |
| 172 | `` | Blank spacing line. |
| 173 | `` | Blank spacing line. |
| 174 | `    # AUTO: Defines function `declare_function`.` | Comment/guideline in current code. |
| 175 | `    def declare_function(self, name, return_type, params, node=None):` | Starts function registration helper. |
| 176 | `        # LINE: Function names must be unique.` | Comment/guideline in current code. |
| 177 | `        if name in self.functions:` | Checks a runtime condition. |
| 178 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 179 | `            return f"Semantic Error: Function '{name}' already declared."` | Returns runtime value/result to caller. |
| 180 | `        # LINE: Save function metadata and body node for later calls.` | Comment/guideline in current code. |
| 181 | `        self.functions[name] = {"return_type": return_type, "params": params, "node": node}` | Stores or updates runtime state/value. |
| 182 | `` | Blank spacing line. |
| 183 | `    # AUTO: Defines function `lookup_function`.` | Comment/guideline in current code. |
| 184 | `    def lookup_function(self, name):` | Starts function lookup helper. |
| 185 | `        # LINE: Return saved function metadata if it exists.` | Comment/guideline in current code. |
| 186 | `        if name in self.functions:` | Checks a runtime condition. |
| 187 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 188 | `            return self.functions[name]` | Returns runtime value/result to caller. |
| 189 | `        # LINE: Return error string if function was never declared.` | Comment/guideline in current code. |
| 190 | `        return f"Semantic Error: Function '{name}' is not defined."` | Returns runtime value/result to caller. |
| 191 | `` | Blank spacing line. |
| 192 | `` | Blank spacing line. |
| 193 | `    # AUTO: Defines function `enter_scope`.` | Comment/guideline in current code. |
| 194 | `    def enter_scope(self):` | Starts helper that creates a new local scope. |
| 195 | `        # LINE: Push a new local variable dictionary.` | Comment/guideline in current code. |
| 196 | `        self.scopes.append({})` | Runtime support logic. |
| 197 | `` | Blank spacing line. |
| 198 | `` | Blank spacing line. |
| 199 | `    # AUTO: Defines function `exit_scope`.` | Comment/guideline in current code. |
| 200 | `    def exit_scope(self):` | Starts helper that exits current local scope. |
| 201 | `        # LINE: Never remove the global scope.` | Comment/guideline in current code. |
| 202 | `        if len(self.scopes) > 1:` | Checks a runtime condition. |
| 203 | `            # LINE: Pop local variables when leaving a block/function.` | Comment/guideline in current code. |
| 204 | `            self.scopes.pop()` | Runtime support logic. |
| 205 | `` | Blank spacing line. |
| 206 | `        # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 207 | `        if self.current_func_name:` | Checks a runtime condition. |
| 208 | `            # AUTO: Sets `current_func`.` | Comment/guideline in current code. |
| 209 | `            current_func = self.current_func_name` | Stores or updates runtime state/value. |
| 210 | `` | Blank spacing line. |
| 211 | `            # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 212 | `            if current_func in self.function_variables:` | Checks a runtime condition. |
| 213 | `                # AUTO: Calls `self.function_variables[current_func].clear`.` | Comment/guideline in current code. |
| 214 | `                self.function_variables[current_func].clear()` | Runtime support logic. |
| 215 | `` | Blank spacing line. |
| 216 | `` | Blank spacing line. |
| 217 | `    # AUTO: Defines function `interpret`.` | Comment/guideline in current code. |
| 218 | `    def interpret(self, node):` | Starts central AST dispatcher. |
| 219 | `        # GUIDE: Central runtime dispatcher; each AST node class is sent to its` | Comment/guideline in current code. |
| 220 | `        # matching eval_* method. This is where execution branches by node type.` | Comment/guideline in current code. |
| 221 | `        # LINE: ProgramNode means start the whole program execution.` | Comment/guideline in current code. |
| 222 | `        if isinstance(node, ProgramNode):` | Dispatcher branch for executing the whole program. |
| 223 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 224 | `            return self.eval_program(node)` | Sends ProgramNode to eval_program. |
| 225 | `        # LINE: BundleDefinitionNode registers a bundle/struct type.` | Comment/guideline in current code. |
| 226 | `        elif isinstance(node, BundleDefinitionNode):` | Alternative runtime condition. |
| 227 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 228 | `            return self.eval_bundle_definition(node)` | Returns runtime value/result to caller. |
| 229 | `        # LINE: MemberAccessNode reads obj.member.` | Comment/guideline in current code. |
| 230 | `        elif isinstance(node, MemberAccessNode):` | Alternative runtime condition. |
| 231 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 232 | `            return self.eval_member_access(node)` | Returns runtime value/result to caller. |
| 233 | `        # LINE: ArrayMemberAccessNode reads arr[i].member.` | Comment/guideline in current code. |
| 234 | `        elif isinstance(node, ArrayMemberAccessNode):` | Alternative runtime condition. |
| 235 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 236 | `            return self.eval_array_member_access(node)` | Returns runtime value/result to caller. |
| 237 | `        # LINE: VariableDeclarationNode creates a variable at runtime.` | Comment/guideline in current code. |
| 238 | `        elif isinstance(node, VariableDeclarationNode):` | Alternative runtime condition. |
| 239 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 240 | `            return self.eval_variable_declaration(node)` | Returns runtime value/result to caller. |
| 241 | `        # LINE: AssignmentNode updates a variable/list/member value.` | Comment/guideline in current code. |
| 242 | `        elif isinstance(node, AssignmentNode):` | Alternative runtime condition. |
| 243 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 244 | `            return self.eval_assignment(node)` | Returns runtime value/result to caller. |
| 245 | `        # LINE: BinaryOpNode evaluates operators like +, -, *, /, ==, &&.` | Comment/guideline in current code. |
| 246 | `        elif isinstance(node, BinaryOpNode):` | Alternative runtime condition. |
| 247 | `            # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 248 | `            value = self.eval_binary_op(node)` | Stores or updates runtime state/value. |
| 249 | `            # LINE: Guard against numbers larger than GAL's numeric limit.` | Comment/guideline in current code. |
| 250 | `            if isinstance(value, (int, float)):` | Checks a runtime condition. |
| 251 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 252 | `                if value > 1000000000000000 or value < -9999999999999999:` | Checks a runtime condition. |
| 253 | `                    # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 254 | `                    raise InterpreterError(f"Runtime Error: Evaluated number exceeds maximum number of 16 digits", node.line)` | Stops execution with a runtime error. |
| 255 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 256 | `            return value` | Returns runtime value/result to caller. |
| 257 | `        # LINE: FunctionDeclarationNode is saved, not executed immediately.` | Comment/guideline in current code. |
| 258 | `        elif isinstance(node, FunctionDeclarationNode):` | Alternative runtime condition. |
| 259 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 260 | `            return self.eval_function_declaration(node)` | Returns runtime value/result to caller. |
| 261 | `        # LINE: PrintNode executes plant().` | Comment/guideline in current code. |
| 262 | `        elif isinstance(node, PrintNode):` | Alternative runtime condition. |
| 263 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 264 | `            return self.eval_print(node)` | Returns runtime value/result to caller. |
| 265 | `        # LINE: ListNode builds an array/list value.` | Comment/guideline in current code. |
| 266 | `        elif isinstance(node, ListNode):` | Alternative runtime condition. |
| 267 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 268 | `            return self.eval_list(node)` | Returns runtime value/result to caller. |
| 269 | `        # LINE: ListAccessNode reads arr[index].` | Comment/guideline in current code. |
| 270 | `        elif isinstance(node, ListAccessNode):` | Alternative runtime condition. |
| 271 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 272 | `            return self.eval_list_access(node)` | Returns runtime value/result to caller. |
| 273 | `        # LINE: ReturnNode executes reclaim.` | Comment/guideline in current code. |
| 274 | `        elif isinstance(node, ReturnNode):` | Alternative runtime condition. |
| 275 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 276 | `            return self.eval_return(node)` | Returns runtime value/result to caller. |
| 277 | `        # LINE: FunctionCallNode executes root(), gcd(), or another function call.` | Comment/guideline in current code. |
| 278 | `        elif isinstance(node, FunctionCallNode):` | Alternative runtime condition. |
| 279 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 280 | `            return self.eval_function_call(node)` | Returns runtime value/result to caller. |
| 281 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 282 | `        elif isinstance(node, AppendNode):` | Alternative runtime condition. |
| 283 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 284 | `            return self.eval_append(node)` | Returns runtime value/result to caller. |
| 285 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 286 | `        elif isinstance(node, InsertNode):` | Alternative runtime condition. |
| 287 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 288 | `            return self.eval_insert(node)` | Returns runtime value/result to caller. |
| 289 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 290 | `        elif isinstance(node, RemoveNode):` | Alternative runtime condition. |
| 291 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 292 | `            return self.eval_remove(node)` | Returns runtime value/result to caller. |
| 293 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 294 | `        elif isinstance(node, UnaryOpNode):` | Alternative runtime condition. |
| 295 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 296 | `            return self.eval_unaryop(node)` | Returns runtime value/result to caller. |
| 297 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 298 | `        elif isinstance(node, FertileDeclarationNode):` | Alternative runtime condition. |
| 299 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 300 | `            return self.eval_sturdy_declaration(node)` | Returns runtime value/result to caller. |
| 301 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 302 | `        elif isinstance(node, CastNode):` | Alternative runtime condition. |
| 303 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 304 | `            return self.eval_cast(node)` | Returns runtime value/result to caller. |
| 305 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 306 | `        elif isinstance(node, SoilNode):` | Alternative runtime condition. |
| 307 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 308 | `            return self.eval_soil(node)` | Returns runtime value/result to caller. |
| 309 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 310 | `        elif isinstance(node, BloomNode):` | Alternative runtime condition. |
| 311 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 312 | `            return self.eval_bloom(node)` | Returns runtime value/result to caller. |
| 313 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 314 | `        elif isinstance(node, IfStatementNode):` | Alternative runtime condition. |
| 315 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 316 | `            return self.eval_if_statement(node)` | Returns runtime value/result to caller. |
| 317 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 318 | `        elif isinstance(node, ForLoopNode):` | Alternative runtime condition. |
| 319 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 320 | `            return self.eval_for_loop(node)` | Returns runtime value/result to caller. |
| 321 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 322 | `        elif isinstance(node, WhileLoopNode):` | Alternative runtime condition. |
| 323 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 324 | `            return self.eval_while_loop(node)` | Returns runtime value/result to caller. |
| 325 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 326 | `        elif isinstance(node, DoWhileLoopNode):` | Alternative runtime condition. |
| 327 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 328 | `            return self.eval_do_while_loop(node)` | Returns runtime value/result to caller. |
| 329 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 330 | `        elif isinstance(node, BreakNode):` | Alternative runtime condition. |
| 331 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 332 | `            return self.eval_break(node)` | Returns runtime value/result to caller. |
| 333 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 334 | `        elif isinstance(node, ContinueNode):` | Alternative runtime condition. |
| 335 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 336 | `            return self.eval_continue(node)` | Returns runtime value/result to caller. |
| 337 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 338 | `        elif isinstance(node, SwitchNode):` | Alternative runtime condition. |
| 339 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 340 | `            return self.eval_switch(node)` | Returns runtime value/result to caller. |
| 341 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 342 | `        elif node.node_type == "Input":` | Alternative runtime condition. |
| 343 | `            # LINE: Input node executes water().` | Comment/guideline in current code. |
| 344 | `            return self.eval_input(node)` | Returns runtime value/result to caller. |
| 345 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 346 | `        elif node.node_type == "Value":` | Alternative runtime condition. |
| 347 | `            # LINE: Value node converts a literal token into a Python value.` | Comment/guideline in current code. |
| 348 | `            value = self._parse_literal(node.value)` | Stores or updates runtime state/value. |
| 349 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 350 | `            return value` | Returns runtime value/result to caller. |
| 351 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 352 | `        elif node.node_type == "Identifier":` | Alternative runtime condition. |
| 353 | `            # LINE: Identifier reads the stored value of a variable.` | Comment/guideline in current code. |
| 354 | `            var_info = self.lookup_variable(node.value)` | Reads variable metadata/value from runtime scopes. |
| 355 | `            # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 356 | `            if isinstance(var_info, str):` | Checks a runtime condition. |
| 357 | `                # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 358 | `                raise InterpreterError(var_info, node.line)` | Stops execution with a runtime error. |
| 359 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 360 | `            return var_info["value"]` | Returns runtime value/result to caller. |
| 361 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 362 | `        elif node.node_type == "FormattedString":` | Alternative runtime condition. |
| 363 | `            # LINE: FormattedString removes quotes and decodes escapes.` | Comment/guideline in current code. |
| 364 | `            return self.eval_formatted_string(node)` | Returns runtime value/result to caller. |
| 365 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 366 | `        elif node.node_type == "VariableDeclarationList":` | Alternative runtime condition. |
| 367 | `            # LINE: Declare each variable inside a grouped declaration list.` | Comment/guideline in current code. |
| 368 | `            for child in node.children:` | Loops through AST children/items. |
| 369 | `                # AUTO: Calls `self.eval_variable_declaration`.` | Comment/guideline in current code. |
| 370 | `                self.eval_variable_declaration(child)` | Runtime support logic. |
| 371 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 372 | `        elif node.node_type == "AssignmentList":` | Alternative runtime condition. |
| 373 | `            # LINE: Execute each assignment/update inside a grouped assignment list.` | Comment/guideline in current code. |
| 374 | `            for child in node.children:` | Loops through AST children/items. |
| 375 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 376 | `                if isinstance(child, AssignmentNode):` | Checks a runtime condition. |
| 377 | `                    # AUTO: Calls `self.eval_assignment`.` | Comment/guideline in current code. |
| 378 | `                    self.eval_assignment(child)` | Runtime support logic. |
| 379 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 380 | `                elif isinstance(child, UnaryOpNode):` | Alternative runtime condition. |
| 381 | `                    # AUTO: Calls `self.eval_unaryop`.` | Comment/guideline in current code. |
| 382 | `                    self.eval_unaryop(child)` | Runtime support logic. |
| 383 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 384 | `        elif node.node_type == "List":` | Alternative runtime condition. |
| 385 | `            # LINE: Evaluate every list child and return a Python list.` | Comment/guideline in current code. |
| 386 | `            return [self.interpret(child) for child in node.children]` | Recursively executes/evaluates a child AST node. |
| 387 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 388 | `        elif node.node_type == "Block":` | Alternative runtime condition. |
| 389 | `            # LINE: Execute a block of statements in order.` | Comment/guideline in current code. |
| 390 | `            self.eval_block(node)` | Runtime support logic. |
| 391 | `        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 392 | `        else:` | Fallback runtime branch. |
| 393 | `            # LINE: Unknown AST node means builder/interpreter are out of sync.` | Comment/guideline in current code. |
| 394 | `            raise Exception(f"Unknown AST node type: {node.node_type}")` | Raises control-flow or runtime error exception. |
| 395 | `` | Blank spacing line. |
| 396 | `    # AUTO: Defines function `eval_program`.` | Comment/guideline in current code. |
| 397 | `    def eval_program(self, node):` | Starts a node-specific runtime evaluator. |
| 398 | `        # GUIDE: First register top-level declarations/functions, then call root().` | Comment/guideline in current code. |
| 399 | `        # LINE: Visit each top-level child under ProgramNode.` | Comment/guideline in current code. |
| 400 | `        for child in node.children:` | Loops through AST children/items. |
| 401 | `            # Top-level children are usually FunctionDeclarationNode, bundle` | Comment/guideline in current code. |
| 402 | `            # definitions, and global declarations. Function declarations are` | Comment/guideline in current code. |
| 403 | `            # stored, not executed yet.` | Comment/guideline in current code. |
| 404 | `            # LINE: This saves function declarations or executes global declarations.` | Comment/guideline in current code. |
| 405 | `            self.interpret(child)` | Recursively executes/evaluates a child AST node. |
| 406 | `` | Blank spacing line. |
| 407 | `        # After registration, create a fake function call node for root().` | Comment/guideline in current code. |
| 408 | `        # This is how the interpreter starts the user's main program.` | Comment/guideline in current code. |
| 409 | `        # LINE: Create a runtime call equivalent to root().` | Comment/guideline in current code. |
| 410 | `        main_call = FunctionCallNode("root", [], node.line)` | Creates the runtime call that starts root(). |
| 411 | `        # LINE: Dispatch that root() call through interpret() like any other call.` | Comment/guideline in current code. |
| 412 | `        return self.interpret(main_call)` | Returns runtime value/result to caller. |
| 413 | `` | Blank spacing line. |
| 414 | `` | Blank spacing line. |
| 415 | `    # AUTO: Defines function `eval_variable_declaration`.` | Comment/guideline in current code. |
| 416 | `    def eval_variable_declaration(self, node):` | Starts a node-specific runtime evaluator. |
| 417 | `        # GUIDE: Creates a runtime variable entry, using either an initializer value` | Comment/guideline in current code. |
| 418 | `        # or a default value based on the GAL data type.` | Comment/guideline in current code. |
| 419 | `        # LINE: First child stores the declared type, like seed/tree/vine.` | Comment/guideline in current code. |
| 420 | `        var_type = node.children[0].value` | Stores or updates runtime state/value. |
| 421 | `        # LINE: Second child stores the variable name.` | Comment/guideline in current code. |
| 422 | `        var_name = node.children[1].value` | Stores or updates runtime state/value. |
| 423 | `        # LINE: Third child is optional initializer, like = 10 or = water(seed).` | Comment/guideline in current code. |
| 424 | `        value_node = node.children[2] if len(node.children) > 2 else None` | Stores or updates runtime state/value. |
| 425 | `        # LINE: Starts false and becomes true for array/list initializers.` | Comment/guideline in current code. |
| 426 | `        is_list = False` | Stores or updates runtime state/value. |
| 427 | `        ` | Blank spacing line. |
| 428 | `        # LINE: Default runtime values when there is no initializer.` | Comment/guideline in current code. |
| 429 | `        default_values = {` | Stores or updates runtime state/value. |
| 430 | `            # If a variable has no initializer, these are the runtime defaults.` | Comment/guideline in current code. |
| 431 | `            # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 432 | `            "seed": 0,` | Runtime support logic. |
| 433 | `            # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 434 | `            "tree": 0.0,` | Runtime support logic. |
| 435 | `            # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 436 | `            "leaf": '',` | Runtime support logic. |
| 437 | `            # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 438 | `            "vine": "",` | Runtime support logic. |
| 439 | `            # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 440 | `            "branch": False,` | Runtime support logic. |
| 441 | `        # AUTO: Closes the current grouped code/data.` | Comment/guideline in current code. |
| 442 | `        }` | Closes Python grouping/list/dict/call. |
| 443 | `` | Blank spacing line. |
| 444 | `        # LINE: If initializer exists, evaluate it before declaring the variable.` | Comment/guideline in current code. |
| 445 | `        if value_node:` | Checks a runtime condition. |
| 446 | `            # There is an initializer, so evaluate the initializer AST node now.` | Comment/guideline in current code. |
| 447 | `            # LINE: List initializer means array/list value.` | Comment/guideline in current code. |
| 448 | `            if value_node.node_type == "List":` | Checks a runtime condition. |
| 449 | `                # Array/list initializer: evaluate each element and store a` | Comment/guideline in current code. |
| 450 | `                # Python list as the runtime value.` | Comment/guideline in current code. |
| 451 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 452 | `                if var_type in self.bundle_types:` | Checks a runtime condition. |
| 453 | `                    # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 454 | `                    value = [self._build_bundle_defaults(var_type) for _ in value_node.children]` | Stores or updates runtime state/value. |
| 455 | `                # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 456 | `                else:` | Fallback runtime branch. |
| 457 | `                    # AUTO: Defines function `materialize`.` | Comment/guideline in current code. |
| 458 | `                    def materialize(list_node):` | Runtime support logic. |
| 459 | `                        # LINE: Convert nested ListNode AST into Python list.` | Comment/guideline in current code. |
| 460 | `                        result = []` | Stores or updates runtime state/value. |
| 461 | `                        # AUTO: Starts a loop over these values.` | Comment/guideline in current code. |
| 462 | `                        for child in list_node.children:` | Loops through AST children/items. |
| 463 | `                            # LINE: Recursively handle nested array values.` | Comment/guideline in current code. |
| 464 | `                            if isinstance(child, ListNode):` | Checks a runtime condition. |
| 465 | `                                # AUTO: Appends a value to a list.` | Comment/guideline in current code. |
| 466 | `                                result.append(materialize(child))` | Runtime support logic. |
| 467 | `                            # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 468 | `                            else:` | Fallback runtime branch. |
| 469 | `                                # LINE: Evaluate normal element expression/literal.` | Comment/guideline in current code. |
| 470 | `                                item = self.interpret(child)` | Recursively executes/evaluates a child AST node. |
| 471 | `                                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 472 | `                                if var_type == "seed" and isinstance(item, float):` | Checks a runtime condition. |
| 473 | `                                    # AUTO: Sets `item`.` | Comment/guideline in current code. |
| 474 | `                                    item = int(item)` | Stores or updates runtime state/value. |
| 475 | `                                # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 476 | `                                elif var_type == "tree":` | Alternative runtime condition. |
| 477 | `                                    # AUTO: Sets `item`.` | Comment/guideline in current code. |
| 478 | `                                    item = float(item)` | Stores or updates runtime state/value. |
| 479 | `                                # AUTO: Appends a value to a list.` | Comment/guideline in current code. |
| 480 | `                                result.append(item)` | Runtime support logic. |
| 481 | `                        # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 482 | `                        return result` | Returns runtime value/result to caller. |
| 483 | `                    # LINE: Store the materialized Python list as the variable value.` | Comment/guideline in current code. |
| 484 | `                    value = materialize(value_node)` | Stores or updates runtime state/value. |
| 485 | `` | Blank spacing line. |
| 486 | `                # LINE: Mark this declaration as a list/array.` | Comment/guideline in current code. |
| 487 | `                is_list = True` | Stores or updates runtime state/value. |
| 488 | `` | Blank spacing line. |
| 489 | `            # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 490 | `            else:` | Fallback runtime branch. |
| 491 | `                # Normal initializer such as seed x = 10 or vine s = "hi".` | Comment/guideline in current code. |
| 492 | `                # LINE: Evaluate the initializer expression.` | Comment/guideline in current code. |
| 493 | `                value = self.interpret(value_node)` | Stores or updates runtime state/value. |
| 494 | `` | Blank spacing line. |
| 495 | `                # LINE: Convert tree-like float into seed integer if needed.` | Comment/guideline in current code. |
| 496 | `                if var_type == "seed" and isinstance(value, float):` | Checks a runtime condition. |
| 497 | `                    # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 498 | `                    value = int(value)` | Stores or updates runtime state/value. |
| 499 | `` | Blank spacing line. |
| 500 | `                # LINE: seed/tree only accept numeric values.` | Comment/guideline in current code. |
| 501 | `                if var_type in {"tree", "seed"}:` | Checks a runtime condition. |
| 502 | `                    # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 503 | `                    if not isinstance(value, (int, float)):` | Checks a runtime condition. |
| 504 | `                        # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 505 | `                        raise InterpreterError(f"Semantic Error: Type Mismatch! Invalid value for {var_name}", node.line)` | Stops execution with a runtime error. |
| 506 | `                    ` | Blank spacing line. |
| 507 | `                    # LINE: Prevent branch/boolean from being treated as a number.` | Comment/guideline in current code. |
| 508 | `                    if isinstance(value, bool):` | Checks a runtime condition. |
| 509 | `                        # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 510 | `                        raise InterpreterError(f"Semantic Error: Type Mismatch! Invalid value for {var_name}", node.line)` | Stops execution with a runtime error. |
| 511 | `` | Blank spacing line. |
| 512 | `` | Blank spacing line. |
| 513 | `                    # LINE: tree stores integer initializer as float.` | Comment/guideline in current code. |
| 514 | `                    if var_type == "tree" and isinstance(value, int):` | Checks a runtime condition. |
| 515 | `                        # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 516 | `                        value = float(value)` | Stores or updates runtime state/value. |
| 517 | `                ` | Blank spacing line. |
| 518 | `                # LINE: leaf must receive a string-like character value.` | Comment/guideline in current code. |
| 519 | `                if var_type == "leaf":` | Checks a runtime condition. |
| 520 | `                    # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 521 | `                    if not isinstance(value, str):` | Checks a runtime condition. |
| 522 | `                        # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 523 | `                        raise InterpreterError(f"Semantic Error: Type Mismatch! Invalid value for {var_name}", node.line)` | Stops execution with a runtime error. |
| 524 | `` | Blank spacing line. |
| 525 | `                # LINE: vine must receive a string value.` | Comment/guideline in current code. |
| 526 | `                if var_type == "vine":` | Checks a runtime condition. |
| 527 | `                    # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 528 | `                    if not isinstance(value, str):` | Checks a runtime condition. |
| 529 | `                        # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 530 | `                        raise InterpreterError(f"Semantic Error: Type Mismatch! Invalid value for {var_name}", node.line)` | Stops execution with a runtime error. |
| 531 | `` | Blank spacing line. |
| 532 | `                # LINE: branch can convert 0/1 numeric-style values into bool.` | Comment/guideline in current code. |
| 533 | `                if var_type == "branch":` | Checks a runtime condition. |
| 534 | `                    # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 535 | `                    if isinstance(value, int) or isinstance(value, float):` | Checks a runtime condition. |
| 536 | `                        # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 537 | `                        if value == 0:` | Checks a runtime condition. |
| 538 | `                            # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 539 | `                            value = False` | Stores or updates runtime state/value. |
| 540 | `                        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 541 | `                        else:` | Fallback runtime branch. |
| 542 | `                            # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 543 | `                            value = True` | Stores or updates runtime state/value. |
| 544 | `        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 545 | `        else:` | Fallback runtime branch. |
| 546 | `            # No initializer, so use a default value based on type.` | Comment/guideline in current code. |
| 547 | `            # LINE: Bundle variables get default member dictionaries.` | Comment/guideline in current code. |
| 548 | `            if var_type in self.bundle_types:` | Checks a runtime condition. |
| 549 | `                # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 550 | `                value = self._build_bundle_defaults(var_type)` | Stores or updates runtime state/value. |
| 551 | `            # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 552 | `            else:` | Fallback runtime branch. |
| 553 | `                # LINE: Built-in types get their default value from default_values.` | Comment/guideline in current code. |
| 554 | `                value = default_values.get(var_type, None)` | Stores or updates runtime state/value. |
| 555 | `        ` | Blank spacing line. |
| 556 | `        # LINE: Save the variable into the current runtime scope.            ` | Comment/guideline in current code. |
| 557 | `        self.declare_variable(var_name, var_type, value, is_list=is_list)` | Creates a variable in current runtime scope. |
| 558 | `` | Blank spacing line. |
| 559 | `    # AUTO: Defines function `eval_bundle_definition`.` | Comment/guideline in current code. |
| 560 | `    def eval_bundle_definition(self, node):` | Starts a node-specific runtime evaluator. |
| 561 | `        # LINE: Save bundle type name with its member definitions.` | Comment/guideline in current code. |
| 562 | `        self.bundle_types[node.bundle_name] = node.members` | Stores or updates runtime state/value. |
| 563 | `` | Blank spacing line. |
| 564 | `    # AUTO: Defines function `_build_bundle_defaults`.` | Comment/guideline in current code. |
| 565 | `    def _build_bundle_defaults(self, bundle_type_name):` | Runtime support logic. |
| 566 | `        # LINE: Default values for each built-in GAL member type.` | Comment/guideline in current code. |
| 567 | `        _member_defaults = {"seed": 0, "tree": 0.0, "leaf": '', "vine": "", "branch": False}` | Stores or updates runtime state/value. |
| 568 | `        # LINE: Get member list for this bundle type.` | Comment/guideline in current code. |
| 569 | `        members = self.bundle_types[bundle_type_name]` | Stores or updates runtime state/value. |
| 570 | `        # LINE: Build a dictionary value for the bundle instance.` | Comment/guideline in current code. |
| 571 | `        result = {}` | Stores or updates runtime state/value. |
| 572 | `        # LINE: Visit every member name/type in the bundle.` | Comment/guideline in current code. |
| 573 | `        for name, typ in members.items():` | Loops through AST children/items. |
| 574 | `            # LINE: Nested bundle member gets its own default dictionary.` | Comment/guideline in current code. |
| 575 | `            if typ in self.bundle_types:` | Checks a runtime condition. |
| 576 | `                # AUTO: Sets `result[name]`.` | Comment/guideline in current code. |
| 577 | `                result[name] = self._build_bundle_defaults(typ)` | Stores or updates runtime state/value. |
| 578 | `            # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 579 | `            else:` | Fallback runtime branch. |
| 580 | `                # LINE: Built-in member gets a simple default value.` | Comment/guideline in current code. |
| 581 | `                result[name] = _member_defaults.get(typ, None)` | Stores or updates runtime state/value. |
| 582 | `        # LINE: Return default bundle value.` | Comment/guideline in current code. |
| 583 | `        return result` | Returns runtime value/result to caller. |
| 584 | `` | Blank spacing line. |
| 585 | `    # AUTO: Defines function `eval_member_access`.` | Comment/guideline in current code. |
| 586 | `    def eval_member_access(self, node):` | Starts a node-specific runtime evaluator. |
| 587 | `        # LINE: First child is object/previous access; second child is member name.` | Comment/guideline in current code. |
| 588 | `        obj_child = node.children[0]` | Stores or updates runtime state/value. |
| 589 | `        # LINE: Store member name being read.` | Comment/guideline in current code. |
| 590 | `        member_name = node.children[1].value` | Stores or updates runtime state/value. |
| 591 | `` | Blank spacing line. |
| 592 | `        # LINE: Nested member access, like a.b.c.` | Comment/guideline in current code. |
| 593 | `        if obj_child.node_type == "MemberAccess":` | Checks a runtime condition. |
| 594 | `            # AUTO: Sets `bundle_value`.` | Comment/guideline in current code. |
| 595 | `            bundle_value = self.eval_member_access(obj_child)` | Stores or updates runtime state/value. |
| 596 | `        # LINE: Array member access, like students[i].age.` | Comment/guideline in current code. |
| 597 | `        elif obj_child.node_type == "ArrayMemberAccess":` | Alternative runtime condition. |
| 598 | `            # AUTO: Sets `bundle_value`.` | Comment/guideline in current code. |
| 599 | `            bundle_value = self.eval_array_member_access(obj_child)` | Stores or updates runtime state/value. |
| 600 | `        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 601 | `        else:` | Fallback runtime branch. |
| 602 | `            # LINE: Simple object name, like student.age.` | Comment/guideline in current code. |
| 603 | `            obj_name = obj_child.value` | Stores or updates runtime state/value. |
| 604 | `            # LINE: Look up the object variable.` | Comment/guideline in current code. |
| 605 | `            var_info = self.lookup_variable(obj_name)` | Reads variable metadata/value from runtime scopes. |
| 606 | `            # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 607 | `            if isinstance(var_info, str):` | Checks a runtime condition. |
| 608 | `                # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 609 | `                raise InterpreterError(var_info, node.line)` | Stops execution with a runtime error. |
| 610 | `            # LINE: Get the bundle dictionary value.` | Comment/guideline in current code. |
| 611 | `            bundle_value = var_info["value"]` | Stores or updates runtime state/value. |
| 612 | `` | Blank spacing line. |
| 613 | `        # LINE: Member access only works on bundle dictionaries.` | Comment/guideline in current code. |
| 614 | `        if not isinstance(bundle_value, dict):` | Checks a runtime condition. |
| 615 | `            # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 616 | `            raise InterpreterError(f"Runtime Error: Value is not a bundle.", node.line)` | Stops execution with a runtime error. |
| 617 | `        # LINE: Requested member must exist in the bundle.` | Comment/guideline in current code. |
| 618 | `        if member_name not in bundle_value:` | Checks a runtime condition. |
| 619 | `            # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 620 | `            raise InterpreterError(f"Runtime Error: Bundle has no member '{member_name}'.", node.line)` | Stops execution with a runtime error. |
| 621 | `        # LINE: Return the member's stored value.` | Comment/guideline in current code. |
| 622 | `        return bundle_value[member_name]` | Returns runtime value/result to caller. |
| 623 | `` | Blank spacing line. |
| 624 | `    # AUTO: Defines function `eval_array_member_access`.` | Comment/guideline in current code. |
| 625 | `    def eval_array_member_access(self, node):` | Starts a node-specific runtime evaluator. |
| 626 | `        # LINE: First child is array access part, like students[i].` | Comment/guideline in current code. |
| 627 | `        list_access_node = node.children[0]` | Stores or updates runtime state/value. |
| 628 | `        # LINE: Second child is member name, like age.` | Comment/guideline in current code. |
| 629 | `        member_name = node.children[1].value` | Stores or updates runtime state/value. |
| 630 | `        # LINE: Evaluate students[i] first.` | Comment/guideline in current code. |
| 631 | `        bundle_element = self.eval_list_access(list_access_node)` | Stores or updates runtime state/value. |
| 632 | `        # LINE: Array element must be a bundle dictionary.` | Comment/guideline in current code. |
| 633 | `        if not isinstance(bundle_element, dict):` | Checks a runtime condition. |
| 634 | `            # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 635 | `            raise InterpreterError(f"Runtime Error: Array element is not a bundle.", node.line)` | Stops execution with a runtime error. |
| 636 | `        # LINE: Requested bundle member must exist.` | Comment/guideline in current code. |
| 637 | `        if member_name not in bundle_element:` | Checks a runtime condition. |
| 638 | `            # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 639 | `            raise InterpreterError(f"Runtime Error: Bundle has no member '{member_name}'.", node.line)` | Stops execution with a runtime error. |
| 640 | `        # LINE: Return students[i].member value.` | Comment/guideline in current code. |
| 641 | `        return bundle_element[member_name]` | Returns runtime value/result to caller. |
| 642 | `` | Blank spacing line. |
| 643 | `    # AUTO: Defines function `eval_sturdy_declaration`.` | Comment/guideline in current code. |
| 644 | `    def eval_sturdy_declaration(self, node):` | Starts a node-specific runtime evaluator. |
| 645 | `        # LINE: First child is fertile variable type.` | Comment/guideline in current code. |
| 646 | `        var_type = node.children[0].value` | Stores or updates runtime state/value. |
| 647 | `        # LINE: Second child is fertile variable name.` | Comment/guideline in current code. |
| 648 | `        var_name = node.children[1].value` | Stores or updates runtime state/value. |
| 649 | `        # LINE: Third child is required initializer.` | Comment/guideline in current code. |
| 650 | `        value_node = node.children[2]` | Stores or updates runtime state/value. |
| 651 | `        # LINE: Evaluate initializer.` | Comment/guideline in current code. |
| 652 | `        value = self.interpret(value_node)` | Stores or updates runtime state/value. |
| 653 | `        # LINE: Declare variable with is_fertile=True so reassignment is blocked.` | Comment/guideline in current code. |
| 654 | `        self.declare_variable(var_name, var_type, value, is_list=False,  is_fertile=True)` | Creates a variable in current runtime scope. |
| 655 | `` | Blank spacing line. |
| 656 | `` | Blank spacing line. |
| 657 | `    # AUTO: Defines function `eval_assignment`.` | Comment/guideline in current code. |
| 658 | `    def eval_assignment(self, node):` | Starts a node-specific runtime evaluator. |
| 659 | `        # GUIDE: Assignments evaluate RHS first, then write into a variable,` | Comment/guideline in current code. |
| 660 | `        # array element, or bundle member target.` | Comment/guideline in current code. |
| 661 | `        # LINE: Left child is the assignment target.` | Comment/guideline in current code. |
| 662 | `        target_node = node.children[0]` | Stores or updates runtime state/value. |
| 663 | `        # LINE: Right child is the value/expression being assigned.` | Comment/guideline in current code. |
| 664 | `        value_node = node.children[1]` | Stores or updates runtime state/value. |
| 665 | `` | Blank spacing line. |
| 666 | `        # LINE: RHS list means assign an array/list value.` | Comment/guideline in current code. |
| 667 | `        if value_node.node_type == "List":` | Checks a runtime condition. |
| 668 | `            # RHS is an array/list value.` | Comment/guideline in current code. |
| 669 | `            # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 670 | `            value = []` | Stores or updates runtime state/value. |
| 671 | `            # AUTO: Starts a loop over these values.` | Comment/guideline in current code. |
| 672 | `            for val in value_node.children:` | Loops through AST children/items. |
| 673 | `                # LINE: Evaluate each list item before storing.` | Comment/guideline in current code. |
| 674 | `                item = self.interpret(val)` | Stores or updates runtime state/value. |
| 675 | `                # AUTO: Appends a value to a list.` | Comment/guideline in current code. |
| 676 | `                value.append(item)` | Runtime support logic. |
| 677 | `        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 678 | `        else:` | Fallback runtime branch. |
| 679 | `            # RHS is an expression, literal, function call, water(), etc.` | Comment/guideline in current code. |
| 680 | `            # LINE: Evaluate the right side first, such as a + b or water(seed).` | Comment/guideline in current code. |
| 681 | `            value = self.interpret(value_node)` | Stores or updates runtime state/value. |
| 682 | `            # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 683 | `            if isinstance(value_node, AppendNode) or isinstance(value_node, InsertNode) or isinstance(value_node, RemoveNode):` | Checks a runtime condition. |
| 684 | `                # LINE: append/insert/remove already changed the list themselves.` | Comment/guideline in current code. |
| 685 | `                return` | Runtime support logic. |
| 686 | `` | Blank spacing line. |
| 687 | `        # LINE: If target is arr[index], write into a list element.` | Comment/guideline in current code. |
| 688 | `        if target_node.node_type == "ListAccess":` | Checks a runtime condition. |
| 689 | `            # Assignment into an array/list element, e.g. arr[i] = value.` | Comment/guideline in current code. |
| 690 | `            # LINE: Collect indexes for arr[i] or nested arr[i][j].` | Comment/guideline in current code. |
| 691 | `            indices = []` | Stores or updates runtime state/value. |
| 692 | `            # LINE: Start from the ListAccess target node.` | Comment/guideline in current code. |
| 693 | `            current = target_node` | Stores or updates runtime state/value. |
| 694 | `            # LINE: Walk nested ListAccess nodes from outside to inside.` | Comment/guideline in current code. |
| 695 | `            while hasattr(current, 'node_type') and current.node_type == "ListAccess":` | Repeats while runtime condition is true. |
| 696 | `                # LINE: Evaluate the index expression inside brackets.` | Comment/guideline in current code. |
| 697 | `                idx = self.interpret(current.children[1].children[0])` | Stores or updates runtime state/value. |
| 698 | `                # LINE: Index must be an integer.` | Comment/guideline in current code. |
| 699 | `                if not isinstance(idx, int):` | Checks a runtime condition. |
| 700 | `                    # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 701 | `                    raise InterpreterError(f"Runtime Error: List index must be an integer. Got '{idx}'", node.line)` | Stops execution with a runtime error. |
| 702 | `                # LINE: Store the index for later navigation.` | Comment/guideline in current code. |
| 703 | `                indices.append(idx)` | Runtime support logic. |
| 704 | `                # LINE: Move toward the base list name.` | Comment/guideline in current code. |
| 705 | `                current = current.children[0].value` | Stores or updates runtime state/value. |
| 706 | `` | Blank spacing line. |
| 707 | `            # LINE: current now holds the base list variable name.` | Comment/guideline in current code. |
| 708 | `            list_name = current` | Stores or updates runtime state/value. |
| 709 | `            # LINE: Look up the list variable.` | Comment/guideline in current code. |
| 710 | `            list_entry = self.lookup_variable(list_name)` | Reads variable metadata/value from runtime scopes. |
| 711 | `            # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 712 | `            if isinstance(list_entry, str):` | Checks a runtime condition. |
| 713 | `                # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 714 | `                raise InterpreterError(list_entry, node.line)` | Stops execution with a runtime error. |
| 715 | `` | Blank spacing line. |
| 716 | `            # LINE: Get the actual list/string value.` | Comment/guideline in current code. |
| 717 | `            list_value = list_entry["value"]` | Stores or updates runtime state/value. |
| 718 | `            # LINE: Target must be a list or string.` | Comment/guideline in current code. |
| 719 | `            if not isinstance(list_value, (list, str)):` | Checks a runtime condition. |
| 720 | `                # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 721 | `                raise InterpreterError(f"Runtime Error: Variable '{list_name}' is not a list.", node.line)` | Stops execution with a runtime error. |
| 722 | `` | Blank spacing line. |
| 723 | `            # LINE: String index assignment path.` | Comment/guideline in current code. |
| 724 | `            if isinstance(list_value, str):` | Checks a runtime condition. |
| 725 | `                # LINE: Strings only support one-dimensional indexing.` | Comment/guideline in current code. |
| 726 | `                if len(indices) != 1:` | Checks a runtime condition. |
| 727 | `                    # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 728 | `                    raise InterpreterError(f"Runtime Error: Multi-dimensional indexing not supported for strings.", node.line)` | Stops execution with a runtime error. |
| 729 | `                # LINE: Final string index.` | Comment/guideline in current code. |
| 730 | `                final_idx = indices[0]` | Stores or updates runtime state/value. |
| 731 | `                # LINE: Check string index bounds.` | Comment/guideline in current code. |
| 732 | `                if final_idx < 0 or final_idx >= len(list_value):` | Checks a runtime condition. |
| 733 | `                    # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 734 | `                    raise InterpreterError(f"Runtime Error: Index '{final_idx}' out of bounds for '{list_name}'.", node.line)` | Stops execution with a runtime error. |
| 735 | `                # LINE: String index assignment must receive one character.` | Comment/guideline in current code. |
| 736 | `                if not isinstance(value, str) or len(value) != 1:` | Checks a runtime condition. |
| 737 | `                    # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 738 | `                    raise InterpreterError(f"Runtime Error: Can only assign a single character to a string index.", node.line)` | Stops execution with a runtime error. |
| 739 | `                # LINE: Create updated string with one character replaced.` | Comment/guideline in current code. |
| 740 | `                list_value = list_value[:final_idx] + value + list_value[final_idx + 1:]` | Stores or updates runtime state/value. |
| 741 | `                # LINE: Save updated string back into variable entry.` | Comment/guideline in current code. |
| 742 | `                list_entry["value"] = list_value` | Stores or updates runtime state/value. |
| 743 | `            # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 744 | `            else:` | Fallback runtime branch. |
| 745 | `                # LINE: Reverse indexes so traversal starts from base list.` | Comment/guideline in current code. |
| 746 | `                indices.reverse()` | Runtime support logic. |
| 747 | `` | Blank spacing line. |
| 748 | `                # LINE: Start navigating from the base list value.` | Comment/guideline in current code. |
| 749 | `                target = list_value` | Stores or updates runtime state/value. |
| 750 | `                # LINE: Walk all indexes except the final assignment index.` | Comment/guideline in current code. |
| 751 | `                for i, idx in enumerate(indices[:-1]):` | Loops through AST children/items. |
| 752 | `                    # LINE: Check each intermediate index is within bounds.` | Comment/guideline in current code. |
| 753 | `                    if idx < 0 or idx >= len(target):` | Checks a runtime condition. |
| 754 | `                        # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 755 | `                        raise InterpreterError(f"Runtime Error: Index '{idx}' out of bounds for list '{list_name}'.", node.line)` | Stops execution with a runtime error. |
| 756 | `                    # LINE: Move into the nested list.` | Comment/guideline in current code. |
| 757 | `                    target = target[idx]` | Stores or updates runtime state/value. |
| 758 | `                    # LINE: Intermediate target must still be a list.` | Comment/guideline in current code. |
| 759 | `                    if not isinstance(target, list):` | Checks a runtime condition. |
| 760 | `                        # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 761 | `                        raise InterpreterError(f"Runtime Error: Cannot index into a non-list value.", node.line)` | Stops execution with a runtime error. |
| 762 | `` | Blank spacing line. |
| 763 | `                # LINE: Last index is where assignment happens.` | Comment/guideline in current code. |
| 764 | `                final_idx = indices[-1]` | Stores or updates runtime state/value. |
| 765 | `                # LINE: Check final index bounds.` | Comment/guideline in current code. |
| 766 | `                if final_idx < 0 or final_idx >= len(target):` | Checks a runtime condition. |
| 767 | `                    # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 768 | `                    raise InterpreterError(f"Runtime Error: Index '{final_idx}' out of bounds for list '{list_name}'.", node.line)` | Stops execution with a runtime error. |
| 769 | `` | Blank spacing line. |
| 770 | `                # LINE: Store RHS value into final list element.` | Comment/guideline in current code. |
| 771 | `                target[final_idx] = value` | Stores or updates runtime state/value. |
| 772 | `` | Blank spacing line. |
| 773 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 774 | `        elif target_node.node_type == "MemberAccess":` | Alternative runtime condition. |
| 775 | `            # Assignment into a bundle member, e.g. student.age = 20.` | Comment/guideline in current code. |
| 776 | `            # LINE: chain stores member path names, like ["info", "age"].` | Comment/guideline in current code. |
| 777 | `            chain = []` | Stores or updates runtime state/value. |
| 778 | `            # LINE: Start from full member access target.` | Comment/guideline in current code. |
| 779 | `            current = target_node` | Stores or updates runtime state/value. |
| 780 | `            # LINE: Walk member access nodes until reaching base object.` | Comment/guideline in current code. |
| 781 | `            while hasattr(current, 'node_type') and current.node_type == "MemberAccess":` | Repeats while runtime condition is true. |
| 782 | `                # LINE: Save current member name.` | Comment/guideline in current code. |
| 783 | `                chain.append(current.children[1].value)` | Runtime support logic. |
| 784 | `                # LINE: Move left toward the base object.` | Comment/guideline in current code. |
| 785 | `                current = current.children[0]` | Stores or updates runtime state/value. |
| 786 | `` | Blank spacing line. |
| 787 | `            # LINE: Reverse to access members from base object outward.` | Comment/guideline in current code. |
| 788 | `            chain.reverse()` | Runtime support logic. |
| 789 | `` | Blank spacing line. |
| 790 | `            # LINE: Base object might be array member access.` | Comment/guideline in current code. |
| 791 | `            if hasattr(current, 'node_type') and current.node_type == "ArrayMemberAccess":` | Checks a runtime condition. |
| 792 | `                # AUTO: Sets `bundle_value`.` | Comment/guideline in current code. |
| 793 | `                bundle_value = self.interpret(current)` | Stores or updates runtime state/value. |
| 794 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 795 | `                if not isinstance(bundle_value, dict):` | Checks a runtime condition. |
| 796 | `                    # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 797 | `                    raise InterpreterError(f"Runtime Error: Value is not a bundle.", node.line)` | Stops execution with a runtime error. |
| 798 | `            # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 799 | `            else:` | Fallback runtime branch. |
| 800 | `                # LINE: Base object is a normal variable.` | Comment/guideline in current code. |
| 801 | `                obj_name = current.value` | Stores or updates runtime state/value. |
| 802 | `                # LINE: Look up bundle variable.` | Comment/guideline in current code. |
| 803 | `                var_info = self.lookup_variable(obj_name)` | Reads variable metadata/value from runtime scopes. |
| 804 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 805 | `                if isinstance(var_info, str):` | Checks a runtime condition. |
| 806 | `                    # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 807 | `                    raise InterpreterError(var_info, node.line)` | Stops execution with a runtime error. |
| 808 | `                # LINE: Get bundle dictionary from variable.` | Comment/guideline in current code. |
| 809 | `                bundle_value = var_info["value"]` | Stores or updates runtime state/value. |
| 810 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 811 | `                if not isinstance(bundle_value, dict):` | Checks a runtime condition. |
| 812 | `                    # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 813 | `                    raise InterpreterError(f"Runtime Error: Variable '{obj_name}' is not a bundle.", node.line)` | Stops execution with a runtime error. |
| 814 | `` | Blank spacing line. |
| 815 | `            # LINE: Navigate through nested bundle members before the final member.` | Comment/guideline in current code. |
| 816 | `            for member in chain[:-1]:` | Loops through AST children/items. |
| 817 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 818 | `                if member not in bundle_value:` | Checks a runtime condition. |
| 819 | `                    # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 820 | `                    raise InterpreterError(f"Runtime Error: Bundle has no member '{member}'.", node.line)` | Stops execution with a runtime error. |
| 821 | `                # AUTO: Sets `bundle_value`.` | Comment/guideline in current code. |
| 822 | `                bundle_value = bundle_value[member]` | Stores or updates runtime state/value. |
| 823 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 824 | `                if not isinstance(bundle_value, dict):` | Checks a runtime condition. |
| 825 | `                    # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 826 | `                    raise InterpreterError(f"Runtime Error: Member '{member}' is not a bundle.", node.line)` | Stops execution with a runtime error. |
| 827 | `` | Blank spacing line. |
| 828 | `            # LINE: Final member is the field being assigned.` | Comment/guideline in current code. |
| 829 | `            final_member = chain[-1]` | Stores or updates runtime state/value. |
| 830 | `            # LINE: Final member must exist.` | Comment/guideline in current code. |
| 831 | `            if final_member not in bundle_value:` | Checks a runtime condition. |
| 832 | `                # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 833 | `                raise InterpreterError(f"Runtime Error: Bundle has no member '{final_member}'.", node.line)` | Stops execution with a runtime error. |
| 834 | `` | Blank spacing line. |
| 835 | `            # LINE: Find the declared type chain for the final member.` | Comment/guideline in current code. |
| 836 | `            type_chain_current = current` | Stores or updates runtime state/value. |
| 837 | `            # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 838 | `            if hasattr(type_chain_current, 'node_type') and type_chain_current.node_type == "ArrayMemberAccess":` | Checks a runtime condition. |
| 839 | `                # LINE: Get base array name from array member access.` | Comment/guideline in current code. |
| 840 | `                la_node = type_chain_current.children[0]` | Stores or updates runtime state/value. |
| 841 | `                # AUTO: Repeats while this condition is true.` | Comment/guideline in current code. |
| 842 | `                while hasattr(la_node, 'node_type') and la_node.node_type == "ListAccess":` | Repeats while runtime condition is true. |
| 843 | `                    # AUTO: Sets `la_node`.` | Comment/guideline in current code. |
| 844 | `                    la_node = la_node.children[0].value` | Stores or updates runtime state/value. |
| 845 | `                # LINE: Read bundle type from base array variable.` | Comment/guideline in current code. |
| 846 | `                var_type = self.lookup_variable(la_node)["type"] if not isinstance(self.lookup_variable(la_node), str) else None  # type: ignore` | Reads variable metadata/value from runtime scopes. |
| 847 | `            # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 848 | `            else:` | Fallback runtime branch. |
| 849 | `                # LINE: Base object type comes from the variable entry.` | Comment/guideline in current code. |
| 850 | `                obj_name = type_chain_current.value` | Stores or updates runtime state/value. |
| 851 | `                # AUTO: Sets `var_info`.` | Comment/guideline in current code. |
| 852 | `                var_info = self.lookup_variable(obj_name)` | Reads variable metadata/value from runtime scopes. |
| 853 | `                # AUTO: Sets `var_type`.` | Comment/guideline in current code. |
| 854 | `                var_type = var_info["type"] if not isinstance(var_info, str) else None` | Stores or updates runtime state/value. |
| 855 | `` | Blank spacing line. |
| 856 | `            # LINE: Convert assigned value to match member type when needed.` | Comment/guideline in current code. |
| 857 | `            if var_type and var_type in self.bundle_types:` | Checks a runtime condition. |
| 858 | `                # AUTO: Sets `cur_type`.` | Comment/guideline in current code. |
| 859 | `                cur_type = var_type` | Stores or updates runtime state/value. |
| 860 | `                # AUTO: Starts a loop over these values.` | Comment/guideline in current code. |
| 861 | `                for member in chain:` | Loops through AST children/items. |
| 862 | `                    # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 863 | `                    if cur_type in self.bundle_types:` | Checks a runtime condition. |
| 864 | `                        # AUTO: Sets `cur_type`.` | Comment/guideline in current code. |
| 865 | `                        cur_type = self.bundle_types[cur_type].get(member, cur_type)` | Stores or updates runtime state/value. |
| 866 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 867 | `                if cur_type == "seed" and isinstance(value, float):` | Checks a runtime condition. |
| 868 | `                    # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 869 | `                    value = int(value)` | Stores or updates runtime state/value. |
| 870 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 871 | `                elif cur_type == "tree" and isinstance(value, int):` | Alternative runtime condition. |
| 872 | `                    # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 873 | `                    value = float(value)` | Stores or updates runtime state/value. |
| 874 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 875 | `                elif cur_type == "branch" and isinstance(value, int):` | Alternative runtime condition. |
| 876 | `                    # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 877 | `                    value = True if value != 0 else False` | Stores or updates runtime state/value. |
| 878 | `` | Blank spacing line. |
| 879 | `            # LINE: Store value into the bundle member.` | Comment/guideline in current code. |
| 880 | `            bundle_value[final_member] = value` | Stores or updates runtime state/value. |
| 881 | `` | Blank spacing line. |
| 882 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 883 | `        elif target_node.node_type == "ArrayMemberAccess":` | Alternative runtime condition. |
| 884 | `            # Assignment into a bundle member inside an array element,` | Comment/guideline in current code. |
| 885 | `            # e.g. students[i].age = 20.` | Comment/guideline in current code. |
| 886 | `            # LINE: First child is list element access.` | Comment/guideline in current code. |
| 887 | `            list_access_node = target_node.children[0]` | Stores or updates runtime state/value. |
| 888 | `            # LINE: Second child is member name.` | Comment/guideline in current code. |
| 889 | `            member_name = target_node.children[1].value` | Stores or updates runtime state/value. |
| 890 | `            # LINE: Evaluate the array element first.` | Comment/guideline in current code. |
| 891 | `            bundle_element = self.eval_list_access(list_access_node)` | Stores or updates runtime state/value. |
| 892 | `            # LINE: Array element must be a bundle dictionary.` | Comment/guideline in current code. |
| 893 | `            if not isinstance(bundle_element, dict):` | Checks a runtime condition. |
| 894 | `                # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 895 | `                raise InterpreterError(f"Runtime Error: Array element is not a bundle.", node.line)` | Stops execution with a runtime error. |
| 896 | `            # LINE: Requested member must exist.` | Comment/guideline in current code. |
| 897 | `            if member_name not in bundle_element:` | Checks a runtime condition. |
| 898 | `                # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 899 | `                raise InterpreterError(f"Runtime Error: Bundle has no member '{member_name}'.", node.line)` | Stops execution with a runtime error. |
| 900 | `` | Blank spacing line. |
| 901 | `            # LINE: Find the base array variable name.` | Comment/guideline in current code. |
| 902 | `            current = list_access_node` | Stores or updates runtime state/value. |
| 903 | `            # AUTO: Repeats while this condition is true.` | Comment/guideline in current code. |
| 904 | `            while hasattr(current, 'node_type') and current.node_type == "ListAccess":` | Repeats while runtime condition is true. |
| 905 | `                # AUTO: Sets `current`.` | Comment/guideline in current code. |
| 906 | `                current = current.children[0].value` | Stores or updates runtime state/value. |
| 907 | `            # LINE: current now stores the base variable name.` | Comment/guideline in current code. |
| 908 | `            var_name = current` | Stores or updates runtime state/value. |
| 909 | `            # LINE: Look up base array variable.` | Comment/guideline in current code. |
| 910 | `            var_info = self.lookup_variable(var_name)` | Reads variable metadata/value from runtime scopes. |
| 911 | `            # LINE: Convert value to member type if the base array is a bundle type.` | Comment/guideline in current code. |
| 912 | `            if not isinstance(var_info, str) and var_info["type"] in self.bundle_types:` | Checks a runtime condition. |
| 913 | `                # AUTO: Sets `member_type`.` | Comment/guideline in current code. |
| 914 | `                member_type = self.bundle_types[var_info["type"]].get(member_name)` | Stores or updates runtime state/value. |
| 915 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 916 | `                if member_type == "seed" and isinstance(value, float):` | Checks a runtime condition. |
| 917 | `                    # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 918 | `                    value = int(value)` | Stores or updates runtime state/value. |
| 919 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 920 | `                elif member_type == "tree" and isinstance(value, int):` | Alternative runtime condition. |
| 921 | `                    # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 922 | `                    value = float(value)` | Stores or updates runtime state/value. |
| 923 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 924 | `                elif member_type == "branch" and isinstance(value, int):` | Alternative runtime condition. |
| 925 | `                    # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 926 | `                    value = True if value != 0 else False` | Stores or updates runtime state/value. |
| 927 | `` | Blank spacing line. |
| 928 | `            # LINE: Store value into the array element's member.` | Comment/guideline in current code. |
| 929 | `            bundle_element[member_name] = value` | Stores or updates runtime state/value. |
| 930 | `` | Blank spacing line. |
| 931 | `        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 932 | `        else:` | Fallback runtime branch. |
| 933 | `            # Simple variable assignment, e.g. total = x + y.` | Comment/guideline in current code. |
| 934 | `            # LINE: Target node value is the variable name.` | Comment/guideline in current code. |
| 935 | `            var_name = target_node.value` | Stores or updates runtime state/value. |
| 936 | `            # LINE: Look up variable metadata and current value.` | Comment/guideline in current code. |
| 937 | `            var_info = self.lookup_variable(var_name)` | Reads variable metadata/value from runtime scopes. |
| 938 | `            # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 939 | `            if isinstance(var_info, str):` | Checks a runtime condition. |
| 940 | `                # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 941 | `                raise InterpreterError(var_info, node.line)` | Stops execution with a runtime error. |
| 942 | `` | Blank spacing line. |
| 943 | `            # LINE: Read declared type for conversion.` | Comment/guideline in current code. |
| 944 | `            var_type = var_info["type"]` | Stores or updates runtime state/value. |
| 945 | `            # LINE: Assigning float to seed truncates to int.` | Comment/guideline in current code. |
| 946 | `            if var_type == "seed" and isinstance(value, float):` | Checks a runtime condition. |
| 947 | `                # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 948 | `                value = int(value)` | Stores or updates runtime state/value. |
| 949 | `            ` | Blank spacing line. |
| 950 | `            # LINE: Assigning int to tree converts to float.` | Comment/guideline in current code. |
| 951 | `            if var_type == "tree" and isinstance(value, int):` | Checks a runtime condition. |
| 952 | `                # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 953 | `                value = float(value)` | Stores or updates runtime state/value. |
| 954 | `` | Blank spacing line. |
| 955 | `            # LINE: Assigning int to branch converts 0 to False and nonzero to True.` | Comment/guideline in current code. |
| 956 | `            if var_type == "branch" and isinstance(value, int):` | Checks a runtime condition. |
| 957 | `                # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 958 | `                value = True if value != 0 else False` | Stores or updates runtime state/value. |
| 959 | `` | Blank spacing line. |
| 960 | `            # LINE: Save converted value into the variable.` | Comment/guideline in current code. |
| 961 | `            self.set_variable(var_name, value)` | Writes a new value to an existing variable. |
| 962 | `` | Blank spacing line. |
| 963 | `        # LINE: Return assigned value so assignment expression can be reused.` | Comment/guideline in current code. |
| 964 | `        return value` | Returns runtime value/result to caller. |
| 965 | `` | Blank spacing line. |
| 966 | `` | Blank spacing line. |
| 967 | `    # AUTO: Defines function `eval_binary_op`.` | Comment/guideline in current code. |
| 968 | `    def eval_binary_op(self, node):` | Starts a node-specific runtime evaluator. |
| 969 | `        # GUIDE: Binary operations evaluate left/right child expressions before` | Comment/guideline in current code. |
| 970 | `        # applying arithmetic, comparison, logical, or concat behavior.` | Comment/guideline in current code. |
| 971 | `        # Example AST for x + y:` | Comment/guideline in current code. |
| 972 | `        # left child = Identifier(x), right child = Identifier(y), value = "+"` | Comment/guideline in current code. |
| 973 | `        # LINE: Evaluate the left operand first.` | Comment/guideline in current code. |
| 974 | `        left = self.interpret(node.children[0])` | Stores or updates runtime state/value. |
| 975 | `        # LINE: Evaluate the right operand second.` | Comment/guideline in current code. |
| 976 | `        right = self.interpret(node.children[1])` | Stores or updates runtime state/value. |
| 977 | `        # LINE: node.value stores the actual operator symbol.` | Comment/guideline in current code. |
| 978 | `        operator = node.value` | Stores or updates runtime state/value. |
| 979 | `` | Blank spacing line. |
| 980 | `        # LINE: Backtick is GAL string concatenation.` | Comment/guideline in current code. |
| 981 | `        if operator == '`':` | Checks a runtime condition. |
| 982 | `            # GAL string concat operator.` | Comment/guideline in current code. |
| 983 | `            # AUTO: Sets `result`.` | Comment/guideline in current code. |
| 984 | `            result = str(left) + str(right)` | Stores or updates runtime state/value. |
| 985 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 986 | `            return result` | Returns runtime value/result to caller. |
| 987 | `` | Blank spacing line. |
| 988 | `        # Convert token/literal strings like "10", "~5", "sunshine" into Python` | Comment/guideline in current code. |
| 989 | `        # values like 10, -5, True before applying the operator.` | Comment/guideline in current code. |
| 990 | `        # LINE: Convert left literal text into Python int/float/bool/string if needed.` | Comment/guideline in current code. |
| 991 | `        left = self._parse_literal(left)` | Stores or updates runtime state/value. |
| 992 | `        # LINE: Convert right literal text into Python int/float/bool/string if needed.` | Comment/guideline in current code. |
| 993 | `        right = self._parse_literal(right)` | Stores or updates runtime state/value. |
| 994 | `` | Blank spacing line. |
| 995 | `        # LINE: Plus with any string becomes concatenation.` | Comment/guideline in current code. |
| 996 | `        if operator == '+' and (isinstance(left, str) or isinstance(right, str)):` | Checks a runtime condition. |
| 997 | `            # AUTO: Sets `result`.` | Comment/guideline in current code. |
| 998 | `            result = str(left) + str(right)` | Stores or updates runtime state/value. |
| 999 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1000 | `            return result` | Returns runtime value/result to caller. |
| 1001 | `` | Blank spacing line. |
| 1002 | `        # AUTO: Starts protected code that can catch errors.` | Comment/guideline in current code. |
| 1003 | `        try:` | Starts protected block for optional runtime dependency or error handling. |
| 1004 | `            # LINE: Choose operation based on the operator stored in the AST node.` | Comment/guideline in current code. |
| 1005 | `            if operator == '+':` | Checks a runtime condition. |
| 1006 | `                # Numeric addition. If both operands are non-numeric, convert` | Comment/guideline in current code. |
| 1007 | `                # truthy/empty values into numbers first.` | Comment/guideline in current code. |
| 1008 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1009 | `                if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):` | Checks a runtime condition. |
| 1010 | `                    # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1011 | `                    if isinstance(left, bool):` | Checks a runtime condition. |
| 1012 | `                        # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1013 | `                        left = 1 if left == True else 0` | Stores or updates runtime state/value. |
| 1014 | `                    # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1015 | `                    elif isinstance(left, str):` | Alternative runtime condition. |
| 1016 | `                        # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1017 | `                        left = 1 if left != "" else 0` | Stores or updates runtime state/value. |
| 1018 | `                    # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1019 | `                    if isinstance(right, bool):` | Checks a runtime condition. |
| 1020 | `                        # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1021 | `                        right = 1 if right == True else 0` | Stores or updates runtime state/value. |
| 1022 | `                    # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1023 | `                    elif isinstance(right, str):` | Alternative runtime condition. |
| 1024 | `                        # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1025 | `                        right = 1 if right != "" else 0` | Stores or updates runtime state/value. |
| 1026 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1027 | `                return left + right  # type: ignore[operator]` | Returns runtime value/result to caller. |
| 1028 | `            ` | Blank spacing line. |
| 1029 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1030 | `            elif operator == '-':` | Alternative runtime condition. |
| 1031 | `                # LINE: Subtraction path.` | Comment/guideline in current code. |
| 1032 | `                if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):` | Checks a runtime condition. |
| 1033 | `                    # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1034 | `                    if isinstance(left, bool):` | Checks a runtime condition. |
| 1035 | `                        # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1036 | `                        left = 1 if left == True else 0` | Stores or updates runtime state/value. |
| 1037 | `                    # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1038 | `                    elif isinstance(left, str):` | Alternative runtime condition. |
| 1039 | `                        # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1040 | `                        left = 1 if left != "" else 0` | Stores or updates runtime state/value. |
| 1041 | `                    # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1042 | `                    if isinstance(right, bool):` | Checks a runtime condition. |
| 1043 | `                        # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1044 | `                        right = 1 if right == True else 0` | Stores or updates runtime state/value. |
| 1045 | `                    # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1046 | `                    elif isinstance(right, str):` | Alternative runtime condition. |
| 1047 | `                        # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1048 | `                        right = 1 if right != "" else 0` | Stores or updates runtime state/value. |
| 1049 | `` | Blank spacing line. |
| 1050 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1051 | `                return left - right  # type: ignore[operator]` | Returns runtime value/result to caller. |
| 1052 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1053 | `            elif operator == '*':` | Alternative runtime condition. |
| 1054 | `                # LINE: Multiplication path.` | Comment/guideline in current code. |
| 1055 | `                if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):` | Checks a runtime condition. |
| 1056 | `                    # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1057 | `                    if isinstance(left, bool):` | Checks a runtime condition. |
| 1058 | `                        # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1059 | `                        left = 1 if left == True else 0` | Stores or updates runtime state/value. |
| 1060 | `                    # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1061 | `                    elif isinstance(left, str):` | Alternative runtime condition. |
| 1062 | `                        # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1063 | `                        left = 1 if left != "" else 0` | Stores or updates runtime state/value. |
| 1064 | `                    # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1065 | `                    if isinstance(right, bool):` | Checks a runtime condition. |
| 1066 | `                        # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1067 | `                        right = 1 if right == True else 0` | Stores or updates runtime state/value. |
| 1068 | `                    # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1069 | `                    elif isinstance(right, str):` | Alternative runtime condition. |
| 1070 | `                        # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1071 | `                        right = 1 if right != "" else 0` | Stores or updates runtime state/value. |
| 1072 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1073 | `                return left * right  # type: ignore[operator]` | Returns runtime value/result to caller. |
| 1074 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1075 | `            elif operator == '**':` | Alternative runtime condition. |
| 1076 | `                # LINE: Exponent path.` | Comment/guideline in current code. |
| 1077 | `                if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):` | Checks a runtime condition. |
| 1078 | `                    # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1079 | `                    if isinstance(left, bool):` | Checks a runtime condition. |
| 1080 | `                        # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1081 | `                        left = 1 if left == True else 0` | Stores or updates runtime state/value. |
| 1082 | `                    # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1083 | `                    elif isinstance(left, str):` | Alternative runtime condition. |
| 1084 | `                        # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1085 | `                        left = 1 if left != "" else 0` | Stores or updates runtime state/value. |
| 1086 | `                    # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1087 | `                    if isinstance(right, bool):` | Checks a runtime condition. |
| 1088 | `                        # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1089 | `                        right = 1 if right == True else 0` | Stores or updates runtime state/value. |
| 1090 | `                    # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1091 | `                    elif isinstance(right, str):` | Alternative runtime condition. |
| 1092 | `                        # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1093 | `                        right = 1 if right != "" else 0` | Stores or updates runtime state/value. |
| 1094 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1095 | `                return left ** right  # type: ignore[operator]` | Returns runtime value/result to caller. |
| 1096 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1097 | `            elif operator == '/':` | Alternative runtime condition. |
| 1098 | `                # Division includes runtime zero checking.` | Comment/guideline in current code. |
| 1099 | `                # LINE: Division path.` | Comment/guideline in current code. |
| 1100 | `                if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):` | Checks a runtime condition. |
| 1101 | `                    # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1102 | `                    if isinstance(left, bool):` | Checks a runtime condition. |
| 1103 | `                        # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1104 | `                        left = 1 if left == True else 0` | Stores or updates runtime state/value. |
| 1105 | `                    # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1106 | `                    elif isinstance(left, str):` | Alternative runtime condition. |
| 1107 | `                        # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1108 | `                        left = 1 if left != "" else 0` | Stores or updates runtime state/value. |
| 1109 | `                    # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1110 | `                    if isinstance(right, bool):` | Checks a runtime condition. |
| 1111 | `                        # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1112 | `                        right = 1 if right == True else 0` | Stores or updates runtime state/value. |
| 1113 | `                    # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1114 | `                    elif isinstance(right, str):` | Alternative runtime condition. |
| 1115 | `                        # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1116 | `                        right = 1 if right != "" else 0` | Stores or updates runtime state/value. |
| 1117 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1118 | `                if right == 0:` | Checks a runtime condition. |
| 1119 | `                    # LINE: Stop execution when divisor is zero.` | Comment/guideline in current code. |
| 1120 | `                    raise InterpreterError("Runtime Error: Division by zero is undefined", node.line)` | Stops execution with a runtime error. |
| 1121 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1122 | `                return left / right  # type: ignore[operator]` | Returns runtime value/result to caller. |
| 1123 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1124 | `            elif operator == '%':` | Alternative runtime condition. |
| 1125 | `                # LINE: Modulo/remainder path.` | Comment/guideline in current code. |
| 1126 | `                if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):` | Checks a runtime condition. |
| 1127 | `                    # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1128 | `                    if isinstance(left, bool):` | Checks a runtime condition. |
| 1129 | `                        # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1130 | `                        left = 1 if left == True else 0` | Stores or updates runtime state/value. |
| 1131 | `                    # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1132 | `                    elif isinstance(left, str):` | Alternative runtime condition. |
| 1133 | `                        # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1134 | `                        left = 1 if left != "" else 0` | Stores or updates runtime state/value. |
| 1135 | `                    # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1136 | `                    if isinstance(right, bool):` | Checks a runtime condition. |
| 1137 | `                        # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1138 | `                        right = 1 if right == True else 0` | Stores or updates runtime state/value. |
| 1139 | `                    # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1140 | `                    elif isinstance(right, str):` | Alternative runtime condition. |
| 1141 | `                        # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1142 | `                        right = 1 if right != "" else 0` | Stores or updates runtime state/value. |
| 1143 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1144 | `                if right == 0:` | Checks a runtime condition. |
| 1145 | `                    # LINE: Modulo by zero is also invalid.` | Comment/guideline in current code. |
| 1146 | `                    raise InterpreterError("Runtime Error: Division by zero is undefined", node.line)` | Stops execution with a runtime error. |
| 1147 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1148 | `                return left % right  # type: ignore[operator]` | Returns runtime value/result to caller. |
| 1149 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1150 | `            elif operator == '==':` | Alternative runtime condition. |
| 1151 | `                # Comparison operators return branch/boolean results.` | Comment/guideline in current code. |
| 1152 | `                # LINE: Equality comparison.` | Comment/guideline in current code. |
| 1153 | `                return left == right` | Returns runtime value/result to caller. |
| 1154 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1155 | `            elif operator == '!=':` | Alternative runtime condition. |
| 1156 | `                # LINE: Not-equal comparison.` | Comment/guideline in current code. |
| 1157 | `                return left != right` | Returns runtime value/result to caller. |
| 1158 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1159 | `            elif operator == '<':` | Alternative runtime condition. |
| 1160 | `                # LINE: Less-than comparison.` | Comment/guideline in current code. |
| 1161 | `                if isinstance(left, str):` | Checks a runtime condition. |
| 1162 | `                    # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1163 | `                    left = 0 if left == "" else 1` | Stores or updates runtime state/value. |
| 1164 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1165 | `                if isinstance(right, str):` | Checks a runtime condition. |
| 1166 | `                    # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1167 | `                    right = 0 if right == "" else 1` | Stores or updates runtime state/value. |
| 1168 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1169 | `                return left < right` | Returns runtime value/result to caller. |
| 1170 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1171 | `            elif operator == '<=':` | Alternative runtime condition. |
| 1172 | `                # LINE: Less-than-or-equal comparison.` | Comment/guideline in current code. |
| 1173 | `                if isinstance(left, str):` | Checks a runtime condition. |
| 1174 | `                    # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1175 | `                    left = 0 if left == "" else 1` | Stores or updates runtime state/value. |
| 1176 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1177 | `                if isinstance(right, str):` | Checks a runtime condition. |
| 1178 | `                    # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1179 | `                    right = 0 if right == "" else 1` | Stores or updates runtime state/value. |
| 1180 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1181 | `                return left <= right` | Returns runtime value/result to caller. |
| 1182 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1183 | `            elif operator == '>':` | Alternative runtime condition. |
| 1184 | `                # LINE: Greater-than comparison.` | Comment/guideline in current code. |
| 1185 | `                if isinstance(left, str):` | Checks a runtime condition. |
| 1186 | `                    # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1187 | `                    left = 0 if left == "" else 1` | Stores or updates runtime state/value. |
| 1188 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1189 | `                if isinstance(right, str):` | Checks a runtime condition. |
| 1190 | `                    # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1191 | `                    right = 0 if right == "" else 1` | Stores or updates runtime state/value. |
| 1192 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1193 | `                return left > right` | Returns runtime value/result to caller. |
| 1194 | `` | Blank spacing line. |
| 1195 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1196 | `            elif operator == '>=':` | Alternative runtime condition. |
| 1197 | `                # LINE: Greater-than-or-equal comparison.` | Comment/guideline in current code. |
| 1198 | `                if isinstance(left, str):` | Checks a runtime condition. |
| 1199 | `                    # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1200 | `                    left = 0 if left == "" else 1` | Stores or updates runtime state/value. |
| 1201 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1202 | `                if isinstance(right, str):` | Checks a runtime condition. |
| 1203 | `                    # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1204 | `                    right = 0 if right == "" else 1` | Stores or updates runtime state/value. |
| 1205 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1206 | `                return left >= right` | Returns runtime value/result to caller. |
| 1207 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1208 | `            elif operator == '&&':` | Alternative runtime condition. |
| 1209 | `                # Logical operators convert numeric/string values into boolean` | Comment/guideline in current code. |
| 1210 | `                # truthiness before applying AND/OR.` | Comment/guideline in current code. |
| 1211 | `                # LINE: Logical AND path.` | Comment/guideline in current code. |
| 1212 | `                if isinstance(left, int) or isinstance(left, float):` | Checks a runtime condition. |
| 1213 | `                    # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1214 | `                    if left == 0:` | Checks a runtime condition. |
| 1215 | `                        # AUTO: Sets `left`.` | Comment/guideline in current code. |
| 1216 | `                        left = False` | Stores or updates runtime state/value. |
| 1217 | `                    # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 1218 | `                    else:` | Fallback runtime branch. |
| 1219 | `                        # AUTO: Sets `left`.` | Comment/guideline in current code. |
| 1220 | `                        left = True` | Stores or updates runtime state/value. |
| 1221 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1222 | `                elif isinstance(right, int) or isinstance(right, float):` | Alternative runtime condition. |
| 1223 | `                    # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1224 | `                    if right == 0:` | Checks a runtime condition. |
| 1225 | `                        # AUTO: Sets `right`.` | Comment/guideline in current code. |
| 1226 | `                        right = False` | Stores or updates runtime state/value. |
| 1227 | `                    # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 1228 | `                    else:` | Fallback runtime branch. |
| 1229 | `                        # AUTO: Sets `right`.` | Comment/guideline in current code. |
| 1230 | `                        right = True` | Stores or updates runtime state/value. |
| 1231 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1232 | `                elif isinstance(left, str):` | Alternative runtime condition. |
| 1233 | `                    # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1234 | `                    left = False if left == "" else True` | Stores or updates runtime state/value. |
| 1235 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1236 | `                elif isinstance(right, str):` | Alternative runtime condition. |
| 1237 | `                    # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1238 | `                    right = False if right == "" else True` | Stores or updates runtime state/value. |
| 1239 | `` | Blank spacing line. |
| 1240 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1241 | `                elif isinstance(left, str) or isinstance(right, str):` | Alternative runtime condition. |
| 1242 | `                    # AUTO: Sets `left`.` | Comment/guideline in current code. |
| 1243 | `                    left = bool(left)` | Stores or updates runtime state/value. |
| 1244 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1245 | `                elif isinstance(left, str) or isinstance(right, str):` | Alternative runtime condition. |
| 1246 | `                    # AUTO: Sets `right`.` | Comment/guideline in current code. |
| 1247 | `                    right = bool(right)` | Stores or updates runtime state/value. |
| 1248 | `` | Blank spacing line. |
| 1249 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1250 | `                return bool(left) and bool(right)` | Returns runtime value/result to caller. |
| 1251 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1252 | `            elif operator == '\|\|':` | Alternative runtime condition. |
| 1253 | `                # LINE: Logical OR path.` | Comment/guideline in current code. |
| 1254 | `                if isinstance(left, int) or isinstance(left, float):` | Checks a runtime condition. |
| 1255 | `                    # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1256 | `                    if left == 0:` | Checks a runtime condition. |
| 1257 | `                        # AUTO: Sets `left`.` | Comment/guideline in current code. |
| 1258 | `                        left = False` | Stores or updates runtime state/value. |
| 1259 | `                    # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 1260 | `                    else:` | Fallback runtime branch. |
| 1261 | `                        # AUTO: Sets `left`.` | Comment/guideline in current code. |
| 1262 | `                        left = True` | Stores or updates runtime state/value. |
| 1263 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1264 | `                elif isinstance(right, int) or isinstance(right, float):` | Alternative runtime condition. |
| 1265 | `                    # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1266 | `                    if right == 0:` | Checks a runtime condition. |
| 1267 | `                        # AUTO: Sets `right`.` | Comment/guideline in current code. |
| 1268 | `                        right = False` | Stores or updates runtime state/value. |
| 1269 | `                    # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 1270 | `                    else:` | Fallback runtime branch. |
| 1271 | `                        # AUTO: Sets `right`.` | Comment/guideline in current code. |
| 1272 | `                        right = True` | Stores or updates runtime state/value. |
| 1273 | `` | Blank spacing line. |
| 1274 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1275 | `                elif isinstance(left, str) or isinstance(right, str):` | Alternative runtime condition. |
| 1276 | `                    # AUTO: Sets `left`.` | Comment/guideline in current code. |
| 1277 | `                    left = bool(left)` | Stores or updates runtime state/value. |
| 1278 | `                # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1279 | `                elif isinstance(left, str) or isinstance(right, str):` | Alternative runtime condition. |
| 1280 | `                    # AUTO: Sets `right`.` | Comment/guideline in current code. |
| 1281 | `                    right = bool(right)` | Stores or updates runtime state/value. |
| 1282 | `` | Blank spacing line. |
| 1283 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1284 | `                return bool(left) or bool(right)` | Returns runtime value/result to caller. |
| 1285 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1286 | `            elif operator == '!':` | Alternative runtime condition. |
| 1287 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1288 | `                return not bool(left)` | Returns runtime value/result to caller. |
| 1289 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 1290 | `            elif operator == 'neg':` | Alternative runtime condition. |
| 1291 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1292 | `                return -left  # type: ignore` | Returns runtime value/result to caller. |
| 1293 | `            # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 1294 | `            else:` | Fallback runtime branch. |
| 1295 | `                # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 1296 | `                raise Exception(f"Unknown operator: {operator}")` | Raises control-flow or runtime error exception. |
| 1297 | `        ` | Blank spacing line. |
| 1298 | `        # AUTO: Handles the matching error case.` | Comment/guideline in current code. |
| 1299 | `        except ZeroDivisionError:` | Handles the matching runtime/import error case. |
| 1300 | `            # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 1301 | `            raise InterpreterError("Runtime Error: Division by zero", "")` | Stops execution with a runtime error. |
| 1302 | `` | Blank spacing line. |
| 1303 | `    # AUTO: Defines function `_parse_literal`.` | Comment/guideline in current code. |
| 1304 | `    def _parse_literal(self, value):` | Runtime support logic. |
| 1305 | `` | Blank spacing line. |
| 1306 | `        # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1307 | `        if isinstance(value, str):` | Checks a runtime condition. |
| 1308 | `            # AUTO: Sets `var_info`.` | Comment/guideline in current code. |
| 1309 | `            var_info = self.lookup_variable(value)` | Reads variable metadata/value from runtime scopes. |
| 1310 | `            # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1311 | `            if var_info is not None and not isinstance(var_info, str):` | Checks a runtime condition. |
| 1312 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1313 | `                return var_info["value"]` | Returns runtime value/result to caller. |
| 1314 | `` | Blank spacing line. |
| 1315 | `        # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1316 | `        if isinstance(value, (int, float, bool)):` | Checks a runtime condition. |
| 1317 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1318 | `            return value` | Returns runtime value/result to caller. |
| 1319 | `` | Blank spacing line. |
| 1320 | `        # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1321 | `        if not isinstance(value, str):` | Checks a runtime condition. |
| 1322 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1323 | `            return value` | Returns runtime value/result to caller. |
| 1324 | `` | Blank spacing line. |
| 1325 | `        # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 1326 | `        value = value.strip()` | Stores or updates runtime state/value. |
| 1327 | `` | Blank spacing line. |
| 1328 | `        # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1329 | `        if value.startswith('"') and value.endswith('"'):` | Checks a runtime condition. |
| 1330 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1331 | `            return value[1:-1]` | Returns runtime value/result to caller. |
| 1332 | `        ` | Blank spacing line. |
| 1333 | `        # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1334 | `        if value.startswith("'") and value.endswith("'"):` | Checks a runtime condition. |
| 1335 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1336 | `            return value[1:-1]` | Returns runtime value/result to caller. |
| 1337 | `` | Blank spacing line. |
| 1338 | `        # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1339 | `        if value in ('true', 'sunshine'):` | Checks a runtime condition. |
| 1340 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1341 | `            return True` | Returns runtime value/result to caller. |
| 1342 | `        # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1343 | `        if value in ('false', 'frost'):` | Checks a runtime condition. |
| 1344 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1345 | `            return False` | Returns runtime value/result to caller. |
| 1346 | `` | Blank spacing line. |
| 1347 | `        # AUTO: Sets `parse_value`.` | Comment/guideline in current code. |
| 1348 | `        parse_value = value` | Stores or updates runtime state/value. |
| 1349 | `        # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1350 | `        if parse_value.startswith('~'):` | Checks a runtime condition. |
| 1351 | `            # AUTO: Sets `parse_value`.` | Comment/guideline in current code. |
| 1352 | `            parse_value = '-' + parse_value[1:]` | Stores or updates runtime state/value. |
| 1353 | `` | Blank spacing line. |
| 1354 | `        # AUTO: Starts protected code that can catch errors.` | Comment/guideline in current code. |
| 1355 | `        try:` | Starts protected block for optional runtime dependency or error handling. |
| 1356 | `            # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1357 | `            if '.' in parse_value:` | Checks a runtime condition. |
| 1358 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1359 | `                return float(parse_value)` | Returns runtime value/result to caller. |
| 1360 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1361 | `            return int(parse_value)` | Returns runtime value/result to caller. |
| 1362 | `        # AUTO: Handles the matching error case.` | Comment/guideline in current code. |
| 1363 | `        except ValueError:` | Handles the matching runtime/import error case. |
| 1364 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1365 | `            return value ` | Returns runtime value/result to caller. |
| 1366 | `    ` | Blank spacing line. |
| 1367 | `` | Blank spacing line. |
| 1368 | `    # AUTO: Defines function `eval_function_declaration`.` | Comment/guideline in current code. |
| 1369 | `    def eval_function_declaration(self, node):` | Starts a node-specific runtime evaluator. |
| 1370 | `        # GUIDE: Function declarations are registered, not executed immediately.` | Comment/guideline in current code. |
| 1371 | `        # The saved body runs later when a FunctionCallNode is interpreted.` | Comment/guideline in current code. |
| 1372 | `        # LINE: First child stores function return type.` | Comment/guideline in current code. |
| 1373 | `        return_type = node.children[0].value` | Stores or updates runtime state/value. |
| 1374 | `        # LINE: Second child stores the parameter list node.` | Comment/guideline in current code. |
| 1375 | `        parameters_node = node.children[1]` | Stores or updates runtime state/value. |
| 1376 | `        # LINE: node.value stores the function name.` | Comment/guideline in current code. |
| 1377 | `        func_name = node.value` | Stores or updates runtime state/value. |
| 1378 | `` | Blank spacing line. |
| 1379 | `        # LINE: Collect parameters into simple dictionaries.` | Comment/guideline in current code. |
| 1380 | `        params = []` | Stores or updates runtime state/value. |
| 1381 | `        # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1382 | `        if parameters_node and len(parameters_node.children) > 0:` | Checks a runtime condition. |
| 1383 | `            # AUTO: Starts a loop over these values.` | Comment/guideline in current code. |
| 1384 | `            for param in parameters_node.children:` | Loops through AST children/items. |
| 1385 | `                # LINE: Parameter nodes must have the expected AST shape.` | Comment/guideline in current code. |
| 1386 | `                if not hasattr(param, 'node_type') or param.node_type != 'Parameter':` | Checks a runtime condition. |
| 1387 | `                    # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 1388 | `                    raise Exception(f"Invalid parameter: {param.value}")` | Raises control-flow or runtime error exception. |
| 1389 | `                # LINE: First parameter child is type.` | Comment/guideline in current code. |
| 1390 | `                param_type = param.children[0].value` | Stores or updates runtime state/value. |
| 1391 | `                # LINE: Second parameter child is name.` | Comment/guideline in current code. |
| 1392 | `                param_name = param.children[1].value` | Stores or updates runtime state/value. |
| 1393 | `                # LINE: Detect array/list parameter marker.` | Comment/guideline in current code. |
| 1394 | `                is_list = any(child.node_type == "ArrayParam" for child in param.children)` | Stores or updates runtime state/value. |
| 1395 | `                # LINE: Save this parameter metadata.` | Comment/guideline in current code. |
| 1396 | `                params.append({"name": param_name, "type": param_type, "is_list": is_list})` | Runtime support logic. |
| 1397 | `` | Blank spacing line. |
| 1398 | `        # LINE: Register the function in self.functions for later calls.` | Comment/guideline in current code. |
| 1399 | `        self.declare_function(func_name, return_type, params, node)` | Stores a function for later execution. |
| 1400 | `` | Blank spacing line. |
| 1401 | `        # LINE: Declaration itself produces no runtime value.` | Comment/guideline in current code. |
| 1402 | `        return None` | Returns runtime value/result to caller. |
| 1403 | `` | Blank spacing line. |
| 1404 | `    # AUTO: Defines function `eval_block`.` | Comment/guideline in current code. |
| 1405 | `    def eval_block(self, block_node):` | Starts a node-specific runtime evaluator. |
| 1406 | `        # GUIDE: Execute statements in order. reclaim/prune/skip can interrupt this` | Comment/guideline in current code. |
| 1407 | `        # normal sequence through ReturnValue or loop flags.` | Comment/guideline in current code. |
| 1408 | `        # LINE: Run each statement inside the block from top to bottom.` | Comment/guideline in current code. |
| 1409 | `        for statement in block_node.children:` | Loops through AST children/items. |
| 1410 | `            # LINE: Dispatch statement to the correct eval_* method.` | Comment/guideline in current code. |
| 1411 | `            self.interpret(statement)` | Runtime support logic. |
| 1412 | `            # LINE: Stop this block if prune was triggered.` | Comment/guideline in current code. |
| 1413 | `            if self.break_triggered():` | Checks a runtime condition. |
| 1414 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1415 | `                return` | Runtime support logic. |
| 1416 | `            # LINE: Stop this block if skip was triggered.` | Comment/guideline in current code. |
| 1417 | `            if self.continue_flag:` | Checks a runtime condition. |
| 1418 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1419 | `                return` | Runtime support logic. |
| 1420 | `` | Blank spacing line. |
| 1421 | `` | Blank spacing line. |
| 1422 | `    # AUTO: Defines function `plant`.` | Comment/guideline in current code. |
| 1423 | `    def plant(self, value):` | Starts helper that emits plant output. |
| 1424 | `        # AUTO: Sends an event/message to the frontend.` | Comment/guideline in current code. |
| 1425 | `        self.socketio.emit('output', {'output': str(value)})` | Sends output/input event to frontend/server collector. |
| 1426 | `` | Blank spacing line. |
| 1427 | `    # AUTO: Defines function `plant_out`.` | Comment/guideline in current code. |
| 1428 | `    def plant_out(self, num):` | Starts helper that emits plant output. |
| 1429 | `        # AUTO: Sends an event/message to the frontend.` | Comment/guideline in current code. |
| 1430 | `        self.socketio.emit('output', {'output': str(num)})` | Sends output/input event to frontend/server collector. |
| 1431 | `        # AUTO: Appends a value to a list.` | Comment/guideline in current code. |
| 1432 | `        self.output.append(str(num))` | Runtime support logic. |
| 1433 | `` | Blank spacing line. |
| 1434 | `` | Blank spacing line. |
| 1435 | `    # AUTO: Defines function `eval_print`.` | Comment/guideline in current code. |
| 1436 | `    def eval_print(self, node):` | Starts a node-specific runtime evaluator. |
| 1437 | `        # GUIDE: plant() evaluates args, applies optional {} formatting, and` | Comment/guideline in current code. |
| 1438 | `        # emits the final text to the UI terminal.` | Comment/guideline in current code. |
| 1439 | `        # LINE: plant() with no arguments prints nothing.` | Comment/guideline in current code. |
| 1440 | `        if not node.children:` | Checks a runtime condition. |
| 1441 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1442 | `            return` | Runtime support logic. |
| 1443 | `` | Blank spacing line. |
| 1444 | `        # LINE: First plant argument can be normal text or a format string.` | Comment/guideline in current code. |
| 1445 | `        first = node.children[0]` | Stores or updates runtime state/value. |
| 1446 | `` | Blank spacing line. |
| 1447 | `        # LINE: Evaluate the first argument.` | Comment/guideline in current code. |
| 1448 | `        evaluated_first = self.interpret(first)` | Stores or updates runtime state/value. |
| 1449 | `        # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1450 | `        if isinstance(evaluated_first, float):` | Checks a runtime condition. |
| 1451 | `            # LINE: Limit displayed float decimals to 5 digits.` | Comment/guideline in current code. |
| 1452 | `            whole, dot, dec = str(evaluated_first).partition('.')` | Stores or updates runtime state/value. |
| 1453 | `            # AUTO: Sets `dec`.` | Comment/guideline in current code. |
| 1454 | `            dec = dec[:5]` | Stores or updates runtime state/value. |
| 1455 | `            # AUTO: Sets `evaluated_first`.` | Comment/guideline in current code. |
| 1456 | `            evaluated_first = float(f"{whole}.{dec}")` | Stores or updates runtime state/value. |
| 1457 | `` | Blank spacing line. |
| 1458 | `        # LINE: If first string has {}, use Python format with remaining args.` | Comment/guideline in current code. |
| 1459 | `        if isinstance(evaluated_first, str) and '{}' in evaluated_first:` | Checks a runtime condition. |
| 1460 | `            # AUTO: Sets `values`.` | Comment/guideline in current code. |
| 1461 | `            values = []` | Stores or updates runtime state/value. |
| 1462 | `            # AUTO: Starts a loop over these values.` | Comment/guideline in current code. |
| 1463 | `            for arg in node.children[1:]:` | Loops through AST children/items. |
| 1464 | `                # LINE: Evaluate each format value.` | Comment/guideline in current code. |
| 1465 | `                value = self.interpret(arg)` | Stores or updates runtime state/value. |
| 1466 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1467 | `                if isinstance(value, str) and not isinstance(self.lookup_variable(value), str):` | Reads variable metadata/value from runtime scopes. |
| 1468 | `                    # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 1469 | `                    value = self.lookup_variable(value)["value"]  # type: ignore[index]` | Reads variable metadata/value from runtime scopes. |
| 1470 | `                ` | Blank spacing line. |
| 1471 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1472 | `                if isinstance(value, float):` | Checks a runtime condition. |
| 1473 | `                    # AUTO: Sets `whole, dot, dec`.` | Comment/guideline in current code. |
| 1474 | `                    whole, dot, dec = str(value).partition('.')` | Stores or updates runtime state/value. |
| 1475 | `                    # AUTO: Sets `dec`.` | Comment/guideline in current code. |
| 1476 | `                    dec = dec[:5]` | Stores or updates runtime state/value. |
| 1477 | `                    # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 1478 | `                    value = float(f"{whole}.{dec}")` | Stores or updates runtime state/value. |
| 1479 | `` | Blank spacing line. |
| 1480 | `                # AUTO: Appends a value to a list.` | Comment/guideline in current code. |
| 1481 | `                values.append(value)` | Runtime support logic. |
| 1482 | `` | Blank spacing line. |
| 1483 | `            # AUTO: Starts protected code that can catch errors.` | Comment/guideline in current code. |
| 1484 | `            try:` | Starts protected block for optional runtime dependency or error handling. |
| 1485 | `                # LINE: Replace {} placeholders with evaluated values.` | Comment/guideline in current code. |
| 1486 | `                output_str = evaluated_first.format(*values)` | Stores or updates runtime state/value. |
| 1487 | `            # AUTO: Handles the matching error case.` | Comment/guideline in current code. |
| 1488 | `            except Exception as e:` | Handles the matching runtime/import error case. |
| 1489 | `                # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 1490 | `                raise Exception(f"Format error in plant(): '{evaluated_first}' with {values}: {e}")` | Raises control-flow or runtime error exception. |
| 1491 | `` | Blank spacing line. |
| 1492 | `            # LINE: Send formatted output to UI.` | Comment/guideline in current code. |
| 1493 | `            self.plant(output_str)` | Runtime support logic. |
| 1494 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1495 | `            return` | Runtime support logic. |
| 1496 | `` | Blank spacing line. |
| 1497 | `        # LINE: Multiple plant args without {} are joined with spaces.` | Comment/guideline in current code. |
| 1498 | `        if len(node.children) > 1:` | Checks a runtime condition. |
| 1499 | `            # AUTO: Sets `parts`.` | Comment/guideline in current code. |
| 1500 | `            parts = [str(evaluated_first)]` | Stores or updates runtime state/value. |
| 1501 | `            # AUTO: Starts a loop over these values.` | Comment/guideline in current code. |
| 1502 | `            for arg in node.children[1:]:` | Loops through AST children/items. |
| 1503 | `                # LINE: Evaluate each extra plant argument.` | Comment/guideline in current code. |
| 1504 | `                value = self.interpret(arg)` | Stores or updates runtime state/value. |
| 1505 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1506 | `                if isinstance(value, float):` | Checks a runtime condition. |
| 1507 | `                    # AUTO: Sets `whole, dot, dec`.` | Comment/guideline in current code. |
| 1508 | `                    whole, dot, dec = str(value).partition('.')` | Stores or updates runtime state/value. |
| 1509 | `                    # AUTO: Sets `dec`.` | Comment/guideline in current code. |
| 1510 | `                    dec = dec[:5]` | Stores or updates runtime state/value. |
| 1511 | `                    # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 1512 | `                    value = float(f"{whole}.{dec}")` | Stores or updates runtime state/value. |
| 1513 | `                # AUTO: Appends a value to a list.` | Comment/guideline in current code. |
| 1514 | `                parts.append(str(value))` | Runtime support logic. |
| 1515 | `            # LINE: Output the combined text.` | Comment/guideline in current code. |
| 1516 | `            self.plant(" ".join(parts))` | Runtime support logic. |
| 1517 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1518 | `            return` | Runtime support logic. |
| 1519 | `` | Blank spacing line. |
| 1520 | `        # LINE: Single plant argument output path.` | Comment/guideline in current code. |
| 1521 | `        self.plant(str(evaluated_first))` | Runtime support logic. |
| 1522 | `` | Blank spacing line. |
| 1523 | `    # AUTO: Defines function `eval_formatted_string`.` | Comment/guideline in current code. |
| 1524 | `    def eval_formatted_string(self, node):` | Starts a node-specific runtime evaluator. |
| 1525 | `        # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 1526 | `        value = node.value` | Stores or updates runtime state/value. |
| 1527 | `        # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1528 | `        if value.startswith('"') and value.endswith('"'):` | Checks a runtime condition. |
| 1529 | `            # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 1530 | `            value = value[1:-1]` | Stores or updates runtime state/value. |
| 1531 | `` | Blank spacing line. |
| 1532 | `        # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 1533 | `        value = value.replace(r'\\', '\\')` | Stores or updates runtime state/value. |
| 1534 | `        # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 1535 | `        value = value.replace(r'\n', '\n')` | Stores or updates runtime state/value. |
| 1536 | `        # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 1537 | `        value = value.replace(r'\t', '\t')` | Stores or updates runtime state/value. |
| 1538 | `        # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 1539 | `        value = value.replace(r'\"', '"')` | Stores or updates runtime state/value. |
| 1540 | `        # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 1541 | `        value = value.replace(r'\{', '{')` | Stores or updates runtime state/value. |
| 1542 | `        # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 1543 | `        value = value.replace(r'\}', '}')` | Stores or updates runtime state/value. |
| 1544 | `        # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 1545 | `        value = value.replace(r'\/', '/')` | Stores or updates runtime state/value. |
| 1546 | `        # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1547 | `        return value` | Returns runtime value/result to caller. |
| 1548 | `` | Blank spacing line. |
| 1549 | `` | Blank spacing line. |
| 1550 | `    # AUTO: Defines function `eval_list`.` | Comment/guideline in current code. |
| 1551 | `    def eval_list(self, node):` | Starts a node-specific runtime evaluator. |
| 1552 | `        # AUTO: Sets `result`.` | Comment/guideline in current code. |
| 1553 | `        result = []` | Stores or updates runtime state/value. |
| 1554 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in current code. |
| 1555 | `        for child in node.children:` | Loops through AST children/items. |
| 1556 | `            # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1557 | `            if isinstance(child, ListNode):` | Checks a runtime condition. |
| 1558 | `                # AUTO: Appends a value to a list.` | Comment/guideline in current code. |
| 1559 | `                result.append(self.eval_list(child))` | Runtime support logic. |
| 1560 | `            # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 1561 | `            else:` | Fallback runtime branch. |
| 1562 | `                # AUTO: Appends a value to a list.` | Comment/guideline in current code. |
| 1563 | `                result.append(self.interpret(child))` | Recursively executes/evaluates a child AST node. |
| 1564 | `        # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1565 | `        return result` | Returns runtime value/result to caller. |
| 1566 | `` | Blank spacing line. |
| 1567 | `` | Blank spacing line. |
| 1568 | `    # AUTO: Defines function `eval_list_access`.` | Comment/guideline in current code. |
| 1569 | `    def eval_list_access(self, node):` | Starts a node-specific runtime evaluator. |
| 1570 | `        # AUTO: Sets `name_or_node`.` | Comment/guideline in current code. |
| 1571 | `        name_or_node = node.children[0].value` | Stores or updates runtime state/value. |
| 1572 | `        # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1573 | `        if hasattr(name_or_node, 'node_type') and name_or_node.node_type == "ListAccess":` | Checks a runtime condition. |
| 1574 | `            # AUTO: Sets `list_value`.` | Comment/guideline in current code. |
| 1575 | `            list_value = self.eval_list_access(name_or_node)` | Stores or updates runtime state/value. |
| 1576 | `            # AUTO: Sets `display_name`.` | Comment/guideline in current code. |
| 1577 | `            display_name = "nested list"` | Stores or updates runtime state/value. |
| 1578 | `        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 1579 | `        else:` | Fallback runtime branch. |
| 1580 | `            # AUTO: Sets `list_name`.` | Comment/guideline in current code. |
| 1581 | `            list_name = name_or_node` | Stores or updates runtime state/value. |
| 1582 | `            # AUTO: Sets `list_entry`.` | Comment/guideline in current code. |
| 1583 | `            list_entry = self.lookup_variable(list_name)` | Reads variable metadata/value from runtime scopes. |
| 1584 | `            # AUTO: Sets `list_value`.` | Comment/guideline in current code. |
| 1585 | `            list_value = list_entry["value"]  # type: ignore` | Stores or updates runtime state/value. |
| 1586 | `            # AUTO: Sets `display_name`.` | Comment/guideline in current code. |
| 1587 | `            display_name = list_name` | Stores or updates runtime state/value. |
| 1588 | `` | Blank spacing line. |
| 1589 | `        # AUTO: Sets `index_node`.` | Comment/guideline in current code. |
| 1590 | `        index_node = node.children[1]` | Stores or updates runtime state/value. |
| 1591 | `        # AUTO: Sets `index`.` | Comment/guideline in current code. |
| 1592 | `        index = self.interpret(index_node.children[0])` | Stores or updates runtime state/value. |
| 1593 | `` | Blank spacing line. |
| 1594 | `        # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1595 | `        if not isinstance(index, int):` | Checks a runtime condition. |
| 1596 | `            # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 1597 | `            raise InterpreterError(f"Runtime Error: List index must be an integer. Got '{index}'", node.line)` | Stops execution with a runtime error. |
| 1598 | `        ` | Blank spacing line. |
| 1599 | `        # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1600 | `        if not isinstance(list_value, (list, str)):` | Checks a runtime condition. |
| 1601 | `            # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 1602 | `            raise InterpreterError(f"Runtime Error: Cannot index into a non-list value.", node.line)` | Stops execution with a runtime error. |
| 1603 | `` | Blank spacing line. |
| 1604 | `        # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1605 | `        if index < 0 or index >= len(list_value):` | Checks a runtime condition. |
| 1606 | `            # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 1607 | `            raise InterpreterError(f"Runtime Error: Index '{index}' out of bounds for '{display_name}'.", node.line)` | Stops execution with a runtime error. |
| 1608 | `` | Blank spacing line. |
| 1609 | `        # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1610 | `        return list_value[index]` | Returns runtime value/result to caller. |
| 1611 | `    ` | Blank spacing line. |
| 1612 | `` | Blank spacing line. |
| 1613 | `    # AUTO: Defines function `eval_return`.` | Comment/guideline in current code. |
| 1614 | `    def eval_return(self, node):` | Starts a node-specific runtime evaluator. |
| 1615 | `        # GUIDE: reclaim jumps out of the current function by raising ReturnValue.` | Comment/guideline in current code. |
| 1616 | `        # LINE: Evaluate reclaim value if present; root usually has none.` | Comment/guideline in current code. |
| 1617 | `        value = self.interpret(node.children[0]) if node.children else None` | Stores or updates runtime state/value. |
| 1618 | `        # LINE: Raise ReturnValue so nested blocks immediately exit the function.` | Comment/guideline in current code. |
| 1619 | `        raise ReturnValue(value)` | Uses exception control flow to jump out of function on reclaim. |
| 1620 | `` | Blank spacing line. |
| 1621 | `` | Blank spacing line. |
| 1622 | `    # AUTO: Defines function `eval_function_call`.` | Comment/guideline in current code. |
| 1623 | `    def eval_function_call(self, node):` | Starts a node-specific runtime evaluator. |
| 1624 | `        # GUIDE: Function call flow; evaluate args, enter scope, bind params,` | Comment/guideline in current code. |
| 1625 | `        # run the saved body, then leave the scope.` | Comment/guideline in current code. |
| 1626 | `        # LINE: node.value is the function name being called.` | Comment/guideline in current code. |
| 1627 | `        function_name = node.value` | Stores or updates runtime state/value. |
| 1628 | `` | Blank spacing line. |
| 1629 | `        # Evaluate all actual arguments before entering the called function.` | Comment/guideline in current code. |
| 1630 | `        # Example: gcd(a, b) becomes [value_of_a, value_of_b].` | Comment/guideline in current code. |
| 1631 | `        # LINE: Evaluate every argument expression before binding parameters.` | Comment/guideline in current code. |
| 1632 | `        args = [self.interpret(arg.children[0]) for arg in node.children]` | Stores or updates runtime state/value. |
| 1633 | `` | Blank spacing line. |
| 1634 | `        # Look up the function saved earlier by eval_function_declaration().` | Comment/guideline in current code. |
| 1635 | `        # LINE: Fetch function metadata from self.functions.` | Comment/guideline in current code. |
| 1636 | `        func_info = self.lookup_function(function_name)` | Stores or updates runtime state/value. |
| 1637 | `        # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1638 | `        if isinstance(func_info, str):` | Checks a runtime condition. |
| 1639 | `            # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 1640 | `            raise InterpreterError(func_info, node.line)` | Stops execution with a runtime error. |
| 1641 | `` | Blank spacing line. |
| 1642 | `        # LINE: Expected parameter list saved during declaration.` | Comment/guideline in current code. |
| 1643 | `        expected_params = func_info["params"]` | Stores or updates runtime state/value. |
| 1644 | `        # LINE: FunctionDeclarationNode containing the function body.` | Comment/guideline in current code. |
| 1645 | `        function_node = func_info["node"]` | Stores or updates runtime state/value. |
| 1646 | `` | Blank spacing line. |
| 1647 | `        # LINE: Argument count must match parameter count.` | Comment/guideline in current code. |
| 1648 | `        if len(expected_params) != len(args):` | Checks a runtime condition. |
| 1649 | `            # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 1650 | `            raise InterpreterError(` | Stops execution with a runtime error. |
| 1651 | `                # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1652 | `                f"Runtime Error: Function '{function_name}' expects {len(expected_params)} argument(s), got {len(args)}.",` | Runtime support logic. |
| 1653 | `                # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1654 | `                node.line` | Runtime support logic. |
| 1655 | `            # AUTO: Closes the current grouped code/data.` | Comment/guideline in current code. |
| 1656 | `            )` | Closes Python grouping/list/dict/call. |
| 1657 | `        ` | Blank spacing line. |
| 1658 | `        # LINE: Enter a new local function scope.` | Comment/guideline in current code. |
| 1659 | `        self.enter_scope()` | Enters a new local runtime scope. |
| 1660 | `        ` | Blank spacing line. |
| 1661 | `        # AUTO: Starts protected code that can catch errors.` | Comment/guideline in current code. |
| 1662 | `        try:` | Starts protected block for optional runtime dependency or error handling. |
| 1663 | `            # LINE: Bind each argument value to its parameter variable.` | Comment/guideline in current code. |
| 1664 | `            for i, param in enumerate(expected_params):` | Loops through AST children/items. |
| 1665 | `                # Bind each argument value to its parameter name in the new` | Comment/guideline in current code. |
| 1666 | `                # function scope. Example: parameter "a" receives 48.` | Comment/guideline in current code. |
| 1667 | `                # AUTO: Sets `param_name`.` | Comment/guideline in current code. |
| 1668 | `                param_name = param["name"]` | Stores or updates runtime state/value. |
| 1669 | `                # AUTO: Sets `param_type`.` | Comment/guideline in current code. |
| 1670 | `                param_type = param["type"]` | Stores or updates runtime state/value. |
| 1671 | `                # AUTO: Sets `arg_value`.` | Comment/guideline in current code. |
| 1672 | `                arg_value = args[i]` | Stores or updates runtime state/value. |
| 1673 | `                # AUTO: Sets `is_list`.` | Comment/guideline in current code. |
| 1674 | `                is_list = param.get("is_list", False)` | Stores or updates runtime state/value. |
| 1675 | `                # LINE: Parameters are stored like local variables.` | Comment/guideline in current code. |
| 1676 | `                self.declare_variable(param_name, param_type, arg_value, is_list=is_list)` | Creates a variable in current runtime scope. |
| 1677 | `` | Blank spacing line. |
| 1678 | `            # AUTO: Starts protected code that can catch errors.` | Comment/guideline in current code. |
| 1679 | `            try:` | Starts protected block for optional runtime dependency or error handling. |
| 1680 | `                # Execute the function body block. If reclaim runs inside,` | Comment/guideline in current code. |
| 1681 | `                # eval_return raises ReturnValue and jumps to the except below.` | Comment/guideline in current code. |
| 1682 | `                # LINE: Run the saved function body.` | Comment/guideline in current code. |
| 1683 | `                self.eval_block(function_node.children[2])` | Runtime support logic. |
| 1684 | `` | Blank spacing line. |
| 1685 | `            # AUTO: Handles the matching error case.` | Comment/guideline in current code. |
| 1686 | `            except ReturnValue as ret:` | Handles the matching runtime/import error case. |
| 1687 | `                # The reclaim value becomes the function call result.` | Comment/guideline in current code. |
| 1688 | `                # LINE: Return reclaim's value to the caller.` | Comment/guideline in current code. |
| 1689 | `                return ret.value` | Returns runtime value/result to caller. |
| 1690 | `` | Blank spacing line. |
| 1691 | `            # LINE: If no reclaim value happened, function returns None.` | Comment/guideline in current code. |
| 1692 | `            return None` | Returns runtime value/result to caller. |
| 1693 | `` | Blank spacing line. |
| 1694 | `        # AUTO: Runs cleanup code no matter what happened.` | Comment/guideline in current code. |
| 1695 | `        finally:` | Runs cleanup even if reclaim/error happens. |
| 1696 | `            # LINE: Always leave the function scope even if an error/reclaim happens.` | Comment/guideline in current code. |
| 1697 | `            self.exit_scope()` | Leaves current runtime scope. |
| 1698 | `            # LINE: Clear active function marker.` | Comment/guideline in current code. |
| 1699 | `            self.current_func_name = None` | Stores or updates runtime state/value. |
| 1700 | `` | Blank spacing line. |
| 1701 | `` | Blank spacing line. |
| 1702 | `    # AUTO: Defines function `eval_append`.` | Comment/guideline in current code. |
| 1703 | `    def eval_append(self, node):` | Starts a node-specific runtime evaluator. |
| 1704 | `        # AUTO: Sets `list_name`.` | Comment/guideline in current code. |
| 1705 | `        list_name = node.parent.children[0].value` | Stores or updates runtime state/value. |
| 1706 | `        # AUTO: Sets `list_info`.` | Comment/guideline in current code. |
| 1707 | `        list_info = self.lookup_variable(list_name)` | Reads variable metadata/value from runtime scopes. |
| 1708 | `` | Blank spacing line. |
| 1709 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in current code. |
| 1710 | `        for child in node.children:` | Loops through AST children/items. |
| 1711 | `            # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 1712 | `            value = self.interpret(child)` | Recursively executes/evaluates a child AST node. |
| 1713 | `            # AUTO: Appends a value to a list.` | Comment/guideline in current code. |
| 1714 | `            list_info["value"].append(value)  # type: ignore` | Runtime support logic. |
| 1715 | `` | Blank spacing line. |
| 1716 | `        ` | Blank spacing line. |
| 1717 | `    # AUTO: Defines function `eval_insert`.` | Comment/guideline in current code. |
| 1718 | `    def eval_insert(self, node):` | Starts a node-specific runtime evaluator. |
| 1719 | `        # AUTO: Sets `list_name`.` | Comment/guideline in current code. |
| 1720 | `        list_name = node.parent.children[0].value` | Stores or updates runtime state/value. |
| 1721 | `        # AUTO: Sets `list_info`.` | Comment/guideline in current code. |
| 1722 | `        list_info = self.lookup_variable(list_name)` | Reads variable metadata/value from runtime scopes. |
| 1723 | `` | Blank spacing line. |
| 1724 | `        # AUTO: Sets `index`.` | Comment/guideline in current code. |
| 1725 | `        index = self.interpret(node.children[0].children[0])` | Stores or updates runtime state/value. |
| 1726 | `` | Blank spacing line. |
| 1727 | `        # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1728 | `        if not isinstance(index, int):` | Checks a runtime condition. |
| 1729 | `            # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 1730 | `            raise InterpreterError("Runtime Error: Insert index must be an integer", node.line)` | Stops execution with a runtime error. |
| 1731 | `` | Blank spacing line. |
| 1732 | `        # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1733 | `        if index < 0 or index > len(list_info["value"]):  # type: ignore` | Checks a runtime condition. |
| 1734 | `            # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 1735 | `            raise InterpreterError(f"Runtime Error: Index {index} out of range for insert", node.line)` | Stops execution with a runtime error. |
| 1736 | `` | Blank spacing line. |
| 1737 | `        # AUTO: Starts a loop over these values.` | Comment/guideline in current code. |
| 1738 | `        for child in node.children[1:]:` | Loops through AST children/items. |
| 1739 | `            # AUTO: Sets `value`.` | Comment/guideline in current code. |
| 1740 | `            value = self.interpret(child)` | Recursively executes/evaluates a child AST node. |
| 1741 | `            # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 1742 | `            list_info["value"].insert(index, value)  # type: ignore` | Runtime support logic. |
| 1743 | `            # AUTO: Adds into `index`.` | Comment/guideline in current code. |
| 1744 | `            index += 1` | Stores or updates runtime state/value. |
| 1745 | `` | Blank spacing line. |
| 1746 | `` | Blank spacing line. |
| 1747 | `    # AUTO: Defines function `eval_remove`.` | Comment/guideline in current code. |
| 1748 | `    def eval_remove(self, node):` | Starts a node-specific runtime evaluator. |
| 1749 | `        # AUTO: Sets `list_name`.` | Comment/guideline in current code. |
| 1750 | `        list_name = node.children[0].value` | Stores or updates runtime state/value. |
| 1751 | `        # AUTO: Sets `index_node`.` | Comment/guideline in current code. |
| 1752 | `        index_node = node.children[1].children[0]` | Stores or updates runtime state/value. |
| 1753 | `` | Blank spacing line. |
| 1754 | `        # AUTO: Sets `list_info`.` | Comment/guideline in current code. |
| 1755 | `        list_info = self.lookup_variable(list_name)` | Reads variable metadata/value from runtime scopes. |
| 1756 | `        # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1757 | `        if isinstance(list_info, str):` | Checks a runtime condition. |
| 1758 | `            # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 1759 | `            raise InterpreterError(list_info, node.line)` | Stops execution with a runtime error. |
| 1760 | `` | Blank spacing line. |
| 1761 | `        # AUTO: Sets `index`.` | Comment/guideline in current code. |
| 1762 | `        index = self.interpret(index_node)` | Stores or updates runtime state/value. |
| 1763 | `` | Blank spacing line. |
| 1764 | `        # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1765 | `        if not isinstance(index, int):` | Checks a runtime condition. |
| 1766 | `            # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 1767 | `            raise InterpreterError("Runtime Error: Remove index must be an integer", node.line)` | Stops execution with a runtime error. |
| 1768 | `` | Blank spacing line. |
| 1769 | `        # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1770 | `        if index < 0 or index >= len(list_info["value"]):` | Checks a runtime condition. |
| 1771 | `            # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 1772 | `            raise InterpreterError(f"Runtime Error: Index {index} out of bounds for remove", node.line)` | Stops execution with a runtime error. |
| 1773 | `` | Blank spacing line. |
| 1774 | `        # AUTO: Sets `removed`.` | Comment/guideline in current code. |
| 1775 | `        removed = list_info["value"].pop(index)` | Stores or updates runtime state/value. |
| 1776 | `` | Blank spacing line. |
| 1777 | `    # AUTO: Defines function `eval_unaryop`.` | Comment/guideline in current code. |
| 1778 | `    def eval_unaryop(self, node):` | Starts a node-specific runtime evaluator. |
| 1779 | `        # LINE: Member increment/decrement path, like student.age++.` | Comment/guideline in current code. |
| 1780 | `        if isinstance(node.children[0], MemberAccessNode) and node.value in {"++", "--"}:` | Checks a runtime condition. |
| 1781 | `            # LINE: Target is the member access node.` | Comment/guideline in current code. |
| 1782 | `            target = node.children[0]` | Stores or updates runtime state/value. |
| 1783 | `            # LINE: chain stores member names from nested access.` | Comment/guideline in current code. |
| 1784 | `            chain = []` | Stores or updates runtime state/value. |
| 1785 | `            # LINE: Start walking from the target access.` | Comment/guideline in current code. |
| 1786 | `            current = target` | Stores or updates runtime state/value. |
| 1787 | `            # LINE: Collect all member names until base object.` | Comment/guideline in current code. |
| 1788 | `            while isinstance(current, MemberAccessNode):` | Repeats while runtime condition is true. |
| 1789 | `                # AUTO: Appends a value to a list.` | Comment/guideline in current code. |
| 1790 | `                chain.append(current.children[1].value)` | Runtime support logic. |
| 1791 | `                # AUTO: Sets `current`.` | Comment/guideline in current code. |
| 1792 | `                current = current.children[0]` | Stores or updates runtime state/value. |
| 1793 | `            # LINE: Reverse so access starts from base object outward.` | Comment/guideline in current code. |
| 1794 | `            chain.reverse()` | Runtime support logic. |
| 1795 | `            # LINE: Base object variable name.` | Comment/guideline in current code. |
| 1796 | `            obj_name = current.value` | Stores or updates runtime state/value. |
| 1797 | `            # LINE: Look up base object variable.` | Comment/guideline in current code. |
| 1798 | `            var_info = self.lookup_variable(obj_name)` | Reads variable metadata/value from runtime scopes. |
| 1799 | `            # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1800 | `            if isinstance(var_info, str):` | Checks a runtime condition. |
| 1801 | `                # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 1802 | `                raise InterpreterError(var_info, node.line)` | Stops execution with a runtime error. |
| 1803 | `            # LINE: Get bundle dictionary value.` | Comment/guideline in current code. |
| 1804 | `            bundle_value = var_info["value"]` | Stores or updates runtime state/value. |
| 1805 | `            # LINE: Member increment requires bundle object.` | Comment/guideline in current code. |
| 1806 | `            if not isinstance(bundle_value, dict):` | Checks a runtime condition. |
| 1807 | `                # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 1808 | `                raise InterpreterError(f"Runtime Error: Variable '{obj_name}' is not a bundle.", node.line)` | Stops execution with a runtime error. |
| 1809 | `            # LINE: Navigate nested bundle path before final member.` | Comment/guideline in current code. |
| 1810 | `            for member in chain[:-1]:` | Loops through AST children/items. |
| 1811 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1812 | `                if member not in bundle_value:` | Checks a runtime condition. |
| 1813 | `                    # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 1814 | `                    raise InterpreterError(f"Runtime Error: Bundle has no member '{member}'.", node.line)` | Stops execution with a runtime error. |
| 1815 | `                # AUTO: Sets `bundle_value`.` | Comment/guideline in current code. |
| 1816 | `                bundle_value = bundle_value[member]` | Stores or updates runtime state/value. |
| 1817 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1818 | `                if not isinstance(bundle_value, dict):` | Checks a runtime condition. |
| 1819 | `                    # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 1820 | `                    raise InterpreterError(f"Runtime Error: Member '{member}' is not a bundle.", node.line)` | Stops execution with a runtime error. |
| 1821 | `            # LINE: Final member is incremented/decremented.` | Comment/guideline in current code. |
| 1822 | `            final_member = chain[-1]` | Stores or updates runtime state/value. |
| 1823 | `            # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1824 | `            if final_member not in bundle_value:` | Checks a runtime condition. |
| 1825 | `                # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 1826 | `                raise InterpreterError(f"Runtime Error: Bundle has no member '{final_member}'.", node.line)` | Stops execution with a runtime error. |
| 1827 | `            # LINE: Save old value for postfix result.` | Comment/guideline in current code. |
| 1828 | `            original = bundle_value[final_member]` | Stores or updates runtime state/value. |
| 1829 | `            # LINE: Compute new value depending on ++ or --.` | Comment/guideline in current code. |
| 1830 | `            new_value = original + 1 if node.value == "++" else original - 1` | Stores or updates runtime state/value. |
| 1831 | `            # LINE: Store updated value in bundle member.` | Comment/guideline in current code. |
| 1832 | `            bundle_value[final_member] = new_value` | Stores or updates runtime state/value. |
| 1833 | `            # LINE: Postfix returns old value, prefix returns new value.` | Comment/guideline in current code. |
| 1834 | `            return original if node.position == "post" else new_value` | Returns runtime value/result to caller. |
| 1835 | `` | Blank spacing line. |
| 1836 | `        # LINE: Simple variable unary path, not array/list access.` | Comment/guideline in current code. |
| 1837 | `        if not isinstance(node.children[0], ListAccessNode):` | Checks a runtime condition. |
| 1838 | `            # LINE: Operand node stores the variable/literal being changed.` | Comment/guideline in current code. |
| 1839 | `            operand_node = node.children[0]` | Stores or updates runtime state/value. |
| 1840 | `            # LINE: For ++/-- this is the variable name.` | Comment/guideline in current code. |
| 1841 | `            operand_name = operand_node.value` | Stores or updates runtime state/value. |
| 1842 | `            # LINE: Look up variable info dictionary.` | Comment/guideline in current code. |
| 1843 | `            var_info = self.lookup_variable(operand_name)` | Reads variable metadata/value from runtime scopes. |
| 1844 | `` | Blank spacing line. |
| 1845 | `            # LINE: Increment variable path.` | Comment/guideline in current code. |
| 1846 | `            if node.value == "++":` | Checks a runtime condition. |
| 1847 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1848 | `                if isinstance(var_info, str):` | Checks a runtime condition. |
| 1849 | `                    # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 1850 | `                    raise InterpreterError(var_info, node.line)` | Stops execution with a runtime error. |
| 1851 | `                # LINE: Prefix ++ updates first then returns new value.` | Comment/guideline in current code. |
| 1852 | `                if node.position == "pre":` | Checks a runtime condition. |
| 1853 | `                    # AUTO: Adds into `var_info["value"]`.` | Comment/guideline in current code. |
| 1854 | `                    var_info["value"] += 1` | Stores or updates runtime state/value. |
| 1855 | `                    # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1856 | `                    return var_info["value"]` | Returns runtime value/result to caller. |
| 1857 | `                # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 1858 | `                else:` | Fallback runtime branch. |
| 1859 | `                    # LINE: Postfix ++ returns old value then updates.` | Comment/guideline in current code. |
| 1860 | `                    original = var_info["value"]` | Stores or updates runtime state/value. |
| 1861 | `                    # AUTO: Adds into `var_info["value"]`.` | Comment/guideline in current code. |
| 1862 | `                    var_info["value"] += 1` | Stores or updates runtime state/value. |
| 1863 | `                    # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1864 | `                    return original` | Returns runtime value/result to caller. |
| 1865 | `` | Blank spacing line. |
| 1866 | `            # LINE: Decrement variable path.` | Comment/guideline in current code. |
| 1867 | `            elif node.value == "--":` | Alternative runtime condition. |
| 1868 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1869 | `                if isinstance(var_info, str):` | Checks a runtime condition. |
| 1870 | `                    # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 1871 | `                    raise InterpreterError(var_info, node.line)` | Stops execution with a runtime error. |
| 1872 | `                # LINE: Prefix -- updates first then returns new value.` | Comment/guideline in current code. |
| 1873 | `                if node.position == "pre":` | Checks a runtime condition. |
| 1874 | `                    # AUTO: Subtracts from `var_info["value"]`.` | Comment/guideline in current code. |
| 1875 | `                    var_info["value"] -= 1` | Stores or updates runtime state/value. |
| 1876 | `                    # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1877 | `                    return var_info["value"]` | Returns runtime value/result to caller. |
| 1878 | `                # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 1879 | `                else:` | Fallback runtime branch. |
| 1880 | `                    # LINE: Postfix -- returns old value then updates.` | Comment/guideline in current code. |
| 1881 | `                    original = var_info["value"]` | Stores or updates runtime state/value. |
| 1882 | `                    # AUTO: Subtracts from `var_info["value"]`.` | Comment/guideline in current code. |
| 1883 | `                    var_info["value"] -= 1` | Stores or updates runtime state/value. |
| 1884 | `                    # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1885 | `                    return original` | Returns runtime value/result to caller. |
| 1886 | `            ` | Blank spacing line. |
| 1887 | `            # LINE: Minus operator path.` | Comment/guideline in current code. |
| 1888 | `            elif node.value == "-":` | Alternative runtime condition. |
| 1889 | `                # LINE: Evaluate operand then negate it.` | Comment/guideline in current code. |
| 1890 | `                value = self.interpret(operand_node)` | Stores or updates runtime state/value. |
| 1891 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1892 | `                return -value` | Returns runtime value/result to caller. |
| 1893 | `` | Blank spacing line. |
| 1894 | `            # LINE: GAL negative operator path.` | Comment/guideline in current code. |
| 1895 | `            elif node.value == "~":` | Alternative runtime condition. |
| 1896 | `                # LINE: Evaluate operand then negate it.` | Comment/guideline in current code. |
| 1897 | `                value = self.interpret(operand_node)` | Stores or updates runtime state/value. |
| 1898 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1899 | `                return -value` | Returns runtime value/result to caller. |
| 1900 | `` | Blank spacing line. |
| 1901 | `            # LINE: Logical not path.` | Comment/guideline in current code. |
| 1902 | `            elif node.value == "!":` | Alternative runtime condition. |
| 1903 | `                # LINE: Evaluate operand then invert boolean truth.` | Comment/guideline in current code. |
| 1904 | `                value = self.interpret(operand_node)` | Stores or updates runtime state/value. |
| 1905 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1906 | `                return not value` | Returns runtime value/result to caller. |
| 1907 | `            ` | Blank spacing line. |
| 1908 | `        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 1909 | `        else:` | Fallback runtime branch. |
| 1910 | `            # LINE: Array/list element ++/-- path, like arr[i]++.` | Comment/guideline in current code. |
| 1911 | `            operand_node = node.children[0]` | Stores or updates runtime state/value. |
| 1912 | `            # LINE: Base list variable name.` | Comment/guideline in current code. |
| 1913 | `            list_name = operand_node.children[0].value` | Stores or updates runtime state/value. |
| 1914 | `            # LINE: Index node inside brackets.` | Comment/guideline in current code. |
| 1915 | `            index_node = operand_node.children[1]` | Stores or updates runtime state/value. |
| 1916 | `            # LINE: Evaluate index expression.` | Comment/guideline in current code. |
| 1917 | `            index = self.interpret(index_node.children[0])` | Stores or updates runtime state/value. |
| 1918 | `` | Blank spacing line. |
| 1919 | `            # LINE: Look up list variable.` | Comment/guideline in current code. |
| 1920 | `            list_entry = self.lookup_variable(list_name)` | Reads variable metadata/value from runtime scopes. |
| 1921 | `            # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 1922 | `            if isinstance(list_entry, str):` | Checks a runtime condition. |
| 1923 | `                # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 1924 | `                raise InterpreterError(list_entry, node.line)` | Stops execution with a runtime error. |
| 1925 | `` | Blank spacing line. |
| 1926 | `            # LINE: Get actual Python list value.` | Comment/guideline in current code. |
| 1927 | `            list_value = list_entry["value"]` | Stores or updates runtime state/value. |
| 1928 | `` | Blank spacing line. |
| 1929 | `            # LINE: Index must be integer.` | Comment/guideline in current code. |
| 1930 | `            if not isinstance(index, int):` | Checks a runtime condition. |
| 1931 | `                # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 1932 | `                raise InterpreterError(f"Runtime Error: List index must be an integer. Got '{index}'", node.line)` | Stops execution with a runtime error. |
| 1933 | `` | Blank spacing line. |
| 1934 | `            # LINE: Target variable must be a list.` | Comment/guideline in current code. |
| 1935 | `            if not isinstance(list_value, list):` | Checks a runtime condition. |
| 1936 | `                # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 1937 | `                raise InterpreterError(f"Runtime Error: Variable '{list_name}' is not a list.", node.line)` | Stops execution with a runtime error. |
| 1938 | `` | Blank spacing line. |
| 1939 | `            # LINE: Check index bounds.` | Comment/guideline in current code. |
| 1940 | `            if index < 0 or index >= len(list_value):` | Checks a runtime condition. |
| 1941 | `                # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 1942 | `                raise InterpreterError(f"Runtime Error: Index '{index}' out of bounds for list '{list_name}'.", node.line)` | Stops execution with a runtime error. |
| 1943 | `` | Blank spacing line. |
| 1944 | `            # LINE: Increment array element.` | Comment/guideline in current code. |
| 1945 | `            if node.value == "++":` | Checks a runtime condition. |
| 1946 | `                # AUTO: Sets `original`.` | Comment/guideline in current code. |
| 1947 | `                original = list_value[index]` | Stores or updates runtime state/value. |
| 1948 | `                # AUTO: Adds into `list_value[index]`.` | Comment/guideline in current code. |
| 1949 | `                list_value[index] += 1` | Stores or updates runtime state/value. |
| 1950 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1951 | `                return original if node.position == "post" else list_value[index]` | Returns runtime value/result to caller. |
| 1952 | `` | Blank spacing line. |
| 1953 | `            # LINE: Decrement array element.` | Comment/guideline in current code. |
| 1954 | `            elif node.value == "--":` | Alternative runtime condition. |
| 1955 | `                # AUTO: Sets `original`.` | Comment/guideline in current code. |
| 1956 | `                original = list_value[index]` | Stores or updates runtime state/value. |
| 1957 | `                # AUTO: Subtracts from `list_value[index]`.` | Comment/guideline in current code. |
| 1958 | `                list_value[index] -= 1` | Stores or updates runtime state/value. |
| 1959 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1960 | `                return original if node.position == "post" else list_value[index]` | Returns runtime value/result to caller. |
| 1961 | `` | Blank spacing line. |
| 1962 | `        ` | Blank spacing line. |
| 1963 | `        # LINE: If no unary branch matched, this operator is unsupported.` | Comment/guideline in current code. |
| 1964 | `        raise InterpreterError(f"Unknown unary operator {node.value}", node.line)` | Stops execution with a runtime error. |
| 1965 | `    ` | Blank spacing line. |
| 1966 | `    # AUTO: Defines function `eval_cast`.` | Comment/guideline in current code. |
| 1967 | `    def eval_cast(self, node):` | Starts a node-specific runtime evaluator. |
| 1968 | `        # LINE: Second child is the expression being converted.` | Comment/guideline in current code. |
| 1969 | `        value = self.interpret(node.children[1])` | Stores or updates runtime state/value. |
| 1970 | `        # LINE: First child stores target cast type.` | Comment/guideline in current code. |
| 1971 | `        cast_type = node.children[0].value` | Stores or updates runtime state/value. |
| 1972 | `` | Blank spacing line. |
| 1973 | `        # LINE: Convert value to seed/int.` | Comment/guideline in current code. |
| 1974 | `        if cast_type == "seed":` | Checks a runtime condition. |
| 1975 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1976 | `            return int(value)` | Returns runtime value/result to caller. |
| 1977 | `        # LINE: Convert value to tree/float.` | Comment/guideline in current code. |
| 1978 | `        elif cast_type == "tree":` | Alternative runtime condition. |
| 1979 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1980 | `            return float(value)` | Returns runtime value/result to caller. |
| 1981 | `        # LINE: Convert value to leaf/character.` | Comment/guideline in current code. |
| 1982 | `        elif cast_type == "leaf":` | Alternative runtime condition. |
| 1983 | `            # LINE: Integer leaf cast uses character code.` | Comment/guideline in current code. |
| 1984 | `            if isinstance(value, int):` | Checks a runtime condition. |
| 1985 | `                # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1986 | `                return chr(value)` | Returns runtime value/result to caller. |
| 1987 | `            # LINE: String leaf cast takes first character or null char.` | Comment/guideline in current code. |
| 1988 | `            return str(value)[0] if value else '\0'` | Returns runtime value/result to caller. |
| 1989 | `        # LINE: Convert value to branch/bool.` | Comment/guideline in current code. |
| 1990 | `        elif cast_type == "branch":` | Alternative runtime condition. |
| 1991 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1992 | `            return bool(value)` | Returns runtime value/result to caller. |
| 1993 | `        # LINE: Convert value to vine/string.` | Comment/guideline in current code. |
| 1994 | `        elif cast_type == "vine":` | Alternative runtime condition. |
| 1995 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 1996 | `            return str(value)` | Returns runtime value/result to caller. |
| 1997 | `        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 1998 | `        else:` | Fallback runtime branch. |
| 1999 | `            # LINE: Unknown target type is runtime error.` | Comment/guideline in current code. |
| 2000 | `            raise InterpreterError(f"Unknown cast type: {cast_type}", node.line)` | Stops execution with a runtime error. |
| 2001 | `` | Blank spacing line. |
| 2002 | `` | Blank spacing line. |
| 2003 | `    # AUTO: Defines function `eval_soil`.` | Comment/guideline in current code. |
| 2004 | `    def eval_soil(self, node):` | Starts a node-specific runtime evaluator. |
| 2005 | `        # LINE: First child is the variable whose value will be lowercased.` | Comment/guideline in current code. |
| 2006 | `        var_name = node.children[0].value` | Stores or updates runtime state/value. |
| 2007 | `        # LINE: Look up the variable entry.` | Comment/guideline in current code. |
| 2008 | `        var_info = self.lookup_variable(var_name)` | Reads variable metadata/value from runtime scopes. |
| 2009 | `        # LINE: Return lowercase version of the stored value.` | Comment/guideline in current code. |
| 2010 | `        return var_info["value"].lower()  # type: ignore` | Returns runtime value/result to caller. |
| 2011 | `` | Blank spacing line. |
| 2012 | `    # AUTO: Defines function `eval_bloom`.` | Comment/guideline in current code. |
| 2013 | `    def eval_bloom(self, node):` | Starts a node-specific runtime evaluator. |
| 2014 | `        # LINE: First child is the variable whose value will be uppercased.` | Comment/guideline in current code. |
| 2015 | `        var_name = node.children[0].value` | Stores or updates runtime state/value. |
| 2016 | `        # LINE: Look up the variable entry.` | Comment/guideline in current code. |
| 2017 | `        var_info = self.lookup_variable(var_name)` | Reads variable metadata/value from runtime scopes. |
| 2018 | `        # LINE: Return uppercase version of the stored value.` | Comment/guideline in current code. |
| 2019 | `        return var_info["value"].upper()  # type: ignore` | Returns runtime value/result to caller. |
| 2020 | `` | Blank spacing line. |
| 2021 | `    # AUTO: Defines function `eval_if_statement`.` | Comment/guideline in current code. |
| 2022 | `    def eval_if_statement(self, node):` | Starts a node-specific runtime evaluator. |
| 2023 | `        # LINE: Evaluate spring condition from first child.` | Comment/guideline in current code. |
| 2024 | `        condition_result = self.interpret(node.children[0].children[0])` | Stores or updates runtime state/value. |
| 2025 | `        # LINE: Create local scope for this if/else chain.` | Comment/guideline in current code. |
| 2026 | `        self.enter_scope()` | Enters a new local runtime scope. |
| 2027 | `` | Blank spacing line. |
| 2028 | `` | Blank spacing line. |
| 2029 | `        # AUTO: Starts protected code that can catch errors.` | Comment/guideline in current code. |
| 2030 | `        try:` | Starts protected block for optional runtime dependency or error handling. |
| 2031 | `            # LINE: If spring condition is True, run spring block.` | Comment/guideline in current code. |
| 2032 | `            if condition_result:` | Checks a runtime condition. |
| 2033 | `                # AUTO: Calls `self.eval_block`.` | Comment/guideline in current code. |
| 2034 | `                self.eval_block(node.children[1])` | Runtime support logic. |
| 2035 | `            ` | Blank spacing line. |
| 2036 | `            # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 2037 | `            else:` | Fallback runtime branch. |
| 2038 | `                # LINE: Start checking children after spring condition/block.` | Comment/guideline in current code. |
| 2039 | `                current_node = 2` | Stores or updates runtime state/value. |
| 2040 | `                # LINE: Walk bud/wither nodes until one runs or list ends.` | Comment/guideline in current code. |
| 2041 | `                while current_node < len(node.children):` | Repeats while runtime condition is true. |
| 2042 | `                    ` | Blank spacing line. |
| 2043 | `                    # LINE: Current child can be ElseIfStatement or ElseStatement.` | Comment/guideline in current code. |
| 2044 | `                    elif_node = node.children[current_node]` | Stores or updates runtime state/value. |
| 2045 | `` | Blank spacing line. |
| 2046 | `                    # LINE: bud condition path.` | Comment/guideline in current code. |
| 2047 | `                    if elif_node.node_type == "ElseIfStatement":` | Checks a runtime condition. |
| 2048 | `                        # LINE: Evaluate bud condition.` | Comment/guideline in current code. |
| 2049 | `                        elif_condition_result = self.interpret(elif_node.children[0].children[0])` | Stores or updates runtime state/value. |
| 2050 | `` | Blank spacing line. |
| 2051 | `                        # LINE: bud condition must be branch/bool.` | Comment/guideline in current code. |
| 2052 | `                        if not isinstance(elif_condition_result, bool):` | Checks a runtime condition. |
| 2053 | `                            # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 2054 | `                            raise InterpreterError(f"Runtime Error: Condition must be a boolean. Got '{condition_result}'", node.line)` | Stops execution with a runtime error. |
| 2055 | `                        ` | Blank spacing line. |
| 2056 | `                        # LINE: If bud is true, run its block and stop the chain.` | Comment/guideline in current code. |
| 2057 | `                        if elif_condition_result:` | Checks a runtime condition. |
| 2058 | `                            # AUTO: Starts protected code that can catch errors.` | Comment/guideline in current code. |
| 2059 | `                            try:` | Starts protected block for optional runtime dependency or error handling. |
| 2060 | `                                # LINE: bud block gets its own local scope.` | Comment/guideline in current code. |
| 2061 | `                                self.enter_scope()` | Enters a new local runtime scope. |
| 2062 | `                                # LINE: Execute bud block.` | Comment/guideline in current code. |
| 2063 | `                                self.eval_block(elif_node.children[1])` | Runtime support logic. |
| 2064 | `                            # AUTO: Runs cleanup code no matter what happened.` | Comment/guideline in current code. |
| 2065 | `                            finally:` | Runs cleanup even if reclaim/error happens. |
| 2066 | `                                # LINE: Leave bud local scope.` | Comment/guideline in current code. |
| 2067 | `                                self.exit_scope()` | Leaves current runtime scope. |
| 2068 | `                            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 2069 | `                            return` | Runtime support logic. |
| 2070 | `                        ` | Blank spacing line. |
| 2071 | `                    # LINE: wither/else path.` | Comment/guideline in current code. |
| 2072 | `                    elif elif_node.node_type == "ElseStatement":` | Alternative runtime condition. |
| 2073 | `                        # AUTO: Starts protected code that can catch errors.` | Comment/guideline in current code. |
| 2074 | `                        try:` | Starts protected block for optional runtime dependency or error handling. |
| 2075 | `                            # LINE: wither block gets its own local scope.` | Comment/guideline in current code. |
| 2076 | `                            self.enter_scope()` | Enters a new local runtime scope. |
| 2077 | `                            # LINE: Execute wither block.` | Comment/guideline in current code. |
| 2078 | `                            self.eval_block(elif_node.children[0])` | Runtime support logic. |
| 2079 | `                        # AUTO: Runs cleanup code no matter what happened.` | Comment/guideline in current code. |
| 2080 | `                        finally:` | Runs cleanup even if reclaim/error happens. |
| 2081 | `                            # LINE: Leave wither local scope.` | Comment/guideline in current code. |
| 2082 | `                            self.exit_scope()` | Leaves current runtime scope. |
| 2083 | `                        # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 2084 | `                        return` | Runtime support logic. |
| 2085 | `` | Blank spacing line. |
| 2086 | `                    # LINE: Move to next bud/wither child.` | Comment/guideline in current code. |
| 2087 | `                    current_node += 1` | Stores or updates runtime state/value. |
| 2088 | `        # AUTO: Runs cleanup code no matter what happened.` | Comment/guideline in current code. |
| 2089 | `        finally:` | Runs cleanup even if reclaim/error happens. |
| 2090 | `            # LINE: Always leave spring chain scope.` | Comment/guideline in current code. |
| 2091 | `            self.exit_scope()` | Leaves current runtime scope. |
| 2092 | `` | Blank spacing line. |
| 2093 | `        # LINE: If no block ran, return no value.` | Comment/guideline in current code. |
| 2094 | `        return None` | Returns runtime value/result to caller. |
| 2095 | `    ` | Blank spacing line. |
| 2096 | `    # AUTO: Defines function `eval_for_loop`.` | Comment/guideline in current code. |
| 2097 | `    def eval_for_loop(self, node):` | Starts a node-specific runtime evaluator. |
| 2098 | `        # GUIDE: cultivate flow; initialize once, check condition, run block,` | Comment/guideline in current code. |
| 2099 | `        # apply update expressions, then repeat.` | Comment/guideline in current code. |
| 2100 | `        # LINE: Mark that execution is inside a cultivate loop.` | Comment/guideline in current code. |
| 2101 | `        self.enter_loop('for')` | Runtime support logic. |
| 2102 | `        # LINE: Create loop-local scope.` | Comment/guideline in current code. |
| 2103 | `        self.enter_scope()` | Enters a new local runtime scope. |
| 2104 | `        # LINE: Safety limit to prevent infinite loops.` | Comment/guideline in current code. |
| 2105 | `        MAX_LOOP_ITERATIONS = 10000` | Infinite-loop guard limit. |
| 2106 | `        # LINE: Counts how many loop iterations already ran.` | Comment/guideline in current code. |
| 2107 | `        LOOP_COUNTER = 0` | Counts loop iterations to detect infinite loops. |
| 2108 | `` | Blank spacing line. |
| 2109 | `        # AUTO: Starts protected code that can catch errors.` | Comment/guideline in current code. |
| 2110 | `        try:` | Starts protected block for optional runtime dependency or error handling. |
| 2111 | `            # LINE: First child is the initializer part of cultivate.` | Comment/guideline in current code. |
| 2112 | `            instantiate_node = node.children[0]` | Stores or updates runtime state/value. |
| 2113 | `` | Blank spacing line. |
| 2114 | `            # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 2115 | `            if isinstance(instantiate_node, VariableDeclarationNode):` | Checks a runtime condition. |
| 2116 | `                # First part of cultivate: seed i = 0` | Comment/guideline in current code. |
| 2117 | `                # AUTO: Sets `var_type`.` | Comment/guideline in current code. |
| 2118 | `                var_type = instantiate_node.children[0].value` | Stores or updates runtime state/value. |
| 2119 | `                # AUTO: Sets `var_name`.` | Comment/guideline in current code. |
| 2120 | `                var_name = instantiate_node.children[1].value` | Stores or updates runtime state/value. |
| 2121 | `                # AUTO: Sets `initial_value_node`.` | Comment/guideline in current code. |
| 2122 | `                initial_value_node = self.interpret(instantiate_node.children[2])` | Stores or updates runtime state/value. |
| 2123 | `                # AUTO: Calls `self.declare_variable`.` | Comment/guideline in current code. |
| 2124 | `                self.declare_variable(var_name, var_type, initial_value_node)` | Creates a variable in current runtime scope. |
| 2125 | `` | Blank spacing line. |
| 2126 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 2127 | `            elif isinstance(instantiate_node, AssignmentNode):` | Alternative runtime condition. |
| 2128 | `                # First part of cultivate: i = 0` | Comment/guideline in current code. |
| 2129 | `                # AUTO: Sets `var_name`.` | Comment/guideline in current code. |
| 2130 | `                var_name = instantiate_node.children[0].value` | Stores or updates runtime state/value. |
| 2131 | `                # AUTO: Sets `initial_value_node`.` | Comment/guideline in current code. |
| 2132 | `                initial_value_node = self.interpret(instantiate_node.children[1])` | Stores or updates runtime state/value. |
| 2133 | `                # AUTO: Sets `self.lookup_variable(var_name)["value"]`.` | Comment/guideline in current code. |
| 2134 | `                self.lookup_variable(var_name)["value"] = initial_value_node  # type: ignore` | Reads variable metadata/value from runtime scopes. |
| 2135 | `` | Blank spacing line. |
| 2136 | `            # LINE: Second child is the loop condition.` | Comment/guideline in current code. |
| 2137 | `            condition_node = node.children[1].children[0]` | Stores or updates runtime state/value. |
| 2138 | `            # Second part of cultivate: evaluate condition such as i <= n.` | Comment/guideline in current code. |
| 2139 | `            # LINE: Evaluate condition before the first iteration.` | Comment/guideline in current code. |
| 2140 | `            condition_result = self.interpret(condition_node)` | Stores or updates runtime state/value. |
| 2141 | `` | Blank spacing line. |
| 2142 | `            # LINE: Loop condition must evaluate to branch/bool.` | Comment/guideline in current code. |
| 2143 | `            if not isinstance(condition_result, bool):` | Checks a runtime condition. |
| 2144 | `                # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 2145 | `                raise InterpreterError(f"Runtime Error: Condition must be a boolean. Got '{condition_result}'", node.line)` | Stops execution with a runtime error. |
| 2146 | `` | Blank spacing line. |
| 2147 | `            # LINE: Keep running while condition is sunshine/True.` | Comment/guideline in current code. |
| 2148 | `            while condition_result:` | Repeats while runtime condition is true. |
| 2149 | `                # AUTO: Adds into `LOOP_COUNTER`.` | Comment/guideline in current code. |
| 2150 | `                LOOP_COUNTER += 1` | Counts loop iterations to detect infinite loops. |
| 2151 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 2152 | `                if LOOP_COUNTER > MAX_LOOP_ITERATIONS:` | Infinite-loop guard limit. |
| 2153 | `                    # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 2154 | `                    raise InterpreterError("Runtime Error: Infinite loop detected!", node.line)` | Stops execution with a runtime error. |
| 2155 | `` | Blank spacing line. |
| 2156 | `                # LINE: Execute the loop body block.` | Comment/guideline in current code. |
| 2157 | `                self.eval_block(node.children[3])` | Runtime support logic. |
| 2158 | `` | Blank spacing line. |
| 2159 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 2160 | `                if self.continue_flag:` | Checks a runtime condition. |
| 2161 | `                    # LINE: skip clears here before updates/next condition.` | Comment/guideline in current code. |
| 2162 | `                    self.continue_flag = False  ` | Stores or updates runtime state/value. |
| 2163 | `` | Blank spacing line. |
| 2164 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 2165 | `                if self.break_triggered():` | Checks a runtime condition. |
| 2166 | `                    # LINE: prune stops the loop immediately.` | Comment/guideline in current code. |
| 2167 | `                    break` | Stops nearest loop. |
| 2168 | `                ` | Blank spacing line. |
| 2169 | `                # LINE: Run update expressions after each iteration.` | Comment/guideline in current code. |
| 2170 | `                for update_expr in node.children[2].children:` | Loops through AST children/items. |
| 2171 | `                    # Third part of cultivate: apply update such as i++.` | Comment/guideline in current code. |
| 2172 | `                    # AUTO: Dispatches an AST node for execution.` | Comment/guideline in current code. |
| 2173 | `                    self.interpret(update_expr)` | Runtime support logic. |
| 2174 | `` | Blank spacing line. |
| 2175 | `                # Re-check the loop condition for the next iteration.` | Comment/guideline in current code. |
| 2176 | `                # LINE: Re-evaluate condition to decide if loop continues.` | Comment/guideline in current code. |
| 2177 | `                condition_result = self.interpret(condition_node)` | Stores or updates runtime state/value. |
| 2178 | `` | Blank spacing line. |
| 2179 | `        # AUTO: Runs cleanup code no matter what happened.` | Comment/guideline in current code. |
| 2180 | `        finally:` | Runs cleanup even if reclaim/error happens. |
| 2181 | `            # LINE: Always remove loop scope after loop ends/errors.` | Comment/guideline in current code. |
| 2182 | `            self.exit_scope()` | Leaves current runtime scope. |
| 2183 | `            # LINE: Always clear loop tracking after loop ends/errors.` | Comment/guideline in current code. |
| 2184 | `            self.exit_loop()` | Runtime support logic. |
| 2185 | `` | Blank spacing line. |
| 2186 | `` | Blank spacing line. |
| 2187 | `    # AUTO: Defines function `eval_while_loop`.` | Comment/guideline in current code. |
| 2188 | `    def eval_while_loop(self, node):` | Starts a node-specific runtime evaluator. |
| 2189 | `        # GUIDE: grow checks the branch condition before each block execution.` | Comment/guideline in current code. |
| 2190 | `        # LINE: Mark that execution is inside a grow loop.` | Comment/guideline in current code. |
| 2191 | `        self.enter_loop('while')` | Runtime support logic. |
| 2192 | `        # LINE: Create local loop scope.` | Comment/guideline in current code. |
| 2193 | `        self.enter_scope()` | Enters a new local runtime scope. |
| 2194 | `        # LINE: Safety limit to avoid infinite grow loops.` | Comment/guideline in current code. |
| 2195 | `        MAX_LOOP_ITERATIONS = 10000` | Infinite-loop guard limit. |
| 2196 | `        # LINE: Count loop iterations.` | Comment/guideline in current code. |
| 2197 | `        LOOP_COUNTER = 0` | Counts loop iterations to detect infinite loops. |
| 2198 | `        # LINE: First child stores grow condition expression.` | Comment/guideline in current code. |
| 2199 | `        condition_node = node.children[0].children[0]` | Stores or updates runtime state/value. |
| 2200 | `` | Blank spacing line. |
| 2201 | `        # AUTO: Starts protected code that can catch errors.` | Comment/guideline in current code. |
| 2202 | `        try:` | Starts protected block for optional runtime dependency or error handling. |
| 2203 | `            # Evaluate grow(condition) before the first iteration.` | Comment/guideline in current code. |
| 2204 | `            # LINE: Evaluate condition before entering body.` | Comment/guideline in current code. |
| 2205 | `            condition_result = self.interpret(condition_node)` | Stores or updates runtime state/value. |
| 2206 | `` | Blank spacing line. |
| 2207 | `            # LINE: grow condition must be branch/bool.` | Comment/guideline in current code. |
| 2208 | `            if not isinstance(condition_result, bool):` | Checks a runtime condition. |
| 2209 | `                # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 2210 | `                raise InterpreterError(f"Runtime Error: Condition must be a boolean. Got '{condition_result}'", node.line)` | Stops execution with a runtime error. |
| 2211 | `` | Blank spacing line. |
| 2212 | `            # LINE: Continue loop while condition is sunshine/True.` | Comment/guideline in current code. |
| 2213 | `            while condition_result:` | Repeats while runtime condition is true. |
| 2214 | `                # AUTO: Adds into `LOOP_COUNTER`.` | Comment/guideline in current code. |
| 2215 | `                LOOP_COUNTER += 1` | Counts loop iterations to detect infinite loops. |
| 2216 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 2217 | `                if LOOP_COUNTER > MAX_LOOP_ITERATIONS:` | Infinite-loop guard limit. |
| 2218 | `                    # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 2219 | `                    raise InterpreterError("Runtime Error: Infinite loop detected!", node.line)` | Stops execution with a runtime error. |
| 2220 | `` | Blank spacing line. |
| 2221 | `                # LINE: Second child is the grow body block.` | Comment/guideline in current code. |
| 2222 | `                block_node = node.children[1]` | Stores or updates runtime state/value. |
| 2223 | `                # LINE: Execute grow body once.` | Comment/guideline in current code. |
| 2224 | `                self.eval_block(block_node)` | Runtime support logic. |
| 2225 | `` | Blank spacing line. |
| 2226 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 2227 | `                if self.continue_flag:` | Checks a runtime condition. |
| 2228 | `                    # LINE: skip resets before next condition check.` | Comment/guideline in current code. |
| 2229 | `                    self.continue_flag = False` | Stores or updates runtime state/value. |
| 2230 | `` | Blank spacing line. |
| 2231 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 2232 | `                if self.break_triggered():` | Checks a runtime condition. |
| 2233 | `                    # LINE: prune exits the grow loop.` | Comment/guideline in current code. |
| 2234 | `                    break` | Stops nearest loop. |
| 2235 | `` | Blank spacing line. |
| 2236 | `                # Re-evaluate the condition after the block. If false, loop stops.` | Comment/guideline in current code. |
| 2237 | `                # LINE: Check condition again after the body.` | Comment/guideline in current code. |
| 2238 | `                condition_result = self.interpret(condition_node)` | Stores or updates runtime state/value. |
| 2239 | `` | Blank spacing line. |
| 2240 | `        # AUTO: Runs cleanup code no matter what happened.` | Comment/guideline in current code. |
| 2241 | `        finally:` | Runs cleanup even if reclaim/error happens. |
| 2242 | `            # LINE: Clear loop tracking.` | Comment/guideline in current code. |
| 2243 | `            self.exit_loop()` | Runtime support logic. |
| 2244 | `            # LINE: Remove loop-local scope.` | Comment/guideline in current code. |
| 2245 | `            self.exit_scope()` | Leaves current runtime scope. |
| 2246 | `` | Blank spacing line. |
| 2247 | `` | Blank spacing line. |
| 2248 | `    # AUTO: Defines function `eval_do_while_loop`.` | Comment/guideline in current code. |
| 2249 | `    def eval_do_while_loop(self, node):` | Starts a node-specific runtime evaluator. |
| 2250 | `        # AUTO: Calls `self.enter_loop`.` | Comment/guideline in current code. |
| 2251 | `        self.enter_loop('do-while')` | Runtime support logic. |
| 2252 | `        # AUTO: Sets `MAX_LOOP_ITERATIONS`.` | Comment/guideline in current code. |
| 2253 | `        MAX_LOOP_ITERATIONS = 10000` | Infinite-loop guard limit. |
| 2254 | `        # AUTO: Sets `LOOP_COUNTER`.` | Comment/guideline in current code. |
| 2255 | `        LOOP_COUNTER = 0` | Counts loop iterations to detect infinite loops. |
| 2256 | `        # AUTO: Sets `condition_node`.` | Comment/guideline in current code. |
| 2257 | `        condition_node = node.children[1].children[0]` | Stores or updates runtime state/value. |
| 2258 | `        # AUTO: Sets `block_node`.` | Comment/guideline in current code. |
| 2259 | `        block_node = node.children[0]` | Stores or updates runtime state/value. |
| 2260 | `` | Blank spacing line. |
| 2261 | `        # AUTO: Starts protected code that can catch errors.` | Comment/guideline in current code. |
| 2262 | `        try:` | Starts protected block for optional runtime dependency or error handling. |
| 2263 | `            # AUTO: Repeats while this condition is true.` | Comment/guideline in current code. |
| 2264 | `            while True:` | Repeats while runtime condition is true. |
| 2265 | `                # AUTO: Calls `self.eval_block`.` | Comment/guideline in current code. |
| 2266 | `                self.eval_block(block_node)` | Runtime support logic. |
| 2267 | `                # AUTO: Adds into `LOOP_COUNTER`.` | Comment/guideline in current code. |
| 2268 | `                LOOP_COUNTER += 1` | Counts loop iterations to detect infinite loops. |
| 2269 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 2270 | `                if LOOP_COUNTER > MAX_LOOP_ITERATIONS:` | Infinite-loop guard limit. |
| 2271 | `                    # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 2272 | `                    raise InterpreterError("Runtime Error: Infinite loop detected!", node.line)` | Stops execution with a runtime error. |
| 2273 | `` | Blank spacing line. |
| 2274 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 2275 | `                if self.continue_flag:` | Checks a runtime condition. |
| 2276 | `                    # AUTO: Sets `self.continue_flag`.` | Comment/guideline in current code. |
| 2277 | `                    self.continue_flag = False` | Stores or updates runtime state/value. |
| 2278 | `` | Blank spacing line. |
| 2279 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 2280 | `                if self.break_triggered():` | Checks a runtime condition. |
| 2281 | `                    # AUTO: Stops the nearest loop.` | Comment/guideline in current code. |
| 2282 | `                    break` | Stops nearest loop. |
| 2283 | `` | Blank spacing line. |
| 2284 | `                # AUTO: Sets `condition_result`.` | Comment/guideline in current code. |
| 2285 | `                condition_result = self.interpret(condition_node)` | Stores or updates runtime state/value. |
| 2286 | `` | Blank spacing line. |
| 2287 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 2288 | `                if not isinstance(condition_result, bool):` | Checks a runtime condition. |
| 2289 | `                    # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 2290 | `                    raise InterpreterError(f"Runtime Error: Condition must be a boolean. Got '{condition_result}'", node.line)` | Stops execution with a runtime error. |
| 2291 | `` | Blank spacing line. |
| 2292 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 2293 | `                if not condition_result:` | Checks a runtime condition. |
| 2294 | `                    # AUTO: Stops the nearest loop.` | Comment/guideline in current code. |
| 2295 | `                    break` | Stops nearest loop. |
| 2296 | `        # AUTO: Runs cleanup code no matter what happened.` | Comment/guideline in current code. |
| 2297 | `        finally:` | Runs cleanup even if reclaim/error happens. |
| 2298 | `            # AUTO: Calls `self.exit_loop`.` | Comment/guideline in current code. |
| 2299 | `            self.exit_loop()` | Runtime support logic. |
| 2300 | `` | Blank spacing line. |
| 2301 | `    ` | Blank spacing line. |
| 2302 | `    # AUTO: Defines function `eval_break`.` | Comment/guideline in current code. |
| 2303 | `    def eval_break(self, node):` | Starts a node-specific runtime evaluator. |
| 2304 | `        # LINE: prune is legal only when loop_stack is not empty.` | Comment/guideline in current code. |
| 2305 | `        if self.loop_stack:` | Checks a runtime condition. |
| 2306 | `            # LINE: Set break flag so the loop can stop.` | Comment/guideline in current code. |
| 2307 | `            self.trigger_break()` | Runtime support logic. |
| 2308 | `        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 2309 | `        else:` | Fallback runtime branch. |
| 2310 | `            # LINE: Using prune outside loop/switch is a runtime error.` | Comment/guideline in current code. |
| 2311 | `            raise InterpreterError("Runtime Error: Break statement used outside of a loop", node.line)` | Stops execution with a runtime error. |
| 2312 | `` | Blank spacing line. |
| 2313 | `    # AUTO: Defines function `trigger_break`.` | Comment/guideline in current code. |
| 2314 | `    def trigger_break(self):` | Starts helper that marks prune/break flag. |
| 2315 | `        # LINE: Mark that current loop should stop.` | Comment/guideline in current code. |
| 2316 | `        self.break_flag = True` | Stores or updates runtime state/value. |
| 2317 | `` | Blank spacing line. |
| 2318 | `    # AUTO: Defines function `break_triggered`.` | Comment/guideline in current code. |
| 2319 | `    def break_triggered(self):` | Starts helper that reads break flag. |
| 2320 | `        # LINE: Return whether prune was triggered.` | Comment/guideline in current code. |
| 2321 | `        return self.break_flag` | Returns runtime value/result to caller. |
| 2322 | `` | Blank spacing line. |
| 2323 | `    # AUTO: Defines function `enter_loop`.` | Comment/guideline in current code. |
| 2324 | `    def enter_loop(self, loop_type):` | Starts helper that marks loop context. |
| 2325 | `        # LINE: Push loop type so prune/skip know we are inside a loop/switch.` | Comment/guideline in current code. |
| 2326 | `        self.loop_stack.append(loop_type)` | Runtime support logic. |
| 2327 | `        # LINE: Reset prune flag for new loop.` | Comment/guideline in current code. |
| 2328 | `        self.break_flag = False` | Stores or updates runtime state/value. |
| 2329 | `        # LINE: Reset skip flag for new loop.` | Comment/guideline in current code. |
| 2330 | `        self.continue_flag = False` | Stores or updates runtime state/value. |
| 2331 | `` | Blank spacing line. |
| 2332 | `    # AUTO: Defines function `exit_loop`.` | Comment/guideline in current code. |
| 2333 | `    def exit_loop(self):` | Starts helper that exits loop context. |
| 2334 | `        # LINE: Only pop when a loop/switch context exists.` | Comment/guideline in current code. |
| 2335 | `        if self.loop_stack:` | Checks a runtime condition. |
| 2336 | `            # LINE: Remove current loop/switch context.` | Comment/guideline in current code. |
| 2337 | `            self.loop_stack.pop()` | Runtime support logic. |
| 2338 | `            # LINE: Clear prune after leaving loop.` | Comment/guideline in current code. |
| 2339 | `            self.break_flag = False` | Stores or updates runtime state/value. |
| 2340 | `            # LINE: Clear skip after leaving loop.` | Comment/guideline in current code. |
| 2341 | `            self.continue_flag = False` | Stores or updates runtime state/value. |
| 2342 | `` | Blank spacing line. |
| 2343 | `    # AUTO: Defines function `eval_continue`.` | Comment/guideline in current code. |
| 2344 | `    def eval_continue(self, node):` | Starts a node-specific runtime evaluator. |
| 2345 | `        # LINE: skip is legal only inside a loop.` | Comment/guideline in current code. |
| 2346 | `        if self.loop_stack:` | Checks a runtime condition. |
| 2347 | `            # LINE: Set skip flag.` | Comment/guideline in current code. |
| 2348 | `            self.trigger_continue()` | Runtime support logic. |
| 2349 | `        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 2350 | `        else:` | Fallback runtime branch. |
| 2351 | `            # LINE: skip outside loop is runtime error.` | Comment/guideline in current code. |
| 2352 | `            raise InterpreterError("Runtime Error: Continue statement used outside of a loop", node.line)` | Stops execution with a runtime error. |
| 2353 | `` | Blank spacing line. |
| 2354 | `    # AUTO: Defines function `continue_triggered`.` | Comment/guideline in current code. |
| 2355 | `    def continue_triggered(self):` | Starts helper that reads continue flag. |
| 2356 | `        # LINE: Return whether skip was triggered.` | Comment/guideline in current code. |
| 2357 | `        return self.continue_flag` | Returns runtime value/result to caller. |
| 2358 | `` | Blank spacing line. |
| 2359 | `    # AUTO: Defines function `trigger_continue`.` | Comment/guideline in current code. |
| 2360 | `    def trigger_continue(self):` | Starts helper that marks continue flag. |
| 2361 | `        # LINE: Mark that current loop should skip to next iteration.` | Comment/guideline in current code. |
| 2362 | `        self.continue_flag = True` | Stores or updates runtime state/value. |
| 2363 | `` | Blank spacing line. |
| 2364 | `` | Blank spacing line. |
| 2365 | `    # AUTO: Defines function `eval_switch`.` | Comment/guideline in current code. |
| 2366 | `    def eval_switch(self, node):` | Starts a node-specific runtime evaluator. |
| 2367 | `        # LINE: harvest behaves like a switch context for prune.` | Comment/guideline in current code. |
| 2368 | `        self.enter_loop('switch')` | Runtime support logic. |
| 2369 | `        # LINE: Create local scope for switch execution.` | Comment/guideline in current code. |
| 2370 | `        self.enter_scope()` | Enters a new local runtime scope. |
| 2371 | `        # LINE: First child is the switch expression.` | Comment/guideline in current code. |
| 2372 | `        switch_expr_node = node.children[0]` | Stores or updates runtime state/value. |
| 2373 | `        # LINE: Evaluate switch expression once.` | Comment/guideline in current code. |
| 2374 | `        switch_value = self.interpret(switch_expr_node)` | Stores or updates runtime state/value. |
| 2375 | `` | Blank spacing line. |
| 2376 | `        # LINE: Tracks if a matching variety case has been found.` | Comment/guideline in current code. |
| 2377 | `        matched_case = False` | Stores or updates runtime state/value. |
| 2378 | `        # LINE: Tracks if prune stopped case execution.` | Comment/guideline in current code. |
| 2379 | `        break_found = False` | Stops nearest loop. |
| 2380 | `        # LINE: Stores soil/default block if present.` | Comment/guideline in current code. |
| 2381 | `        default_case = None` | Stores or updates runtime state/value. |
| 2382 | `` | Blank spacing line. |
| 2383 | `        # AUTO: Starts protected code that can catch errors.` | Comment/guideline in current code. |
| 2384 | `        try:` | Starts protected block for optional runtime dependency or error handling. |
| 2385 | `            # LINE: Visit every variety/soil child after switch expression.` | Comment/guideline in current code. |
| 2386 | `            for case_node in node.children[1:]:` | Loops through AST children/items. |
| 2387 | `                # LINE: Case node type tells variety or soil/default.` | Comment/guideline in current code. |
| 2388 | `                label_type = case_node.node_type` | Stores or updates runtime state/value. |
| 2389 | `                # LINE: variety case path.` | Comment/guideline in current code. |
| 2390 | `                if label_type == "Case":` | Checks a runtime condition. |
| 2391 | `                    # LINE: First case child is case literal/expression.` | Comment/guideline in current code. |
| 2392 | `                    case_value_node = case_node.children[0]` | Stores or updates runtime state/value. |
| 2393 | `                    # LINE: Second case child is block to run.` | Comment/guideline in current code. |
| 2394 | `                    block_node = case_node.children[1]` | Stores or updates runtime state/value. |
| 2395 | `                    # LINE: Evaluate case value for comparison.` | Comment/guideline in current code. |
| 2396 | `                    case_value = self.interpret(case_value_node)` | Stores or updates runtime state/value. |
| 2397 | `` | Blank spacing line. |
| 2398 | `                    # LINE: Run this block if value matches or fall-through already started.` | Comment/guideline in current code. |
| 2399 | `                    if switch_value == case_value or matched_case:` | Checks a runtime condition. |
| 2400 | `                        # LINE: Mark that switch found a matching case.` | Comment/guideline in current code. |
| 2401 | `                        matched_case = True` | Stores or updates runtime state/value. |
| 2402 | `                        # AUTO: Starts protected code that can catch errors.` | Comment/guideline in current code. |
| 2403 | `                        try:` | Starts protected block for optional runtime dependency or error handling. |
| 2404 | `                            # LINE: Each case block gets its own local scope.` | Comment/guideline in current code. |
| 2405 | `                            self.enter_scope()` | Enters a new local runtime scope. |
| 2406 | `                            # LINE: Execute case statements.` | Comment/guideline in current code. |
| 2407 | `                            self.eval_block(block_node)` | Runtime support logic. |
| 2408 | `                            # LINE: Stop switch if prune was triggered.` | Comment/guideline in current code. |
| 2409 | `                            if self.break_triggered():` | Checks a runtime condition. |
| 2410 | `                                # AUTO: Stops the nearest loop.` | Comment/guideline in current code. |
| 2411 | `                                break_found = True` | Stops nearest loop. |
| 2412 | `                                # AUTO: Stops the nearest loop.` | Comment/guideline in current code. |
| 2413 | `                                break` | Stops nearest loop. |
| 2414 | `                        # AUTO: Runs cleanup code no matter what happened.` | Comment/guideline in current code. |
| 2415 | `                        finally:` | Runs cleanup even if reclaim/error happens. |
| 2416 | `                            # LINE: Leave case scope.` | Comment/guideline in current code. |
| 2417 | `                            self.exit_scope()` | Leaves current runtime scope. |
| 2418 | `                    ` | Blank spacing line. |
| 2419 | `                # LINE: soil/default case path.` | Comment/guideline in current code. |
| 2420 | `                elif label_type == "Default":` | Alternative runtime condition. |
| 2421 | `                    # LINE: Save default block to run later if no case matched.` | Comment/guideline in current code. |
| 2422 | `                    default_case = case_node.children[0]` | Stores or updates runtime state/value. |
| 2423 | `            ` | Blank spacing line. |
| 2424 | `            # LINE: Run soil/default only if no variety matched and no prune happened.` | Comment/guideline in current code. |
| 2425 | `            if not matched_case and not break_found and default_case:` | Checks a runtime condition. |
| 2426 | `                # AUTO: Starts protected code that can catch errors.` | Comment/guideline in current code. |
| 2427 | `                try:` | Starts protected block for optional runtime dependency or error handling. |
| 2428 | `                    # LINE: Default block gets its own local scope.` | Comment/guideline in current code. |
| 2429 | `                    self.enter_scope()` | Enters a new local runtime scope. |
| 2430 | `                    # LINE: Execute soil/default statements.` | Comment/guideline in current code. |
| 2431 | `                    self.eval_block(default_case)` | Runtime support logic. |
| 2432 | `                # AUTO: Runs cleanup code no matter what happened.` | Comment/guideline in current code. |
| 2433 | `                finally:` | Runs cleanup even if reclaim/error happens. |
| 2434 | `                    # LINE: Leave default scope.` | Comment/guideline in current code. |
| 2435 | `                    self.exit_scope()` | Leaves current runtime scope. |
| 2436 | `` | Blank spacing line. |
| 2437 | `        # AUTO: Runs cleanup code no matter what happened.` | Comment/guideline in current code. |
| 2438 | `        finally:` | Runs cleanup even if reclaim/error happens. |
| 2439 | `            # LINE: Leave switch/prune context.` | Comment/guideline in current code. |
| 2440 | `            self.exit_loop()` | Runtime support logic. |
| 2441 | `            # LINE: Leave switch local scope.` | Comment/guideline in current code. |
| 2442 | `            self.exit_scope()` | Leaves current runtime scope. |
| 2443 | `` | Blank spacing line. |
| 2444 | `` | Blank spacing line. |
| 2445 | `    # AUTO: Defines function `emit_input_request`.` | Comment/guideline in current code. |
| 2446 | `    def emit_input_request(self, var_name, prompt):` | Runtime support logic. |
| 2447 | `        # LINE: Tell frontend to show input prompt for water().` | Comment/guideline in current code. |
| 2448 | `        self.socketio.emit('input_required', {'prompt': prompt, 'variable': var_name})` | Sends output/input event to frontend/server collector. |
| 2449 | `` | Blank spacing line. |
| 2450 | `    # AUTO: Defines function `provide_input`.` | Comment/guideline in current code. |
| 2451 | `    def provide_input(self, var_name, input_value):` | Runtime support logic. |
| 2452 | `        # LINE: Get waiting event for this water() variable.` | Comment/guideline in current code. |
| 2453 | `        evt = self.input_events.get(var_name)` | Stores or updates runtime state/value. |
| 2454 | `        # LINE: If interpreter is not waiting yet, store input for later.` | Comment/guideline in current code. |
| 2455 | `        if evt is None:` | Checks a runtime condition. |
| 2456 | `            # AUTO: Sets `self.input_values[var_name]`.` | Comment/guideline in current code. |
| 2457 | `            self.input_values[var_name] = input_value` | Stores or updates runtime state/value. |
| 2458 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 2459 | `            return` | Runtime support logic. |
| 2460 | `        # LINE: Eventlet mode resumes the waiting green thread.` | Comment/guideline in current code. |
| 2461 | `        if _USE_EVENTLET:` | Checks a runtime condition. |
| 2462 | `            # AUTO: Calls `evt.send`.` | Comment/guideline in current code. |
| 2463 | `            evt.send(input_value)` | Runtime support logic. |
| 2464 | `        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 2465 | `        else:` | Fallback runtime branch. |
| 2466 | `            # LINE: Threading mode stores value and releases wait().` | Comment/guideline in current code. |
| 2467 | `            self.input_values[var_name] = input_value` | Stores or updates runtime state/value. |
| 2468 | `            # AUTO: Calls `evt.set`.` | Comment/guideline in current code. |
| 2469 | `            evt.set()` | Runtime support logic. |
| 2470 | `` | Blank spacing line. |
| 2471 | `    # AUTO: Defines function `wait_for_input`.` | Comment/guideline in current code. |
| 2472 | `    def wait_for_input(self, var_name):` | Runtime support logic. |
| 2473 | `        # LINE: If input arrived early, consume it immediately.` | Comment/guideline in current code. |
| 2474 | `        if var_name in self.input_values:` | Checks a runtime condition. |
| 2475 | `            # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 2476 | `            return self.input_values.pop(var_name)` | Returns runtime value/result to caller. |
| 2477 | `` | Blank spacing line. |
| 2478 | `        # LINE: Eventlet waiting path used by Socket.IO server.` | Comment/guideline in current code. |
| 2479 | `        if _USE_EVENTLET:` | Checks a runtime condition. |
| 2480 | `            # LINE: Create event object that pauses execution.` | Comment/guideline in current code. |
| 2481 | `            evt = _ev.Event()` | Stores or updates runtime state/value. |
| 2482 | `            # LINE: Store event so provide_input can resume it.` | Comment/guideline in current code. |
| 2483 | `            self.input_events[var_name] = evt` | Stores or updates runtime state/value. |
| 2484 | `            # LINE: Pause here until frontend sends input.` | Comment/guideline in current code. |
| 2485 | `            value = evt.wait()` | Stores or updates runtime state/value. |
| 2486 | `            # LINE: Remove event after input arrives.` | Comment/guideline in current code. |
| 2487 | `            self.input_events.pop(var_name, None)` | Runtime support logic. |
| 2488 | `            # LINE: Stop if execution was cancelled while waiting.` | Comment/guideline in current code. |
| 2489 | `            if getattr(self, '_cancelled', False):` | Checks a runtime condition. |
| 2490 | `                # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 2491 | `                raise _CancelledError()` | Raises control-flow or runtime error exception. |
| 2492 | `            # LINE: Return received input value.` | Comment/guideline in current code. |
| 2493 | `            return value` | Returns runtime value/result to caller. |
| 2494 | `        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 2495 | `        else:` | Fallback runtime branch. |
| 2496 | `            # LINE: Standard threading waiting path.` | Comment/guideline in current code. |
| 2497 | `            event = threading.Event()` | Stores or updates runtime state/value. |
| 2498 | `            # LINE: Store event so provide_input can set it.` | Comment/guideline in current code. |
| 2499 | `            self.input_events[var_name] = event` | Stores or updates runtime state/value. |
| 2500 | `            # LINE: Pause here until event.set().` | Comment/guideline in current code. |
| 2501 | `            event.wait()` | Runtime support logic. |
| 2502 | `            # LINE: Stop if execution was cancelled while waiting.` | Comment/guideline in current code. |
| 2503 | `            if getattr(self, '_cancelled', False):` | Checks a runtime condition. |
| 2504 | `                # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 2505 | `                raise _CancelledError()` | Raises control-flow or runtime error exception. |
| 2506 | `            # LINE: Read input value sent by frontend.` | Comment/guideline in current code. |
| 2507 | `            value = self.input_values.pop(var_name, None)` | Stores or updates runtime state/value. |
| 2508 | `            # LINE: Remove finished event.` | Comment/guideline in current code. |
| 2509 | `            self.input_events.pop(var_name, None)` | Runtime support logic. |
| 2510 | `            # LINE: Return received input value.` | Comment/guideline in current code. |
| 2511 | `            return value` | Returns runtime value/result to caller. |
| 2512 | `` | Blank spacing line. |
| 2513 | `    # AUTO: Defines function `eval_input`.` | Comment/guideline in current code. |
| 2514 | `    def eval_input(self, node):` | Starts a node-specific runtime evaluator. |
| 2515 | `        # GUIDE: water() finds target variable/type from parent node, asks the` | Comment/guideline in current code. |
| 2516 | `        # UI for a value, then converts that value before assignment.` | Comment/guideline in current code. |
| 2517 | `        # LINE: Parent tells whether water() is declaration, assignment, or expression.` | Comment/guideline in current code. |
| 2518 | `        parent_node = node.parent` | Stores or updates runtime state/value. |
| 2519 | `        # LINE: Case seed n = water(seed);` | Comment/guideline in current code. |
| 2520 | `        if isinstance(parent_node, VariableDeclarationNode):` | Checks a runtime condition. |
| 2521 | `            # Case: seed n = water(seed);` | Comment/guideline in current code. |
| 2522 | `            # AUTO: Sets `var_name`.` | Comment/guideline in current code. |
| 2523 | `            var_name = parent_node.children[1].value` | Stores or updates runtime state/value. |
| 2524 | `            # AUTO: Sets `var_type`.` | Comment/guideline in current code. |
| 2525 | `            var_type = parent_node.children[0].value` | Stores or updates runtime state/value. |
| 2526 | `        ` | Blank spacing line. |
| 2527 | `        # LINE: Case water(n); or n = water(seed);` | Comment/guideline in current code. |
| 2528 | `        elif isinstance(parent_node, AssignmentNode):` | Alternative runtime condition. |
| 2529 | `            # Case: water(n); or n = water(seed);` | Comment/guideline in current code. |
| 2530 | `            # AUTO: Sets `target`.` | Comment/guideline in current code. |
| 2531 | `            target = parent_node.children[0]` | Stores or updates runtime state/value. |
| 2532 | `            # LINE: Array input target path like arr[i].` | Comment/guideline in current code. |
| 2533 | `            if isinstance(target, ListAccessNode):` | Checks a runtime condition. |
| 2534 | `                # AUTO: Sets `current`.` | Comment/guideline in current code. |
| 2535 | `                current = target` | Stores or updates runtime state/value. |
| 2536 | `                # AUTO: Repeats while this condition is true.` | Comment/guideline in current code. |
| 2537 | `                while hasattr(current, 'node_type') and current.node_type == "ListAccess":` | Repeats while runtime condition is true. |
| 2538 | `                    # AUTO: Sets `current`.` | Comment/guideline in current code. |
| 2539 | `                    current = current.children[0].value` | Stores or updates runtime state/value. |
| 2540 | `                # AUTO: Sets `var_name`.` | Comment/guideline in current code. |
| 2541 | `                var_name = current if isinstance(current, str) else str(current)` | Stores or updates runtime state/value. |
| 2542 | `                # AUTO: Sets `var_type`.` | Comment/guideline in current code. |
| 2543 | `                var_type = self.lookup_variable(var_name)["type"]  # type: ignore` | Reads variable metadata/value from runtime scopes. |
| 2544 | `            # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 2545 | `            else:` | Fallback runtime branch. |
| 2546 | `                # LINE: Simple variable input target path.` | Comment/guideline in current code. |
| 2547 | `                var_name = target.value` | Stores or updates runtime state/value. |
| 2548 | `                # AUTO: Sets `var_type`.` | Comment/guideline in current code. |
| 2549 | `                var_type = self.lookup_variable(var_name)["type"]  # type: ignore` | Reads variable metadata/value from runtime scopes. |
| 2550 | `` | Blank spacing line. |
| 2551 | `        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 2552 | `        else:` | Fallback runtime branch. |
| 2553 | `            # Case: water(seed) used directly as an expression.` | Comment/guideline in current code. |
| 2554 | `            # LINE: Expression water() has no variable target, so use temporary name.` | Comment/guideline in current code. |
| 2555 | `            var_name = "_input"` | Stores or updates runtime state/value. |
| 2556 | `            # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 2557 | `            if node.value and "(" in node.value:` | Checks a runtime condition. |
| 2558 | `                # LINE: Extract requested input type from water(seed/tree/etc.).` | Comment/guideline in current code. |
| 2559 | `                inner = node.value.split("(")[1].rstrip(")")` | Stores or updates runtime state/value. |
| 2560 | `                # AUTO: Sets `var_type`.` | Comment/guideline in current code. |
| 2561 | `                var_type = inner if inner in {"seed", "tree", "leaf", "branch", "vine"} else "vine"` | Stores or updates runtime state/value. |
| 2562 | `            # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 2563 | `            else:` | Fallback runtime branch. |
| 2564 | `                # LINE: Plain water() defaults to vine/string input.` | Comment/guideline in current code. |
| 2565 | `                var_type = "vine"` | Stores or updates runtime state/value. |
| 2566 | `` | Blank spacing line. |
| 2567 | `        # LINE: Prompt text sent to UI.` | Comment/guideline in current code. |
| 2568 | `        prompt = f"Input for {var_name}: "` | Stores or updates runtime state/value. |
| 2569 | `        # LINE: Mark interpreter as waiting for input.` | Comment/guideline in current code. |
| 2570 | `        self.input_required = True` | Stores or updates runtime state/value. |
| 2571 | `` | Blank spacing line. |
| 2572 | `` | Blank spacing line. |
| 2573 | `        # Ask the UI/browser for input and wait until capture_input sends it.` | Comment/guideline in current code. |
| 2574 | `        # LINE: Send input_required event to frontend.` | Comment/guideline in current code. |
| 2575 | `        self.emit_input_request(var_name, prompt)` | Runtime support logic. |
| 2576 | `` | Blank spacing line. |
| 2577 | `        # LINE: Pause execution until frontend sends input.` | Comment/guideline in current code. |
| 2578 | `        input_value = self.wait_for_input(var_name)` | Stores or updates runtime state/value. |
| 2579 | `` | Blank spacing line. |
| 2580 | `` | Blank spacing line. |
| 2581 | `        # LINE: Mark input wait as finished.` | Comment/guideline in current code. |
| 2582 | `        self.input_required = False` | Stores or updates runtime state/value. |
| 2583 | `` | Blank spacing line. |
| 2584 | `        # LINE: Convert user text into seed integer when needed.` | Comment/guideline in current code. |
| 2585 | `        if var_type == "seed":` | Checks a runtime condition. |
| 2586 | `            # AUTO: Sets `original_input`.` | Comment/guideline in current code. |
| 2587 | `            original_input = input_value` | Stores or updates runtime state/value. |
| 2588 | `            # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 2589 | `            if isinstance(input_value, str) and input_value.startswith('-'):` | Checks a runtime condition. |
| 2590 | `                # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 2591 | `                raise InterpreterError(f"Runtime Error: GAL uses '~' for negative numbers, not '-'. Got '{original_input}'; did you mean '~{original_input[1:]}'?", node.line)  # type: ignore` | Stops execution with a runtime error. |
| 2592 | `            # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 2593 | `            if isinstance(input_value, str) and input_value.startswith('~'):` | Checks a runtime condition. |
| 2594 | `                # AUTO: Sets `input_value`.` | Comment/guideline in current code. |
| 2595 | `                input_value = '-' + input_value[1:]` | Stores or updates runtime state/value. |
| 2596 | `            # AUTO: Starts protected code that can catch errors.` | Comment/guideline in current code. |
| 2597 | `            try:` | Starts protected block for optional runtime dependency or error handling. |
| 2598 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 2599 | `                if len(input_value.strip('-').lstrip('0')) > 16:` | Checks a runtime condition. |
| 2600 | `                    # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 2601 | `                    raise InterpreterError(f"Runtime Error: Input value exceeds maximum number of 16 digits", node.line)` | Stops execution with a runtime error. |
| 2602 | `                # AUTO: Sets `input_value`.` | Comment/guideline in current code. |
| 2603 | `                input_value = int(float(input_value))  # type: ignore` | Stores or updates runtime state/value. |
| 2604 | `            # AUTO: Handles the matching error case.` | Comment/guideline in current code. |
| 2605 | `            except ValueError:` | Handles the matching runtime/import error case. |
| 2606 | `                # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 2607 | `                raise InterpreterError(f"Runtime Error: Expected integer value, got '{original_input}'", node.line)` | Stops execution with a runtime error. |
| 2608 | `` | Blank spacing line. |
| 2609 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 2610 | `        elif var_type == "tree":` | Alternative runtime condition. |
| 2611 | `            # AUTO: Sets `original_input`.` | Comment/guideline in current code. |
| 2612 | `            original_input = input_value` | Stores or updates runtime state/value. |
| 2613 | `            # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 2614 | `            if isinstance(input_value, str) and input_value.startswith('-'):` | Checks a runtime condition. |
| 2615 | `                # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 2616 | `                raise InterpreterError(f"Runtime Error: GAL uses '~' for negative numbers, not '-'. Got '{original_input}'; did you mean '~{original_input[1:]}'?", node.line)  # type: ignore` | Stops execution with a runtime error. |
| 2617 | `            # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 2618 | `            if isinstance(input_value, str) and input_value.startswith('~'):` | Checks a runtime condition. |
| 2619 | `                # AUTO: Sets `input_value`.` | Comment/guideline in current code. |
| 2620 | `                input_value = '-' + input_value[1:]` | Stores or updates runtime state/value. |
| 2621 | `            # AUTO: Starts protected code that can catch errors.` | Comment/guideline in current code. |
| 2622 | `            try:` | Starts protected block for optional runtime dependency or error handling. |
| 2623 | `                # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 2624 | `                if '.' in input_value:  # type: ignore` | Checks a runtime condition. |
| 2625 | `                    # AUTO: Sets `integer_part, decimal_part`.` | Comment/guideline in current code. |
| 2626 | `                    integer_part, decimal_part = str(input_value).split('.')` | Stores or updates runtime state/value. |
| 2627 | `                    # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 2628 | `                    if len(integer_part.strip('-').lstrip('0')) > 16:` | Checks a runtime condition. |
| 2629 | `                        # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 2630 | `                        raise InterpreterError(f"Runtime Error: Input value exceeds maximum number of 16 digits", node.line)` | Stops execution with a runtime error. |
| 2631 | `                    # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 2632 | `                    if len(decimal_part.rstrip('0')) > 5:` | Checks a runtime condition. |
| 2633 | `                        # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 2634 | `                        raise InterpreterError(f"Runtime Error: Input value exceeds maximum number of 5 decimal numbers", node.line)` | Stops execution with a runtime error. |
| 2635 | `` | Blank spacing line. |
| 2636 | `                # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 2637 | `                else:` | Fallback runtime branch. |
| 2638 | `                    # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 2639 | `                    if len(input_value.strip('-').lstrip('0')) > 16:` | Checks a runtime condition. |
| 2640 | `                        # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 2641 | `                        raise InterpreterError(f"Runtime Error: Input value exceeds maximum number of 16 digits", node.line)` | Stops execution with a runtime error. |
| 2642 | `` | Blank spacing line. |
| 2643 | `                # AUTO: Sets `input_value`.` | Comment/guideline in current code. |
| 2644 | `                input_value = float(input_value)  # type: ignore` | Stores or updates runtime state/value. |
| 2645 | `` | Blank spacing line. |
| 2646 | `` | Blank spacing line. |
| 2647 | `            # AUTO: Handles the matching error case.` | Comment/guideline in current code. |
| 2648 | `            except ValueError:` | Handles the matching runtime/import error case. |
| 2649 | `                # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 2650 | `                raise InterpreterError(f"Runtime Error: Expected float value, got '{original_input}'", node.line)` | Stops execution with a runtime error. |
| 2651 | `` | Blank spacing line. |
| 2652 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 2653 | `        elif var_type == "branch":` | Alternative runtime condition. |
| 2654 | `            # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 2655 | `            if input_value == "true" or input_value == "false":` | Checks a runtime condition. |
| 2656 | `                # AUTO: Executes this statement.` | Comment/guideline in current code. |
| 2657 | `                suggestion = "sunshine" if input_value == "true" else "frost"` | Stores or updates runtime state/value. |
| 2658 | `                # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 2659 | `                raise InterpreterError(f"Runtime Error: GAL uses 'sunshine' and 'frost' for booleans, not 'true'/'false'. Got '{input_value}'; did you mean '{suggestion}'?", node.line)` | Stops execution with a runtime error. |
| 2660 | `            # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 2661 | `            if input_value == "sunshine":` | Checks a runtime condition. |
| 2662 | `                # AUTO: Sets `input_value`.` | Comment/guideline in current code. |
| 2663 | `                input_value = True` | Stores or updates runtime state/value. |
| 2664 | `            # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 2665 | `            elif input_value == "frost":` | Alternative runtime condition. |
| 2666 | `                # AUTO: Sets `input_value`.` | Comment/guideline in current code. |
| 2667 | `                input_value = False` | Stores or updates runtime state/value. |
| 2668 | `            # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 2669 | `            else:` | Fallback runtime branch. |
| 2670 | `                # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 2671 | `                raise InterpreterError(f"Runtime Error: expected branch value (sunshine/frost), got '{input_value}'", node.line)` | Stops execution with a runtime error. |
| 2672 | `            ` | Blank spacing line. |
| 2673 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 2674 | `        elif var_type == "leaf":` | Alternative runtime condition. |
| 2675 | `            # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 2676 | `            if len(input_value) != 1:  # type: ignore` | Checks a runtime condition. |
| 2677 | `                # AUTO: Stops this flow by raising an error.` | Comment/guideline in current code. |
| 2678 | `                raise InterpreterError(f"Runtime Error: Expected a single character for leaf, got '{input_value}'", node.line)` | Stops execution with a runtime error. |
| 2679 | `            # AUTO: Sets `input_value`.` | Comment/guideline in current code. |
| 2680 | `            input_value = str(input_value)` | Stores or updates runtime state/value. |
| 2681 | `` | Blank spacing line. |
| 2682 | `        # AUTO: Checks the next alternate condition.` | Comment/guideline in current code. |
| 2683 | `        elif var_type == "vine":` | Alternative runtime condition. |
| 2684 | `            # AUTO: Sets `input_value`.` | Comment/guideline in current code. |
| 2685 | `            input_value = str(input_value)` | Stores or updates runtime state/value. |
| 2686 | `` | Blank spacing line. |
| 2687 | `        # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 2688 | `        return input_value` | Returns runtime value/result to caller. |
| 2689 | `` | Blank spacing line. |

## 11. Line-by-Line: interpreter/errors.py
| Line | Code | Explanation |
|---:|---|---|
| 1 | `# AUTO: Imports a module used by this file.` | Comment/guideline in current code. |
| 2 | `import re` | Imports dependency used during runtime execution. |
| 3 | `` | Blank spacing line. |
| 4 | `# AUTO: Sets `_REDUNDANT_PREFIX`.` | Comment/guideline in current code. |
| 5 | `_REDUNDANT_PREFIX = re.compile(r'^(Runtime Error\|Semantic Error\|Type Mismatch\|Syntax Error)\s*:?\s*', re.IGNORECASE)` | Stores or updates runtime state/value. |
| 6 | `` | Blank spacing line. |
| 7 | `` | Blank spacing line. |
| 8 | `# AUTO: Defines class `ReturnValue`.` | Comment/guideline in current code. |
| 9 | `class ReturnValue(Exception):` | Defines internal exception for reclaim return values. |
| 10 | `` | Blank spacing line. |
| 11 | `    # AUTO: Defines function `__init__`.` | Comment/guideline in current code. |
| 12 | `    def __init__(self, value):` | Initializes object state. |
| 13 | `        # AUTO: Sets `self.value`.` | Comment/guideline in current code. |
| 14 | `        self.value = value` | Stores or updates runtime state/value. |
| 15 | `` | Blank spacing line. |
| 16 | `` | Blank spacing line. |
| 17 | `# AUTO: Defines class `_CancelledError`.` | Comment/guideline in current code. |
| 18 | `class _CancelledError(Exception):` | Runtime support logic. |
| 19 | `    # AUTO: Does nothing for this required block.` | Comment/guideline in current code. |
| 20 | `    pass` | Runtime support logic. |
| 21 | `` | Blank spacing line. |
| 22 | `` | Blank spacing line. |
| 23 | `# AUTO: Defines class `InterpreterError`.` | Comment/guideline in current code. |
| 24 | `class InterpreterError(Exception):` | Defines the GAL runtime interpreter. |
| 25 | `` | Blank spacing line. |
| 26 | `    # AUTO: Defines function `__init__`.` | Comment/guideline in current code. |
| 27 | `    def __init__(self, message, line):` | Initializes object state. |
| 28 | `        # AUTO: Calls `super`.` | Comment/guideline in current code. |
| 29 | `        super().__init__(message)` | Runtime support logic. |
| 30 | `        # AUTO: Sets `clean`.` | Comment/guideline in current code. |
| 31 | `        clean = _REDUNDANT_PREFIX.sub('', str(message)).strip()` | Stores or updates runtime state/value. |
| 32 | `        # AUTO: Checks this condition.` | Comment/guideline in current code. |
| 33 | `        if line is not None and str(line) != "":` | Checks a runtime condition. |
| 34 | `            # AUTO: Sets `self.message`.` | Comment/guideline in current code. |
| 35 | `            self.message = f"RUNTIME error line {line}: {clean}"` | Stores or updates runtime state/value. |
| 36 | `        # AUTO: Runs when previous condition did not pass.` | Comment/guideline in current code. |
| 37 | `        else:` | Fallback runtime branch. |
| 38 | `            # AUTO: Sets `self.message`.` | Comment/guideline in current code. |
| 39 | `            self.message = clean` | Stores or updates runtime state/value. |
| 40 | `` | Blank spacing line. |
| 41 | `    # AUTO: Defines function `__str__`.` | Comment/guideline in current code. |
| 42 | `    def __str__(self):` | Runtime support logic. |
| 43 | `        # AUTO: Returns this result to the caller.` | Comment/guideline in current code. |
| 44 | `        return self.message` | Returns runtime value/result to caller. |
| 45 | `` | Blank spacing line. |
| 46 | `` | Blank spacing line. |
| 47 | `# AUTO: Defines class `InterpreterInputRequest`.` | Comment/guideline in current code. |
| 48 | `class InterpreterInputRequest(Exception):` | Defines the GAL runtime interpreter. |
| 49 | `` | Blank spacing line. |
| 50 | `    # AUTO: Defines function `__init__`.` | Comment/guideline in current code. |
| 51 | `    def __init__(self, prompt, line):` | Initializes object state. |
| 52 | `        # AUTO: Sets `self.prompt`.` | Comment/guideline in current code. |
| 53 | `        self.prompt = prompt` | Stores or updates runtime state/value. |
| 54 | `        # AUTO: Sets `self.line`.` | Comment/guideline in current code. |
| 55 | `        self.line = line` | Stores or updates runtime state/value. |