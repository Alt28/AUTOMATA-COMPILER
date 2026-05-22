# File 4 of 7: Parser, AST, Semantic, ICG, and Interpreter

This section continues the defense guide after `server.py`, tokens/errors, and `lexer.py`. It covers the rest of the backend compiler pipeline up to execution.

Compiler path covered here:

```text
lexer tokens -> cfg.py grammar -> Gal_Parser.py LL(1) parser -> GALsemantic.py AST builder -> GALsemantic.py semantic validator -> icg.py TAC generator -> GALinterpreter.py execution
```

Important implementation note:

- `GALsemantic.py` is not only semantic analysis. In this codebase, it also defines AST node classes and contains the AST builder.
- `icg.py` currently generates intermediate code from the validated token stream, not from the AST.
- The GAL PDF says arrays start at index 1. The current interpreter uses Python-style index checks and access, so list/vine runtime indexing is 0-based. This is a mismatch to disclose.

---

## A. Backend/cfg.py

### 1. FILE PURPOSE

`cfg.py` stores the context-free grammar and computes the FIRST, FOLLOW, and PREDICT sets used by the LL(1) parser.

It fits between lexer and parser:

```text
tokens from lexer.py + grammar sets from cfg.py -> LL1Parser in Gal_Parser.py
```

`server.py` does not directly parse the grammar. It imports `cfg`, `first_sets`, and `predict_sets`, then passes them into `LL1Parser`.

### 2. IMPORTS / DEPENDENCIES

Code:

```python
import sys
from collections import defaultdict
```

Explanation:

- `sys` is used to reconfigure console encoding on Windows.
- `defaultdict` is used for grammar sets so each non-terminal can collect terminals without manually initializing every set.
- If `defaultdict` is removed, FIRST/FOLLOW computation would need manual dictionary initialization.

### 3. GLOBAL CONSTANTS / VARIABLES

Code:

```python
EPSILON = "lambda symbol in source"
cfg = {...}
first_sets = compute_first(cfg)
follow_sets = compute_follow(cfg, first_sets)
predict_sets = compute_predict(cfg, first_sets, follow_sets)
```

Explanation:

- `EPSILON` represents an empty production.
- `cfg` is the grammar dictionary.
- `first_sets` stores what terminals can begin each non-terminal.
- `follow_sets` stores what terminals can legally follow each non-terminal.
- `predict_sets` stores the final LL(1) decision sets.
- If `predict_sets` is wrong, the parser will choose the wrong production or report syntax errors incorrectly.

### 4. CLASSES AND FUNCTIONS

`compute_first(cfg)`

- Input: grammar dictionary.
- Output: FIRST set dictionary.
- Stage: parser preparation.
- Purpose: Know which terminals can start each grammar rule.

`compute_follow(cfg, first)`

- Input: grammar and FIRST sets.
- Output: FOLLOW set dictionary.
- Stage: parser preparation.
- Purpose: Know what can appear after a non-terminal, especially when epsilon is possible.

`compute_predict(cfg, first, follow)`

- Input: grammar, FIRST, FOLLOW.
- Output: PREDICT set dictionary.
- Stage: parser preparation.
- Purpose: Build the LL(1) production-selection data.

### 5. LINE-BY-LINE / BLOCK-BY-BLOCK EXPLANATION

Code:

```python
def compute_first(cfg):
    first = defaultdict(set)
    epsilon = EPSILON
```

Explanation:

- Defines the FIRST computation function.
- `first` maps each non-terminal to a set of starting terminals.
- `epsilon` stores the empty-production symbol locally for readability.

Code:

```python
for lhs, productions in cfg.items():
    for prod in productions:
        if not prod:
            continue
        if prod[0] == epsilon:
            first[lhs].add(epsilon)
        elif prod[0] not in cfg:
            first[lhs].add(prod[0])
```

Explanation:

- Loops through every grammar rule.
- `lhs` is the non-terminal on the left side.
- `prod` is one right-side production.
- Empty productions are skipped.
- If the production directly starts with epsilon, epsilon is added.
- If the first symbol is a terminal, that terminal is added.
- This is the first pass before recursive dependencies are resolved.

Code:

```python
changed = True
while changed:
    changed = False
```

Explanation:

- FIRST sets depend on one another, so one pass is not enough.
- The loop repeats until no FIRST set changes.
- This is a fixed-point algorithm.

Code:

```python
if symbol in cfg:
    first[lhs] |= (first[symbol] - {epsilon})
    if epsilon not in first[symbol]:
        break
else:
    if symbol != epsilon:
        first[lhs].add(symbol)
    break
```

Explanation:

- If a production symbol is a non-terminal, copy its FIRST set into the current rule.
- Epsilon is excluded first because epsilon does not consume input.
- If that non-terminal cannot become epsilon, stop scanning the production.
- If the symbol is terminal, add it and stop.

### 6. DEFENSE QUESTIONS

Q: Why do you need FIRST and FOLLOW sets?

A: They turn the grammar into parser decisions. FIRST tells what can start a rule, and FOLLOW helps decide when an empty production is allowed.

Q: Why use PREDICT sets?

A: PREDICT sets tell the LL(1) parser exactly which production to use based on the current non-terminal and one lookahead token.

### 7. MEMORIZED EXPLANATION

`cfg.py` is the grammar preparation file. It stores the GAL grammar and computes FIRST, FOLLOW, and PREDICT sets. The parser uses those sets to choose grammar productions during LL(1) parsing.

---

## B. Backend/Gal_Parser.py

### 1. FILE PURPOSE

`Gal_Parser.py` performs syntax analysis using LL(1) parsing. It also bridges syntax analysis to AST construction through `parse_and_build()`.

Pipeline position:

```text
tokens -> parser.parse() -> syntax result
tokens -> parser.parse_and_build() -> syntax result + AST + symbol table
```

### 2. IMPORTS / DEPENDENCIES

Code:

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple
```

Explanation:

- Future annotations simplify type hints.
- `dataclass` is used for normalized token views.
- `typing` makes parser inputs and outputs clearer.

Code:

```python
from GALsemantic import (
    build_ast as _build_ast,
    symbol_table as _builder_st,
    SemanticError as _SemanticError,
)
```

Explanation:

- `_build_ast` is called after syntax succeeds.
- `_builder_st` is read after AST construction to serialize variables/functions.
- `_SemanticError` catches AST-building errors.
- This is why AST construction is connected to the parser even though AST node classes live in `GALsemantic.py`.

### 3. GLOBAL CONSTANTS / VARIABLES

No major global parser object is created here. The parser instance is created in `server.py`.

### 4. CLASSES AND FUNCTIONS

`_TokView`

- Input: normalized token data.
- Purpose: Give the parser a consistent token format.

`_as_tok(token)`

- Input: token object or dictionary.
- Returns: `_TokView`.
- Purpose: Make parser reusable from lexer objects or JSON-like dictionaries.

`LL1Parser.__init__`

- Receives grammar, FIRST sets, PREDICT sets, start symbol, EOF marker, skip token types, aliases.
- Builds the parsing table.

`construct_parsing_table()`

- Receives no external input except parser state.
- Returns LL(1) table.
- Detects LL(1) conflicts.

`parse(tokens)`

- Input: token sequence.
- Returns: `(success, errors)`.
- Stage: syntax analysis.

`parse_and_build(tokens)`

- Input: token sequence.
- Returns: dictionary with `success`, `errors`, `ast`, and `symbol_table`.
- Stage: syntax + AST construction.

### 5. LINE-BY-LINE / BLOCK-BY-BLOCK EXPLANATION

Code:

```python
@dataclass(frozen=True)
class _TokView:
    type: str
    value: str
    line: int
    col: int = 0
```

Explanation:

- `_TokView` is a read-only token representation.
- The parser only needs token type, value, line, and column.
- `frozen=True` means parser logic cannot accidentally mutate token data.

Code:

```python
def _as_tok(token):
    if isinstance(token, Mapping):
        return _TokView(...)
    return _TokView(...)
```

Explanation:

- If the input token is a dictionary, fields are read with `.get()`.
- If it is a lexer `Token` object, fields are read with `getattr()`.
- This protects the parser from depending on only one token representation.

Code:

```python
class LL1Parser:
    def __init__(self, cfg, predict_sets, first_sets, *, start_symbol="<program>", end_marker="EOF", epsilon_symbols=(...), skip_token_types=None, token_type_alias=None):
        self.cfg = cfg
        self.predict_sets = predict_sets
        self.first_sets = first_sets
```

Explanation:

- Defines the parser class.
- Receives grammar and parsing sets from `cfg.py`.
- Stores start symbol and EOF marker.
- Allows skipped token types such as newline.
- Allows token aliases when lexer names and grammar names differ.

Code:

```python
self.skip_token_types = set(skip_token_types or {"\n"})
self.token_type_alias = token_type_alias or {
    'idf': 'id',
    'dbllit': 'dblit',
}
self.parsing_table = self.construct_parsing_table()
```

Explanation:

- Newline is skipped by default.
- Token aliases handle naming inconsistencies.
- The parsing table is built immediately when the parser is constructed.

Code:

```python
def construct_parsing_table(self):
    table = {}
    for non_terminal, productions in self.cfg.items():
        row = {}
```

Explanation:

- Creates the LL(1) table.
- Each non-terminal gets one row.

Code:

```python
key = (non_terminal, tuple(production))
terms = self.predict_sets.get(key, set())
for terminal in terms:
    if terminal in row and row[terminal] != production:
        raise ValueError(...)
    row[terminal] = production
```

Explanation:

- Looks up the PREDICT set for that production.
- For each lookahead terminal, stores which production to use.
- If two productions claim the same lookahead, that is an LL(1) conflict.

Code:

```python
def parse(self, tokens):
    toks = [_as_tok(t) for t in tokens]
    toks = [_TokView(self._normalize_token_type(t.type), t.value, t.line, t.col) for t in toks]
    toks = self._ensure_eof(toks)
```

Explanation:

- Converts tokens into parser view objects.
- Normalizes token type names.
- Ensures EOF exists.

Code:

```python
stack = [self.end_marker, self.start_symbol]
index = 0
```

Explanation:

- LL(1) parsing uses a stack.
- EOF is bottom marker.
- `<program>` is the first grammar symbol to expand.
- `index` points to the current input token.

Code:

```python
while stack:
    top = stack[-1]
    tok = current_token()
    token_type = tok.type
```

Explanation:

- Main parser loop.
- `top` is the grammar symbol currently being matched or expanded.
- `tok` is the current lookahead token.

Code:

```python
if token_type in self.skip_token_types and top != token_type:
    index += 1
    continue
```

Explanation:

- Skips newline tokens.
- This is the skipped token filtering requested in the defense prompt.
- It lets the lexer keep newlines while the parser ignores them.

Code:

```python
if top in self.parsing_table:
    row = self.parsing_table[top]
    if token_type in row:
        production = row[token_type]
```

Explanation:

- If `top` is a non-terminal, the parser uses the parsing table.
- The lookahead token chooses one production.

Code:

```python
stack.pop()
if production is not epsilon:
    stack.extend(reversed(production))
continue
```

Explanation:

- Removes the non-terminal.
- Pushes the right-hand side of the chosen production.
- Uses reverse order because stacks process last-in-first-out.

Code:

```python
expected = set(row.keys())
error_msg = self._generate_helpful_error(...)
return False, [error_msg]
```

Explanation:

- If no production matches, syntax fails.
- The parser generates a helpful message with expected tokens.

Code:

```python
if top == token_type:
    ...
```

Explanation:

- If the stack top is a terminal and equals the current token type, the parser consumes the token.
- This is a successful match.

Code:

```python
elif expecting_value_for_type is not None and token_type in {...}:
    type_value_map = {...}
```

Explanation:

- The parser includes extra validation for simple declaration assignments.
- This is partially semantic checking inside the parser for better immediate messages.
- Full semantic validation still happens later through `validate_ast()`.

Code:

```python
def parse_and_build(self, tokens):
    syntax_ok, syntax_errors = self.parse(tokens)
    if not syntax_ok:
        return {"success": False, "errors": syntax_errors, "ast": None, "symbol_table": {}}
```

Explanation:

- `parse_and_build()` starts by running syntax validation.
- If syntax fails, AST construction is skipped.
- This protects AST builder from invalid token order.

Code:

```python
filtered = [t for t in tokens if getattr(t, 'type', '') != '\n']
ast = _build_ast(filtered)
```

Explanation:

- Removes newline tokens before AST construction.
- Calls `build_ast()` from `GALsemantic.py`.

Code:

```python
st = {
    "variables": [...],
    "functions": {...},
}
```

Explanation:

- Converts the AST builder's symbol table into a JSON-friendly dictionary.
- Returned to server and frontend.

Code:

```python
except _SemanticError as e:
    return {"success": False, "errors": [str(e)], "ast": None, "symbol_table": {}, "error_stage": "semantic"}
```

Explanation:

- AST builder can detect semantic-like errors while building.
- The parser reports those as semantic-stage errors, not pure syntax errors.

### 6. DEFENSE QUESTIONS

Q: Why does the parser skip newline tokens?

A: The lexer emits newlines for display and accurate lines, but grammar matching should not depend on formatting. So the parser skips `\n`.

Q: Why does `parse_and_build()` parse first before building AST?

A: AST construction assumes valid structure. Parsing first prevents invalid syntax from creating a broken tree.

Q: Why are there semantic checks inside the parser?

A: Some checks are added for clearer early diagnostics, but the full semantic pass still runs after AST construction.

### 7. WALKTHROUGH EXAMPLE

For:

```gal
root() {
    seed age = 10;
    plant(age);
    reclaim;
}
```

The parser matches the grammar for `root`, parameter parentheses, function body, declaration, print statement, reclaim statement, closing brace, and EOF.

### 8. MEMORIZED EXPLANATION

`Gal_Parser.py` validates GAL syntax using LL(1) parsing. It uses the grammar and PREDICT sets from `cfg.py`, skips newline tokens, reports syntax errors, and only after successful parsing does it call the AST builder.

---

## C. Backend/GALsemantic.py: AST Nodes and AST Builder

### 1. FILE PURPOSE

`GALsemantic.py` has two responsibilities:

1. It defines AST node classes and builds the AST from validated tokens.
2. It validates the AST semantically.

This section covers the AST-building part first.

### 2. IMPORTS / DEPENDENCIES

Code:

```python
import re
```

Explanation:

- Used for pattern checks inside semantic parsing/validation.
- If removed, regex-based validation would fail where used.

### 3. GLOBAL CONSTANTS / VARIABLES

Important state:

- `symbol_table`: records variables, functions, scopes, and bundle types during AST construction.
- `context_stack`: helps know whether parser is inside loop/switch-like contexts.

Important warning:

- Because `symbol_table` is shared state, `build_ast()` resets it at the start of each compilation.

### 4. CLASSES AND FUNCTIONS

`SemanticError`

- Exception class for line-numbered semantic/syntax messages.

`ASTNode`

- Base class for all AST nodes.

AST subclasses include:

- `ProgramNode`
- `VariableDeclarationNode`
- `AssignmentNode`
- `BinaryOpNode`
- `FunctionDeclarationNode`
- `FunctionCallNode`
- `IfStatementNode`
- `ForLoopNode`
- `WhileLoopNode`
- `DoWhileLoopNode`
- `PrintNode`
- `ReturnNode`
- `SwitchNode`
- `ListNode`
- `ListAccessNode`
- `MemberAccessNode`
- `BundleDefinitionNode`

`SymbolTable`

- Tracks declarations and scopes during AST construction.

`build_ast(tokens)`

- Entry point for AST construction.

`parse_function(...)`

- Builds function declaration nodes for `root()` and `pollinate` functions.

`parse_statement(...)`

- Dispatches statements based on token type/value.

### 5. LINE-BY-LINE / BLOCK-BY-BLOCK EXPLANATION

Code:

```python
class ASTNode:
    def __init__(self, node_type, value=None, line=None):
        self.node_type = node_type
        self.value = value
        self.children = []
        self.parent = None
        self.line = line
```

Explanation:

- All AST nodes share this structure.
- `node_type` tells what kind of construct it is.
- `value` stores things like identifier names, literal values, or operators.
- `children` store nested syntax structure.
- `parent` gives reverse navigation.
- `line` supports error reporting.

Code:

```python
def add_child(self, child):
    child.parent = self
    self.children.append(child)
```

Explanation:

- Adds a child node.
- Also records the parent pointer.
- Parent pointers are used later, especially by interpreter input handling.

Code:

```python
class VariableDeclarationNode(ASTNode):
    def __init__(self, var_type, var_name, value=None, line=None):
        super().__init__("VariableDeclaration", line=line)
        self.add_child(ASTNode("Type", var_type, line=line))
        self.add_child(ASTNode("Identifier", var_name, line=line))
        if value:
            self.add_child(value)
```

Explanation:

- Represents declarations like `seed age = 10;`.
- Child 0 is type.
- Child 1 is identifier.
- Optional child 2 is initializer.
- The interpreter relies on this exact child order.

Code:

```python
class FunctionDeclarationNode(ASTNode):
    def __init__(self, return_type, name, params, line=None):
        super().__init__("FunctionDeclaration", name, line=line)
        self.add_child(ASTNode("ReturnType", return_type, line=line))
        self.add_child(params)
```

Explanation:

- Represents both `root()` and `pollinate` functions.
- Function name is stored in `value`.
- Return type and parameter list are children.
- The function body block is added later.

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
```

Explanation:

- Tracks declared names during AST construction.
- `variables` stores global variables.
- `functions` stores function declarations.
- `scopes` tracks local scopes.
- `current_func_name` tells whether we are inside a function.
- `function_variables` detects duplicate local variables.
- `bundle_types` stores struct-like definitions.

Code:

```python
def declare_variable(self, name, type_, value=None, is_list=False, is_fertile=False):
    scope = self.scopes[-1]
    current_func = self.current_func_name
```

Explanation:

- Declares a variable in the active scope.
- Uses the current function name to distinguish locals from globals.
- Stores whether the variable is an array/list or constant.

Code:

```python
if name in self.functions:
    return f"Semantic Error: Variable '{name}' already declared as a function."
```

Explanation:

- Prevents a variable from reusing a function name.
- This is a semantic rule because the name is lexically valid but invalid in context.

Code:

```python
def lookup_variable(self, name):
    for scope in reversed(self.scopes):
        if name in scope:
            return scope[name]
    if name in self.variables:
        return self.variables[name]
    return f"Semantic Error: Variable '{name}' used before declaration."
```

Explanation:

- Searches local scope first, then globals.
- Supports normal scoping behavior.
- Reports declaration-before-use errors.

Code:

```python
def build_ast(tokens):
    root = ProgramNode()
    symbol_table.variables = {}
    symbol_table.functions = {}
    symbol_table.scopes = [{}]
    symbol_table.function_variables = {}
    symbol_table.bundle_types = {}
    index = 0
```

Explanation:

- Creates the AST root.
- Resets old compiler state.
- Begins token scanning at index 0.
- Resetting matters because the server may compile many programs in one run.

Code:

```python
while index < len(tokens):
    token = tokens[index]
```

Explanation:

- Main AST-building loop.
- Reads top-level program constructs: global declarations, `pollinate`, `bundle`, and `root`.

Code:

```python
if tokens[index].value in {"seed", "tree", "vine", "leaf", "branch"}:
    id_type = token.value
    index += 1
    if tokens[index].type != "id":
        raise SemanticError(...)
    id_name = tokens[index].value
    index += 1
    node, index = parse_variable(tokens, index, id_name, id_type)
```

Explanation:

- Handles top-level variable declarations.
- Reads data type then identifier.
- Delegates initializer/list handling to `parse_variable()`.

Code:

```python
elif tokens[index].value in {"pollinate"}:
    index += 1
    if tokens[index].value in {"seed", "tree", "vine", "leaf", "branch", "empty"}:
        id_type = tokens[index].value
        index += 1
        id_name = tokens[index].value
        index += 1
        node, index = parse_function(tokens, index, id_name, id_type)
```

Explanation:

- Handles user-defined function declarations.
- `pollinate` must be followed by return type.
- Then function name is read.
- `parse_function()` handles parameters and body.

Code:

```python
elif token.value in {"root"}:
    func_name = token.value
    func_type = "empty"
    node, index = parse_function(tokens, index, func_name, func_type)
```

Explanation:

- Handles the main entry point.
- `root()` is treated as an empty-return function.
- Later, the interpreter explicitly calls `root()`.

Code:

```python
elif token.value == "bundle":
    bundle_name = tokens[index + 1].value
    members = {}
```

Explanation:

- Handles bundle/struct definitions.
- Collects member fields and stores the type definition.

Code:

```python
def parse_function(tokens, index, func_name, func_type):
    symbol_table.current_func_name = func_name
```

Explanation:

- Begins function parsing.
- Sets current function context so local declarations go into function scope.

Code:

```python
if func_name in {"root"}:
    symbol_table.enter_scope()
    index += 1
    if tokens[index].type == "(":
        index += 1
        if tokens[index].type != ")":
            raise SemanticError(...)
```

Explanation:

- Special handling for `root()`.
- Enters a local scope for root body.
- Requires empty parameter list.
- Rejects `root(seed x)` because root should not receive parameters.

Code:

```python
while tokens[index].type != ")":
    if tokens[index].value in {"seed", "tree", "vine", "leaf", "branch", "empty"}:
        param_type = tokens[index].value
        ...
        params_node.add_child(param_node)
        symbol_table.declare_variable(param_name, param_type, is_list=is_list)
```

Explanation:

- Parses pollinate function parameters.
- Builds parameter AST nodes.
- Declares each parameter in the function's local scope.

Code:

```python
while tokens[index].type != "}":
    stmt, index = parse_statement(tokens, index, func_type)
    if stmt:
        block_node.add_child(stmt)
        if _contains_return(stmt):
            has_any_return = True
```

Explanation:

- Parses statements inside the function body.
- Adds them to a block node.
- Tracks whether `reclaim` appears.

Code:

```python
if (func_type != "empty" and not all_paths) and func_name not in {"root"}:
    raise SemanticError(...)
```

Explanation:

- Non-empty functions must return a value on all paths.
- This enforces `reclaim value;` for functions like `pollinate seed add(...)`.

Code:

```python
if not has_any_return:
    if func_name == "root":
        raise SemanticError("root() must end with 'reclaim;'", line)
```

Explanation:

- Enforces required termination in `root()`.
- This matches the GAL specification.

Code:

```python
def parse_statement(tokens, index, func_type=None):
    token = tokens[index]
    if token.type == ";":
        return None, index + 1
```

Explanation:

- Dispatches individual statements.
- Ignores stray semicolons safely.

Code:

```python
if token.value in {"seed", "tree", "vine", "leaf", "branch"}:
    var_type = token.value
    var_name = tokens[index + 1].value
    node, index = parse_variable(tokens, index, var_name, var_type)
```

Explanation:

- Handles local variable declarations.
- Produces a `VariableDeclarationNode` or declaration list node.

Code:

```python
elif token.type == "id" and tokens[index + 1].type == "(":
    func_name = token.value
    error = symbol_table.lookup_function(func_name)
    func_call_node, index = parse_function_call(...)
```

Explanation:

- Detects function calls.
- Checks that the function exists.
- Builds a function call AST node.

### 6. DEFENSE QUESTIONS

Q: Why does `GALsemantic.py` build the AST?

A: In this implementation, AST node definitions and AST building are grouped with semantic logic. The parser calls it only after syntax succeeds.

Q: Why reset the symbol table in `build_ast()`?

A: The server can compile multiple programs. Resetting prevents old variables/functions from leaking into a new compilation.

Q: Why store parent links in AST nodes?

A: Parent links help when a node needs context. For example, the interpreter checks where an input node appears to determine the target variable and type.

### 7. WALKTHROUGH EXAMPLE

For:

```gal
seed age = 10;
plant(age);
reclaim;
```

The AST block contains:

```text
VariableDeclaration(Type seed, Identifier age, Value 10)
PrintStatement(Value age)
Return
```

### 8. MEMORIZED EXPLANATION

`GALsemantic.py` defines the AST structure and builds the tree from validated tokens. It also uses a symbol table to record declarations, scopes, functions, and bundles while building that tree.

---

## D. Backend/GALsemantic.py: Semantic Analyzer

### 1. FILE PURPOSE

After the AST is built, the semantic analyzer walks the tree and validates meaning. It checks context and structure that grammar alone cannot fully guarantee.

Examples of semantic concerns:

- Is `prune` inside a loop or switch?
- Is `skip` inside a loop?
- Is a declaration structurally complete?
- Does a function have valid return structure?
- Are blocks and expressions well formed?

### 2. CLASSES AND FUNCTIONS

`ASTValidator`

- Input: AST and serialized symbol table.
- Output: dictionary containing success, errors, warnings, symbol table, and AST.
- Stage: semantic analysis.

`validate_ast(ast, symbol_table_data)`

- Public API used by `server.py`.
- Creates a validator and returns validation result.

### 3. LINE-BY-LINE / BLOCK-BY-BLOCK EXPLANATION

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
```

Explanation:

- `errors` stores semantic errors.
- `warnings` stores non-fatal notices.
- `_in_loop` tracks loop nesting.
- `_in_switch` tracks harvest/switch nesting.
- `_in_function` tracks function context.
- `_current_func_type` tracks expected return type while walking a function.

Code:

```python
def validate(self, ast, symbol_table_data):
    self._walk(ast)
    return {
        "success": len(self.errors) == 0,
        "errors": self.errors,
        "warnings": self.warnings,
        "symbol_table": symbol_table_data,
        "ast": ast,
    }
```

Explanation:

- Starts validation by walking the AST root.
- Success is true only when no errors were collected.
- Returns the AST again so later stages can use the validated tree.

Code:

```python
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

Explanation:

- This is recursive tree walking.
- It looks for a method named after the node type, such as `_check_FunctionDeclaration`.
- If a specific handler exists, it uses it.
- Otherwise, it walks all children by default.

Code:

```python
def _check_FunctionDeclaration(self, node):
    if not node.value:
        self.errors.append("Function declaration missing name")
    prev_in_func = self._in_function
    prev_func_type = self._current_func_type
    self._in_function = True
    if node.children:
        self._current_func_type = node.children[0].value
```

Explanation:

- Verifies the function has a name.
- Saves previous context before entering this function.
- Sets current function information while walking the body.

Code:

```python
for child in node.children:
    self._walk(child)
self._in_function = prev_in_func
self._current_func_type = prev_func_type
```

Explanation:

- Walks return type, parameters, and body.
- Restores previous context afterward.
- This prevents one function's context from leaking into another.

Code:

```python
def _check_ForLoop(self, node):
    self._in_loop += 1
    for child in node.children:
        self._walk(child)
    self._in_loop -= 1
```

Explanation:

- Marks that validation is inside a loop.
- Validates all loop children.
- Decrements loop depth afterward.

Code:

```python
def _check_Switch(self, node):
    self._in_switch += 1
    for child in node.children:
        self._walk(child)
    self._in_switch -= 1
```

Explanation:

- Marks that validation is inside a `harvest` switch.
- Needed because `prune` is valid inside a switch.

Code:

```python
def _check_Break(self, node):
    if self._in_loop == 0 and self._in_switch == 0:
        self.errors.append("'prune' used outside a loop or switch")
```

Explanation:

- `prune` is only valid in loops or harvest/switch blocks.
- If there is no loop or switch context, it is a semantic error.

Code:

```python
def _check_Continue(self, node):
    if self._in_loop == 0:
        self.errors.append("'skip' used outside a loop")
```

Explanation:

- `skip` only makes sense inside loops.
- Using it elsewhere is syntactically possible but semantically wrong.

Code:

```python
def validate_ast(ast, symbol_table_data):
    validator = ASTValidator()
    return validator.validate(ast, symbol_table_data)
```

Explanation:

- This is the public function called by `server.py`.
- It creates a fresh validator for every compilation.
- It returns a dictionary that the server can send as JSON.

### 4. DEFENSE QUESTIONS

Q: Why validate semantics after AST construction?

A: The AST gives structured meaning. It is easier to validate loops, functions, returns, and nested statements after syntax is organized as a tree.

Q: Why use counters like `_in_loop` instead of booleans?

A: Loops can be nested. A counter correctly handles multiple levels of nesting.

Q: Why collect errors instead of immediately throwing?

A: The validator can gather semantic issues in a structured result and return them to the frontend.

### 5. MEMORIZED EXPLANATION

`validate_ast()` is the semantic validation phase. It walks the AST and checks context-sensitive rules, such as whether `prune` and `skip` are used in valid locations and whether AST structures are complete.

---

## E. Backend/icg.py

### 1. FILE PURPOSE

`icg.py` generates intermediate code, specifically three-address code or TAC. This is a lower-level representation of the program.

Pipeline position:

```text
validated token stream -> generate_icg() -> TAC list + TAC text
```

Important implementation detail:

- The ICG module reads tokens directly.
- The server validates lexer, parser, AST, and semantic stages before calling ICG.

### 2. IMPORTS / DEPENDENCIES

Code:

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
```

Explanation:

- Future annotations support cleaner type hints.
- `dataclass` is used for token views and TAC instructions.
- `typing` documents the structures passed around.
- `field` appears possibly unused in this file; do not remove during defense unless verified.

### 3. GLOBAL CONSTANTS / VARIABLES

Code:

```python
GAL_TYPE_MAP = {
    "seed": "int",
    "tree": "float",
    "leaf": "char",
    "branch": "bool",
    "vine": "string",
    "empty": "void",
}
DATA_TYPE_TOKENS = set(GAL_TYPE_MAP.keys())
ASSIGN_OPS = {"=", "+=", "-=", "*=", "/=", "%="}
```

Explanation:

- `GAL_TYPE_MAP` converts GAL type names into conventional intermediate-code type names.
- `DATA_TYPE_TOKENS` lets the generator quickly ask whether a token is a type.
- `ASSIGN_OPS` lists assignment operators that ICG can translate.

### 4. CLASSES AND FUNCTIONS

`_Tok`

- Normalized token view for ICG.

`_as_tok(raw)`

- Converts lexer tokens or dictionaries into `_Tok`.

`TACInstruction`

- Represents one intermediate instruction with `op`, `arg1`, `arg2`, and `result`.

`ICGenerator`

- Main class that reads tokens and emits TAC.

`generate_icg(tokens)`

- Public API used by `server.py`.

### 5. LINE-BY-LINE / BLOCK-BY-BLOCK EXPLANATION

Code:

```python
@dataclass(frozen=True)
class _Tok:
    type: str
    value: str
    line: int
    col: int = 0
```

Explanation:

- Gives ICG a stable token format.
- Prevents ICG from depending on the exact lexer `Token` class.

Code:

```python
@dataclass
class TACInstruction:
    op: str
    arg1: Optional[str] = None
    arg2: Optional[str] = None
    result: Optional[str] = None
```

Explanation:

- Stores one TAC instruction.
- `op` is the operation.
- `arg1` and `arg2` are operands.
- `result` is destination or label depending on the instruction.

Code:

```python
def __str__(self):
    if self.op == "LABEL":
        return f"{self.result}:"
    if self.op == "GOTO":
        return f"goto {self.result}"
    if self.op == "PRINT":
        return f"print {self.arg1}"
```

Explanation:

- Converts TAC objects into human-readable TAC text.
- This is what `/api/icg` can display in the frontend.

Code:

```python
class ICGenerator:
    def __init__(self, tokens):
        self.tokens = self._prepare(tokens)
        self.pos = 0
        self.code = []
        self.errors = []
        self._temp_counter = 0
        self._label_counter = 0
```

Explanation:

- Prepares tokens by normalizing and skipping newlines.
- `pos` tracks current token index.
- `code` stores generated instructions.
- `errors` stores ICG errors.
- Counters generate temporary names and labels.

Code:

```python
def _prepare(self, raw_tokens):
    toks = []
    for t in raw_tokens:
        tv = _as_tok(t)
        if tv.type == "\n":
            continue
        toks.append(tv)
```

Explanation:

- Filters newline tokens, similar to parser and AST builder.
- ICG does not need newline tokens to generate code.

Code:

```python
if not toks or toks[-1].type != "EOF":
    toks.append(_Tok("EOF", "EOF", last_line))
```

Explanation:

- Ensures the token stream has EOF.
- EOF prevents reading beyond the input.

Code:

```python
def _emit(self, op, arg1=None, arg2=None, result=None):
    self.code.append(TACInstruction(op, arg1, arg2, result))
```

Explanation:

- Central helper for creating TAC.
- Every declaration, expression, loop, and statement uses this to append instructions.

Code:

```python
def _new_temp(self):
    name = f"t{self._temp_counter}"
    self._temp_counter += 1
    return name
```

Explanation:

- Generates temporary variables like `t0`, `t1`.
- Used for intermediate expression results.

Code:

```python
def _new_label(self):
    name = f"L{self._label_counter}"
    self._label_counter += 1
    return name
```

Explanation:

- Generates labels like `L0`, `L1`.
- Used for jumps in loops and conditionals.

Code:

```python
def generate(self):
    try:
        self._program()
    except Exception as exc:
        self.errors.append(f"ICG internal error: {exc}")
    return self.code, self.errors
```

Explanation:

- Starts generating TAC from the whole program.
- Catches unexpected generator failures.
- Returns generated code and errors.

Code:

```python
def _program(self):
    self._global_declaration()
    self._function_definition()
    self._expect("root")
    self._expect("(")
    self._expect(")")
    self._expect("{")
    self._emit("FUNC", "root")
```

Explanation:

- Follows GAL program structure.
- Handles globals and pollinate functions before `root`.
- Emits a TAC function start for root.

Code:

```python
self._declaration()
self._statement()
```

Explanation:

- Emits declarations first.
- Emits executable statements next.
- Mirrors the GAL rule that local declarations come before statements.

Code:

```python
if self._peek().type == "reclaim":
    self._advance()
    if self._peek().type != ";":
        val = self._expression()
        self._emit("RETURN", val)
    else:
        self._emit("RETURN")
```

Explanation:

- Converts `reclaim;` or `reclaim expression;` into TAC return.
- For `root()`, return usually has no value.

Code:

```python
def _simple_stmt(self):
    if tok.type == "id":
        self._id_stmt()
    elif tok.type in ("water", "plant"):
        self._io_stmt()
    elif tok.type == "spring":
        self._conditional_stmt()
    elif tok.type in ("grow", "cultivate", "tend"):
        self._loop_stmt()
```

Explanation:

- Dispatches based on statement starter token.
- Each GAL construct has its own TAC generation path.

Code:

```python
if op_tok.type == "=":
    self._emit("=", rhs, None, lhs)
else:
    base_op = op_tok.type[0]
    tmp = self._new_temp()
    self._emit(base_op, lhs, rhs, tmp)
    self._emit("=", tmp, None, lhs)
```

Explanation:

- Assignment becomes one TAC instruction.
- Compound assignment becomes operation plus assignment.
- Example: `x += y` becomes `t0 = x + y`, then `x = t0`.

Code:

```python
def _while_loop(self):
    start_label = self._new_label()
    end_label = self._new_label()
    self._emit("LABEL", None, None, start_label)
    cond = self._expression()
    self._emit("IFFALSE", cond, None, end_label)
    self._statement()
    self._emit("GOTO", None, None, start_label)
    self._emit("LABEL", None, None, end_label)
```

Explanation:

- `grow` loop is translated into labels and jumps.
- If condition is false, jump to end.
- After body, jump back to start.

Code:

```python
def _expression(self):
    return self._logic_or()
```

Explanation:

- Expression generation starts at the lowest precedence level.
- Deeper functions handle logical, relational, arithmetic, and factor parsing.

Code:

```python
def generate_icg(tokens):
    gen = ICGenerator(tokens)
    code, errors = gen.generate()
    tac_dicts = [instr.to_dict() for instr in code]
    tac_text = "\n".join(str(instr) for instr in code)
    return {...}
```

Explanation:

- Public API called by `server.py`.
- Creates a generator, runs it, converts instructions to JSON-friendly dictionaries and readable text.

### 6. DEFENSE QUESTIONS

Q: Why have ICG if the interpreter can run the AST?

A: ICG shows an intermediate compiler representation. It can be used for future optimization or target-code generation, while the interpreter is for immediate execution.

Q: Why use temporary variables?

A: TAC breaks complex expressions into simple operations with at most two operands.

Q: Why use labels?

A: Loops and conditionals need jump targets. Labels represent those targets.

### 7. WALKTHROUGH EXAMPLE

For the sample program, ICG output is:

```text
func root:
declare age : int
age = 10
print age
return
endfunc
```

### 8. MEMORIZED EXPLANATION

`icg.py` converts validated GAL tokens into three-address code. It emits declarations, assignments, labels, jumps, input/output, function calls, and returns. It is separate from execution because it represents the compiler's intermediate form.

---

## F. Backend/GALinterpreter.py

### 1. FILE PURPOSE

`GALinterpreter.py` is the execution engine. It walks the validated AST and performs the actual program behavior.

Pipeline position:

```text
validated AST -> Interpreter.interpret(ast) -> runtime output / input / errors
```

### 2. IMPORTS / DEPENDENCIES

Code:

```python
from GALsemantic import (ProgramNode, VariableDeclarationNode, AssignmentNode, ...)
import threading
import sys
sys.setrecursionlimit(10000)
```

Explanation:

- Imports AST node classes so the interpreter can identify node types.
- `threading` is fallback support for input waiting.
- `sys.setrecursionlimit(10000)` allows deeper recursive interpretation/function calls.

Code:

```python
try:
    import eventlet.event as _ev
    _USE_EVENTLET = True
except ImportError:
    _USE_EVENTLET = False
```

Explanation:

- Uses eventlet events when available.
- Eventlet lets `water()` wait without blocking the whole Socket.IO server.
- Falls back to threading events if eventlet is unavailable.

### 3. GLOBAL CONSTANTS / VARIABLES

There are no major global compiler constants here. The runtime state is inside each `Interpreter` object:

- variables
- functions
- scopes
- bundle types
- input events
- output socket
- loop flags

### 4. CLASSES AND FUNCTIONS

`ReturnValue`

- Internal exception used to implement `reclaim`.
- Carries return value out of a function body.

`_CancelledError`

- Raised when a previous interpreter is cancelled by a new run.

`InterpreterError`

- Runtime error with line-numbered message.

`Interpreter`

- Main runtime class.
- Executes AST nodes.
- Stores variables, functions, scopes, bundle types, loop flags, and input state.

### 5. LINE-BY-LINE / BLOCK-BY-BLOCK EXPLANATION

Code:

```python
class Interpreter:
    def __init__(self, socketio=None):
        self.output = []
        self.loop_stack = []
        self.break_flag = False
        self.continue_flag = False
        self.input_required = False
        self.socketio = socketio
```

Explanation:

- Creates one runtime environment.
- `output` stores printed output in compatibility paths.
- `loop_stack`, `break_flag`, and `continue_flag` implement `prune` and `skip`.
- `input_required` marks whether `water()` is waiting.
- `socketio` receives output and input events.

Code:

```python
self.input_events = {}
self.input_values = {}
self.variables = {}
self.global_variables = {}
self.functions = {}
self.scopes = [{}]
self.current_func_name = None
self.function_variables = {}
self.bundle_types = {}
```

Explanation:

- `input_events` stores waiting input requests.
- `input_values` stores input that arrived early.
- `variables` and `global_variables` store runtime values.
- `functions` stores function declarations.
- `scopes` models local scope stack.
- `bundle_types` stores struct-like type definitions.

Code:

```python
def declare_variable(self, name, type_, value=None, is_list=False, is_fertile=False):
    scope = self.scopes[-1]
    if name not in self.scopes[-1]:
        scope[name] = {
            "type": type_,
            "value": value,
            "is_list": is_list,
            "is_fertile": is_fertile
        }
```

Explanation:

- Stores a variable in the current runtime scope.
- Keeps type, value, array/list flag, and constant flag.

Code:

```python
def lookup_variable(self, name):
    for scope in reversed(self.scopes):
        if name in scope:
            return scope[name]
    if name in self.variables:
        return self.variables[name]
    return f"Semantic Error: Variable '{name}' used before declaration."
```

Explanation:

- Searches from innermost scope outward.
- Falls back to global variables.
- Returns an error string if variable does not exist.

Code:

```python
def interpret(self, node):
    if isinstance(node, ProgramNode):
        return self.eval_program(node)
    elif isinstance(node, VariableDeclarationNode):
        return self.eval_variable_declaration(node)
    elif isinstance(node, AssignmentNode):
        return self.eval_assignment(node)
```

Explanation:

- This is the main AST dispatcher.
- Each node type is routed to the correct evaluator.
- This is how the interpreter walks and executes the AST.

Code:

```python
elif node.node_type == "Identifier":
    var_info = self.lookup_variable(node.value)
    if isinstance(var_info, str):
        raise InterpreterError(var_info, node.line)
    return var_info["value"]
```

Explanation:

- Identifier evaluation means reading the current runtime value.
- If the variable is missing, execution stops with an error.

Code:

```python
def eval_program(self, node):
    for child in node.children:
        self.interpret(child)
    main_call = FunctionCallNode("root", [], node.line)
    return self.interpret(main_call)
```

Explanation:

- First registers global declarations, bundles, and functions.
- Then creates a call to `root()`.
- This implements GAL's entry point rule.

Code:

```python
def eval_variable_declaration(self, node):
    var_type = node.children[0].value
    var_name = node.children[1].value
    value_node = node.children[2] if len(node.children) > 2 else None
```

Explanation:

- Reads type, name, and optional initializer from AST children.
- The interpreter relies on the AST layout created by `VariableDeclarationNode`.

Code:

```python
default_values = {
    "seed": 0,
    "tree": 0.0,
    "leaf": '',
    "vine": "",
    "branch": False,
}
```

Explanation:

- Provides default values for declarations without initializers.
- Example: `seed x;` becomes `x = 0` at runtime.

Code:

```python
if value_node:
    value = self.interpret(value_node)
    if var_type == "seed" and isinstance(value, float):
        value = int(value)
else:
    value = default_values.get(var_type, None)
```

Explanation:

- If there is an initializer, evaluate it.
- If the variable is `seed` and value is float, convert to int.
- If there is no initializer, use default value.

Code:

```python
self.declare_variable(var_name, var_type, value, is_list=is_list)
```

Explanation:

- Stores the variable in the current runtime scope.
- After this line, later statements can access the variable.

Code:

```python
def eval_assignment(self, node):
    target_node = node.children[0]
    value_node = node.children[1]
    value = self.interpret(value_node)
```

Explanation:

- Evaluates the right-hand side first.
- Then assigns it to the target.
- The target can be a normal variable, list element, or bundle member.

Code:

```python
if target_node.node_type == "ListAccess":
    indices = []
    current = target_node
    while current.node_type == "ListAccess":
        idx = self.interpret(current.children[1].children[0])
        if not isinstance(idx, int):
            raise InterpreterError(...)
        indices.append(idx)
```

Explanation:

- Handles assignment to array/list elements.
- Evaluates each index expression.
- Requires indexes to be integers.

Code:

```python
if final_idx < 0 or final_idx >= len(target):
    raise InterpreterError("Index out of bounds", node.line)
target[final_idx] = value
```

Explanation:

- Performs runtime bounds check.
- Writes the new value.
- Current implementation uses 0-based indexing. This differs from the GAL PDF's 1-based rule.

Code:

```python
def eval_binary_op(self, node):
    left = self.interpret(node.children[0])
    right = self.interpret(node.children[1])
    operator = node.value
```

Explanation:

- Evaluates both operands recursively.
- Reads the operator from the AST node.

Code:

```python
if operator == '`':
    result = str(left) + str(right)
    return result
```

Explanation:

- Implements GAL string concatenation using backtick.
- Converts both operands to string.

Code:

```python
elif operator == '/':
    if right == 0:
        raise InterpreterError("Runtime Error: Division by zero is undefined", node.line)
    return left / right
```

Explanation:

- Executes division.
- Checks division by zero at runtime because actual values are known only during execution.

Code:

```python
def eval_block(self, block_node):
    for statement in block_node.children:
        self.interpret(statement)
        if self.break_triggered():
            return
        if self.continue_flag:
            return
```

Explanation:

- Executes statements in source order.
- Stops block execution if `prune` or `skip` changes control flow.

Code:

```python
def plant(self, value):
    self.socketio.emit('output', {'output': str(value)})
```

Explanation:

- Implements output.
- The interpreter emits to whatever socket-like object it was given.
- In Socket.IO mode, output goes live to the frontend.
- In REST mode, `OutputCollector` catches it.

Code:

```python
def eval_return(self, node):
    value = self.interpret(node.children[0]) if node.children else None
    raise ReturnValue(value)
```

Explanation:

- Implements `reclaim`.
- Raises `ReturnValue` to immediately exit the current function.
- Carries return value if present.

Code:

```python
def eval_function_call(self, node):
    function_name = node.value
    args = [self.interpret(arg.children[0]) for arg in node.children]
    func_info = self.lookup_function(function_name)
```

Explanation:

- Evaluates function call arguments.
- Looks up the function declaration.

Code:

```python
self.enter_scope()
try:
    for i, param in enumerate(expected_params):
        self.declare_variable(param_name, param_type, arg_value, is_list=is_list)
    self.eval_block(function_node.children[2])
except ReturnValue as ret:
    return ret.value
finally:
    self.exit_scope()
```

Explanation:

- Function call creates a new local scope.
- Parameters become local variables.
- Function body executes.
- `ReturnValue` captures `reclaim`.
- Scope is cleaned up after the call.

Code:

```python
def provide_input(self, var_name, input_value):
    evt = self.input_events.get(var_name)
    if evt is None:
        self.input_values[var_name] = input_value
        return
```

Explanation:

- Receives input from `server.py`.
- If interpreter is not waiting yet, stores the value.
- Prevents lost input.

Code:

```python
def wait_for_input(self, var_name):
    if var_name in self.input_values:
        return self.input_values.pop(var_name)
```

Explanation:

- If input already arrived, returns it immediately.
- Otherwise waits for eventlet/threading event.

Code:

```python
def eval_input(self, node):
    parent_node = node.parent
    if isinstance(parent_node, VariableDeclarationNode):
        var_name = parent_node.children[1].value
        var_type = parent_node.children[0].value
```

Explanation:

- Figures out where `water()` is being used.
- If it is inside a declaration, the target variable and type come from the parent declaration.

Code:

```python
self.emit_input_request(var_name, prompt)
input_value = self.wait_for_input(var_name)
```

Explanation:

- Tells the frontend input is needed.
- Waits until the user responds.

Code:

```python
if var_type == "seed":
    if input_value.startswith('-'):
        raise InterpreterError("GAL uses '~' for negative numbers", node.line)
    if input_value.startswith('~'):
        input_value = '-' + input_value[1:]
    input_value = int(float(input_value))
```

Explanation:

- Converts input string to integer.
- Enforces GAL negative syntax using `~` instead of `-`.
- Raises runtime error if conversion fails.

### 6. DEFENSE QUESTIONS

Q: Why execute the AST instead of tokens?

A: Tokens are flat. The AST already shows program structure, so execution can naturally follow blocks, expressions, functions, and control flow.

Q: Why does `reclaim` use an exception?

A: A return must immediately exit the current function, even from nested blocks. `ReturnValue` carries the return value out cleanly.

Q: How does `plant()` output reach the frontend?

A: The interpreter calls `self.socketio.emit('output', ...)`. In live mode this is Socket.IO; in REST mode it is an `OutputCollector`.

Q: How does `water()` work?

A: The interpreter emits an input request, waits on an event, and `server.py` later calls `provide_input()` when the frontend sends user input.

Q: What array indexing issue should you mention?

A: The GAL document says arrays are 1-based, but the interpreter currently checks `index < 0` and accesses `list_value[index]`, so runtime behavior is 0-based.

### 7. WALKTHROUGH EXAMPLE

For:

```gal
root() {
    seed age = 10;
    plant(age);
    reclaim;
}
```

Execution steps:

1. `eval_program()` registers declarations and functions.
2. It creates a `FunctionCallNode("root", [])`.
3. `eval_function_call()` enters a scope for root.
4. `eval_variable_declaration()` stores `age` as a `seed` with value `10`.
5. `eval_print()` reads `age` and emits `10`.
6. `eval_return()` raises `ReturnValue(None)`.
7. The function call catches return and exits.
8. `server.py` returns output to frontend.

### 8. MEMORIZED EXPLANATION

`GALinterpreter.py` is the runtime engine. It walks the AST, stores variables in scopes, registers functions, evaluates expressions, executes loops and conditionals, handles `plant()` output, handles `water()` input, and uses `ReturnValue` to implement `reclaim`.

---

# Final Full-Pipeline Defense Explanation

`server.py` receives source code from the frontend. It sends the raw text to `lexer.py`, which converts characters into tokens and reports lexical errors. Those tokens go to `Gal_Parser.py`, which uses the grammar and PREDICT sets from `cfg.py` to validate syntax with LL(1) parsing. If syntax succeeds, `parse_and_build()` calls the AST builder in `GALsemantic.py`. The AST builder creates structured nodes and a symbol table. Then `validate_ast()` walks the AST for semantic checks. If the user requests ICG, `icg.py` generates three-address code. If the user runs the program, `GALinterpreter.py` walks the AST, calls `root()`, executes declarations, statements, expressions, functions, loops, `plant()`, `water()`, and `reclaim`, then sends the output back through the server.

# Common Panel Questions For The Whole System

Q: Why did you separate the compiler into files?

A: Each file represents a compiler responsibility. Lexer handles characters, parser handles grammar, AST/semantic handles meaning, ICG handles intermediate representation, and interpreter handles execution.

Q: What happens if lexical analysis fails?

A: The server stops immediately and returns lexical errors. Parser does not run because invalid tokens would make syntax analysis unreliable.

Q: What happens if syntax analysis fails?

A: AST construction does not happen. The server returns syntax errors from the parser.

Q: What happens if semantic analysis fails?

A: ICG and interpreter are skipped. The server returns semantic errors.

Q: What happens if runtime execution fails?

A: The interpreter raises `InterpreterError`; `server.py` catches it and sends a runtime error to the frontend.

Q: Why is `root()` called by the interpreter instead of just executing top to bottom?

A: Top-level declarations and function definitions must be registered first. Actual program execution begins at `root()`, as required by the GAL specification.

Q: What is one known implementation/spec mismatch?

A: The GAL PDF specifies 1-based arrays, but the current interpreter uses 0-based indexing for lists/vines. That should be acknowledged honestly during defense.
