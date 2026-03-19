# GAL Compiler — Comprehensive Knowledge Base

> **Auto-generated reference** covering every grammar production, token type, semantic rule, error message, and runtime behaviour extracted from the Backend source code.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Lexer — Token Types & Keywords](#2-lexer--token-types--keywords)
3. [CFG — All Grammar Productions](#3-cfg--all-grammar-productions)
4. [Parser — LL(1) Parsing & Error Messages](#4-parser--ll1-parsing--error-messages)
5. [Semantic Analyzer — All Rules & Error Messages](#5-semantic-analyzer--all-rules--error-messages)
6. [Interpreter — All Runtime Errors & Behaviour](#6-interpreter--all-runtime-errors--behaviour)
7. [ICG — Intermediate Code Generation](#7-icg--intermediate-code-generation)
8. [Quick-Reference: GAL ↔ Conventional Keyword Map](#8-quick-reference-gal--conventional-keyword-map)
9. [Limits & Constraints](#9-limits--constraints)
10. [AST Node Types](#10-ast-node-types)

---

## 1. Architecture Overview

```
Source (.gal)
     │
     ▼
┌─────────┐   tokens   ┌──────────┐  syntax ok?  ┌──────────────┐   AST   ┌─────────────┐
│  Lexer   │──────────▶│  Parser   │────────────▶│  Semantic     │───────▶│ Interpreter  │
│ lexer.py │           │Gal_Parser │             │GALsemantic.py│        │GALinterpreter│
└─────────┘           └──────────┘              └──────────────┘        └─────────────┘
                           │                                                   │
                           │  tokens (parallel)                                │
                           ▼                                                   │
                      ┌─────────┐                                              │
                      │  ICG    │ ← Three-Address Code                         │
                      │ icg.py  │                                              │
                      └─────────┘                                              │
                                                                               ▼
                                                                          Output / I/O
```

| Module | File | Lines | Role |
|--------|------|-------|------|
| Lexer | `lexer.py` | ~2000 | Hand-written char-by-char tokeniser |
| CFG | `cfg.py` | ~850 | Context-free grammar + FIRST/FOLLOW/PREDICT sets |
| Parser | `Gal_Parser.py` | ~1600 | LL(1) table-driven parser with rich error messages |
| Semantic Analyser | `GALsemantic.py` | ~4000 | AST builder + tree-walking semantic validator |
| Interpreter | `GALinterpreter.py` | ~1600 | Tree-walk interpreter with async I/O (socketio) |
| ICG | `icg.py` | ~1200 | Three-address code generator |

---

## 2. Lexer — Token Types & Keywords

### 2.1 Reserved Keywords (24)

| Keyword | Conventional Equivalent |
|---------|------------------------|
| `seed` | `int` |
| `tree` | `float` / `double` |
| `leaf` | `char` |
| `branch` | `bool` / `boolean` |
| `vine` | `string` |
| `empty` | `void` |
| `fertile` | `const` |
| `bundle` | `struct` |
| `root` | `main` |
| `pollinate` | `function` |
| `spring` | `if` |
| `bud` | `else if` / `elif` |
| `wither` | `else` |
| `grow` | `while` |
| `cultivate` | `for` |
| `tend` | `do` (do-while) |
| `harvest` | `switch` |
| `variety` | `case` |
| `soil` | `default` |
| `plant` | `print` / `printf` |
| `water` | `input` / `scanf` |
| `prune` | `break` |
| `skip` | `continue` |
| `reclaim` | `return` |

### 2.2 Boolean Literals

| Token | Value |
|-------|-------|
| `sunshine` | `true` |
| `frost` | `false` |

### 2.3 Operators

| Category | Tokens |
|----------|--------|
| Arithmetic | `+`, `-`, `*`, `/`, `%` |
| Exponent | `**` |
| Assignment | `=` |
| Compound assignment | `+=`, `-=`, `*=`, `/=`, `%=` |
| Comparison | `==`, `!=`, `<`, `>`, `<=`, `>=` |
| Strict equality | `===` (lexed, but generates parser error) |
| Logical | `&&`, `||`, `!` |
| Bitwise (single) | `&`, `|` |
| Unary | `~` (negation), `++`, `--` |
| String concat | `` ` `` (backtick) |
| Member access | `.` |

### 2.4 Delimiters

`(`, `)`, `{`, `}`, `[`, `]`, `;`, `,`, `:`

### 2.5 Literal Types

| Token Type | Description | Example |
|------------|-------------|---------|
| `intlit` | Integer literal | `42` |
| `dbllit` | Double/float literal | `3.14` |
| `stringlit` | String literal (double-quoted) | `"hello"` |
| `chrlit` | Character literal (single-quoted) | `'a'` |
| `~intlit` | Negated integer | `~5` → `-5` |
| `~dbllit` | Negated double | `~3.14` → `-3.14` |
| `sunshine` | Boolean `true` | `sunshine` |
| `frost` | Boolean `false` | `frost` |

### 2.6 Escape Sequences in Strings

`\n`, `\t`, `\\`, `\"`, `\{`, `\}`

### 2.7 Comments

- Single-line: `// ...`
- Multi-line: `/* ... */`

### 2.8 Lexer Error Messages

| Error | Trigger |
|-------|---------|
| `"Invalid delimiter 'X' after 'Y'"` | Unexpected delimiter following a token |
| `"Identifier exceeds maximum length of 15 characters"` | Identifier > 15 chars |
| `"Integer exceeds maximum of 8 digits"` | Integer portion > 8 digits |
| `"Fractional part exceeds maximum of 8 digits"` | Decimal portion > 8 digits |
| `"Missing closing '"' for string literal"` | Unclosed string |
| `"Missing closing quote for character literal"` | Unclosed char literal |
| `"Character literal must contain exactly one character"` | Multi-char in `'...'` |
| `"Illegal Character 'X'"` | Unknown/disallowed character |
| `"Identifiers cannot start with a number"` | e.g. `1abc` |
| `"Reserved word cannot start with a number/symbol"` | e.g. `1seed` |
| `"Invalid escape sequence"` | `\x` where `x` not recognised |
| `"Missing closing '*/' for multi-line comment"` | Unclosed `/* */` comment |

---

## 3. CFG — All Grammar Productions

Epsilon is represented as `λ`. Terminals are in **single quotes** or **lowercase**. Non-terminals are in `<angle brackets>`.

### 3.1 Program Structure

```
<program> → <global_declaration> <function_definition> root ( ) { <statement> }

<global_declaration> → <declaration> <global_declaration> | λ

<function_definition> → pollinate <return_type> id ( <parameters> ) { <statement> } <function_definition> | λ

<return_type> → <data_type> | empty
```

### 3.2 Declarations

```
<declaration> → <const_dec> | <var_dec> | <bundle_declaration>

<data_type> → seed | tree | leaf | branch | vine

<const_dec> → fertile <data_type> id = <const_value> ;

<const_value> → intlit | dbllit | stringlit | chrlit | sunshine | frost

<var_dec> → <data_type> <var_list> ;

<var_list> → id <var_init> <var_list_tail>

<var_list_tail> → , id <var_init> <var_list_tail> | λ

<var_init> → = <expression> | [ <expression> ] <array_init> | λ

<array_init> → = { <array_elements> } | λ

<array_elements> → <expression> <array_elements_tail> | λ

<array_elements_tail> → , <expression> <array_elements_tail> | λ
```

### 3.3 Bundle (Struct)

```
<bundle_declaration> → bundle id { <bundle_members> } ;

<bundle_members> → <data_type> id ; <bundle_members> | λ
```

### 3.4 Parameters

```
<parameters> → <data_type> id <param_tail> | λ

<param_tail> → , <data_type> id <param_tail> | λ
```

### 3.5 Statements

```
<statement> → <simple_stmt> ; <statement>
            | <conditional_stmt> <statement>
            | <loop_stmt> <statement>
            | <switch_stmt> <statement>
            | <declaration> <statement>
            | reclaim <return_expr> ; <statement>
            | λ

<simple_stmt> → <io_stmt>
              | <id_stmt>
              | prune
              | skip
              | <pre_update>

<id_stmt> → id <id_stmt_tail>

<id_stmt_tail> → <assignment_stmt>
               | ( <arguments> )
               | ++ | --
               | [ <expression> ] <array_assign>
               | . id <struct_tail>

<assignment_stmt> → <assign_op> <expression>

<assign_op> → = | += | -= | *= | /= | %=

<array_assign> → = <expression> | λ

<struct_tail> → = <expression> | . id <struct_tail>

<pre_update> → ++ id | -- id
```

### 3.6 I/O Statements

```
<io_stmt> → plant ( <print_args> ) | water ( id )

<print_args> → stringlit <print_extra_args> | <expression> <print_extra_args>

<print_extra_args> → , <expression> <print_extra_args> | λ
```

### 3.7 Conditional Statement

```
<conditional_stmt> → spring ( <expression> ) { <statement> } <else_chain>

<else_chain> → bud ( <expression> ) { <statement> } <else_chain>
             | wither { <statement> }
             | λ
```

### 3.8 Loop Statements

```
<loop_stmt> → <while_stmt> | <for_stmt> | <do_while_stmt>

<while_stmt> → grow ( <expression> ) { <statement> }

<for_stmt> → cultivate ( <for_init> ; <expression> ; <for_update> ) { <statement> }

<for_init> → <data_type> id = <expression> | id = <expression>

<for_update> → id <update_op> <for_update_tail>

<update_op> → ++ | -- | <assign_op> <expression>

<for_update_tail> → , id <update_op> <for_update_tail> | λ

<do_while_stmt> → tend { <statement> } grow ( <expression> ) ;
```

### 3.9 Switch Statement

```
<switch_stmt> → harvest ( <expression> ) { <case_list> <default_case> }

<case_list> → variety <const_value> : <statement> <case_list> | λ

<default_case> → soil : <statement> | λ
```

### 3.10 Expressions (operator precedence, lowest → highest)

```
<expression> → <logic_or>

<logic_or> → <logic_and> <logic_or_tail>
<logic_or_tail> → || <logic_and> <logic_or_tail> | λ

<logic_and> → <relational> <logic_and_tail>
<logic_and_tail> → && <relational> <logic_and_tail> | λ

<relational> → <arithmetic> <relational_tail>
<relational_tail> → <rel_op> <arithmetic> | λ
<rel_op> → == | != | < | > | <= | >=

<arithmetic> → <term> <arithmetic_tail>
<arithmetic_tail> → + <term> <arithmetic_tail>
                   | - <term> <arithmetic_tail>
                   | ` <term> <arithmetic_tail>
                   | λ

<term> → <factor> <term_tail>
<term_tail> → * <factor> <term_tail>
            | / <factor> <term_tail>
            | % <factor> <term_tail>
            | λ

<factor> → <unary_op> <factor>
         | ( <paren_expr> )
         | id <factor_id_next>
         | <literal>
         | ! <factor>
         | <cast_expr>

<unary_op> → ++ | -- | ~

<paren_expr> → <expression> ) <paren_tail>
<paren_tail> → <term_tail> <arithmetic_tail> <relational_tail> <logic_and_tail> <logic_or_tail> | λ

<factor_id_next> → ( <arguments> )
                  | [ <expression> ]
                  | . id
                  | ++ | --
                  | λ

<literal> → intlit | dbllit | stringlit | chrlit | sunshine | frost

<return_expr> → <expression> | λ

<arguments> → <expression> <arg_tail> | λ
<arg_tail> → , <expression> <arg_tail> | λ

<cast_expr> → <data_type> ( <expression> )
```

---

## 4. Parser — LL(1) Parsing & Error Messages

### 4.1 Parser Architecture

- **Type**: LL(1) table-driven parser
- **Class**: `LL1Parser` in `Gal_Parser.py`
- **Table**: Built from PREDICT sets computed in `cfg.py`
- **Recovery**: No error recovery — stops at first error
- **AST**: After syntax passes, calls `GALsemantic.build_ast()` for AST construction

### 4.2 Skip Tokens

The parser skips tokens of type `\n` (newlines) during parsing.

### 4.3 Syntax Error Format

```
SYNTAX error line {line} col {col} {message}. Expected: {expected_set}
```

### 4.4 Comprehensive Error Messages

#### 4.4.1 Operator Errors

| Pattern | Error Message |
|---------|---------------|
| `===` used | `"SYNTAX error line L col C '===' is not valid in GAL. Use '==' for comparison."` |
| `&&&` used | `"SYNTAX error line L col C '&&&' is not valid in GAL. Use '&&' for logical AND."` |
| <code>&#124;&#124;&#124;</code> used | `"SYNTAX error line L col C '\|\|\|' is not valid in GAL. Use '\|\|' for logical OR."` |
| Single `&` | `"SYNTAX error line L col C '&' is not valid in GAL. Use '&&' for logical AND."` |
| Single `\|` | `"SYNTAX error line L col C '\|' is not valid in GAL. Use '\|\|' for logical OR."` |

#### 4.4.2 Missing Delimiter Errors

| Pattern | Error Message |
|---------|---------------|
| Missing `;` | `"SYNTAX error line L col C Unexpected token 'X'. Expected ';'."` |
| Missing `}` | `"SYNTAX error line L col C Unexpected token 'X'. Missing closing brace."` |
| Missing `)` | `"SYNTAX error line L col C Unexpected token 'X'."` with expected `)` |
| Missing `:` after `variety` | `"SYNTAX error line L col C Unexpected token 'X' after 'variety'. Expected: {':'}."` |
| Missing `:` after `soil` | `"SYNTAX error line L col C Unexpected token 'X' after 'soil'. Expected: {':'}."` |

#### 4.4.3 Keyword Mistake Errors (Other languages → GAL)

The parser detects conventional keywords used by mistake and suggests GAL equivalents:

| Mistaken Keyword | GAL Equivalent | Error |
|------------------|----------------|-------|
| `if` | `spring` | `"'if' is not a GAL keyword. Use 'spring' instead."` |
| `else` | `wither` | `"'else' is not a GAL keyword. Use 'wither' instead."` |
| `elif` | `bud` | `"'elif' is not a GAL keyword. Use 'bud' instead."` |
| `while` | `grow` | `"'while' is not a GAL keyword. Use 'grow' instead."` |
| `for` | `cultivate` | `"'for' is not a GAL keyword. Use 'cultivate' instead."` |
| `switch` | `harvest` | `"'switch' is not a GAL keyword. Use 'harvest' instead."` |
| `case` | `variety` | `"'case' is not a GAL keyword. Use 'variety' instead."` |
| `default` | `soil` | `"'default' is not a GAL keyword. Use 'soil' instead."` |
| `break` | `prune` | `"'break' is not a GAL keyword. Use 'prune' instead."` |
| `continue` | `skip` | `"'continue' is not a GAL keyword. Use 'skip' instead."` |
| `return` | `reclaim` | `"'return' is not a GAL keyword. Use 'reclaim' instead."` |
| `int` | `seed` | `"'int' is not a GAL keyword. Use 'seed' instead."` |
| `float` / `double` | `tree` | `"'float'/'double' is not a GAL keyword. Use 'tree' instead."` |
| `char` | `leaf` | `"'char' is not a GAL keyword. Use 'leaf' instead."` |
| `bool` / `boolean` | `branch` | `"'bool'/'boolean' is not a GAL keyword. Use 'branch' instead."` |
| `string` | `vine` | `"'string' is not a GAL keyword. Use 'vine' instead."` |
| `void` | `empty` | `"'void' is not a GAL keyword. Use 'empty' instead."` |
| `const` | `fertile` | `"'const' is not a GAL keyword. Use 'fertile' instead."` |
| `struct` | `bundle` | `"'struct' is not a GAL keyword. Use 'bundle' instead."` |
| `function` | `pollinate` | `"'function' is not a GAL keyword. Use 'pollinate' instead."` |
| `printf` / `print` | `plant` | `"'printf'/'print' is not a GAL keyword. Use 'plant' instead."` |
| `scanf` / `input` | `water` | `"'scanf'/'input' is not a GAL keyword. Use 'water' instead."` |

#### 4.4.4 Type Mismatch in Declarations (caught at parse time)

```
SEMANTIC error line L col C Type mismatch in declaration of '{name}': 
  variable declared as '{type}' but assigned '{literal_type}' value(s).
```

Type-to-literal mappings enforced:

| Declared Type | Accepted Literals |
|---------------|-------------------|
| `seed` | `intlit`, `dbllit` |
| `tree` | `intlit`, `dbllit` |
| `leaf` | `chrlit` |
| `branch` | `sunshine`, `frost` |
| `vine` | `stringlit` |

#### 4.4.5 Character Literal Errors

| Pattern | Error |
|---------|-------|
| Empty char `''` | `"SEMANTIC error line L col C Empty character literal. Character literals must contain exactly one character."` |
| Multi-char `'abc'` | `"SEMANTIC error line L col C Invalid character literal: '{value}'. Character literals must contain exactly one character."` |

#### 4.4.6 Structural Errors

| Pattern | Error |
|---------|-------|
| Empty block `{}` | `"SYNTAX error line L col C Empty block. Expected at least one statement inside braces."` |
| Code after `reclaim` | `"SYNTAX error line L col C Unreachable code after 'reclaim'. Statements after a return will never execute."` |
| Chained `++`/`--` | `"SYNTAX error line L col C Unexpected token 'X' after 'Y'. Increment/decrement operators cannot be chained."` |
| Binary op after `++`/`--` | `"SYNTAX error line L col C Unexpected binary operator 'X' after unary operator 'Y'. Increment/decrement must be standalone statements."` |
| Missing return type | `"SYNTAX error line L col C Missing return type after 'pollinate'. '{name}' was parsed as the return type, not the function name."` |
| Missing param type | `"SYNTAX error line L col C Missing type for parameter '{name}'. Each parameter requires a type."` |
| Code after program end | `"SYNTAX error line L col C Unexpected token 'X' after program end. All code must be inside functions or global declarations."` |

---

## 5. Semantic Analyzer — All Rules & Error Messages

### 5.1 Error Format

```
Ln {line} Semantic Error: {message}
```

or simply:

```
Semantic Error: {message}
```

(The `SemanticError` class prepends `Ln {line}`)

### 5.2 Variable Declaration Rules

| Rule | Error Message |
|------|---------------|
| Variable already declared in scope | `"Semantic Error: Variable '{name}' already declared."` |
| Variable used before declaration | `"Semantic Error: Variable '{name}' used before declaration."` |
| Variable name conflicts with function | `"Semantic Error: '{name}' is already declared as a function."` |
| Multiple fertile declaration | `"Semantic Error: Multiple fertile declaration is not allowed."` |
| Invalid fertile type | `"Semantic Error: Invalid fertile variable type '{value}'."` |
| Fertile not initialised | `"Semantic Error: Fertile variables must be initialized."` |
| Fertile wrong literal type | `"Semantic Error: '{name}' must be initialized with a {type} literal."` |
| Fertile re-assignment | `"Semantic Error: Variable '{name}' is declared as fertile and cannot be re-assigned a value."` |

### 5.3 Type System Rules

| Rule | Error Message |
|------|---------------|
| Type mismatch on assignment | `"Semantic Error: Type Mismatch! Cannot assign {rhs_type} to variable '{name}' of type {lhs_type}."` |
| `seed`↔`tree` compatible | (no error — implicit numeric conversion) |
| Modulo requires seed operands | `"Semantic Error: Modulo operator '%' requires 'seed' (integer) operands."` |
| `!` only on branch | `"Semantic Error: '!' operator can only be used with 'branch' (boolean) values."` |
| Cannot compare incompatible types | `"Semantic Error: Cannot compare '{type1}' and '{type2}'."` |
| Concat requires vine | `"Semantic Error: Cannot concatenate non-vine with backtick."` |
| Compound assignment on non-numeric | `"Semantic Error: Cannot use compound assignment on '{name}' of type '{type}'."` |
| `%=` requires seed | `"Semantic Error: Modulo operator '%' requires 'seed' (integer) operands, but '{name}' is of type 'tree'."` |

### 5.4 Array & List Rules

| Rule | Error Message |
|------|---------------|
| Array size must be seed | `"Semantic Error: Array size must be of type 'seed' (integer)."` |
| List index must be seed | `"Semantic Error: List index must be of type 'seed', got '{type}'."` |
| Not a list | `"Semantic Error: '{name}' is not a list."` |
| List must be indexed | `"Semantic Error: List '{name}' must be indexed with '[]' in expressions."` |
| Missing closing bracket | `"Syntax Error: Missing closing bracket."` |

### 5.5 Function Rules

| Rule | Error Message |
|------|---------------|
| Function already declared | `"Semantic Error: Function '{name}' already declared."` |
| Function not declared/defined | `"Semantic Error: Function '{name}' is not declared."` / `"...is not defined."` |
| Argument count mismatch | `"Semantic Error: Function '{name}' expects {n} argument(s), got {m}."` |
| Argument type mismatch | `"Semantic Error: Argument {i} of function '{name}': expected '{expected}', got '{actual}'."` |
| Empty function must not return value | `"Semantic Error: empty function must not return any value."` |
| Non-empty function missing return expr | `"Semantic Error: Function expects to return a '{type}' value, but 'reclaim' has no return expression."` |
| Return type mismatch | `"Semantic Error: Function '{name}' returns '{actual}', but expected '{expected}'."` |
| Variable type doesn't match return | `"Semantic Error: Variable '{name}' is of type '{var_type}'. Expected return value: '{func_type}'."` |
| Not all paths return | `"Semantic Error: Function '{name}' must return a value on all code paths."` |
| All functions must end with reclaim | `"Semantic Error: Function '{name}' must end with 'reclaim'."` |
| `water()` used as expression | `"Semantic Error: 'water()' is an I/O statement, not a value expression."` |

### 5.6 Control Flow Rules

| Rule | Error Message |
|------|---------------|
| `spring` condition not branch | `"Semantic Error: spring condition must be branch, got {type}."` |
| `bud` condition not branch | `"Semantic Error: bud condition must be branch, got {type}."` |
| `grow` condition not branch | `"Semantic Error: grow condition must be branch, got {type}."` |
| `tend` condition not branch | `"Semantic Error: tend condition must be branch, got {type}."` |
| `cultivate` condition not branch | `"Semantic Error: cultivate condition must be branch, got {type}."` |
| `prune` outside loop/switch | `"Semantic Error: 'prune' used outside a loop or switch."` |
| `skip` outside loop | `"Semantic Error: 'skip' used outside a loop."` |

### 5.7 Switch (Harvest) Rules

| Rule | Error Message |
|------|---------------|
| Harvest expr must be seed/leaf/branch | `"Semantic Error: 'harvest' expression must be 'seed'/'leaf'/'branch', not '{type}'."` |
| Variety type mismatch | `"Semantic Error: 'variety' value type mismatch — expected '{switch_type}' but got '{lit_type}' ('{value}')."` |
| Duplicate variety value | `"Semantic Error: Duplicate 'variety' value '{value}' in 'harvest'."` |

### 5.8 Bundle (Struct) Rules

| Rule | Error Message |
|------|---------------|
| Bundle type not defined | `"Semantic Error: Bundle type '{name}' is not defined."` |
| Duplicate bundle member | `"Semantic Error: Duplicate member '{name}' in bundle."` |
| Bundle missing name | `"Semantic Error: Bundle definition missing name."` |

### 5.9 Built-in Function Rules

| Rule | Error Message |
|------|---------------|
| `ts()` on non-list/string | `"Semantic Error: 'ts()' can only be used on lists or vines."` |
| `taper()` on non-leaf | `"Semantic Error: 'taper()' can only be used on 'leaf' type."` |
| `plant()` > 15 args | `"Semantic Error: Exceeded maximum amount of 15 arguments in plant statement."` |
| `plant()` placeholder mismatch | `"Semantic Error: Found {n} argument(s). Expected {m} argument(s)."` |
| Invalid string in `plant()` | `"Semantic Error: Invalid string literal '{str}' in plant()."` |
| Placeholders not adjacent | `"Syntax Error: Placeholders {} must be adjacent to each other within the string literal."` |
| Concat non-vine in `plant()` | `"Semantic Error: Only values of type vine can be concatenated in plant()."` |
| Concat non-leaf var | `"Semantic Error: Variable '{name}' with type {type} cannot be concatenated in plant()."` |

### 5.10 Syntax Errors Raised by Semantic Analyser

These are `"Syntax Error: ..."` messages raised during AST construction:

| Error |
|-------|
| `"Syntax Error: Expected '(' after 'spring'."` |
| `"Syntax Error: Expected ')' after 'spring' condition."` |
| `"Syntax Error: Expected '{' after 'spring' condition."` |
| `"Syntax Error: Expected '}' after 'spring' block."` |
| `"Syntax Error: Expected '(' after else-if."` |
| `"Syntax Error: Expected ')' after else-if condition."` |
| `"Syntax Error: Expected '{' after else-if condition."` |
| `"Syntax Error: Expected '(' after 'grow'."` |
| `"Syntax Error: Expected ')' after 'grow' condition."` |
| `"Syntax Error: Expected '{' after 'grow' condition."` |
| `"Syntax Error: Expected '{' after 'tend'."` |
| `"Syntax Error: Expected 'grow' after 'tend' block."` |
| `"Syntax Error: Expected '(' after 'cultivate'."` |
| `"Syntax Error: Expected '=' after for loop identifier."` |
| `"Syntax Error: Expected ';' after for loop initialization."` |
| `"Syntax Error: Expected ';' after for loop condition."` |
| `"Syntax Error: Expected ')' after for loop update."` |
| `"Syntax Error: Expected '{' after for loop condition."` |
| `"Syntax Error: Expected '(' after 'harvest'."` |
| `"Syntax Error: Expected ')' after 'harvest' expression."` |
| `"Syntax Error: Expected '{' after 'harvest' expression."` |
| `"Syntax Error: Expected '}' after 'harvest' statement."` |
| `"Syntax Error: Expected ':' after 'variety' value."` |
| `"Syntax Error: Expected ':' after 'soil'."` |
| `"Syntax Error: Expected identifier after '{type}'."` |
| `"Syntax Error: Expected identifier after '{operator}'."` |
| `"Syntax Error: Expected '(' after 'append'."` |
| `"Syntax Error: Expected ')' after append arguments."` |
| `"Syntax Error: Expected '(' after 'insert'."` |
| `"Syntax Error: Expected ',' after index in 'insert'."` |
| `"Syntax Error: Expected ')' after insert arguments."` |
| `"Syntax Error: Expected '(' after 'remove'."` |
| `"Syntax Error: Expected ')' after remove argument."` |
| `"Syntax Error: Expected '[' for list declaration."` |
| `"Syntax Error: Expected ']' after list elements."` |

---

## 6. Interpreter — All Runtime Errors & Behaviour

### 6.1 Error Format

```
Ln {line} Runtime Error: {message}
```

or:

```
Ln {line} Semantic Error: {message}
```

(The interpreter raises some errors labelled "Semantic Error" at runtime)

### 6.2 Runtime Error Catalogue

#### Arithmetic Errors

| Error |
|-------|
| `"Runtime Error: Division by zero is undefined"` |
| `"Runtime Error: Evaluated number exceeds maximum number of 16 digits"` |

#### Loop Protection

| Error |
|-------|
| `"Runtime Error: Infinite loop detected!"` (after 10,000 iterations) |

#### Type Errors

| Error |
|-------|
| `"Runtime Error: Condition must be a boolean. Got '{value}'"` |
| `"Runtime Error: List index must be an integer. Got '{index}'"` |
| `"Runtime Error: Expected integer value, got '{value}'"` |
| `"Runtime Error: Expected float value, got '{value}'"` |
| `"Runtime Error: Expected branch value, got '{value}'"` |
| `"Runtime Error: Expected leaf value, got '{value}'"` |
| `"Runtime Error: Input value exceeds maximum number of 16 digits"` |

#### List/Array Errors

| Error |
|-------|
| `"Runtime Error: Index '{idx}' out of bounds for list '{name}'"` |
| `"Runtime Error: Variable '{name}' is not a list"` |
| `"Runtime Error: Cannot index into a non-list value"` |
| `"Runtime Error: Insert index must be an integer"` |
| `"Runtime Error: Remove index must be an integer"` |
| `"Runtime Error: Index N out of range for insert"` |
| `"Runtime Error: Index N out of bounds for remove"` |

#### Bundle (Struct) Errors

| Error |
|-------|
| `"Runtime Error: Value is not a bundle"` |
| `"Runtime Error: Array element is not a bundle"` |
| `"Runtime Error: Bundle has no member '{name}'"` |
| `"Runtime Error: Member '{name}' is not a bundle"` |

#### Function Errors

| Error |
|-------|
| `"Runtime Error: Function '{name}' expects N argument(s), got M"` |
| `"Runtime Error: Break statement used outside of a loop"` |
| `"Runtime Error: Continue statement used outside of a loop"` |

#### Variable Errors (raised at runtime as "Semantic Error")

| Error |
|-------|
| `"Semantic Error: Type Mismatch! Invalid value for {name}"` |
| `"Semantic Error: Variable '{name}' already declared"` |
| `"Semantic Error: Variable '{name}' not declared"` |
| `"Semantic Error: Variable '{name}' used before declaration"` |
| `"Semantic Error: Function '{name}' already declared"` |
| `"Semantic Error: Function '{name}' is not defined"` |

### 6.3 Interpreter Behaviour Notes

| Feature | Behaviour |
|---------|-----------|
| **MAX_LOOP_ITERATIONS** | 10,000 |
| **MAX_DIGITS** | 16 digits for any evaluated number |
| **Float display** | Truncated to 5 decimal places, trailing zeros stripped |
| **`seed`↔`tree` coercion** | Implicit — `seed` vars can hold `tree` values and vice versa |
| **String interpolation** | `plant("Hello {}", name)` — `{}` replaced by args positionally |
| **Async I/O** | Uses `socketio` + `eventlet` for non-blocking `water()` input |
| **Scope** | Stack-based — `enter_scope()` pushes, `exit_scope()` pops |
| **Global scope** | Separate `global_variables` dict accessible from all functions |
| **Type casting** | `seed(x)` → `int`, `tree(x)` → `float`, `leaf(x)` → `chr`/first char, `branch(x)` → `bool`, `vine(x)` → `str` |
| **`taper(x)`** | Splits a `leaf` (char/string) into a list of individual characters |
| **`ts(x)`** | Returns length of list or string |
| **`++`/`--`** | Pre and post increment/decrement; pre returns new value, post returns old |

---

## 7. ICG — Intermediate Code Generation

### 7.1 Architecture

- **Input**: Token stream (parallel to semantic analysis)
- **Output**: List of `TACInstruction` objects (three-address code)
- **Format**: `(op, arg1, arg2, result)`

### 7.2 GAL → TAC Type Map

| GAL Type | TAC Type |
|----------|----------|
| `seed` | `int` |
| `tree` | `float` |
| `leaf` | `char` |
| `branch` | `bool` |
| `vine` | `string` |
| `empty` | `void` |

### 7.3 TAC Instruction Types

| Instruction | Format |
|-------------|--------|
| `DECLARE` | `(DECLARE, type, _, name)` |
| `ASSIGN` | `(=, value, _, name)` |
| `CONST` | `(CONST, type, value, name)` |
| `ARRAY_DECLARE` | `(ARRAY_DECLARE, type, size, name)` |
| `ARRAY_STORE` | `(ARRAY_STORE, value, index, name)` |
| `ARRAY_LOAD` | `(ARRAY_LOAD, name, index, temp)` |
| `STRUCT_STORE` | `(STRUCT_STORE, value, member, name)` |
| `STRUCT_LOAD` | `(STRUCT_LOAD, name, member, temp)` |
| Binary ops | `(op, left, right, temp)` — where op is `+`,`-`,`*`,`/`,`%`,`==`,`!=`,`<`,`>`,`<=`,`>=`,`&&`,`\|\|` |
| `UNARY_MINUS` | `(UNARY_MINUS, arg, _, temp)` |
| `NOT` | `(NOT, arg, _, temp)` |
| `INC` / `DEC` | `(INC/DEC, name, _, name)` |
| `LABEL` | `(LABEL, _, _, label_name)` |
| `GOTO` | `(GOTO, _, _, label_name)` |
| `IF` | `(IF, condition, _, label_name)` |
| `IFFALSE` | `(IFFALSE, condition, _, label_name)` |
| `PARAM` | `(PARAM, _, _, arg_value)` |
| `CALL` | `(CALL, func_name, arg_count, result_temp)` |
| `RETURN` | `(RETURN, _, _, value)` |
| `FUNC` | `(FUNC, _, _, func_name)` |
| `ENDFUNC` | `(ENDFUNC, _, _, func_name)` |
| `PRINT` | `(PRINT, _, _, value)` |
| `READ` | `(READ, type, _, name)` |

### 7.4 ICG Error Format

```
ICG Line {N}: expected '{X}', got '{Y}'
ICG internal error: {message}
```

### 7.5 Public API

```python
generate_icg(tokens) → {
    "success": bool,
    "tac": List[TACInstruction],
    "tac_text": str,           # human-readable output
    "errors": List[str]
}
```

---

## 8. Quick-Reference: GAL ↔ Conventional Keyword Map

| Conventional | GAL | Category |
|-------------|-----|----------|
| `int` | `seed` | Data type |
| `float`/`double` | `tree` | Data type |
| `char` | `leaf` | Data type |
| `bool` | `branch` | Data type |
| `string` | `vine` | Data type |
| `void` | `empty` | Return type |
| `const` | `fertile` | Modifier |
| `struct` | `bundle` | Aggregate type |
| `true` | `sunshine` | Boolean literal |
| `false` | `frost` | Boolean literal |
| `main` | `root` | Entry point |
| `function` | `pollinate` | Function declaration |
| `return` | `reclaim` | Return statement |
| `if` | `spring` | Conditional |
| `else if` | `bud` | Conditional |
| `else` | `wither` | Conditional |
| `while` | `grow` | Loop |
| `for` | `cultivate` | Loop |
| `do` | `tend` | Loop (do-while) |
| `switch` | `harvest` | Switch |
| `case` | `variety` | Switch case |
| `default` | `soil` | Switch default |
| `break` | `prune` | Control flow |
| `continue` | `skip` | Control flow |
| `print` | `plant` | I/O |
| `input`/`scanf` | `water` | I/O |
| `len()` | `ts()` | Built-in |
| `split('')` | `taper()` | Built-in |
| `.append()` | `.append()` | List method |
| `.insert()` | `.insert()` | List method |
| `.remove()` | `.remove()` | List method |

---

## 9. Limits & Constraints

| Constraint | Value |
|------------|-------|
| Max identifier length | 15 characters |
| Max integer digits | 8 digits |
| Max fractional digits | 8 digits |
| Max evaluated number digits (runtime) | 16 digits |
| Max loop iterations | 10,000 |
| Max `plant()` arguments | 15 |
| Float display precision | 5 decimal places |
| String escape sequences | `\n`, `\t`, `\\`, `\"`, `\{`, `\}` |

---

## 10. AST Node Types

All node types used in the AST produced by `GALsemantic.py`:

| Node Class | Purpose |
|-----------|---------|
| `ASTNode` | Generic node (type, value, children) |
| `ProgramNode` | Root of AST |
| `VariableDeclarationNode` | Variable declaration |
| `FertileDeclarationNode` | Constant declaration |
| `AssignmentNode` | Assignment statement |
| `BinaryOpNode` | Binary operation (e.g., `a + b`) |
| `UnaryOpNode` | Unary operation (`++`, `--`, `~`, `!`) |
| `FunctionDeclarationNode` | Function definition |
| `FunctionCallNode` | Function call |
| `IfStatementNode` | `spring`/`bud`/`wither` |
| `ForLoopNode` | `cultivate` loop |
| `WhileLoopNode` | `grow` loop |
| `DoWhileLoopNode` | `tend`...`grow` loop |
| `SwitchNode` | `harvest` statement |
| `PrintNode` | `plant()` output |
| `ReturnNode` | `reclaim` statement |
| `UpdateNode` | For-loop update clause |
| `ContinueNode` | `skip` |
| `BreakNode` | `prune` |
| `ListNode` | List literal `[a, b, c]` |
| `ListAccessNode` | List indexing `x[i]` |
| `AppendNode` | `.append()` call |
| `InsertNode` | `.insert()` call |
| `RemoveNode` | `.remove()` call |
| `CastNode` | Type cast `seed(x)` |
| `TaperNode` | `taper()` call |
| `TSNode` | `ts()` call |
| `MemberAccessNode` | Bundle member `.member` |
| `ArrayMemberAccessNode` | Array element member access |
| `BundleDefinitionNode` | `bundle` definition |

---

*End of Knowledge Base*
