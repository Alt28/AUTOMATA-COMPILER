# Interpreter Line-by-Line Code Explanation

Detailed explanation of `Backend/interpreter/interpreter.py`, organized for defense study.

Project path: `C:\Users\clarence\Downloads\AUTOMATA-COMPILER-main (1)\AUTOMATA-COMPILER-main\my GAL code`

Source file: `Backend/interpreter/interpreter.py`

Generated: 2026-06-02 23:48

## 1. How To Study The Interpreter

The interpreter executes the AST after lexer, parser, builder, and semantic analyzer have already succeeded. The most important method is `interpret()`, because it is the dispatcher that receives an AST node and sends it to the correct evaluator.

General runtime flow:

```text
interp.interpret(ast)
-> interpret(ProgramNode)
-> eval_program()
-> register declarations/functions
-> create and call root()
-> eval_function_call(root)
-> eval_block(root body)
-> each statement goes back to interpret()
-> matching eval method executes the statement
```

## 2. Python Concepts Used In This File

| Concept | Meaning In This Interpreter |
|---|---|
| `self` | The current Interpreter object. It lets a method access shared runtime state like `self.scopes`, `self.functions`, and `self.socketio`. |
| `node` | The current AST node being executed. |
| `node.children` | List of child AST nodes. Example: assignment has target child and value child. |
| `node.value` | Stored value of a node, such as an identifier name, operator, or literal. |
| `isinstance(node, X)` | Checks what kind of AST node is being interpreted. |
| `dict {}` | Key-value storage, used for variables, functions, scopes, and bundles. |
| `list []` | Ordered collection, used for output, scopes, parameters, arguments, and loop stack. |
| `raise ReturnValue` | Special control flow for `reclaim`. |
| `try/finally` | Ensures cleanup such as leaving scopes and loops. |

## 3. Function Map

| Section/Function | Lines | Purpose |
|---|---|---|
| Module Setup | 1-24 | File/class setup. |
| Interpreter Class | 25-25 | File/class setup. |
| __init__ | 26-49 | Initializes the interpreter runtime memory: output channel, loop flags, input handling, variable scopes, function table, and bundle table. |
| declare_variable | 50-74 | Creates a variable record in the current runtime scope. |
| lookup_variable | 75-84 | Searches the active scopes and variable table for a variable name. |
| set_variable | 85-94 | Updates an existing variable value inside the nearest active scope. |
| declare_function | 95-99 | Stores a function declaration so it can be called later. |
| lookup_function | 100-105 | Finds a stored function declaration by name. |
| enter_scope | 106-109 | Creates a new local scope for functions, blocks, loops, or conditionals. |
| exit_scope | 110-120 | Removes the current local scope after leaving a function/block. |
| interpret | 121-209 | Main dispatcher. It receives any AST node and routes it to the correct evaluator method. |
| eval_program | 210-217 | Executes the whole program node: registers top-level declarations and automatically calls root(). |
| eval_variable_declaration | 218-236 | Executes variable declarations and stores default or evaluated initial values. |
| materialize | 237-292 | Runtime helper/evaluator. |
| eval_bundle_definition | 293-295 | Registers bundle/struct member definitions. |
| _build_bundle_defaults | 296-306 | Creates default runtime values for all members of a bundle type. |
| eval_member_access | 307-327 | Reads a bundle member value like student.age. |
| eval_array_member_access | 328-337 | Reads a member from a bundle stored inside an array/list. |
| eval_sturdy_declaration | 338-345 | Executes fertile/constant declarations. |
| eval_assignment | 346-509 | Executes assignments, including normal variables, lists, bundle members, and input assignments. |
| eval_binary_op | 510-677 | Evaluates binary expressions such as +, -, *, /, %, ==, &&, and \|\|. |
| _parse_literal | 678-715 | Converts literal text or token values into Python runtime values. |
| eval_function_declaration | 716-734 | Stores function declarations into the interpreter function table. |
| eval_block | 735-743 | Executes every statement inside a block one by one. |
| plant | 744-746 | Sends output text to the frontend through Socket.IO or the output collector. |
| plant_out | 747-751 | Sends and stores output text for collector-style execution. |
| eval_print | 752-799 | Executes plant() statements, including placeholder formatting and multi-argument printing. |
| eval_formatted_string | 800-814 | Removes string quotes and converts escape sequences such as \n and \t. |
| eval_list | 815-824 | Evaluates list/array literal values. |
| eval_list_access | 825-850 | Reads a value from a list or string using an index. |
| eval_return | 851-855 | Executes reclaim by raising ReturnValue to stop the current function. |
| eval_function_call | 856-895 | Executes a function call: evaluates arguments, creates scope, binds parameters, runs body, and catches reclaim. |
| eval_append | 896-904 | Executes list append behavior. |
| eval_insert | 905-922 | Executes list insertion behavior. |
| eval_remove | 923-940 | Executes list removal behavior. |
| eval_unaryop | 941-1043 | Executes unary operators like ++, --, !, and ~. |
| eval_cast | 1044-1063 | Converts values to a requested GAL type. |
| eval_soil | 1064-1068 | Converts a string variable to lowercase. |
| eval_bloom | 1069-1073 | Converts a string variable to uppercase. |
| eval_if_statement | 1074-1116 | Executes spring/bud/wither conditional logic. |
| eval_for_loop | 1117-1166 | Executes cultivate loops. |
| eval_while_loop | 1167-1200 | Executes grow loops. |
| eval_do_while_loop | 1201-1231 | Executes tend/wither style do-while loops. |
| eval_break | 1232-1237 | Executes prune by setting the break flag. |
| trigger_break | 1238-1240 | Turns on the runtime break flag. |
| break_triggered | 1241-1243 | Checks if a break/prune was triggered. |
| enter_loop | 1244-1248 | Records that the interpreter is currently inside a loop. |
| exit_loop | 1249-1254 | Removes the current loop marker and resets loop flags. |
| eval_continue | 1255-1260 | Executes skip by setting the continue flag. |
| continue_triggered | 1261-1263 | Checks if skip/continue was triggered. |
| trigger_continue | 1264-1267 | Turns on the runtime continue flag. |
| eval_switch | 1268-1311 | Executes switch/variety style branching. |
| emit_input_request | 1312-1314 | Asks the frontend UI for input when water() is executed. |
| provide_input | 1315-1325 | Receives user input from the frontend and wakes the waiting interpreter. |
| wait_for_input | 1326-1347 | Pauses execution until the frontend supplies an input value. |
| eval_input | 1348-1442 | Executes water(), determines expected type, waits for input, and converts it. |

## 4. Example Program Simulation

Example input values: `a = 5`, `b = 7`.



```gal
root() {
    seed a;
    seed b;
    seed sum;

    plant("Enter 1st number: ");
    water(a);

    plant("Enter 2nd number: ");
    water(b);

    sum = a + b;

    plant("Sum: {}", sum);
    reclaim;
}
```

| Step | Interpreter route | Runtime effect |
|---|---|---|
| 1 | `interpret(ProgramNode)` -> `eval_program()` | Registers root and creates a call to `root()`. |
| 2 | `eval_function_call(root)` | Creates root scope and executes root block. |
| 3 | `eval_variable_declaration()` for `seed a;` | Stores `a = 0`. |
| 4 | `eval_variable_declaration()` for `seed b;` | Stores `b = 0`. |
| 5 | `eval_variable_declaration()` for `seed sum;` | Stores `sum = 0`. |
| 6 | `eval_print()` | Outputs `Enter 1st number:`. |
| 7 | `eval_input()` + `eval_assignment()` | Receives input `5`, converts to seed, stores `a = 5`. |
| 8 | `eval_print()` | Outputs `Enter 2nd number:`. |
| 9 | `eval_input()` + `eval_assignment()` | Receives input `7`, converts to seed, stores `b = 7`. |
| 10 | `eval_assignment()` + `eval_binary_op()` | Computes `a + b`, so `5 + 7 = 12`, then stores `sum = 12`. |
| 11 | `eval_print()` | Outputs `Sum: 12`. |
| 12 | `eval_return()` | `reclaim;` stops root and ends the program. |

Variable table during the sample:

| Moment | a | b | sum |
|---|---|---|---|
| After declarations | 0 | 0 | 0 |
| After `water(a)` | 5 | 0 | 0 |
| After `water(b)` | 5 | 7 | 0 |
| After `sum = a + b` | 5 | 7 | 12 |

## 5. Line-By-Line Explanation Of interpreter.py

### Module Setup - Lines 1-24

Purpose: File/class setup or runtime support block.

Process flow:

- Imports AST node classes and runtime error classes.

- Configures recursion and eventlet input handling.

- Prepares the Interpreter class dependencies.

Code:

```python
0001: 
0002: 
0003: from shared.ast_nodes import *
0004: 
0005: import threading
0006: import sys
0007: 
0008: sys.setrecursionlimit(10000)
0009: 
0010: try:
0011:     import eventlet.event as _ev
0012:     _USE_EVENTLET = True
0013: except ImportError:
0014:     _USE_EVENTLET = False
0015: 
0016: 
0017: from semantic.errors import SemanticError  # noqa: F401 - some runtime checks raise it
0018: from interpreter.errors import (  # noqa: F401 - runtime-specific error classes
0019:     ReturnValue,
0020:     _CancelledError,
0021:     InterpreterError,
0022:     InterpreterInputRequest,
0023: )
0024: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 1 | `` | Blank line used to separate code sections for readability. |
| 2 | `` | Blank line used to separate code sections for readability. |
| 3 | `from shared.ast_nodes import *` | Imports modules/classes needed by the interpreter. |
| 4 | `` | Blank line used to separate code sections for readability. |
| 5 | `import threading` | Imports modules/classes needed by the interpreter. |
| 6 | `import sys` | Imports modules/classes needed by the interpreter. |
| 7 | `` | Blank line used to separate code sections for readability. |
| 8 | `sys.setrecursionlimit(10000)` | Raises Python recursion limit so recursive GAL functions can run deeper before hitting Python's default limit. |
| 9 | `` | Blank line used to separate code sections for readability. |
| 10 | `try:` | Starts a protected block where errors can be handled by except/finally. |
| 11 | `    import eventlet.event as _ev` | Imports modules/classes needed by the interpreter. |
| 12 | `    _USE_EVENTLET = True` | Assigns/computes a value and stores it in `_USE_EVENTLET` for later use in this method. |
| 13 | `except ImportError:` | Handles the case where eventlet is not installed. |
| 14 | `    _USE_EVENTLET = False` | Assigns/computes a value and stores it in `_USE_EVENTLET` for later use in this method. |
| 15 | `` | Blank line used to separate code sections for readability. |
| 16 | `` | Blank line used to separate code sections for readability. |
| 17 | `from semantic.errors import SemanticError  # noqa: F401 - some runtime checks raise it` | Imports modules/classes needed by the interpreter. |
| 18 | `from interpreter.errors import (  # noqa: F401 - runtime-specific error classes` | Imports modules/classes needed by the interpreter. |
| 19 | `    ReturnValue,` | Runtime support statement used by the interpreter. |
| 20 | `    _CancelledError,` | Runtime support statement used by the interpreter. |
| 21 | `    InterpreterError,` | Runtime support statement used by the interpreter. |
| 22 | `    InterpreterInputRequest,` | Runtime support statement used by the interpreter. |
| 23 | `)` | Calls a function/method to perform part of the runtime operation. |
| 24 | `` | Blank line used to separate code sections for readability. |

### Interpreter Class - Lines 25-25

Purpose: File/class setup or runtime support block.

Process flow:

- Defines the runtime object that will hold all interpreter state.

- All eval methods below belong to this class.

Code:

```python
0025: class Interpreter:
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 25 | `class Interpreter:` | Defines the Interpreter class, the runtime engine that executes AST nodes. |

### __init__ - Lines 26-49

Purpose: Initializes the interpreter runtime memory: output channel, loop flags, input handling, variable scopes, function table, and bundle table.

Process flow:

- Initializes the interpreter runtime memory: output channel, loop flags, input handling, variable scopes, function table, and bundle table.

Code:

```python
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
0049: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 26 | `    def __init__(self, socketio=None):` | Initializes the interpreter runtime memory: output channel, loop flags, input handling, variable scopes, function table, and bundle table. |
| 27 | `        self.output = []` | Creates a list used to collect runtime values. |
| 28 | `        self.socketio = socketio` | Stores/updates frontend communication object used for plant() and water() events. |
| 29 | `` | Blank line used to separate code sections for readability. |
| 30 | `        self.loop_stack = []` | Creates a list used to collect runtime values. |
| 31 | `        self.break_flag = False` | Stores/updates flag set when prune/break is triggered. |
| 32 | `        self.continue_flag = False` | Stores/updates flag set when skip/continue is triggered. |
| 33 | `` | Blank line used to separate code sections for readability. |
| 34 | `        self.input_required = False` | Stores/updates flag showing the program is waiting for water() input. |
| 35 | `        self.input_events = {}` | Creates a dictionary used for key-value runtime storage. |
| 36 | `        self.input_values = {}` | Creates a dictionary used for key-value runtime storage. |
| 37 | `` | Blank line used to separate code sections for readability. |
| 38 | `        self.current_node = None` | Stores/updates optional tracker for the current AST node. |
| 39 | `        self.current_parent = None` | Stores/updates optional tracker for the current parent AST node. |
| 40 | `` | Blank line used to separate code sections for readability. |
| 41 | `        self.variables = {}` | Creates a dictionary used for key-value runtime storage. |
| 42 | `        self.global_variables = {}` | Creates a dictionary used for key-value runtime storage. |
| 43 | `        self.functions = {}` | Creates a dictionary used for key-value runtime storage. |
| 44 | `        self.scopes = [{}]` | Creates a list used to collect runtime values. |
| 45 | `        self.current_func_name = None` | Stores/updates name of the function currently being executed. |
| 46 | `        self.function_variables = {}` | Creates a dictionary used for key-value runtime storage. |
| 47 | `        self.bundle_types = {}` | Creates a dictionary used for key-value runtime storage. |
| 48 | `` | Blank line used to separate code sections for readability. |
| 49 | `` | Blank line used to separate code sections for readability. |

### declare_variable - Lines 50-74

Purpose: Creates a variable record in the current runtime scope.

Process flow:

- Creates a variable record in the current runtime scope.

Code:

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
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 50 | `    def declare_variable(self, name, type_, value=None, is_list=False, is_fertile=False):` | Creates a variable record in the current runtime scope. |
| 51 | `        scope = self.scopes[-1]` | Assigns/computes a value and stores it in `scope` for later use in this method. |
| 52 | `        current_func = self.current_func_name` | Assigns/computes a value and stores it in `current_func` for later use in this method. |
| 53 | `    ` | Blank line used to separate code sections for readability. |
| 54 | `` | Blank line used to separate code sections for readability. |
| 55 | `        if name not in self.scopes[-1]:` | Conditional branch that decides which runtime path should run. |
| 56 | `            scope[name] = {` | Creates a dictionary used for key-value runtime storage. |
| 57 | `                "type": type_,  ` | Runtime support statement used by the interpreter. |
| 58 | `                "value": value,` | Runtime support statement used by the interpreter. |
| 59 | `                "is_list": is_list,` | Runtime support statement used by the interpreter. |
| 60 | `                "is_fertile": is_fertile` | Runtime support statement used by the interpreter. |
| 61 | `                }` | Runtime support statement used by the interpreter. |
| 62 | `        else:` | Fallback branch used when the previous if/elif conditions were false. |
| 63 | `            if name in self.global_variables:` | Conditional branch that decides which runtime path should run. |
| 64 | `                return f"Semantic Error: Variable '{name}' already declared."` | Returns the computed value/result from this method to its caller. |
| 65 | `            ` | Blank line used to separate code sections for readability. |
| 66 | `            self.variables[name] = {` | Creates a dictionary used for key-value runtime storage. |
| 67 | `                "type": type_,` | Runtime support statement used by the interpreter. |
| 68 | `                "value": value,` | Runtime support statement used by the interpreter. |
| 69 | `                "is_list": is_list,` | Runtime support statement used by the interpreter. |
| 70 | `                "is_fertile": is_fertile` | Runtime support statement used by the interpreter. |
| 71 | `            }` | Runtime support statement used by the interpreter. |
| 72 | `            self.global_variables[name] = self.variables[name]` | Stores/updates table for global variables. |
| 73 | `        ` | Blank line used to separate code sections for readability. |
| 74 | `` | Blank line used to separate code sections for readability. |

### lookup_variable - Lines 75-84

Purpose: Searches the active scopes and variable table for a variable name.

Process flow:

- Searches the active scopes and variable table for a variable name.

Code:

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
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 75 | `    def lookup_variable(self, name):` | Searches the active scopes and variable table for a variable name. |
| 76 | `        for i, scope in enumerate(reversed(self.scopes)):` | Loops through a collection of values/items. |
| 77 | `            if name in scope:` | Conditional branch that decides which runtime path should run. |
| 78 | `                return scope[name]` | Returns the computed value/result from this method to its caller. |
| 79 | `        ` | Blank line used to separate code sections for readability. |
| 80 | `        if name in self.variables:` | Conditional branch that decides which runtime path should run. |
| 81 | `            return self.variables[name]` | Calls variables() on the same interpreter object and returns its result to the caller. |
| 82 | `` | Blank line used to separate code sections for readability. |
| 83 | `        return f"Semantic Error: Variable '{name}' used before declaration."` | Returns the computed value/result from this method to its caller. |
| 84 | `    ` | Blank line used to separate code sections for readability. |

### set_variable - Lines 85-94

Purpose: Updates an existing variable value inside the nearest active scope.

Process flow:

- Updates an existing variable value inside the nearest active scope.

Code:

```python
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
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 85 | `    def set_variable(self, name, value):` | Updates an existing variable value inside the nearest active scope. |
| 86 | `        for i in reversed(range(len(self.scopes))):` | Loops through a collection of values/items. |
| 87 | `            scope = self.scopes[i]` | Assigns/computes a value and stores it in `scope` for later use in this method. |
| 88 | `            if name in scope:` | Conditional branch that decides which runtime path should run. |
| 89 | `                scope[name]["value"] = value` | Assigns/computes a value and stores it in `scope[name]["value"]` for later use in this method. |
| 90 | `                return  ` | Stops this method without returning a meaningful value. |
| 91 | `` | Blank line used to separate code sections for readability. |
| 92 | `        return f"Semantic Error: Variable '{name}' not declared in any scope."` | Returns the computed value/result from this method to its caller. |
| 93 | `` | Blank line used to separate code sections for readability. |
| 94 | `` | Blank line used to separate code sections for readability. |

### declare_function - Lines 95-99

Purpose: Stores a function declaration so it can be called later.

Process flow:

- Stores a function declaration so it can be called later.

Code:

```python
0095:     def declare_function(self, name, return_type, params, node=None):
0096:         if name in self.functions:
0097:             return f"Semantic Error: Function '{name}' already declared."
0098:         self.functions[name] = {"return_type": return_type, "params": params, "node": node}
0099: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 95 | `    def declare_function(self, name, return_type, params, node=None):` | Stores a function declaration so it can be called later. |
| 96 | `        if name in self.functions:` | Conditional branch that decides which runtime path should run. |
| 97 | `            return f"Semantic Error: Function '{name}' already declared."` | Returns the computed value/result from this method to its caller. |
| 98 | `        self.functions[name] = {"return_type": return_type, "params": params, "node": node}` | Creates a dictionary used for key-value runtime storage. |
| 99 | `` | Blank line used to separate code sections for readability. |

### lookup_function - Lines 100-105

Purpose: Finds a stored function declaration by name.

Process flow:

- Finds a stored function declaration by name.

Code:

```python
0100:     def lookup_function(self, name):
0101:         if name in self.functions:
0102:             return self.functions[name]
0103:         return f"Semantic Error: Function '{name}' is not defined."
0104: 
0105: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 100 | `    def lookup_function(self, name):` | Finds a stored function declaration by name. |
| 101 | `        if name in self.functions:` | Conditional branch that decides which runtime path should run. |
| 102 | `            return self.functions[name]` | Calls functions() on the same interpreter object and returns its result to the caller. |
| 103 | `        return f"Semantic Error: Function '{name}' is not defined."` | Returns the computed value/result from this method to its caller. |
| 104 | `` | Blank line used to separate code sections for readability. |
| 105 | `` | Blank line used to separate code sections for readability. |

### enter_scope - Lines 106-109

Purpose: Creates a new local scope for functions, blocks, loops, or conditionals.

Process flow:

- Creates a new local scope for functions, blocks, loops, or conditionals.

Code:

```python
0106:     def enter_scope(self):
0107:         self.scopes.append({})
0108: 
0109: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 106 | `    def enter_scope(self):` | Creates a new local scope for functions, blocks, loops, or conditionals. |
| 107 | `        self.scopes.append({})` | Adds a new item to a list, such as output, parameters, arguments, or evaluated list values. |
| 108 | `` | Blank line used to separate code sections for readability. |
| 109 | `` | Blank line used to separate code sections for readability. |

### exit_scope - Lines 110-120

Purpose: Removes the current local scope after leaving a function/block.

Process flow:

- Removes the current local scope after leaving a function/block.

Code:

```python
0110:     def exit_scope(self):
0111:         if len(self.scopes) > 1:
0112:             self.scopes.pop()
0113: 
0114:         if self.current_func_name:
0115:             current_func = self.current_func_name
0116: 
0117:             if current_func in self.function_variables:
0118:                 self.function_variables[current_func].clear()
0119: 
0120: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 110 | `    def exit_scope(self):` | Removes the current local scope after leaving a function/block. |
| 111 | `        if len(self.scopes) > 1:` | Conditional branch that decides which runtime path should run. |
| 112 | `            self.scopes.pop()` | Removes and returns an item from a list/dictionary, often during cleanup. |
| 113 | `` | Blank line used to separate code sections for readability. |
| 114 | `        if self.current_func_name:` | Conditional branch that decides which runtime path should run. |
| 115 | `            current_func = self.current_func_name` | Assigns/computes a value and stores it in `current_func` for later use in this method. |
| 116 | `` | Blank line used to separate code sections for readability. |
| 117 | `            if current_func in self.function_variables:` | Conditional branch that decides which runtime path should run. |
| 118 | `                self.function_variables[current_func].clear()` | Stores/updates per-function variable helper storage. |
| 119 | `` | Blank line used to separate code sections for readability. |
| 120 | `` | Blank line used to separate code sections for readability. |

### interpret - Lines 121-209

Purpose: Main dispatcher. It receives any AST node and routes it to the correct evaluator method.

Process flow:

- Receive an AST node.

- Check its class or node_type.

- Call the correct eval method.

- Return the eval method result.

Code:

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
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 121 | `    def interpret(self, node):` | Main dispatcher. It receives any AST node and routes it to the correct evaluator method. |
| 122 | `        if isinstance(node, ProgramNode):` | Dispatcher check: if the current AST node has this class, route it to the matching eval method. |
| 123 | `            return self.eval_program(node)` | Calls eval_program() on the same interpreter object and returns its result to the caller. |
| 124 | `        elif isinstance(node, BundleDefinitionNode):` | Next dispatcher check for another possible AST node class. |
| 125 | `            return self.eval_bundle_definition(node)` | Calls eval_bundle_definition() on the same interpreter object and returns its result to the caller. |
| 126 | `        elif isinstance(node, MemberAccessNode):` | Next dispatcher check for another possible AST node class. |
| 127 | `            return self.eval_member_access(node)` | Calls eval_member_access() on the same interpreter object and returns its result to the caller. |
| 128 | `        elif isinstance(node, ArrayMemberAccessNode):` | Next dispatcher check for another possible AST node class. |
| 129 | `            return self.eval_array_member_access(node)` | Calls eval_array_member_access() on the same interpreter object and returns its result to the caller. |
| 130 | `        elif isinstance(node, VariableDeclarationNode):` | Next dispatcher check for another possible AST node class. |
| 131 | `            return self.eval_variable_declaration(node)` | Calls eval_variable_declaration() on the same interpreter object and returns its result to the caller. |
| 132 | `        elif isinstance(node, AssignmentNode):` | Next dispatcher check for another possible AST node class. |
| 133 | `            return self.eval_assignment(node)` | Calls eval_assignment() on the same interpreter object and returns its result to the caller. |
| 134 | `        elif isinstance(node, BinaryOpNode):` | Next dispatcher check for another possible AST node class. |
| 135 | `            value = self.eval_binary_op(node)` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 136 | `            if isinstance(value, (int, float)):` | Conditional branch that decides which runtime path should run. |
| 137 | `                if value > 1000000000000000 or value < -9999999999999999:` | Conditional branch that decides which runtime path should run. |
| 138 | `                    raise InterpreterError(f"Runtime Error: Evaluated number exceeds maximum number of 16 digits", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 139 | `            return value` | Returns the computed value/result from this method to its caller. |
| 140 | `        elif isinstance(node, FunctionDeclarationNode):` | Next dispatcher check for another possible AST node class. |
| 141 | `            return self.eval_function_declaration(node)` | Calls eval_function_declaration() on the same interpreter object and returns its result to the caller. |
| 142 | `        elif isinstance(node, PrintNode):` | Next dispatcher check for another possible AST node class. |
| 143 | `            return self.eval_print(node)` | Calls eval_print() on the same interpreter object and returns its result to the caller. |
| 144 | `        elif isinstance(node, ListNode):` | Next dispatcher check for another possible AST node class. |
| 145 | `            return self.eval_list(node)` | Calls eval_list() on the same interpreter object and returns its result to the caller. |
| 146 | `        elif isinstance(node, ListAccessNode):` | Next dispatcher check for another possible AST node class. |
| 147 | `            return self.eval_list_access(node)` | Calls eval_list_access() on the same interpreter object and returns its result to the caller. |
| 148 | `        elif isinstance(node, ReturnNode):` | Next dispatcher check for another possible AST node class. |
| 149 | `            return self.eval_return(node)` | Calls eval_return() on the same interpreter object and returns its result to the caller. |
| 150 | `        elif isinstance(node, FunctionCallNode):` | Next dispatcher check for another possible AST node class. |
| 151 | `            return self.eval_function_call(node)` | Calls eval_function_call() on the same interpreter object and returns its result to the caller. |
| 152 | `        elif isinstance(node, AppendNode):` | Next dispatcher check for another possible AST node class. |
| 153 | `            return self.eval_append(node)` | Calls eval_append() on the same interpreter object and returns its result to the caller. |
| 154 | `        elif isinstance(node, InsertNode):` | Next dispatcher check for another possible AST node class. |
| 155 | `            return self.eval_insert(node)` | Calls eval_insert() on the same interpreter object and returns its result to the caller. |
| 156 | `        elif isinstance(node, RemoveNode):` | Next dispatcher check for another possible AST node class. |
| 157 | `            return self.eval_remove(node)` | Calls eval_remove() on the same interpreter object and returns its result to the caller. |
| 158 | `        elif isinstance(node, UnaryOpNode):` | Next dispatcher check for another possible AST node class. |
| 159 | `            return self.eval_unaryop(node)` | Calls eval_unaryop() on the same interpreter object and returns its result to the caller. |
| 160 | `        elif isinstance(node, FertileDeclarationNode):` | Next dispatcher check for another possible AST node class. |
| 161 | `            return self.eval_sturdy_declaration(node)` | Calls eval_sturdy_declaration() on the same interpreter object and returns its result to the caller. |
| 162 | `        elif isinstance(node, CastNode):` | Next dispatcher check for another possible AST node class. |
| 163 | `            return self.eval_cast(node)` | Calls eval_cast() on the same interpreter object and returns its result to the caller. |
| 164 | `        elif isinstance(node, SoilNode):` | Next dispatcher check for another possible AST node class. |
| 165 | `            return self.eval_soil(node)` | Calls eval_soil() on the same interpreter object and returns its result to the caller. |
| 166 | `        elif isinstance(node, BloomNode):` | Next dispatcher check for another possible AST node class. |
| 167 | `            return self.eval_bloom(node)` | Calls eval_bloom() on the same interpreter object and returns its result to the caller. |
| 168 | `        elif isinstance(node, IfStatementNode):` | Next dispatcher check for another possible AST node class. |
| 169 | `            return self.eval_if_statement(node)` | Calls eval_if_statement() on the same interpreter object and returns its result to the caller. |
| 170 | `        elif isinstance(node, ForLoopNode):` | Next dispatcher check for another possible AST node class. |
| 171 | `            return self.eval_for_loop(node)` | Calls eval_for_loop() on the same interpreter object and returns its result to the caller. |
| 172 | `        elif isinstance(node, WhileLoopNode):` | Next dispatcher check for another possible AST node class. |
| 173 | `            return self.eval_while_loop(node)` | Calls eval_while_loop() on the same interpreter object and returns its result to the caller. |
| 174 | `        elif isinstance(node, DoWhileLoopNode):` | Next dispatcher check for another possible AST node class. |
| 175 | `            return self.eval_do_while_loop(node)` | Calls eval_do_while_loop() on the same interpreter object and returns its result to the caller. |
| 176 | `        elif isinstance(node, BreakNode):` | Next dispatcher check for another possible AST node class. |
| 177 | `            return self.eval_break(node)` | Calls eval_break() on the same interpreter object and returns its result to the caller. |
| 178 | `        elif isinstance(node, ContinueNode):` | Next dispatcher check for another possible AST node class. |
| 179 | `            return self.eval_continue(node)` | Calls eval_continue() on the same interpreter object and returns its result to the caller. |
| 180 | `        elif isinstance(node, SwitchNode):` | Next dispatcher check for another possible AST node class. |
| 181 | `            return self.eval_switch(node)` | Calls eval_switch() on the same interpreter object and returns its result to the caller. |
| 182 | `        elif node.node_type == "Input":` | Dispatcher check for AST nodes identified by their node_type string. |
| 183 | `            return self.eval_input(node)` | Calls eval_input() on the same interpreter object and returns its result to the caller. |
| 184 | `        elif node.node_type == "Value":` | Dispatcher check for AST nodes identified by their node_type string. |
| 185 | `            value = self._parse_literal(node.value)` | Reads the stored value of the AST node, such as an operator, identifier name, or literal text. |
| 186 | `            return value` | Returns the computed value/result from this method to its caller. |
| 187 | `        elif node.node_type == "Identifier":` | Dispatcher check for AST nodes identified by their node_type string. |
| 188 | `            var_info = self.lookup_variable(node.value)` | Finds a variable record in the active runtime scopes. |
| 189 | `            if isinstance(var_info, str):` | Conditional branch that decides which runtime path should run. |
| 190 | `                raise InterpreterError(var_info, node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 191 | `            return var_info["value"]` | Returns the computed value/result from this method to its caller. |
| 192 | `        elif node.node_type == "FormattedString":` | Dispatcher check for AST nodes identified by their node_type string. |
| 193 | `            return self.eval_formatted_string(node)` | Calls eval_formatted_string() on the same interpreter object and returns its result to the caller. |
| 194 | `        elif node.node_type == "VariableDeclarationList":` | Dispatcher check for AST nodes identified by their node_type string. |
| 195 | `            for child in node.children:` | Loops through child AST nodes and processes each one in order. |
| 196 | `                self.eval_variable_declaration(child)` | Calls a function/method to perform part of the runtime operation. |
| 197 | `        elif node.node_type == "AssignmentList":` | Dispatcher check for AST nodes identified by their node_type string. |
| 198 | `            for child in node.children:` | Loops through child AST nodes and processes each one in order. |
| 199 | `                if isinstance(child, AssignmentNode):` | Conditional branch that decides which runtime path should run. |
| 200 | `                    self.eval_assignment(child)` | Calls a function/method to perform part of the runtime operation. |
| 201 | `                elif isinstance(child, UnaryOpNode):` | Conditional branch that decides which runtime path should run. |
| 202 | `                    self.eval_unaryop(child)` | Calls a function/method to perform part of the runtime operation. |
| 203 | `        elif node.node_type == "List":` | Dispatcher check for AST nodes identified by their node_type string. |
| 204 | `            return [self.interpret(child) for child in node.children]` | Returns the computed value/result from this method to its caller. |
| 205 | `        elif node.node_type == "Block":` | Dispatcher check for AST nodes identified by their node_type string. |
| 206 | `            self.eval_block(node)` | Calls a function/method to perform part of the runtime operation. |
| 207 | `        else:` | Fallback branch used when the previous if/elif conditions were false. |
| 208 | `            raise Exception(f"Unknown AST node type: {node.node_type}")` | Calls a function/method to perform part of the runtime operation. |
| 209 | `` | Blank line used to separate code sections for readability. |

### eval_program - Lines 210-217

Purpose: Executes the whole program node: registers top-level declarations and automatically calls root().

Process flow:

- Loop through top-level AST children.

- Register declarations/functions.

- Create a FunctionCallNode for root().

- Interpret that root call to start program execution.

Code:

```python
0210:     def eval_program(self, node):
0211:         for child in node.children:
0212:             self.interpret(child)
0213: 
0214:         main_call = FunctionCallNode("root", [], node.line)
0215:         return self.interpret(main_call)
0216: 
0217: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 210 | `    def eval_program(self, node):` | Executes the whole program node: registers top-level declarations and automatically calls root(). |
| 211 | `        for child in node.children:` | Loops through child AST nodes and processes each one in order. |
| 212 | `            self.interpret(child)` | Recursively sends another AST node back to the interpreter dispatcher. |
| 213 | `` | Blank line used to separate code sections for readability. |
| 214 | `        main_call = FunctionCallNode("root", [], node.line)` | Assigns/computes a value and stores it in `main_call` for later use in this method. |
| 215 | `        return self.interpret(main_call)` | Calls interpret() on the same interpreter object and returns its result to the caller. |
| 216 | `` | Blank line used to separate code sections for readability. |
| 217 | `` | Blank line used to separate code sections for readability. |

### eval_variable_declaration - Lines 218-236

Purpose: Executes variable declarations and stores default or evaluated initial values.

Process flow:

- Executes variable declarations and stores default or evaluated initial values.

Code:

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
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 218 | `    def eval_variable_declaration(self, node):` | Executes variable declarations and stores default or evaluated initial values. |
| 219 | `        var_type = node.children[0].value` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 220 | `        var_name = node.children[1].value` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 221 | `        value_node = node.children[2] if len(node.children) > 2 else None` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 222 | `        is_list = False` | Assigns/computes a value and stores it in `is_list` for later use in this method. |
| 223 | `        ` | Blank line used to separate code sections for readability. |
| 224 | `        default_values = {` | Creates a dictionary used for key-value runtime storage. |
| 225 | `            "seed": 0,` | Runtime support statement used by the interpreter. |
| 226 | `            "tree": 0.0,` | Runtime support statement used by the interpreter. |
| 227 | `            "leaf": '',` | Runtime support statement used by the interpreter. |
| 228 | `            "vine": "",` | Runtime support statement used by the interpreter. |
| 229 | `            "branch": False,` | Runtime support statement used by the interpreter. |
| 230 | `        }` | Runtime support statement used by the interpreter. |
| 231 | `` | Blank line used to separate code sections for readability. |
| 232 | `        if value_node:` | Conditional branch that decides which runtime path should run. |
| 233 | `            if value_node.node_type == "List":` | Conditional branch that decides which runtime path should run. |
| 234 | `                if var_type in self.bundle_types:` | Checks the declared GAL type so the runtime can validate or convert the value. |
| 235 | `                    value = [self._build_bundle_defaults(var_type) for _ in value_node.children]` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 236 | `                else:` | Fallback branch used when the previous if/elif conditions were false. |

### materialize - Lines 237-292

Purpose: File/class setup or runtime support block.

Process flow:

- Executes/supports part of the interpreter runtime.

Code:

```python
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
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 237 | `                    def materialize(list_node):` | Defines interpreter method materialize(). |
| 238 | `                        result = []` | Creates a list used to collect runtime values. |
| 239 | `                        for child in list_node.children:` | Loops through child AST nodes and processes each one in order. |
| 240 | `                            if isinstance(child, ListNode):` | Conditional branch that decides which runtime path should run. |
| 241 | `                                result.append(materialize(child))` | Adds a new item to a list, such as output, parameters, arguments, or evaluated list values. |
| 242 | `                            else:` | Fallback branch used when the previous if/elif conditions were false. |
| 243 | `                                item = self.interpret(child)` | Recursively sends another AST node back to the interpreter dispatcher. |
| 244 | `                                if var_type == "seed" and isinstance(item, float):` | Checks the declared GAL type so the runtime can validate or convert the value. |
| 245 | `                                    item = int(item)` | Assigns/computes a value and stores it in `item` for later use in this method. |
| 246 | `                                elif var_type == "tree":` | Checks the declared GAL type so the runtime can validate or convert the value. |
| 247 | `                                    item = float(item)` | Assigns/computes a value and stores it in `item` for later use in this method. |
| 248 | `                                result.append(item)` | Adds a new item to a list, such as output, parameters, arguments, or evaluated list values. |
| 249 | `                        return result` | Returns the computed value/result from this method to its caller. |
| 250 | `                    value = materialize(value_node)` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 251 | `` | Blank line used to separate code sections for readability. |
| 252 | `                is_list = True` | Assigns/computes a value and stores it in `is_list` for later use in this method. |
| 253 | `` | Blank line used to separate code sections for readability. |
| 254 | `            else:` | Fallback branch used when the previous if/elif conditions were false. |
| 255 | `                value = self.interpret(value_node)` | Recursively sends another AST node back to the interpreter dispatcher. |
| 256 | `` | Blank line used to separate code sections for readability. |
| 257 | `                if var_type == "seed" and isinstance(value, float):` | Checks the declared GAL type so the runtime can validate or convert the value. |
| 258 | `                    value = int(value)` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 259 | `` | Blank line used to separate code sections for readability. |
| 260 | `                if var_type in {"tree", "seed"}:` | Checks the declared GAL type so the runtime can validate or convert the value. |
| 261 | `                    if not isinstance(value, (int, float)):` | Conditional branch that decides which runtime path should run. |
| 262 | `                        raise InterpreterError(f"Semantic Error: Type Mismatch! Invalid value for {var_name}", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 263 | `                    ` | Blank line used to separate code sections for readability. |
| 264 | `                    if isinstance(value, bool):` | Conditional branch that decides which runtime path should run. |
| 265 | `                        raise InterpreterError(f"Semantic Error: Type Mismatch! Invalid value for {var_name}", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 266 | `` | Blank line used to separate code sections for readability. |
| 267 | `` | Blank line used to separate code sections for readability. |
| 268 | `                    if var_type == "tree" and isinstance(value, int):` | Checks the declared GAL type so the runtime can validate or convert the value. |
| 269 | `                        value = float(value)` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 270 | `                ` | Blank line used to separate code sections for readability. |
| 271 | `                if var_type == "leaf":` | Checks the declared GAL type so the runtime can validate or convert the value. |
| 272 | `                    if not isinstance(value, str):` | Conditional branch that decides which runtime path should run. |
| 273 | `                        raise InterpreterError(f"Semantic Error: Type Mismatch! Invalid value for {var_name}", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 274 | `` | Blank line used to separate code sections for readability. |
| 275 | `                if var_type == "vine":` | Checks the declared GAL type so the runtime can validate or convert the value. |
| 276 | `                    if not isinstance(value, str):` | Conditional branch that decides which runtime path should run. |
| 277 | `                        raise InterpreterError(f"Semantic Error: Type Mismatch! Invalid value for {var_name}", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 278 | `` | Blank line used to separate code sections for readability. |
| 279 | `                if var_type == "branch":` | Checks the declared GAL type so the runtime can validate or convert the value. |
| 280 | `                    if isinstance(value, int) or isinstance(value, float):` | Conditional branch that decides which runtime path should run. |
| 281 | `                        if value == 0:` | Conditional branch that decides which runtime path should run. |
| 282 | `                            value = False` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 283 | `                        else:` | Fallback branch used when the previous if/elif conditions were false. |
| 284 | `                            value = True` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 285 | `        else:` | Fallback branch used when the previous if/elif conditions were false. |
| 286 | `            if var_type in self.bundle_types:` | Checks the declared GAL type so the runtime can validate or convert the value. |
| 287 | `                value = self._build_bundle_defaults(var_type)` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 288 | `            else:` | Fallback branch used when the previous if/elif conditions were false. |
| 289 | `                value = default_values.get(var_type, None)` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 290 | `                    ` | Blank line used to separate code sections for readability. |
| 291 | `        self.declare_variable(var_name, var_type, value, is_list=is_list)` | Creates a variable record in the current scope. |
| 292 | `` | Blank line used to separate code sections for readability. |

### eval_bundle_definition - Lines 293-295

Purpose: Registers bundle/struct member definitions.

Process flow:

- Registers bundle/struct member definitions.

Code:

```python
0293:     def eval_bundle_definition(self, node):
0294:         self.bundle_types[node.bundle_name] = node.members
0295: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 293 | `    def eval_bundle_definition(self, node):` | Registers bundle/struct member definitions. |
| 294 | `        self.bundle_types[node.bundle_name] = node.members` | Stores/updates bundle/struct type definition table. |
| 295 | `` | Blank line used to separate code sections for readability. |

### _build_bundle_defaults - Lines 296-306

Purpose: Creates default runtime values for all members of a bundle type.

Process flow:

- Creates default runtime values for all members of a bundle type.

Code:

```python
0296:     def _build_bundle_defaults(self, bundle_type_name):
0297:         _member_defaults = {"seed": 0, "tree": 0.0, "leaf": '', "vine": "", "branch": False}
0298:         members = self.bundle_types[bundle_type_name]
0299:         result = {}
0300:         for name, typ in members.items():
0301:             if typ in self.bundle_types:
0302:                 result[name] = self._build_bundle_defaults(typ)
0303:             else:
0304:                 result[name] = _member_defaults.get(typ, None)
0305:         return result
0306: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 296 | `    def _build_bundle_defaults(self, bundle_type_name):` | Creates default runtime values for all members of a bundle type. |
| 297 | `        _member_defaults = {"seed": 0, "tree": 0.0, "leaf": '', "vine": "", "branch": False}` | Creates a dictionary used for key-value runtime storage. |
| 298 | `        members = self.bundle_types[bundle_type_name]` | Assigns/computes a value and stores it in `members` for later use in this method. |
| 299 | `        result = {}` | Creates a dictionary used for key-value runtime storage. |
| 300 | `        for name, typ in members.items():` | Loops through a collection of values/items. |
| 301 | `            if typ in self.bundle_types:` | Conditional branch that decides which runtime path should run. |
| 302 | `                result[name] = self._build_bundle_defaults(typ)` | Assigns/computes a value and stores it in `result[name]` for later use in this method. |
| 303 | `            else:` | Fallback branch used when the previous if/elif conditions were false. |
| 304 | `                result[name] = _member_defaults.get(typ, None)` | Assigns/computes a value and stores it in `result[name]` for later use in this method. |
| 305 | `        return result` | Returns the computed value/result from this method to its caller. |
| 306 | `` | Blank line used to separate code sections for readability. |

### eval_member_access - Lines 307-327

Purpose: Reads a bundle member value like student.age.

Process flow:

- Reads a bundle member value like student.age.

Code:

```python
0307:     def eval_member_access(self, node):
0308:         obj_child = node.children[0]
0309:         member_name = node.children[1].value
0310: 
0311:         if obj_child.node_type == "MemberAccess":
0312:             bundle_value = self.eval_member_access(obj_child)
0313:         elif obj_child.node_type == "ArrayMemberAccess":
0314:             bundle_value = self.eval_array_member_access(obj_child)
0315:         else:
0316:             obj_name = obj_child.value
0317:             var_info = self.lookup_variable(obj_name)
0318:             if isinstance(var_info, str):
0319:                 raise InterpreterError(var_info, node.line)
0320:             bundle_value = var_info["value"]
0321: 
0322:         if not isinstance(bundle_value, dict):
0323:             raise InterpreterError(f"Runtime Error: Value is not a bundle.", node.line)
0324:         if member_name not in bundle_value:
0325:             raise InterpreterError(f"Runtime Error: Bundle has no member '{member_name}'.", node.line)
0326:         return bundle_value[member_name]
0327: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 307 | `    def eval_member_access(self, node):` | Reads a bundle member value like student.age. |
| 308 | `        obj_child = node.children[0]` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 309 | `        member_name = node.children[1].value` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 310 | `` | Blank line used to separate code sections for readability. |
| 311 | `        if obj_child.node_type == "MemberAccess":` | Conditional branch that decides which runtime path should run. |
| 312 | `            bundle_value = self.eval_member_access(obj_child)` | Assigns/computes a value and stores it in `bundle_value` for later use in this method. |
| 313 | `        elif obj_child.node_type == "ArrayMemberAccess":` | Conditional branch that decides which runtime path should run. |
| 314 | `            bundle_value = self.eval_array_member_access(obj_child)` | Assigns/computes a value and stores it in `bundle_value` for later use in this method. |
| 315 | `        else:` | Fallback branch used when the previous if/elif conditions were false. |
| 316 | `            obj_name = obj_child.value` | Assigns/computes a value and stores it in `obj_name` for later use in this method. |
| 317 | `            var_info = self.lookup_variable(obj_name)` | Finds a variable record in the active runtime scopes. |
| 318 | `            if isinstance(var_info, str):` | Conditional branch that decides which runtime path should run. |
| 319 | `                raise InterpreterError(var_info, node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 320 | `            bundle_value = var_info["value"]` | Assigns/computes a value and stores it in `bundle_value` for later use in this method. |
| 321 | `` | Blank line used to separate code sections for readability. |
| 322 | `        if not isinstance(bundle_value, dict):` | Conditional branch that decides which runtime path should run. |
| 323 | `            raise InterpreterError(f"Runtime Error: Value is not a bundle.", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 324 | `        if member_name not in bundle_value:` | Conditional branch that decides which runtime path should run. |
| 325 | `            raise InterpreterError(f"Runtime Error: Bundle has no member '{member_name}'.", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 326 | `        return bundle_value[member_name]` | Returns the computed value/result from this method to its caller. |
| 327 | `` | Blank line used to separate code sections for readability. |

### eval_array_member_access - Lines 328-337

Purpose: Reads a member from a bundle stored inside an array/list.

Process flow:

- Reads a member from a bundle stored inside an array/list.

Code:

```python
0328:     def eval_array_member_access(self, node):
0329:         list_access_node = node.children[0]
0330:         member_name = node.children[1].value
0331:         bundle_element = self.eval_list_access(list_access_node)
0332:         if not isinstance(bundle_element, dict):
0333:             raise InterpreterError(f"Runtime Error: Array element is not a bundle.", node.line)
0334:         if member_name not in bundle_element:
0335:             raise InterpreterError(f"Runtime Error: Bundle has no member '{member_name}'.", node.line)
0336:         return bundle_element[member_name]
0337: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 328 | `    def eval_array_member_access(self, node):` | Reads a member from a bundle stored inside an array/list. |
| 329 | `        list_access_node = node.children[0]` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 330 | `        member_name = node.children[1].value` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 331 | `        bundle_element = self.eval_list_access(list_access_node)` | Assigns/computes a value and stores it in `bundle_element` for later use in this method. |
| 332 | `        if not isinstance(bundle_element, dict):` | Conditional branch that decides which runtime path should run. |
| 333 | `            raise InterpreterError(f"Runtime Error: Array element is not a bundle.", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 334 | `        if member_name not in bundle_element:` | Conditional branch that decides which runtime path should run. |
| 335 | `            raise InterpreterError(f"Runtime Error: Bundle has no member '{member_name}'.", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 336 | `        return bundle_element[member_name]` | Returns the computed value/result from this method to its caller. |
| 337 | `` | Blank line used to separate code sections for readability. |

### eval_sturdy_declaration - Lines 338-345

Purpose: Executes fertile/constant declarations.

Process flow:

- Executes fertile/constant declarations.

Code:

```python
0338:     def eval_sturdy_declaration(self, node):
0339:         var_type = node.children[0].value
0340:         var_name = node.children[1].value
0341:         value_node = node.children[2]
0342:         value = self.interpret(value_node)
0343:         self.declare_variable(var_name, var_type, value, is_list=False,  is_fertile=True)
0344: 
0345: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 338 | `    def eval_sturdy_declaration(self, node):` | Executes fertile/constant declarations. |
| 339 | `        var_type = node.children[0].value` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 340 | `        var_name = node.children[1].value` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 341 | `        value_node = node.children[2]` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 342 | `        value = self.interpret(value_node)` | Recursively sends another AST node back to the interpreter dispatcher. |
| 343 | `        self.declare_variable(var_name, var_type, value, is_list=False,  is_fertile=True)` | Creates a variable record in the current scope. |
| 344 | `` | Blank line used to separate code sections for readability. |
| 345 | `` | Blank line used to separate code sections for readability. |

### eval_assignment - Lines 346-509

Purpose: Executes assignments, including normal variables, lists, bundle members, and input assignments.

Process flow:

- Evaluate the right-hand value.

- Find the target variable/list/member.

- Convert value when needed based on GAL type.

- Store the final value.

Code:

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
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 346 | `    def eval_assignment(self, node):` | Executes assignments, including normal variables, lists, bundle members, and input assignments. |
| 347 | `        target_node = node.children[0]` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 348 | `        value_node = node.children[1]` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 349 | `` | Blank line used to separate code sections for readability. |
| 350 | `        if value_node.node_type == "List":` | Conditional branch that decides which runtime path should run. |
| 351 | `            value = []` | Creates a list used to collect runtime values. |
| 352 | `            for val in value_node.children:` | Loops through child AST nodes and processes each one in order. |
| 353 | `                item = self.interpret(val)` | Recursively sends another AST node back to the interpreter dispatcher. |
| 354 | `                value.append(item)` | Adds a new item to a list, such as output, parameters, arguments, or evaluated list values. |
| 355 | `        else:` | Fallback branch used when the previous if/elif conditions were false. |
| 356 | `            value = self.interpret(value_node)` | Recursively sends another AST node back to the interpreter dispatcher. |
| 357 | `            if isinstance(value_node, AppendNode) or isinstance(value_node, InsertNode) or isinstance(value_node, RemoveNode):` | Conditional branch that decides which runtime path should run. |
| 358 | `                return` | Stops this method without returning a meaningful value. |
| 359 | `` | Blank line used to separate code sections for readability. |
| 360 | `        if target_node.node_type == "ListAccess":` | Conditional branch that decides which runtime path should run. |
| 361 | `            indices = []` | Creates a list used to collect runtime values. |
| 362 | `            current = target_node` | Assigns/computes a value and stores it in `current` for later use in this method. |
| 363 | `            while hasattr(current, 'node_type') and current.node_type == "ListAccess":` | Repeats a runtime action while the condition remains true. |
| 364 | `                idx = self.interpret(current.children[1].children[0])` | Recursively sends another AST node back to the interpreter dispatcher. |
| 365 | `                if not isinstance(idx, int):` | Conditional branch that decides which runtime path should run. |
| 366 | `                    raise InterpreterError(f"Runtime Error: List index must be an integer. Got '{idx}'", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 367 | `                indices.append(idx)` | Adds a new item to a list, such as output, parameters, arguments, or evaluated list values. |
| 368 | `                current = current.children[0].value` | Assigns/computes a value and stores it in `current` for later use in this method. |
| 369 | `` | Blank line used to separate code sections for readability. |
| 370 | `            list_name = current` | Assigns/computes a value and stores it in `list_name` for later use in this method. |
| 371 | `            list_entry = self.lookup_variable(list_name)` | Finds a variable record in the active runtime scopes. |
| 372 | `            if isinstance(list_entry, str):` | Conditional branch that decides which runtime path should run. |
| 373 | `                raise InterpreterError(list_entry, node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 374 | `` | Blank line used to separate code sections for readability. |
| 375 | `            list_value = list_entry["value"]` | Assigns/computes a value and stores it in `list_value` for later use in this method. |
| 376 | `            if not isinstance(list_value, (list, str)):` | Conditional branch that decides which runtime path should run. |
| 377 | `                raise InterpreterError(f"Runtime Error: Variable '{list_name}' is not a list.", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 378 | `` | Blank line used to separate code sections for readability. |
| 379 | `            if isinstance(list_value, str):` | Conditional branch that decides which runtime path should run. |
| 380 | `                if len(indices) != 1:` | Conditional branch that decides which runtime path should run. |
| 381 | `                    raise InterpreterError(f"Runtime Error: Multi-dimensional indexing not supported for strings.", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 382 | `                final_idx = indices[0]` | Assigns/computes a value and stores it in `final_idx` for later use in this method. |
| 383 | `                if final_idx < 0 or final_idx >= len(list_value):` | Conditional branch that decides which runtime path should run. |
| 384 | `                    raise InterpreterError(f"Runtime Error: Index '{final_idx}' out of bounds for '{list_name}'.", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 385 | `                if not isinstance(value, str) or len(value) != 1:` | Conditional branch that decides which runtime path should run. |
| 386 | `                    raise InterpreterError(f"Runtime Error: Can only assign a single character to a string index.", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 387 | `                list_value = list_value[:final_idx] + value + list_value[final_idx + 1:]` | Assigns/computes a value and stores it in `list_value` for later use in this method. |
| 388 | `                list_entry["value"] = list_value` | Assigns/computes a value and stores it in `list_entry["value"]` for later use in this method. |
| 389 | `            else:` | Fallback branch used when the previous if/elif conditions were false. |
| 390 | `                indices.reverse()` | Calls a function/method to perform part of the runtime operation. |
| 391 | `` | Blank line used to separate code sections for readability. |
| 392 | `                target = list_value` | Assigns/computes a value and stores it in `target` for later use in this method. |
| 393 | `                for i, idx in enumerate(indices[:-1]):` | Loops through a collection of values/items. |
| 394 | `                    if idx < 0 or idx >= len(target):` | Conditional branch that decides which runtime path should run. |
| 395 | `                        raise InterpreterError(f"Runtime Error: Index '{idx}' out of bounds for list '{list_name}'.", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 396 | `                    target = target[idx]` | Assigns/computes a value and stores it in `target` for later use in this method. |
| 397 | `                    if not isinstance(target, list):` | Conditional branch that decides which runtime path should run. |
| 398 | `                        raise InterpreterError(f"Runtime Error: Cannot index into a non-list value.", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 399 | `` | Blank line used to separate code sections for readability. |
| 400 | `                final_idx = indices[-1]` | Assigns/computes a value and stores it in `final_idx` for later use in this method. |
| 401 | `                if final_idx < 0 or final_idx >= len(target):` | Conditional branch that decides which runtime path should run. |
| 402 | `                    raise InterpreterError(f"Runtime Error: Index '{final_idx}' out of bounds for list '{list_name}'.", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 403 | `` | Blank line used to separate code sections for readability. |
| 404 | `                target[final_idx] = value` | Assigns/computes a value and stores it in `target[final_idx]` for later use in this method. |
| 405 | `` | Blank line used to separate code sections for readability. |
| 406 | `        elif target_node.node_type == "MemberAccess":` | Conditional branch that decides which runtime path should run. |
| 407 | `            chain = []` | Creates a list used to collect runtime values. |
| 408 | `            current = target_node` | Assigns/computes a value and stores it in `current` for later use in this method. |
| 409 | `            while hasattr(current, 'node_type') and current.node_type == "MemberAccess":` | Repeats a runtime action while the condition remains true. |
| 410 | `                chain.append(current.children[1].value)` | Adds a new item to a list, such as output, parameters, arguments, or evaluated list values. |
| 411 | `                current = current.children[0]` | Assigns/computes a value and stores it in `current` for later use in this method. |
| 412 | `` | Blank line used to separate code sections for readability. |
| 413 | `            chain.reverse()` | Calls a function/method to perform part of the runtime operation. |
| 414 | `` | Blank line used to separate code sections for readability. |
| 415 | `            if hasattr(current, 'node_type') and current.node_type == "ArrayMemberAccess":` | Conditional branch that decides which runtime path should run. |
| 416 | `                bundle_value = self.interpret(current)` | Recursively sends another AST node back to the interpreter dispatcher. |
| 417 | `                if not isinstance(bundle_value, dict):` | Conditional branch that decides which runtime path should run. |
| 418 | `                    raise InterpreterError(f"Runtime Error: Value is not a bundle.", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 419 | `            else:` | Fallback branch used when the previous if/elif conditions were false. |
| 420 | `                obj_name = current.value` | Assigns/computes a value and stores it in `obj_name` for later use in this method. |
| 421 | `                var_info = self.lookup_variable(obj_name)` | Finds a variable record in the active runtime scopes. |
| 422 | `                if isinstance(var_info, str):` | Conditional branch that decides which runtime path should run. |
| 423 | `                    raise InterpreterError(var_info, node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 424 | `                bundle_value = var_info["value"]` | Assigns/computes a value and stores it in `bundle_value` for later use in this method. |
| 425 | `                if not isinstance(bundle_value, dict):` | Conditional branch that decides which runtime path should run. |
| 426 | `                    raise InterpreterError(f"Runtime Error: Variable '{obj_name}' is not a bundle.", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 427 | `` | Blank line used to separate code sections for readability. |
| 428 | `            for member in chain[:-1]:` | Loops through a collection of values/items. |
| 429 | `                if member not in bundle_value:` | Conditional branch that decides which runtime path should run. |
| 430 | `                    raise InterpreterError(f"Runtime Error: Bundle has no member '{member}'.", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 431 | `                bundle_value = bundle_value[member]` | Assigns/computes a value and stores it in `bundle_value` for later use in this method. |
| 432 | `                if not isinstance(bundle_value, dict):` | Conditional branch that decides which runtime path should run. |
| 433 | `                    raise InterpreterError(f"Runtime Error: Member '{member}' is not a bundle.", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 434 | `` | Blank line used to separate code sections for readability. |
| 435 | `            final_member = chain[-1]` | Assigns/computes a value and stores it in `final_member` for later use in this method. |
| 436 | `            if final_member not in bundle_value:` | Conditional branch that decides which runtime path should run. |
| 437 | `                raise InterpreterError(f"Runtime Error: Bundle has no member '{final_member}'.", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 438 | `` | Blank line used to separate code sections for readability. |
| 439 | `            type_chain_current = current` | Assigns/computes a value and stores it in `type_chain_current` for later use in this method. |
| 440 | `            if hasattr(type_chain_current, 'node_type') and type_chain_current.node_type == "ArrayMemberAccess":` | Conditional branch that decides which runtime path should run. |
| 441 | `                la_node = type_chain_current.children[0]` | Assigns/computes a value and stores it in `la_node` for later use in this method. |
| 442 | `                while hasattr(la_node, 'node_type') and la_node.node_type == "ListAccess":` | Repeats a runtime action while the condition remains true. |
| 443 | `                    la_node = la_node.children[0].value` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 444 | `                var_type = self.lookup_variable(la_node)["type"] if not isinstance(self.lookup_variable(la_node), str) else None  # type: ignore` | Finds a variable record in the active runtime scopes. |
| 445 | `            else:` | Fallback branch used when the previous if/elif conditions were false. |
| 446 | `                obj_name = type_chain_current.value` | Assigns/computes a value and stores it in `obj_name` for later use in this method. |
| 447 | `                var_info = self.lookup_variable(obj_name)` | Finds a variable record in the active runtime scopes. |
| 448 | `                var_type = var_info["type"] if not isinstance(var_info, str) else None` | Assigns/computes a value and stores it in `var_type` for later use in this method. |
| 449 | `` | Blank line used to separate code sections for readability. |
| 450 | `            if var_type and var_type in self.bundle_types:` | Checks the declared GAL type so the runtime can validate or convert the value. |
| 451 | `                cur_type = var_type` | Assigns/computes a value and stores it in `cur_type` for later use in this method. |
| 452 | `                for member in chain:` | Loops through a collection of values/items. |
| 453 | `                    if cur_type in self.bundle_types:` | Conditional branch that decides which runtime path should run. |
| 454 | `                        cur_type = self.bundle_types[cur_type].get(member, cur_type)` | Assigns/computes a value and stores it in `cur_type` for later use in this method. |
| 455 | `                if cur_type == "seed" and isinstance(value, float):` | Conditional branch that decides which runtime path should run. |
| 456 | `                    value = int(value)` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 457 | `                elif cur_type == "tree" and isinstance(value, int):` | Conditional branch that decides which runtime path should run. |
| 458 | `                    value = float(value)` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 459 | `                elif cur_type == "branch" and isinstance(value, int):` | Conditional branch that decides which runtime path should run. |
| 460 | `                    value = True if value != 0 else False` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 461 | `` | Blank line used to separate code sections for readability. |
| 462 | `            bundle_value[final_member] = value` | Assigns/computes a value and stores it in `bundle_value[final_member]` for later use in this method. |
| 463 | `` | Blank line used to separate code sections for readability. |
| 464 | `        elif target_node.node_type == "ArrayMemberAccess":` | Conditional branch that decides which runtime path should run. |
| 465 | `            list_access_node = target_node.children[0]` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 466 | `            member_name = target_node.children[1].value` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 467 | `            bundle_element = self.eval_list_access(list_access_node)` | Assigns/computes a value and stores it in `bundle_element` for later use in this method. |
| 468 | `            if not isinstance(bundle_element, dict):` | Conditional branch that decides which runtime path should run. |
| 469 | `                raise InterpreterError(f"Runtime Error: Array element is not a bundle.", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 470 | `            if member_name not in bundle_element:` | Conditional branch that decides which runtime path should run. |
| 471 | `                raise InterpreterError(f"Runtime Error: Bundle has no member '{member_name}'.", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 472 | `` | Blank line used to separate code sections for readability. |
| 473 | `            current = list_access_node` | Assigns/computes a value and stores it in `current` for later use in this method. |
| 474 | `            while hasattr(current, 'node_type') and current.node_type == "ListAccess":` | Repeats a runtime action while the condition remains true. |
| 475 | `                current = current.children[0].value` | Assigns/computes a value and stores it in `current` for later use in this method. |
| 476 | `            var_name = current` | Assigns/computes a value and stores it in `var_name` for later use in this method. |
| 477 | `            var_info = self.lookup_variable(var_name)` | Finds a variable record in the active runtime scopes. |
| 478 | `            if not isinstance(var_info, str) and var_info["type"] in self.bundle_types:` | Conditional branch that decides which runtime path should run. |
| 479 | `                member_type = self.bundle_types[var_info["type"]].get(member_name)` | Assigns/computes a value and stores it in `member_type` for later use in this method. |
| 480 | `                if member_type == "seed" and isinstance(value, float):` | Conditional branch that decides which runtime path should run. |
| 481 | `                    value = int(value)` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 482 | `                elif member_type == "tree" and isinstance(value, int):` | Conditional branch that decides which runtime path should run. |
| 483 | `                    value = float(value)` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 484 | `                elif member_type == "branch" and isinstance(value, int):` | Conditional branch that decides which runtime path should run. |
| 485 | `                    value = True if value != 0 else False` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 486 | `` | Blank line used to separate code sections for readability. |
| 487 | `            bundle_element[member_name] = value` | Assigns/computes a value and stores it in `bundle_element[member_name]` for later use in this method. |
| 488 | `` | Blank line used to separate code sections for readability. |
| 489 | `        else:` | Fallback branch used when the previous if/elif conditions were false. |
| 490 | `            var_name = target_node.value` | Reads the stored value of the AST node, such as an operator, identifier name, or literal text. |
| 491 | `            var_info = self.lookup_variable(var_name)` | Finds a variable record in the active runtime scopes. |
| 492 | `            if isinstance(var_info, str):` | Conditional branch that decides which runtime path should run. |
| 493 | `                raise InterpreterError(var_info, node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 494 | `` | Blank line used to separate code sections for readability. |
| 495 | `            var_type = var_info["type"]` | Assigns/computes a value and stores it in `var_type` for later use in this method. |
| 496 | `            if var_type == "seed" and isinstance(value, float):` | Checks the declared GAL type so the runtime can validate or convert the value. |
| 497 | `                value = int(value)` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 498 | `            ` | Blank line used to separate code sections for readability. |
| 499 | `            if var_type == "tree" and isinstance(value, int):` | Checks the declared GAL type so the runtime can validate or convert the value. |
| 500 | `                value = float(value)` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 501 | `` | Blank line used to separate code sections for readability. |
| 502 | `            if var_type == "branch" and isinstance(value, int):` | Checks the declared GAL type so the runtime can validate or convert the value. |
| 503 | `                value = True if value != 0 else False` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 504 | `` | Blank line used to separate code sections for readability. |
| 505 | `            self.set_variable(var_name, value)` | Updates a variable's stored runtime value. |
| 506 | `` | Blank line used to separate code sections for readability. |
| 507 | `        return value` | Returns the computed value/result from this method to its caller. |
| 508 | `` | Blank line used to separate code sections for readability. |
| 509 | `` | Blank line used to separate code sections for readability. |

### eval_binary_op - Lines 510-677

Purpose: Evaluates binary expressions such as +, -, *, /, %, ==, &&, and ||.

Process flow:

- Evaluate left and right operands.

- Read the operator.

- Run the matching operator branch.

- Return the computed result.

Code:

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
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 510 | `    def eval_binary_op(self, node):` | Evaluates binary expressions such as +, -, *, /, %, ==, &&, and \|\|. |
| 511 | `        left = self.interpret(node.children[0])` | Recursively sends another AST node back to the interpreter dispatcher. |
| 512 | `        right = self.interpret(node.children[1])` | Recursively sends another AST node back to the interpreter dispatcher. |
| 513 | `        operator = node.value` | Reads the stored value of the AST node, such as an operator, identifier name, or literal text. |
| 514 | `` | Blank line used to separate code sections for readability. |
| 515 | `        if operator == '`':` | Chooses which binary/unary operator logic to execute. |
| 516 | `            result = str(left) + str(right)` | Assigns/computes a value and stores it in `result` for later use in this method. |
| 517 | `            return result` | Returns the computed value/result from this method to its caller. |
| 518 | `` | Blank line used to separate code sections for readability. |
| 519 | `        left = self._parse_literal(left)` | Assigns/computes a value and stores it in `left` for later use in this method. |
| 520 | `        right = self._parse_literal(right)` | Assigns/computes a value and stores it in `right` for later use in this method. |
| 521 | `` | Blank line used to separate code sections for readability. |
| 522 | `        if operator == '+' and (isinstance(left, str) or isinstance(right, str)):` | Chooses which binary/unary operator logic to execute. |
| 523 | `            result = str(left) + str(right)` | Assigns/computes a value and stores it in `result` for later use in this method. |
| 524 | `            return result` | Returns the computed value/result from this method to its caller. |
| 525 | `` | Blank line used to separate code sections for readability. |
| 526 | `        try:` | Starts a protected block where errors can be handled by except/finally. |
| 527 | `            if operator == '+':` | Chooses which binary/unary operator logic to execute. |
| 528 | `                if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):` | Conditional branch that decides which runtime path should run. |
| 529 | `                    if isinstance(left, bool):` | Conditional branch that decides which runtime path should run. |
| 530 | `                        left = 1 if left == True else 0` | Assigns/computes a value and stores it in `left` for later use in this method. |
| 531 | `                    elif isinstance(left, str):` | Conditional branch that decides which runtime path should run. |
| 532 | `                        left = 1 if left != "" else 0` | Assigns/computes a value and stores it in `left` for later use in this method. |
| 533 | `                    if isinstance(right, bool):` | Conditional branch that decides which runtime path should run. |
| 534 | `                        right = 1 if right == True else 0` | Assigns/computes a value and stores it in `right` for later use in this method. |
| 535 | `                    elif isinstance(right, str):` | Conditional branch that decides which runtime path should run. |
| 536 | `                        right = 1 if right != "" else 0` | Assigns/computes a value and stores it in `right` for later use in this method. |
| 537 | `                return left + right  # type: ignore[operator]` | Returns the computed value/result from this method to its caller. |
| 538 | `            ` | Blank line used to separate code sections for readability. |
| 539 | `            elif operator == '-':` | Chooses which binary/unary operator logic to execute. |
| 540 | `                if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):` | Conditional branch that decides which runtime path should run. |
| 541 | `                    if isinstance(left, bool):` | Conditional branch that decides which runtime path should run. |
| 542 | `                        left = 1 if left == True else 0` | Assigns/computes a value and stores it in `left` for later use in this method. |
| 543 | `                    elif isinstance(left, str):` | Conditional branch that decides which runtime path should run. |
| 544 | `                        left = 1 if left != "" else 0` | Assigns/computes a value and stores it in `left` for later use in this method. |
| 545 | `                    if isinstance(right, bool):` | Conditional branch that decides which runtime path should run. |
| 546 | `                        right = 1 if right == True else 0` | Assigns/computes a value and stores it in `right` for later use in this method. |
| 547 | `                    elif isinstance(right, str):` | Conditional branch that decides which runtime path should run. |
| 548 | `                        right = 1 if right != "" else 0` | Assigns/computes a value and stores it in `right` for later use in this method. |
| 549 | `` | Blank line used to separate code sections for readability. |
| 550 | `                return left - right  # type: ignore[operator]` | Returns the computed value/result from this method to its caller. |
| 551 | `            elif operator == '*':` | Chooses which binary/unary operator logic to execute. |
| 552 | `                if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):` | Conditional branch that decides which runtime path should run. |
| 553 | `                    if isinstance(left, bool):` | Conditional branch that decides which runtime path should run. |
| 554 | `                        left = 1 if left == True else 0` | Assigns/computes a value and stores it in `left` for later use in this method. |
| 555 | `                    elif isinstance(left, str):` | Conditional branch that decides which runtime path should run. |
| 556 | `                        left = 1 if left != "" else 0` | Assigns/computes a value and stores it in `left` for later use in this method. |
| 557 | `                    if isinstance(right, bool):` | Conditional branch that decides which runtime path should run. |
| 558 | `                        right = 1 if right == True else 0` | Assigns/computes a value and stores it in `right` for later use in this method. |
| 559 | `                    elif isinstance(right, str):` | Conditional branch that decides which runtime path should run. |
| 560 | `                        right = 1 if right != "" else 0` | Assigns/computes a value and stores it in `right` for later use in this method. |
| 561 | `                return left * right  # type: ignore[operator]` | Returns the computed value/result from this method to its caller. |
| 562 | `            elif operator == '**':` | Chooses which binary/unary operator logic to execute. |
| 563 | `                if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):` | Conditional branch that decides which runtime path should run. |
| 564 | `                    if isinstance(left, bool):` | Conditional branch that decides which runtime path should run. |
| 565 | `                        left = 1 if left == True else 0` | Assigns/computes a value and stores it in `left` for later use in this method. |
| 566 | `                    elif isinstance(left, str):` | Conditional branch that decides which runtime path should run. |
| 567 | `                        left = 1 if left != "" else 0` | Assigns/computes a value and stores it in `left` for later use in this method. |
| 568 | `                    if isinstance(right, bool):` | Conditional branch that decides which runtime path should run. |
| 569 | `                        right = 1 if right == True else 0` | Assigns/computes a value and stores it in `right` for later use in this method. |
| 570 | `                    elif isinstance(right, str):` | Conditional branch that decides which runtime path should run. |
| 571 | `                        right = 1 if right != "" else 0` | Assigns/computes a value and stores it in `right` for later use in this method. |
| 572 | `                return left ** right  # type: ignore[operator]` | Returns the computed value/result from this method to its caller. |
| 573 | `            elif operator == '/':` | Chooses which binary/unary operator logic to execute. |
| 574 | `                if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):` | Conditional branch that decides which runtime path should run. |
| 575 | `                    if isinstance(left, bool):` | Conditional branch that decides which runtime path should run. |
| 576 | `                        left = 1 if left == True else 0` | Assigns/computes a value and stores it in `left` for later use in this method. |
| 577 | `                    elif isinstance(left, str):` | Conditional branch that decides which runtime path should run. |
| 578 | `                        left = 1 if left != "" else 0` | Assigns/computes a value and stores it in `left` for later use in this method. |
| 579 | `                    if isinstance(right, bool):` | Conditional branch that decides which runtime path should run. |
| 580 | `                        right = 1 if right == True else 0` | Assigns/computes a value and stores it in `right` for later use in this method. |
| 581 | `                    elif isinstance(right, str):` | Conditional branch that decides which runtime path should run. |
| 582 | `                        right = 1 if right != "" else 0` | Assigns/computes a value and stores it in `right` for later use in this method. |
| 583 | `                if right == 0:` | Conditional branch that decides which runtime path should run. |
| 584 | `                    raise InterpreterError("Runtime Error: Division by zero is undefined", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 585 | `                return left / right  # type: ignore[operator]` | Returns the computed value/result from this method to its caller. |
| 586 | `            elif operator == '%':` | Chooses which binary/unary operator logic to execute. |
| 587 | `                if not isinstance(left, (int, float)) and not isinstance(right, (int, float)):` | Conditional branch that decides which runtime path should run. |
| 588 | `                    if isinstance(left, bool):` | Conditional branch that decides which runtime path should run. |
| 589 | `                        left = 1 if left == True else 0` | Assigns/computes a value and stores it in `left` for later use in this method. |
| 590 | `                    elif isinstance(left, str):` | Conditional branch that decides which runtime path should run. |
| 591 | `                        left = 1 if left != "" else 0` | Assigns/computes a value and stores it in `left` for later use in this method. |
| 592 | `                    if isinstance(right, bool):` | Conditional branch that decides which runtime path should run. |
| 593 | `                        right = 1 if right == True else 0` | Assigns/computes a value and stores it in `right` for later use in this method. |
| 594 | `                    elif isinstance(right, str):` | Conditional branch that decides which runtime path should run. |
| 595 | `                        right = 1 if right != "" else 0` | Assigns/computes a value and stores it in `right` for later use in this method. |
| 596 | `                if right == 0:` | Conditional branch that decides which runtime path should run. |
| 597 | `                    raise InterpreterError("Runtime Error: Division by zero is undefined", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 598 | `                return left % right  # type: ignore[operator]` | Returns the computed value/result from this method to its caller. |
| 599 | `            elif operator == '==':` | Chooses which binary/unary operator logic to execute. |
| 600 | `                return left == right` | Returns the computed value/result from this method to its caller. |
| 601 | `            elif operator == '!=':` | Chooses which binary/unary operator logic to execute. |
| 602 | `                return left != right` | Returns the computed value/result from this method to its caller. |
| 603 | `            elif operator == '<':` | Chooses which binary/unary operator logic to execute. |
| 604 | `                if isinstance(left, str):` | Conditional branch that decides which runtime path should run. |
| 605 | `                    left = 0 if left == "" else 1` | Assigns/computes a value and stores it in `left` for later use in this method. |
| 606 | `                if isinstance(right, str):` | Conditional branch that decides which runtime path should run. |
| 607 | `                    right = 0 if right == "" else 1` | Assigns/computes a value and stores it in `right` for later use in this method. |
| 608 | `                return left < right` | Returns the computed value/result from this method to its caller. |
| 609 | `            elif operator == '<=':` | Chooses which binary/unary operator logic to execute. |
| 610 | `                if isinstance(left, str):` | Conditional branch that decides which runtime path should run. |
| 611 | `                    left = 0 if left == "" else 1` | Assigns/computes a value and stores it in `left` for later use in this method. |
| 612 | `                if isinstance(right, str):` | Conditional branch that decides which runtime path should run. |
| 613 | `                    right = 0 if right == "" else 1` | Assigns/computes a value and stores it in `right` for later use in this method. |
| 614 | `                return left <= right` | Returns the computed value/result from this method to its caller. |
| 615 | `            elif operator == '>':` | Chooses which binary/unary operator logic to execute. |
| 616 | `                if isinstance(left, str):` | Conditional branch that decides which runtime path should run. |
| 617 | `                    left = 0 if left == "" else 1` | Assigns/computes a value and stores it in `left` for later use in this method. |
| 618 | `                if isinstance(right, str):` | Conditional branch that decides which runtime path should run. |
| 619 | `                    right = 0 if right == "" else 1` | Assigns/computes a value and stores it in `right` for later use in this method. |
| 620 | `                return left > right` | Returns the computed value/result from this method to its caller. |
| 621 | `` | Blank line used to separate code sections for readability. |
| 622 | `            elif operator == '>=':` | Chooses which binary/unary operator logic to execute. |
| 623 | `                if isinstance(left, str):` | Conditional branch that decides which runtime path should run. |
| 624 | `                    left = 0 if left == "" else 1` | Assigns/computes a value and stores it in `left` for later use in this method. |
| 625 | `                if isinstance(right, str):` | Conditional branch that decides which runtime path should run. |
| 626 | `                    right = 0 if right == "" else 1` | Assigns/computes a value and stores it in `right` for later use in this method. |
| 627 | `                return left >= right` | Returns the computed value/result from this method to its caller. |
| 628 | `            elif operator == '&&':` | Chooses which binary/unary operator logic to execute. |
| 629 | `                if isinstance(left, int) or isinstance(left, float):` | Conditional branch that decides which runtime path should run. |
| 630 | `                    if left == 0:` | Conditional branch that decides which runtime path should run. |
| 631 | `                        left = False` | Assigns/computes a value and stores it in `left` for later use in this method. |
| 632 | `                    else:` | Fallback branch used when the previous if/elif conditions were false. |
| 633 | `                        left = True` | Assigns/computes a value and stores it in `left` for later use in this method. |
| 634 | `                elif isinstance(right, int) or isinstance(right, float):` | Conditional branch that decides which runtime path should run. |
| 635 | `                    if right == 0:` | Conditional branch that decides which runtime path should run. |
| 636 | `                        right = False` | Assigns/computes a value and stores it in `right` for later use in this method. |
| 637 | `                    else:` | Fallback branch used when the previous if/elif conditions were false. |
| 638 | `                        right = True` | Assigns/computes a value and stores it in `right` for later use in this method. |
| 639 | `                elif isinstance(left, str):` | Conditional branch that decides which runtime path should run. |
| 640 | `                    left = False if left == "" else True` | Assigns/computes a value and stores it in `left` for later use in this method. |
| 641 | `                elif isinstance(right, str):` | Conditional branch that decides which runtime path should run. |
| 642 | `                    right = False if right == "" else True` | Assigns/computes a value and stores it in `right` for later use in this method. |
| 643 | `` | Blank line used to separate code sections for readability. |
| 644 | `                elif isinstance(left, str) or isinstance(right, str):` | Conditional branch that decides which runtime path should run. |
| 645 | `                    left = bool(left)` | Assigns/computes a value and stores it in `left` for later use in this method. |
| 646 | `                elif isinstance(left, str) or isinstance(right, str):` | Conditional branch that decides which runtime path should run. |
| 647 | `                    right = bool(right)` | Assigns/computes a value and stores it in `right` for later use in this method. |
| 648 | `` | Blank line used to separate code sections for readability. |
| 649 | `                return bool(left) and bool(right)` | Returns the computed value/result from this method to its caller. |
| 650 | `            elif operator == '\\|\\|':` | Chooses which binary/unary operator logic to execute. |
| 651 | `                if isinstance(left, int) or isinstance(left, float):` | Conditional branch that decides which runtime path should run. |
| 652 | `                    if left == 0:` | Conditional branch that decides which runtime path should run. |
| 653 | `                        left = False` | Assigns/computes a value and stores it in `left` for later use in this method. |
| 654 | `                    else:` | Fallback branch used when the previous if/elif conditions were false. |
| 655 | `                        left = True` | Assigns/computes a value and stores it in `left` for later use in this method. |
| 656 | `                elif isinstance(right, int) or isinstance(right, float):` | Conditional branch that decides which runtime path should run. |
| 657 | `                    if right == 0:` | Conditional branch that decides which runtime path should run. |
| 658 | `                        right = False` | Assigns/computes a value and stores it in `right` for later use in this method. |
| 659 | `                    else:` | Fallback branch used when the previous if/elif conditions were false. |
| 660 | `                        right = True` | Assigns/computes a value and stores it in `right` for later use in this method. |
| 661 | `` | Blank line used to separate code sections for readability. |
| 662 | `                elif isinstance(left, str) or isinstance(right, str):` | Conditional branch that decides which runtime path should run. |
| 663 | `                    left = bool(left)` | Assigns/computes a value and stores it in `left` for later use in this method. |
| 664 | `                elif isinstance(left, str) or isinstance(right, str):` | Conditional branch that decides which runtime path should run. |
| 665 | `                    right = bool(right)` | Assigns/computes a value and stores it in `right` for later use in this method. |
| 666 | `` | Blank line used to separate code sections for readability. |
| 667 | `                return bool(left) or bool(right)` | Returns the computed value/result from this method to its caller. |
| 668 | `            elif operator == '!':` | Chooses which binary/unary operator logic to execute. |
| 669 | `                return not bool(left)` | Returns the computed value/result from this method to its caller. |
| 670 | `            elif operator == 'neg':` | Chooses which binary/unary operator logic to execute. |
| 671 | `                return -left  # type: ignore` | Returns the computed value/result from this method to its caller. |
| 672 | `            else:` | Fallback branch used when the previous if/elif conditions were false. |
| 673 | `                raise Exception(f"Unknown operator: {operator}")` | Calls a function/method to perform part of the runtime operation. |
| 674 | `        ` | Blank line used to separate code sections for readability. |
| 675 | `        except ZeroDivisionError:` | Handles an error or special control-flow case. |
| 676 | `            raise InterpreterError("Runtime Error: Division by zero", "")` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 677 | `` | Blank line used to separate code sections for readability. |

### _parse_literal - Lines 678-715

Purpose: Converts literal text or token values into Python runtime values.

Process flow:

- Converts literal text or token values into Python runtime values.

Code:

```python
0678:     def _parse_literal(self, value):
0679: 
0680:         if isinstance(value, str):
0681:             var_info = self.lookup_variable(value)
0682:             if var_info is not None and not isinstance(var_info, str):
0683:                 return var_info["value"]
0684: 
0685:         if isinstance(value, (int, float, bool)):
0686:             return value
0687: 
0688:         if not isinstance(value, str):
0689:             return value
0690: 
0691:         value = value.strip()
0692: 
0693:         if value.startswith('"') and value.endswith('"'):
0694:             return value[1:-1]
0695:         
0696:         if value.startswith("'") and value.endswith("'"):
0697:             return value[1:-1]
0698: 
0699:         if value in ('true', 'sunshine'):
0700:             return True
0701:         if value in ('false', 'frost'):
0702:             return False
0703: 
0704:         parse_value = value
0705:         if parse_value.startswith('~'):
0706:             parse_value = '-' + parse_value[1:]
0707: 
0708:         try:
0709:             if '.' in parse_value:
0710:                 return float(parse_value)
0711:             return int(parse_value)
0712:         except ValueError:
0713:             return value 
0714:     
0715: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 678 | `    def _parse_literal(self, value):` | Converts literal text or token values into Python runtime values. |
| 679 | `` | Blank line used to separate code sections for readability. |
| 680 | `        if isinstance(value, str):` | Conditional branch that decides which runtime path should run. |
| 681 | `            var_info = self.lookup_variable(value)` | Finds a variable record in the active runtime scopes. |
| 682 | `            if var_info is not None and not isinstance(var_info, str):` | Conditional branch that decides which runtime path should run. |
| 683 | `                return var_info["value"]` | Returns the computed value/result from this method to its caller. |
| 684 | `` | Blank line used to separate code sections for readability. |
| 685 | `        if isinstance(value, (int, float, bool)):` | Conditional branch that decides which runtime path should run. |
| 686 | `            return value` | Returns the computed value/result from this method to its caller. |
| 687 | `` | Blank line used to separate code sections for readability. |
| 688 | `        if not isinstance(value, str):` | Conditional branch that decides which runtime path should run. |
| 689 | `            return value` | Returns the computed value/result from this method to its caller. |
| 690 | `` | Blank line used to separate code sections for readability. |
| 691 | `        value = value.strip()` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 692 | `` | Blank line used to separate code sections for readability. |
| 693 | `        if value.startswith('"') and value.endswith('"'):` | Conditional branch that decides which runtime path should run. |
| 694 | `            return value[1:-1]` | Returns the computed value/result from this method to its caller. |
| 695 | `        ` | Blank line used to separate code sections for readability. |
| 696 | `        if value.startswith("'") and value.endswith("'"):` | Conditional branch that decides which runtime path should run. |
| 697 | `            return value[1:-1]` | Returns the computed value/result from this method to its caller. |
| 698 | `` | Blank line used to separate code sections for readability. |
| 699 | `        if value in ('true', 'sunshine'):` | Conditional branch that decides which runtime path should run. |
| 700 | `            return True` | Returns the computed value/result from this method to its caller. |
| 701 | `        if value in ('false', 'frost'):` | Conditional branch that decides which runtime path should run. |
| 702 | `            return False` | Returns the computed value/result from this method to its caller. |
| 703 | `` | Blank line used to separate code sections for readability. |
| 704 | `        parse_value = value` | Assigns/computes a value and stores it in `parse_value` for later use in this method. |
| 705 | `        if parse_value.startswith('~'):` | Conditional branch that decides which runtime path should run. |
| 706 | `            parse_value = '-' + parse_value[1:]` | Assigns/computes a value and stores it in `parse_value` for later use in this method. |
| 707 | `` | Blank line used to separate code sections for readability. |
| 708 | `        try:` | Starts a protected block where errors can be handled by except/finally. |
| 709 | `            if '.' in parse_value:` | Conditional branch that decides which runtime path should run. |
| 710 | `                return float(parse_value)` | Returns the computed value/result from this method to its caller. |
| 711 | `            return int(parse_value)` | Returns the computed value/result from this method to its caller. |
| 712 | `        except ValueError:` | Handles an error or special control-flow case. |
| 713 | `            return value ` | Returns the computed value/result from this method to its caller. |
| 714 | `    ` | Blank line used to separate code sections for readability. |
| 715 | `` | Blank line used to separate code sections for readability. |

### eval_function_declaration - Lines 716-734

Purpose: Stores function declarations into the interpreter function table.

Process flow:

- Stores function declarations into the interpreter function table.

Code:

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
0734: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 716 | `    def eval_function_declaration(self, node):` | Stores function declarations into the interpreter function table. |
| 717 | `        return_type = node.children[0].value` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 718 | `        parameters_node = node.children[1]` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 719 | `        func_name = node.value` | Reads the stored value of the AST node, such as an operator, identifier name, or literal text. |
| 720 | `` | Blank line used to separate code sections for readability. |
| 721 | `        params = []` | Creates a list used to collect runtime values. |
| 722 | `        if parameters_node and len(parameters_node.children) > 0:` | Checks a condition using values stored inside the AST node children. |
| 723 | `            for param in parameters_node.children:` | Loops through child AST nodes and processes each one in order. |
| 724 | `                if not hasattr(param, 'node_type') or param.node_type != 'Parameter':` | Conditional branch that decides which runtime path should run. |
| 725 | `                    raise Exception(f"Invalid parameter: {param.value}")` | Calls a function/method to perform part of the runtime operation. |
| 726 | `                param_type = param.children[0].value` | Assigns/computes a value and stores it in `param_type` for later use in this method. |
| 727 | `                param_name = param.children[1].value` | Assigns/computes a value and stores it in `param_name` for later use in this method. |
| 728 | `                is_list = any(child.node_type == "ArrayParam" for child in param.children)` | Assigns/computes a value and stores it in `is_list` for later use in this method. |
| 729 | `                params.append({"name": param_name, "type": param_type, "is_list": is_list})` | Adds a new item to a list, such as output, parameters, arguments, or evaluated list values. |
| 730 | `` | Blank line used to separate code sections for readability. |
| 731 | `        self.declare_function(func_name, return_type, params, node)` | Registers a function in the interpreter's function table. |
| 732 | `` | Blank line used to separate code sections for readability. |
| 733 | `        return None` | Returns the computed value/result from this method to its caller. |
| 734 | `` | Blank line used to separate code sections for readability. |

### eval_block - Lines 735-743

Purpose: Executes every statement inside a block one by one.

Process flow:

- Executes every statement inside a block one by one.

Code:

```python
0735:     def eval_block(self, block_node):
0736:         for statement in block_node.children:
0737:             self.interpret(statement)
0738:             if self.break_triggered():
0739:                 return
0740:             if self.continue_flag:
0741:                 return
0742: 
0743: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 735 | `    def eval_block(self, block_node):` | Executes every statement inside a block one by one. |
| 736 | `        for statement in block_node.children:` | Loops through child AST nodes and processes each one in order. |
| 737 | `            self.interpret(statement)` | Recursively sends another AST node back to the interpreter dispatcher. |
| 738 | `            if self.break_triggered():` | Conditional branch that decides which runtime path should run. |
| 739 | `                return` | Stops this method without returning a meaningful value. |
| 740 | `            if self.continue_flag:` | Conditional branch that decides which runtime path should run. |
| 741 | `                return` | Stops this method without returning a meaningful value. |
| 742 | `` | Blank line used to separate code sections for readability. |
| 743 | `` | Blank line used to separate code sections for readability. |

### plant - Lines 744-746

Purpose: Sends output text to the frontend through Socket.IO or the output collector.

Process flow:

- Sends output text to the frontend through Socket.IO or the output collector.

Code:

```python
0744:     def plant(self, value):
0745:         self.socketio.emit('output', {'output': str(value)})
0746: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 744 | `    def plant(self, value):` | Sends output text to the frontend through Socket.IO or the output collector. |
| 745 | `        self.socketio.emit('output', {'output': str(value)})` | Sends an event to the frontend/UI, such as output text or an input request. |
| 746 | `` | Blank line used to separate code sections for readability. |

### plant_out - Lines 747-751

Purpose: Sends and stores output text for collector-style execution.

Process flow:

- Sends and stores output text for collector-style execution.

Code:

```python
0747:     def plant_out(self, num):
0748:         self.socketio.emit('output', {'output': str(num)})
0749:         self.output.append(str(num))
0750: 
0751: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 747 | `    def plant_out(self, num):` | Sends and stores output text for collector-style execution. |
| 748 | `        self.socketio.emit('output', {'output': str(num)})` | Sends an event to the frontend/UI, such as output text or an input request. |
| 749 | `        self.output.append(str(num))` | Adds a new item to a list, such as output, parameters, arguments, or evaluated list values. |
| 750 | `` | Blank line used to separate code sections for readability. |
| 751 | `` | Blank line used to separate code sections for readability. |

### eval_print - Lines 752-799

Purpose: Executes plant() statements, including placeholder formatting and multi-argument printing.

Process flow:

- Evaluate plant() arguments.

- Use placeholder formatting if the first string has {}.

- Otherwise join multiple arguments with spaces.

- Emit the final output text.

Code:

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
0799: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 752 | `    def eval_print(self, node):` | Executes plant() statements, including placeholder formatting and multi-argument printing. |
| 753 | `        if not node.children:` | Checks a condition using values stored inside the AST node children. |
| 754 | `            return` | Stops this method without returning a meaningful value. |
| 755 | `` | Blank line used to separate code sections for readability. |
| 756 | `        first = node.children[0]` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 757 | `` | Blank line used to separate code sections for readability. |
| 758 | `        evaluated_first = self.interpret(first)` | Recursively sends another AST node back to the interpreter dispatcher. |
| 759 | `        if isinstance(evaluated_first, float):` | Conditional branch that decides which runtime path should run. |
| 760 | `            whole, dot, dec = str(evaluated_first).partition('.')` | Assigns/computes a value and stores it in `whole, dot, dec` for later use in this method. |
| 761 | `            dec = dec[:5]` | Assigns/computes a value and stores it in `dec` for later use in this method. |
| 762 | `            evaluated_first = float(f"{whole}.{dec}")` | Assigns/computes a value and stores it in `evaluated_first` for later use in this method. |
| 763 | `` | Blank line used to separate code sections for readability. |
| 764 | `        if isinstance(evaluated_first, str) and '{}' in evaluated_first:` | Conditional branch that decides which runtime path should run. |
| 765 | `            values = []` | Creates a list used to collect runtime values. |
| 766 | `            for arg in node.children[1:]:` | Loops through child AST nodes and processes each one in order. |
| 767 | `                value = self.interpret(arg)` | Recursively sends another AST node back to the interpreter dispatcher. |
| 768 | `                if isinstance(value, str) and not isinstance(self.lookup_variable(value), str):` | Conditional branch that decides which runtime path should run. |
| 769 | `                    value = self.lookup_variable(value)["value"]  # type: ignore[index]` | Finds a variable record in the active runtime scopes. |
| 770 | `                ` | Blank line used to separate code sections for readability. |
| 771 | `                if isinstance(value, float):` | Conditional branch that decides which runtime path should run. |
| 772 | `                    whole, dot, dec = str(value).partition('.')` | Assigns/computes a value and stores it in `whole, dot, dec` for later use in this method. |
| 773 | `                    dec = dec[:5]` | Assigns/computes a value and stores it in `dec` for later use in this method. |
| 774 | `                    value = float(f"{whole}.{dec}")` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 775 | `` | Blank line used to separate code sections for readability. |
| 776 | `                values.append(value)` | Adds a new item to a list, such as output, parameters, arguments, or evaluated list values. |
| 777 | `` | Blank line used to separate code sections for readability. |
| 778 | `            try:` | Starts a protected block where errors can be handled by except/finally. |
| 779 | `                output_str = evaluated_first.format(*values)` | Assigns/computes a value and stores it in `output_str` for later use in this method. |
| 780 | `            except Exception as e:` | Handles an error or special control-flow case. |
| 781 | `                raise Exception(f"Format error in plant(): '{evaluated_first}' with {values}: {e}")` | Calls a function/method to perform part of the runtime operation. |
| 782 | `` | Blank line used to separate code sections for readability. |
| 783 | `            self.plant(output_str)` | Calls a function/method to perform part of the runtime operation. |
| 784 | `            return` | Stops this method without returning a meaningful value. |
| 785 | `` | Blank line used to separate code sections for readability. |
| 786 | `        if len(node.children) > 1:` | Checks a condition using values stored inside the AST node children. |
| 787 | `            parts = [str(evaluated_first)]` | Creates a list used to collect runtime values. |
| 788 | `            for arg in node.children[1:]:` | Loops through child AST nodes and processes each one in order. |
| 789 | `                value = self.interpret(arg)` | Recursively sends another AST node back to the interpreter dispatcher. |
| 790 | `                if isinstance(value, float):` | Conditional branch that decides which runtime path should run. |
| 791 | `                    whole, dot, dec = str(value).partition('.')` | Assigns/computes a value and stores it in `whole, dot, dec` for later use in this method. |
| 792 | `                    dec = dec[:5]` | Assigns/computes a value and stores it in `dec` for later use in this method. |
| 793 | `                    value = float(f"{whole}.{dec}")` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 794 | `                parts.append(str(value))` | Adds a new item to a list, such as output, parameters, arguments, or evaluated list values. |
| 795 | `            self.plant(" ".join(parts))` | Calls a function/method to perform part of the runtime operation. |
| 796 | `            return` | Stops this method without returning a meaningful value. |
| 797 | `` | Blank line used to separate code sections for readability. |
| 798 | `        self.plant(str(evaluated_first))` | Calls a function/method to perform part of the runtime operation. |
| 799 | `` | Blank line used to separate code sections for readability. |

### eval_formatted_string - Lines 800-814

Purpose: Removes string quotes and converts escape sequences such as \n and \t.

Process flow:

- Removes string quotes and converts escape sequences such as \n and \t.

Code:

```python
0800:     def eval_formatted_string(self, node):
0801:         value = node.value
0802:         if value.startswith('"') and value.endswith('"'):
0803:             value = value[1:-1]
0804: 
0805:         value = value.replace(r'\\', '\\')
0806:         value = value.replace(r'\n', '\n')
0807:         value = value.replace(r'\t', '\t')
0808:         value = value.replace(r'\"', '"')
0809:         value = value.replace(r'\{', '{')
0810:         value = value.replace(r'\}', '}')
0811:         value = value.replace(r'\/', '/')
0812:         return value
0813: 
0814: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 800 | `    def eval_formatted_string(self, node):` | Removes string quotes and converts escape sequences such as \n and \t. |
| 801 | `        value = node.value` | Reads the stored value of the AST node, such as an operator, identifier name, or literal text. |
| 802 | `        if value.startswith('"') and value.endswith('"'):` | Conditional branch that decides which runtime path should run. |
| 803 | `            value = value[1:-1]` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 804 | `` | Blank line used to separate code sections for readability. |
| 805 | `        value = value.replace(r'\\', '\\')` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 806 | `        value = value.replace(r'\n', '\n')` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 807 | `        value = value.replace(r'\t', '\t')` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 808 | `        value = value.replace(r'\"', '"')` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 809 | `        value = value.replace(r'\{', '{')` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 810 | `        value = value.replace(r'\}', '}')` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 811 | `        value = value.replace(r'\/', '/')` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 812 | `        return value` | Returns the computed value/result from this method to its caller. |
| 813 | `` | Blank line used to separate code sections for readability. |
| 814 | `` | Blank line used to separate code sections for readability. |

### eval_list - Lines 815-824

Purpose: Evaluates list/array literal values.

Process flow:

- Evaluates list/array literal values.

Code:

```python
0815:     def eval_list(self, node):
0816:         result = []
0817:         for child in node.children:
0818:             if isinstance(child, ListNode):
0819:                 result.append(self.eval_list(child))
0820:             else:
0821:                 result.append(self.interpret(child))
0822:         return result
0823: 
0824: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 815 | `    def eval_list(self, node):` | Evaluates list/array literal values. |
| 816 | `        result = []` | Creates a list used to collect runtime values. |
| 817 | `        for child in node.children:` | Loops through child AST nodes and processes each one in order. |
| 818 | `            if isinstance(child, ListNode):` | Conditional branch that decides which runtime path should run. |
| 819 | `                result.append(self.eval_list(child))` | Adds a new item to a list, such as output, parameters, arguments, or evaluated list values. |
| 820 | `            else:` | Fallback branch used when the previous if/elif conditions were false. |
| 821 | `                result.append(self.interpret(child))` | Adds a new item to a list, such as output, parameters, arguments, or evaluated list values. |
| 822 | `        return result` | Returns the computed value/result from this method to its caller. |
| 823 | `` | Blank line used to separate code sections for readability. |
| 824 | `` | Blank line used to separate code sections for readability. |

### eval_list_access - Lines 825-850

Purpose: Reads a value from a list or string using an index.

Process flow:

- Reads a value from a list or string using an index.

Code:

```python
0825:     def eval_list_access(self, node):
0826:         name_or_node = node.children[0].value
0827:         if hasattr(name_or_node, 'node_type') and name_or_node.node_type == "ListAccess":
0828:             list_value = self.eval_list_access(name_or_node)
0829:             display_name = "nested list"
0830:         else:
0831:             list_name = name_or_node
0832:             list_entry = self.lookup_variable(list_name)
0833:             list_value = list_entry["value"]  # type: ignore
0834:             display_name = list_name
0835: 
0836:         index_node = node.children[1]
0837:         index = self.interpret(index_node.children[0])
0838: 
0839:         if not isinstance(index, int):
0840:             raise InterpreterError(f"Runtime Error: List index must be an integer. Got '{index}'", node.line)
0841:         
0842:         if not isinstance(list_value, (list, str)):
0843:             raise InterpreterError(f"Runtime Error: Cannot index into a non-list value.", node.line)
0844: 
0845:         if index < 0 or index >= len(list_value):
0846:             raise InterpreterError(f"Runtime Error: Index '{index}' out of bounds for '{display_name}'.", node.line)
0847: 
0848:         return list_value[index]
0849:     
0850: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 825 | `    def eval_list_access(self, node):` | Reads a value from a list or string using an index. |
| 826 | `        name_or_node = node.children[0].value` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 827 | `        if hasattr(name_or_node, 'node_type') and name_or_node.node_type == "ListAccess":` | Conditional branch that decides which runtime path should run. |
| 828 | `            list_value = self.eval_list_access(name_or_node)` | Assigns/computes a value and stores it in `list_value` for later use in this method. |
| 829 | `            display_name = "nested list"` | Assigns/computes a value and stores it in `display_name` for later use in this method. |
| 830 | `        else:` | Fallback branch used when the previous if/elif conditions were false. |
| 831 | `            list_name = name_or_node` | Assigns/computes a value and stores it in `list_name` for later use in this method. |
| 832 | `            list_entry = self.lookup_variable(list_name)` | Finds a variable record in the active runtime scopes. |
| 833 | `            list_value = list_entry["value"]  # type: ignore` | Assigns/computes a value and stores it in `list_value` for later use in this method. |
| 834 | `            display_name = list_name` | Assigns/computes a value and stores it in `display_name` for later use in this method. |
| 835 | `` | Blank line used to separate code sections for readability. |
| 836 | `        index_node = node.children[1]` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 837 | `        index = self.interpret(index_node.children[0])` | Recursively sends another AST node back to the interpreter dispatcher. |
| 838 | `` | Blank line used to separate code sections for readability. |
| 839 | `        if not isinstance(index, int):` | Conditional branch that decides which runtime path should run. |
| 840 | `            raise InterpreterError(f"Runtime Error: List index must be an integer. Got '{index}'", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 841 | `        ` | Blank line used to separate code sections for readability. |
| 842 | `        if not isinstance(list_value, (list, str)):` | Conditional branch that decides which runtime path should run. |
| 843 | `            raise InterpreterError(f"Runtime Error: Cannot index into a non-list value.", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 844 | `` | Blank line used to separate code sections for readability. |
| 845 | `        if index < 0 or index >= len(list_value):` | Conditional branch that decides which runtime path should run. |
| 846 | `            raise InterpreterError(f"Runtime Error: Index '{index}' out of bounds for '{display_name}'.", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 847 | `` | Blank line used to separate code sections for readability. |
| 848 | `        return list_value[index]` | Returns the computed value/result from this method to its caller. |
| 849 | `    ` | Blank line used to separate code sections for readability. |
| 850 | `` | Blank line used to separate code sections for readability. |

### eval_return - Lines 851-855

Purpose: Executes reclaim by raising ReturnValue to stop the current function.

Process flow:

- Evaluate the reclaim expression if one exists.

- Raise ReturnValue so the current function stops immediately.

Code:

```python
0851:     def eval_return(self, node):
0852:         value = self.interpret(node.children[0]) if node.children else None
0853:         raise ReturnValue(value)
0854: 
0855: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 851 | `    def eval_return(self, node):` | Executes reclaim by raising ReturnValue to stop the current function. |
| 852 | `        value = self.interpret(node.children[0]) if node.children else None` | Recursively sends another AST node back to the interpreter dispatcher. |
| 853 | `        raise ReturnValue(value)` | Implements reclaim: raises a special return object so function execution stops immediately. |
| 854 | `` | Blank line used to separate code sections for readability. |
| 855 | `` | Blank line used to separate code sections for readability. |

### eval_function_call - Lines 856-895

Purpose: Executes a function call: evaluates arguments, creates scope, binds parameters, runs body, and catches reclaim.

Process flow:

- Evaluate call arguments.

- Look up the called function.

- Create a new scope.

- Bind parameters to argument values.

- Execute the function body block.

- Catch ReturnValue from reclaim and return it.

Code:

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
0891:         finally:
0892:             self.exit_scope()
0893:             self.current_func_name = None
0894: 
0895: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 856 | `    def eval_function_call(self, node):` | Executes a function call: evaluates arguments, creates scope, binds parameters, runs body, and catches reclaim. |
| 857 | `        function_name = node.value` | Reads the stored value of the AST node, such as an operator, identifier name, or literal text. |
| 858 | `        args = [self.interpret(arg.children[0]) for arg in node.children]` | Recursively sends another AST node back to the interpreter dispatcher. |
| 859 | `` | Blank line used to separate code sections for readability. |
| 860 | `        func_info = self.lookup_function(function_name)` | Finds a function record in the function table. |
| 861 | `        if isinstance(func_info, str):` | Conditional branch that decides which runtime path should run. |
| 862 | `            raise InterpreterError(func_info, node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 863 | `` | Blank line used to separate code sections for readability. |
| 864 | `        expected_params = func_info["params"]` | Assigns/computes a value and stores it in `expected_params` for later use in this method. |
| 865 | `        function_node = func_info["node"]` | Assigns/computes a value and stores it in `function_node` for later use in this method. |
| 866 | `` | Blank line used to separate code sections for readability. |
| 867 | `        if len(expected_params) != len(args):` | Conditional branch that decides which runtime path should run. |
| 868 | `            raise InterpreterError(` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 869 | `                f"Runtime Error: Function '{function_name}' expects {len(expected_params)} argument(s), got {len(args)}.",` | Runtime support statement used by the interpreter. |
| 870 | `                node.line` | Runtime support statement used by the interpreter. |
| 871 | `            )` | Calls a function/method to perform part of the runtime operation. |
| 872 | `        ` | Blank line used to separate code sections for readability. |
| 873 | `        self.enter_scope()` | Creates a new local runtime scope. |
| 874 | `        ` | Blank line used to separate code sections for readability. |
| 875 | `        try:` | Starts a protected block where errors can be handled by except/finally. |
| 876 | `            for i, param in enumerate(expected_params):` | Loops through a collection of values/items. |
| 877 | `                param_name = param["name"]` | Assigns/computes a value and stores it in `param_name` for later use in this method. |
| 878 | `                param_type = param["type"]` | Assigns/computes a value and stores it in `param_type` for later use in this method. |
| 879 | `                arg_value = args[i]` | Assigns/computes a value and stores it in `arg_value` for later use in this method. |
| 880 | `                is_list = param.get("is_list", False)` | Assigns/computes a value and stores it in `is_list` for later use in this method. |
| 881 | `                self.declare_variable(param_name, param_type, arg_value, is_list=is_list)` | Creates a variable record in the current scope. |
| 882 | `` | Blank line used to separate code sections for readability. |
| 883 | `            try:` | Starts a protected block where errors can be handled by except/finally. |
| 884 | `                self.eval_block(function_node.children[2])` | Calls a function/method to perform part of the runtime operation. |
| 885 | `` | Blank line used to separate code sections for readability. |
| 886 | `            except ReturnValue as ret:` | Catches a reclaim return value from a called function. |
| 887 | `                return ret.value` | Returns the computed value/result from this method to its caller. |
| 888 | `` | Blank line used to separate code sections for readability. |
| 889 | `            return None` | Returns the computed value/result from this method to its caller. |
| 890 | `` | Blank line used to separate code sections for readability. |
| 891 | `        finally:` | Cleanup block that runs even if the try block returns or raises an error. |
| 892 | `            self.exit_scope()` | Leaves/removes the current local runtime scope. |
| 893 | `            self.current_func_name = None` | Stores/updates name of the function currently being executed. |
| 894 | `` | Blank line used to separate code sections for readability. |
| 895 | `` | Blank line used to separate code sections for readability. |

### eval_append - Lines 896-904

Purpose: Executes list append behavior.

Process flow:

- Executes list append behavior.

Code:

```python
0896:     def eval_append(self, node):
0897:         list_name = node.parent.children[0].value
0898:         list_info = self.lookup_variable(list_name)
0899: 
0900:         for child in node.children:
0901:             value = self.interpret(child)
0902:             list_info["value"].append(value)  # type: ignore
0903: 
0904:         
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 896 | `    def eval_append(self, node):` | Executes list append behavior. |
| 897 | `        list_name = node.parent.children[0].value` | Assigns/computes a value and stores it in `list_name` for later use in this method. |
| 898 | `        list_info = self.lookup_variable(list_name)` | Finds a variable record in the active runtime scopes. |
| 899 | `` | Blank line used to separate code sections for readability. |
| 900 | `        for child in node.children:` | Loops through child AST nodes and processes each one in order. |
| 901 | `            value = self.interpret(child)` | Recursively sends another AST node back to the interpreter dispatcher. |
| 902 | `            list_info["value"].append(value)  # type: ignore` | Adds a new item to a list, such as output, parameters, arguments, or evaluated list values. |
| 903 | `` | Blank line used to separate code sections for readability. |
| 904 | `        ` | Blank line used to separate code sections for readability. |

### eval_insert - Lines 905-922

Purpose: Executes list insertion behavior.

Process flow:

- Executes list insertion behavior.

Code:

```python
0905:     def eval_insert(self, node):
0906:         list_name = node.parent.children[0].value
0907:         list_info = self.lookup_variable(list_name)
0908: 
0909:         index = self.interpret(node.children[0].children[0])
0910: 
0911:         if not isinstance(index, int):
0912:             raise InterpreterError("Runtime Error: Insert index must be an integer", node.line)
0913: 
0914:         if index < 0 or index > len(list_info["value"]):  # type: ignore
0915:             raise InterpreterError(f"Runtime Error: Index {index} out of range for insert", node.line)
0916: 
0917:         for child in node.children[1:]:
0918:             value = self.interpret(child)
0919:             list_info["value"].insert(index, value)  # type: ignore
0920:             index += 1
0921: 
0922: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 905 | `    def eval_insert(self, node):` | Executes list insertion behavior. |
| 906 | `        list_name = node.parent.children[0].value` | Assigns/computes a value and stores it in `list_name` for later use in this method. |
| 907 | `        list_info = self.lookup_variable(list_name)` | Finds a variable record in the active runtime scopes. |
| 908 | `` | Blank line used to separate code sections for readability. |
| 909 | `        index = self.interpret(node.children[0].children[0])` | Recursively sends another AST node back to the interpreter dispatcher. |
| 910 | `` | Blank line used to separate code sections for readability. |
| 911 | `        if not isinstance(index, int):` | Conditional branch that decides which runtime path should run. |
| 912 | `            raise InterpreterError("Runtime Error: Insert index must be an integer", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 913 | `` | Blank line used to separate code sections for readability. |
| 914 | `        if index < 0 or index > len(list_info["value"]):  # type: ignore` | Conditional branch that decides which runtime path should run. |
| 915 | `            raise InterpreterError(f"Runtime Error: Index {index} out of range for insert", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 916 | `` | Blank line used to separate code sections for readability. |
| 917 | `        for child in node.children[1:]:` | Loops through child AST nodes and processes each one in order. |
| 918 | `            value = self.interpret(child)` | Recursively sends another AST node back to the interpreter dispatcher. |
| 919 | `            list_info["value"].insert(index, value)  # type: ignore` | Runtime support statement used by the interpreter. |
| 920 | `            index += 1` | Assigns/computes a value and stores it in `index +` for later use in this method. |
| 921 | `` | Blank line used to separate code sections for readability. |
| 922 | `` | Blank line used to separate code sections for readability. |

### eval_remove - Lines 923-940

Purpose: Executes list removal behavior.

Process flow:

- Executes list removal behavior.

Code:

```python
0923:     def eval_remove(self, node):
0924:         list_name = node.children[0].value
0925:         index_node = node.children[1].children[0]
0926: 
0927:         list_info = self.lookup_variable(list_name)
0928:         if isinstance(list_info, str):
0929:             raise InterpreterError(list_info, node.line)
0930: 
0931:         index = self.interpret(index_node)
0932: 
0933:         if not isinstance(index, int):
0934:             raise InterpreterError("Runtime Error: Remove index must be an integer", node.line)
0935: 
0936:         if index < 0 or index >= len(list_info["value"]):
0937:             raise InterpreterError(f"Runtime Error: Index {index} out of bounds for remove", node.line)
0938: 
0939:         removed = list_info["value"].pop(index)
0940: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 923 | `    def eval_remove(self, node):` | Executes list removal behavior. |
| 924 | `        list_name = node.children[0].value` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 925 | `        index_node = node.children[1].children[0]` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 926 | `` | Blank line used to separate code sections for readability. |
| 927 | `        list_info = self.lookup_variable(list_name)` | Finds a variable record in the active runtime scopes. |
| 928 | `        if isinstance(list_info, str):` | Conditional branch that decides which runtime path should run. |
| 929 | `            raise InterpreterError(list_info, node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 930 | `` | Blank line used to separate code sections for readability. |
| 931 | `        index = self.interpret(index_node)` | Recursively sends another AST node back to the interpreter dispatcher. |
| 932 | `` | Blank line used to separate code sections for readability. |
| 933 | `        if not isinstance(index, int):` | Conditional branch that decides which runtime path should run. |
| 934 | `            raise InterpreterError("Runtime Error: Remove index must be an integer", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 935 | `` | Blank line used to separate code sections for readability. |
| 936 | `        if index < 0 or index >= len(list_info["value"]):` | Conditional branch that decides which runtime path should run. |
| 937 | `            raise InterpreterError(f"Runtime Error: Index {index} out of bounds for remove", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 938 | `` | Blank line used to separate code sections for readability. |
| 939 | `        removed = list_info["value"].pop(index)` | Removes and returns an item from a list/dictionary, often during cleanup. |
| 940 | `` | Blank line used to separate code sections for readability. |

### eval_unaryop - Lines 941-1043

Purpose: Executes unary operators like ++, --, !, and ~.

Process flow:

- Executes unary operators like ++, --, !, and ~.

Code:

```python
0941:     def eval_unaryop(self, node):
0942:         if isinstance(node.children[0], MemberAccessNode) and node.value in {"++", "--"}:
0943:             target = node.children[0]
0944:             chain = []
0945:             current = target
0946:             while isinstance(current, MemberAccessNode):
0947:                 chain.append(current.children[1].value)
0948:                 current = current.children[0]
0949:             chain.reverse()
0950:             obj_name = current.value
0951:             var_info = self.lookup_variable(obj_name)
0952:             if isinstance(var_info, str):
0953:                 raise InterpreterError(var_info, node.line)
0954:             bundle_value = var_info["value"]
0955:             if not isinstance(bundle_value, dict):
0956:                 raise InterpreterError(f"Runtime Error: Variable '{obj_name}' is not a bundle.", node.line)
0957:             for member in chain[:-1]:
0958:                 if member not in bundle_value:
0959:                     raise InterpreterError(f"Runtime Error: Bundle has no member '{member}'.", node.line)
0960:                 bundle_value = bundle_value[member]
0961:                 if not isinstance(bundle_value, dict):
0962:                     raise InterpreterError(f"Runtime Error: Member '{member}' is not a bundle.", node.line)
0963:             final_member = chain[-1]
0964:             if final_member not in bundle_value:
0965:                 raise InterpreterError(f"Runtime Error: Bundle has no member '{final_member}'.", node.line)
0966:             original = bundle_value[final_member]
0967:             new_value = original + 1 if node.value == "++" else original - 1
0968:             bundle_value[final_member] = new_value
0969:             return original if node.position == "post" else new_value
0970: 
0971:         if not isinstance(node.children[0], ListAccessNode):
0972:             operand_node = node.children[0]
0973:             operand_name = operand_node.value
0974:             var_info = self.lookup_variable(operand_name)
0975: 
0976:             if node.value == "++":
0977:                 if isinstance(var_info, str):
0978:                     raise InterpreterError(var_info, node.line)
0979:                 if node.position == "pre":
0980:                     var_info["value"] += 1
0981:                     return var_info["value"]
0982:                 else:
0983:                     original = var_info["value"]
0984:                     var_info["value"] += 1
0985:                     return original
0986: 
0987:             elif node.value == "--":
0988:                 if isinstance(var_info, str):
0989:                     raise InterpreterError(var_info, node.line)
0990:                 if node.position == "pre":
0991:                     var_info["value"] -= 1
0992:                     return var_info["value"]
0993:                 else:
0994:                     original = var_info["value"]
0995:                     var_info["value"] -= 1
0996:                     return original
0997:             
0998:             elif node.value == "-":
0999:                 value = self.interpret(operand_node)
1000:                 return -value
1001: 
1002:             elif node.value == "~":
1003:                 value = self.interpret(operand_node)
1004:                 return -value
1005: 
1006:             elif node.value == "!":
1007:                 value = self.interpret(operand_node)
1008:                 return not value
1009:             
1010:         else:
1011:             operand_node = node.children[0]
1012:             list_name = operand_node.children[0].value
1013:             index_node = operand_node.children[1]
1014:             index = self.interpret(index_node.children[0])
1015: 
1016:             list_entry = self.lookup_variable(list_name)
1017:             if isinstance(list_entry, str):
1018:                 raise InterpreterError(list_entry, node.line)
1019: 
1020:             list_value = list_entry["value"]
1021: 
1022:             if not isinstance(index, int):
1023:                 raise InterpreterError(f"Runtime Error: List index must be an integer. Got '{index}'", node.line)
1024: 
1025:             if not isinstance(list_value, list):
1026:                 raise InterpreterError(f"Runtime Error: Variable '{list_name}' is not a list.", node.line)
1027: 
1028:             if index < 0 or index >= len(list_value):
1029:                 raise InterpreterError(f"Runtime Error: Index '{index}' out of bounds for list '{list_name}'.", node.line)
1030: 
1031:             if node.value == "++":
1032:                 original = list_value[index]
1033:                 list_value[index] += 1
1034:                 return original if node.position == "post" else list_value[index]
1035: 
1036:             elif node.value == "--":
1037:                 original = list_value[index]
1038:                 list_value[index] -= 1
1039:                 return original if node.position == "post" else list_value[index]
1040: 
1041:         
1042:         raise InterpreterError(f"Unknown unary operator {node.value}", node.line)
1043:     
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 941 | `    def eval_unaryop(self, node):` | Executes unary operators like ++, --, !, and ~. |
| 942 | `        if isinstance(node.children[0], MemberAccessNode) and node.value in {"++", "--"}:` | Checks a condition using values stored inside the AST node children. |
| 943 | `            target = node.children[0]` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 944 | `            chain = []` | Creates a list used to collect runtime values. |
| 945 | `            current = target` | Assigns/computes a value and stores it in `current` for later use in this method. |
| 946 | `            while isinstance(current, MemberAccessNode):` | Repeats a runtime action while the condition remains true. |
| 947 | `                chain.append(current.children[1].value)` | Adds a new item to a list, such as output, parameters, arguments, or evaluated list values. |
| 948 | `                current = current.children[0]` | Assigns/computes a value and stores it in `current` for later use in this method. |
| 949 | `            chain.reverse()` | Calls a function/method to perform part of the runtime operation. |
| 950 | `            obj_name = current.value` | Assigns/computes a value and stores it in `obj_name` for later use in this method. |
| 951 | `            var_info = self.lookup_variable(obj_name)` | Finds a variable record in the active runtime scopes. |
| 952 | `            if isinstance(var_info, str):` | Conditional branch that decides which runtime path should run. |
| 953 | `                raise InterpreterError(var_info, node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 954 | `            bundle_value = var_info["value"]` | Assigns/computes a value and stores it in `bundle_value` for later use in this method. |
| 955 | `            if not isinstance(bundle_value, dict):` | Conditional branch that decides which runtime path should run. |
| 956 | `                raise InterpreterError(f"Runtime Error: Variable '{obj_name}' is not a bundle.", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 957 | `            for member in chain[:-1]:` | Loops through a collection of values/items. |
| 958 | `                if member not in bundle_value:` | Conditional branch that decides which runtime path should run. |
| 959 | `                    raise InterpreterError(f"Runtime Error: Bundle has no member '{member}'.", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 960 | `                bundle_value = bundle_value[member]` | Assigns/computes a value and stores it in `bundle_value` for later use in this method. |
| 961 | `                if not isinstance(bundle_value, dict):` | Conditional branch that decides which runtime path should run. |
| 962 | `                    raise InterpreterError(f"Runtime Error: Member '{member}' is not a bundle.", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 963 | `            final_member = chain[-1]` | Assigns/computes a value and stores it in `final_member` for later use in this method. |
| 964 | `            if final_member not in bundle_value:` | Conditional branch that decides which runtime path should run. |
| 965 | `                raise InterpreterError(f"Runtime Error: Bundle has no member '{final_member}'.", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 966 | `            original = bundle_value[final_member]` | Assigns/computes a value and stores it in `original` for later use in this method. |
| 967 | `            new_value = original + 1 if node.value == "++" else original - 1` | Reads the stored value of the AST node, such as an operator, identifier name, or literal text. |
| 968 | `            bundle_value[final_member] = new_value` | Assigns/computes a value and stores it in `bundle_value[final_member]` for later use in this method. |
| 969 | `            return original if node.position == "post" else new_value` | Returns the computed value/result from this method to its caller. |
| 970 | `` | Blank line used to separate code sections for readability. |
| 971 | `        if not isinstance(node.children[0], ListAccessNode):` | Checks a condition using values stored inside the AST node children. |
| 972 | `            operand_node = node.children[0]` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 973 | `            operand_name = operand_node.value` | Reads the stored value of the AST node, such as an operator, identifier name, or literal text. |
| 974 | `            var_info = self.lookup_variable(operand_name)` | Finds a variable record in the active runtime scopes. |
| 975 | `` | Blank line used to separate code sections for readability. |
| 976 | `            if node.value == "++":` | Conditional branch that decides which runtime path should run. |
| 977 | `                if isinstance(var_info, str):` | Conditional branch that decides which runtime path should run. |
| 978 | `                    raise InterpreterError(var_info, node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 979 | `                if node.position == "pre":` | Conditional branch that decides which runtime path should run. |
| 980 | `                    var_info["value"] += 1` | Assigns/computes a value and stores it in `var_info["value"] +` for later use in this method. |
| 981 | `                    return var_info["value"]` | Returns the computed value/result from this method to its caller. |
| 982 | `                else:` | Fallback branch used when the previous if/elif conditions were false. |
| 983 | `                    original = var_info["value"]` | Assigns/computes a value and stores it in `original` for later use in this method. |
| 984 | `                    var_info["value"] += 1` | Assigns/computes a value and stores it in `var_info["value"] +` for later use in this method. |
| 985 | `                    return original` | Returns the computed value/result from this method to its caller. |
| 986 | `` | Blank line used to separate code sections for readability. |
| 987 | `            elif node.value == "--":` | Conditional branch that decides which runtime path should run. |
| 988 | `                if isinstance(var_info, str):` | Conditional branch that decides which runtime path should run. |
| 989 | `                    raise InterpreterError(var_info, node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 990 | `                if node.position == "pre":` | Conditional branch that decides which runtime path should run. |
| 991 | `                    var_info["value"] -= 1` | Assigns/computes a value and stores it in `var_info["value"] -` for later use in this method. |
| 992 | `                    return var_info["value"]` | Returns the computed value/result from this method to its caller. |
| 993 | `                else:` | Fallback branch used when the previous if/elif conditions were false. |
| 994 | `                    original = var_info["value"]` | Assigns/computes a value and stores it in `original` for later use in this method. |
| 995 | `                    var_info["value"] -= 1` | Assigns/computes a value and stores it in `var_info["value"] -` for later use in this method. |
| 996 | `                    return original` | Returns the computed value/result from this method to its caller. |
| 997 | `            ` | Blank line used to separate code sections for readability. |
| 998 | `            elif node.value == "-":` | Conditional branch that decides which runtime path should run. |
| 999 | `                value = self.interpret(operand_node)` | Recursively sends another AST node back to the interpreter dispatcher. |
| 1000 | `                return -value` | Returns the computed value/result from this method to its caller. |
| 1001 | `` | Blank line used to separate code sections for readability. |
| 1002 | `            elif node.value == "~":` | Conditional branch that decides which runtime path should run. |
| 1003 | `                value = self.interpret(operand_node)` | Recursively sends another AST node back to the interpreter dispatcher. |
| 1004 | `                return -value` | Returns the computed value/result from this method to its caller. |
| 1005 | `` | Blank line used to separate code sections for readability. |
| 1006 | `            elif node.value == "!":` | Conditional branch that decides which runtime path should run. |
| 1007 | `                value = self.interpret(operand_node)` | Recursively sends another AST node back to the interpreter dispatcher. |
| 1008 | `                return not value` | Returns the computed value/result from this method to its caller. |
| 1009 | `            ` | Blank line used to separate code sections for readability. |
| 1010 | `        else:` | Fallback branch used when the previous if/elif conditions were false. |
| 1011 | `            operand_node = node.children[0]` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 1012 | `            list_name = operand_node.children[0].value` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 1013 | `            index_node = operand_node.children[1]` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 1014 | `            index = self.interpret(index_node.children[0])` | Recursively sends another AST node back to the interpreter dispatcher. |
| 1015 | `` | Blank line used to separate code sections for readability. |
| 1016 | `            list_entry = self.lookup_variable(list_name)` | Finds a variable record in the active runtime scopes. |
| 1017 | `            if isinstance(list_entry, str):` | Conditional branch that decides which runtime path should run. |
| 1018 | `                raise InterpreterError(list_entry, node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 1019 | `` | Blank line used to separate code sections for readability. |
| 1020 | `            list_value = list_entry["value"]` | Assigns/computes a value and stores it in `list_value` for later use in this method. |
| 1021 | `` | Blank line used to separate code sections for readability. |
| 1022 | `            if not isinstance(index, int):` | Conditional branch that decides which runtime path should run. |
| 1023 | `                raise InterpreterError(f"Runtime Error: List index must be an integer. Got '{index}'", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 1024 | `` | Blank line used to separate code sections for readability. |
| 1025 | `            if not isinstance(list_value, list):` | Conditional branch that decides which runtime path should run. |
| 1026 | `                raise InterpreterError(f"Runtime Error: Variable '{list_name}' is not a list.", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 1027 | `` | Blank line used to separate code sections for readability. |
| 1028 | `            if index < 0 or index >= len(list_value):` | Conditional branch that decides which runtime path should run. |
| 1029 | `                raise InterpreterError(f"Runtime Error: Index '{index}' out of bounds for list '{list_name}'.", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 1030 | `` | Blank line used to separate code sections for readability. |
| 1031 | `            if node.value == "++":` | Conditional branch that decides which runtime path should run. |
| 1032 | `                original = list_value[index]` | Assigns/computes a value and stores it in `original` for later use in this method. |
| 1033 | `                list_value[index] += 1` | Assigns/computes a value and stores it in `list_value[index] +` for later use in this method. |
| 1034 | `                return original if node.position == "post" else list_value[index]` | Returns the computed value/result from this method to its caller. |
| 1035 | `` | Blank line used to separate code sections for readability. |
| 1036 | `            elif node.value == "--":` | Conditional branch that decides which runtime path should run. |
| 1037 | `                original = list_value[index]` | Assigns/computes a value and stores it in `original` for later use in this method. |
| 1038 | `                list_value[index] -= 1` | Assigns/computes a value and stores it in `list_value[index] -` for later use in this method. |
| 1039 | `                return original if node.position == "post" else list_value[index]` | Returns the computed value/result from this method to its caller. |
| 1040 | `` | Blank line used to separate code sections for readability. |
| 1041 | `        ` | Blank line used to separate code sections for readability. |
| 1042 | `        raise InterpreterError(f"Unknown unary operator {node.value}", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 1043 | `    ` | Blank line used to separate code sections for readability. |

### eval_cast - Lines 1044-1063

Purpose: Converts values to a requested GAL type.

Process flow:

- Converts values to a requested GAL type.

Code:

```python
1044:     def eval_cast(self, node):
1045:         value = self.interpret(node.children[1])
1046:         cast_type = node.children[0].value
1047: 
1048:         if cast_type == "seed":
1049:             return int(value)
1050:         elif cast_type == "tree":
1051:             return float(value)
1052:         elif cast_type == "leaf":
1053:             if isinstance(value, int):
1054:                 return chr(value)
1055:             return str(value)[0] if value else '\0'
1056:         elif cast_type == "branch":
1057:             return bool(value)
1058:         elif cast_type == "vine":
1059:             return str(value)
1060:         else:
1061:             raise InterpreterError(f"Unknown cast type: {cast_type}", node.line)
1062: 
1063: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 1044 | `    def eval_cast(self, node):` | Converts values to a requested GAL type. |
| 1045 | `        value = self.interpret(node.children[1])` | Recursively sends another AST node back to the interpreter dispatcher. |
| 1046 | `        cast_type = node.children[0].value` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 1047 | `` | Blank line used to separate code sections for readability. |
| 1048 | `        if cast_type == "seed":` | Conditional branch that decides which runtime path should run. |
| 1049 | `            return int(value)` | Returns the computed value/result from this method to its caller. |
| 1050 | `        elif cast_type == "tree":` | Conditional branch that decides which runtime path should run. |
| 1051 | `            return float(value)` | Returns the computed value/result from this method to its caller. |
| 1052 | `        elif cast_type == "leaf":` | Conditional branch that decides which runtime path should run. |
| 1053 | `            if isinstance(value, int):` | Conditional branch that decides which runtime path should run. |
| 1054 | `                return chr(value)` | Returns the computed value/result from this method to its caller. |
| 1055 | `            return str(value)[0] if value else '\0'` | Returns the computed value/result from this method to its caller. |
| 1056 | `        elif cast_type == "branch":` | Conditional branch that decides which runtime path should run. |
| 1057 | `            return bool(value)` | Returns the computed value/result from this method to its caller. |
| 1058 | `        elif cast_type == "vine":` | Conditional branch that decides which runtime path should run. |
| 1059 | `            return str(value)` | Returns the computed value/result from this method to its caller. |
| 1060 | `        else:` | Fallback branch used when the previous if/elif conditions were false. |
| 1061 | `            raise InterpreterError(f"Unknown cast type: {cast_type}", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 1062 | `` | Blank line used to separate code sections for readability. |
| 1063 | `` | Blank line used to separate code sections for readability. |

### eval_soil - Lines 1064-1068

Purpose: Converts a string variable to lowercase.

Process flow:

- Converts a string variable to lowercase.

Code:

```python
1064:     def eval_soil(self, node):
1065:         var_name = node.children[0].value
1066:         var_info = self.lookup_variable(var_name)
1067:         return var_info["value"].lower()  # type: ignore
1068: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 1064 | `    def eval_soil(self, node):` | Converts a string variable to lowercase. |
| 1065 | `        var_name = node.children[0].value` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 1066 | `        var_info = self.lookup_variable(var_name)` | Finds a variable record in the active runtime scopes. |
| 1067 | `        return var_info["value"].lower()  # type: ignore` | Returns the computed value/result from this method to its caller. |
| 1068 | `` | Blank line used to separate code sections for readability. |

### eval_bloom - Lines 1069-1073

Purpose: Converts a string variable to uppercase.

Process flow:

- Converts a string variable to uppercase.

Code:

```python
1069:     def eval_bloom(self, node):
1070:         var_name = node.children[0].value
1071:         var_info = self.lookup_variable(var_name)
1072:         return var_info["value"].upper()  # type: ignore
1073: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 1069 | `    def eval_bloom(self, node):` | Converts a string variable to uppercase. |
| 1070 | `        var_name = node.children[0].value` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 1071 | `        var_info = self.lookup_variable(var_name)` | Finds a variable record in the active runtime scopes. |
| 1072 | `        return var_info["value"].upper()  # type: ignore` | Returns the computed value/result from this method to its caller. |
| 1073 | `` | Blank line used to separate code sections for readability. |

### eval_if_statement - Lines 1074-1116

Purpose: Executes spring/bud/wither conditional logic.

Process flow:

- Evaluate the spring condition.

- If true, run the spring block.

- If false, check bud blocks.

- If no bud is true, run wither block if present.

- Exit conditional scopes after execution.

Code:

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
1116:     
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 1074 | `    def eval_if_statement(self, node):` | Executes spring/bud/wither conditional logic. |
| 1075 | `        condition_result = self.interpret(node.children[0].children[0])` | Recursively sends another AST node back to the interpreter dispatcher. |
| 1076 | `        self.enter_scope()` | Creates a new local runtime scope. |
| 1077 | `` | Blank line used to separate code sections for readability. |
| 1078 | `` | Blank line used to separate code sections for readability. |
| 1079 | `        try:` | Starts a protected block where errors can be handled by except/finally. |
| 1080 | `            if condition_result:` | Conditional branch that decides which runtime path should run. |
| 1081 | `                self.eval_block(node.children[1])` | Calls a function/method to perform part of the runtime operation. |
| 1082 | `            ` | Blank line used to separate code sections for readability. |
| 1083 | `            else:` | Fallback branch used when the previous if/elif conditions were false. |
| 1084 | `                current_node = 2` | Assigns/computes a value and stores it in `current_node` for later use in this method. |
| 1085 | `                while current_node < len(node.children):` | Repeats a runtime action while the condition remains true. |
| 1086 | `                    ` | Blank line used to separate code sections for readability. |
| 1087 | `                    elif_node = node.children[current_node]` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 1088 | `` | Blank line used to separate code sections for readability. |
| 1089 | `                    if elif_node.node_type == "ElseIfStatement":` | Conditional branch that decides which runtime path should run. |
| 1090 | `                        elif_condition_result = self.interpret(elif_node.children[0].children[0])` | Recursively sends another AST node back to the interpreter dispatcher. |
| 1091 | `` | Blank line used to separate code sections for readability. |
| 1092 | `                        if not isinstance(elif_condition_result, bool):` | Conditional branch that decides which runtime path should run. |
| 1093 | `                            raise InterpreterError(f"Runtime Error: Condition must be a boolean. Got '{condition_result}'", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 1094 | `                        ` | Blank line used to separate code sections for readability. |
| 1095 | `                        if elif_condition_result:` | Conditional branch that decides which runtime path should run. |
| 1096 | `                            try:` | Starts a protected block where errors can be handled by except/finally. |
| 1097 | `                                self.enter_scope()` | Creates a new local runtime scope. |
| 1098 | `                                self.eval_block(elif_node.children[1])` | Calls a function/method to perform part of the runtime operation. |
| 1099 | `                            finally:` | Cleanup block that runs even if the try block returns or raises an error. |
| 1100 | `                                self.exit_scope()` | Leaves/removes the current local runtime scope. |
| 1101 | `                            return` | Stops this method without returning a meaningful value. |
| 1102 | `                        ` | Blank line used to separate code sections for readability. |
| 1103 | `                    elif elif_node.node_type == "ElseStatement":` | Conditional branch that decides which runtime path should run. |
| 1104 | `                        try:` | Starts a protected block where errors can be handled by except/finally. |
| 1105 | `                            self.enter_scope()` | Creates a new local runtime scope. |
| 1106 | `                            self.eval_block(elif_node.children[0])` | Calls a function/method to perform part of the runtime operation. |
| 1107 | `                        finally:` | Cleanup block that runs even if the try block returns or raises an error. |
| 1108 | `                            self.exit_scope()` | Leaves/removes the current local runtime scope. |
| 1109 | `                        return` | Stops this method without returning a meaningful value. |
| 1110 | `` | Blank line used to separate code sections for readability. |
| 1111 | `                    current_node += 1` | Assigns/computes a value and stores it in `current_node +` for later use in this method. |
| 1112 | `        finally:` | Cleanup block that runs even if the try block returns or raises an error. |
| 1113 | `            self.exit_scope()` | Leaves/removes the current local runtime scope. |
| 1114 | `` | Blank line used to separate code sections for readability. |
| 1115 | `        return None` | Returns the computed value/result from this method to its caller. |
| 1116 | `    ` | Blank line used to separate code sections for readability. |

### eval_for_loop - Lines 1117-1166

Purpose: Executes cultivate loops.

Process flow:

- Enter loop tracking.

- Evaluate loop condition/control values.

- Execute block while rules allow.

- Handle skip/prune flags.

- Exit loop tracking and scope.

Code:

```python
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
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 1117 | `    def eval_for_loop(self, node):` | Executes cultivate loops. |
| 1118 | `        self.enter_loop('for')` | Marks that execution is now inside a loop. |
| 1119 | `        self.enter_scope()` | Creates a new local runtime scope. |
| 1120 | `        MAX_LOOP_ITERATIONS = 10000` | Assigns/computes a value and stores it in `MAX_LOOP_ITERATIONS` for later use in this method. |
| 1121 | `        LOOP_COUNTER = 0` | Assigns/computes a value and stores it in `LOOP_COUNTER` for later use in this method. |
| 1122 | `` | Blank line used to separate code sections for readability. |
| 1123 | `        try:` | Starts a protected block where errors can be handled by except/finally. |
| 1124 | `            instantiate_node = node.children[0]` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 1125 | `` | Blank line used to separate code sections for readability. |
| 1126 | `            if isinstance(instantiate_node, VariableDeclarationNode):` | Conditional branch that decides which runtime path should run. |
| 1127 | `                var_type = instantiate_node.children[0].value` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 1128 | `                var_name = instantiate_node.children[1].value` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 1129 | `                initial_value_node = self.interpret(instantiate_node.children[2])` | Recursively sends another AST node back to the interpreter dispatcher. |
| 1130 | `                self.declare_variable(var_name, var_type, initial_value_node)` | Creates a variable record in the current scope. |
| 1131 | `` | Blank line used to separate code sections for readability. |
| 1132 | `            elif isinstance(instantiate_node, AssignmentNode):` | Conditional branch that decides which runtime path should run. |
| 1133 | `                var_name = instantiate_node.children[0].value` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 1134 | `                initial_value_node = self.interpret(instantiate_node.children[1])` | Recursively sends another AST node back to the interpreter dispatcher. |
| 1135 | `                self.lookup_variable(var_name)["value"] = initial_value_node  # type: ignore` | Finds a variable record in the active runtime scopes. |
| 1136 | `` | Blank line used to separate code sections for readability. |
| 1137 | `            condition_node = node.children[1].children[0]` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 1138 | `            condition_result = self.interpret(condition_node)` | Recursively sends another AST node back to the interpreter dispatcher. |
| 1139 | `` | Blank line used to separate code sections for readability. |
| 1140 | `            if not isinstance(condition_result, bool):` | Conditional branch that decides which runtime path should run. |
| 1141 | `                raise InterpreterError(f"Runtime Error: Condition must be a boolean. Got '{condition_result}'", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 1142 | `` | Blank line used to separate code sections for readability. |
| 1143 | `            while condition_result:` | Repeats a runtime action while the condition remains true. |
| 1144 | `                LOOP_COUNTER += 1` | Assigns/computes a value and stores it in `LOOP_COUNTER +` for later use in this method. |
| 1145 | `                if LOOP_COUNTER > MAX_LOOP_ITERATIONS:` | Conditional branch that decides which runtime path should run. |
| 1146 | `                    raise InterpreterError("Runtime Error: Infinite loop detected!", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 1147 | `` | Blank line used to separate code sections for readability. |
| 1148 | `                ` | Blank line used to separate code sections for readability. |
| 1149 | `                self.eval_block(node.children[3])` | Calls a function/method to perform part of the runtime operation. |
| 1150 | `` | Blank line used to separate code sections for readability. |
| 1151 | `                if self.continue_flag:` | Conditional branch that decides which runtime path should run. |
| 1152 | `                    self.continue_flag = False  ` | Stores/updates flag set when skip/continue is triggered. |
| 1153 | `` | Blank line used to separate code sections for readability. |
| 1154 | `                if self.break_triggered():` | Conditional branch that decides which runtime path should run. |
| 1155 | `                    break` | Runtime support statement used by the interpreter. |
| 1156 | `                ` | Blank line used to separate code sections for readability. |
| 1157 | `                for update_expr in node.children[2].children:` | Loops through child AST nodes and processes each one in order. |
| 1158 | `                    self.interpret(update_expr)` | Recursively sends another AST node back to the interpreter dispatcher. |
| 1159 | `` | Blank line used to separate code sections for readability. |
| 1160 | `                condition_result = self.interpret(condition_node)` | Recursively sends another AST node back to the interpreter dispatcher. |
| 1161 | `` | Blank line used to separate code sections for readability. |
| 1162 | `        finally:` | Cleanup block that runs even if the try block returns or raises an error. |
| 1163 | `            self.exit_scope()` | Leaves/removes the current local runtime scope. |
| 1164 | `            self.exit_loop()` | Leaves the current loop and resets loop control flags. |
| 1165 | `` | Blank line used to separate code sections for readability. |
| 1166 | `` | Blank line used to separate code sections for readability. |

### eval_while_loop - Lines 1167-1200

Purpose: Executes grow loops.

Process flow:

- Enter loop tracking.

- Evaluate loop condition/control values.

- Execute block while rules allow.

- Handle skip/prune flags.

- Exit loop tracking and scope.

Code:

```python
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
1193: 
1194:                 condition_result = self.interpret(condition_node)
1195: 
1196:         finally:
1197:             self.exit_loop()
1198:             self.exit_scope()
1199: 
1200: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 1167 | `    def eval_while_loop(self, node):` | Executes grow loops. |
| 1168 | `        self.enter_loop('while')` | Marks that execution is now inside a loop. |
| 1169 | `        self.enter_scope()` | Creates a new local runtime scope. |
| 1170 | `        MAX_LOOP_ITERATIONS = 10000` | Assigns/computes a value and stores it in `MAX_LOOP_ITERATIONS` for later use in this method. |
| 1171 | `        LOOP_COUNTER = 0` | Assigns/computes a value and stores it in `LOOP_COUNTER` for later use in this method. |
| 1172 | `        condition_node = node.children[0].children[0]` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 1173 | `` | Blank line used to separate code sections for readability. |
| 1174 | `        try:` | Starts a protected block where errors can be handled by except/finally. |
| 1175 | `            condition_result = self.interpret(condition_node)` | Recursively sends another AST node back to the interpreter dispatcher. |
| 1176 | `` | Blank line used to separate code sections for readability. |
| 1177 | `            if not isinstance(condition_result, bool):` | Conditional branch that decides which runtime path should run. |
| 1178 | `                raise InterpreterError(f"Runtime Error: Condition must be a boolean. Got '{condition_result}'", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 1179 | `` | Blank line used to separate code sections for readability. |
| 1180 | `            while condition_result:` | Repeats a runtime action while the condition remains true. |
| 1181 | `                LOOP_COUNTER += 1` | Assigns/computes a value and stores it in `LOOP_COUNTER +` for later use in this method. |
| 1182 | `                if LOOP_COUNTER > MAX_LOOP_ITERATIONS:` | Conditional branch that decides which runtime path should run. |
| 1183 | `                    raise InterpreterError("Runtime Error: Infinite loop detected!", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 1184 | `` | Blank line used to separate code sections for readability. |
| 1185 | `                block_node = node.children[1]` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 1186 | `                self.eval_block(block_node)` | Calls a function/method to perform part of the runtime operation. |
| 1187 | `` | Blank line used to separate code sections for readability. |
| 1188 | `                if self.continue_flag:` | Conditional branch that decides which runtime path should run. |
| 1189 | `                    self.continue_flag = False` | Stores/updates flag set when skip/continue is triggered. |
| 1190 | `` | Blank line used to separate code sections for readability. |
| 1191 | `                if self.break_triggered():` | Conditional branch that decides which runtime path should run. |
| 1192 | `                    break` | Runtime support statement used by the interpreter. |
| 1193 | `` | Blank line used to separate code sections for readability. |
| 1194 | `                condition_result = self.interpret(condition_node)` | Recursively sends another AST node back to the interpreter dispatcher. |
| 1195 | `` | Blank line used to separate code sections for readability. |
| 1196 | `        finally:` | Cleanup block that runs even if the try block returns or raises an error. |
| 1197 | `            self.exit_loop()` | Leaves the current loop and resets loop control flags. |
| 1198 | `            self.exit_scope()` | Leaves/removes the current local runtime scope. |
| 1199 | `` | Blank line used to separate code sections for readability. |
| 1200 | `` | Blank line used to separate code sections for readability. |

### eval_do_while_loop - Lines 1201-1231

Purpose: Executes tend/wither style do-while loops.

Process flow:

- Enter loop tracking.

- Evaluate loop condition/control values.

- Execute block while rules allow.

- Handle skip/prune flags.

- Exit loop tracking and scope.

Code:

```python
1201:     def eval_do_while_loop(self, node):
1202:         self.enter_loop('do-while')
1203:         MAX_LOOP_ITERATIONS = 10000
1204:         LOOP_COUNTER = 0
1205:         condition_node = node.children[1].children[0]
1206:         block_node = node.children[0]
1207: 
1208:         try:
1209:             while True:
1210:                 self.eval_block(block_node)
1211:                 LOOP_COUNTER += 1
1212:                 if LOOP_COUNTER > MAX_LOOP_ITERATIONS:
1213:                     raise InterpreterError("Runtime Error: Infinite loop detected!", node.line)
1214: 
1215:                 if self.continue_flag:
1216:                     self.continue_flag = False
1217: 
1218:                 if self.break_triggered():
1219:                     break
1220: 
1221:                 condition_result = self.interpret(condition_node)
1222: 
1223:                 if not isinstance(condition_result, bool):
1224:                     raise InterpreterError(f"Runtime Error: Condition must be a boolean. Got '{condition_result}'", node.line)
1225: 
1226:                 if not condition_result:
1227:                     break
1228:         finally:
1229:             self.exit_loop()
1230: 
1231:     
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 1201 | `    def eval_do_while_loop(self, node):` | Executes tend/wither style do-while loops. |
| 1202 | `        self.enter_loop('do-while')` | Marks that execution is now inside a loop. |
| 1203 | `        MAX_LOOP_ITERATIONS = 10000` | Assigns/computes a value and stores it in `MAX_LOOP_ITERATIONS` for later use in this method. |
| 1204 | `        LOOP_COUNTER = 0` | Assigns/computes a value and stores it in `LOOP_COUNTER` for later use in this method. |
| 1205 | `        condition_node = node.children[1].children[0]` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 1206 | `        block_node = node.children[0]` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 1207 | `` | Blank line used to separate code sections for readability. |
| 1208 | `        try:` | Starts a protected block where errors can be handled by except/finally. |
| 1209 | `            while True:` | Repeats a runtime action while the condition remains true. |
| 1210 | `                self.eval_block(block_node)` | Calls a function/method to perform part of the runtime operation. |
| 1211 | `                LOOP_COUNTER += 1` | Assigns/computes a value and stores it in `LOOP_COUNTER +` for later use in this method. |
| 1212 | `                if LOOP_COUNTER > MAX_LOOP_ITERATIONS:` | Conditional branch that decides which runtime path should run. |
| 1213 | `                    raise InterpreterError("Runtime Error: Infinite loop detected!", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 1214 | `` | Blank line used to separate code sections for readability. |
| 1215 | `                if self.continue_flag:` | Conditional branch that decides which runtime path should run. |
| 1216 | `                    self.continue_flag = False` | Stores/updates flag set when skip/continue is triggered. |
| 1217 | `` | Blank line used to separate code sections for readability. |
| 1218 | `                if self.break_triggered():` | Conditional branch that decides which runtime path should run. |
| 1219 | `                    break` | Runtime support statement used by the interpreter. |
| 1220 | `` | Blank line used to separate code sections for readability. |
| 1221 | `                condition_result = self.interpret(condition_node)` | Recursively sends another AST node back to the interpreter dispatcher. |
| 1222 | `` | Blank line used to separate code sections for readability. |
| 1223 | `                if not isinstance(condition_result, bool):` | Conditional branch that decides which runtime path should run. |
| 1224 | `                    raise InterpreterError(f"Runtime Error: Condition must be a boolean. Got '{condition_result}'", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 1225 | `` | Blank line used to separate code sections for readability. |
| 1226 | `                if not condition_result:` | Conditional branch that decides which runtime path should run. |
| 1227 | `                    break` | Runtime support statement used by the interpreter. |
| 1228 | `        finally:` | Cleanup block that runs even if the try block returns or raises an error. |
| 1229 | `            self.exit_loop()` | Leaves the current loop and resets loop control flags. |
| 1230 | `` | Blank line used to separate code sections for readability. |
| 1231 | `    ` | Blank line used to separate code sections for readability. |

### eval_break - Lines 1232-1237

Purpose: Executes prune by setting the break flag.

Process flow:

- Executes prune by setting the break flag.

Code:

```python
1232:     def eval_break(self, node):
1233:         if self.loop_stack:
1234:             self.trigger_break()
1235:         else:
1236:             raise InterpreterError("Runtime Error: Break statement used outside of a loop", node.line)
1237: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 1232 | `    def eval_break(self, node):` | Executes prune by setting the break flag. |
| 1233 | `        if self.loop_stack:` | Conditional branch that decides which runtime path should run. |
| 1234 | `            self.trigger_break()` | Calls a function/method to perform part of the runtime operation. |
| 1235 | `        else:` | Fallback branch used when the previous if/elif conditions were false. |
| 1236 | `            raise InterpreterError("Runtime Error: Break statement used outside of a loop", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 1237 | `` | Blank line used to separate code sections for readability. |

### trigger_break - Lines 1238-1240

Purpose: Turns on the runtime break flag.

Process flow:

- Turns on the runtime break flag.

Code:

```python
1238:     def trigger_break(self):
1239:         self.break_flag = True
1240: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 1238 | `    def trigger_break(self):` | Turns on the runtime break flag. |
| 1239 | `        self.break_flag = True` | Stores/updates flag set when prune/break is triggered. |
| 1240 | `` | Blank line used to separate code sections for readability. |

### break_triggered - Lines 1241-1243

Purpose: Checks if a break/prune was triggered.

Process flow:

- Checks if a break/prune was triggered.

Code:

```python
1241:     def break_triggered(self):
1242:         return self.break_flag
1243: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 1241 | `    def break_triggered(self):` | Checks if a break/prune was triggered. |
| 1242 | `        return self.break_flag` | Calls break_flag() on the same interpreter object and returns its result to the caller. |
| 1243 | `` | Blank line used to separate code sections for readability. |

### enter_loop - Lines 1244-1248

Purpose: Records that the interpreter is currently inside a loop.

Process flow:

- Records that the interpreter is currently inside a loop.

Code:

```python
1244:     def enter_loop(self, loop_type):
1245:         self.loop_stack.append(loop_type)
1246:         self.break_flag = False
1247:         self.continue_flag = False
1248: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 1244 | `    def enter_loop(self, loop_type):` | Records that the interpreter is currently inside a loop. |
| 1245 | `        self.loop_stack.append(loop_type)` | Adds a new item to a list, such as output, parameters, arguments, or evaluated list values. |
| 1246 | `        self.break_flag = False` | Stores/updates flag set when prune/break is triggered. |
| 1247 | `        self.continue_flag = False` | Stores/updates flag set when skip/continue is triggered. |
| 1248 | `` | Blank line used to separate code sections for readability. |

### exit_loop - Lines 1249-1254

Purpose: Removes the current loop marker and resets loop flags.

Process flow:

- Removes the current loop marker and resets loop flags.

Code:

```python
1249:     def exit_loop(self):
1250:         if self.loop_stack:
1251:             self.loop_stack.pop()
1252:             self.break_flag = False
1253:             self.continue_flag = False
1254: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 1249 | `    def exit_loop(self):` | Removes the current loop marker and resets loop flags. |
| 1250 | `        if self.loop_stack:` | Conditional branch that decides which runtime path should run. |
| 1251 | `            self.loop_stack.pop()` | Removes and returns an item from a list/dictionary, often during cleanup. |
| 1252 | `            self.break_flag = False` | Stores/updates flag set when prune/break is triggered. |
| 1253 | `            self.continue_flag = False` | Stores/updates flag set when skip/continue is triggered. |
| 1254 | `` | Blank line used to separate code sections for readability. |

### eval_continue - Lines 1255-1260

Purpose: Executes skip by setting the continue flag.

Process flow:

- Executes skip by setting the continue flag.

Code:

```python
1255:     def eval_continue(self, node):
1256:         if self.loop_stack:
1257:             self.trigger_continue()
1258:         else:
1259:             raise InterpreterError("Runtime Error: Continue statement used outside of a loop", node.line)
1260: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 1255 | `    def eval_continue(self, node):` | Executes skip by setting the continue flag. |
| 1256 | `        if self.loop_stack:` | Conditional branch that decides which runtime path should run. |
| 1257 | `            self.trigger_continue()` | Calls a function/method to perform part of the runtime operation. |
| 1258 | `        else:` | Fallback branch used when the previous if/elif conditions were false. |
| 1259 | `            raise InterpreterError("Runtime Error: Continue statement used outside of a loop", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 1260 | `` | Blank line used to separate code sections for readability. |

### continue_triggered - Lines 1261-1263

Purpose: Checks if skip/continue was triggered.

Process flow:

- Checks if skip/continue was triggered.

Code:

```python
1261:     def continue_triggered(self):
1262:         return self.continue_flag
1263: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 1261 | `    def continue_triggered(self):` | Checks if skip/continue was triggered. |
| 1262 | `        return self.continue_flag` | Calls continue_flag() on the same interpreter object and returns its result to the caller. |
| 1263 | `` | Blank line used to separate code sections for readability. |

### trigger_continue - Lines 1264-1267

Purpose: Turns on the runtime continue flag.

Process flow:

- Turns on the runtime continue flag.

Code:

```python
1264:     def trigger_continue(self):
1265:         self.continue_flag = True
1266: 
1267: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 1264 | `    def trigger_continue(self):` | Turns on the runtime continue flag. |
| 1265 | `        self.continue_flag = True` | Stores/updates flag set when skip/continue is triggered. |
| 1266 | `` | Blank line used to separate code sections for readability. |
| 1267 | `` | Blank line used to separate code sections for readability. |

### eval_switch - Lines 1268-1311

Purpose: Executes switch/variety style branching.

Process flow:

- Executes switch/variety style branching.

Code:

```python
1268:     def eval_switch(self, node):
1269:         self.enter_loop('switch')
1270:         self.enter_scope()
1271:         switch_expr_node = node.children[0]
1272:         switch_value = self.interpret(switch_expr_node)
1273: 
1274:         matched_case = False
1275:         break_found = False
1276:         default_case = None
1277: 
1278:         try:
1279:             for case_node in node.children[1:]:
1280:                 label_type = case_node.node_type
1281:                 if label_type == "Case":
1282:                     case_value_node = case_node.children[0]
1283:                     block_node = case_node.children[1]
1284:                     case_value = self.interpret(case_value_node)
1285: 
1286:                     if switch_value == case_value or matched_case:
1287:                         matched_case = True
1288:                         try:
1289:                             self.enter_scope()
1290:                             self.eval_block(block_node)
1291:                             if self.break_triggered():
1292:                                 break_found = True
1293:                                 break
1294:                         finally:
1295:                             self.exit_scope()
1296:                     
1297:                 elif label_type == "Default":
1298:                     default_case = case_node.children[0]
1299:             
1300:             if not matched_case and not break_found and default_case:
1301:                 try:
1302:                     self.enter_scope()
1303:                     self.eval_block(default_case)
1304:                 finally:
1305:                     self.exit_scope()
1306: 
1307:         finally:
1308:             self.exit_loop()
1309:             self.exit_scope()
1310: 
1311: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 1268 | `    def eval_switch(self, node):` | Executes switch/variety style branching. |
| 1269 | `        self.enter_loop('switch')` | Marks that execution is now inside a loop. |
| 1270 | `        self.enter_scope()` | Creates a new local runtime scope. |
| 1271 | `        switch_expr_node = node.children[0]` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 1272 | `        switch_value = self.interpret(switch_expr_node)` | Recursively sends another AST node back to the interpreter dispatcher. |
| 1273 | `` | Blank line used to separate code sections for readability. |
| 1274 | `        matched_case = False` | Assigns/computes a value and stores it in `matched_case` for later use in this method. |
| 1275 | `        break_found = False` | Assigns/computes a value and stores it in `break_found` for later use in this method. |
| 1276 | `        default_case = None` | Assigns/computes a value and stores it in `default_case` for later use in this method. |
| 1277 | `` | Blank line used to separate code sections for readability. |
| 1278 | `        try:` | Starts a protected block where errors can be handled by except/finally. |
| 1279 | `            for case_node in node.children[1:]:` | Loops through child AST nodes and processes each one in order. |
| 1280 | `                label_type = case_node.node_type` | Assigns/computes a value and stores it in `label_type` for later use in this method. |
| 1281 | `                if label_type == "Case":` | Conditional branch that decides which runtime path should run. |
| 1282 | `                    case_value_node = case_node.children[0]` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 1283 | `                    block_node = case_node.children[1]` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 1284 | `                    case_value = self.interpret(case_value_node)` | Recursively sends another AST node back to the interpreter dispatcher. |
| 1285 | `` | Blank line used to separate code sections for readability. |
| 1286 | `                    if switch_value == case_value or matched_case:` | Conditional branch that decides which runtime path should run. |
| 1287 | `                        matched_case = True` | Assigns/computes a value and stores it in `matched_case` for later use in this method. |
| 1288 | `                        try:` | Starts a protected block where errors can be handled by except/finally. |
| 1289 | `                            self.enter_scope()` | Creates a new local runtime scope. |
| 1290 | `                            self.eval_block(block_node)` | Calls a function/method to perform part of the runtime operation. |
| 1291 | `                            if self.break_triggered():` | Conditional branch that decides which runtime path should run. |
| 1292 | `                                break_found = True` | Assigns/computes a value and stores it in `break_found` for later use in this method. |
| 1293 | `                                break` | Runtime support statement used by the interpreter. |
| 1294 | `                        finally:` | Cleanup block that runs even if the try block returns or raises an error. |
| 1295 | `                            self.exit_scope()` | Leaves/removes the current local runtime scope. |
| 1296 | `                    ` | Blank line used to separate code sections for readability. |
| 1297 | `                elif label_type == "Default":` | Conditional branch that decides which runtime path should run. |
| 1298 | `                    default_case = case_node.children[0]` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 1299 | `            ` | Blank line used to separate code sections for readability. |
| 1300 | `            if not matched_case and not break_found and default_case:` | Conditional branch that decides which runtime path should run. |
| 1301 | `                try:` | Starts a protected block where errors can be handled by except/finally. |
| 1302 | `                    self.enter_scope()` | Creates a new local runtime scope. |
| 1303 | `                    self.eval_block(default_case)` | Calls a function/method to perform part of the runtime operation. |
| 1304 | `                finally:` | Cleanup block that runs even if the try block returns or raises an error. |
| 1305 | `                    self.exit_scope()` | Leaves/removes the current local runtime scope. |
| 1306 | `` | Blank line used to separate code sections for readability. |
| 1307 | `        finally:` | Cleanup block that runs even if the try block returns or raises an error. |
| 1308 | `            self.exit_loop()` | Leaves the current loop and resets loop control flags. |
| 1309 | `            self.exit_scope()` | Leaves/removes the current local runtime scope. |
| 1310 | `` | Blank line used to separate code sections for readability. |
| 1311 | `` | Blank line used to separate code sections for readability. |

### emit_input_request - Lines 1312-1314

Purpose: Asks the frontend UI for input when water() is executed.

Process flow:

- Asks the frontend UI for input when water() is executed.

Code:

```python
1312:     def emit_input_request(self, var_name, prompt):
1313:         self.socketio.emit('input_required', {'prompt': prompt, 'variable': var_name})
1314: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 1312 | `    def emit_input_request(self, var_name, prompt):` | Asks the frontend UI for input when water() is executed. |
| 1313 | `        self.socketio.emit('input_required', {'prompt': prompt, 'variable': var_name})` | Sends an event to the frontend/UI, such as output text or an input request. |
| 1314 | `` | Blank line used to separate code sections for readability. |

### provide_input - Lines 1315-1325

Purpose: Receives user input from the frontend and wakes the waiting interpreter.

Process flow:

- Receives user input from the frontend and wakes the waiting interpreter.

Code:

```python
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
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 1315 | `    def provide_input(self, var_name, input_value):` | Receives user input from the frontend and wakes the waiting interpreter. |
| 1316 | `        evt = self.input_events.get(var_name)` | Assigns/computes a value and stores it in `evt` for later use in this method. |
| 1317 | `        if evt is None:` | Conditional branch that decides which runtime path should run. |
| 1318 | `            self.input_values[var_name] = input_value` | Stores/updates dictionary of input values already received from the frontend. |
| 1319 | `            return` | Stops this method without returning a meaningful value. |
| 1320 | `        if _USE_EVENTLET:` | Conditional branch that decides which runtime path should run. |
| 1321 | `            evt.send(input_value)` | Calls a function/method to perform part of the runtime operation. |
| 1322 | `        else:` | Fallback branch used when the previous if/elif conditions were false. |
| 1323 | `            self.input_values[var_name] = input_value` | Stores/updates dictionary of input values already received from the frontend. |
| 1324 | `            evt.set()` | Calls a function/method to perform part of the runtime operation. |
| 1325 | `` | Blank line used to separate code sections for readability. |

### wait_for_input - Lines 1326-1347

Purpose: Pauses execution until the frontend supplies an input value.

Process flow:

- Pauses execution until the frontend supplies an input value.

Code:

```python
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
1347: 
```

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 1326 | `    def wait_for_input(self, var_name):` | Pauses execution until the frontend supplies an input value. |
| 1327 | `        if var_name in self.input_values:` | Conditional branch that decides which runtime path should run. |
| 1328 | `            return self.input_values.pop(var_name)` | Calls input_values() on the same interpreter object and returns its result to the caller. |
| 1329 | `` | Blank line used to separate code sections for readability. |
| 1330 | `        if _USE_EVENTLET:` | Conditional branch that decides which runtime path should run. |
| 1331 | `            evt = _ev.Event()` | Assigns/computes a value and stores it in `evt` for later use in this method. |
| 1332 | `            self.input_events[var_name] = evt` | Stores/updates dictionary of waiting input events by variable name. |
| 1333 | `            value = evt.wait()` | Assigns/computes a value and stores it in `value` for later use in this method. |
| 1334 | `            self.input_events.pop(var_name, None)` | Removes and returns an item from a list/dictionary, often during cleanup. |
| 1335 | `            if getattr(self, '_cancelled', False):` | Conditional branch that decides which runtime path should run. |
| 1336 | `                raise _CancelledError()` | Calls a function/method to perform part of the runtime operation. |
| 1337 | `            return value` | Returns the computed value/result from this method to its caller. |
| 1338 | `        else:` | Fallback branch used when the previous if/elif conditions were false. |
| 1339 | `            event = threading.Event()` | Assigns/computes a value and stores it in `event` for later use in this method. |
| 1340 | `            self.input_events[var_name] = event` | Stores/updates dictionary of waiting input events by variable name. |
| 1341 | `            event.wait()` | Calls a function/method to perform part of the runtime operation. |
| 1342 | `            if getattr(self, '_cancelled', False):` | Conditional branch that decides which runtime path should run. |
| 1343 | `                raise _CancelledError()` | Calls a function/method to perform part of the runtime operation. |
| 1344 | `            value = self.input_values.pop(var_name, None)` | Removes and returns an item from a list/dictionary, often during cleanup. |
| 1345 | `            self.input_events.pop(var_name, None)` | Removes and returns an item from a list/dictionary, often during cleanup. |
| 1346 | `            return value` | Returns the computed value/result from this method to its caller. |
| 1347 | `` | Blank line used to separate code sections for readability. |

### eval_input - Lines 1348-1442

Purpose: Executes water(), determines expected type, waits for input, and converts it.

Process flow:

- Find where water() is being used.

- Determine target variable name and expected GAL type.

- Ask frontend for input.

- Wait for the input value.

- Convert the input string into the expected runtime type.

- Return the converted input.

Code:

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

Line-by-line notes:

| Line | Code | Explanation |
|---|---|---|
| 1348 | `    def eval_input(self, node):` | Executes water(), determines expected type, waits for input, and converts it. |
| 1349 | `        parent_node = node.parent` | Assigns/computes a value and stores it in `parent_node` for later use in this method. |
| 1350 | `        if isinstance(parent_node, VariableDeclarationNode):` | Conditional branch that decides which runtime path should run. |
| 1351 | `            var_name = parent_node.children[1].value` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 1352 | `            var_type = parent_node.children[0].value` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 1353 | `        ` | Blank line used to separate code sections for readability. |
| 1354 | `        elif isinstance(parent_node, AssignmentNode):` | Conditional branch that decides which runtime path should run. |
| 1355 | `            target = parent_node.children[0]` | Reads a specific child from the AST node. Child indexes represent parts such as type, name, condition, target, or value. |
| 1356 | `            if isinstance(target, ListAccessNode):` | Conditional branch that decides which runtime path should run. |
| 1357 | `                current = target` | Assigns/computes a value and stores it in `current` for later use in this method. |
| 1358 | `                while hasattr(current, 'node_type') and current.node_type == "ListAccess":` | Repeats a runtime action while the condition remains true. |
| 1359 | `                    current = current.children[0].value` | Assigns/computes a value and stores it in `current` for later use in this method. |
| 1360 | `                var_name = current if isinstance(current, str) else str(current)` | Assigns/computes a value and stores it in `var_name` for later use in this method. |
| 1361 | `                var_type = self.lookup_variable(var_name)["type"]  # type: ignore` | Finds a variable record in the active runtime scopes. |
| 1362 | `            else:` | Fallback branch used when the previous if/elif conditions were false. |
| 1363 | `                var_name = target.value` | Assigns/computes a value and stores it in `var_name` for later use in this method. |
| 1364 | `                var_type = self.lookup_variable(var_name)["type"]  # type: ignore` | Finds a variable record in the active runtime scopes. |
| 1365 | `` | Blank line used to separate code sections for readability. |
| 1366 | `        else:` | Fallback branch used when the previous if/elif conditions were false. |
| 1367 | `            var_name = "_input"` | Assigns/computes a value and stores it in `var_name` for later use in this method. |
| 1368 | `            if node.value and "(" in node.value:` | Conditional branch that decides which runtime path should run. |
| 1369 | `                inner = node.value.split("(")[1].rstrip(")")` | Reads the stored value of the AST node, such as an operator, identifier name, or literal text. |
| 1370 | `                var_type = inner if inner in {"seed", "tree", "leaf", "branch", "vine"} else "vine"` | Assigns/computes a value and stores it in `var_type` for later use in this method. |
| 1371 | `            else:` | Fallback branch used when the previous if/elif conditions were false. |
| 1372 | `                var_type = "vine"` | Assigns/computes a value and stores it in `var_type` for later use in this method. |
| 1373 | `` | Blank line used to separate code sections for readability. |
| 1374 | `        prompt = f"Input for {var_name}: "` | Assigns/computes a value and stores it in `prompt` for later use in this method. |
| 1375 | `        self.input_required = True` | Stores/updates flag showing the program is waiting for water() input. |
| 1376 | `` | Blank line used to separate code sections for readability. |
| 1377 | `` | Blank line used to separate code sections for readability. |
| 1378 | `        self.emit_input_request(var_name, prompt)` | Calls a function/method to perform part of the runtime operation. |
| 1379 | `` | Blank line used to separate code sections for readability. |
| 1380 | `        input_value = self.wait_for_input(var_name)` | Assigns/computes a value and stores it in `input_value` for later use in this method. |
| 1381 | `` | Blank line used to separate code sections for readability. |
| 1382 | `` | Blank line used to separate code sections for readability. |
| 1383 | `        self.input_required = False` | Stores/updates flag showing the program is waiting for water() input. |
| 1384 | `` | Blank line used to separate code sections for readability. |
| 1385 | `        if var_type == "seed":` | Checks the declared GAL type so the runtime can validate or convert the value. |
| 1386 | `            original_input = input_value` | Assigns/computes a value and stores it in `original_input` for later use in this method. |
| 1387 | `            if isinstance(input_value, str) and input_value.startswith('-'):` | Conditional branch that decides which runtime path should run. |
| 1388 | `                raise InterpreterError(f"Runtime Error: GAL uses '~' for negative numbers, not '-'. Got '{original_input}'; did you mean '~{original_input[1:]}'?", node.line)  # type: ignore` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 1389 | `            if isinstance(input_value, str) and input_value.startswith('~'):` | Conditional branch that decides which runtime path should run. |
| 1390 | `                input_value = '-' + input_value[1:]` | Assigns/computes a value and stores it in `input_value` for later use in this method. |
| 1391 | `            try:` | Starts a protected block where errors can be handled by except/finally. |
| 1392 | `                if len(input_value.strip('-').lstrip('0')) > 16:` | Conditional branch that decides which runtime path should run. |
| 1393 | `                    raise InterpreterError(f"Runtime Error: Input value exceeds maximum number of 16 digits", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 1394 | `                input_value = int(float(input_value))  # type: ignore` | Assigns/computes a value and stores it in `input_value` for later use in this method. |
| 1395 | `            except ValueError:` | Handles an error or special control-flow case. |
| 1396 | `                raise InterpreterError(f"Runtime Error: Expected integer value, got '{original_input}'", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 1397 | `` | Blank line used to separate code sections for readability. |
| 1398 | `        elif var_type == "tree":` | Checks the declared GAL type so the runtime can validate or convert the value. |
| 1399 | `            original_input = input_value` | Assigns/computes a value and stores it in `original_input` for later use in this method. |
| 1400 | `            if isinstance(input_value, str) and input_value.startswith('-'):` | Conditional branch that decides which runtime path should run. |
| 1401 | `                raise InterpreterError(f"Runtime Error: GAL uses '~' for negative numbers, not '-'. Got '{original_input}'; did you mean '~{original_input[1:]}'?", node.line)  # type: ignore` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 1402 | `            if isinstance(input_value, str) and input_value.startswith('~'):` | Conditional branch that decides which runtime path should run. |
| 1403 | `                input_value = '-' + input_value[1:]` | Assigns/computes a value and stores it in `input_value` for later use in this method. |
| 1404 | `            try:` | Starts a protected block where errors can be handled by except/finally. |
| 1405 | `                if '.' in input_value:  # type: ignore` | Conditional branch that decides which runtime path should run. |
| 1406 | `                    integer_part, decimal_part = str(input_value).split('.')` | Assigns/computes a value and stores it in `integer_part, decimal_part` for later use in this method. |
| 1407 | `                    if len(integer_part.strip('-').lstrip('0')) > 16:` | Conditional branch that decides which runtime path should run. |
| 1408 | `                        raise InterpreterError(f"Runtime Error: Input value exceeds maximum number of 16 digits", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 1409 | `                    if len(decimal_part.rstrip('0')) > 5:` | Conditional branch that decides which runtime path should run. |
| 1410 | `                        raise InterpreterError(f"Runtime Error: Input value exceeds maximum number of 5 decimal numbers", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 1411 | `` | Blank line used to separate code sections for readability. |
| 1412 | `                else:` | Fallback branch used when the previous if/elif conditions were false. |
| 1413 | `                    if len(input_value.strip('-').lstrip('0')) > 16:` | Conditional branch that decides which runtime path should run. |
| 1414 | `                        raise InterpreterError(f"Runtime Error: Input value exceeds maximum number of 16 digits", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 1415 | `` | Blank line used to separate code sections for readability. |
| 1416 | `                input_value = float(input_value)  # type: ignore` | Assigns/computes a value and stores it in `input_value` for later use in this method. |
| 1417 | `` | Blank line used to separate code sections for readability. |
| 1418 | `` | Blank line used to separate code sections for readability. |
| 1419 | `            except ValueError:` | Handles an error or special control-flow case. |
| 1420 | `                raise InterpreterError(f"Runtime Error: Expected float value, got '{original_input}'", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 1421 | `` | Blank line used to separate code sections for readability. |
| 1422 | `        elif var_type == "branch":` | Checks the declared GAL type so the runtime can validate or convert the value. |
| 1423 | `            if input_value == "true" or input_value == "false":` | Conditional branch that decides which runtime path should run. |
| 1424 | `                suggestion = "sunshine" if input_value == "true" else "frost"` | Assigns/computes a value and stores it in `suggestion` for later use in this method. |
| 1425 | `                raise InterpreterError(f"Runtime Error: GAL uses 'sunshine' and 'frost' for booleans, not 'true'/'false'. Got '{input_value}'; did you mean '{suggestion}'?", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 1426 | `            if input_value == "sunshine":` | Conditional branch that decides which runtime path should run. |
| 1427 | `                input_value = True` | Assigns/computes a value and stores it in `input_value` for later use in this method. |
| 1428 | `            elif input_value == "frost":` | Conditional branch that decides which runtime path should run. |
| 1429 | `                input_value = False` | Assigns/computes a value and stores it in `input_value` for later use in this method. |
| 1430 | `            else:` | Fallback branch used when the previous if/elif conditions were false. |
| 1431 | `                raise InterpreterError(f"Runtime Error: expected branch value (sunshine/frost), got '{input_value}'", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 1432 | `            ` | Blank line used to separate code sections for readability. |
| 1433 | `        elif var_type == "leaf":` | Checks the declared GAL type so the runtime can validate or convert the value. |
| 1434 | `            if len(input_value) != 1:  # type: ignore` | Conditional branch that decides which runtime path should run. |
| 1435 | `                raise InterpreterError(f"Runtime Error: Expected a single character for leaf, got '{input_value}'", node.line)` | Creates a runtime error message and stops execution for an invalid runtime situation. |
| 1436 | `            input_value = str(input_value)` | Assigns/computes a value and stores it in `input_value` for later use in this method. |
| 1437 | `` | Blank line used to separate code sections for readability. |
| 1438 | `        elif var_type == "vine":` | Checks the declared GAL type so the runtime can validate or convert the value. |
| 1439 | `            input_value = str(input_value)` | Assigns/computes a value and stores it in `input_value` for later use in this method. |
| 1440 | `` | Blank line used to separate code sections for readability. |
| 1441 | `        return input_value` | Returns the computed value/result from this method to its caller. |
| 1442 | `` | Blank line used to separate code sections for readability. |

## 6. Defense Shortcut

Use this if you need a short spoken explanation:

```text
Sa interpreter, ang pinaka-start is interpret(ast). Usually ProgramNode muna ang node, kaya papasok siya sa eval_program. Doon nireregister muna ang top-level declarations and functions, then automatic niyang tatawagin ang root(). Pag root function call na, eval_function_call ang bahala gumawa ng scope, mag-bind ng parameters kung meron, at patakbuhin ang body gamit eval_block. Sa eval_block, every statement pinapasa ulit sa interpret(), kaya automatic siyang napupunta sa eval_variable_declaration, eval_assignment, eval_print, eval_input, eval_if_statement, eval_binary_op, or eval_return depende sa AST node type. Basically, interpret() ang dispatcher, and bawat eval_* method ang actual executor ng specific language feature.
```