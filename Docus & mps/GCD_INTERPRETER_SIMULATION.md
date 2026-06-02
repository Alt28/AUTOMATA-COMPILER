# GCD Program Interpreter Simulation

Detailed step-by-step explanation of how the GrowALanguage interpreter executes the recursive GCD program.

Project path: `C:\Users\clarence\Downloads\AUTOMATA-COMPILER-main (1)\AUTOMATA-COMPILER-main\my GAL code`

Generated: 2026-06-02 22:30

## 1. Program Under Simulation

This is the exact GAL program being simulated:

```gal
pollinate seed gcd(seed a, seed b) {
    spring (b == 0) {
        reclaim a;
    }
    reclaim gcd(b, a % b);
}

root() {
    seed a;
    seed b;
    seed result;

    plant("Enter first number: ");
    a = water();
    plant("Enter second number: ");
    b = water();

    result = gcd(a, b);
    plant("GCD of", a,"and ",b, "is", result);

    reclaim;
}
```

Sample input used in this simulation:

```text
first number = 48
second number = 18
```

Expected mathematical result:

```text
gcd(48, 18) = 6
```

## 2. Important Interpreter View

By the time the interpreter runs, the source code is no longer plain text. The lexer already created tokens, the parser checked the CFG, the builder created AST nodes, and semantic validation already passed. The interpreter executes AST nodes such as `FunctionDeclarationNode`, `AssignmentNode`, `FunctionCallNode`, `IfStatementNode`, `ReturnNode`, and `PrintNode`.

## 3. Backend Execution Path For This Program

Because this program uses `water()`, the interactive UI normally uses the Socket.IO run path. That path is in `Backend/server.py`.

Source: `Backend/server.py:411-489`

```python
0411: def handle_run_code(data):
0412:     sid = request.sid
0413:     source_code = data.get('source_code', '')
0414: 
0415:     tokens, lex_errors = lex(source_code)
0416:     if lex_errors:
0417:         for err in lex_errors:
0418:             emit('output', {'output': f'Lexical Error: {err}'})
0419:         emit('execution_complete', {'success': False, 'stage': 'lexical'})
0420:         return
0421: 
0422:     emit('stage_complete', {'stage': 'lexical', 'success': True})
0423: 
0424:     parse_result = parser.parse_and_build(tokens)
0425:     if not parse_result['success']:
0426:         error_stage = parse_result.get('error_stage', 'syntax')
0427:         for err in parse_result['errors']:
0428:             emit('output', {'output': f'{err}'})
0429:         emit('execution_complete', {'success': False, 'stage': error_stage})
0430:         return
0431: 
0432:     emit('stage_complete', {'stage': 'syntax', 'success': True})
0433: 
0434:     semantic_result = validate_ast(parse_result['ast'], parse_result['symbol_table'])
0435:     if not semantic_result['success']:
0436:         for err in semantic_result['errors']:
0437:             emit('output', {'output': f'{err}'})
0438:         emit('execution_complete', {'success': False, 'stage': 'semantic'})
0439:         return
0440: 
0441:     emit('stage_complete', {'stage': 'semantic', 'success': True})
0442: 
0443:     ast = semantic_result['ast']
0444: 
0445:     old_interp = interpreters.get(sid)
0446:     if old_interp and hasattr(old_interp, '_cancelled'):
0447:         old_interp._cancelled = True
0448:         for evt in list(old_interp.input_events.values()):
0449:             try:
0450:                 evt.send(None)
0451:             except (AttributeError, AssertionError):
0452:                 try:
0453:                     evt.set()
0454:                 except Exception:
0455:                     pass
0456: 
0457:     def run_interpreter():
0458:         try:
0459:             session_emitter = SessionEmitter(socketio, sid)
0460:             interp = Interpreter(socketio=session_emitter)
0461:             interp._cancelled = False
0462:             interpreters[sid] = interp
0463:             interp.interpret(ast)
0464:             if not interp._cancelled:
0465:                 socketio.emit('execution_complete', {'success': True, 'stage': 'execution'}, to=sid)
0466:         except _CancelledError:
0467:             pass
0468:         except InterpreterError as e:
0469:             if not getattr(interp, '_cancelled', False):
0470:                 socketio.emit('output', {'output': f'Runtime Error: {e}'}, to=sid)
0471:                 socketio.emit('execution_complete', {'success': False, 'stage': 'execution'}, to=sid)
0472:         except Exception as e:
0473:             if not getattr(interp, '_cancelled', False):
0474:                 socketio.emit('output', {'output': f'Internal Error: {e}'}, to=sid)
0475:                 socketio.emit('execution_complete', {'success': False, 'stage': 'execution'}, to=sid)
0476:         finally:
0477:             if interpreters.get(sid) is interp:
0478:                 interpreters.pop(sid, None)
0479: 
0480:     socketio.start_background_task(run_interpreter)
0481: 
0482: @socketio.on('capture_input')
0483: def handle_capture_input(data):
0484:     sid = request.sid
0485:     interp = interpreters.get(sid)
0486:     if interp:
0487:         var_name = data.get('var_name', '')
0488:         input_value = data.get('input', '')
0489:         interp.provide_input(var_name, input_value)
```

Explanation:

- Lines 411-414 receive the source code from the UI.
- Line 415 sends the complete source code to the lexer.
- Lines 424-430 run parser plus AST builder using `parser.parse_and_build(tokens)`.
- Lines 434-439 run semantic validation.
- Lines 457-463 create an `Interpreter` object and execute the AST with `interp.interpret(ast)`.
- Lines 482-489 receive input from the UI when `water()` asks for a value.

## 4. AST Nodes Used By This Program

Source: `Backend/shared/ast_nodes.py:3-65`

```python
0003: class ASTNode:
0004:     def __init__(self, node_type, value=None, line=None):
0005:         self.node_type = node_type
0006:         self.value = value
0007:         self.children = []
0008:         self.parent = None
0009:         self.line = line
0010: 
0011:     def add_child(self, child):
0012:         child.parent = self
0013:         self.children.append(child)
0014: 
0015:     def print_tree(self, level=0):
0016:         indent = ' ' * (level * 3)
0017:         print(f"{indent}╚═{self.node_type}: {self.value if self.value else ''}")
0018:         for child in self.children:
0019:             child.print_tree(level + 1)
0020:         
0021: 
0022: class ProgramNode(ASTNode):
0023:     def __init__(self, line=None):
0024:         super().__init__("Program", line=line)
0025: 
0026: class VariableDeclarationNode(ASTNode):
0027:     def __init__(self, var_type, var_name, value=None, line=None):
0028:         super().__init__("VariableDeclaration", line=line)
0029:         self.add_child(ASTNode("Type", var_type, line=line))
0030:         self.add_child(ASTNode("Identifier", var_name, line=line))
0031:         if value:
0032:             self.add_child(value)
0033: 
0034: class AssignmentNode(ASTNode):
0035:     def __init__(self, target, value, line=None):
0036:         super().__init__("Assignment", line=line)
0037:         if isinstance(target, str):
0038:             self.add_child(ASTNode("Identifier", target, line=line))
0039:         else:
0040:             self.add_child(target)
0041:         self.add_child(value)
0042:         
0043: 
0044: class BinaryOpNode(ASTNode):
0045:     def __init__(self, left, operator, right, line=None):
0046:         super().__init__("BinaryOp", operator, line=line)
0047:         self.add_child(left)
0048:         self.add_child(right)
0049: 
0050: class FunctionDeclarationNode(ASTNode):
0051:     def __init__(self, return_type, name, params, line=None):
0052:         super().__init__("FunctionDeclaration", name, line=line)
0053:         self.add_child(ASTNode("ReturnType", return_type, line=line))
0054:         self.add_child(params)
0055: 
0056: class FunctionCallNode(ASTNode):
0057:     def __init__(self, name, args, line=None):
0058:         super().__init__("FunctionCall", name, line=line)
0059:         for arg in args:
0060:             self.add_child(arg)
0061: 
0062: class IfStatementNode(ASTNode):
0063:     def __init__(self, condition, line=None):
0064:         super().__init__("IfStatement", line=line)
0065:         self.add_child(condition)
```

Source: `Backend/shared/ast_nodes.py:83-106`

```python
0083: class PrintNode(ASTNode):
0084:     def __init__(self, args, line=None):
0085:         super().__init__("PrintStatement", line=line) 
0086:         for arg in args:
0087:             self.add_child(arg)
0088: 
0089: class UnaryOpNode(ASTNode):
0090:     def __init__(self, operator, operand, position="pre", line=None):
0091:         super().__init__("UnaryOp", operator, line=line)
0092:         self.position = position
0093:         self.add_child(operand)
0094: 
0095: class FertileDeclarationNode(ASTNode):
0096:     def __init__(self, var_type, var_name, value, line=None):
0097:         super().__init__("SturdyDeclaration", line=line)
0098:         self.add_child(ASTNode("Type", var_type, line=line))
0099:         self.add_child(ASTNode("Identifier", var_name, line=line))
0100:         self.add_child(value)
0101: 
0102: class ReturnNode(ASTNode):
0103:     def __init__(self, return_value=None, line=None):
0104:         super().__init__("Return", line=line)
0105:         if return_value:
0106:             self.add_child(return_value)
```

Main AST node meanings for the GCD program:

| GAL construct | AST node | Purpose |
|---|---|---|
| `pollinate seed gcd(...) { ... }` | `FunctionDeclarationNode` | Stores function name, return type, parameters, and body block. |
| `root() { ... }` | `FunctionDeclarationNode` | Stored as the main function that `eval_program()` calls. |
| `seed a;` | `VariableDeclarationNode` | Creates a variable record. |
| `a = water();` | `AssignmentNode` + `Input` node | Gets input then assigns it to `a`. |
| `result = gcd(a, b);` | `AssignmentNode` + `FunctionCallNode` | Calls `gcd`, receives returned value, stores it in `result`. |
| `spring (b == 0)` | `IfStatementNode` | Checks base case of recursion. |
| `reclaim a;` | `ReturnNode` | Returns a value from the function. |
| `plant(...)` | `PrintNode` | Sends output to UI. |

## 5. Builder Creates Function And Statement Nodes

Source: `Backend/parser/builder.py:195-300`

```python
0195: def parse_function(tokens, index, func_name, func_type):
0196:     line = tokens[index].line
0197: 
0198:     symbol_table.current_func_name = func_name
0199: 
0200:     if func_name in symbol_table.functions:
0201:         error = f"Semantic Error: '{func_name}' already declared."
0202:         raise SemanticError(error, tokens[index].line)
0203:     
0204:     elif func_name in symbol_table.variables:
0205:         error = f"Semantic Error: '{func_name}' already declared."
0206:         raise SemanticError(error, tokens[index].line)
0207: 
0208:     if func_name in {"root"}:
0209:         symbol_table.enter_scope()
0210:         index += 1
0211: 
0212:         if tokens[index].type == "(":
0213:             index += 1
0214:             if tokens[index].type != ")":
0215:                 raise SemanticError(f"Semantic Error: {func_name}() should not have parameters.", line)
0216:             index += 1
0217:         elif func_name == "root":
0218:             raise SemanticError("Semantic Error: Missing () for root function declaration.", line)
0219: 
0220:         params_node = ASTNode("Parameters")
0221:         func_node = FunctionDeclarationNode(func_type, func_name, params_node)
0222: 
0223:     else:
0224:         if tokens[index].type != "(":
0225:             error = f"Semantic Error: Missing () for function declaration."
0226:             raise SemanticError(error, line)
0227: 
0228:         params_node = ASTNode("Parameters")
0229:         line = tokens[index].line
0230:         symbol_table.enter_scope()
0231: 
0232:         while tokens[index].type != ")":
0233:             if tokens[index].value in {"seed", "tree", "vine", "leaf", "branch", "empty"}:
0234:                 param_type = tokens[index].value
0235:                 index += 1
0236:                 if tokens[index].type == "id":
0237:                     param_name = tokens[index].value
0238:                     param_node = ASTNode("Parameter")
0239:                     param_node.add_child(ASTNode("Type", param_type))
0240:                     param_node.add_child(ASTNode("Identifier", param_name))
0241:                     index += 1
0242: 
0243:                     is_list = False
0244:                     if tokens[index].type == "[":
0245:                         index += 1
0246:                         if tokens[index].type != "]":
0247:                             raise SemanticError(f"Semantic Error: Expected ']' after '[' in array parameter.", line)
0248:                         index += 1
0249:                         is_list = True
0250:                         param_node.add_child(ASTNode("ArrayParam", "true"))
0251: 
0252:                     params_node.add_child(param_node)
0253:                     error = symbol_table.declare_variable(param_name, param_type, is_list=is_list)
0254:                     if error:
0255:                         raise SemanticError(error, line)
0256: 
0257:                     if tokens[index].type == ",":
0258:                         index += 1
0259: 
0260:                 else:
0261:                     error = f"Semantic Error: Invalid parameter declaration."
0262:                     raise SemanticError(error, line)
0263: 
0264:             elif tokens[index].type == "id" and tokens[index].value in symbol_table.bundle_types:
0265:                 param_type = tokens[index].value
0266:                 index += 1
0267:                 if tokens[index].type == "id":
0268:                     param_name = tokens[index].value
0269:                     param_node = ASTNode("Parameter")
0270:                     param_node.add_child(ASTNode("Type", param_type))
0271:                     param_node.add_child(ASTNode("Identifier", param_name))
0272:                     params_node.add_child(param_node)
0273:                     error = symbol_table.declare_variable(param_name, param_type)
0274:                     if error:
0275:                         raise SemanticError(error, line)
0276:                     index += 1
0277: 
0278:                     if tokens[index].type == ",":
0279:                         index += 1
0280:                 else:
0281:                     error = f"Semantic Error: Invalid parameter declaration."
0282:                     raise SemanticError(error, line)
0283: 
0284:             else:
0285:                 index += 1
0286: 
0287:         symbol_table.declare_function(func_name, func_type, params_node.children)
0288:         index += 1
0289:         func_node = FunctionDeclarationNode(func_type, func_name, params_node)
0290: 
0291:     if tokens[index].type == "{":
0292:         index += 1
0293:         block_node = ASTNode("Block")
0294:         
0295:         while tokens[index].type != "}":
0296:             stmt, index = parse_statement(tokens, index, func_type)
0297:             if stmt:
0298:                 block_node.add_child(stmt)
0299: 
0300:         index += 1
```

How this applies to the program:

- `pollinate seed gcd(seed a, seed b)` becomes a `FunctionDeclarationNode` named `gcd`.
- The return type is `seed`.
- The parameter list stores two parameters: `seed a` and `seed b`.
- `root()` is also built as a `FunctionDeclarationNode`, but with no parameters.
- The block between `{` and `}` becomes the function body stored in the node.

Source: `Backend/parser/builder.py:1909-1968`

```python
1909: def parse_function_call(tokens, index, func_name, func_type, func_params):
1910:     line = tokens[index].line
1911:     
1912:     index += 2
1913:     args_node = ASTNode("Arguments")
1914:     provided_args = []  
1915:     expected_params = func_params  
1916:     
1917:     while tokens[index].type != ")":
1918:         if len(provided_args) >= len(expected_params):
1919:             raise SemanticError(f"Semantic Error: Too many arguments in function call '{func_name}'.", line)
1920: 
1921:         expected_type = expected_params[len(provided_args)].children[0].value 
1922:         
1923:         expected_param = expected_params[len(provided_args)]
1924:         is_array_param = any(child.node_type == "ArrayParam" for child in expected_param.children)
1925: 
1926:         if is_array_param:
1927:             if tokens[index].type != "id":
1928:                 raise SemanticError(f"Semantic Error: Expected array variable for parameter {len(provided_args) + 1} of '{func_name}'.", line)
1929:             arg_name = tokens[index].value
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
1959: 
1960:     for i, (arg_node, arg_type) in enumerate(provided_args):
1961:         expected_type = expected_params[i].children[0].value
1962: 
1963:         if expected_type in {"seed", "tree"} and arg_type == "seed":
1964:             continue 
1965:         
1966:         if arg_type != expected_type:
1967:             raise SemanticError(f"Semantic Error: Argument {i+1} of '{func_name}' should be '{expected_type}', but got '{arg_type}'.", line)
1968: 
```

This code builds calls like `gcd(a, b)` and recursive calls like `gcd(b, a % b)`. It checks the function exists, counts arguments, checks argument types, and creates a `FunctionCallNode`.

Source: `Backend/parser/builder.py:1972-2057`

```python
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
2022:             index_wrapper.add_child(index_expr)
2023:             list_access_node = ListAccessNode(var_name, index_wrapper, line=line)
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
```

`water()` and `water(variable)` are turned into `Input` nodes. For `a = water();`, the assignment parser creates an `AssignmentNode` whose right side is an `Input` node.

Source: `Backend/parser/builder.py:2063-2304`

```python
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
2113: 
2114:             if not list_info["is_list"] and list_info.get("type") != "vine":
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
2189:         elif tokens[index].type == "id" and tokens[index + 1].type == "[":
2190:             start_index = index
2191:             list_name = tokens[index].value
2192:             list_info = symbol_table.lookup_variable(list_name)
2193:             list_type = list_info["type"]
2194:             is_list = list_info["is_list"]
2195:             
2196:             if isinstance(list_info, str):
2197:                 raise SemanticError(f"Semantic Error: List '{list_name}' used before declaration.", tokens[index].line)
2198: 
2199:             if not list_info["is_list"] and list_info.get("type") != "vine":
2200:                 raise SemanticError(f"Semantic Error: '{list_name}' is not a list.", tokens[index].line)
2201: 
2202:             index += 2
2203:             expr_node, index, _ = parse_expression_branch(tokens, index)
2204: 
2205:             if tokens[index].type != "]":
2206:                 raise SemanticError("Syntax Error: Missing closing bracket.", tokens[index].line)
2207: 
2208:             index_node = ASTNode("Index", line=tokens[index].line)
2209:             index_node.add_child(expr_node)
2210: 
2211:             index += 1
2212:             list_access_node = ListAccessNode(list_name, index_node, line=tokens[index].line)
2213:             
2214:             if list_type in {"seed", "tree"}:
2215:                 arg_node, index, _ = parse_expression(tokens, start_index)
2216:                 actual_args.append(arg_node)
2217:                 
2218:             elif is_list:
2219:                 actual_args.append(list_access_node)
2220:             
2221: 
2222:         elif tokens[index].type == "id" and tokens[index+1].type == "(":
2223:             func_name = tokens[index].value
2224:             func_info = symbol_table.lookup_function(func_name)
2225:             index_start = index
2226: 
2227:             if isinstance(func_info, str):
2228:                 raise SemanticError(f"Semantic Error: Function '{func_name}' is not declared.", line)
2229:             
2230:             func_return_type = func_info["return_type"]
2231:             func_params = func_info["params"]
2232: 
2233:             func_node, index = parse_function_call(tokens, index, func_name, func_return_type, func_params)
2234:             if func_return_type in {"seed", "tree"}:
2235:                 expr_node, index, _ = parse_expression(tokens, index_start)
2236:                 actual_args.append(expr_node)
2237: 
2238:             else:
2239:                 actual_args.append(func_node)
2240:             
2241:             
2242:         elif tokens[index].type == "id":
2243:             arg_name = tokens[index].value
2244:             arg_info = symbol_table.lookup_variable(arg_name)
2245:             
2246:             if isinstance(arg_info, str):
2247:                 raise SemanticError(f"Semantic Error: Variable '{arg_name}' used before declaration.", line)
2248:             
2249:             if arg_info["is_list"]:
2250:                 if tokens[index + 1].type != "[":
2251:                     raise SemanticError(f"Semantic Error: List '{arg_name}' must be indexed with '[]' in expressions.", line)
2252:                 
2253:             if tokens[index + 1].type == "." and arg_info["type"] in symbol_table.bundle_types:
2254:                 arg_node, index, _ = parse_expression(tokens, index)
2255:                 actual_args.append(arg_node)
2256: 
2257:             elif arg_info["type"] in {"seed", "tree"}:
2258:                 arg_node, index, _ = parse_expression_branch(tokens, index)
2259:                 actual_args.append(arg_node)
2260: 
2261:             elif arg_info["type"] in {"vine", "leaf"} and tokens[index + 1].type == "`":
2262:                 arg_node, index, _ = parse_expression_branch(tokens, index)
2263:                 actual_args.append(arg_node)
2264:                 
2265:             else:
2266:                 actual_args.append(ASTNode("Value", arg_name, line=line))
2267:                 index += 1
2268:             
2269:         elif tokens[index].type in {"("}:
2270:             arg_node, index, _ = parse_expression_branch(tokens, index)
2271:             actual_args.append(arg_node)
2272: 
2273:         elif tokens[index].type == "stringlit":
2274:             arg_node, index, _ = parse_string_concatenation(tokens, index)
2275:             actual_args.append(arg_node)
2276: 
2277:         elif tokens[index].type in {"chrlit"}:
2278:             arg_node, index, _ = parse_expression_branch(tokens, index)
2279:             actual_args.append(arg_node)
2280: 
2281:         elif tokens[index].type in {"sunshine", "frost", "!"}:
2282:             arg_node, index, _ = parse_expression_branch(tokens, index)
2283:             actual_args.append(arg_node)
2284: 
2285:         elif tokens[index].type in {"++", "--"}:
2286:             arg_node, index, _ = parse_expression(tokens, index)
2287:             actual_args.append(arg_node)
2288: 
2289:         else:
2290:             raise SemanticError(f"Semantic Error: Expected valid argument after ',' in plant statement.", line)
2291: 
2292:     if placeholder_count > 15:
2293:         raise SemanticError(f"Semantic Error: Exceeded maximum amount of 15 arguments in plant statement.", line)
2294: 
2295:     if placeholder_count > 0 and placeholder_count != len(actual_args):
2296:         raise SemanticError(f"Semantic Error: Found {len(actual_args)} argument(s). Expected {placeholder_count} argument(s).", line)
2297:     
2298:     args.extend(actual_args)
2299: 
2300:     if tokens[index].type != ")":
2301:         raise SemanticError(f"Semantic Error: Expected ')' after {tokens[index-1].value} in plant statement.", line)
2302:     index += 1
2303: 
2304:     return PrintNode(args, line=line), index
```

`plant("GCD of", a,"and ",b, "is", result);` becomes a `PrintNode` with multiple children. Since the first string has no `{}` placeholder, the interpreter uses the multi-argument join behavior.

Source: `Backend/parser/builder.py:2412-2451`

```python
2412:         raise SemanticError(f"Syntax Error: Expected '(' after 'spring'.", line)
2413:     index += 1
2414: 
2415:     condition_expr, index, cond_type = parse_expression_branch(tokens, index)
2416: 
2417:     if cond_type != "branch":
2418:         raise SemanticError(f"Semantic Error: spring condition must be branch, got {cond_type}.", line)
2419:     
2420:     if tokens[index].type != ")":
2421:         raise SemanticError(f"Syntax Error: Expected ')' after 'spring' condition.", line)
2422:     
2423:     index += 1  
2424: 
2425:     symbol_table.enter_scope()
2426:     
2427:     condition_node = ASTNode("Condition", line=line)
2428:     condition_node.add_child(condition_expr)
2429: 
2430:     if_node = IfStatementNode(condition_node, line=line)
2431:     
2432:     if tokens[index].type == "{":
2433:         index += 1
2434: 
2435:         block_node = ASTNode("Block", line=line)
2436: 
2437:         while tokens[index].type != "}":
2438:             stmt, index = parse_statement(tokens, index, func_type)
2439:             if stmt:
2440:                 block_node.add_child(stmt)
2441: 
2442:         if tokens[index].type != "}":
2443:             raise SemanticError(f"Syntax Error: Expected '}}' after 'spring' block.", line)
2444:         index += 1
2445:         symbol_table.exit_scope()
2446:         if_node.add_child(block_node)
2447: 
2448:     else:
2449:         raise SemanticError(f"Syntax Error: Expected '{{' after 'spring' condition.", line)
2450: 
2451: 
```

`spring (b == 0)` becomes an `IfStatementNode` with a condition wrapper and a block.

Source: `Backend/parser/builder.py:2518-2560`

```python
2518: def parse_return(tokens, index, func_type):
2519:     line = tokens[index].line
2520:     index += 1
2521: 
2522:     if func_type == "empty":
2523:         if tokens[index].type not in {"}", ";"}:
2524:             raise SemanticError(f"Semantic Error: empty function must not return any value.", line)
2525:         return ReturnNode(None, line=line), index
2526: 
2527:     if tokens[index].type in {";", "}"}:
2528:         raise SemanticError(f"Semantic Error: Function expects to return a '{func_type}' value, but 'reclaim' has no return expression.", line)
2529: 
2530:     elif tokens[index].type == "id":
2531:         identifier = tokens[index].value
2532: 
2533:         if tokens[index+1].type == "(":
2534:             func_info = symbol_table.lookup_function(identifier)
2535: 
2536:             if isinstance(func_info, str):
2537:                 raise SemanticError(f"Semantic Error: Function '{identifier}' is not defined.", line)
2538: 
2539:             return_type = func_info["return_type"]
2540:             if return_type != func_type:
2541:                 raise SemanticError(f"Semantic Error: Function '{identifier}' returns '{return_type}', but expected '{func_type}'.", line)
2542: 
2543:             return_expr, index = parse_expression_type(tokens, index, func_type)
2544: 
2545:         else:
2546:             var_info = symbol_table.lookup_variable(identifier)
2547:             if isinstance(var_info, str):
2548:                 raise SemanticError(f"Semantic Error: Variable '{identifier}' used before declaration.", line)
2549: 
2550:             is_member_access = var_info["type"] in symbol_table.bundle_types and tokens[index+1].type == "."
2551:             if not is_member_access:
2552:                 if var_info["type"] not in [func_type, "seed", "tree"] and var_info["type"] != "seed" and var_info["type"] != "tree":                
2553:                     raise SemanticError(f"Semantic Error: Variable '{identifier}' is of type '{var_info['type']}'. Expected return value: '{func_type}'.", line)
2554: 
2555:             return_expr, index = parse_expression_type(tokens, index, func_type)
2556: 
2557:     else:  
2558:         return_expr, index = parse_expression_type(tokens, index, func_type)
2559: 
2560:     return ReturnNode(return_expr, line=line), index
```

`reclaim a;` and `reclaim gcd(b, a % b);` become `ReturnNode` objects. During execution, these nodes stop the current function call by raising a `ReturnValue` object.

## 6. Interpreter Dispatch: How It Chooses What To Run

Source: `Backend/interpreter/interpreter.py:121-190`

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
```

The interpreter uses `interpret(node)` as a dispatcher. It checks the node class or node type, then sends it to the correct method. For this GCD program, the important branches are:

| Node seen by `interpret()` | Line | Method called |
|---|---|---|
| `ProgramNode` | 122-123 | `eval_program()` |
| `FunctionDeclarationNode` | 140-141 | `eval_function_declaration()` |
| `VariableDeclarationNode` | 130-131 | `eval_variable_declaration()` |
| `AssignmentNode` | 132-133 | `eval_assignment()` |
| `BinaryOpNode` | 134-139 | `eval_binary_op()` |
| `PrintNode` | 142-143 | `eval_print()` |
| `ReturnNode` | 148-149 | `eval_return()` |
| `FunctionCallNode` | 150-151 | `eval_function_call()` |
| `IfStatementNode` | 168-169 | `eval_if_statement()` |
| `Input` node | 182-183 | `eval_input()` |
| `Identifier` node | 187-190 | Looks variable up by name |

## 7. Program Start: Register Functions Then Call root()

Source: `Backend/interpreter/interpreter.py:210-215`

```python
0210:     def eval_program(self, node):
0211:         for child in node.children:
0212:             self.interpret(child)
0213: 
0214:         main_call = FunctionCallNode("root", [], node.line)
0215:         return self.interpret(main_call)
```

Source: `Backend/interpreter/interpreter.py:716-733`

```python
0716:     def eval_function_declaration(self, node):
0717:         return_type = node.children[0].value
0718:         parameters_node = node.children[1]
0719:         func_name = node.value
0720: 
0721:         params = []
0722:         if parameters_node and len(parameters_node.children) > 0:
0723:             for param in parameters_node.children:
0724:                 if not hasattr(param, 'node_type') or param.node_type != 'Parameter':
0725:                     raise Exception(f"Invalid parameter: {param.value}")
0726:                 param_type = param.children[0].value
0727:                 param_name = param.children[1].value
0728:                 is_list = any(child.node_type == "ArrayParam" for child in param.children)
0729:                 params.append({"name": param_name, "type": param_type, "is_list": is_list})
0730: 
0731:         self.declare_function(func_name, return_type, params, node)
0732: 
0733:         return None
```

Execution starts with the whole `ProgramNode`.

Step-by-step:

1. `eval_program()` loops through the program children on lines 211-212.
2. First child is the `gcd` function declaration, so `eval_function_declaration()` stores it in `self.functions`.
3. Second child is the `root` function declaration, so it is also stored in `self.functions`.
4. After all declarations are registered, line 214 creates `FunctionCallNode("root", [])`.
5. Line 215 executes that root call.

After registration, the function table is conceptually:

| Function | Return type | Parameters | Stored body |
|---|---|---|---|
| `gcd` | `seed` | `seed a`, `seed b` | spring base case and recursive reclaim |
| `root` | `empty` or main/root type depending builder | none | input, function call, print, reclaim |

## 8. Calling root()

Source: `Backend/interpreter/interpreter.py:856-890`

```python
0856:     def eval_function_call(self, node):
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
```

When `root()` is called:

- Line 857 gets the function name: `root`.
- Line 858 evaluates arguments. Root has no arguments, so `args = []`.
- Line 860 finds `root` in `self.functions`.
- Line 873 enters a new function scope.
- Lines 876-881 declare parameters if any. Root has none.
- Line 884 executes the root body block.
- If `reclaim;` happens, line 886 catches the return and line 887 returns its value.

## 9. Root Variable Declarations

Source: `Backend/interpreter/interpreter.py:218-275`

```python
0218:     def eval_variable_declaration(self, node):
0219:         var_type = node.children[0].value
0220:         var_name = node.children[1].value
0221:         value_node = node.children[2] if len(node.children) > 2 else None
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
```

Source: `Backend/interpreter/interpreter.py:50-61`

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
```

Root executes:

```gal
seed a;
seed b;
seed result;
```

For each declaration:

- Lines 219-221 read type, name, and optional value node.
- Lines 224-230 define default values for each GAL type.
- Because `seed a;`, `seed b;`, and `seed result;` have no explicit value, they receive default `0`.
- Lines 55-61 store the variable record in the current scope.

Root scope after declarations:

| Variable | Type | Initial value | Stored in |
|---|---|---|---|
| `a` | `seed` | 0 | `self.scopes[-1]` |
| `b` | `seed` | 0 | `self.scopes[-1]` |
| `result` | `seed` | 0 | `self.scopes[-1]` |

## 10. First plant() And water()

Source: `Backend/interpreter/interpreter.py:752-798`

```python
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
```

Source: `Backend/interpreter/interpreter.py:800-805`

```python
0800:     def eval_formatted_string(self, node):
0801:         value = node.value
0802:         if value.startswith('"') and value.endswith('"'):
0803:             value = value[1:-1]
0804: 
0805:         value = value.replace(r'\\', '\\')
```

For:

```gal
plant("Enter first number: ");
```

- Line 752 enters `eval_print()`.
- Line 756 gets the first print argument.
- Line 758 interprets the string node.
- Lines 800-805 remove quotes and process escape basics in `eval_formatted_string()`.
- Line 798 sends the string to `self.plant()`.
- Line 745 emits output to the UI.

Source: `Backend/interpreter/interpreter.py:1312-1346`

```python
1312:     def emit_input_request(self, var_name, prompt):
1313:         self.socketio.emit('input_required', {'prompt': prompt, 'variable': var_name})
1314: 
1315:     def provide_input(self, var_name, input_value):
1316:         evt = self.input_events.get(var_name)
1317:         if evt is None:
1318:             self.input_values[var_name] = input_value
1319:             return
1320:         if _USE_EVENTLET:
1321:             evt.send(input_value)
1322:         else:
1323:             self.input_values[var_name] = input_value
1324:             evt.set()
1325: 
1326:     def wait_for_input(self, var_name):
1327:         if var_name in self.input_values:
1328:             return self.input_values.pop(var_name)
1329: 
1330:         if _USE_EVENTLET:
1331:             evt = _ev.Event()
1332:             self.input_events[var_name] = evt
1333:             value = evt.wait()
1334:             self.input_events.pop(var_name, None)
1335:             if getattr(self, '_cancelled', False):
1336:                 raise _CancelledError()
1337:             return value
1338:         else:
1339:             event = threading.Event()
1340:             self.input_events[var_name] = event
1341:             event.wait()
1342:             if getattr(self, '_cancelled', False):
1343:                 raise _CancelledError()
1344:             value = self.input_values.pop(var_name, None)
1345:             self.input_events.pop(var_name, None)
1346:             return value
```

Source: `Backend/interpreter/interpreter.py:1348-1396`

```python
1348:     def eval_input(self, node):
1349:         parent_node = node.parent
1350:         if isinstance(parent_node, VariableDeclarationNode):
1351:             var_name = parent_node.children[1].value
1352:             var_type = parent_node.children[0].value
1353:         
1354:         elif isinstance(parent_node, AssignmentNode):
1355:             target = parent_node.children[0]
1356:             if isinstance(target, ListAccessNode):
1357:                 current = target
1358:                 while hasattr(current, 'node_type') and current.node_type == "ListAccess":
1359:                     current = current.children[0].value
1360:                 var_name = current if isinstance(current, str) else str(current)
1361:                 var_type = self.lookup_variable(var_name)["type"]  # type: ignore
1362:             else:
1363:                 var_name = target.value
1364:                 var_type = self.lookup_variable(var_name)["type"]  # type: ignore
1365: 
1366:         else:
1367:             var_name = "_input"
1368:             if node.value and "(" in node.value:
1369:                 inner = node.value.split("(")[1].rstrip(")")
1370:                 var_type = inner if inner in {"seed", "tree", "leaf", "branch", "vine"} else "vine"
1371:             else:
1372:                 var_type = "vine"
1373: 
1374:         prompt = f"Input for {var_name}: "
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
```

Source: `Backend/interpreter/interpreter.py:346-358`

```python
0346:     def eval_assignment(self, node):
0347:         target_node = node.children[0]
0348:         value_node = node.children[1]
0349: 
0350:         if value_node.node_type == "List":
0351:             value = []
0352:             for val in value_node.children:
0353:                 item = self.interpret(val)
0354:                 value.append(item)
0355:         else:
0356:             value = self.interpret(value_node)
0357:             if isinstance(value_node, AppendNode) or isinstance(value_node, InsertNode) or isinstance(value_node, RemoveNode):
0358:                 return
```

Source: `Backend/interpreter/interpreter.py:489-505`

```python
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
```

For:

```gal
a = water();
```

The interpreter executes an assignment node.

Detailed flow:

1. `eval_assignment()` starts at line 346.
2. Line 347 gets target node `a`.
3. Line 348 gets value node `Input/water()`.
4. Line 356 calls `self.interpret(value_node)`, which routes to `eval_input()`.
5. In `eval_input()`, lines 1354-1364 detect that the parent is an `AssignmentNode` and target is `a`.
6. Line 1364 looks up `a` and discovers its type is `seed`.
7. Lines 1374-1380 emit an input request and wait for the UI.
8. Server receives the user input through `capture_input` in `server.py` lines 482-489.
9. `provide_input()` lines 1315-1324 wakes the waiting input event.
10. Since type is `seed`, lines 1385-1395 convert the text input `"48"` into integer `48`.
11. Back in `eval_assignment()`, lines 489-505 store `a = 48`.

After the first input:

| Variable | Value |
|---|---|
| `a` | 48 |
| `b` | 0 |
| `result` | 0 |

## 11. Second plant() And water()

The second input follows the same flow:

```gal
plant("Enter second number: ");
b = water();
```

With sample input `18`, `eval_input()` converts `"18"` into integer `18`, then `eval_assignment()` stores it in `b`.

Root scope after both inputs:

| Variable | Value |
|---|---|
| `a` | 48 |
| `b` | 18 |
| `result` | 0 |

## 12. result = gcd(a, b)

Now root executes:

```gal
result = gcd(a, b);
```

This is an assignment whose right side is a `FunctionCallNode`.

Source: `Backend/interpreter/interpreter.py:75-103`

```python
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
0093: 
0094: 
0095:     def declare_function(self, name, return_type, params, node=None):
0096:         if name in self.functions:
0097:             return f"Semantic Error: Function '{name}' already declared."
0098:         self.functions[name] = {"return_type": return_type, "params": params, "node": node}
0099: 
0100:     def lookup_function(self, name):
0101:         if name in self.functions:
0102:             return self.functions[name]
0103:         return f"Semantic Error: Function '{name}' is not defined."
```

Source: `Backend/interpreter/interpreter.py:856-890`

```python
0856:     def eval_function_call(self, node):
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
```

Flow for the first `gcd(a, b)` call:

1. `eval_assignment()` line 356 interprets the right side.
2. `interpret()` sees `FunctionCallNode` and calls `eval_function_call()` line 856.
3. Line 857 reads function name `gcd`.
4. Line 858 evaluates arguments `a` and `b`. It uses identifier lookup to get `48` and `18`.
5. Line 860 uses `lookup_function()` to find the stored `gcd` declaration.
6. Line 873 creates a new function scope.
7. Lines 876-881 declare local parameter variables for this call: `a = 48`, `b = 18`.
8. Line 884 executes the body of `gcd`.

## 13. How spring(b == 0) Runs Inside gcd

Source: `Backend/interpreter/interpreter.py:1074-1115`

```python
1074:     def eval_if_statement(self, node):
1075:         condition_result = self.interpret(node.children[0].children[0])
1076:         self.enter_scope()
1077: 
1078: 
1079:         try:
1080:             if condition_result:
1081:                 self.eval_block(node.children[1])
1082:             
1083:             else:
1084:                 current_node = 2
1085:                 while current_node < len(node.children):
1086:                     
1087:                     elif_node = node.children[current_node]
1088: 
1089:                     if elif_node.node_type == "ElseIfStatement":
1090:                         elif_condition_result = self.interpret(elif_node.children[0].children[0])
1091: 
1092:                         if not isinstance(elif_condition_result, bool):
1093:                             raise InterpreterError(f"Runtime Error: Condition must be a boolean. Got '{condition_result}'", node.line)
1094:                         
1095:                         if elif_condition_result:
1096:                             try:
1097:                                 self.enter_scope()
1098:                                 self.eval_block(elif_node.children[1])
1099:                             finally:
1100:                                 self.exit_scope()
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
```

Source: `Backend/interpreter/interpreter.py:510-600`

```python
0510:     def eval_binary_op(self, node):
0511:         left = self.interpret(node.children[0])
0512:         right = self.interpret(node.children[1])
0513:         operator = node.value
0514: 
0515:         if operator == '`':
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
```

Inside each `gcd` call, the first statement is:

```gal
spring (b == 0) {
    reclaim a;
}
```

The condition `b == 0` is a `BinaryOpNode`.

- `eval_if_statement()` line 1075 calls `self.interpret()` on the condition.
- `eval_binary_op()` lines 511-513 evaluate left, right, and operator.
- Line 599 checks `==`.
- Line 600 returns `left == right`.

For the first call:

```text
b = 18
18 == 0 -> False
```

Because it is false, line 1083 goes to the else path. Since there is no `bud` or `wither` inside the function, the if statement ends and execution continues to the next statement.

## 14. How reclaim gcd(b, a % b) Runs

Source: `Backend/interpreter/interpreter.py:851-853`

```python
0851:     def eval_return(self, node):
0852:         value = self.interpret(node.children[0]) if node.children else None
0853:         raise ReturnValue(value)
```

Source: `Backend/interpreter/interpreter.py:586-598`

```python
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
```

The next statement in `gcd` is:

```gal
reclaim gcd(b, a % b);
```

`eval_return()` line 852 interprets the return expression first. The return expression is another function call.

For the first call, current local values are:

```text
a = 48
b = 18
```

The recursive call is:

```text
gcd(b, a % b)
gcd(18, 48 % 18)
```

Modulo is handled in `eval_binary_op()`:

- Line 586 checks operator `%`.
- Lines 596-597 prevent modulo by zero.
- Line 598 returns `left % right`.

So:

```text
48 % 18 = 12
```

The next recursive call becomes:

```text
gcd(18, 12)
```

## 15. Complete Recursive Call Stack

| Depth | Call | `b == 0`? | `a % b` | Next action |
|---|---|---|---|---|
| 1 | `gcd(48, 18)` | `18 == 0` -> false | `48 % 18 = 12` | return `gcd(18, 12)` |
| 2 | `gcd(18, 12)` | `12 == 0` -> false | `18 % 12 = 6` | return `gcd(12, 6)` |
| 3 | `gcd(12, 6)` | `6 == 0` -> false | `12 % 6 = 0` | return `gcd(6, 0)` |
| 4 | `gcd(6, 0)` | `0 == 0` -> true | not needed | run `reclaim a;`, return `6` |

Each recursive call has its own function scope. That means the parameter names `a` and `b` are reused, but each call has its own local values.

| Call depth | Local `a` | Local `b` | Scope meaning |
|---|---|---|---|
| 1 | 48 | 18 | First gcd call from root |
| 2 | 18 | 12 | Recursive call from depth 1 |
| 3 | 12 | 6 | Recursive call from depth 2 |
| 4 | 6 | 0 | Base case call |

## 16. Base Case: reclaim a

At depth 4:

```text
gcd(6, 0)
```

The condition is true:

```text
b == 0
0 == 0 -> true
```

`eval_if_statement()` line 1080 enters the true branch, and line 1081 evaluates the spring block. That block contains:

```gal
reclaim a;
```

`eval_return()` line 852 interprets `a`, which looks up the current local parameter value `6`. Then line 853 raises `ReturnValue(6)`. That is how the interpreter stops the current function body immediately.

Source: `Backend/interpreter/interpreter.py:883-887`

```python
0883:             try:
0884:                 self.eval_block(function_node.children[2])
0885: 
0886:             except ReturnValue as ret:
0887:                 return ret.value
```

The raised return value is caught by `eval_function_call()`:

- Line 884 is executing the function body.
- Line 886 catches `ReturnValue`.
- Line 887 returns `ret.value` to the caller.

Return unwinding:

```text
gcd(6, 0) returns 6
gcd(12, 6) returns 6
gcd(18, 12) returns 6
gcd(48, 18) returns 6
```

## 17. Storing The Result

After `gcd(a, b)` returns `6`, the interpreter goes back to:

```gal
result = gcd(a, b);
```

`eval_assignment()` now stores the returned value in `result`.

Source: `Backend/interpreter/interpreter.py:489-505`

```python
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
```

At this moment, root scope becomes:

| Variable | Value |
|---|---|
| `a` | 48 |
| `b` | 18 |
| `result` | 6 |

## 18. Final plant() Output

The final print statement is:

```gal
plant("GCD of", a,"and ",b, "is", result);
```

In your interpreter, this uses the multi-argument print path because the first string `"GCD of"` does not contain `{}` placeholders.

Source: `Backend/interpreter/interpreter.py:752-798`

```python
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
```

Detailed print behavior:

- Line 758 evaluates the first argument: `"GCD of"`.
- Line 764 checks if the first string contains `{}`. It does not.
- Line 786 sees there are multiple arguments.
- Line 787 starts `parts = ["GCD of"]`.
- Lines 788-794 evaluate and append `a`, `"and "`, `b`, `"is"`, and `result`.
- Line 795 prints `' '.join(parts)`.

Because `"and "` already contains a trailing space and line 795 adds spaces between all parts, the actual output has two spaces before `18`:

```text
GCD of 48 and  18 is 6
```

Cleaner version if you want single spaces:

```gal
plant("GCD of", a, "and", b, "is", result);
```

Or using placeholders:

```gal
plant("GCD of {} and {} is: {}\n", a, b, result);
```

## 19. Final reclaim In root

The last statement is:

```gal
reclaim;
```

This becomes a `ReturnNode` with no value. `eval_return()` line 852 sets value to `None`, then line 853 raises `ReturnValue(None)`. `eval_function_call()` catches it at line 886 and returns from `root()`. Program execution is complete.

## 20. Actual Simulated Output

With user inputs `48` and `18`, the backend test produced these output events:

```text
Enter first number: 
[input_required: Input for a]
Enter second number: 
[input_required: Input for b]
GCD of 48 and  18 is 6
```

The `input_required` events are not normal printed text from `plant()`. They are UI events emitted by `eval_input()` so the frontend can ask the user for a value.

## 21. Whole Interpreter Simulation Summary

| Step | GAL code | Interpreter method | Result |
|---|---|---|---|
| 1 | `pollinate seed gcd(...)` | `eval_function_declaration()` line 716 | Stores `gcd` in `self.functions`. |
| 2 | `root() { ... }` | `eval_function_declaration()` line 716 | Stores `root` in `self.functions`. |
| 3 | Program start | `eval_program()` line 210 | Creates and executes `FunctionCallNode("root")`. |
| 4 | `seed a; seed b; seed result;` | `eval_variable_declaration()` line 218 | Creates variables with default `0`. |
| 5 | `plant("Enter first number: ")` | `eval_print()` line 752 | Outputs prompt. |
| 6 | `a = water();` | `eval_input()` line 1348 + `eval_assignment()` line 346 | Stores input `48` in `a`. |
| 7 | `b = water();` | `eval_input()` line 1348 + `eval_assignment()` line 346 | Stores input `18` in `b`. |
| 8 | `result = gcd(a, b);` | `eval_function_call()` line 856 | Runs recursive GCD and returns `6`. |
| 9 | `spring (b == 0)` | `eval_if_statement()` line 1074 | Controls recursion base case. |
| 10 | `a % b` | `eval_binary_op()` line 586 | Computes remainder for next recursive call. |
| 11 | `reclaim a;` | `eval_return()` line 851 | Returns final answer `6`. |
| 12 | Final `plant(...)` | `eval_print()` line 752 | Outputs `GCD of 48 and  18 is 6`. |
| 13 | `reclaim;` | `eval_return()` line 851 | Stops `root()` and completes program. |

## 22. Defense Script Taglish

Pwede mong sabihin sa defense:

```text
Sa interpreter part, hindi na raw source code ang binabasa ng system. AST nodes na siya. Una, sa eval_program, nireregister muna niya yung pollinate function na gcd at yung root function. Pag tapos na maregister, automatic niyang tatawagin yung root.

Sa root, yung seed a, seed b, at seed result ay ginagawa niyang variables sa current scope. Then yung plant ay dumadaan sa eval_print para mag-output sa UI. Yung water naman ay dumadaan sa eval_input. Dahil naka-assign siya sa variable a or b, tinitingnan ng interpreter yung type ng variable. Since seed siya, kino-convert niya yung input string into integer.

Pag dumating sa result = gcd(a, b), tatawagin niya yung eval_function_call. Doon gumagawa siya ng bagong scope para sa parameters ng gcd. Sa unang call, a is 48 and b is 18. Chine-check niya yung spring b == 0. Kapag false, gagawin niya yung recursive reclaim gcd(b, a % b). Kaya magiging gcd(18, 12), then gcd(12, 6), then gcd(6, 0).

Pag gcd(6, 0), true na yung b == 0 kaya reclaim a, meaning return 6. Yung return value na 6 babalik pataas sa lahat ng recursive calls hanggang mastore siya sa result. Finally, ipiprint niya yung GCD message, then reclaim sa root to end the program.
```

## 23. Quick Line Reference Table

| File | Line(s) | Purpose |
|---|---|---|
| `Backend/server.py` | 411-489 | Interactive run path and input capture. |
| `Backend/parser/builder.py` | 195-300 | Builds function declarations. |
| `Backend/parser/builder.py` | 1909-1968 | Builds function calls such as `gcd(a, b)`. |
| `Backend/parser/builder.py` | 1972-2057 | Builds `water()` input nodes. |
| `Backend/parser/builder.py` | 2063-2304 | Builds `plant()` print nodes. |
| `Backend/parser/builder.py` | 2412-2451 | Builds `spring` if nodes. |
| `Backend/parser/builder.py` | 2518-2560 | Builds `reclaim` return nodes. |
| `Backend/interpreter/interpreter.py` | 121-190 | Main node dispatcher. |
| `Backend/interpreter/interpreter.py` | 210-215 | Registers declarations and calls `root`. |
| `Backend/interpreter/interpreter.py` | 716-733 | Stores function declarations. |
| `Backend/interpreter/interpreter.py` | 856-890 | Executes function calls and catches returns. |
| `Backend/interpreter/interpreter.py` | 218-275 | Executes variable declarations. |
| `Backend/interpreter/interpreter.py` | 346-505 | Executes assignments. |
| `Backend/interpreter/interpreter.py` | 510-600 | Executes binary operations including `==`, `%`, and arithmetic. |
| `Backend/interpreter/interpreter.py` | 752-798 | Executes `plant()`. |
| `Backend/interpreter/interpreter.py` | 851-853 | Executes `reclaim`. |
| `Backend/interpreter/interpreter.py` | 1074-1115 | Executes `spring/bud/wither`. |
| `Backend/interpreter/interpreter.py` | 1312-1396 | Handles interactive input and conversion. |