# GAL Compiler — Full System Documentation

> **GAL (Grow A Language)** is a custom programming language with a garden/nature theme. This document covers the complete compilation pipeline: architecture, lexical analysis, context-free grammar, parsing, semantic analysis, intermediate code generation, interpretation, and the web-based UI.

---

## Table of Contents

1. [System Architecture & Flow](#1-system-architecture--flow)
2. [Lexical Analysis (Lexer)](#2-lexical-analysis-lexer)
3. [Context-Free Grammar (CFG)](#3-context-free-grammar-cfg)
4. [Syntax Analysis (Parser)](#4-syntax-analysis-parser)
5. [Semantic Analysis](#5-semantic-analysis)
6. [Intermediate Code Generation (ICG)](#6-intermediate-code-generation-icg)
7. [Interpreter](#7-interpreter)
8. [NLP Fallback / AI Chat Assistant](#8-nlp-fallback--ai-chat-assistant)
9. [Web Interface & Server](#9-web-interface--server)
10. [General Rules & Constraints](#10-general-rules--constraints)
11. [Keyword Reference: GAL ↔ Conventional](#11-keyword-reference-gal--conventional)
12. [AST Node Types Reference](#12-ast-node-types-reference)
13. [Complete Error Catalogue](#13-complete-error-catalogue)

---

## 1. System Architecture & Flow

### 1.1 High-Level Pipeline

The GAL compiler follows a **classic multi-phase compilation pipeline**. Each phase validates its input and passes structured output to the next phase. If any phase encounters an error, the pipeline halts and reports the error to the user.

```
 ┌────────────────────────────────────────────────────────────────────────────┐
 │                          GAL Source Code (.gal)                           │
 └──────────────────────────────────┬─────────────────────────────────────────┘
                                    │
                                    ▼
 ┌──────────────────────────────────────────────────────────────────────────┐
 │  PHASE 1: LEXICAL ANALYSIS  (lexer.py)                                  │
 │  • Reads source code character-by-character                              │
 │  • Groups characters into tokens (keywords, identifiers, literals, etc.) │
 │  • Validates delimiters after each token                                 │
 │  • Detects lexical errors (illegal chars, unclosed strings, etc.)        │
 │  Output: Token Stream  [Token(type, value, line, col), ...]              │
 └──────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
 ┌──────────────────────────────────────────────────────────────────────────┐
 │  PHASE 2: SYNTAX ANALYSIS  (Gal_Parser.py + cfg.py)                     │
 │  • LL(1) table-driven predictive parser                                  │
 │  • Uses FIRST, FOLLOW, PREDICT sets computed from CFG                    │
 │  • Validates token sequence against grammar productions                  │
 │  • Detects syntax errors with helpful, context-aware messages            │
 │  • Detects conventional keyword misuse (e.g., "if" → "spring")          │
 │  Output: Validated token stream (syntax is correct)                      │
 └──────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
 ┌──────────────────────────────────────────────────────────────────────────┐
 │  PHASE 3: SEMANTIC ANALYSIS  (GALsemantic.py)                           │
 │  • Builds Abstract Syntax Tree (AST) from token stream                   │
 │  • Tree-walking validation of the AST                                    │
 │  • Type checking, scope validation, function signature checking          │
 │  • Detects semantic errors (type mismatch, undeclared vars, etc.)        │
 │  Output: Validated AST + Symbol Table                                    │
 └──────────────┬───────────────────────────────────────────┬───────────────┘
                │                                           │
                ▼                                           ▼
 ┌──────────────────────────┐              ┌────────────────────────────────┐
 │  PHASE 4A: ICG (icg.py)  │              │  PHASE 4B: INTERPRETER         │
 │  • Three-Address Code     │              │  (GALinterpreter.py)           │
 │  • Quad format            │              │  • Tree-walk interpreter       │
 │  • (op, arg1, arg2, res)  │              │  • Executes AST nodes          │
 │  Output: TAC instructions │              │  • Async I/O via WebSocket     │
 └──────────────────────────┘              │  Output: Program output        │
                                           └────────────────────────────────┘
```

### 1.2 Module Inventory

| Module | File | Approx. Lines | Responsibility |
|--------|------|---------------|----------------|
| Lexer | `Backend/lexer.py` | ~2000 | Hand-written character-by-character tokenizer |
| CFG | `Backend/cfg.py` | ~850 | Context-free grammar definition + FIRST/FOLLOW/PREDICT computation |
| Parser | `Backend/Gal_Parser.py` | ~1600 | LL(1) table-driven parser with rich error messages |
| Semantic Analyzer | `Backend/GALsemantic.py` | ~4000 | AST construction + tree-walking semantic validation |
| Interpreter | `Backend/GALinterpreter.py` | ~1600 | Tree-walk interpreter with async I/O (Socket.IO) |
| ICG | `Backend/icg.py` | ~1200 | Three-address code generator from token stream |
| Server | `Backend/server.py` | ~600 | Flask + Socket.IO web server with REST API endpoints |
| NLP Fallback | `Backend/gal_fallback.py` | ~800 | Regex + semantic-search AI chat assistant for error help |
| Frontend | `UI/index.html`, `UI/style.pixel.css`, `UI/main.js` | — | Web-based code editor UI |

### 1.3 How the Phases Connect (Server Flow)

When the user clicks **"Run"** in the web UI:

1. The frontend sends the source code to the server via **Socket.IO** (`run_code` event) or **REST API** (`/api/run`).
2. **Lexer** tokenizes the code → if errors, stop and return lexical errors.
3. **Parser** validates syntax using LL(1) table → if errors, stop and return syntax errors.
4. **Semantic Analyzer** builds AST and validates types/scopes → if errors, stop and return semantic errors.
5. **Interpreter** executes the AST → streams output back via Socket.IO events.
6. If `water()` (input) is called, the server emits `input_required` and waits for user response.

For **ICG** (intermediate code generation), the pipeline is:
Lexer → Parser → Semantic → ICG (generates three-address code from tokens in parallel).

---

## 2. Lexical Analysis (Lexer)

**File:** `Backend/lexer.py` (~2000 lines)

### 2.1 How It Works

The lexer is a **hand-written, character-by-character scanner** (not using regex or generator tools like Lex/Flex). It works as follows:

1. The source code string is scanned one character at a time using a `Position` tracker (index, line, column).
2. For each character, the lexer determines what token it could start:
   - **Letters** → could be a keyword or identifier
   - **Digits** → integer or double literal
   - **Quote characters** → string or character literal
   - **Operator characters** → single or multi-character operator
   - **Whitespace** → skipped (except newlines, which are emitted as `\n` tokens)
3. Keywords are recognized by **character-by-character matching** (e.g., `s` → `se` → `see` → `seed` → check delimiter). If the full keyword is matched and followed by a valid delimiter, it's emitted as a keyword token. Otherwise, it falls through to identifier parsing.
4. After each token is recognized, the lexer checks the **delimiter** — the character immediately following the token — to ensure it's valid for that token type. Invalid delimiters produce a lexical error.

### 2.2 Character Sets

| Constant | Characters | Purpose |
|----------|-----------|---------|
| `ZERO` | `0` | Special case for leading zeros |
| `DIGIT` | `123456789` | Non-zero digits |
| `ZERODIGIT` | `0123456789` | All digits |
| `LOW_ALPHA` | `a-z` | Lowercase letters |
| `UPPER_ALPHA` | `A-Z` | Uppercase letters |
| `ALPHA` | `a-zA-Z` | All letters |
| `ALPHANUM` | `a-zA-Z0-9_` | Valid identifier characters |

### 2.3 Reserved Keywords (24 keywords)

GAL uses a garden/nature theme for all its keywords:

| GAL Keyword | Conventional Equivalent | Category | Description |
|-------------|------------------------|----------|-------------|
| `seed` | `int` | Data Type | Integer type |
| `tree` | `float` / `double` | Data Type | Floating-point type |
| `leaf` | `char` | Data Type | Character type |
| `branch` | `bool` / `boolean` | Data Type | Boolean type |
| `vine` | `string` | Data Type | String type |
| `empty` | `void` | Return Type | Void return type |
| `fertile` | `const` | Modifier | Constant declaration |
| `bundle` | `struct` | Aggregate | Struct/record type |
| `root` | `main` | Entry Point | Main function |
| `pollinate` | `function` | Function | Function declaration keyword |
| `spring` | `if` | Conditional | If statement |
| `bud` | `else if` / `elif` | Conditional | Else-if statement |
| `wither` | `else` | Conditional | Else statement |
| `grow` | `while` | Loop | While loop |
| `cultivate` | `for` | Loop | For loop |
| `tend` | `do` | Loop | Do-while loop start |
| `harvest` | `switch` | Switch | Switch statement |
| `variety` | `case` | Switch | Case label |
| `soil` | `default` | Switch | Default case |
| `plant` | `print` / `printf` | I/O | Output function |
| `water` | `input` / `scanf` | I/O | Input function |
| `prune` | `break` | Control Flow | Break out of loop/switch |
| `skip` | `continue` | Control Flow | Skip to next iteration |
| `reclaim` | `return` | Control Flow | Return from function |

### 2.4 Boolean Literals

| Token | Meaning |
|-------|---------|
| `sunshine` | Boolean `true` |
| `frost` | Boolean `false` |

### 2.5 Token Types

The lexer produces the following token categories:

#### 2.5.1 Literal Tokens

| Token Type | Description | Example |
|------------|-------------|---------|
| `intlit` | Integer literal (max 8 digits) | `42`, `100` |
| `dbllit` | Double/float literal (max 8.8 digits) | `3.14`, `2.5` |
| `stringlit` | String literal (double-quoted) | `"hello world"` |
| `chrlit` | Character literal (single-quoted, exactly 1 char) | `'a'`, `'Z'` |
| `~intlit` | Negated integer literal | `~5` → `-5` |
| `~dbllit` | Negated double literal | `~3.14` → `-3.14` |
| `sunshine` | Boolean true literal | `sunshine` |
| `frost` | Boolean false literal | `frost` |

#### 2.5.2 Operator Tokens

| Token | Type | Description |
|-------|------|-------------|
| `+` | Arithmetic | Addition |
| `-` | Arithmetic | Subtraction |
| `*` | Arithmetic | Multiplication |
| `/` | Arithmetic | Division |
| `%` | Arithmetic | Modulo (remainder) |
| `**` | Arithmetic | Exponentiation |
| `~` | Unary | Negation (replaces unary minus) |
| `++` | Unary | Increment |
| `--` | Unary | Decrement |
| `=` | Assignment | Simple assignment |
| `+=` | Assignment | Add and assign |
| `-=` | Assignment | Subtract and assign |
| `*=` | Assignment | Multiply and assign |
| `/=` | Assignment | Divide and assign |
| `%=` | Assignment | Modulo and assign |
| `==` | Comparison | Equality |
| `!=` | Comparison | Not equal |
| `<` | Comparison | Less than |
| `>` | Comparison | Greater than |
| `<=` | Comparison | Less than or equal |
| `>=` | Comparison | Greater than or equal |
| `&&` | Logical | Logical AND |
| `\|\|` | Logical | Logical OR |
| `!` | Logical | Logical NOT |
| `` ` `` | String | Concatenation operator |
| `.` | Access | Struct member access |

#### 2.5.3 Delimiter Tokens

| Token | Description |
|-------|-------------|
| `(` | Left parenthesis |
| `)` | Right parenthesis |
| `{` | Left brace (block start) |
| `}` | Right brace (block end) |
| `[` | Left bracket (array indexing) |
| `]` | Right bracket |
| `;` | Semicolon (statement terminator) |
| `,` | Comma (separator) |
| `:` | Colon (switch cases) |

#### 2.5.4 Special Tokens

| Token | Description |
|-------|-------------|
| `\n` | Newline (skipped by parser) |
| `EOF` | End of file marker |
| `id` | Identifier (variable/function name) |

### 2.6 Delimiter Validation

A key feature of the GAL lexer is **post-token delimiter checking**. After recognizing each token, the lexer verifies that the character immediately following the token is valid for that token type. For example:

- After `seed` (data type keyword): must be followed by a space, tab, or newline
- After `bud` (else-if): must be followed by whitespace, `:`, or `(`
- After an identifier: must be followed by a space, comma, semicolon, operator, bracket, etc.
- After an integer literal: must be followed by a semicolon, operator, closing bracket, etc.

This catches errors like `seedx` (missing space) or `42abc` (identifier starting with a digit).

### 2.7 Escape Sequences in Strings

| Sequence | Meaning |
|----------|---------|
| `\n` | Newline |
| `\t` | Tab |
| `\\` | Backslash |
| `\"` | Double quote |
| `\{` | Literal left brace |
| `\}` | Literal right brace |

### 2.8 Comments

| Syntax | Type |
|--------|------|
| `// ...` | Single-line comment (until end of line) |
| `/* ... */` | Multi-line comment (must be closed) |

### 2.9 Identifier Rules

- Must start with a **letter** (a-z, A-Z)
- Can contain letters, digits (0-9), and underscore (`_`)
- **Maximum length: 15 characters**
- Cannot be a reserved keyword
- Cannot start with a digit

### 2.10 Number Literal Rules

- **Integers**: Maximum 8 digits. No leading zeros (except `0` itself).
- **Doubles/Floats**: Integer part max 8 digits + decimal point + fractional part max 8 digits.
- **Negative numbers**: Use the `~` prefix (e.g., `~5` for -5, `~3.14` for -3.14).

### 2.11 Lexer Error Messages

| Error | Trigger |
|-------|---------|
| `"Invalid delimiter 'X' after 'Y'"` | Unexpected character following a token |
| `"Identifier exceeds maximum length of 15 characters"` | Identifier > 15 chars |
| `"Integer exceeds maximum of 8 digits"` | Integer portion > 8 digits |
| `"Fractional part exceeds maximum of 8 digits"` | Decimal portion > 8 digits |
| `"Missing closing '"' for string literal"` | Unclosed string |
| `"Missing closing quote for character literal"` | Unclosed char literal |
| `"Character literal must contain exactly one character"` | Multi-char in `'...'` |
| `"Illegal Character 'X'"` | Unknown/disallowed character |
| `"Identifiers cannot start with a number"` | e.g., `1abc` |
| `"Invalid escape sequence"` | `\x` where `x` is not recognized |
| `"Missing closing '*/' for multi-line comment"` | Unclosed `/* */` |

---

## 3. Context-Free Grammar (CFG)

**File:** `Backend/cfg.py` (~850 lines)

### 3.1 What Is the CFG?

The **Context-Free Grammar (CFG)** formally defines the syntax of the GAL language. It specifies which arrangements of tokens are valid programs. The CFG is used to build the **LL(1) parsing table** that drives the parser.

### 3.2 Notation

- **Non-terminals**: Enclosed in angle brackets, e.g., `<program>`, `<expression>`
- **Terminals**: Actual token types from the lexer, e.g., `seed`, `id`, `{`, `;`
- **λ (lambda/epsilon)**: Represents an empty production (the rule can produce nothing)
- **|**: Separates alternatives (multiple productions for the same non-terminal)

### 3.3 FIRST, FOLLOW, and PREDICT Sets

The CFG module computes three critical sets used for LL(1) parsing:

**FIRST(X)** — the set of terminals that can appear at the **beginning** of any string derived from non-terminal X.
- Example: `FIRST(<data_type>) = {seed, tree, leaf, branch, vine}`

**FOLLOW(X)** — the set of terminals that can appear **immediately after** non-terminal X in any derivation.
- Example: `FOLLOW(<statement>) includes }, EOF`

**PREDICT(A → α)** — the set of terminals that indicate which production to use:
- If α does NOT derive λ: `PREDICT = FIRST(α)`
- If α CAN derive λ: `PREDICT = FIRST(α) ∪ FOLLOW(A)`

These sets are computed automatically by `compute_first()`, `compute_follow()`, and `compute_predict()` in `cfg.py`.

### 3.4 Complete Grammar Productions

#### 3.4.1 Program Structure

```
<program> → <global_declaration> <function_definition> root ( ) { <statement> }
```

Every GAL program must have a `root()` function as its entry point (equivalent to `main()` in C).

#### 3.4.2 Global Declarations

```
<global_declaration> → bundle id <bundle_or_var> <global_declaration>
                      | <data_type> id <array_dec> <var_value> ; <global_declaration>
                      | fertile <data_type> id = <init_val> <const_next> ; <global_declaration>
                      | λ
```

#### 3.4.3 Data Types

```
<data_type> → seed | tree | leaf | branch | vine
```

#### 3.4.4 Variable Declarations

```
<var_dec> → <data_type> id <array_dec> <var_value>
          | bundle id <bundle_mem_dec>

<var_value> → = <init_val> <var_value_next>
            | <var_value_next>

<var_value_next> → , id <array_dec> <var_value>
                 | λ

<init_val> → <array_init_opt>
           | water ( <water_arg> )
           | <expression>
```

Multiple variables can be declared in one statement: `seed x = 1, y = 2, z;`

#### 3.4.5 Constant Declarations

```
<const_dec> → fertile <data_type> id = <init_val> <const_next>

<const_next> → , id = <init_val> <const_next>
             | λ
```

Example: `fertile seed MAX = 100;`

#### 3.4.6 Array Declarations

```
<array_dec> → [ <array_dim_opt> ] <array_dec>
            | λ

<array_dim_opt> → intlit | λ
```

Supports multi-dimensional arrays: `seed matrix[2][3];`

#### 3.4.7 Array Initialization

```
<array_init_opt> → { <init_vals> }
                 | λ

<init_vals> → <init_val_item> <init_vals_next>
            | λ

<init_val_item> → { <init_vals> }
               | <expression>
```

Example: `seed arr[] = {1, 2, 3};` or nested: `seed m[][] = {{1, 2}, {3, 4}};`

#### 3.4.8 Bundle (Struct) Definition

```
<bundle_declaration> → bundle id { <bundle_members> }

<bundle_members> → <data_type> id ; <bundle_members>
                 | id id ; <bundle_members>
                 | λ
```

Example:
```
bundle Person {
    seed age;
    vine name;
};
```

#### 3.4.9 Function Definition

```
<function_definition> → pollinate <return_type> id ( <parameters> ) { <statement> } <function_definition>
                       | λ

<return_type> → <data_type> | empty | id

<parameters> → <param> <param_next> | λ

<param> → <data_type> id | id id

<param_next> → , <param> <param_next> | λ
```

Example:
```
pollinate seed add(seed a, seed b) {
    reclaim a + b;
}
```

#### 3.4.10 Statements

```
<statement> → <simple_stmt> <statement>
            | λ

<simple_stmt> → id <id_stmt>
              | <inc_dec_op> id ;
              | <io_stmt>
              | <conditional_stmt>
              | <loop_stmt>
              | <switch_stmt>
              | <control_stmt>
              | reclaim <reclaim_value>
              | <var_dec> ;
              | <const_dec> ;
```

Declarations and statements can be **interleaved** (like C99), not just at the beginning of a block.

#### 3.4.11 Assignment Statements

```
<id_stmt> → <id_next> <assign_op> <assign_rhs> ;
           | <inc_dec_op> ;
           | ( <arguments> ) ;

<assign_op> → = | += | -= | *= | /= | %=

<assign_rhs> → water ( <water_arg> )
             | <expression>
```

#### 3.4.12 I/O Statements

```
<io_stmt> → plant ( <arguments> ) ;
          | water ( <water_arg> ) ;

<water_arg> → <data_type> | id <water_id_tail> | λ
```

- `plant("Hello {}!", name)` — output with placeholder substitution
- `water(seed)` — read integer input
- `water(name)` — read input into variable

#### 3.4.13 Conditional Statements (if / else-if / else)

```
<conditional_stmt> → spring ( <expression> ) { <statement> } <elseif_chain> <else_opt>

<elseif_chain> → bud ( <expression> ) { <statement> } <elseif_chain>
               | λ

<else_opt> → wither { <statement> }
           | λ
```

Example:
```
spring (x > 0) {
    plant("positive");
}
bud (x < 0) {
    plant("negative");
}
wither {
    plant("zero");
}
```

#### 3.4.14 Loop Statements

**While loop:**
```
grow ( <expression> ) { <statement> }
```

**For loop:**
```
cultivate ( <for_init> ; <expression> ; <for_update> ) { <statement> }

<for_init> → <data_type> id <array_dec> <var_value>
           | id <id_next> <assign_op> <expression>
           | λ

<for_update> → id <for_update_type> | λ

<for_update_type> → <inc_dec_op>
                  | <id_next> <assign_op> <expression>
```

**Do-while loop:**
```
tend { <statement> } grow ( <expression> ) ;
```

Examples:
```
grow (i < 10) { plant("{}",i); i++; }

cultivate (seed i = 0; i < 10; i++) { plant("{}",i); }

tend { plant("at least once"); } grow (frost);
```

#### 3.4.15 Switch Statement

```
<switch_stmt> → harvest ( <expression> ) { <case_list> <default_opt> }

<case_list> → variety <case_literal> : <case_statements> <case_list>
            | λ

<case_literal> → intlit | chrlit | stringlit | sunshine | frost

<default_opt> → soil : <case_statements> | λ
```

Example:
```
harvest (choice) {
    variety 1: plant("One"); prune;
    variety 2: plant("Two"); prune;
    soil: plant("Default");
}
```

#### 3.4.16 Expressions (Operator Precedence — lowest to highest)

```
Level 1 (lowest):  <expression> → <logic_or>
Level 2:           <logic_or>   → <logic_and> ( || <logic_and> )*
Level 3:           <logic_and>  → <relational> ( && <relational> )*
Level 4:           <relational> → <arithmetic> ( <rel_op> <arithmetic> )?
Level 5:           <arithmetic> → <term> ( (+|-|`) <term> )*
Level 6:           <term>       → <factor> ( (*|/|%) <factor> )*
Level 7 (highest): <factor>     → ( <paren_expr> ) | <unary_op> <factor>
                                 | id <factor_id_next> | <literal>
```

**Operator Precedence Table:**

| Precedence | Operators | Associativity | Description |
|------------|-----------|---------------|-------------|
| 1 (lowest) | `\|\|` | Left-to-right | Logical OR |
| 2 | `&&` | Left-to-right | Logical AND |
| 3 | `==` `!=` `<` `>` `<=` `>=` | Non-associative | Relational |
| 4 | `+` `-` `` ` `` | Left-to-right | Addition, subtraction, concatenation |
| 5 | `*` `/` `%` | Left-to-right | Multiplication, division, modulo |
| 6 (highest) | `~` `!` `++` `--` | Right-to-left (unary) | Negation, NOT, increment, decrement |

#### 3.4.17 Type Casting

```
<paren_expr> → <data_type> ) <factor>    // Cast: (seed)x, (tree)3.14
             | <expression> )             // Grouped: (x + 1)
```

#### 3.4.18 Control Flow

```
<control_stmt> → prune ;     // break
               | skip ;      // continue
```

#### 3.4.19 Return Statement

```
<reclaim_value> → <expression> ;   // Return with value: reclaim x + y;
                | ;                // Return without value: reclaim;
```

---

## 4. Syntax Analysis (Parser)

**File:** `Backend/Gal_Parser.py` (~1600 lines)

### 4.1 Parser Type

The GAL parser is an **LL(1) table-driven predictive parser**. This means:

- **LL**: reads input **L**eft-to-right, produces **L**eftmost derivation
- **(1)**: uses **1** token of lookahead to decide which production to apply
- **Table-driven**: uses a pre-computed parsing table (not recursive descent)

### 4.2 How It Works

1. **Parsing Table Construction**: At startup, the `LL1Parser` class builds a parsing table from the PREDICT sets computed in `cfg.py`. For each non-terminal and lookahead terminal, the table stores which production to use.

2. **Stack-Based Parsing**: The parser maintains a stack initialized with `[<program>, EOF]`. At each step:
   - If the top of stack is a **terminal**: match it against the current input token, then pop and advance.
   - If the top of stack is a **non-terminal**: look up the parsing table using the non-terminal and the current input token to find the production, then replace the non-terminal on the stack with the production's right-hand side.
   - If the top is **λ (epsilon)**: simply pop it (empty production).

3. **Token Normalization**: The parser normalizes token types to match CFG terminal names (e.g., `dbllit` → `dblit`). Newline tokens (`\n`) are automatically skipped.

4. **Error Detection**: If no matching production exists in the parsing table for a given (non-terminal, lookahead) pair, a syntax error is reported. The parser **does not perform error recovery** — it stops at the first error.

### 4.3 After Parsing: AST Construction

After the LL(1) syntax validation succeeds, the parser calls `GALsemantic.build_ast()` to construct the Abstract Syntax Tree. The method `parse_and_build()` combines:
1. LL(1) syntax validation
2. AST construction
3. Returns `{success, ast, symbol_table, errors}`

### 4.4 Context-Aware Error Messages

The parser provides **smart, context-aware error messages** rather than generic "unexpected token" errors:

#### 4.4.1 Conventional Keyword Detection

If a user accidentally uses a keyword from another language, the parser recognizes it and suggests the GAL equivalent:

| Mistaken Keyword | Suggestion |
|------------------|-----------|
| `if` | `'if' is not a GAL keyword. Use 'spring' instead.` |
| `else` | `'else' is not a GAL keyword. Use 'wither' instead.` |
| `elif` | `'elif' is not a GAL keyword. Use 'bud' instead.` |
| `while` | `'while' is not a GAL keyword. Use 'grow' instead.` |
| `for` | `'for' is not a GAL keyword. Use 'cultivate' instead.` |
| `switch` | `'switch' is not a GAL keyword. Use 'harvest' instead.` |
| `case` | `'case' is not a GAL keyword. Use 'variety' instead.` |
| `default` | `'default' is not a GAL keyword. Use 'soil' instead.` |
| `break` | `'break' is not a GAL keyword. Use 'prune' instead.` |
| `continue` | `'continue' is not a GAL keyword. Use 'skip' instead.` |
| `return` | `'return' is not a GAL keyword. Use 'reclaim' instead.` |
| `int` | `'int' is not a GAL keyword. Use 'seed' instead.` |
| `float` / `double` | Use `'tree'` instead |
| `char` | Use `'leaf'` instead |
| `bool` / `boolean` | Use `'branch'` instead |
| `string` | Use `'vine'` instead |
| `void` | Use `'empty'` instead |
| `const` | Use `'fertile'` instead |
| `struct` | Use `'bundle'` instead |
| `function` | Use `'pollinate'` instead |
| `printf` / `print` | Use `'plant'` instead |
| `scanf` / `input` | Use `'water'` instead |

#### 4.4.2 Invalid Operator Detection

| Pattern | Error Message |
|---------|---------------|
| `===` used | `'===' is not valid in GAL. Use '==' for comparison.` |
| Single `&` | `'&' is not valid in GAL. Use '&&' for logical AND.` |
| Single `\|` | `'\|' is not valid in GAL. Use '\|\|' for logical OR.` |

#### 4.4.3 Structural Error Detection

| Situation | Error Message |
|-----------|---------------|
| Empty block `{}` | `Empty block. Expected at least one statement inside braces.` |
| Code after `reclaim` | `Unreachable code after 'reclaim'. Statements after a return will never execute.` |
| Chained `++`/`--` | `Increment/decrement operators cannot be chained.` |
| Missing return type after `pollinate` | `Missing return type after 'pollinate'.` |
| Missing parameter type | `Missing type for parameter '{name}'.` |
| Code after program end | `Unexpected token after program end. All code must be inside functions or global declarations.` |

### 4.5 Syntax Error Format

```
SYNTAX error line {line} col {col} {message}. Expected: {expected_set}
```

---

## 5. Semantic Analysis

**File:** `Backend/GALsemantic.py` (~4000 lines)

### 5.1 Overview

Semantic analysis is the **third phase** of compilation. It ensures the program is **meaningful** — not just syntactically correct. The semantic analyzer:

1. **Builds the Abstract Syntax Tree (AST)** from the validated token stream
2. **Tree-walks the AST** to check types, scopes, function signatures, and other rules
3. Maintains a **Symbol Table** to track variables, functions, and scopes

### 5.2 Symbol Table

The `SymbolTable` class manages all declared symbols:

```
SymbolTable:
  ├── variables: {}           # Global variable registry
  ├── global_variables: {}    # Global scope variables
  ├── functions: {}           # Function declarations {name: {return_type, params, ...}}
  ├── scopes: [{}]            # Stack of scopes (push on block entry, pop on exit)
  ├── current_func_name: None # Currently being analyzed function
  ├── function_variables: {}  # Variables per function (for duplicate detection)
  └── bundle_types: {}        # Struct type definitions
```

**Scope Rules:**
- A new scope is pushed when entering a function body, loop body, or conditional block.
- When a scope is popped, its local variables are no longer accessible.
- Variables in outer scopes are visible in inner scopes (lexical scoping).
- Global variables are accessible from all functions.

### 5.3 AST Construction

The `build_ast()` function walks the token stream and constructs a tree of `ASTNode` objects. Each node type represents a language construct:

- `ProgramNode` — root of the AST
- `VariableDeclarationNode` — `seed x = 5;`
- `AssignmentNode` — `x = 10;`
- `BinaryOpNode` — `a + b`, `x == y`
- `UnaryOpNode` — `~x`, `!flag`, `x++`
- `FunctionDeclarationNode` — `pollinate seed add(...) { ... }`
- `FunctionCallNode` — `add(2, 3)`
- `IfStatementNode` — `spring (...) { ... } bud (...) { ... } wither { ... }`
- `ForLoopNode` — `cultivate (...) { ... }`
- `WhileLoopNode` — `grow (...) { ... }`
- `DoWhileLoopNode` — `tend { ... } grow (...);`
- `SwitchNode` — `harvest (...) { variety ...: ... }`
- `PrintNode` — `plant(...);`
- `ReturnNode` — `reclaim x;`
- `ListNode` — `{1, 2, 3}` (array literal)
- `ListAccessNode` — `arr[i]`
- `CastNode` — `seed(x)`, `tree(3)`
- `MemberAccessNode` — `person.age`
- `BundleDefinitionNode` — `bundle Person { ... }`

### 5.4 Semantic Rules — General Rules

These rules apply across the entire program:

#### 5.4.1 Variable Declaration Rules

| Rule | Error If Violated |
|------|-------------------|
| Variables must be declared before use | `Variable '{name}' used before declaration.` |
| No duplicate variable names in the same scope | `Variable '{name}' already declared.` |
| Variable name cannot conflict with function name | `'{name}' is already declared as a function.` |
| Constants (`fertile`) must be initialized at declaration | `Fertile variables must be initialized.` |
| Constants cannot be reassigned | `Variable '{name}' is declared as fertile and cannot be re-assigned.` |
| Multiple `fertile` variables in one line are not allowed | `Multiple fertile declaration is not allowed.` |

#### 5.4.2 Type System Rules

GAL has a **static type system** with 5 primitive types:

| Type | GAL Keyword | Values |
|------|-------------|--------|
| Integer | `seed` | Whole numbers: `0`, `42`, `~5` |
| Float | `tree` | Decimal numbers: `3.14`, `~2.5` |
| Character | `leaf` | Single characters: `'a'`, `'Z'` |
| Boolean | `branch` | `sunshine` (true), `frost` (false) |
| String | `vine` | Text: `"hello"` |

**Type Compatibility Matrix:**

| Operation | Allowed Types | Notes |
|-----------|--------------|-------|
| Assignment `=` | Must match or be `seed`↔`tree` | Implicit numeric conversion |
| Arithmetic `+ - * /` | `seed`, `tree` | `seed`↔`tree` mixing allowed |
| Modulo `%` | `seed` only | Both operands must be `seed` |
| Comparison `== != < > <= >=` | Same type or `seed`↔`tree` | Cannot compare incompatible types |
| Logical `&& \|\|` | `branch` | Must be boolean |
| NOT `!` | `branch` | Operand must be boolean |
| Concatenation `` ` `` | `vine` | At least one operand must be `vine` |
| Increment/Decrement `++ --` | `seed`, `tree` | Numeric types only |

**Implicit Conversions:**
- `seed` ↔ `tree` are compatible (implicit numeric conversion)
- All other type mismatches produce errors

#### 5.4.3 Function Rules

| Rule | Error If Violated |
|------|-------------------|
| Functions must be declared before use | `Function '{name}' is not defined.` |
| No duplicate function declarations | `Function '{name}' already declared.` |
| Argument count must match parameter count | `Function '{name}' expects {n} argument(s), got {m}.` |
| Argument types must match parameter types | `Argument {i} of function '{name}': expected '{expected}', got '{actual}'.` |
| `empty` functions must not return a value | `empty function must not return any value.` |
| Non-`empty` functions must return a value | `Function expects to return a '{type}' value.` |
| Return type must match function declaration | `Function '{name}' returns '{actual}', but expected '{expected}'.` |
| All code paths must return a value | `Function '{name}' must return a value on all code paths.` |
| Functions must end with `reclaim` | `Function '{name}' must end with 'reclaim'.` |
| `water()` cannot be used as an expression value | `'water()' is an I/O statement, not a value expression.` |

#### 5.4.4 Control Flow Rules

| Rule | Error If Violated |
|------|-------------------|
| `spring`/`bud` condition must be `branch` | `spring condition must be branch, got {type}.` |
| `grow` condition must be `branch` | `grow condition must be branch, got {type}.` |
| `tend` condition must be `branch` | `tend condition must be branch, got {type}.` |
| `cultivate` condition must be `branch` | `cultivate condition must be branch, got {type}.` |
| `prune` only inside loop or switch | `'prune' used outside a loop or switch.` |
| `skip` only inside loop | `'skip' used outside a loop.` |

### 5.5 Semantic Rules — Specific Rules

These rules apply to specific language constructs:

#### 5.5.1 Array/List Rules

| Rule | Error If Violated |
|------|-------------------|
| Array size must be `seed` (integer) | `Array size must be of type 'seed' (integer).` |
| List index must be `seed` | `List index must be of type 'seed', got '{type}'.` |
| Only lists can be indexed | `'{name}' is not a list.` |
| Lists must be indexed in expressions | `List '{name}' must be indexed with '[]' in expressions.` |

#### 5.5.2 Switch (Harvest) Rules

| Rule | Error If Violated |
|------|-------------------|
| `harvest` expression must be `seed`, `leaf`, or `branch` | `'harvest' expression must be 'seed'/'leaf'/'branch', not '{type}'.` |
| `variety` value must match switch expression type | `'variety' value type mismatch.` |
| No duplicate `variety` values | `Duplicate 'variety' value '{value}' in 'harvest'.` |

#### 5.5.3 Bundle (Struct) Rules

| Rule | Error If Violated |
|------|-------------------|
| Bundle type must be defined before use | `Bundle type '{name}' is not defined.` |
| No duplicate members in a bundle | `Duplicate member '{name}' in bundle.` |

#### 5.5.4 Built-in Function Rules

| Rule | Error If Violated |
|------|-------------------|
| `ts()` only on lists or strings | `'ts()' can only be used on lists or vines.` |
| `taper()` only on `leaf` type | `'taper()' can only be used on 'leaf' type.` |
| `plant()` max 15 arguments | `Exceeded maximum amount of 15 arguments in plant statement.` |
| `plant()` placeholder count must match args | `Found {n} argument(s). Expected {m} argument(s).` |
| `plant()` string concat only with `vine` | `Only values of type vine can be concatenated in plant().` |

#### 5.5.5 Constant (`fertile`) Rules

| Rule | Error If Violated |
|------|-------------------|
| Must be initialized with matching literal type | `'{name}' must be initialized with a {type} literal.` |
| `seed` constants: `intlit` or `dbllit` accepted | — |
| `tree` constants: `intlit` or `dbllit` accepted | — |
| `leaf` constants: only `chrlit` | — |
| `branch` constants: only `sunshine` or `frost` | — |
| `vine` constants: only `stringlit` | — |

### 5.6 Error Format

```
Ln {line} Semantic Error: {message}
```

---

## 6. Intermediate Code Generation (ICG)

**File:** `Backend/icg.py` (~1200 lines)

### 6.1 Overview

The ICG module generates **Three-Address Code (TAC)** from the GAL token stream. TAC is an intermediate representation where each instruction has at most three operands:

```
result = arg1 op arg2
```

This is represented as a quad: `(op, arg1, arg2, result)`

### 6.2 How It Works

1. The ICG receives the **token stream** (after lexing — it runs in parallel with semantic analysis).
2. It walks through the tokens, generating TAC instructions for each construct.
3. Temporary variables (`t0`, `t1`, ...) are created for intermediate values.
4. Labels (`L0`, `L1`, ...) are created for control flow.

### 6.3 GAL → TAC Type Mapping

| GAL Type | TAC Type |
|----------|----------|
| `seed` | `int` |
| `tree` | `float` |
| `leaf` | `char` |
| `branch` | `bool` |
| `vine` | `string` |
| `empty` | `void` |

### 6.4 TAC Instruction Types

| Instruction | Format | Example |
|-------------|--------|---------|
| `DECLARE` | `(DECLARE, type, _, name)` | `declare x : int` |
| `ASSIGN` | `(=, value, _, name)` | `x = 5` |
| `CONST` | `(CONST, type, value, name)` | `const MAX : int = 100` |
| `ARRAY_DECLARE` | `(ARRAY_DECLARE, type, size, name)` | `declare arr[10] : int` |
| `ARRAY_STORE` | `(ARRAY_STORE, value, index, name)` | `arr[0] = 5` |
| `ARRAY_LOAD` | `(ARRAY_LOAD, name, index, temp)` | `t0 = arr[0]` |
| `STRUCT_STORE` | `(STRUCT_STORE, value, member, name)` | `person.age = 25` |
| `STRUCT_LOAD` | `(STRUCT_LOAD, name, member, temp)` | `t0 = person.age` |
| Binary ops | `(op, left, right, temp)` | `t0 = a + b` |
| `UNARY_MINUS` | `(UNARY_MINUS, arg, _, temp)` | `t0 = -a` |
| `NOT` | `(NOT, arg, _, temp)` | `t0 = !flag` |
| `INC` / `DEC` | `(INC, name, _, name)` | `x = x + 1` |
| `LABEL` | `(LABEL, _, _, label)` | `L0:` |
| `GOTO` | `(GOTO, _, _, label)` | `goto L1` |
| `IF` | `(IF, cond, _, label)` | `if t0 goto L1` |
| `IFFALSE` | `(IFFALSE, cond, _, label)` | `ifFalse t0 goto L2` |
| `PARAM` | `(PARAM, _, _, value)` | `param x` |
| `CALL` | `(CALL, func, argc, temp)` | `t1 = call add, 2` |
| `RETURN` | `(RETURN, _, _, value)` | `return t0` |
| `FUNC` | `(FUNC, _, _, name)` | `func add:` |
| `ENDFUNC` | `(ENDFUNC, _, _, name)` | `endfunc` |
| `PRINT` | `(PRINT, _, _, value)` | `print t0` |
| `READ` | `(READ, type, _, name)` | `read x` |

### 6.5 ICG Example

**GAL Source:**
```
root() {
    seed x = 5;
    seed y = 10;
    seed z = x + y;
    plant("{}", z);
}
```

**Generated TAC:**
```
func main:
  declare x : int
  x = 5
  declare y : int
  y = 10
  t0 = x + y
  declare z : int
  z = t0
  print z
endfunc
```

### 6.6 Public API

```python
generate_icg(tokens) → {
    "success": bool,
    "tac": List[TACInstruction],
    "tac_text": str,           # Human-readable TAC output
    "errors": List[str]
}
```

---

## 7. Interpreter

**File:** `Backend/GALinterpreter.py` (~1600 lines)

### 7.1 Overview

The interpreter is a **tree-walk interpreter** that directly executes the AST produced by the semantic analyzer. It does NOT compile to machine code — it traverses the AST nodes and evaluates them on the fly.

### 7.2 How It Works

1. The `Interpreter` class receives the validated AST (rooted at a `ProgramNode`).
2. It walks the tree, evaluating each node:
   - `VariableDeclarationNode` → stores variable in the current scope
   - `AssignmentNode` → updates variable value
   - `BinaryOpNode` → evaluates left and right children, applies operator
   - `IfStatementNode` → evaluates condition, enters appropriate branch
   - `ForLoopNode` → evaluates init, then loops: check condition → body → update
   - `PrintNode` → evaluates arguments, sends output via Socket.IO
   - `FunctionCallNode` → pushes new scope, evaluates body, pops scope
3. For `water()` (input): the interpreter emits an `input_required` event via Socket.IO and **blocks** until the client sends the input value back.

### 7.3 Scope Management

The interpreter uses a **stack-based scope system**:
- `self.scopes = [{}]` — starts with one global scope
- `enter_scope()` — pushes a new empty scope dict onto the stack
- `exit_scope()` — pops the top scope
- Variable lookup searches from innermost scope outward (lexical scoping)
- `self.global_variables` — separate dict for globally declared variables

### 7.4 Type Casting

The interpreter supports explicit type casting:

| Cast | Behaviour |
|------|-----------|
| `seed(x)` | Converts to integer (`int(x)`) |
| `tree(x)` | Converts to float (`float(x)`) |
| `leaf(x)` | Converts to character (first char of string or `chr()`) |
| `branch(x)` | Converts to boolean |
| `vine(x)` | Converts to string (`str(x)`) |

### 7.5 Built-in Functions

| Function | Description |
|----------|-------------|
| `ts(x)` | Returns length of list or string (like `len()`) |
| `taper(x)` | Splits a `leaf`/string into a list of individual characters (like `split('')`) |
| `.append(x)` | Appends element to a list |
| `.insert(i, x)` | Inserts element at index in a list |
| `.remove(i)` | Removes element at index from a list |

### 7.6 Runtime Behaviour

| Feature | Behaviour |
|---------|-----------|
| Max loop iterations | 10,000 (prevents infinite loops) |
| Max number digits | 16 digits for any evaluated number |
| Float display | Truncated to 5 decimal places, trailing zeros stripped |
| `seed` ↔ `tree` coercion | Implicit — `seed` vars can hold `tree` values and vice versa |
| String interpolation | `plant("Hello {}!", name)` — `{}` replaced positionally |
| Async I/O | Uses Socket.IO + eventlet for non-blocking `water()` input |
| `++`/`--` | Pre and post: pre returns new value, post returns old |

### 7.7 Runtime Error Catalogue

| Category | Errors |
|----------|--------|
| **Arithmetic** | Division by zero; Number exceeds 16 digits |
| **Loop** | Infinite loop detected (>10,000 iterations) |
| **Type** | Condition must be boolean; List index must be integer; Expected int/float/branch/leaf value |
| **Array** | Index out of bounds; Not a list; Cannot index non-list |
| **Bundle** | Value is not a bundle; No member '{name}'; Member not a bundle |
| **Function** | Argument count mismatch; Break/continue outside loop |
| **Variable** | Already declared; Not declared; Used before declaration |

---

## 8. NLP Fallback / AI Chat Assistant

**File:** `Backend/gal_fallback.py` (~800 lines)

### 8.1 Three-Layer Architecture

The AI chat assistant uses a hybrid approach to help users understand errors:

**Layer 1 — Rule Engine** (regex-based):
- Matches compiler error messages against 50+ regex patterns
- Returns structured explanations with: Stage, Cause, Rule, Fix, Explanation

**Layer 2 — Semantic Retrieval** (sentence-transformers):
- Uses a fine-tuned `gal-mpnet-finetuned` model for semantic search
- Matches user questions against 50+ knowledge base topics
- Returns the most relevant topic if similarity > 0.35 threshold

**Layer 3 — Default**:
- Falls back to a help menu if no match is found
- Returns a general help message listing available topics

### 8.2 Error Explanation Format

```
**Stage:** Lexical Analysis (Lexer)
**Cause:** An identifier exceeded 15 characters.
**Rule:** Identifiers must be at most 15 characters long.
**Fix:**
// BAD:  seed thisIsWayTooLong = 5;
// GOOD: seed shortName = 5;
```

---

## 9. Web Interface & Server

### 9.1 Server (`Backend/server.py`)

- **Framework**: Flask + Flask-SocketIO (with eventlet for async)
- **CORS**: Enabled for cross-origin requests

**REST API Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/lex` | POST | Lexical analysis only → returns tokens + errors |
| `/api/parse` | POST | Lexer + Parser → returns syntax analysis results |
| `/api/semantic` | POST | Full pipeline through semantic analysis → returns AST + symbol table |
| `/api/icg` | POST | Full pipeline + ICG → returns three-address code |
| `/api/run` | POST | Full pipeline + execution (REST, no input support) |
| `/api/health` | GET | Health check |

**Socket.IO Events:**

| Event | Direction | Description |
|-------|-----------|-------------|
| `run_code` | Client → Server | Send source code for execution |
| `output` | Server → Client | Program output line |
| `input_required` | Server → Client | Program needs user input (`water()`) |
| `input_response` | Client → Server | User provides input value |
| `stage_complete` | Server → Client | Compilation stage completed |
| `execution_complete` | Server → Client | Program finished |

### 9.2 Frontend (`UI/`)

- `index.html` — Main page with code editor and output panels
- `style.pixel.css` — Pixel/retro-themed CSS styling
- `main.js` — Client-side logic: editor, Socket.IO communication, UI updates

---

## 10. General Rules & Constraints

### 10.1 Program Structure Rules

1. Every program **must** have a `root()` function (entry point).
2. Global declarations (variables, constants, bundles) come **before** function definitions.
3. Function definitions come **before** `root()`.
4. All code must be inside functions or global declarations.
5. Statements end with semicolons (`;`).
6. Blocks are delimited by `{ }`.
7. Declarations and statements can be interleaved within blocks (C99-style).

### 10.2 Limits & Constraints

| Constraint | Value |
|------------|-------|
| Max identifier length | 15 characters |
| Max integer literal digits | 8 digits |
| Max fractional digits | 8 digits |
| Max evaluated number digits (runtime) | 16 digits |
| Max loop iterations | 10,000 |
| Max `plant()` arguments | 15 |
| Float display precision | 5 decimal places |
| String escape sequences | `\n`, `\t`, `\\`, `\"`, `\{`, `\}` |

### 10.3 Naming Conventions

- **Identifiers**: Start with a letter, followed by letters/digits/underscores, max 15 chars.
- **Keywords**: All lowercase, garden-themed (see Section 2.3).
- **Boolean literals**: `sunshine` (true), `frost` (false).
- **Negation**: Uses `~` prefix instead of unary minus `-`.

---

## 11. Keyword Reference: GAL ↔ Conventional

| Category | Conventional | GAL Keyword |
|----------|-------------|-------------|
| **Data Types** | `int` | `seed` |
| | `float` / `double` | `tree` |
| | `char` | `leaf` |
| | `bool` / `boolean` | `branch` |
| | `string` | `vine` |
| | `void` | `empty` |
| **Modifiers** | `const` | `fertile` |
| **Aggregates** | `struct` | `bundle` |
| **Booleans** | `true` | `sunshine` |
| | `false` | `frost` |
| **Entry Point** | `main` | `root` |
| **Functions** | `function` | `pollinate` |
| | `return` | `reclaim` |
| **Conditionals** | `if` | `spring` |
| | `else if` | `bud` |
| | `else` | `wither` |
| **Loops** | `while` | `grow` |
| | `for` | `cultivate` |
| | `do` (do-while) | `tend` |
| **Switch** | `switch` | `harvest` |
| | `case` | `variety` |
| | `default` | `soil` |
| **Control Flow** | `break` | `prune` |
| | `continue` | `skip` |
| **I/O** | `print` / `printf` | `plant` |
| | `input` / `scanf` | `water` |
| **Built-ins** | `len()` | `ts()` |
| | `split('')` | `taper()` |
| | `.append()` | `.append()` |
| | `.insert()` | `.insert()` |
| | `.remove()` | `.remove()` |
| **Operators** | unary `-` | `~` (tilde) |
| | string `+` | `` ` `` (backtick) |

---

## 12. AST Node Types Reference

| Node Class | Purpose | Example |
|-----------|---------|---------|
| `ProgramNode` | Root of AST | Entire program |
| `VariableDeclarationNode` | Variable declaration | `seed x = 5;` |
| `FertileDeclarationNode` | Constant declaration | `fertile seed MAX = 100;` |
| `AssignmentNode` | Assignment statement | `x = 10;` |
| `BinaryOpNode` | Binary operation | `a + b`, `x == y` |
| `UnaryOpNode` | Unary operation | `~x`, `!flag`, `x++` |
| `FunctionDeclarationNode` | Function definition | `pollinate seed add(...)` |
| `FunctionCallNode` | Function call | `add(2, 3)` |
| `IfStatementNode` | Conditional chain | `spring/bud/wither` |
| `ForLoopNode` | For loop | `cultivate (...)` |
| `WhileLoopNode` | While loop | `grow (...)` |
| `DoWhileLoopNode` | Do-while loop | `tend {...} grow (...)` |
| `SwitchNode` | Switch statement | `harvest (...)` |
| `PrintNode` | Output statement | `plant(...)` |
| `ReturnNode` | Return statement | `reclaim x;` |
| `UpdateNode` | For-loop update | `i++` in for-loop |
| `ContinueNode` | Continue statement | `skip;` |
| `BreakNode` | Break statement | `prune;` |
| `ListNode` | Array literal | `{1, 2, 3}` |
| `ListAccessNode` | Array indexing | `arr[i]` |
| `AppendNode` | List append | `.append(x)` |
| `InsertNode` | List insert | `.insert(0, x)` |
| `RemoveNode` | List remove | `.remove(0)` |
| `CastNode` | Type cast | `seed(x)` |
| `TaperNode` | Character split | `taper(str)` |
| `TSNode` | Length function | `ts(arr)` |
| `MemberAccessNode` | Struct member access | `person.age` |
| `ArrayMemberAccessNode` | Array element member | `people[0].name` |
| `BundleDefinitionNode` | Struct definition | `bundle Person {...}` |

---

## 13. Complete Error Catalogue

### 13.1 Lexical Errors

| # | Error Message | Cause |
|---|---------------|-------|
| L1 | `Invalid delimiter 'X' after 'Y'` | Wrong character after a token |
| L2 | `Identifier exceeds maximum length of 15 characters` | Identifier too long |
| L3 | `Integer exceeds maximum of 8 digits` | Integer literal too large |
| L4 | `Fractional part exceeds maximum of 8 digits` | Too many decimal digits |
| L5 | `Missing closing '"' for string literal` | Unclosed string |
| L6 | `Missing closing quote for character literal` | Unclosed char |
| L7 | `Character literal must contain exactly one character` | Multi-char in `'...'` |
| L8 | `Illegal Character 'X'` | Unknown character |
| L9 | `Identifiers cannot start with a number` | e.g., `1abc` |
| L10 | `Invalid escape sequence` | Bad escape like `\x` |
| L11 | `Missing closing '*/' for multi-line comment` | Unclosed comment |

### 13.2 Syntax Errors

| # | Error Message | Cause |
|---|---------------|-------|
| S1 | `'X' is not a GAL keyword. Use 'Y' instead.` | Conventional keyword used |
| S2 | `'===' is not valid in GAL. Use '==' for comparison.` | Triple equals |
| S3 | `'&' is not valid. Use '&&' for logical AND.` | Single ampersand |
| S4 | `'\|' is not valid. Use '\|\|' for logical OR.` | Single pipe |
| S5 | `Empty block. Expected at least one statement.` | Empty `{}` |
| S6 | `Unreachable code after 'reclaim'.` | Code after return |
| S7 | `Increment/decrement operators cannot be chained.` | `++++x` |
| S8 | `Missing return type after 'pollinate'.` | No type before function name |
| S9 | `Missing type for parameter '{name}'.` | Parameter without type |
| S10 | `Unexpected token after program end.` | Code after `root(){}` closing |
| S11 | `Type mismatch in declaration` | Wrong literal type |
| S12 | `Empty character literal.` | `''` |
| S13 | `Invalid character literal: '{value}'.` | `'abc'` |

### 13.3 Semantic Errors

| # | Error Message | Cause |
|---|---------------|-------|
| SE1 | `Variable '{name}' already declared.` | Duplicate declaration |
| SE2 | `Variable '{name}' used before declaration.` | Undeclared variable use |
| SE3 | `'{name}' is already declared as a function.` | Name conflict |
| SE4 | `Fertile variables must be initialized.` | Uninitialized constant |
| SE5 | `Variable '{name}' is declared as fertile and cannot be re-assigned.` | Constant mutation |
| SE6 | `Type Mismatch! Cannot assign {rhs} to variable '{name}' of type {lhs}.` | Type mismatch |
| SE7 | `Modulo operator '%' requires 'seed' operands.` | Non-integer modulo |
| SE8 | `'!' operator can only be used with 'branch' values.` | NOT on non-boolean |
| SE9 | `Cannot compare '{type1}' and '{type2}'.` | Incompatible comparison |
| SE10 | `Cannot concatenate non-vine with backtick.` | Non-string concat |
| SE11 | `Array size must be of type 'seed'.` | Non-integer array size |
| SE12 | `List index must be of type 'seed'.` | Non-integer index |
| SE13 | `'{name}' is not a list.` | Indexing non-array |
| SE14 | `Function '{name}' already declared.` | Duplicate function |
| SE15 | `Function '{name}' is not defined.` | Undefined function |
| SE16 | `Function '{name}' expects {n} argument(s), got {m}.` | Wrong arg count |
| SE17 | `Argument {i}: expected '{expected}', got '{actual}'.` | Wrong arg type |
| SE18 | `empty function must not return any value.` | Void returning value |
| SE19 | `spring condition must be branch, got {type}.` | Non-boolean condition |
| SE20 | `'prune' used outside a loop or switch.` | Break outside loop |
| SE21 | `'skip' used outside a loop.` | Continue outside loop |
| SE22 | `'harvest' expression must be 'seed'/'leaf'/'branch'.` | Invalid switch type |
| SE23 | `Duplicate 'variety' value '{value}'.` | Duplicate case |
| SE24 | `Bundle type '{name}' is not defined.` | Unknown struct |
| SE25 | `'ts()' can only be used on lists or vines.` | Wrong ts() target |
| SE26 | `'taper()' can only be used on 'leaf' type.` | Wrong taper() target |
| SE27 | `Exceeded maximum of 15 arguments in plant.` | Too many print args |

### 13.4 Runtime Errors

| # | Error Message | Cause |
|---|---------------|-------|
| R1 | `Division by zero is undefined` | `x / 0` |
| R2 | `Evaluated number exceeds maximum of 16 digits` | Number overflow |
| R3 | `Infinite loop detected!` | > 10,000 iterations |
| R4 | `Condition must be a boolean. Got '{value}'` | Non-boolean in condition |
| R5 | `List index must be an integer. Got '{index}'` | Non-integer index |
| R6 | `Index '{idx}' out of bounds for list '{name}'` | Array out of bounds |
| R7 | `Variable '{name}' is not a list` | Indexing non-array |
| R8 | `Value is not a bundle` | Struct access on non-struct |
| R9 | `Bundle has no member '{name}'` | Invalid member access |
| R10 | `Function '{name}' expects N argument(s), got M` | Wrong arg count at runtime |
| R11 | `Input value exceeds maximum of 16 digits` | Input too large |

---

## Sample GAL Program

```gal
// Global constant
fertile seed MAX = 100;

// Function definition
pollinate seed add(seed a, seed b) {
    reclaim a + b;
}

// Main entry point
root() {
    seed x = 10;
    seed y = 20;
    seed result = add(x, y);

    spring (result > MAX) {
        plant("Result {} exceeds max!", result);
    }
    bud (result == MAX) {
        plant("Result equals max.");
    }
    wither {
        plant("Result is {}", result);
    }

    // Loop example
    cultivate (seed i = 0; i < 5; i++) {
        plant("i = {}", i);
    }

    // Array example
    seed arr[] = {1, 2, 3, 4, 5};
    plant("Array length: {}", ts(arr));

    // Input example
    seed userInput = water(seed);
    plant("You entered: {}", userInput);
}
```

---

*End of Documentation*
