
# AUTO: Imports a module used by this file.
import re as _re

# AUTO: Sets `_THRESHOLD`.
_THRESHOLD = 0.35


# AUTO: Defines function `_structured_error`.
def _structured_error(stage, cause, rule="", fix="", explanation=""):
    # AUTO: Sets `parts`.
    parts = [f"**Stage:** {stage}", f"**Cause:** {cause}"]
    # AUTO: Checks this condition.
    if rule:
        # AUTO: Appends a value to a list.
        parts.append(f"**Rule:** {rule}")
    # AUTO: Checks this condition.
    if fix:
        # AUTO: Appends a value to a list.
        parts.append(f"**Fix:**\n```\n{fix}\n```")
    # AUTO: Checks this condition.
    if explanation:
        # AUTO: Appends a value to a list.
        parts.append(explanation)
    # AUTO: Returns this result to the caller.
    return "\n\n".join(parts)


# AUTO: Defines function `_lexer_err`.
def _lexer_err(cause, rule, fix, explanation=""):
    # AUTO: Returns this result to the caller.
    return _structured_error("Lexical Analysis (Lexer)", cause, rule, fix, explanation)

# AUTO: Defines function `_parser_err`.
def _parser_err(cause, rule, fix, explanation=""):
    # AUTO: Returns this result to the caller.
    return _structured_error("Syntax Analysis (Parser)", cause, rule, fix, explanation)

# AUTO: Defines function `_semantic_err`.
def _semantic_err(cause, rule, fix, explanation=""):
    # AUTO: Returns this result to the caller.
    return _structured_error("Semantic Analysis", cause, rule, fix, explanation)

# AUTO: Defines function `_runtime_err`.
def _runtime_err(cause, rule, fix, explanation=""):
    # AUTO: Returns this result to the caller.
    return _structured_error("Runtime (Interpreter)", cause, rule, fix, explanation)


# AUTO: Sets `_ERROR_PATTERNS`.
_ERROR_PATTERNS = [

    # AUTO: Calls `function`.
    (_re.compile(r"Identifier exceeds maximum length of 15 characters", _re.I),
     # AUTO: Executes this statement.
     _lexer_err(
         # AUTO: Executes this statement.
         "An identifier (variable or function name) exceeded 15 characters.",
         # AUTO: Executes this statement.
         "Identifiers must be at most 15 characters long.",
         # AUTO: Sets `"// BAD:  seed thisIsWayTooLong`.
         "// BAD:  seed thisIsWayTooLong = 5;\n// GOOD: seed shortName = 5;",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Integer exceeds maximum of 8 digits", _re.I),
     # AUTO: Executes this statement.
     _lexer_err(
         # AUTO: Executes this statement.
         "An integer literal has more than 8 digits.",
         # AUTO: Executes this statement.
         "Integer literals are limited to 8 digits.",
         # AUTO: Sets `"// BAD:  seed x`.
         "// BAD:  seed x = 123456789;\n// GOOD: seed x = 12345678;",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Fractional part exceeds maximum of 8 digits", _re.I),
     # AUTO: Executes this statement.
     _lexer_err(
         # AUTO: Executes this statement.
         "A float literal's decimal part has more than 8 digits.",
         # AUTO: Executes this statement.
         "Fractional portions are limited to 8 digits.",
         # AUTO: Sets `"// BAD:  tree x`.
         "// BAD:  tree x = 3.123456789;\n// GOOD: tree x = 3.12345678;",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Missing closing ['\"].*string literal", _re.I),
     # AUTO: Executes this statement.
     _lexer_err(
         # AUTO: Executes this statement.
         "A string literal is missing its closing double quote.",
         # AUTO: Executes this statement.
         "All strings must be enclosed in double quotes.",
         # AUTO: Sets `'// BAD:  vine s`.
         '// BAD:  vine s = "hello;\n// GOOD: vine s = "hello";',
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Missing closing.*character literal", _re.I),
     # AUTO: Executes this statement.
     _lexer_err(
         # AUTO: Executes this statement.
         "A character literal is missing its closing single quote.",
         # AUTO: Executes this statement.
         "Character literals use single quotes.",
         # AUTO: Sets `"// BAD:  leaf c`.
         "// BAD:  leaf c = 'A;\n// GOOD: leaf c = 'A';",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Character literal must contain exactly one character", _re.I),
     # AUTO: Executes this statement.
     _lexer_err(
         # AUTO: Executes this statement.
         "A character literal contains more than one character or is empty.",
         # AUTO: Executes this statement.
         "Character literals must be exactly one character.",
         # AUTO: Sets `"// BAD:  leaf c`.
         "// BAD:  leaf c = 'AB';\n// GOOD: leaf c = 'A';\n// For text use vine: vine s = \"AB\";",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Illegal Character '(.)'", _re.I),
     # AUTO: Executes this statement.
     lambda m: _lexer_err(
         # AUTO: Executes this statement.
         f"The character '{m.group(1)}' is not valid in GAL.",
         # AUTO: Executes this statement.
         "Only recognized operators, delimiters, and alphanumerics are allowed.",
         # AUTO: Executes this statement.
         f"Remove or replace the '{m.group(1)}' character.",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Identifiers cannot start with a number", _re.I),
     # AUTO: Executes this statement.
     _lexer_err(
         # AUTO: Executes this statement.
         "A variable name starts with a digit.",
         # AUTO: Executes this statement.
         "Identifiers must start with a letter (a-z, A-Z).",
         # AUTO: Sets `"// BAD:  seed 2count`.
         "// BAD:  seed 2count = 0;\n// GOOD: seed count2 = 0;",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Invalid escape sequence", _re.I),
     # AUTO: Executes this statement.
     _lexer_err(
         # AUTO: Executes this statement.
         "An unrecognized escape sequence was used in a string.",
         # AUTO: Executes this statement.
         "Valid escapes: \\n, \\t, \\\\, \\\", \\{, \\}",
         # AUTO: Sets `'// BAD:  vine s`.
         '// BAD:  vine s = "hello\\x";\n// GOOD: vine s = "hello\\n";',
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Missing closing '\*/'.*multi-line comment", _re.I),
     # AUTO: Executes this statement.
     _lexer_err(
         # AUTO: Executes this statement.
         "A multi-line comment was opened with /* but never closed.",
         # AUTO: Executes this statement.
         "Multi-line comments must be closed with */.",
         # AUTO: Executes this statement.
         "/* This is a comment */  // Correct\n/* Unclosed comment      // ERROR",
     # AUTO: Closes the current grouped code/data.
     )),


    # AUTO: Calls `function`.
    (_re.compile(r"'===' is not valid", _re.I),
     # AUTO: Executes this statement.
     _parser_err(
         # AUTO: Executes this statement.
         "Triple equals `===` is not a GAL operator.",
         # AUTO: Executes this statement.
         "Use `==` for equality comparison.",
         # AUTO: Executes this statement.
         "// BAD:  spring (x === 5) { ... }\n// GOOD: spring (x == 5) { ... }",
         # AUTO: Executes this statement.
         "GAL does not have strict equality like JavaScript.",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"'&' is not valid.*Use '&&'", _re.I),
     # AUTO: Executes this statement.
     _parser_err(
         # AUTO: Executes this statement.
         "Single `&` is not valid in GAL.",
         # AUTO: Executes this statement.
         "Use `&&` for logical AND (GAL has no bitwise operators).",
         # AUTO: Executes this statement.
         "// BAD:  spring (a & b) { ... }\n// GOOD: spring (a && b) { ... }",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"'\|' is not valid.*Use '\|\|'", _re.I),
     # AUTO: Executes this statement.
     _parser_err(
         # AUTO: Executes this statement.
         "Single `|` is not valid in GAL.",
         # AUTO: Executes this statement.
         "Use `||` for logical OR (GAL has no bitwise operators).",
         # AUTO: Executes this statement.
         "// BAD:  spring (a | b) { ... }\n// GOOD: spring (a || b) { ... }",
     # AUTO: Closes the current grouped code/data.
     )),


    # AUTO: Calls `function`.
    (_re.compile(r"'(\w+)' is not a GAL keyword\.\s*Use '(\w+)' instead", _re.I),
     # AUTO: Executes this statement.
     lambda m: _parser_err(
         # AUTO: Executes this statement.
         f"`{m.group(1)}` is not a GAL keyword.",
         # AUTO: Executes this statement.
         f"Use `{m.group(2)}` instead of `{m.group(1)}`.",
         # AUTO: Executes this statement.
         f"// BAD:  {m.group(1)} ...\n// GOOD: {m.group(2)} ...",
         # AUTO: Executes this statement.
         "GAL uses botanical-themed keywords. See the keyword reference for all mappings.",
     # AUTO: Closes the current grouped code/data.
     )),


    # AUTO: Calls `function`.
    (_re.compile(r"Expected\s*['\"]?;['\"]?|Unexpected token.*Expected\s*['\"]?;['\"]?", _re.I),
     # AUTO: Executes this statement.
     _parser_err(
         # AUTO: Executes this statement.
         "A statement is missing its terminating semicolon.",
         # AUTO: Executes this statement.
         "Every statement must end with `;`.",
         # AUTO: Sets `"// BAD:  seed x`.
         "// BAD:  seed x = 5\n// GOOD: seed x = 5;",
         # AUTO: Executes this statement.
         "Check the line in the error — the semicolon is usually needed at the end.",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Missing closing brace|Expected\s*'}'", _re.I),
     # AUTO: Executes this statement.
     _parser_err(
         # AUTO: Executes this statement.
         "A code block is missing its closing brace `}`.",
         # AUTO: Executes this statement.
         "Every `{` must have a matching `}`.",
         # AUTO: Executes this statement.
         "spring (x > 0) {\n    plant(\"positive\");\n}  // <-- don't forget this",
         # AUTO: Executes this statement.
         "Count your opening and closing braces. Nested blocks are a common source of this error.",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Empty block.*Expected at least one statement", _re.I),
     # AUTO: Executes this statement.
     _parser_err(
         # AUTO: Executes this statement.
         "An empty block `{}` was found.",
         # AUTO: Executes this statement.
         "Every block must contain at least one statement.",
         # AUTO: Executes this statement.
         '// BAD:  spring (x > 0) { }\n// GOOD: spring (x > 0) { plant("yes"); }',
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Local declarations must appear first in the block", _re.I),
     # AUTO: Executes this statement.
     _parser_err(
         # AUTO: Executes this statement.
         "A local declaration appears after executable code in the same block.",
         # AUTO: Executes this statement.
         "GrowALanguage uses declaration-first C-style blocks: declare local variables, arrays, constants, and bundle variables before statements in that block.",
         # AUTO: Sets `'// BAD:  plant("start"); seed x`.
         '// BAD:  plant("start"); seed x = 5;\n// GOOD: seed x = 5; plant("start");',
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"expected 'reclaim;' before", _re.I),
     # AUTO: Executes this statement.
     _parser_err(
         # AUTO: Executes this statement.
         "The function is missing its required final `reclaim` statement.",
         # AUTO: Executes this statement.
         "The CFG requires every function, including `root()`, to end with `reclaim;`.",
         # AUTO: Executes this statement.
         'root() {\n    plant("Done");\n    reclaim;\n}',
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Unreachable code after 'reclaim'", _re.I),
     # AUTO: Executes this statement.
     _parser_err(
         # AUTO: Executes this statement.
         "Code appears after a `reclaim` (return) statement.",
         # AUTO: Executes this statement.
         "Statements after `reclaim` will never execute.",
         # AUTO: Executes this statement.
         "pollinate seed add(seed a, seed b) {\n    reclaim a + b;\n    // Remove any code below reclaim\n}",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Increment/decrement operators cannot be chained", _re.I),
     # AUTO: Executes this statement.
     _parser_err(
         # AUTO: Executes this statement.
         "Attempted to chain `++` or `--` operators.",
         # AUTO: Executes this statement.
         "`++` and `--` cannot be chained.",
         # AUTO: Executes this statement.
         "// BAD:  x++++;\n// GOOD: x++;\n//       x++;  // separate statements",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Missing return type after 'pollinate'", _re.I),
     # AUTO: Executes this statement.
     _parser_err(
         # AUTO: Executes this statement.
         "A function is missing its return type.",
         # AUTO: Executes this statement.
         "Functions need a return type between `pollinate` and the name.",
         # AUTO: Executes this statement.
         "// BAD:  pollinate add(seed a, seed b) { ... }\n// GOOD: pollinate seed add(seed a, seed b) { ... }",
         # AUTO: Executes this statement.
         "Use `empty` for functions that don't return a value.",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Missing type for parameter '(\w+)'", _re.I),
     # AUTO: Executes this statement.
     lambda m: _parser_err(
         # AUTO: Executes this statement.
         f"Parameter `{m.group(1)}` is missing its type.",
         # AUTO: Executes this statement.
         "Each function parameter must have a type.",
         # AUTO: Executes this statement.
         f"// BAD:  pollinate seed fn({m.group(1)}) {{ ... }}\n// GOOD: pollinate seed fn(seed {m.group(1)}) {{ ... }}",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Unexpected token.*after program end", _re.I),
     # AUTO: Executes this statement.
     _parser_err(
         # AUTO: Executes this statement.
         "Code found after `root() { ... }` ended.",
         # AUTO: Executes this statement.
         "All code must be inside functions or global declarations before `root()`.",
         # AUTO: Executes this statement.
         "pollinate seed add(seed a, seed b) {\n    reclaim a + b;\n}\n\nroot() {\n    plant(add(1, 2));\n    reclaim;\n}",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Type mismatch in declaration of '(\w+)'.*declared as '(\w+)' but assigned '(\w+)'", _re.I),
     # AUTO: Executes this statement.
     lambda m: _parser_err(
         # AUTO: Executes this statement.
         f"Variable `{m.group(1)}` declared as `{m.group(2)}` but assigned a `{m.group(3)}` value.",
         # AUTO: Executes this statement.
         "The value type must match the declared variable type.",
         # AUTO: Sets `f"// Use the correct type or value\n{m.group(2)} {m.group(1)}`.
         f"// Use the correct type or value\n{m.group(2)} {m.group(1)} = <correct_{m.group(2)}_value>;",
         # AUTO: Executes this statement.
         "`seed`↔`tree` are compatible. `leaf`, `vine`, `branch` are not interchangeable.",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Empty character literal.*must contain exactly one character", _re.I),
     # AUTO: Executes this statement.
     _parser_err(
         # AUTO: Executes this statement.
         "An empty character literal `''` was found.",
         # AUTO: Executes this statement.
         "Character literals must contain exactly one character.",
         # AUTO: Sets `"// BAD:  leaf c`.
         "// BAD:  leaf c = '';\n// GOOD: leaf c = 'A';",
     # AUTO: Closes the current grouped code/data.
     )),


    # AUTO: Calls `function`.
    (_re.compile(r"Variable '(\w+)' already declared", _re.I),
     # AUTO: Executes this statement.
     lambda m: _semantic_err(
         # AUTO: Executes this statement.
         f"Variable `{m.group(1)}` has already been declared in this scope.",
         # AUTO: Executes this statement.
         "Each variable name can only be declared once per scope.",
         # AUTO: Sets `f"seed {m.group(1)}`.
         f"seed {m.group(1)} = 10;  // Keep ONE declaration\n// seed {m.group(1)} = 20;  // Remove duplicate",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Variable '(\w+)' used before declaration", _re.I),
     # AUTO: Executes this statement.
     lambda m: _semantic_err(
         # AUTO: Executes this statement.
         f"Variable `{m.group(1)}` was used before being declared.",
         # AUTO: Executes this statement.
         "All variables must be declared before use.",
         # AUTO: Sets `f"seed {m.group(1)}`.
         f"seed {m.group(1)} = 0;     // Declare FIRST\nplant({m.group(1)});      // Then use",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Type Mismatch.*Cannot assign (\w+) to variable '(\w+)' of type (\w+)", _re.I),
     # AUTO: Executes this statement.
     lambda m: _semantic_err(
         # AUTO: Executes this statement.
         f"Cannot assign `{m.group(1)}` value to `{m.group(2)}` (type `{m.group(3)}`).",
         # AUTO: Executes this statement.
         "Assignment values must match the variable's declared type.",
         # AUTO: Sets `f"// Ensure the type matches:\n{m.group(3)} {m.group(2)}`.
         f"// Ensure the type matches:\n{m.group(3)} {m.group(2)} = <correct_value>;",
         # AUTO: Executes this statement.
         "`seed`↔`tree` are compatible. Other types must match exactly.",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Modulo operator '%' requires 'seed'.*operands", _re.I),
     # AUTO: Executes this statement.
     _semantic_err(
         # AUTO: Executes this statement.
         "The `%` (modulo) operator was used with non-integer operands.",
         # AUTO: Executes this statement.
         "Modulo requires both operands to be `seed` (integer).",
         # AUTO: Sets `"seed a`.
         "seed a = 10;\nseed b = 3;\nseed r = a % b;  // OK\n// tree x = 3.5 % 2;  // ERROR",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"'!' operator can only be used with 'branch'", _re.I),
     # AUTO: Executes this statement.
     _semantic_err(
         # AUTO: Executes this statement.
         "The `!` (NOT) operator was used on a non-boolean value.",
         # AUTO: Executes this statement.
         "`!` can only be applied to `branch` (boolean) values.",
         # AUTO: Sets `"branch flag`.
         "branch flag = sunshine;\nbranch opp = !flag;  // OK\n// seed x = !5;       // ERROR",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Function '(\w+)' is not (?:declared|defined)", _re.I),
     # AUTO: Executes this statement.
     lambda m: _semantic_err(
         # AUTO: Executes this statement.
         f"Function `{m.group(1)}` was called but never defined.",
         # AUTO: Executes this statement.
         "Functions must be defined with `pollinate` before `root()`.",
         # AUTO: Executes this statement.
         f"pollinate seed {m.group(1)}(seed x) {{\n    reclaim x * 2;\n}}\n\nroot() {{\n    plant({m.group(1)}(5));\n    reclaim;\n}}",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Function '(\w+)' expects (\d+) argument\(s\), got (\d+)", _re.I),
     # AUTO: Executes this statement.
     lambda m: _semantic_err(
         # AUTO: Executes this statement.
         f"Function `{m.group(1)}` expects {m.group(2)} argument(s) but got {m.group(3)}.",
         # AUTO: Executes this statement.
         "The number of arguments must match the function's parameter list.",
         # AUTO: Executes this statement.
         f"// Check the function definition and pass the correct number of arguments.",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Argument (\d+) of function '(\w+)': expected '(\w+)', got '(\w+)'", _re.I),
     # AUTO: Executes this statement.
     lambda m: _semantic_err(
         # AUTO: Executes this statement.
         f"Argument {m.group(1)} of `{m.group(2)}` should be `{m.group(3)}`, got `{m.group(4)}`.",
         # AUTO: Executes this statement.
         "Argument types must match the function's parameter types.",
         # AUTO: Executes this statement.
         f"// Ensure argument {m.group(1)} is of type `{m.group(3)}`.",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"empty function must not return any value", _re.I),
     # AUTO: Executes this statement.
     _semantic_err(
         # AUTO: Executes this statement.
         "A function declared as `empty` (void) is returning a value.",
         # AUTO: Executes this statement.
         "Empty functions must use `reclaim;` without a value.",
         # AUTO: Executes this statement.
         "pollinate empty greet() {\n    plant(\"Hello!\");\n    reclaim;  // No value after reclaim\n}",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"'prune' used outside a loop or switch", _re.I),
     # AUTO: Executes this statement.
     _semantic_err(
         # AUTO: Executes this statement.
         "`prune` (break) was used outside of a loop or switch.",
         # AUTO: Executes this statement.
         "`prune` can only be used inside loops or `harvest` blocks.",
         # AUTO: Executes this statement.
         "cultivate (seed i = 0; i < 10; i++) {\n    spring (i == 5) {\n        prune;  // OK — inside loop\n    }\n}",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"'skip' used outside a loop", _re.I),
     # AUTO: Executes this statement.
     _semantic_err(
         # AUTO: Executes this statement.
         "`skip` (continue) was used outside of a loop.",
         # AUTO: Executes this statement.
         "`skip` can only be used inside loops.",
         # AUTO: Executes this statement.
         "cultivate (seed i = 0; i < 10; i++) {\n    spring (i % 2 == 0) { skip; }\n    plant(i);  // prints odd numbers\n}",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Variable '(\w+)' is declared as fertile and cannot be re-assigned", _re.I),
     # AUTO: Executes this statement.
     lambda m: _semantic_err(
         # AUTO: Executes this statement.
         f"Attempted to reassign fertile (const) variable `{m.group(1)}`.",
         # AUTO: Executes this statement.
         "Variables declared with `fertile` cannot be changed.",
         # AUTO: Sets `f"fertile seed {m.group(1)}`.
         f"fertile seed {m.group(1)} = 100;\n// {m.group(1)} = 200;  // ERROR!\n// Use a non-fertile variable if it needs to change.",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Fertile variables must be initialized", _re.I),
     # AUTO: Executes this statement.
     _semantic_err(
         # AUTO: Executes this statement.
         "A `fertile` (const) variable was declared without an initial value.",
         # AUTO: Executes this statement.
         "Fertile variables must be assigned a value at declaration.",
         # AUTO: Sets `"// BAD:  fertile seed MAX;\n// GOOD: fertile seed MAX`.
         "// BAD:  fertile seed MAX;\n// GOOD: fertile seed MAX = 100;",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"(spring|bud|grow|tend|cultivate) condition must be branch, got (\w+)", _re.I),
     # AUTO: Executes this statement.
     lambda m: _semantic_err(
         # AUTO: Executes this statement.
         f"The `{m.group(1)}` condition must be `branch` (boolean), got `{m.group(2)}`.",
         # AUTO: Executes this statement.
         "Conditions must evaluate to a boolean.",
         # AUTO: Executes this statement.
         f"// BAD:  {m.group(1)} (x) {{ ... }}       // x is {m.group(2)}\n// GOOD: {m.group(1)} (x > 0) {{ ... }}   // comparison → branch",
         # AUTO: Executes this statement.
         "Use comparison operators (`==`, `!=`, `<`, `>`, `<=`, `>=`) to produce boolean values.",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"'harvest' expression must be 'seed'/'leaf'/'branch', not '(\w+)'", _re.I),
     # AUTO: Executes this statement.
     lambda m: _semantic_err(
         # AUTO: Executes this statement.
         f"The `harvest` (switch) expression is of type `{m.group(1)}`.",
         # AUTO: Executes this statement.
         "Switch expressions must be `seed`, `leaf`, or `branch`.",
         # AUTO: Sets `"seed choice`.
         "seed choice = water(seed);\nharvest (choice) {\n    variety 1: plant(\"One\"); prune;\n    soil: plant(\"Other\");\n}",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Duplicate 'variety' value", _re.I),
     # AUTO: Executes this statement.
     _semantic_err(
         # AUTO: Executes this statement.
         "Two `variety` (case) labels have the same value.",
         # AUTO: Executes this statement.
         "Each `variety` value must be unique.",
         # AUTO: Executes this statement.
         "harvest (x) {\n    variety 1: plant(\"One\"); prune;\n    variety 2: plant(\"Two\"); prune;  // Each unique\n    soil: plant(\"Other\");\n}",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Bundle type '(\w+)' is not defined", _re.I),
     # AUTO: Executes this statement.
     lambda m: _semantic_err(
         # AUTO: Executes this statement.
         f"Bundle type `{m.group(1)}` has not been defined.",
         # AUTO: Executes this statement.
         "Bundle types must be defined before use.",
         # AUTO: Sets `f"bundle {m.group(1)} {{\n    seed x;\n    seed y;\n}};\n\nbundle {m.group(1)} obj;\nobj.x`.
         f"bundle {m.group(1)} {{\n    seed x;\n    seed y;\n}};\n\nbundle {m.group(1)} obj;\nobj.x = 5;",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Exceeded maximum.*15 arguments in plant", _re.I),
     # AUTO: Executes this statement.
     _semantic_err(
         # AUTO: Executes this statement.
         "A `plant()` statement has more than 15 arguments.",
         # AUTO: Executes this statement.
         "`plant()` supports a maximum of 15 arguments.",
         # AUTO: Executes this statement.
         "// Split into multiple plant() calls if needed.",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Found (\d+) argument\(s\)\.\s*Expected (\d+) argument\(s\)", _re.I),
     # AUTO: Executes this statement.
     lambda m: _semantic_err(
         # AUTO: Executes this statement.
         f"`plant()` has {m.group(1)} argument(s) but the format string expects {m.group(2)}.",
         # AUTO: Executes this statement.
         "The number of `{{}}` placeholders must match the extra arguments.",
         # AUTO: Executes this statement.
         '// BAD:  plant("{} + {}", a);         // 2 placeholders, 1 arg\n// GOOD: plant("{} + {}", a, b);      // 2 placeholders, 2 args',
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Array size must be of type 'seed'", _re.I),
     # AUTO: Executes this statement.
     _semantic_err(
         # AUTO: Executes this statement.
         "A non-integer was used as an array size.",
         # AUTO: Executes this statement.
         "Array sizes must be `seed` (integer).",
         # AUTO: Executes this statement.
         "// BAD:  seed arr[3.5];\n// GOOD: seed arr[5];",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"List index must be of type 'seed', got '(\w+)'", _re.I),
     # AUTO: Executes this statement.
     lambda m: _semantic_err(
         # AUTO: Executes this statement.
         f"An array index of type `{m.group(1)}` was used instead of `seed`.",
         # AUTO: Executes this statement.
         "Array indices must be `seed` (integer).",
         # AUTO: Sets `"seed arr[]`.
         "seed arr[] = {10, 20, 30};\nseed i = 1;\nplant(arr[i]);  // OK: seed index",
     # AUTO: Closes the current grouped code/data.
     )),


    # AUTO: Calls `function`.
    (_re.compile(r"Division by zero", _re.I),
     # AUTO: Executes this statement.
     _runtime_err(
         # AUTO: Executes this statement.
         "A division or modulo by zero was attempted.",
         # AUTO: Executes this statement.
         "The divisor must not be zero.",
         # AUTO: Executes this statement.
         "seed a = 10;\nseed b = 0;\n// seed c = a / b;  // Runtime Error!\nspring (b != 0) {\n    seed c = a / b;  // Safe\n}",
         # AUTO: Executes this statement.
         "Always check that the divisor is non-zero before dividing.",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Infinite loop detected", _re.I),
     # AUTO: Executes this statement.
     _runtime_err(
         # AUTO: Executes this statement.
         "A loop exceeded the maximum iteration limit (10,000).",
         # AUTO: Executes this statement.
         "Loops are limited to 10,000 iterations.",
         # AUTO: Sets `"seed i`.
         "seed i = 0;\ngrow (i < 100) {\n    plant(i);\n    i++;  // Don't forget to update!\n}",
         # AUTO: Executes this statement.
         "Common cause: forgetting to update the loop variable so the condition never becomes false.",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Index '?(-?\d+)'? out of bounds for (?:list )?'?(\w+)'?", _re.I),
     # AUTO: Executes this statement.
     lambda m: _runtime_err(
         # AUTO: Executes this statement.
         f"Index `{m.group(1)}` is out of bounds for array `{m.group(2)}`.",
         # AUTO: Executes this statement.
         "Array indices must be between 0 and length-1.",
         # AUTO: Sets `f"// Keep a separate seed variable for the array size.\nseed size`.
         f"// Keep a separate seed variable for the array size.\nseed size = 3;\ncultivate (seed i = 0; i < size; i++) {{\n    plant({m.group(2)}[i]);\n}}",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Evaluated number exceeds maximum.*16 digits", _re.I),
     # AUTO: Executes this statement.
     _runtime_err(
         # AUTO: Executes this statement.
         "A computed number exceeded the 16-digit limit.",
         # AUTO: Executes this statement.
         "Numbers at runtime cannot exceed 16 digits.",
         # AUTO: Executes this statement.
         "// Use smaller values or break computations into steps.",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Condition must be a boolean.*Got '(.+)'", _re.I),
     # AUTO: Executes this statement.
     lambda m: _runtime_err(
         # AUTO: Executes this statement.
         f"A condition evaluated to `{m.group(1)}` instead of a boolean.",
         # AUTO: Executes this statement.
         "Conditions must be `sunshine` or `frost`.",
         # AUTO: Executes this statement.
         "// Use a comparison to produce a boolean:\nspring (x > 0) { ... }  // Correct",
     # AUTO: Closes the current grouped code/data.
     )),

    # AUTO: Calls `function`.
    (_re.compile(r"Variable '(\w+)' is not a list", _re.I),
     # AUTO: Executes this statement.
     lambda m: _runtime_err(
         # AUTO: Executes this statement.
         f"Attempted to index `{m.group(1)}`, which is not an array.",
         # AUTO: Executes this statement.
         "Only arrays can be indexed with `[]`.",
         # AUTO: Sets `f"// Declare as array:\nseed {m.group(1)}[5];  // Array\n// Not: seed {m.group(1)}`.
         f"// Declare as array:\nseed {m.group(1)}[5];  // Array\n// Not: seed {m.group(1)} = 5;  // Scalar",
     # AUTO: Closes the current grouped code/data.
     )),
# AUTO: Closes the current grouped code/data.
]


# AUTO: Defines function `_rule_engine_match`.
def _rule_engine_match(msg):
    # AUTO: Starts a loop over these values.
    for pattern, response in _ERROR_PATTERNS:
        # AUTO: Sets `m`.
        m = pattern.search(msg)
        # AUTO: Checks this condition.
        if m:
            # AUTO: Returns this result to the caller.
            return response(m) if callable(response) else response
    # AUTO: Returns this result to the caller.
    return None


# AUTO: Sets `_KNOWLEDGE_BASE`.
_KNOWLEDGE_BASE = [
    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "what are the data types",
        # AUTO: Executes this statement.
        "data types in GAL",
        # AUTO: Executes this statement.
        "seed tree leaf vine branch",
        # AUTO: Executes this statement.
        "integer float char string boolean",
        # AUTO: Executes this statement.
        "types of variables",
        # AUTO: Executes this statement.
        "what type should I use",
        # AUTO: Executes this statement.
        "type system",
        # AUTO: Executes this statement.
        "GAL types",
        # AUTO: Executes this statement.
        "int float double char string bool",
        # AUTO: Executes this statement.
        "the seed",
        # AUTO: Executes this statement.
        "what is seed",
        # AUTO: Executes this statement.
        "what is tree",
        # AUTO: Executes this statement.
        "what is leaf",
        # AUTO: Executes this statement.
        "what is vine",
        # AUTO: Executes this statement.
        "what is branch",
        # AUTO: Executes this statement.
        "give me code of seed",
        # AUTO: Executes this statement.
        "give me code of tree",
        # AUTO: Executes this statement.
        "show me seed",
        # AUTO: Executes this statement.
        "show me tree",
        # AUTO: Executes this statement.
        "show me vine",
        # AUTO: Executes this statement.
        "show me leaf",
        # AUTO: Executes this statement.
        "show me branch",
        # AUTO: Executes this statement.
        "code for seed",
        # AUTO: Executes this statement.
        "code for tree",
        # AUTO: Executes this statement.
        "code for vine",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "how to declare a variable",
        # AUTO: Executes this statement.
        "variable declaration",
        # AUTO: Executes this statement.
        "create a variable",
        # AUTO: Executes this statement.
        "initialize variable",
        # AUTO: Executes this statement.
        "define variable",
        # AUTO: Executes this statement.
        "constant fertile const",
        # AUTO: Executes this statement.
        "multiple variables",
        # AUTO: Executes this statement.
        "declare seed tree vine",
        # AUTO: Executes this statement.
        "the fertile",
        # AUTO: Executes this statement.
        "what is fertile",
        # AUTO: Executes this statement.
        "give me code of variable",
        # AUTO: Executes this statement.
        "show me variable declaration",
        # AUTO: Executes this statement.
        "how to make a variable",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "how to use arrays",
        # AUTO: Executes this statement.
        "array declaration",
        # AUTO: Executes this statement.
        "create an array",
        # AUTO: Executes this statement.
        "list in GAL",
        # AUTO: Executes this statement.
        "2d array multidimensional matrix",
        # AUTO: Executes this statement.
        "array index element access",
        # AUTO: Executes this statement.
        "arr bracket",
        # AUTO: Executes this statement.
        "array of integers",
        # AUTO: Executes this statement.
        "tell me about arrays",
        # AUTO: Executes this statement.
        "store multiple values in a variable",
        # AUTO: Executes this statement.
        "hold many items in a collection",
        # AUTO: Executes this statement.
        "iterate over array elements",
        # AUTO: Executes this statement.
        "go through each item in array",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "for loop",
        # AUTO: Executes this statement.
        "cultivate loop",
        # AUTO: Executes this statement.
        "what is cultivate",
        # AUTO: Executes this statement.
        "how to use cultivate",
        # AUTO: Executes this statement.
        "count from 0 to 10",
        # AUTO: Executes this statement.
        "iterate with index",
        # AUTO: Executes this statement.
        "loop with counter",
        # AUTO: Executes this statement.
        "for i in range",
        # AUTO: Executes this statement.
        "traditional for loop",
        # AUTO: Executes this statement.
        "cultivate",
        # AUTO: Executes this statement.
        "the cultivate",
        # AUTO: Executes this statement.
        "what is the cultivate",
        # AUTO: Executes this statement.
        "give me code of cultivate",
        # AUTO: Executes this statement.
        "show me cultivate",
        # AUTO: Executes this statement.
        "code for cultivate",
        # AUTO: Executes this statement.
        "how does cultivate work",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "while loop",
        # AUTO: Executes this statement.
        "grow loop",
        # AUTO: Executes this statement.
        "what is grow",
        # AUTO: Executes this statement.
        "how to use grow",
        # AUTO: Executes this statement.
        "what is while loop",
        # AUTO: Executes this statement.
        "while loop in GAL",
        # AUTO: Executes this statement.
        "loop while condition",
        # AUTO: Executes this statement.
        "repeat while true",
        # AUTO: Executes this statement.
        "loop until condition",
        # AUTO: Executes this statement.
        "keep looping",
        # AUTO: Executes this statement.
        "grow",
        # AUTO: Executes this statement.
        "the grow",
        # AUTO: Executes this statement.
        "what is the grow",
        # AUTO: Executes this statement.
        "give me code of grow",
        # AUTO: Executes this statement.
        "show me grow",
        # AUTO: Executes this statement.
        "code for grow",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "do while loop",
        # AUTO: Executes this statement.
        "do-while loop",
        # AUTO: Executes this statement.
        "tend grow do-while",
        # AUTO: Executes this statement.
        "what is tend",
        # AUTO: Executes this statement.
        "how to use tend",
        # AUTO: Executes this statement.
        "do while",
        # AUTO: Executes this statement.
        "what is do while",
        # AUTO: Executes this statement.
        "do while in GAL",
        # AUTO: Executes this statement.
        "loop at least once",
        # AUTO: Executes this statement.
        "execute then check",
        # AUTO: Executes this statement.
        "post-condition loop",
        # AUTO: Executes this statement.
        "tend",
        # AUTO: Executes this statement.
        "the tend",
        # AUTO: Executes this statement.
        "what is the tend",
        # AUTO: Executes this statement.
        "give me code of tend",
        # AUTO: Executes this statement.
        "show me tend",
        # AUTO: Executes this statement.
        "code for tend",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "how to make a loop",
        # AUTO: Executes this statement.
        "loop types in GAL",
        # AUTO: Executes this statement.
        "looping construct",
        # AUTO: Executes this statement.
        "all loops",
        # AUTO: Executes this statement.
        "what loops exist",
        # AUTO: Executes this statement.
        "what are the loops",
        # AUTO: Executes this statement.
        "types of loops",
        # AUTO: Executes this statement.
        "how many loops",
        # AUTO: Executes this statement.
        "list all loops",
        # AUTO: Executes this statement.
        "loop overview",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "if else condition",
        # AUTO: Executes this statement.
        "conditional statement",
        # AUTO: Executes this statement.
        "spring bud wither",
        # AUTO: Executes this statement.
        "how to use spring bud wither",
        # AUTO: Executes this statement.
        "if statement else if",
        # AUTO: Executes this statement.
        "check a condition",
        # AUTO: Executes this statement.
        "branching logic",
        # AUTO: Executes this statement.
        "compare values",
        # AUTO: Executes this statement.
        "decision making",
        # AUTO: Executes this statement.
        "if then else",
        # AUTO: Executes this statement.
        "spring",
        # AUTO: Executes this statement.
        "the spring",
        # AUTO: Executes this statement.
        "what is the spring",
        # AUTO: Executes this statement.
        "what is spring",
        # AUTO: Executes this statement.
        "bud",
        # AUTO: Executes this statement.
        "what is bud",
        # AUTO: Executes this statement.
        "wither",
        # AUTO: Executes this statement.
        "what is wither",
        # AUTO: Executes this statement.
        "give me code of spring",
        # AUTO: Executes this statement.
        "show me spring",
        # AUTO: Executes this statement.
        "code for spring",
        # AUTO: Executes this statement.
        "show me bud wither",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "switch case statement",
        # AUTO: Executes this statement.
        "harvest variety soil",
        # AUTO: Executes this statement.
        "switch multiple cases",
        # AUTO: Executes this statement.
        "select from options",
        # AUTO: Executes this statement.
        "menu selection choice",
        # AUTO: Executes this statement.
        "match value",
        # AUTO: Executes this statement.
        "harvest",
        # AUTO: Executes this statement.
        "the harvest",
        # AUTO: Executes this statement.
        "what is harvest",
        # AUTO: Executes this statement.
        "what is the harvest",
        # AUTO: Executes this statement.
        "variety",
        # AUTO: Executes this statement.
        "what is variety",
        # AUTO: Executes this statement.
        "soil",
        # AUTO: Executes this statement.
        "what is soil",
        # AUTO: Executes this statement.
        "give me code of harvest",
        # AUTO: Executes this statement.
        "show me harvest",
        # AUTO: Executes this statement.
        "code for harvest",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "how to create a function",
        # AUTO: Executes this statement.
        "function declaration definition",
        # AUTO: Executes this statement.
        "pollinate reclaim return",
        # AUTO: Executes this statement.
        "define a function",
        # AUTO: Executes this statement.
        "call a function",
        # AUTO: Executes this statement.
        "function parameters arguments",
        # AUTO: Executes this statement.
        "return value from function",
        # AUTO: Executes this statement.
        "void function empty",
        # AUTO: Executes this statement.
        "root main entry point",
        # AUTO: Executes this statement.
        "function with parameters",
        # AUTO: Executes this statement.
        "pollinate",
        # AUTO: Executes this statement.
        "the pollinate",
        # AUTO: Executes this statement.
        "what is pollinate",
        # AUTO: Executes this statement.
        "what is the pollinate",
        # AUTO: Executes this statement.
        "reclaim",
        # AUTO: Executes this statement.
        "what is reclaim",
        # AUTO: Executes this statement.
        "root",
        # AUTO: Executes this statement.
        "what is root",
        # AUTO: Executes this statement.
        "give me code of pollinate",
        # AUTO: Executes this statement.
        "show me pollinate",
        # AUTO: Executes this statement.
        "code for pollinate",
        # AUTO: Executes this statement.
        "give me code of function",
        # AUTO: Executes this statement.
        "show me root",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "how to read input",
        # AUTO: Executes this statement.
        "get user input",
        # AUTO: Executes this statement.
        "water input scanf stdin",
        # AUTO: Executes this statement.
        "read from keyboard",
        # AUTO: Executes this statement.
        "ask user for value",
        # AUTO: Executes this statement.
        "input a number string",
        # AUTO: Executes this statement.
        "water seed vine",
        # AUTO: Executes this statement.
        "read into variable",
        # AUTO: Executes this statement.
        "prompt user",
        # AUTO: Executes this statement.
        "water",
        # AUTO: Executes this statement.
        "the water",
        # AUTO: Executes this statement.
        "what is water",
        # AUTO: Executes this statement.
        "what is the water",
        # AUTO: Executes this statement.
        "give me code of water",
        # AUTO: Executes this statement.
        "show me water",
        # AUTO: Executes this statement.
        "code for water",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "how to print output",
        # AUTO: Executes this statement.
        "display show output",
        # AUTO: Executes this statement.
        "plant print printf",
        # AUTO: Executes this statement.
        "print a variable",
        # AUTO: Executes this statement.
        "format string placeholder",
        # AUTO: Executes this statement.
        "print text to screen",
        # AUTO: Executes this statement.
        "output a message",
        # AUTO: Executes this statement.
        "write to console",
        # AUTO: Executes this statement.
        "show result",
        # AUTO: Executes this statement.
        "plant",
        # AUTO: Executes this statement.
        "the plant",
        # AUTO: Executes this statement.
        "what is plant",
        # AUTO: Executes this statement.
        "what is the plant",
        # AUTO: Executes this statement.
        "give me code of plant",
        # AUTO: Executes this statement.
        "show me plant",
        # AUTO: Executes this statement.
        "code for plant",
     # AUTO: Closes the current grouped code/data.
     ],
     """**Output** uses `plant()` with format strings:
```
plant("Hello World!");
plant("x = {}", x);
plant("{} + {} = {}", a, b, a + b);
plant(num);                  // print a single value
```
Use `{}` as placeholders (like Python's `.format()`).

Backtick concatenation may join `vine` and `leaf` values in plant():
- `plant("Hello {}", name);` is valid formatting
- `plant("Hello " ` name);` is valid string concatenation"""),

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "struct bundle record",
        # AUTO: Executes this statement.
        "create a struct",
        # AUTO: Executes this statement.
        "bundle definition",
        # AUTO: Executes this statement.
        "group fields together",
        # AUTO: Executes this statement.
        "custom type with fields",
        # AUTO: Executes this statement.
        "object with properties",
        # AUTO: Executes this statement.
        "struct member access dot",
        # AUTO: Executes this statement.
        "bundle Point",
        # AUTO: Executes this statement.
        "how to use bundles",
        # AUTO: Executes this statement.
        "bundle",
        # AUTO: Executes this statement.
        "the bundle",
        # AUTO: Executes this statement.
        "what is bundle",
        # AUTO: Executes this statement.
        "what is the bundle",
        # AUTO: Executes this statement.
        "give me code of bundle",
        # AUTO: Executes this statement.
        "show me bundle",
        # AUTO: Executes this statement.
        "code for bundle",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "operators in GAL",
        # AUTO: Executes this statement.
        "arithmetic comparison logical",
        # AUTO: Executes this statement.
        "plus minus multiply divide modulo",
        # AUTO: Executes this statement.
        "tilde negation negate",
        # AUTO: Executes this statement.
        "string concatenation backtick",
        # AUTO: Executes this statement.
        "increment decrement",
        # AUTO: Executes this statement.
        "assignment operator",
        # AUTO: Executes this statement.
        "operator precedence",
        # AUTO: Executes this statement.
        "equal not equal greater less",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "error bug debug fix",
        # AUTO: Executes this statement.
        "why is my code not working",
        # AUTO: Executes this statement.
        "syntax error semantic error",
        # AUTO: Executes this statement.
        "runtime error crash",
        # AUTO: Executes this statement.
        "common mistakes problems",
        # AUTO: Executes this statement.
        "troubleshoot issue",
        # AUTO: Executes this statement.
        "what went wrong",
        # AUTO: Executes this statement.
        "how to fix this error",
        # AUTO: Executes this statement.
        "code not running",
        # AUTO: Executes this statement.
        "fails with error",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "keyword reference list",
        # AUTO: Executes this statement.
        "all GAL keywords",
        # AUTO: Executes this statement.
        "cheat sheet quick reference",
        # AUTO: Executes this statement.
        "GAL syntax summary",
        # AUTO: Executes this statement.
        "what keywords does GAL have",
        # AUTO: Executes this statement.
        "GAL to C mapping",
        # AUTO: Executes this statement.
        "keyword table",
        # AUTO: Executes this statement.
        "help reference guide",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "example program template",
        # AUTO: Executes this statement.
        "hello world starter code",
        # AUTO: Executes this statement.
        "sample code basic program",
        # AUTO: Executes this statement.
        "simple GAL program",
        # AUTO: Executes this statement.
        "beginner getting started",
        # AUTO: Executes this statement.
        "write a GAL program",
        # AUTO: Executes this statement.
        "show me an example",
        # AUTO: Executes this statement.
        "generate code",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "convert C to GAL",
        # AUTO: Executes this statement.
        "translate from C language",
        # AUTO: Executes this statement.
        "C equivalent GAL equivalent",
        # AUTO: Executes this statement.
        "how to write this in GAL",
        # AUTO: Executes this statement.
        "what is the GAL version of",
        # AUTO: Executes this statement.
        "same as C but in GAL",
        # AUTO: Executes this statement.
        "porting C code to GAL",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "how to write comments in GAL code",
        # AUTO: Executes this statement.
        "comment syntax slash slash",
        # AUTO: Executes this statement.
        "single line comment double slash",
        # AUTO: Executes this statement.
        "multi line block comment",
        # AUTO: Executes this statement.
        "how to comment out code",
        # AUTO: Executes this statement.
        "annotation note in source code",
        # AUTO: Executes this statement.
        "commenting GAL code",
        # AUTO: Executes this statement.
        "// slash star block comment format",
     # AUTO: Closes the current grouped code/data.
     ],
     """**Comments** in GAL:
```
// This is a single-line comment

/* This is a
   multi-line comment */
```
Same syntax as C/Java."""),

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "identifier rules naming",
        # AUTO: Executes this statement.
        "variable name rules",
        # AUTO: Executes this statement.
        "maximum length identifier",
        # AUTO: Executes this statement.
        "valid variable names",
        # AUTO: Executes this statement.
        "naming conventions",
        # AUTO: Executes this statement.
        "identifier too long",
     # AUTO: Closes the current grouped code/data.
     ],
     """**Identifier rules:**
- Must start with a letter (a-z, A-Z)
- Can contain letters, digits, underscores after first character
- Maximum **15 characters** (longer = lexical error)
- Cannot start with a number or underscore
- Keywords are reserved

Valid: `x`, `count`, `myVar`, `total_sum`, `playerScore1`
Invalid: `2count`, `_name`, `thisIsWayTooLong`"""),

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "type casting conversion",
        # AUTO: Executes this statement.
        "convert between types",
        # AUTO: Executes this statement.
        "cast seed to tree",
        # AUTO: Executes this statement.
        "cast integer to float string",
        # AUTO: Executes this statement.
        "change variable type",
        # AUTO: Executes this statement.
        "how to cast in GAL",
        # AUTO: Executes this statement.
        "convert float to int",
        # AUTO: Executes this statement.
        "convert number to string",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "array built-in methods operations",
        # AUTO: Executes this statement.
        "append to array add element",
        # AUTO: Executes this statement.
        "insert into array",
        # AUTO: Executes this statement.
        "remove from array delete element",
        # AUTO: Executes this statement.
        "array length size count",
        # AUTO: Executes this statement.
        "add item to list",
        # AUTO: Executes this statement.
        "delete item from list",
        # AUTO: Executes this statement.
        "how many elements in array",
     # AUTO: Closes the current grouped code/data.
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
Array size must be managed explicitly with your own `seed` counter variable."""),

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "escape sequences special characters",
        # AUTO: Executes this statement.
        "newline tab in string",
        # AUTO: Executes this statement.
        "backslash n backslash t",
        # AUTO: Executes this statement.
        "print new line",
        # AUTO: Executes this statement.
        "special characters in strings",
        # AUTO: Executes this statement.
        "how to add newline",
        # AUTO: Executes this statement.
        "escape quote in string",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "string concatenation combine join",
        # AUTO: Executes this statement.
        "concatenate two strings",
        # AUTO: Executes this statement.
        "join strings together",
        # AUTO: Executes this statement.
        "backtick concat operator",
        # AUTO: Executes this statement.
        "combine text values",
        # AUTO: Executes this statement.
        "merge strings",
        # AUTO: Executes this statement.
        "add strings together",
     # AUTO: Closes the current grouped code/data.
     ],
     """**String concatenation** uses the backtick `` ` `` operator:
```
vine first = "Hello";
vine second = "World";
leaf mark = '!';
vine result = first ` " " ` second ` mark;  // "Hello World!"
```
Only `vine` and `leaf` operands may be joined with backtick; `+` is numeric, not string concatenation.
For output, prefer format strings:
```
plant("{} {}", first, second);  // cleaner
```"""),


    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "program structure organization",
        # AUTO: Executes this statement.
        "where does root go",
        # AUTO: Executes this statement.
        "how to organize GAL program",
        # AUTO: Executes this statement.
        "file structure layout",
        # AUTO: Executes this statement.
        "code organization order",
        # AUTO: Executes this statement.
        "what comes first in program",
        # AUTO: Executes this statement.
        "program skeleton template",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "scope rules variable visibility",
        # AUTO: Executes this statement.
        "local variable global variable",
        # AUTO: Executes this statement.
        "variable scope lifetime",
        # AUTO: Executes this statement.
        "where can I access variable",
        # AUTO: Executes this statement.
        "block scope braces",
        # AUTO: Executes this statement.
        "variable not visible",
        # AUTO: Executes this statement.
        "inner scope outer scope",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "how to make constant",
        # AUTO: Executes this statement.
        "fertile keyword constant",
        # AUTO: Executes this statement.
        "immutable variable value",
        # AUTO: Executes this statement.
        "cannot change value once set",
        # AUTO: Executes this statement.
        "fixed value read only",
        # AUTO: Executes this statement.
        "declare constant GAL",
        # AUTO: Executes this statement.
        "fertile rules restrictions",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "boolean values in GAL",
        # AUTO: Executes this statement.
        "sunshine and frost meaning",
        # AUTO: Executes this statement.
        "what is sunshine frost",
        # AUTO: Executes this statement.
        "true and false in GAL",
        # AUTO: Executes this statement.
        "branch type values",
        # AUTO: Executes this statement.
        "boolean literals",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "function return type options",
        # AUTO: Executes this statement.
        "empty function void return",
        # AUTO: Executes this statement.
        "what return types exist",
        # AUTO: Executes this statement.
        "how to return value function",
        # AUTO: Executes this statement.
        "reclaim with value",
        # AUTO: Executes this statement.
        "function that returns nothing",
     # AUTO: Closes the current grouped code/data.
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
- Non-empty functions must provide a value in their required final `reclaim`
- The CFG requires every function to end with `reclaim`"""),

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "recursive function in GAL",
        # AUTO: Executes this statement.
        "recursion example",
        # AUTO: Executes this statement.
        "function calls itself",
        # AUTO: Executes this statement.
        "recursive algorithm",
        # AUTO: Executes this statement.
        "base case recursion",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "nested if statements",
        # AUTO: Executes this statement.
        "if inside if nested",
        # AUTO: Executes this statement.
        "multiple nested conditions",
        # AUTO: Executes this statement.
        "nested spring bud wither",
        # AUTO: Executes this statement.
        "complex conditional logic",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "break statement prune",
        # AUTO: Executes this statement.
        "continue statement skip",
        # AUTO: Executes this statement.
        "exit loop early",
        # AUTO: Executes this statement.
        "skip iteration next",
        # AUTO: Executes this statement.
        "stop loop prematurely",
        # AUTO: Executes this statement.
        "prune and skip usage",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "nested loop inside loop",
        # AUTO: Executes this statement.
        "double loop two loops",
        # AUTO: Executes this statement.
        "inner outer loop",
        # AUTO: Executes this statement.
        "loop within loop",
        # AUTO: Executes this statement.
        "two dimensional loop",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "two dimensional array detailed",
        # AUTO: Executes this statement.
        "matrix operations rows columns",
        # AUTO: Executes this statement.
        "2d array initialization access",
        # AUTO: Executes this statement.
        "array of arrays nested",
        # AUTO: Executes this statement.
        "row column indexing",
        # AUTO: Executes this statement.
        "multi dimensional array",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "array of bundles structs",
        # AUTO: Executes this statement.
        "list of struct objects",
        # AUTO: Executes this statement.
        "multiple bundles in array",
        # AUTO: Executes this statement.
        "bundle array declaration",
        # AUTO: Executes this statement.
        "storing multiple records",
        # AUTO: Executes this statement.
        "bundle Point pts array",
        # AUTO: Executes this statement.
        "array of struct records",
        # AUTO: Executes this statement.
        "declaring array of bundle",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "nested bundle struct inside struct",
        # AUTO: Executes this statement.
        "bundle with bundle member",
        # AUTO: Executes this statement.
        "deep member access chain",
        # AUTO: Executes this statement.
        "bundle composition nested fields",
        # AUTO: Executes this statement.
        "struct within struct",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "operator precedence order",
        # AUTO: Executes this statement.
        "which operator evaluated first",
        # AUTO: Executes this statement.
        "order of operations math",
        # AUTO: Executes this statement.
        "evaluation order priority",
        # AUTO: Executes this statement.
        "operator priority table",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "prefix postfix increment",
        # AUTO: Executes this statement.
        "i++ vs ++i difference",
        # AUTO: Executes this statement.
        "decrement minus minus",
        # AUTO: Executes this statement.
        "plus plus operator",
        # AUTO: Executes this statement.
        "pre increment post increment",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "tilde operator negation",
        # AUTO: Executes this statement.
        "negative number in GAL",
        # AUTO: Executes this statement.
        "how to negate value",
        # AUTO: Executes this statement.
        "minus sign replacement",
        # AUTO: Executes this statement.
        "unary minus tilde",
        # AUTO: Executes this statement.
        "make number negative",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "compound assignment operators",
        # AUTO: Executes this statement.
        "plus equals minus equals",
        # AUTO: Executes this statement.
        "shorthand assignment",
        # AUTO: Adds into `"x`.
        "x += 5 operator",
        # AUTO: Executes this statement.
        "augmented assignment",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "format string in plant",
        # AUTO: Executes this statement.
        "placeholder curly braces",
        # AUTO: Executes this statement.
        "string interpolation output",
        # AUTO: Executes this statement.
        "plant with multiple values",
        # AUTO: Executes this statement.
        "how to format output",
        # AUTO: Executes this statement.
        "print formatted text",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "limits constraints maximum GAL",
        # AUTO: Executes this statement.
        "what are the GAL limits",
        # AUTO: Executes this statement.
        "size restrictions boundaries",
        # AUTO: Executes this statement.
        "maximum values allowed in GAL",
        # AUTO: Executes this statement.
        "language limitations GAL",
        # AUTO: Executes this statement.
        "max identifier length 15",
        # AUTO: Executes this statement.
        "max loop iterations 10000",
        # AUTO: Executes this statement.
        "maximum integer digits 8",
        # AUTO: Executes this statement.
        "GAL restrictions constraints",
        # AUTO: Executes this statement.
        "15 character limit identifier",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "how does compiler work",
        # AUTO: Executes this statement.
        "compilation process stages",
        # AUTO: Executes this statement.
        "lexer parser semantic interpreter",
        # AUTO: Executes this statement.
        "compiler pipeline phases",
        # AUTO: Executes this statement.
        "what happens when code runs",
        # AUTO: Executes this statement.
        "how GAL compiles code",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "forgot semicolon error",
        # AUTO: Executes this statement.
        "where do I put semicolons",
        # AUTO: Executes this statement.
        "which statements need semicolons",
        # AUTO: Executes this statement.
        "semicolon rules placement",
        # AUTO: Executes this statement.
        "unexpected token expected semicolon",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "type mismatch error help",
        # AUTO: Executes this statement.
        "cannot assign wrong type",
        # AUTO: Executes this statement.
        "incompatible types problem",
        # AUTO: Executes this statement.
        "type error how to fix",
        # AUTO: Executes this statement.
        "wrong type assignment",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "variable not declared error",
        # AUTO: Executes this statement.
        "undefined undeclared variable",
        # AUTO: Executes this statement.
        "forgot to declare variable",
        # AUTO: Executes this statement.
        "used before declaration fix",
        # AUTO: Executes this statement.
        "variable not found scope",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "used wrong keyword from C",
        # AUTO: Executes this statement.
        "if instead of spring",
        # AUTO: Executes this statement.
        "for instead of cultivate",
        # AUTO: Executes this statement.
        "C keyword not working",
        # AUTO: Executes this statement.
        "not a GAL keyword error",
        # AUTO: Executes this statement.
        "converted from C not working",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "fertile constant error",
        # AUTO: Executes this statement.
        "cannot reassign fertile",
        # AUTO: Executes this statement.
        "constant not initialized",
        # AUTO: Executes this statement.
        "fertile must be initialized",
        # AUTO: Executes this statement.
        "modify const variable error",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "factorial example program",
        # AUTO: Executes this statement.
        "recursive example code",
        # AUTO: Executes this statement.
        "factorial GAL code",
        # AUTO: Executes this statement.
        "recursion complete example",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "array operations example",
        # AUTO: Executes this statement.
        "sum of array elements",
        # AUTO: Executes this statement.
        "find element in array",
        # AUTO: Executes this statement.
        "array manipulation code",
        # AUTO: Executes this statement.
        "array example program",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "sorting example program",
        # AUTO: Executes this statement.
        "bubble sort GAL code",
        # AUTO: Executes this statement.
        "sort an array numbers",
        # AUTO: Executes this statement.
        "sorting algorithm example",
        # AUTO: Executes this statement.
        "arrange elements in order",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "bundle struct example program",
        # AUTO: Executes this statement.
        "complete bundle example",
        # AUTO: Executes this statement.
        "struct usage code sample",
        # AUTO: Executes this statement.
        "bundle with functions example",
     # AUTO: Closes the current grouped code/data.
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

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "difference between GAL and C", "GAL vs C", "how is GAL different from C",
        # AUTO: Executes this statement.
        "compare GAL and C", "GAL compared to C", "what makes GAL unique",
        # AUTO: Executes this statement.
        "GAL versus C programming", "why GAL instead of C",
    # AUTO: Closes the current grouped code/data.
    ],
     """Here's a side-by-side comparison of **GAL vs C**:

| Concept | C | GAL |
|---|---|---|
| Integer | `int` | `seed` |
| Float | `float` | `tree` |
| Character | `char` | `leaf` |
| String | `char[]` / `char*` | `vine` |
| Boolean | `_Bool` / `stdbool.h` | `branch` |
| True/False | `1`/`0` | `sunshine`/`frost` |
| Print | `printf()` | `plant()` |
| Input | `scanf()` | `water()` |
| For loop | `for` | `cultivate` |
| While loop | `while` | `grow` |
| Do-while | `do...while` | `tend...grow` |
| If/else | `if`/`else` | `spring`/`wither` |
| Else-if | `else if` | `bud` |
| Switch | `switch`/`case`/`default` | `harvest`/`variety`/`soil` |
| Function | function definition | `pollinate` |
| Return | `return` | `reclaim` |
| Main | `main()` | `root()` |
| Struct | `struct` | `bundle` |
| Constant | `const` | `fertile` |
| Break | `break` | `prune` |
| Continue | `continue` | `skip` |

**Key differences:**
- GAL uses **botanical/garden-themed** keywords instead of C's traditional keywords
- GAL has **built-in string type** (`vine`) — no pointer arithmetic needed
- GAL has **built-in array operations**: `append()`, `insert()`, `remove()`
- GAL uses `~` for **unary negation** (not `-`)
- Format strings use `{}` placeholders (like Python), not `%d`/`%s`"""),

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "common mistakes in GAL", "GAL pitfalls", "beginners mistakes",
        # AUTO: Executes this statement.
        "what mistakes do people make", "things to watch out for in GAL",
        # AUTO: Executes this statement.
        "GAL gotchas", "common errors beginners make", "tips for GAL",
        # AUTO: Executes this statement.
        "mistakes to avoid", "what should I be careful about",
    # AUTO: Closes the current grouped code/data.
    ],
     """**Common GAL Mistakes & How to Avoid Them:**

1. **Using C keywords instead of GAL keywords**
   - ❌ `int x = 5;` → ✅ `seed x = 5;`
   - ❌ `printf("hi");` → ✅ `plant("hi");`
   - ❌ `if (x > 0)` → ✅ `spring (x > 0)`

2. **Forgetting `reclaim` in `root()`**
   - Every `root()` function must end with `reclaim;`

3. **Using `-` for negation instead of `~`**
   - ❌ `seed x = -5;` → ✅ `seed x = ~5;`

4. **Identifier too long (max 15 characters)**
   - ❌ `seed myVeryLongVariableName = 1;`
   - ✅ `seed myVarName = 1;`

5. **Integer too large (max 8 digits)**
   - ❌ `seed x = 123456789;` → ✅ `seed x = 12345678;`

6. **Missing semicolons** — every statement needs one!

7. **Type mismatch in declarations**
   - ❌ `seed x = 3.14;` (seed can't hold decimals)
   - ✅ `tree x = 3.14;`

8. **Forgetting to update loop variable** → infinite loop!
   - Always increment/decrement inside `grow` loops

9. **Using `==` for strings** — string comparison is supported but be aware of types

10. **Array index out of bounds** — indices are 0 to `TS(arr)-1`"""),

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "how to debug GAL", "debugging GAL code", "my GAL code doesn't work",
        # AUTO: Executes this statement.
        "GAL code not working", "how to fix GAL errors", "debug my code",
        # AUTO: Executes this statement.
        "troubleshoot GAL", "find errors in GAL", "why doesn't my code work",
        # AUTO: Executes this statement.
        "help me debug", "my program crashes",
    # AUTO: Closes the current grouped code/data.
    ],
     """**How to Debug GAL Code:**

**Step 1: Read the error message carefully**
The compiler tells you exactly what's wrong and which line. Error messages include:
- **Lexer errors**: Invalid characters, identifiers too long, unclosed strings
- **Parser errors**: Missing keywords, wrong syntax structure
- **Semantic errors**: Type mismatches, undeclared variables, wrong function arguments
- **Runtime errors**: Division by zero, array out of bounds, infinite loops

**Step 2: Check these common issues**
- Did you use GAL keywords (not C keywords)?
- Are all semicolons present?
- Does every `root()` end with `reclaim;`?
- Do types match? (`seed` = integers only, `tree` = decimals, etc.)
- Are array indices within bounds?

**Step 3: Simplify and isolate**
- Comment out code sections with `// ...` or `/* ... */`
- Test small pieces individually
- Use `plant()` to print variable values at key points

**Step 4: Use the Run button**
- The output panel shows errors with line numbers
- Click Run to execute and see runtime behavior

**Pro tip:** Paste any error message into this chat — I can explain it in detail!"""),

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "what is GAL", "what is the GAL language", "tell me about GAL",
        # AUTO: Executes this statement.
        "GAL programming language", "what is this language", "about GAL",
        # AUTO: Executes this statement.
        "introduction to GAL", "GAL overview", "what language is this",
        # AUTO: Executes this statement.
        "what programming language", "explain GAL",
    # AUTO: Closes the current grouped code/data.
    ],
     """**GAL (Garden Abstraction Language)** is an educational programming language with a **botanical/garden theme**.

**Key characteristics:**
- 🌱 **Garden-themed keywords** — variables are `seed`/`tree`/`leaf`/`vine`/`branch`, functions use `pollinate`/`reclaim`, loops use `cultivate`/`grow`
- 📚 **C-like structure** — if you know C, you already know the structure (just different keywords)
- 🔧 **Full compiler pipeline** — lexer → parser → semantic analyzer → intermediate code generator → interpreter
- 🎮 **Built-in IDE** — this web interface with syntax highlighting, error reporting, and AI chat
- ✅ **Educational purpose** — designed to teach compiler construction and language design concepts

**Quick example:**
```
root() {
    vine greeting = "Hello, Garden!";
    plant(greeting);
    reclaim;
}
```
This prints "Hello, Garden!" — `root()` is like `main()`, `plant()` is like `printf()`, and `reclaim` is like `return`."""),

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "how to run GAL", "how to execute", "run my program", "how to compile",
        # AUTO: Executes this statement.
        "how to use this IDE", "how to use the editor", "where do I type code",
        # AUTO: Executes this statement.
        "how to start coding", "getting started with GAL", "how to write GAL",
        # AUTO: Executes this statement.
        "run button", "execute program",
    # AUTO: Closes the current grouped code/data.
    ],
     """**How to Run a GAL Program:**

1. **Write your code** in the editor panel (left side)
2. **Click the ▶ Run button** in the toolbar
3. **See output** in the Output panel (bottom/right)

**IDE Features:**
- **Syntax highlighting** — GAL keywords are colored automatically
- **Error reporting** — compiler errors show in the output with line numbers
- **Lexer tab** — see all tokens your code produces
- **Parser tab** — see the syntax analysis results
- **Semantic tab** — see variable/function declarations and type checking
- **ICG tab** — see the intermediate code generated
- **AI Chat** — ask me questions about GAL anytime!

**Basic template to start with:**
```
root() {
    plant("Hello World!");
    reclaim;
}
```

Just type this in the editor and hit Run!"""),

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "string operations", "how to work with strings", "vine operations",
        # AUTO: Executes this statement.
        "string manipulation", "string functions", "what can I do with strings",
        # AUTO: Executes this statement.
        "string methods", "vine methods", "string in GAL",
    # AUTO: Closes the current grouped code/data.
    ],
     """**String (`vine`) Operations in GAL:**

**Declaration:**
```
vine name = "Alice";
vine empty = "";
```

**Concatenation** — use the backtick operator `` ` ``:
```
vine first = "Hello";
vine second = "World";
vine result = first ` " " ` second;  // "Hello World"
```

**Print with format strings:**
```
plant("Name: {}", name);
```

**Escape sequences:**
- `\\n` — newline
- `\\t` — tab
- `\\\\"` — literal double quote
- `\\\\` — literal backslash"""),

    # AUTO: Executes this statement.
    ([
        # AUTO: Executes this statement.
        "math in GAL", "arithmetic operations", "math operations",
        # AUTO: Executes this statement.
        "how to do math", "calculations in GAL", "number operations",
        # AUTO: Executes this statement.
        "mathematical operations", "division in GAL", "modulo",
    # AUTO: Closes the current grouped code/data.
    ],
     """**Math & Number Operations in GAL:**

**Arithmetic:**
| Operator | Meaning | Example |
|---|---|---|
| `+` | Addition | `seed x = 5 + 3;` → 8 |
| `-` | Subtraction | `seed x = 10 - 4;` → 6 |
| `*` | Multiplication | `seed x = 3 * 4;` → 12 |
| `/` | Division | `tree x = 10.0 / 3.0;` → 3.33 |
| `%` | Modulo | `seed x = 10 % 3;` → 1 |

**Important notes:**
- Integer division truncates: `seed x = 7 / 2;` → `3`
- Use `tree` for decimal results: `tree x = 7.0 / 2.0;` → `3.5`
- Unary negation uses `~` (tilde): `seed x = ~5;` → `-5`
- Max 8 digits for integers, 8 decimal digits for floats

**Increment / Decrement:**
```
seed x = 5;
x++;    // x is now 6
x--;    // x is now 5 again
++x;    // prefix: increment then use
x--;    // postfix: use then decrement
```

**Compound assignment:**
```
seed x = 10;
x += 5;   // x = 15
x -= 3;   // x = 12
x *= 2;   // x = 24
x /= 4;   // x = 6
x %= 4;   // x = 2
```"""),
# AUTO: Closes the current grouped code/data.
]


# AUTO: Sets `_st_model`.
_st_model = None
# AUTO: Sets `_phrase_embeddings`.
_phrase_embeddings = None
# AUTO: Sets `_phrase_topic_idx`.
_phrase_topic_idx = []
# AUTO: Sets `_responses`.
_responses = []
# AUTO: Sets `_last_topic_idx`.
_last_topic_idx = None
# AUTO: Sets `_last_query`.
_last_query = ""


# AUTO: Sets `_SYNONYMS`.
_SYNONYMS = {
    # AUTO: Executes this statement.
    "int":       "seed",    "integer":    "seed",
    # AUTO: Executes this statement.
    "float":     "tree",    "double":     "tree",   "decimal": "tree",
    # AUTO: Executes this statement.
    "char":      "leaf",    "character":  "leaf",
    # AUTO: Executes this statement.
    "string":    "vine",    "text":       "vine",   "str": "vine",
    # AUTO: Executes this statement.
    "bool":      "branch data type",  "boolean":    "branch data type",
    # AUTO: Executes this statement.
    "void":      "empty",
    # AUTO: Executes this statement.
    "print":     "plant",   "output":     "plant",  "display": "plant",  "log": "plant",
    # AUTO: Executes this statement.
    "input":     "water",   "read":       "water",  "scanf": "water",    "cin": "water",
    # AUTO: Executes this statement.
    "for":       "cultivate",  "for loop":  "cultivate", "while":   "grow",  "while loop": "grow",  "do while": "tend do-while",  "do-while": "tend do-while",
    # AUTO: Executes this statement.
    "if":        "spring",  "else":       "wither", "elif": "bud",       "else if": "bud",
    # AUTO: Executes this statement.
    "switch":    "harvest", "case":       "pick",
    # AUTO: Executes this statement.
    "function":  "pollinate", "func":     "pollinate", "method": "pollinate", "return": "reclaim",
    # AUTO: Executes this statement.
    "main":      "root",    "entry point":"root",
    # AUTO: Executes this statement.
    "struct":    "bundle",  "class":      "bundle", "object": "bundle",  "record": "bundle",
    # AUTO: Executes this statement.
    "true":      "sunshine","false":      "frost",
    # AUTO: Executes this statement.
    "array":     "array declaration", "list": "array",
    # AUTO: Executes this statement.
    "cast":      "type casting", "convert": "type casting", "conversion": "type casting",
    # AUTO: Executes this statement.
    "concatenate":"backtick string concat", "concat": "backtick string concat",
    # AUTO: Executes this statement.
    "comment":   "comment annotation",
    # AUTO: Executes this statement.
    "append":    "array append built-in", "remove": "array remove built-in",
    # AUTO: Executes this statement.
    "escape":    "escape sequence backslash",
    # AUTO: Executes this statement.
    "scope":     "local global scope variable visibility",
    # AUTO: Executes this statement.
    "constant":  "fertile const immutable",
    # AUTO: Executes this statement.
    "recursion": "recursive function calls itself",
    # AUTO: Executes this statement.
    "precedence":"operator precedence order evaluation",
    # AUTO: Executes this statement.
    "format":    "format string placeholder curly braces",
    # AUTO: Executes this statement.
    "limit":     "limits constraints maximum",
    # AUTO: Executes this statement.
    "compile":   "compiler stages lexer parser",
    # AUTO: Executes this statement.
    "length":    "array size manual bounds",
    # AUTO: Executes this statement.
    "split":     "manual character array",
    # AUTO: Executes this statement.
    "negative":  "tilde negation unary",
    # AUTO: Executes this statement.
    "increment": "increment prefix postfix",
    # AUTO: Executes this statement.
    "decrement": "decrement prefix postfix",
    # AUTO: Executes this statement.
    "debug":     "debugging error fix troubleshoot",
    # AUTO: Executes this statement.
    "run":       "execute compile program root",
    # AUTO: Executes this statement.
    "help":      "getting started help tutorial",
    # AUTO: Executes this statement.
    "variable":  "declaration seed tree leaf vine branch",
    # AUTO: Executes this statement.
    "loop":      "cultivate grow tend loop iteration",
    # AUTO: Executes this statement.
    "condition":  "spring bud wither conditional if else",
    # AUTO: Executes this statement.
    "break":     "prune exit loop",
    # AUTO: Executes this statement.
    "continue":  "skip next iteration",
    # AUTO: Executes this statement.
    "string":    "vine",
    # AUTO: Executes this statement.
    "math":      "arithmetic operations calculation",
    # AUTO: Executes this statement.
    "number":    "seed tree integer float arithmetic",
# AUTO: Closes the current grouped code/data.
}

# AUTO: Sets `_GAL_KEYWORD_MAP`.
_GAL_KEYWORD_MAP = {
    # AUTO: Executes this statement.
    "seed":       "seed data type integer variable declaration",
    # AUTO: Executes this statement.
    "tree":       "tree data type float decimal variable declaration",
    # AUTO: Executes this statement.
    "leaf":       "leaf data type character char single character",
    # AUTO: Executes this statement.
    "vine":       "vine data type string text declaration",
    # AUTO: Executes this statement.
    "branch":     "branch data type boolean true false sunshine frost",
    # AUTO: Executes this statement.
    "cultivate":  "cultivate for loop iteration counter",
    # AUTO: Executes this statement.
    "grow":       "grow while loop condition repeat",
    # AUTO: Executes this statement.
    "tend":       "tend do-while loop tend grow",
    # AUTO: Executes this statement.
    "spring":     "spring if conditional statement",
    # AUTO: Executes this statement.
    "bud":        "bud else if conditional elif",
    # AUTO: Executes this statement.
    "wither":     "wither else conditional fallback",
    # AUTO: Executes this statement.
    "harvest":    "harvest switch statement case",
    # AUTO: Executes this statement.
    "variety":    "variety case in harvest switch",
    # AUTO: Executes this statement.
    "soil":       "soil default case in harvest switch",
    # AUTO: Executes this statement.
    "pollinate":  "pollinate function declaration definition",
    # AUTO: Executes this statement.
    "reclaim":    "reclaim return value from function",
    # AUTO: Executes this statement.
    "root":       "root main function entry point program",
    # AUTO: Executes this statement.
    "plant":      "plant print output display text",
    # AUTO: Executes this statement.
    "water":      "water input read user prompt",
    # AUTO: Executes this statement.
    "bundle":     "bundle struct record data structure fields",
    # AUTO: Executes this statement.
    "fertile":    "fertile constant immutable variable",
    # AUTO: Executes this statement.
    "prune":      "prune break exit loop switch",
    # AUTO: Executes this statement.
    "skip":       "skip continue next iteration loop",
    # AUTO: Executes this statement.
    "sunshine":   "sunshine true boolean value",
    # AUTO: Executes this statement.
    "frost":      "frost false boolean value",
    # AUTO: Executes this statement.
    "empty":      "empty void no return type function",
    # AUTO: Executes this statement.
    "append":     "append add element to array built-in",
    # AUTO: Executes this statement.
    "insert":     "insert element at index array built-in",
    # AUTO: Executes this statement.
    "remove":     "remove element from array built-in",
# AUTO: Closes the current grouped code/data.
}


# AUTO: Sets `_GREETING_PATTERNS`.
_GREETING_PATTERNS = [
    # AUTO: Calls `function`.
    (_re.compile(r"^\s*(hi|hello|hey|howdy|sup|yo|greetings|good\s*(morning|afternoon|evening))\b", _re.I),
     # AUTO: Executes this statement.
     "Hey there! I'm the GAL AI Assistant. Ask me anything about GAL — data types, loops, functions, arrays, I/O, and more!"),
    # AUTO: Calls `function`.
    (_re.compile(r"^\s*(thanks?|thank\s*you|ty|thx|cheers)\b", _re.I),
     # AUTO: Executes this statement.
     "You're welcome! Feel free to ask more about GAL anytime."),
    # AUTO: Calls `function`.
    (_re.compile(r"^\s*(bye|goodbye|see\s*ya|later|cya)\b", _re.I),
     # AUTO: Executes this statement.
     "Goodbye! Happy coding with GAL! 🌱"),
    # AUTO: Calls `function`.
    (_re.compile(r"\b(what can you do|help me|what do you know|how can you help)\b", _re.I),
     # AUTO: Executes this statement.
     None),
    # AUTO: Calls `function`.
    (_re.compile(r"^\s*(who are you|what are you)\b", _re.I),
     # AUTO: Executes this statement.
     "I'm the GAL AI Assistant — I help with GAL syntax, concepts, and debugging. Ask me about data types, loops, functions, arrays, or anything else in GAL!"),
# AUTO: Closes the current grouped code/data.
]


# AUTO: Defines function `_encode`.
def _encode(texts):
    # AUTO: Returns this result to the caller.
    return _st_model.encode(texts, normalize_embeddings=True, show_progress_bar=False)


# AUTO: Defines function `_ensure_model`.
def _ensure_model():
    # AUTO: Uses a module-level variable inside this function.
    global _st_model, _phrase_embeddings, _phrase_topic_idx, _responses
    # AUTO: Checks this condition.
    if _st_model is not None:
        # AUTO: Returns this result to the caller.
        return

    # AUTO: Imports names from another module.
    from sentence_transformers import SentenceTransformer
    # AUTO: Imports a module used by this file.
    import os

    # AUTO: Sets `finetuned`.
    finetuned = os.path.join(os.path.dirname(__file__), "..", "gal-mpnet-finetuned")
    # AUTO: Checks this condition.
    if os.path.isdir(finetuned):
        # AUTO: Sets `_st_model`.
        _st_model = SentenceTransformer(finetuned)
    # AUTO: Runs when previous condition did not pass.
    else:
        # AUTO: Sets `_st_model`.
        _st_model = SentenceTransformer("Clarkoer/gal-mpnet-finetuned")

    # AUTO: Sets `_phrase_topic_idx`.
    _phrase_topic_idx = []
    # AUTO: Sets `_responses`.
    _responses = []
    # AUTO: Sets `all_phrases`.
    all_phrases = []

    # AUTO: Starts a loop over these values.
    for topic_idx, (phrases, response) in enumerate(_KNOWLEDGE_BASE):
        # AUTO: Appends a value to a list.
        _responses.append(response)
        # AUTO: Starts a loop over these values.
        for p in phrases:
            # AUTO: Appends a value to a list.
            all_phrases.append(p)
            # AUTO: Appends a value to a list.
            _phrase_topic_idx.append(topic_idx)

    # AUTO: Sets `_phrase_embeddings`.
    _phrase_embeddings = _encode(all_phrases)


# AUTO: Sets `_DEFAULT_RESPONSE`.
_DEFAULT_RESPONSE = """I can help with GAL syntax and concepts! Try asking about:
# AUTO: Executes this statement.
- **Data types**: seed, tree, leaf, vine, branch
# AUTO: Executes this statement.
- **Variables**: declarations, constants (`fertile`), scope rules
# AUTO: Calls `cultivate`.
- **Loops**: cultivate (for), grow (while), tend...grow (do-while)
# AUTO: Calls `spring`.
- **Conditions**: spring (if), bud (else if), wither (else)
# AUTO: Executes this statement.
- **Functions**: pollinate, reclaim, root(), recursion
# AUTO: Executes this statement.
- **I/O**: plant() (print), water() (input), format strings
# AUTO: Calls `built-ins`.
- **Arrays**: declaration, 2D arrays, built-ins (append, insert, remove)
# AUTO: Executes this statement.
- **Bundles**: struct-like types, nested bundles, array of bundles
# AUTO: Executes this statement.
- **Type casting**: `(seed)`, `(tree)`, `(vine)`, etc.
# AUTO: Executes this statement.
- **Operators**: arithmetic, comparison, logical, precedence
# AUTO: Executes this statement.
- **Built-ins**: append/insert/remove
# AUTO: Executes this statement.
- **Errors**: paste any compiler error for a detailed explanation!

# AUTO: Executes this statement.
Or ask for "keyword reference", "example program", or "how does the compiler work"!

# AUTO: Executes this statement.
*Note: I'm running in offline mode right now. For more detailed help, try again later when the AI service is available.*"""

# AUTO: Imports a module used by this file.
import random as _random

# AUTO: Sets `_CONFIDENT_INTROS`.
_CONFIDENT_INTROS = [
    # AUTO: Executes this statement.
    "Great question! ",
    # AUTO: Executes this statement.
    "Sure thing! ",
    # AUTO: Executes this statement.
    "Here's what you need to know:\n\n",
    # AUTO: Executes this statement.
    "Absolutely! ",
    # AUTO: Executes this statement.
    "Good question — ",
    # AUTO: Executes this statement.
    "Here you go:\n\n",
    # AUTO: Executes this statement.
    "",
    # AUTO: Executes this statement.
    "",
# AUTO: Closes the current grouped code/data.
]

# AUTO: Sets `_MODERATE_INTROS`.
_MODERATE_INTROS = [
    # AUTO: Executes this statement.
    "I think you're asking about this — ",
    # AUTO: Executes this statement.
    "Based on your question, this should help:\n\n",
    # AUTO: Executes this statement.
    "This looks relevant to what you're asking:\n\n",
    # AUTO: Executes this statement.
    "Here's what I found:\n\n",
# AUTO: Closes the current grouped code/data.
]

# AUTO: Sets `_BLEND_TRANSITIONS`.
_BLEND_TRANSITIONS = [
    # AUTO: Executes this statement.
    "\n\n**Also related:**\n\n",
    # AUTO: Executes this statement.
    "\n\nYou might also find this useful:\n\n",
    # AUTO: Executes this statement.
    "\n\n**Additionally:**\n\n",
    # AUTO: Executes this statement.
    "\n\nThis is also relevant:\n\n",
# AUTO: Closes the current grouped code/data.
]

# AUTO: Sets `_FOLLOWUP_INTROS`.
_FOLLOWUP_INTROS = [
    # AUTO: Executes this statement.
    "Following up on that — ",
    # AUTO: Executes this statement.
    "Continuing from before:\n\n",
    # AUTO: Executes this statement.
    "Building on our previous topic:\n\n",
    # AUTO: Executes this statement.
    "Sure, here's more on that:\n\n",
# AUTO: Closes the current grouped code/data.
]

# AUTO: Sets `_OUTROS`.
_OUTROS = [
    # AUTO: Executes this statement.
    "\n\n---\n*Feel free to ask follow-up questions!*",
    # AUTO: Executes this statement.
    "\n\n---\n*Let me know if you need more details on any part!*",
    # AUTO: Executes this statement.
    "\n\n---\n*Want me to explain any part further?*",
    # AUTO: Executes this statement.
    "",
    # AUTO: Executes this statement.
    "",
# AUTO: Closes the current grouped code/data.
]

# AUTO: Sets `_conv_history`.
_conv_history = []
# AUTO: Sets `_MAX_HISTORY`.
_MAX_HISTORY = 8


# AUTO: Defines function `_expand_query`.
def _expand_query(text):
    # AUTO: Sets `words`.
    words = text.lower().split()
    # AUTO: Sets `extras`.
    extras = set()

    # AUTO: Starts a loop over these values.
    for w in words:
        # AUTO: Checks this condition.
        if w in _SYNONYMS:
            # AUTO: Calls `extras.add`.
            extras.add(_SYNONYMS[w])

    # AUTO: Sets `lower`.
    lower = text.lower()
    # AUTO: Starts a loop over these values.
    for phrase, replacement in _SYNONYMS.items():
        # AUTO: Checks this condition.
        if " " in phrase and phrase in lower:
            # AUTO: Calls `extras.add`.
            extras.add(replacement)

    # AUTO: Starts a loop over these values.
    for w in words:
        # AUTO: Checks this condition.
        if w in _GAL_KEYWORD_MAP:
            # AUTO: Calls `extras.add`.
            extras.add(_GAL_KEYWORD_MAP[w])

    # AUTO: Starts a loop over these values.
    for kw, desc in _GAL_KEYWORD_MAP.items():
        # AUTO: Checks this condition.
        if " " in kw and kw in lower:
            # AUTO: Calls `extras.add`.
            extras.add(desc)

    # AUTO: Checks this condition.
    if extras:
        # AUTO: Returns this result to the caller.
        return text + " " + " ".join(extras)
    # AUTO: Returns this result to the caller.
    return text


# AUTO: Defines function `_detect_intent`.
def _detect_intent(msg):
    # AUTO: Sets `low`.
    low = msg.lower()
    # AUTO: Checks this condition.
    if any(w in low for w in ["how do i", "how to", "how can i", "how would"]):
        # AUTO: Returns this result to the caller.
        return "how-to"
    # AUTO: Checks this condition.
    if any(w in low for w in ["what is", "what are", "what's", "define", "explain"]):
        # AUTO: Returns this result to the caller.
        return "definition"
    # AUTO: Checks this condition.
    if any(w in low for w in ["example", "show me", "sample", "demonstrate", "code for", "give me code", "code of"]):
        # AUTO: Returns this result to the caller.
        return "example"
    # AUTO: Checks this condition.
    if any(w in low for w in ["difference", "vs", "versus", "compared to", "or"]):
        # AUTO: Returns this result to the caller.
        return "comparison"
    # AUTO: Checks this condition.
    if any(w in low for w in ["error", "wrong", "fail", "bug", "fix", "issue", "problem", "doesn't work", "not working"]):
        # AUTO: Returns this result to the caller.
        return "debug"
    # AUTO: Checks this condition.
    if any(w in low for w in ["why", "reason"]):
        # AUTO: Returns this result to the caller.
        return "why"
    # AUTO: Checks this condition.
    if any(w in low for w in ["tell me more", "more about", "elaborate", "explain further", "go deeper", "more detail"]):
        # AUTO: Returns this result to the caller.
        return "more"
    # AUTO: Returns this result to the caller.
    return "general"


# AUTO: Defines function `_is_followup`.
def _is_followup(msg):
    # AUTO: Sets `low`.
    low = msg.lower().split()
    # AUTO: Checks this condition.
    if len(low) <= 5 and any(w in msg.lower() for w in [
        # AUTO: Executes this statement.
        "it", "that", "this", "those", "them", "more", "also",
        # AUTO: Executes this statement.
        "too", "same", "again", "another", "other"
    # AUTO: Closes the current grouped code/data.
    ]):
        # AUTO: Returns this result to the caller.
        return True
    # AUTO: Checks this condition.
    if _detect_intent(msg) == "more":
        # AUTO: Returns this result to the caller.
        return True
    # AUTO: Returns this result to the caller.
    return False


# AUTO: Defines function `_pick_intro`.
def _pick_intro(score, intent, is_followup):
    # AUTO: Checks this condition.
    if is_followup:
        # AUTO: Returns this result to the caller.
        return _random.choice(_FOLLOWUP_INTROS)
    # AUTO: Checks this condition.
    if score > 0.6:
        # AUTO: Returns this result to the caller.
        return _random.choice(_CONFIDENT_INTROS)
    # AUTO: Checks this condition.
    if score > 0.45:
        # AUTO: Returns this result to the caller.
        return _random.choice(_MODERATE_INTROS)
    # AUTO: Returns this result to the caller.
    return _random.choice(_MODERATE_INTROS)


# AUTO: Defines function `_wrap_response`.
def _wrap_response(raw_response, score, intent, is_followup, has_blend=False):
    # AUTO: Sets `intro`.
    intro = _pick_intro(score, intent, is_followup)
    # AUTO: Sets `outro`.
    outro = _random.choice(_OUTROS) if not has_blend else ""
    # AUTO: Returns this result to the caller.
    return intro + raw_response + outro


# AUTO: Defines function `fallback_reply`.
def fallback_reply(user_message):
    # AUTO: Imports a module used by this file.
    import numpy as np
    # AUTO: Uses a module-level variable inside this function.
    global _last_topic_idx, _last_query

    # AUTO: Sets `msg`.
    msg = user_message.strip()

    # AUTO: Starts a loop over these values.
    for pattern, response in _GREETING_PATTERNS:
        # AUTO: Checks this condition.
        if pattern.search(msg):
            # AUTO: Returns this result to the caller.
            return response if response else _DEFAULT_RESPONSE

    # AUTO: Checks this condition.
    if not msg or len(msg) < 2:
        # AUTO: Returns this result to the caller.
        return _DEFAULT_RESPONSE

    # AUTO: Checks this condition.
    if len(msg) < 4 and msg.lower() not in _GAL_KEYWORD_MAP:
        # AUTO: Returns this result to the caller.
        return _DEFAULT_RESPONSE

    # AUTO: Sets `rule_match`.
    rule_match = _rule_engine_match(msg)
    # AUTO: Checks this condition.
    if rule_match:
        # AUTO: Sets `_last_query`.
        _last_query = msg
        # AUTO: Appends a value to a list.
        _conv_history.append((msg, -1, 1.0))
        # AUTO: Checks this condition.
        if len(_conv_history) > _MAX_HISTORY:
            # AUTO: Removes and returns an item.
            _conv_history.pop(0)
        # AUTO: Returns this result to the caller.
        return rule_match

    # AUTO: Calls `_ensure_model`.
    _ensure_model()

    # AUTO: Sets `intent`.
    intent = _detect_intent(msg)
    # AUTO: Sets `is_followup`.
    is_followup = _is_followup(msg) and _conv_history

    # AUTO: Sets `expanded`.
    expanded = _expand_query(msg)

    # AUTO: Checks this condition.
    if is_followup and _conv_history:
        # AUTO: Sets `recent`.
        recent = [h[0] for h in _conv_history[-2:]]
        # AUTO: Sets `expanded`.
        expanded = " ".join(recent) + " " + expanded

    # AUTO: Sets `query_emb`.
    query_emb = _encode([expanded])
    # AUTO: Sets `scores`.
    scores = np.dot(_phrase_embeddings, query_emb.T).flatten()

    # AUTO: Sets `topic_best`.
    topic_best = {}
    # AUTO: Starts a loop over these values.
    for i, score in enumerate(scores):
        # AUTO: Sets `tidx`.
        tidx = _phrase_topic_idx[i]
        # AUTO: Checks this condition.
        if tidx not in topic_best or score > topic_best[tidx]:
            # AUTO: Sets `topic_best[tidx]`.
            topic_best[tidx] = float(score)

    # AUTO: Sets `ranked`.
    ranked = sorted(topic_best.items(), key=lambda x: -x[1])
    # AUTO: Sets `best_idx, best_score`.
    best_idx, best_score = ranked[0]

    # AUTO: Checks this condition.
    if best_score < _THRESHOLD:
        # AUTO: Sets `_last_query`.
        _last_query = msg
        # AUTO: Checks this condition.
        if is_followup:
            # AUTO: Sets `bare_expanded`.
            bare_expanded = _expand_query(msg)
            # AUTO: Sets `query_emb2`.
            query_emb2 = _encode([bare_expanded])
            # AUTO: Sets `scores2`.
            scores2 = np.dot(_phrase_embeddings, query_emb2.T).flatten()
            # AUTO: Sets `topic_best2`.
            topic_best2 = {}
            # AUTO: Starts a loop over these values.
            for i, s in enumerate(scores2):
                # AUTO: Sets `tidx`.
                tidx = _phrase_topic_idx[i]
                # AUTO: Checks this condition.
                if tidx not in topic_best2 or s > topic_best2[tidx]:
                    # AUTO: Sets `topic_best2[tidx]`.
                    topic_best2[tidx] = float(s)
            # AUTO: Sets `ranked2`.
            ranked2 = sorted(topic_best2.items(), key=lambda x: -x[1])
            # AUTO: Checks this condition.
            if ranked2[0][1] >= _THRESHOLD:
                # AUTO: Sets `best_idx, best_score`.
                best_idx, best_score = ranked2[0]
                # AUTO: Sets `ranked`.
                ranked = ranked2
            # AUTO: Runs when previous condition did not pass.
            else:
                # AUTO: Returns this result to the caller.
                return _DEFAULT_RESPONSE
        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Returns this result to the caller.
            return _DEFAULT_RESPONSE

    # AUTO: Sets `result`.
    result = _responses[best_idx]
    # AUTO: Sets `has_blend`.
    has_blend = False

    # AUTO: Checks this condition.
    if len(ranked) >= 2:
        # AUTO: Sets `second_idx, second_score`.
        second_idx, second_score = ranked[1]
        # AUTO: Sets `gap`.
        gap = best_score - second_score
        # AUTO: Checks this condition.
        if second_score >= _THRESHOLD and gap < 0.07:
            # AUTO: Sets `transition`.
            transition = _random.choice(_BLEND_TRANSITIONS)
            # AUTO: Adds into `result`.
            result += transition + _responses[second_idx]
            # AUTO: Sets `has_blend`.
            has_blend = True

    # AUTO: Sets `result`.
    result = _wrap_response(result, best_score, intent, is_followup, has_blend)

    # AUTO: Sets `_last_topic_idx`.
    _last_topic_idx = best_idx
    # AUTO: Sets `_last_query`.
    _last_query = msg
    # AUTO: Appends a value to a list.
    _conv_history.append((msg, best_idx, best_score))
    # AUTO: Checks this condition.
    if len(_conv_history) > _MAX_HISTORY:
        # AUTO: Removes and returns an item.
        _conv_history.pop(0)

    # AUTO: Returns this result to the caller.
    return result
