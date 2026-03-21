"""
NLP-based fallback responder for the GAL AI chat.

Three-layer hybrid architecture:
  Layer 1 — Rule Engine: regex matches compiler error messages → structured explanations
  Layer 2 — Retriever: sentence-transformers (all-mpnet-base-v2) semantic search over 50+ KB topics
  Layer 3 — Default: help menu when nothing matches

Plus: synonym expansion, greeting detection, follow-up context, multi-topic blending.
Uses the #1 ranked sentence embedding model for best semantic matching accuracy.
All heavy imports are deferred so the server binds its port immediately.
"""

import re as _re

# Minimum cosine similarity score to return a topic match (else use default)
_THRESHOLD = 0.35


# ═══════════════════════════════════════════════════════════════════════
# STRUCTURED RESPONSE BUILDER
# ═══════════════════════════════════════════════════════════════════════

def _structured_error(stage, cause, rule="", fix="", explanation=""):
    """Build a structured error explanation from labeled slots."""
    parts = [f"**Stage:** {stage}", f"**Cause:** {cause}"]
    if rule:
        parts.append(f"**Rule:** {rule}")
    if fix:
        parts.append(f"**Fix:**\n```\n{fix}\n```")
    if explanation:
        parts.append(explanation)
    return "\n\n".join(parts)


def _lexer_err(cause, rule, fix, explanation=""):
    return _structured_error("Lexical Analysis (Lexer)", cause, rule, fix, explanation)

def _parser_err(cause, rule, fix, explanation=""):
    return _structured_error("Syntax Analysis (Parser)", cause, rule, fix, explanation)

def _semantic_err(cause, rule, fix, explanation=""):
    return _structured_error("Semantic Analysis", cause, rule, fix, explanation)

def _runtime_err(cause, rule, fix, explanation=""):
    return _structured_error("Runtime (Interpreter)", cause, rule, fix, explanation)


# ═══════════════════════════════════════════════════════════════════════
# LAYER 1: RULE ENGINE — regex-based compiler error pattern matching
# ═══════════════════════════════════════════════════════════════════════
# Each entry: (compiled_regex, response_string_or_callable)
# If callable, it receives the re.Match object and returns a string.

_ERROR_PATTERNS = [
    # ── Lexer Errors ──────────────────────────────────────────────

    (_re.compile(r"Identifier exceeds maximum length of 15 characters", _re.I),
     _lexer_err(
         "An identifier (variable or function name) exceeded 15 characters.",
         "Identifiers must be at most 15 characters long.",
         "// BAD:  seed thisIsWayTooLong = 5;\n// GOOD: seed shortName = 5;",
     )),

    (_re.compile(r"Integer exceeds maximum of 8 digits", _re.I),
     _lexer_err(
         "An integer literal has more than 8 digits.",
         "Integer literals are limited to 8 digits.",
         "// BAD:  seed x = 123456789;\n// GOOD: seed x = 12345678;",
     )),

    (_re.compile(r"Fractional part exceeds maximum of 8 digits", _re.I),
     _lexer_err(
         "A float literal's decimal part has more than 8 digits.",
         "Fractional portions are limited to 8 digits.",
         "// BAD:  tree x = 3.123456789;\n// GOOD: tree x = 3.12345678;",
     )),

    (_re.compile(r"Missing closing ['\"].*string literal", _re.I),
     _lexer_err(
         "A string literal is missing its closing double quote.",
         "All strings must be enclosed in double quotes.",
         '// BAD:  vine s = "hello;\n// GOOD: vine s = "hello";',
     )),

    (_re.compile(r"Missing closing.*character literal", _re.I),
     _lexer_err(
         "A character literal is missing its closing single quote.",
         "Character literals use single quotes.",
         "// BAD:  leaf c = 'A;\n// GOOD: leaf c = 'A';",
     )),

    (_re.compile(r"Character literal must contain exactly one character", _re.I),
     _lexer_err(
         "A character literal contains more than one character or is empty.",
         "Character literals must be exactly one character.",
         "// BAD:  leaf c = 'AB';\n// GOOD: leaf c = 'A';\n// For text use vine: vine s = \"AB\";",
     )),

    (_re.compile(r"Illegal Character '(.)'", _re.I),
     lambda m: _lexer_err(
         f"The character '{m.group(1)}' is not valid in GAL.",
         "Only recognized operators, delimiters, and alphanumerics are allowed.",
         f"Remove or replace the '{m.group(1)}' character.",
     )),

    (_re.compile(r"Identifiers cannot start with a number", _re.I),
     _lexer_err(
         "A variable name starts with a digit.",
         "Identifiers must start with a letter (a-z, A-Z).",
         "// BAD:  seed 2count = 0;\n// GOOD: seed count2 = 0;",
     )),

    (_re.compile(r"Invalid escape sequence", _re.I),
     _lexer_err(
         "An unrecognized escape sequence was used in a string.",
         "Valid escapes: \\n, \\t, \\\\, \\\", \\{, \\}",
         '// BAD:  vine s = "hello\\x";\n// GOOD: vine s = "hello\\n";',
     )),

    (_re.compile(r"Missing closing '\*/'.*multi-line comment", _re.I),
     _lexer_err(
         "A multi-line comment was opened with /* but never closed.",
         "Multi-line comments must be closed with */.",
         "/* This is a comment */  // Correct\n/* Unclosed comment      // ERROR",
     )),

    # ── Parser: Operator Errors ───────────────────────────────────

    (_re.compile(r"'===' is not valid", _re.I),
     _parser_err(
         "Triple equals `===` is not a GAL operator.",
         "Use `==` for equality comparison.",
         "// BAD:  spring (x === 5) { ... }\n// GOOD: spring (x == 5) { ... }",
         "GAL does not have strict equality like JavaScript.",
     )),

    (_re.compile(r"'&' is not valid.*Use '&&'", _re.I),
     _parser_err(
         "Single `&` is not valid in GAL.",
         "Use `&&` for logical AND (GAL has no bitwise operators).",
         "// BAD:  spring (a & b) { ... }\n// GOOD: spring (a && b) { ... }",
     )),

    (_re.compile(r"'\|' is not valid.*Use '\|\|'", _re.I),
     _parser_err(
         "Single `|` is not valid in GAL.",
         "Use `||` for logical OR (GAL has no bitwise operators).",
         "// BAD:  spring (a | b) { ... }\n// GOOD: spring (a || b) { ... }",
     )),

    # ── Parser: Keyword Mistakes (generic — catches all 20+) ─────

    (_re.compile(r"'(\w+)' is not a GAL keyword\.\s*Use '(\w+)' instead", _re.I),
     lambda m: _parser_err(
         f"`{m.group(1)}` is not a GAL keyword.",
         f"Use `{m.group(2)}` instead of `{m.group(1)}`.",
         f"// BAD:  {m.group(1)} ...\n// GOOD: {m.group(2)} ...",
         "GAL uses botanical-themed keywords. See the keyword reference for all mappings.",
     )),

    # ── Parser: Missing Delimiters ────────────────────────────────

    (_re.compile(r"Expected\s*['\"]?;['\"]?|Unexpected token.*Expected\s*['\"]?;['\"]?", _re.I),
     _parser_err(
         "A statement is missing its terminating semicolon.",
         "Every statement must end with `;`.",
         "// BAD:  seed x = 5\n// GOOD: seed x = 5;",
         "Check the line in the error — the semicolon is usually needed at the end.",
     )),

    (_re.compile(r"Missing closing brace|Expected\s*'}'", _re.I),
     _parser_err(
         "A code block is missing its closing brace `}`.",
         "Every `{` must have a matching `}`.",
         "spring (x > 0) {\n    plant(\"positive\");\n}  // <-- don't forget this",
         "Count your opening and closing braces. Nested blocks are a common source of this error.",
     )),

    (_re.compile(r"Empty block.*Expected at least one statement", _re.I),
     _parser_err(
         "An empty block `{}` was found.",
         "Every block must contain at least one statement.",
         '// BAD:  spring (x > 0) { }\n// GOOD: spring (x > 0) { plant("yes"); }',
     )),

    (_re.compile(r"Unreachable code after 'reclaim'", _re.I),
     _parser_err(
         "Code appears after a `reclaim` (return) statement.",
         "Statements after `reclaim` will never execute.",
         "pollinate seed add(seed a, seed b) {\n    reclaim a + b;\n    // Remove any code below reclaim\n}",
     )),

    (_re.compile(r"Increment/decrement operators cannot be chained", _re.I),
     _parser_err(
         "Attempted to chain `++` or `--` operators.",
         "`++` and `--` cannot be chained.",
         "// BAD:  x++++;\n// GOOD: x++;\n//       x++;  // separate statements",
     )),

    (_re.compile(r"Missing return type after 'pollinate'", _re.I),
     _parser_err(
         "A function is missing its return type.",
         "Functions need a return type between `pollinate` and the name.",
         "// BAD:  pollinate add(seed a, seed b) { ... }\n// GOOD: pollinate seed add(seed a, seed b) { ... }",
         "Use `empty` for functions that don't return a value.",
     )),

    (_re.compile(r"Missing type for parameter '(\w+)'", _re.I),
     lambda m: _parser_err(
         f"Parameter `{m.group(1)}` is missing its type.",
         "Each function parameter must have a type.",
         f"// BAD:  pollinate seed fn({m.group(1)}) {{ ... }}\n// GOOD: pollinate seed fn(seed {m.group(1)}) {{ ... }}",
     )),

    (_re.compile(r"Unexpected token.*after program end", _re.I),
     _parser_err(
         "Code found after `root() { ... }` ended.",
         "All code must be inside functions or global declarations before `root()`.",
         "pollinate seed add(seed a, seed b) {\n    reclaim a + b;\n}\n\nroot() {\n    plant(add(1, 2));\n    reclaim;\n}",
     )),

    (_re.compile(r"Type mismatch in declaration of '(\w+)'.*declared as '(\w+)' but assigned '(\w+)'", _re.I),
     lambda m: _parser_err(
         f"Variable `{m.group(1)}` declared as `{m.group(2)}` but assigned a `{m.group(3)}` value.",
         "The value type must match the declared variable type.",
         f"// Use the correct type or value\n{m.group(2)} {m.group(1)} = <correct_{m.group(2)}_value>;",
         "`seed`↔`tree` are compatible. `leaf`, `vine`, `branch` are not interchangeable.",
     )),

    (_re.compile(r"Empty character literal.*must contain exactly one character", _re.I),
     _parser_err(
         "An empty character literal `''` was found.",
         "Character literals must contain exactly one character.",
         "// BAD:  leaf c = '';\n// GOOD: leaf c = 'A';",
     )),

    # ── Semantic Errors ───────────────────────────────────────────

    (_re.compile(r"Variable '(\w+)' already declared", _re.I),
     lambda m: _semantic_err(
         f"Variable `{m.group(1)}` has already been declared in this scope.",
         "Each variable name can only be declared once per scope.",
         f"seed {m.group(1)} = 10;  // Keep ONE declaration\n// seed {m.group(1)} = 20;  // Remove duplicate",
     )),

    (_re.compile(r"Variable '(\w+)' used before declaration", _re.I),
     lambda m: _semantic_err(
         f"Variable `{m.group(1)}` was used before being declared.",
         "All variables must be declared before use.",
         f"seed {m.group(1)} = 0;     // Declare FIRST\nplant({m.group(1)});      // Then use",
     )),

    (_re.compile(r"Type Mismatch.*Cannot assign (\w+) to variable '(\w+)' of type (\w+)", _re.I),
     lambda m: _semantic_err(
         f"Cannot assign `{m.group(1)}` value to `{m.group(2)}` (type `{m.group(3)}`).",
         "Assignment values must match the variable's declared type.",
         f"// Ensure the type matches:\n{m.group(3)} {m.group(2)} = <correct_value>;",
         "`seed`↔`tree` are compatible. Other types must match exactly.",
     )),

    (_re.compile(r"Modulo operator '%' requires 'seed'.*operands", _re.I),
     _semantic_err(
         "The `%` (modulo) operator was used with non-integer operands.",
         "Modulo requires both operands to be `seed` (integer).",
         "seed a = 10;\nseed b = 3;\nseed r = a % b;  // OK\n// tree x = 3.5 % 2;  // ERROR",
     )),

    (_re.compile(r"'!' operator can only be used with 'branch'", _re.I),
     _semantic_err(
         "The `!` (NOT) operator was used on a non-boolean value.",
         "`!` can only be applied to `branch` (boolean) values.",
         "branch flag = sunshine;\nbranch opp = !flag;  // OK\n// seed x = !5;       // ERROR",
     )),

    (_re.compile(r"Function '(\w+)' is not (?:declared|defined)", _re.I),
     lambda m: _semantic_err(
         f"Function `{m.group(1)}` was called but never defined.",
         "Functions must be defined with `pollinate` before `root()`.",
         f"pollinate seed {m.group(1)}(seed x) {{\n    reclaim x * 2;\n}}\n\nroot() {{\n    plant({m.group(1)}(5));\n    reclaim;\n}}",
     )),

    (_re.compile(r"Function '(\w+)' expects (\d+) argument\(s\), got (\d+)", _re.I),
     lambda m: _semantic_err(
         f"Function `{m.group(1)}` expects {m.group(2)} argument(s) but got {m.group(3)}.",
         "The number of arguments must match the function's parameter list.",
         f"// Check the function definition and pass the correct number of arguments.",
     )),

    (_re.compile(r"Argument (\d+) of function '(\w+)': expected '(\w+)', got '(\w+)'", _re.I),
     lambda m: _semantic_err(
         f"Argument {m.group(1)} of `{m.group(2)}` should be `{m.group(3)}`, got `{m.group(4)}`.",
         "Argument types must match the function's parameter types.",
         f"// Ensure argument {m.group(1)} is of type `{m.group(3)}`.",
     )),

    (_re.compile(r"empty function must not return any value", _re.I),
     _semantic_err(
         "A function declared as `empty` (void) is returning a value.",
         "Empty functions must use `reclaim;` without a value.",
         "pollinate empty greet() {\n    plant(\"Hello!\");\n    reclaim;  // No value after reclaim\n}",
     )),

    (_re.compile(r"Function '(\w+)' must end with 'reclaim'", _re.I),
     lambda m: _semantic_err(
         f"Function `{m.group(1)}` is missing a `reclaim` statement.",
         "All functions must end with `reclaim`.",
         f"pollinate seed {m.group(1)}(seed x) {{\n    // ... your code ...\n    reclaim x;  // Must end with reclaim\n}}",
     )),

    (_re.compile(r"must return a value on all code paths", _re.I),
     _semantic_err(
         "Not all code paths return a value.",
         "Non-empty functions must return a value on every execution path.",
         "pollinate seed abs(seed x) {\n    spring (x >= 0) {\n        reclaim x;\n    } wither {\n        reclaim ~x;  // Both paths return\n    }\n}",
     )),

    (_re.compile(r"'prune' used outside a loop or switch", _re.I),
     _semantic_err(
         "`prune` (break) was used outside of a loop or switch.",
         "`prune` can only be used inside loops or `harvest` blocks.",
         "cultivate (seed i = 0; i < 10; i++) {\n    spring (i == 5) {\n        prune;  // OK — inside loop\n    }\n}",
     )),

    (_re.compile(r"'skip' used outside a loop", _re.I),
     _semantic_err(
         "`skip` (continue) was used outside of a loop.",
         "`skip` can only be used inside loops.",
         "cultivate (seed i = 0; i < 10; i++) {\n    spring (i % 2 == 0) { skip; }\n    plant(i);  // prints odd numbers\n}",
     )),

    (_re.compile(r"Variable '(\w+)' is declared as fertile and cannot be re-assigned", _re.I),
     lambda m: _semantic_err(
         f"Attempted to reassign fertile (const) variable `{m.group(1)}`.",
         "Variables declared with `fertile` cannot be changed.",
         f"fertile seed {m.group(1)} = 100;\n// {m.group(1)} = 200;  // ERROR!\n// Use a non-fertile variable if it needs to change.",
     )),

    (_re.compile(r"Fertile variables must be initialized", _re.I),
     _semantic_err(
         "A `fertile` (const) variable was declared without an initial value.",
         "Fertile variables must be assigned a value at declaration.",
         "// BAD:  fertile seed MAX;\n// GOOD: fertile seed MAX = 100;",
     )),

    (_re.compile(r"(spring|bud|grow|tend|cultivate) condition must be branch, got (\w+)", _re.I),
     lambda m: _semantic_err(
         f"The `{m.group(1)}` condition must be `branch` (boolean), got `{m.group(2)}`.",
         "Conditions must evaluate to a boolean.",
         f"// BAD:  {m.group(1)} (x) {{ ... }}       // x is {m.group(2)}\n// GOOD: {m.group(1)} (x > 0) {{ ... }}   // comparison → branch",
         "Use comparison operators (`==`, `!=`, `<`, `>`, `<=`, `>=`) to produce boolean values.",
     )),

    (_re.compile(r"'harvest' expression must be 'seed'/'leaf'/'branch', not '(\w+)'", _re.I),
     lambda m: _semantic_err(
         f"The `harvest` (switch) expression is of type `{m.group(1)}`.",
         "Switch expressions must be `seed`, `leaf`, or `branch`.",
         "seed choice = water(seed);\nharvest (choice) {\n    variety 1: plant(\"One\"); prune;\n    soil: plant(\"Other\");\n}",
     )),

    (_re.compile(r"Duplicate 'variety' value", _re.I),
     _semantic_err(
         "Two `variety` (case) labels have the same value.",
         "Each `variety` value must be unique.",
         "harvest (x) {\n    variety 1: plant(\"One\"); prune;\n    variety 2: plant(\"Two\"); prune;  // Each unique\n    soil: plant(\"Other\");\n}",
     )),

    (_re.compile(r"Bundle type '(\w+)' is not defined", _re.I),
     lambda m: _semantic_err(
         f"Bundle type `{m.group(1)}` has not been defined.",
         "Bundle types must be defined before use.",
         f"bundle {m.group(1)} {{\n    seed x;\n    seed y;\n}};\n\nbundle {m.group(1)} obj;\nobj.x = 5;",
     )),

    (_re.compile(r"'ts\(\)' can only be used on lists or vines", _re.I),
     _semantic_err(
         "`ts()` was called on a non-list, non-string value.",
         "`ts()` only works on arrays and `vine` strings.",
         "seed arr[] = {1, 2, 3};\nseed len = ts(arr);  // 3\nvine msg = \"hello\";\nseed slen = ts(msg); // 5",
     )),

    (_re.compile(r"'taper\(\)' can only be used on 'leaf' type", _re.I),
     _semantic_err(
         "`taper()` was called on a non-string/char value.",
         "`taper()` splits a string into individual characters.",
         'leaf chars[] = taper("hello");  // [\'h\',\'e\',\'l\',\'l\',\'o\']',
     )),

    (_re.compile(r"Exceeded maximum.*15 arguments in plant", _re.I),
     _semantic_err(
         "A `plant()` statement has more than 15 arguments.",
         "`plant()` supports a maximum of 15 arguments.",
         "// Split into multiple plant() calls if needed.",
     )),

    (_re.compile(r"Found (\d+) argument\(s\)\.\s*Expected (\d+) argument\(s\)", _re.I),
     lambda m: _semantic_err(
         f"`plant()` has {m.group(1)} argument(s) but the format string expects {m.group(2)}.",
         "The number of `{{}}` placeholders must match the extra arguments.",
         '// BAD:  plant("{} + {}", a);         // 2 placeholders, 1 arg\n// GOOD: plant("{} + {}", a, b);      // 2 placeholders, 2 args',
     )),

    (_re.compile(r"Array size must be of type 'seed'", _re.I),
     _semantic_err(
         "A non-integer was used as an array size.",
         "Array sizes must be `seed` (integer).",
         "// BAD:  seed arr[3.5];\n// GOOD: seed arr[5];",
     )),

    (_re.compile(r"List index must be of type 'seed', got '(\w+)'", _re.I),
     lambda m: _semantic_err(
         f"An array index of type `{m.group(1)}` was used instead of `seed`.",
         "Array indices must be `seed` (integer).",
         "seed arr[] = {10, 20, 30};\nseed i = 1;\nplant(arr[i]);  // OK: seed index",
     )),

    # ── Runtime Errors ────────────────────────────────────────────

    (_re.compile(r"Division by zero", _re.I),
     _runtime_err(
         "A division or modulo by zero was attempted.",
         "The divisor must not be zero.",
         "seed a = 10;\nseed b = 0;\n// seed c = a / b;  // Runtime Error!\nspring (b != 0) {\n    seed c = a / b;  // Safe\n}",
         "Always check that the divisor is non-zero before dividing.",
     )),

    (_re.compile(r"Infinite loop detected", _re.I),
     _runtime_err(
         "A loop exceeded the maximum iteration limit (10,000).",
         "Loops are limited to 10,000 iterations.",
         "seed i = 0;\ngrow (i < 100) {\n    plant(i);\n    i++;  // Don't forget to update!\n}",
         "Common cause: forgetting to update the loop variable so the condition never becomes false.",
     )),

    (_re.compile(r"Index '?(-?\d+)'? out of bounds for (?:list )?'?(\w+)'?", _re.I),
     lambda m: _runtime_err(
         f"Index `{m.group(1)}` is out of bounds for array `{m.group(2)}`.",
         "Array indices must be between 0 and length-1.",
         f"// Valid indices: 0 to ts({m.group(2)})-1\ncultivate (seed i = 0; i < ts({m.group(2)}); i++) {{\n    plant({m.group(2)}[i]);\n}}",
     )),

    (_re.compile(r"Evaluated number exceeds maximum.*16 digits", _re.I),
     _runtime_err(
         "A computed number exceeded the 16-digit limit.",
         "Numbers at runtime cannot exceed 16 digits.",
         "// Use smaller values or break computations into steps.",
     )),

    (_re.compile(r"Condition must be a boolean.*Got '(.+)'", _re.I),
     lambda m: _runtime_err(
         f"A condition evaluated to `{m.group(1)}` instead of a boolean.",
         "Conditions must be `sunshine` or `frost`.",
         "// Use a comparison to produce a boolean:\nspring (x > 0) { ... }  // Correct",
     )),

    (_re.compile(r"Variable '(\w+)' is not a list", _re.I),
     lambda m: _runtime_err(
         f"Attempted to index `{m.group(1)}`, which is not an array.",
         "Only arrays can be indexed with `[]`.",
         f"// Declare as array:\nseed {m.group(1)}[5];  // Array\n// Not: seed {m.group(1)} = 5;  // Scalar",
     )),
]


def _rule_engine_match(msg):
    """Try each regex pattern against the user message.
    Return a structured response string if matched, else None."""
    for pattern, response in _ERROR_PATTERNS:
        m = pattern.search(msg)
        if m:
            return response(m) if callable(response) else response
    return None


# ═══════════════════════════════════════════════════════════════════════
# LAYER 2: EXPANDED KNOWLEDGE BASE (50+ topics)
# ═══════════════════════════════════════════════════════════════════════
# Each entry: (training_phrases_list, response_string)

_KNOWLEDGE_BASE = [
    # ── 1. Data types ─────────────────────────────────────────────
    ([
        "what are the data types",
        "data types in GAL",
        "seed tree leaf vine branch",
        "integer float char string boolean",
        "types of variables",
        "what type should I use",
        "type system",
        "GAL types",
        "int float double char string bool",
     ],
     """GAL has 5 data types (botanical-themed):

| GAL | C Equivalent | Description |
|-----|-------------|-------------|
| `seed` | int | Integer |
| `tree` | float | Decimal number |
| `leaf` | char | Single character (`'A'`) |
| `vine` | string | Text (`"hello"`) |
| `branch` | bool | Boolean (`sunshine` / `frost`) |
| `empty` | void | No return value (functions only) |

Example:
```
seed x = 10;
tree pi = 3.14;
vine name = "Alice";
leaf ch = 'A';
branch flag = sunshine;
```"""),

    # ── 2. Variables / declarations ───────────────────────────────
    ([
        "how to declare a variable",
        "variable declaration",
        "create a variable",
        "initialize variable",
        "define variable",
        "constant fertile const",
        "multiple variables",
        "declare seed tree vine",
     ],
     """Declare variables with a type keyword followed by the name:
```
seed x;          // integer, uninitialized
seed x = 10;     // integer with initial value
tree pi = 3.14;  // float
vine msg = "Hi"; // string
leaf ch = 'A';   // character
branch ok = sunshine; // boolean
```
Multiple on one line: `seed a = 1, b = 2, c;`

Constants use `fertile`:
```
fertile seed MAX = 100;
```"""),

    # ── 3. Arrays ─────────────────────────────────────────────────
    ([
        "how to use arrays",
        "array declaration",
        "create an array",
        "list in GAL",
        "2d array multidimensional matrix",
        "array index element access",
        "arr bracket",
        "array of integers",
        "tell me about arrays",
        "store multiple values in a variable",
        "hold many items in a collection",
        "iterate over array elements",
        "go through each item in array",
     ],
     """**Arrays** — declare with a size or use brace initialization:
```
seed arr[5];
arr[0] = 10;
arr[1] = 20;
```
**Brace initialization:**
```
seed arr[] = {1, 2, 3};      // size inferred
seed nums[5] = {10, 20, 30}; // fixed size
```
**2D arrays:**
```
seed matrix[2][3];
matrix[0][1] = 5;
seed grid[][] = {{1, 2}, {3, 4}};  // nested init
```
Arrays are 0-indexed."""),

    # ── 4. For loop (cultivate) ───────────────────────────────────
    ([
        "for loop",
        "cultivate loop",
        "what is cultivate",
        "how to use cultivate",
        "count from 0 to 10",
        "iterate with index",
        "loop with counter",
        "for i in range",
        "traditional for loop",
     ],
     """**For loop** uses `cultivate`:
```
cultivate(seed i = 0; i < 5; i++) {
    plant(i);
}
```
- Syntax: `cultivate(init; condition; update) { body }`
- `cultivate` = C's `for`
- Use `prune;` (break) to exit early
- Use `skip;` (continue) to skip to next iteration

Example — traverse an array:
```
seed arr[] = {10, 20, 30};
cultivate(seed i = 0; i < TS(arr); i++) {
    plant(arr[i]);
}
```"""),

    # ── 5. While loop (grow) ──────────────────────────────────────
    ([
        "while loop",
        "grow loop",
        "what is grow",
        "how to use grow",
        "what is while loop",
        "while loop in GAL",
        "loop while condition",
        "repeat while true",
        "loop until condition",
        "keep looping",
     ],
     """**While loop** uses `grow`:
```
seed count = 0;
grow (count < 3) {
    plant(count);
    count++;
}
```
- Syntax: `grow (condition) { body }`
- `grow` = C's `while`
- Checks condition **before** each iteration
- Use `prune;` (break) to exit early
- Use `skip;` (continue) to skip to next iteration"""),

    # ── 6. Do-while loop (tend...grow) ────────────────────────────
    ([
        "do while loop",
        "do-while loop",
        "tend grow do-while",
        "what is tend",
        "how to use tend",
        "do while",
        "what is do while",
        "do while in GAL",
        "loop at least once",
        "execute then check",
        "post-condition loop",
     ],
     """**Do-while loop** uses `tend...grow`:
```
seed val = 0;
tend {
    val++;
    plant(val);
} grow (val < 5);
```
- Syntax: `tend { body } grow (condition);`
- `tend...grow` = C's `do...while`
- Body runs **at least once** before checking condition
- Use `prune;` (break) to exit early
- Use `skip;` (continue) to skip to next iteration"""),

    # ── 7. Loops overview ─────────────────────────────────────────
    ([
        "how to make a loop",
        "loop types in GAL",
        "looping construct",
        "all loops",
        "what loops exist",
        "what are the loops",
        "types of loops",
        "how many loops",
        "list all loops",
        "loop overview",
     ],
     """GAL has 3 loop types:

**1. For loop** (`cultivate`):
```
cultivate(seed i = 0; i < 5; i++) {
    plant(i);
}
```

**2. While loop** (`grow`):
```
seed count = 0;
grow (count < 3) {
    plant(count);
    count++;
}
```

**3. Do-while loop** (`tend...grow`):
```
seed val = 0;
tend {
    val++;
} grow (val < 5);
```

Use `prune;` (break) and `skip;` (continue) inside loops."""),

    # ── 8. If / else ──────────────────────────────────────────────
    ([
        "if else condition",
        "conditional statement",
        "spring bud wither",
        "if statement else if",
        "check a condition",
        "branching logic",
        "compare values",
        "decision making",
        "if then else",
     ],
     """**If/else** uses botanical keywords:
```
spring (x > 0) {
    plant("positive");
} bud (x == 0) {
    plant("zero");
} wither {
    plant("negative");
}
```
- `spring` = if
- `bud` = else if
- `wither` = else"""),

    # ── 9. Switch ─────────────────────────────────────────────────
    ([
        "switch case statement",
        "harvest variety soil",
        "switch multiple cases",
        "select from options",
        "menu selection choice",
        "match value",
     ],
     """**Switch statement** uses `harvest`/`variety`/`soil`:
```
harvest (choice) {
    variety 1: plant("One"); prune;
    variety 2: plant("Two"); prune;
    soil: plant("Other");
}
```
- `harvest` = switch
- `variety` = case
- `soil` = default
- `prune` = break"""),

    # ── 10. Functions ─────────────────────────────────────────────
    ([
        "how to create a function",
        "function declaration definition",
        "pollinate reclaim return",
        "define a function",
        "call a function",
        "function parameters arguments",
        "return value from function",
        "void function empty",
        "root main entry point",
        "function with parameters",
     ],
     """**Functions** are declared with `pollinate`:
```
pollinate seed add(seed a, seed b) {
    reclaim a + b;
}
```
- `pollinate <return_type> <name>(<params>) { ... }`
- `reclaim` = return
- `reclaim;` for void functions
- `empty` = void return type

The entry point is always `root()`:
```
root() {
    plant("Hello!");
    reclaim;
}
```"""),

    # ── 11. Input (water) ─────────────────────────────────────────
    ([
        "how to read input",
        "get user input",
        "water input scanf stdin",
        "read from keyboard",
        "ask user for value",
        "input a number string",
        "water seed vine",
        "read into variable",
        "prompt user",
     ],
     """**Input** uses `water()`:
```
seed x = water(seed);      // read integer into x
vine name = water(vine);    // read string into name
water(myVar);               // read into existing variable
water(arr[i]);              // read into array element
water(arr[i][j]);           // read into 2D array element
```
`water(seed x)` is WRONG — don't combine type + variable name."""),

    # ── 12. Output (plant) ────────────────────────────────────────
    ([
        "how to print output",
        "display show output",
        "plant print printf",
        "print a variable",
        "format string placeholder",
        "print text to screen",
        "output a message",
        "write to console",
        "show result",
     ],
     """**Output** uses `plant()` with format strings:
```
plant("Hello World!");
plant("x = {}", x);
plant("{} + {} = {}", a, b, a + b);
plant(num);                  // print a single value
```
Use `{}` as placeholders (like Python's `.format()`).

Do NOT use backtick concat with variables in plant():
- `plant("Hello {}", name);` is CORRECT
- Use format strings with `{}` placeholder instead"""),

    # ── 13. Bundles (structs) ─────────────────────────────────────
    ([
        "struct bundle record",
        "create a struct",
        "bundle definition",
        "group fields together",
        "custom type with fields",
        "object with properties",
        "struct member access dot",
        "bundle Point",
        "how to use bundles",
     ],
     """**Bundles** are like C structs:
```
bundle Point {
    seed x;
    seed y;
};
```
Declare and use:
```
bundle Point p;    // 'bundle' keyword required!
p.x = 5;
p.y = 10;
```
**Nested bundles:**
```
bundle Address { vine city; seed zip; };
bundle Person  { vine name; Address addr; };

bundle Person p;
p.name = "Alice";
p.addr.city = "Manila";
p.addr.zip = 1000;
```
**Array of bundles:** `bundle Point pts[5];` then `pts[0].x = 1;`

No inline init: `bundle Point p = {5, 10};` is NOT supported."""),

    # ── 14. Operators ─────────────────────────────────────────────
    ([
        "operators in GAL",
        "arithmetic comparison logical",
        "plus minus multiply divide modulo",
        "tilde negation negate",
        "string concatenation backtick",
        "increment decrement",
        "assignment operator",
        "operator precedence",
        "equal not equal greater less",
     ],
     """**Operators:**
- Arithmetic: `+`, `-`, `*`, `/`, `%`
- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Logical: `&&`, `||`, `!`
- Assignment: `=`, `+=`, `-=`, `*=`, `/=`, `%=`
- Increment: `++`, `--` (prefix and postfix)
- Negation: `~` (tilde, e.g. `~5` = -5)
- String concat: backtick character

`**` (exponent) is NOT supported."""),

    # ── 15. Errors / debugging ────────────────────────────────────
    ([
        "error bug debug fix",
        "why is my code not working",
        "syntax error semantic error",
        "runtime error crash",
        "common mistakes problems",
        "troubleshoot issue",
        "what went wrong",
        "how to fix this error",
        "code not running",
        "fails with error",
     ],
     """Common GAL errors and fixes:

**Syntax errors:**
- Missing `;` at end of statement
- Missing `}` or `)` (check matching brackets)
- Using C keywords instead of GAL: `if` -> `spring`, `for` -> `cultivate`

**Semantic errors:**
- Variable not declared before use
- Type mismatch in operations
- Using `Point p;` instead of `bundle Point p;`

**Runtime errors:**
- Array index out of bounds (arrays are 0-indexed)
- Division by zero

Tip: Check the OUTPUT panel for line numbers to locate errors."""),

    # ── 16. Keywords reference ────────────────────────────────────
    ([
        "keyword reference list",
        "all GAL keywords",
        "cheat sheet quick reference",
        "GAL syntax summary",
        "what keywords does GAL have",
        "GAL to C mapping",
        "keyword table",
        "help reference guide",
     ],
     """**GAL Keyword Reference:**

| GAL | C Equivalent |
|-----|-------------|
| `root()` | main() |
| `pollinate` | function declaration |
| `reclaim` | return |
| `plant()` | printf/print |
| `water()` | scanf/input |
| `spring` | if |
| `bud` | else if |
| `wither` | else |
| `cultivate` | for loop |
| `grow` | while loop |
| `tend...grow` | do-while |
| `harvest` | switch |
| `variety` | case |
| `soil` | default |
| `prune` | break |
| `skip` | continue |
| `fertile` | const |
| `bundle` | struct |
| `sunshine` | true |
| `frost` | false |
| `~` | unary minus |"""),

    # ── 17. Example / template ────────────────────────────────────
    ([
        "example program template",
        "hello world starter code",
        "sample code basic program",
        "simple GAL program",
        "beginner getting started",
        "write a GAL program",
        "show me an example",
        "generate code",
     ],
     """Here's a complete GAL program:
```
root() {
    seed num = water(seed);

    spring (num > 0) {
        plant("Positive: {}", num);
    } bud (num < 0) {
        plant("Negative: {}", num);
    } wither {
        plant("Zero!");
    }

    reclaim;
}
```
Every GAL program needs a `root()` function as the entry point."""),

    # ── 18. Convert from C ────────────────────────────────────────
    ([
        "convert C to GAL",
        "translate from C language",
        "C equivalent GAL equivalent",
        "how to write this in GAL",
        "what is the GAL version of",
        "same as C but in GAL",
        "porting C code to GAL",
     ],
     """**C to GAL translation guide:**
- `int` -> `seed`, `float` -> `tree`, `char` -> `leaf`, `string` -> `vine`, `bool` -> `branch`
- `main()` -> `root()`
- `printf()` -> `plant()`, `scanf()` -> `water()`
- `if` -> `spring`, `else if` -> `bud`, `else` -> `wither`
- `for` -> `cultivate`, `while` -> `grow`, `do-while` -> `tend...grow`
- `switch` -> `harvest`, `case` -> `variety`, `default` -> `soil`
- `break` -> `prune`, `continue` -> `skip`
- `const` -> `fertile`, `struct` -> `bundle`
- `return` -> `reclaim`, `void` -> `empty`
- `-x` -> `~x` (unary negation uses tilde)"""),

    # ── 19. Comments ──────────────────────────────────────────────
    ([
        "how to write comments in GAL code",
        "comment syntax slash slash",
        "single line comment double slash",
        "multi line block comment",
        "how to comment out code",
        "annotation note in source code",
        "commenting GAL code",
        "// slash star block comment format",
     ],
     """**Comments** in GAL:
```
// This is a single-line comment

/* This is a
   multi-line comment */
```
Same syntax as C/Java."""),

    # ── 20. Identifier rules ──────────────────────────────────────
    ([
        "identifier rules naming",
        "variable name rules",
        "maximum length identifier",
        "valid variable names",
        "naming conventions",
        "identifier too long",
     ],
     """**Identifier rules:**
- Must start with a letter (a-z, A-Z)
- Can contain letters, digits, underscores after first character
- Maximum **15 characters** (longer = lexical error)
- Cannot start with a number or underscore
- Keywords are reserved

Valid: `x`, `count`, `myVar`, `total_sum`, `playerScore1`
Invalid: `2count`, `_name`, `thisIsWayTooLong`"""),

    # ── 21. Type casting ──────────────────────────────────────────
    ([
        "type casting conversion",
        "convert between types",
        "cast seed to tree",
        "cast integer to float string",
        "change variable type",
        "how to cast in GAL",
        "convert float to int",
        "convert number to string",
     ],
     """**Type casting** uses parenthesized type before an expression:
```
tree x = 3.14;
seed y = (seed)x;       // y = 3 (truncated)
vine s = (vine)42;      // s = "42"
leaf c = (leaf)65;      // c = 'A' (ASCII)
branch b = (branch)1;   // b = sunshine
tree f = (tree)10;      // f = 10.0
```
Supported casts:
- `(seed)` — converts to integer (truncates floats)
- `(tree)` — converts to float
- `(leaf)` — int→char (ASCII), string→first char
- `(vine)` — converts anything to string
- `(branch)` — converts to boolean"""),

    # ── 22. Array built-in operations ─────────────────────────────
    ([
        "array built-in methods operations",
        "append to array add element",
        "insert into array",
        "remove from array delete element",
        "array length size count",
        "taper split string to chars",
        "TS function array size",
        "add item to list",
        "delete item from list",
        "how many elements in array",
     ],
     """**Array built-in operations:**

**Append** — add element(s) to end:
```
seed arr[5];
arr.append(10);        // arr = [10]
arr.append(20, 30);    // arr = [10, 20, 30]
```
**Insert** — insert at index:
```
arr.insert(1, 99);     // insert 99 at index 1
```
**Remove** — remove element at index:
```
arr.remove(0);         // remove first element
```
**TS** — get length of array or string:
```
seed len = TS(arr);    // number of elements
seed slen = TS("hello"); // 5
```
**Taper** — split string into char array:
```
leaf chars[] = taper("abc"); // chars = ['a','b','c']
```"""),

    # ── 23. Escape sequences ──────────────────────────────────────
    ([
        "escape sequences special characters",
        "newline tab in string",
        "backslash n backslash t",
        "print new line",
        "special characters in strings",
        "how to add newline",
        "escape quote in string",
     ],
     """**Escape sequences** in strings:

| Sequence | Result |
|----------|--------|
| `\\n` | Newline |
| `\\t` | Tab |
| `\\\\` | Backslash `\\` |
| `\\"` | Double quote |
| `\\{` | Literal `{` (in format strings) |
| `\\}` | Literal `}` |
| `\\/` | Forward slash |

Example:
```
plant("Line 1\\nLine 2");
plant("Name:\\tAlice");
plant("She said \\"hi\\"");
```"""),

    # ── 24. String concatenation ──────────────────────────────────
    ([
        "string concatenation combine join",
        "concatenate two strings",
        "join strings together",
        "backtick concat operator",
        "combine text values",
        "merge strings",
        "add strings together",
     ],
     """**String concatenation** uses the backtick `` ` `` operator:
```
vine first = "Hello";
vine second = "World";
vine result = first ` " " ` second;  // "Hello World"
```
The `+` operator also works for concatenation when at least one operand is a string:
```
vine msg = "Age: " + (vine)25;  // "Age: 25"
```
For output, prefer format strings:
```
plant("{} {}", first, second);  // cleaner
```"""),

    # ══════════════════════════════════════════════════════════════
    #  NEW TOPICS (25–54) — expanded coverage
    # ══════════════════════════════════════════════════════════════

    # ── 25. Program structure & root() ────────────────────────────
    ([
        "program structure organization",
        "where does root go",
        "how to organize GAL program",
        "file structure layout",
        "code organization order",
        "what comes first in program",
        "program skeleton template",
     ],
     """**GAL program structure:**
```
// 1. Global declarations (optional)
seed globalVar = 42;

// 2. Bundle definitions (optional)
bundle Point { seed x; seed y; };

// 3. Function definitions (optional)
pollinate seed add(seed a, seed b) {
    reclaim a + b;
}

// 4. Entry point (REQUIRED)
root() {
    plant(add(1, 2));
    reclaim;
}
```
**Rules:**
- `root()` is always the entry point (like C's `main`)
- Functions must be defined **before** `root()`
- Global variables go at the top
- `root()` must end with `reclaim;`
- No code is allowed after `root()`'s closing `}`"""),

    # ── 26. Scope rules ───────────────────────────────────────────
    ([
        "scope rules variable visibility",
        "local variable global variable",
        "variable scope lifetime",
        "where can I access variable",
        "block scope braces",
        "variable not visible",
        "inner scope outer scope",
     ],
     """**Scope rules in GAL:**

**Global scope** — declared outside `root()` and functions:
```
seed globalCount = 0;  // accessible everywhere
root() {
    plant(globalCount);  // OK
    reclaim;
}
```

**Local scope** — declared inside a block `{ }`:
```
root() {
    seed x = 10;       // local to root
    spring (x > 0) {
        seed y = 20;   // local to this block
        plant(x);      // OK — x is in outer scope
    }
    // plant(y);  // ERROR — y not visible here
    reclaim;
}
```

**Function scope** — each function has its own scope:
```
pollinate empty test() {
    seed a = 5;  // only visible inside test()
    reclaim;
}
```

Variables in inner scopes can see outer scopes, but not vice versa."""),

    # ── 27. Constants (fertile) ───────────────────────────────────
    ([
        "how to make constant",
        "fertile keyword constant",
        "immutable variable value",
        "cannot change value once set",
        "fixed value read only",
        "declare constant GAL",
        "fertile rules restrictions",
     ],
     """**Constants** use the `fertile` keyword:
```
fertile seed MAX = 100;
fertile tree PI = 3.14159;
fertile vine GREETING = "Hello";
fertile leaf NEWLINE = '\\n';
fertile branch DEBUG = frost;
```

**Rules:**
- Must be initialized at declaration: `fertile seed MAX;` is **invalid**
- Cannot be reassigned: `MAX = 200;` gives a semantic error
- Only literal values allowed (no expressions or variables)
- Multiple `fertile` declarations on one line are **not** allowed
- `fertile` goes before the type: `fertile seed`, not `seed fertile`"""),

    # ── 28. Boolean values ────────────────────────────────────────
    ([
        "boolean values in GAL",
        "sunshine and frost meaning",
        "what is sunshine frost",
        "true and false in GAL",
        "branch type values",
        "boolean literals",
     ],
     """**Boolean values** in GAL use botanical names:

| GAL | Meaning |
|-----|---------|
| `sunshine` | `true` |
| `frost` | `false` |

```
branch isReady = sunshine;   // true
branch isDone = frost;       // false

spring (isReady) {
    plant("Ready!");
}

// Comparisons return branch values:
branch result = (5 > 3);    // sunshine
branch equal = (x == y);    // depends on x, y
```

Use `!` to negate: `!sunshine` = `frost`"""),

    # ── 29. Function return types ─────────────────────────────────
    ([
        "function return type options",
        "empty function void return",
        "what return types exist",
        "how to return value function",
        "reclaim with value",
        "function that returns nothing",
     ],
     """**Function return types:**

Every function must specify a return type after `pollinate`:

```
pollinate seed square(seed x) {    // returns seed
    reclaim x * x;
}

pollinate tree average(seed a, seed b) {  // returns tree
    reclaim (tree)(a + b) / 2;
}

pollinate vine greet(vine name) {  // returns vine
    reclaim "Hello " ` name;
}

pollinate empty sayHi() {          // returns nothing
    plant("Hi!");
    reclaim;                       // no value after reclaim
}
```

**Available return types:** `seed`, `tree`, `leaf`, `vine`, `branch`, `empty`

**Rules:**
- `empty` functions must use `reclaim;` (no value)
- Non-empty functions must `reclaim` a value on **all** code paths
- All functions must end with `reclaim`"""),

    # ── 30. Recursive functions ───────────────────────────────────
    ([
        "recursive function in GAL",
        "recursion example",
        "function calls itself",
        "recursive algorithm",
        "base case recursion",
     ],
     """**Recursive functions** — a function that calls itself:
```
pollinate seed factorial(seed n) {
    spring (n <= 1) {
        reclaim 1;              // base case
    } wither {
        reclaim n * factorial(n - 1);  // recursive call
    }
}

root() {
    plant("5! = {}", factorial(5));  // prints 120
    reclaim;
}
```

**Tips:**
- Always have a **base case** to stop recursion
- Each recursive call should move toward the base case
- Be mindful of the 10,000 iteration limit (applies to deep recursion too)"""),

    # ── 31. Nested conditionals ───────────────────────────────────
    ([
        "nested if statements",
        "if inside if nested",
        "multiple nested conditions",
        "nested spring bud wither",
        "complex conditional logic",
     ],
     """**Nested conditionals** — `spring`/`bud`/`wither` inside each other:
```
root() {
    seed age = water(seed);
    vine status = water(vine);

    spring (age >= 18) {
        spring (status == "student") {
            plant("Adult student");
        } wither {
            plant("Adult non-student");
        }
    } wither {
        spring (age >= 13) {
            plant("Teenager");
        } wither {
            plant("Child");
        }
    }
    reclaim;
}
```

Tip: Deeply nested conditions can be hard to read. Consider using `bud` chains instead:
```
spring (condition1) { ... }
bud (condition2) { ... }
bud (condition3) { ... }
wither { ... }
```"""),

    # ── 32. Prune (break) & skip (continue) ──────────────────────
    ([
        "break statement prune",
        "continue statement skip",
        "exit loop early",
        "skip iteration next",
        "stop loop prematurely",
        "prune and skip usage",
     ],
     """**`prune`** (break) — exit a loop or switch immediately:
```
cultivate (seed i = 0; i < 100; i++) {
    spring (i == 5) {
        prune;  // exits the loop when i is 5
    }
    plant(i);   // prints 0,1,2,3,4
}
```

**`skip`** (continue) — skip to the next iteration:
```
cultivate (seed i = 0; i < 10; i++) {
    spring (i % 2 == 0) {
        skip;  // skip even numbers
    }
    plant(i);  // prints 1,3,5,7,9
}
```

**Rules:**
- `prune` can be used in loops (`cultivate`, `grow`, `tend`) and `harvest` (switch)
- `skip` can only be used in loops (not in `harvest`)
- Using them outside their valid context gives a semantic error"""),

    # ── 33. Nested loops ──────────────────────────────────────────
    ([
        "nested loop inside loop",
        "double loop two loops",
        "inner outer loop",
        "loop within loop",
        "two dimensional loop",
     ],
     """**Nested loops** — a loop inside another loop:
```
// Multiplication table
cultivate (seed i = 1; i <= 5; i++) {
    cultivate (seed j = 1; j <= 5; j++) {
        plant("{} x {} = {}", i, j, i * j);
    }
}
```

**Traversing a 2D array:**
```
seed grid[3][3];
cultivate (seed r = 0; r < 3; r++) {
    cultivate (seed c = 0; c < 3; c++) {
        grid[r][c] = r * 3 + c;
    }
}
```

Note: `prune` only exits the **innermost** loop. To exit an outer loop, use a flag variable."""),

    # ── 34. 2D arrays detailed ────────────────────────────────────
    ([
        "two dimensional array detailed",
        "matrix operations rows columns",
        "2d array initialization access",
        "array of arrays nested",
        "row column indexing",
        "multi dimensional array",
     ],
     """**2D arrays** in GAL:

**Declaration:**
```
seed matrix[3][4];   // 3 rows, 4 columns
```

**Brace initialization:**
```
seed grid[][] = {
    {1, 2, 3},
    {4, 5, 6}
};
```

**Access and assignment:**
```
matrix[0][0] = 10;       // first element
matrix[2][3] = 99;       // last element (0-indexed)
seed val = matrix[1][2];  // read element
```

**Traversal:**
```
cultivate (seed i = 0; i < 3; i++) {
    cultivate (seed j = 0; j < 4; j++) {
        plant("matrix[{}][{}] = {}", i, j, matrix[i][j]);
    }
}
```

Arrays are 0-indexed: valid indices for `arr[M][N]` are `[0..M-1][0..N-1]`."""),

    # ── 35. Array of bundles ──────────────────────────────────────
    ([
        "array of bundles structs",
        "list of struct objects",
        "multiple bundles in array",
        "bundle array declaration",
        "storing multiple records",
        "bundle Point pts array",
        "array of struct records",
        "declaring array of bundle",
     ],
     """**Array of bundles:**
```
bundle Student {
    vine name;
    seed grade;
};

root() {
    bundle Student class[3];

    class[0].name = "Alice";
    class[0].grade = 95;
    class[1].name = "Bob";
    class[1].grade = 87;
    class[2].name = "Carol";
    class[2].grade = 92;

    cultivate (seed i = 0; i < 3; i++) {
        plant("{}: {}", class[i].name, class[i].grade);
    }
    reclaim;
}
```

**Syntax:** `bundle <Type> <name>[<size>];`
Then access: `name[index].member`"""),

    # ── 36. Nested bundles ────────────────────────────────────────
    ([
        "nested bundle struct inside struct",
        "bundle with bundle member",
        "deep member access chain",
        "bundle composition nested fields",
        "struct within struct",
     ],
     """**Nested bundles** — a bundle containing another bundle:
```
bundle Address {
    vine city;
    seed zipCode;
};

bundle Person {
    vine name;
    seed age;
    Address addr;       // nested bundle
};

root() {
    bundle Person p;
    p.name = "Alice";
    p.age = 25;
    p.addr.city = "Manila";    // access nested field
    p.addr.zipCode = 1000;

    plant("{} lives in {} ({})",
        p.name, p.addr.city, p.addr.zipCode);
    reclaim;
}
```

Define inner bundles **before** the outer bundle that uses them."""),

    # ── 37. TS() function ─────────────────────────────────────────
    ([
        "ts function get length",
        "array length size",
        "string length character count",
        "how many elements in list",
        "count items in array",
        "TS usage examples",
     ],
     """**`TS()`** — returns the length of an array or string:
```
seed arr[] = {10, 20, 30, 40};
seed len = TS(arr);         // 4

vine msg = "Hello World";
seed slen = TS(msg);        // 11

// Common pattern — loop with TS:
cultivate (seed i = 0; i < TS(arr); i++) {
    plant(arr[i]);
}
```

**Rules:**
- Works on arrays/lists and `vine` strings
- Returns a `seed` (integer) value
- Does NOT work on `seed`, `tree`, `leaf`, or `branch` scalars
- `TS()` is GAL's equivalent of `len()` / `.length`"""),

    # ── 38. Taper() function ──────────────────────────────────────
    ([
        "taper function usage",
        "split string into characters",
        "string to char array",
        "character array from string",
        "taper examples",
     ],
     """**`taper()`** — splits a string into an array of characters:
```
leaf chars[] = taper("Hello");
// chars = ['H', 'e', 'l', 'l', 'o']

plant(chars[0]);  // H
plant(TS(chars));  // 5

// Iterate over characters:
cultivate (seed i = 0; i < TS(chars); i++) {
    plant(chars[i]);
}
```

**Rules:**
- Returns a `leaf` array
- Works on `vine` (string) values
- `taper()` is GAL's equivalent of `split('')` / `toCharArray()`"""),

    # ── 39. Operator precedence ───────────────────────────────────
    ([
        "operator precedence order",
        "which operator evaluated first",
        "order of operations math",
        "evaluation order priority",
        "operator priority table",
     ],
     """**Operator precedence** (highest to lowest):

| Priority | Operators | Description |
|----------|-----------|-------------|
| 1 (highest) | `~`, `++`, `--`, `!` | Unary |
| 2 | `*`, `/`, `%` | Multiplication, division, modulo |
| 3 | `+`, `-`, `` ` `` | Addition, subtraction, concat |
| 4 | `<`, `>`, `<=`, `>=` | Relational comparison |
| 5 | `==`, `!=` | Equality |
| 6 | `&&` | Logical AND |
| 7 (lowest) | `\\|\\|` | Logical OR |

**Use parentheses to override:**
```
seed result = (2 + 3) * 4;  // 20, not 14
branch check = (a > 0) && (b < 10);
```"""),

    # ── 40. Increment / decrement ─────────────────────────────────
    ([
        "prefix postfix increment",
        "i++ vs ++i difference",
        "decrement minus minus",
        "plus plus operator",
        "pre increment post increment",
     ],
     """**Increment (`++`) and Decrement (`--`):**

**Prefix** — changes value BEFORE using it:
```
seed x = 5;
seed y = ++x;  // x becomes 6, then y = 6
```

**Postfix** — uses value BEFORE changing it:
```
seed x = 5;
seed y = x++;  // y = 5, then x becomes 6
```

**As standalone statements (most common):**
```
seed count = 0;
count++;   // count = 1
count++;   // count = 2
count--;   // count = 1
```

**Rules:**
- Only works on `seed` and `tree` variables
- Cannot be chained: `x++++` is invalid
- Cannot combine with binary ops: `x++ + 1` needs separate statements"""),

    # ── 41. Unary negation (tilde) ────────────────────────────────
    ([
        "tilde operator negation",
        "negative number in GAL",
        "how to negate value",
        "minus sign replacement",
        "unary minus tilde",
        "make number negative",
     ],
     """**Unary negation** uses `~` (tilde) instead of `-`:
```
seed x = ~5;       // x = -5
tree y = ~3.14;    // y = -3.14
seed z = ~x;       // z = 5 (negates -5)
```

**Why tilde?** GAL uses `~` to avoid ambiguity with the subtraction operator `-`.

**In expressions:**
```
seed result = 10 + ~3;  // result = 7
seed abs = ~(~5);       // abs = 5
```

**Negative literals:**
```
seed neg = ~42;      // -42
tree negPi = ~3.14;  // -3.14
```"""),

    # ── 42. Compound assignment ───────────────────────────────────
    ([
        "compound assignment operators",
        "plus equals minus equals",
        "shorthand assignment",
        "x += 5 operator",
        "augmented assignment",
     ],
     """**Compound assignment operators:**

| Operator | Equivalent |
|----------|-----------|
| `x += 5` | `x = x + 5` |
| `x -= 3` | `x = x - 3` |
| `x *= 2` | `x = x * 2` |
| `x /= 4` | `x = x / 4` |
| `x %= 3` | `x = x % 3` |

```
seed score = 100;
score += 10;    // score = 110
score -= 25;    // score = 85
score *= 2;     // score = 170
score /= 10;    // score = 17
score %= 5;     // score = 2
```

**Rules:**
- Only works on numeric types (`seed`, `tree`)
- `%=` requires `seed` operands (modulo needs integers)
- Cannot use on `fertile` (const) variables"""),

    # ── 43. Format strings in plant() ─────────────────────────────
    ([
        "format string in plant",
        "placeholder curly braces",
        "string interpolation output",
        "plant with multiple values",
        "how to format output",
        "print formatted text",
     ],
     """**Format strings** in `plant()` use `{}` placeholders:
```
seed x = 10;
vine name = "Alice";

plant("Hello!");                        // plain text
plant("x = {}", x);                     // one placeholder
plant("{} + {} = {}", 3, 4, 3 + 4);     // multiple
plant("Name: {}, Age: {}", name, 25);   // mixed types
```

**Rules:**
- Number of `{}` placeholders must match the number of extra arguments
- Placeholders are replaced positionally (left to right)
- To print a literal `{`, use `\\{`; for `}`, use `\\}`

**Common mistake:**
```
// BAD:  plant("{} {} {}", a, b);    // 3 placeholders, 2 args
// GOOD: plant("{} {}", a, b);        // 2 placeholders, 2 args
```"""),

    # ── 44. Limits & constraints ──────────────────────────────────
    ([
        "limits constraints maximum GAL",
        "what are the GAL limits",
        "size restrictions boundaries",
        "maximum values allowed in GAL",
        "language limitations GAL",
        "max identifier length 15",
        "max loop iterations 10000",
        "maximum integer digits 8",
        "GAL restrictions constraints",
        "15 character limit identifier",
     ],
     """**GAL limits and constraints:**

| Constraint | Limit |
|------------|-------|
| Identifier length | 15 characters max |
| Integer literal | 8 digits max |
| Fractional part | 8 digits max |
| Runtime number | 16 digits max |
| Loop iterations | 10,000 max |
| `plant()` arguments | 15 max |
| Float display | 5 decimal places |

**Other constraints:**
- No `**` (exponent) operator
- No bitwise operators (single `&` or `|`)
- No inline bundle initialization (`bundle P p = {1,2}` is invalid)
- No `===` (strict equality)
- Arrays are 0-indexed
- `root()` function is required"""),

    # ── 45. Compiler stages ───────────────────────────────────────
    ([
        "how does compiler work",
        "compilation process stages",
        "lexer parser semantic interpreter",
        "compiler pipeline phases",
        "what happens when code runs",
        "how GAL compiles code",
     ],
     """**GAL compilation pipeline:**

```
Source Code → Lexer → Parser → Semantic Analyzer → Interpreter
                                    ↓
                             ICG (parallel)
```

**1. Lexer** (`lexer.py`) — Converts source text into tokens:
- Identifies keywords, operators, literals, identifiers
- Reports lexical errors (bad chars, unclosed strings)

**2. Parser** (`Gal_Parser.py`) — Checks syntax via LL(1) parsing:
- Validates token order against grammar rules
- Reports syntax errors (missing `;`, `}`, wrong keywords)

**3. Semantic Analyzer** (`GALsemantic.py`) — Builds AST and checks meaning:
- Type checking, scope validation, function signatures
- Reports semantic errors (type mismatch, undeclared variables)

**4. Interpreter** (`GALinterpreter.py`) — Executes the AST:
- Walks the tree and runs statements
- Reports runtime errors (division by zero, out of bounds)

**5. ICG** (`icg.py`) — Generates three-address code (parallel to semantic):
- Produces intermediate representation for analysis"""),

    # ── 46. Error: missing semicolons ─────────────────────────────
    ([
        "forgot semicolon error",
        "where do I put semicolons",
        "which statements need semicolons",
        "semicolon rules placement",
        "unexpected token expected semicolon",
     ],
     """**Semicolon rules in GAL:**

**Statements that need `;`:**
- Variable declarations: `seed x = 5;`
- Assignments: `x = 10;`
- Function calls: `myFunc(x);`
- `plant()` and `water()`: `plant("hello");`
- `reclaim`: `reclaim x;`
- `prune` and `skip`: `prune;`
- Increment/decrement: `x++;`
- Bundle definitions: `bundle Point { seed x; seed y; };`
- `tend...grow`: `} grow (cond);`

**Blocks that do NOT end with `;` after `}`:**
- `spring/bud/wither`: `spring (x > 0) { ... }`
- `cultivate`: `cultivate (...) { ... }`
- `grow`: `grow (cond) { ... }`
- `harvest`: `harvest (x) { ... }`
- Functions: `pollinate seed fn() { ... }`
- `root()`: `root() { ... }`"""),

    # ── 47. Error: type mismatches ────────────────────────────────
    ([
        "type mismatch error help",
        "cannot assign wrong type",
        "incompatible types problem",
        "type error how to fix",
        "wrong type assignment",
     ],
     """**Type mismatch errors** — when types don't match:

**Compatible types:** `seed` ↔ `tree` (automatic conversion)
```
seed x = 5;
tree y = x;    // OK — seed to tree
seed z = y;    // OK — tree to seed (truncates)
```

**Incompatible types:**
```
seed x = "hello";   // ERROR: vine → seed
vine s = 42;         // ERROR: seed → vine
leaf c = "abc";      // ERROR: vine → leaf
branch b = 5;        // ERROR: seed → branch
```

**How to fix:**
1. Use the correct type: `vine s = "hello";`
2. Use type casting: `vine s = (vine)42;`
3. Check your variable declarations match your values

**In operations:**
- `%` requires both operands to be `seed`
- `!` only works on `branch`
- Comparisons require compatible types"""),

    # ── 48. Error: undeclared variables ────────────────────────────
    ([
        "variable not declared error",
        "undefined undeclared variable",
        "forgot to declare variable",
        "used before declaration fix",
        "variable not found scope",
     ],
     """**"Variable not declared" error:**

**Cause:** Using a variable name that hasn't been declared yet.

**Common scenarios:**
```
// 1. Forgot to declare:
plant(x);          // ERROR: x not declared
// Fix: seed x = 10; plant(x);

// 2. Typo in variable name:
seed count = 5;
plant(cont);       // ERROR: 'cont' not declared (typo!)
// Fix: plant(count);

// 3. Out of scope:
spring (sunshine) {
    seed temp = 42;
}
plant(temp);       // ERROR: temp not visible here
// Fix: declare temp before the spring block

// 4. Wrong order:
plant(x);          // ERROR: used before declaration
seed x = 10;
// Fix: move declaration before use
```"""),

    # ── 49. Error: wrong C keywords ───────────────────────────────
    ([
        "used wrong keyword from C",
        "if instead of spring",
        "for instead of cultivate",
        "C keyword not working",
        "not a GAL keyword error",
        "converted from C not working",
     ],
     """**"Not a GAL keyword" error:**

GAL uses botanical-themed keywords. If you use C/Java/Python keywords, the compiler will suggest the correct GAL equivalent.

**Most common mistakes:**

| You wrote | Should be | Category |
|-----------|-----------|----------|
| `if` | `spring` | Conditional |
| `else` | `wither` | Conditional |
| `for` | `cultivate` | Loop |
| `while` | `grow` | Loop |
| `int` | `seed` | Type |
| `float` | `tree` | Type |
| `string` | `vine` | Type |
| `return` | `reclaim` | Return |
| `break` | `prune` | Control |
| `continue` | `skip` | Control |
| `printf`/`print` | `plant` | Output |
| `scanf`/`input` | `water` | Input |
| `struct` | `bundle` | Struct |

Tip: Use the keyword reference for the complete mapping."""),

    # ── 50. Error: fertile (const) issues ─────────────────────────
    ([
        "fertile constant error",
        "cannot reassign fertile",
        "constant not initialized",
        "fertile must be initialized",
        "modify const variable error",
     ],
     """**`fertile` (constant) errors:**

**Error: "Fertile variables must be initialized"**
```
// BAD:
fertile seed MAX;
// FIX:
fertile seed MAX = 100;
```

**Error: "Cannot be re-assigned"**
```
fertile seed MAX = 100;
MAX = 200;  // ERROR!
// FIX: Don't reassign. Use a non-fertile variable if the value needs to change:
seed max = 100;
max = 200;  // OK
```

**Error: "Multiple fertile declaration is not allowed"**
```
// BAD:
fertile seed A = 1, B = 2;
// FIX: Declare separately:
fertile seed A = 1;
fertile seed B = 2;
```

**Rules:**
- Only literal values (no expressions): `fertile seed X = 2 + 3;` is invalid
- `fertile` goes before the type: `fertile seed`, not `seed fertile`"""),

    # ── 51. Example: Factorial / recursion ─────────────────────────
    ([
        "factorial example program",
        "recursive example code",
        "factorial GAL code",
        "recursion complete example",
     ],
     """**Example: Factorial calculator (recursive)**
```
pollinate seed factorial(seed n) {
    spring (n <= 1) {
        reclaim 1;
    } wither {
        reclaim n * factorial(n - 1);
    }
}

root() {
    plant("Enter a number:");
    seed num = water(seed);
    plant("{}! = {}", num, factorial(num));
    reclaim;
}
```

**Example: Fibonacci sequence (iterative)**
```
root() {
    seed n = water(seed);
    seed a = 0;
    seed b = 1;

    cultivate (seed i = 0; i < n; i++) {
        plant(a);
        seed temp = a + b;
        a = b;
        b = temp;
    }
    reclaim;
}
```"""),

    # ── 52. Example: Array operations ─────────────────────────────
    ([
        "array operations example",
        "sum of array elements",
        "find element in array",
        "array manipulation code",
        "array example program",
     ],
     """**Example: Array sum**
```
root() {
    seed arr[] = {10, 20, 30, 40, 50};
    seed sum = 0;
    cultivate (seed i = 0; i < TS(arr); i++) {
        sum += arr[i];
    }
    plant("Sum = {}", sum);  // 150
    reclaim;
}
```

**Example: Find maximum**
```
root() {
    seed arr[] = {3, 7, 1, 9, 4};
    seed max = arr[0];
    cultivate (seed i = 1; i < TS(arr); i++) {
        spring (arr[i] > max) {
            max = arr[i];
        }
    }
    plant("Max = {}", max);  // 9
    reclaim;
}
```

**Example: Linear search**
```
root() {
    seed arr[] = {5, 10, 15, 20, 25};
    seed target = 15;
    seed found = ~1;
    cultivate (seed i = 0; i < TS(arr); i++) {
        spring (arr[i] == target) {
            found = i;
            prune;
        }
    }
    spring (found != ~1) {
        plant("Found at index {}", found);
    } wither {
        plant("Not found");
    }
    reclaim;
}
```"""),

    # ── 53. Example: Bubble sort ──────────────────────────────────
    ([
        "sorting example program",
        "bubble sort GAL code",
        "sort an array numbers",
        "sorting algorithm example",
        "arrange elements in order",
     ],
     """**Example: Bubble sort**
```
root() {
    seed arr[] = {64, 34, 25, 12, 22, 11, 90};
    seed n = TS(arr);

    cultivate (seed i = 0; i < n - 1; i++) {
        cultivate (seed j = 0; j < n - i - 1; j++) {
            spring (arr[j] > arr[j + 1]) {
                // Swap
                seed temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }

    plant("Sorted:");
    cultivate (seed i = 0; i < n; i++) {
        plant(arr[i]);
    }
    reclaim;
}
```"""),

    # ── 54. Example: Bundle usage ─────────────────────────────────
    ([
        "bundle struct example program",
        "complete bundle example",
        "struct usage code sample",
        "bundle with functions example",
     ],
     """**Example: Student records with bundles**
```
bundle Student {
    vine name;
    seed score;
};

pollinate empty printStudent(vine n, seed s) {
    plant("Name: {}, Score: {}", n, s);
    reclaim;
}

pollinate seed getAverage(seed a, seed b, seed c) {
    reclaim (a + b + c) / 3;
}

root() {
    bundle Student s1;
    s1.name = "Alice";
    s1.score = 95;

    bundle Student s2;
    s2.name = "Bob";
    s2.score = 87;

    printStudent(s1.name, s1.score);
    printStudent(s2.name, s2.score);

    seed avg = getAverage(s1.score, s2.score, 90);
    plant("Average: {}", avg);
    reclaim;
}
```"""),
]


# ═══════════════════════════════════════════════════════════════════════
# Sentence-Transformers (all-mpnet-base-v2) — lazy-loaded on first query
# ═══════════════════════════════════════════════════════════════════════

_st_model = None
_phrase_embeddings = None
_phrase_topic_idx = []
_responses = []
_last_topic_idx = None          # track last matched topic for follow-ups
_last_query = ""                # last user message for dedup


# ── GAL synonym map: C/common terms → GAL equivalents ────────────────
_SYNONYMS = {
    "int":       "seed",    "integer":    "seed",
    "float":     "tree",    "double":     "tree",   "decimal": "tree",
    "char":      "leaf",    "character":  "leaf",
    "string":    "vine",    "text":       "vine",   "str": "vine",
    "bool":      "branch data type",  "boolean":    "branch data type",
    "void":      "empty",
    "print":     "plant",   "output":     "plant",  "display": "plant",  "log": "plant",
    "input":     "water",   "read":       "water",  "scanf": "water",    "cin": "water",
    "for":       "cultivate",  "for loop":  "cultivate", "while":   "grow",  "while loop": "grow",  "do while": "tend do-while",  "do-while": "tend do-while",
    "if":        "spring",  "else":       "wither", "elif": "bud",       "else if": "bud",
    "switch":    "harvest", "case":       "pick",
    "function":  "pollinate", "func":     "pollinate", "method": "pollinate", "return": "reclaim",
    "main":      "root",    "entry point":"root",
    "struct":    "bundle",  "class":      "bundle", "object": "bundle",  "record": "bundle",
    "true":      "sunshine","false":      "frost",
    "array":     "array declaration", "list": "array",
    "cast":      "type casting", "convert": "type casting", "conversion": "type casting",
    "concatenate":"backtick string concat", "concat": "backtick string concat",
    "comment":   "comment annotation",
    "append":    "array append built-in", "remove": "array remove built-in",
    "escape":    "escape sequence backslash",
    "scope":     "local global scope variable visibility",
    "constant":  "fertile const immutable",
    "recursion": "recursive function calls itself",
    "precedence":"operator precedence order evaluation",
    "format":    "format string placeholder curly braces",
    "limit":     "limits constraints maximum",
    "compile":   "compiler stages lexer parser",
    "length":    "ts array length size",
    "split":     "taper split string characters",
    "negative":  "tilde negation unary",
    "increment": "increment prefix postfix",
    "decrement": "decrement prefix postfix",
}


# ── Greeting / meta patterns ─────────────────────────────────────────

_GREETING_PATTERNS = [
    (_re.compile(r"^\s*(hi|hello|hey|howdy|sup|yo|greetings|good\s*(morning|afternoon|evening))\b", _re.I),
     "Hey there! I'm the GAL AI Assistant. Ask me anything about GAL — data types, loops, functions, arrays, I/O, and more!"),
    (_re.compile(r"^\s*(thanks?|thank\s*you|ty|thx|cheers)\b", _re.I),
     "You're welcome! Feel free to ask more about GAL anytime."),
    (_re.compile(r"^\s*(bye|goodbye|see\s*ya|later|cya)\b", _re.I),
     "Goodbye! Happy coding with GAL! 🌱"),
    (_re.compile(r"\b(what can you do|help me|what do you know|how can you help)\b", _re.I),
     None),  # None → return _DEFAULT_RESPONSE (the help menu)
    (_re.compile(r"^\s*(who are you|what are you)\b", _re.I),
     "I'm the GAL AI Assistant — I help with GAL syntax, concepts, and debugging. Ask me about data types, loops, functions, arrays, or anything else in GAL!"),
]


def _encode(texts):
    """Encode texts using sentence-transformers (returns L2-normalised embeddings)."""
    return _st_model.encode(texts, normalize_embeddings=True, show_progress_bar=False)


def _ensure_model():
    """Load sentence-transformers model and encode training phrases on first call."""
    global _st_model, _phrase_embeddings, _phrase_topic_idx, _responses
    if _st_model is not None:
        return

    from sentence_transformers import SentenceTransformer

    _st_model = SentenceTransformer("all-mpnet-base-v2")

    _phrase_topic_idx = []
    _responses = []
    all_phrases = []

    for topic_idx, (phrases, response) in enumerate(_KNOWLEDGE_BASE):
        _responses.append(response)
        for p in phrases:
            all_phrases.append(p)
            _phrase_topic_idx.append(topic_idx)

    _phrase_embeddings = _encode(all_phrases)


# Default fallback when no topic is similar enough
_DEFAULT_RESPONSE = """I can help with GAL syntax and concepts! Try asking about:
- **Data types**: seed, tree, leaf, vine, branch
- **Variables**: declarations, constants (`fertile`), scope rules
- **Loops**: cultivate (for), grow (while), tend...grow (do-while)
- **Conditions**: spring (if), bud (else if), wither (else)
- **Functions**: pollinate, reclaim, root(), recursion
- **I/O**: plant() (print), water() (input), format strings
- **Arrays**: declaration, 2D arrays, built-ins (append, insert, remove, TS)
- **Bundles**: struct-like types, nested bundles, array of bundles
- **Type casting**: `(seed)`, `(tree)`, `(vine)`, etc.
- **Operators**: arithmetic, comparison, logical, precedence
- **Built-ins**: TS() (length), taper() (split), append/insert/remove
- **Errors**: paste any compiler error for a detailed explanation!

Or ask for "keyword reference", "example program", or "how does the compiler work"!

*Note: I'm running in offline mode right now. For more detailed help, try again later when the AI service is available.*"""


def _expand_query(text):
    """Inject GAL synonyms into the query so the model sees both vocabularies."""
    words = text.lower().split()
    extras = set()
    for w in words:
        if w in _SYNONYMS:
            extras.add(_SYNONYMS[w])
    # Also check 2-word combos (e.g. "else if" → "bud")
    lower = text.lower()
    for phrase, replacement in _SYNONYMS.items():
        if " " in phrase and phrase in lower:
            extras.add(replacement)
    if extras:
        return text + " " + " ".join(extras)
    return text


def fallback_reply(user_message):
    """Hybrid fallback: greeting → rule engine → ONNX retriever → default."""
    import numpy as np
    global _last_topic_idx, _last_query

    msg = user_message.strip()

    # ── Layer 0: Greeting / meta patterns ─────────────────────────
    for pattern, response in _GREETING_PATTERNS:
        if pattern.search(msg):
            return response if response else _DEFAULT_RESPONSE

    if not msg or len(msg) < 4:
        return _DEFAULT_RESPONSE

    # ── Layer 1: Rule Engine — exact compiler error matching ──────
    rule_match = _rule_engine_match(msg)
    if rule_match:
        _last_query = msg
        return rule_match

    # ── Layer 2: ONNX Retriever — semantic similarity search ──────
    _ensure_model()

    # Synonym expansion
    expanded = _expand_query(msg)

    # Follow-up detection — only trigger on short pronoun/reference queries
    is_followup = (
        len(msg.split()) <= 3
        and _last_query
        and any(w in msg.lower() for w in ["it", "that", "this", "those", "them", "more", "also"])
    )
    if is_followup and _last_query:
        expanded = _last_query + " " + expanded

    # Encode and score
    query_emb = _encode([expanded])
    scores = np.dot(_phrase_embeddings, query_emb.T).flatten()

    # Get top-2 topic scores (deduped by topic)
    topic_best = {}
    for i, score in enumerate(scores):
        tidx = _phrase_topic_idx[i]
        if tidx not in topic_best or score > topic_best[tidx]:
            topic_best[tidx] = float(score)

    ranked = sorted(topic_best.items(), key=lambda x: -x[1])
    best_idx, best_score = ranked[0]

    if best_score < _THRESHOLD:
        _last_query = msg
        return _DEFAULT_RESPONSE

    # Multi-topic blending
    result = _responses[best_idx]
    if len(ranked) >= 2:
        second_idx, second_score = ranked[1]
        if second_score >= _THRESHOLD and (best_score - second_score) < 0.05:
            result += "\n\n---\n\n" + _responses[second_idx]

    _last_topic_idx = best_idx
    _last_query = msg
    return result
