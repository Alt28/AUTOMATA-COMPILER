# GAL Compiler — Defense-Prep Walkthrough

## File 2 of 9: tokens / errors (the Token, Position, and LexicalError classes inside `lexer.py`)

These three classes are tiny but **they are the vocabulary the whole compiler speaks**. Every layer after the lexer — parser, AST builder, semantic, ICG, interpreter — consumes `Token` objects and produces typed errors. If a panel asks "how does your compiler represent a piece of source code?", the answer starts here.

---

## 1. FILE PURPOSE

These three classes (and the token-type constants and `get_token_description` helper that surround them) live inside `lexer.py` (lines 1-246, 252-297). They define **how a single character or word from the user's program is represented internally** so it can travel through the rest of the pipeline.

Where they fit:

```
Source code (a Python string)
        │
        ▼
   ┌──────────┐
   │  Lexer   │
   └──────────┘
        │  produces:
        ▼
  list[Token]  + list[LexicalError]
        │
        ▼
   ┌──────────┐
   │  Parser  │ ◄── reads Token.type to decide grammar action
   └──────────┘    reads Token.line/col for error messages
        │
        ▼
   ┌──────────────┐
   │  AST builder │ ◄── attaches Token.value and Token.line to AST nodes
   └──────────────┘
        │
        ▼
   semantic, ICG, interpreter — same Token references, never mutated
```

What depends on these classes:

| File | What it uses |
|---|---|
| `lexer.py` (the rest of it) | `Lexer.make_tokens()` builds `Token` instances |
| `Gal_Parser.py` | Reads `token.type` for LL(1) table lookup, `token.line/col` for syntax error messages |
| `GALsemantic.py` | Uses `token.value` for variable names, `token.line` for semantic errors |
| `icg.py` | Reads `token.type` to dispatch TAC emission |
| `GALinterpreter.py` | Reads `token.line` to attach line numbers to runtime errors |
| `server.py` | Uses `_display_value(token.value)` and `get_token_description(token.type, token.value)` to render the lexeme table for the IDE |

These classes are the **single source of truth** for what a token looks like. They are never subclassed and never extended.

---

## 2. IMPORTS / DEPENDENCIES

The token/error classes use **no imports of their own** — they are pure-Python data containers. The surrounding `lexer.py` imports nothing for them. That's deliberate:

- They are POPOs (plain old Python objects), so any other file can import them without dragging in third-party libraries.
- No JSON, no logging, no runtime configuration. Each `Token` is just four fields, each `LexicalError` is just two.

If a panel asks *"why are these classes so simple?"*: the answer is that **simplicity is the feature**. A token is just data. Behavior (how it's displayed, how it's serialized, how it's compared) lives in the layers that use the token — not on the token itself.

---

## 3. GLOBAL CONSTANTS / VARIABLES

This layer has **two flavors** of constants — character classes (used by the lexer to recognize tokens) and **token-type strings** (used by every later layer to identify what kind of token they're looking at).

### 3.1 Character-class constants (lines 11-19)

```python
ZERO = '0'
DIGIT = '123456789'
ZERODIGIT = ZERO + DIGIT          # '0123456789'

LOW_ALPHA = 'abcdefghijklmnopqrstuvwxyz'
UPPER_ALPHA = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
ALPHA = LOW_ALPHA + UPPER_ALPHA   # 'a-zA-Z'
ALPHANUM = ALPHA + ZERODIGIT + '_'
```

**Why two digit sets?** GAL identifiers may contain digits anywhere except the **first** character. So `DIGIT` (no zero) is used to validate the first digit of a number that should not have leading zeros, while `ZERODIGIT` is used for the rest.

**Why `ALPHANUM` includes underscore but `ALPHA` doesn't?** Because identifiers are `letter (letter|digit|_)*` — the first character must be a letter, so `ALPHA` is used to validate it; everything after that uses `ALPHANUM`. This matches Rule 3 in your GAL specification: *"Identifiers must start with a letter and may include letters, digits, and underscore."*

**Defense answer:** *"These are the alphabets the lexer uses to validate identifier and number formation. They directly mirror the regular definitions in our compiler proposal — `letter`, `digit`, `alphanumeric`."*

### 3.2 Delimiter sets (lines 25-52)

```python
space_delim = {' ', '\t', '\n'}
delim2 = {';', ':'}
delim3 = {'{'}
delim4 = {':', '('}
...
idf_delim = {' ', ',', ';', '(', ')', '{', '}', ...}
whlnum_delim = {';', ' ', ',', '}', ']', ')', ':', ...}
decim_delim = {'}', ';', ',', '+', '-', '*', '/', ...}
```

**What these are:** Each delimiter set lists the characters that may **legally come immediately after** a particular kind of token. The lexer uses them to detect things like `seedage` (where `seed` runs into `age` with no whitespace) — that's invalid because `seed` must be followed by whitespace, a paren, or punctuation, not by a letter.

**Why they're needed:** GAL's grammar is *delimiter-aware*. A keyword like `seed` is only a keyword if it's followed by something that lets the lexer know it ended; otherwise, `seedling` would be tokenized as the keyword `seed` followed by the identifier `ling`, which is a different mistake than what the user intended.

**Honest note for the defense:** A code review of `lexer.py` showed that **only some of these delimiter sets are actively used** (`space_delim`, `delim2`, `delim3`, `delim4`, `delim6`, `delim7`, `delim8`, `delim23`, `idf_delim`, `whlnum_delim`, `decim_delim` are referenced in scanning logic). The numbered ones from 9 through 22, plus 24 and `comment_delim`, are defined but not consumed by the current implementation. They are kept as documentation that mirrors the **regular-definition tables** in your compiler proposal — each numbered `delim` corresponds to one row of the proposal's "Regular Definition" section. Removing them would lose the proposal-to-code traceability, so they stay.

If asked: *"Some delimiter sets are kept for spec traceability — each name maps to a delim row in the GAL proposal document. The actively-used ones drive the scanner's lookahead checks; the others are kept as living documentation."*

### 3.3 Token-type constants (lines 60-133)

This is the **vocabulary list of the entire compiler**. Every token produced by the lexer has a `.type` field whose value is one of these strings. There are roughly 60 of them, grouped into:

**Reserved words (26):**

```python
TT_RW_WATER       = 'water'     TT_RW_PLANT       = 'plant'
TT_RW_SEED        = 'seed'      TT_RW_LEAF        = 'leaf'
TT_RW_BRANCH      = 'branch'    TT_RW_TREE        = 'tree'
TT_RW_VINE        = 'vine'      TT_RW_SPRING      = 'spring'
TT_RW_WITHER      = 'wither'    TT_RW_BUD         = 'bud'
TT_RW_HARVEST     = 'harvest'   TT_RW_GROW        = 'grow'
TT_RW_CULTIVATE   = 'cultivate' TT_RW_TEND        = 'tend'
TT_RW_EMPTY       = 'empty'     TT_RW_PRUNE       = 'prune'
TT_RW_SKIP        = 'skip'      TT_RW_RECLAIM     = 'reclaim'
TT_RW_ROOT        = 'root'      TT_RW_POLLINATE   = 'pollinate'
TT_RW_VARIETY     = 'variety'   TT_RW_FERTILE     = 'fertile'
TT_RW_SOIL        = 'soil'      TT_RW_BUNDLE      = 'bundle'
```

**Operators (arithmetic, assignment, comparison, logical, increment/decrement):**

```python
TT_PLUS = '+'         TT_MINUS = '-'        TT_MUL = '*'
TT_DIV = '/'          TT_MOD = '%'          TT_EQ = '='
TT_EQTO = '=='        TT_NOTEQ = '!='       TT_LT = '<'
TT_GT = '>'           TT_LTEQ = '<='        TT_GTEQ = '>='
TT_AND = '&&'         TT_OR = '||'          TT_NOT = '!'
TT_INCREMENT = '++'   TT_DECREMENT = '--'
TT_PLUSEQ = '+='      TT_MINUSEQ = '-='     TT_MULTIEQ = '*='
TT_DIVEQ = '/='       TT_MODEQ = '%='
TT_NEGATIVE = '~'     TT_CONCAT = '`'
```

**Punctuation:**

```python
TT_LPAREN = '('       TT_RPAREN = ')'
TT_BLOCK_START = '{'  TT_BLOCK_END = '}'
TT_LSQBR = '['        TT_RSQBR = ']'
TT_SEMICOLON = ';'    TT_COMMA = ','        TT_COLON = ':'
TT_DOT = '.'
```

**Identifiers, literals, special:**

```python
TT_IDENTIFIER     = 'id'        # any user-defined name
TT_INTEGERLIT     = 'intlit'    # 42, 100
TT_DOUBLELIT      = 'dbllit'    # 3.14
TT_STRINGLIT      = 'stringlit' # "hello"
TT_CHARLIT        = 'chrlit'    # 'a'
TT_BOOLLIT_TRUE   = 'sunshine'
TT_BOOLLIT_FALSE  = 'frost'
TT_EOF            = 'EOF'       # synthetic end-of-file marker
TT_NL             = '\n'        # newline (skipped during parsing)
```

**Why each constant has both a Python name and a string value:**

```python
TT_RW_SEED = 'seed'
```

The Python name `TT_RW_SEED` is what the lexer **writes** when emitting tokens. The string value `'seed'` is what every later layer **compares against**. The duplication looks odd, but it gives us:

- **Symbolic names** in the lexer for self-documenting code: `Token(TT_RW_SEED, ...)` reads better than `Token('seed', ...)`.
- **String comparisons** in the parser: when the LL(1) table says "expect token type `'seed'`", the parser does a fast string equality check. Strings are hashable and immutable in Python — perfect for being keys in the predict-set dictionary.

**Two important conventions:**

1. **Token type strings match the surface text for keywords.** `TT_RW_SEED = 'seed'`. So when the lexer sees the word `seed` in the source, the token's type is literally the string `'seed'`. This makes the parser's grammar definitions in `cfg.py` read like the GAL source itself.
2. **Token type strings for symbols are the symbol itself.** `TT_PLUS = '+'`. So `Token('+', '+', ...)` represents a literal `+`. This is consistent and easy to debug.

**Defense answer for "why is the type a string and not an enum?":** *"Strings are hashable, immutable, and easy to inspect. Our LL(1) parsing table uses token-type strings as dictionary keys — we use the string `'seed'` directly as a terminal in the grammar. Using an `enum` would force every comparison to go through the enum's value attribute, with no benefit. The token-type constants serve as a self-documenting catalogue."*

### 3.4 The known typo / token name discrepancy

The token-type constant for double literals is `TT_DOUBLELIT = 'dbllit'`. However, the parser internally uses the name `'dblit'` everywhere (in the grammar productions in `cfg.py`, in error filters in `Gal_Parser.py`).

**The bridge:** the parser's `LL1Parser` is configured with a `token_type_alias` map: `{'dbllit': 'dblit'}`. When it reads a token from the lexer with type `'dbllit'`, it normalizes it to `'dblit'` before comparing against the grammar.

**Why two names for one thing?** Historical reasons — the lexer settled on `'dbllit'` (one word, "double literal") and the grammar settled on `'dblit'` (shorter alternative). Rather than touch both, we keep the alias as a one-line bridge.

**For defense:** if a panelist sees this discrepancy: *"`dbllit` is the lexer's internal name; `dblit` is the grammar terminal. They are bridged by a single alias entry in the parser configuration. We documented this in our system-documentation file."*

---

## 4. CLASSES AND FUNCTIONS

### 4.1 `Position` class (lines 252-272)

```python
class Position:
    def __init__(self, index, ln, col=0):
        self.index = index
        self.ln = ln
        self.col = col

    def advance(self, current_char):
        self.index += 1
        self.col += 1
        if current_char == '\n':
            self.ln += 1
            self.col = 0
        return self

    def copy(self):
        return Position(self.index, self.ln, self.col)
```

**What it receives:** A character index, a line number (1-based), and an optional column number (0-based).

**What it returns / modifies:** The instance is mutated in-place by `advance()`; `copy()` returns a snapshot.

**Why it exists:** Errors must be reported with a precise location, e.g., *"Lexical error line 4 col 12: unclosed string literal"*. Without a position object, the lexer would have to track three separate counters everywhere.

**When it is called:**
- `Lexer.__init__` creates one: `self.pos = Position(-1, 1, -1)` (intentionally pre-first-char so the first `advance()` lands at index 0, line 1, col 0).
- `Lexer.advance` calls `self.pos.advance(self.current_char)` for every character read.
- Various scanners call `pos = self.pos.copy()` at the start of a multi-character token (e.g., the start of a string literal) so that if an error occurs, the error message points to the token's *start*, not its *end*.

**Stage:** Lexical (used during scanning).

**Errors handled:** None directly. It's a passive data tracker.

**Edge cases:**
- The constructor accepts `index=-1` so the lexer can call `advance()` once and land at the true first character. Calling `Position(0, 1, 0)` then `advance()` would skip the first character.
- When `\n` is consumed, the column resets to 0 *of the new line*, but the `\n` token itself is at col 0 of the new line. Tokens on the previous line that span past col 0 are reported correctly because we use `pos.copy()` at the token's *start*.

### 4.2 `LexicalError` class (lines 277-286)

```python
class LexicalError:
    def __init__(self, pos, details):
        self.pos = pos
        self.details = details

    def as_string(self):
        self.details = self.details.replace('\n', '\\n')
        return f"LEXICAL error line {self.pos.ln} col {self.pos.col} {self.details}"
```

**What it receives:** A `Position` snapshot (where the error occurred) and a string `details` describing what went wrong.

**What it returns:** Stores the data; `as_string()` formats a single human-readable line.

**Why it exists:** Lexical errors and runtime errors have different concerns. A lexical error must include *line and column*, must format consistently across the whole compiler, and must not stop the lexer (the lexer continues scanning so it can report multiple errors at once).

**When it is called:**
- Inside the lexer, whenever an invalid character or malformed token is detected: `errors.append(LexicalError(pos, "Invalid character '$'"))`.
- `as_string()` is called when assembling the final error list to send back via `server.py`.

**Edge case:** The `replace('\n', '\\n')` line escapes newlines in the error description so a single error never breaks across multiple lines of output. Note this **mutates `self.details`** the first time it's called; calling `as_string()` twice returns the same string. Harmless but technically a side effect — a defensible design choice for a single-shot error formatter.

**Defense answer for "why is this a class instead of just a string?":** *"Errors have two pieces of data: position and message. Wrapping them in a class lets us preserve both fields all the way to the IDE, where the frontend uses the line/column to highlight the exact source location. A flat string would lose the structured location."*

### 4.3 `Token` class (lines 291-297)

```python
class Token:
    def __init__(self, type_, value=None, line=1, col=0):
        self.type = type_    # e.g., 'seed', 'id', 'intlit', '+', '=='
        self.value = value   # actual text/value (e.g., 42, "myVar", "+")
        self.line = line     # line number where token starts
        self.col = col       # column number where token starts
```

**What it receives:** A type string (one of the `TT_*` constants), a value (the literal text or numeric/string value), a line number, and a column number.

**What it returns / modifies:** Just stores the four fields.

**Why it exists:** This is the **interface between every compiler stage**. Lexer produces them; parser/AST/semantic/ICG/interpreter consume them. By making the class minimal and immutable-by-convention (no setter methods), we guarantee that no later stage can accidentally rewrite a token's type or position.

**When it is called:** The lexer constructs `Token(...)` every time it finishes recognizing a lexeme. After construction, tokens are read but never reassigned.

**Stage:** Spans Lexical → Syntax → Semantic → ICG → Execution. Probably the most-used class in the codebase by reference count.

**Edge cases:**

- `value=None` is allowed because some tokens (notably `TT_EOF`) carry no payload.
- `line=1, col=0` defaults exist so synthetic tokens (created at parse time, not lex time) don't crash.
- The `Token` class has no `__repr__` or `__eq__` — comparisons elsewhere always use `token.type == 'seed'`. **This is intentional and not a bug.** If you added `__eq__`, careless comparisons like `token == 'seed'` would silently work and obscure the type-vs-value distinction.

**Defense answer for "why doesn't `Token` have a `__repr__`?":** *"Token comparisons are always done on specific fields — `token.type` for grammar matching, `token.value` for semantic checks, `token.line` for error reporting. Defining `__repr__` would tempt callers to print tokens directly and cross fields. The IDE rendering goes through `_display_value()` and `get_token_description()` instead, which gives controlled formatting."*

### 4.4 `get_token_description(token_type, value)` helper (lines 139-246)

```python
def get_token_description(token_type: str, value: str = '') -> str:
    """Returns a descriptive name for each token type"""
    if token_type == 'intlit' and isinstance(value, str) and value.startswith('~'):
        return 'negative integer'
    if token_type == 'dbllit' and isinstance(value, str) and value.startswith('~'):
        return 'negative float'
    descriptions = { 'water': 'Input Function', 'plant': 'Output Function',
                     'seed': 'Integer Type', ... }
    return descriptions.get(token_type, 'Unknown Token')
```

**What it receives:** A token type string and (optionally) the token's value.

**What it returns:** A human-readable label like `"Integer Type"`, `"While Loop"`, or `"Plus Operator"`.

**Why it exists:** The IDE displays a "Lexemes" table with three columns: lexeme (the text), token (the type), and type (the friendly description). The friendly description comes from this function.

**When it is called:** Inside `server.py` at every endpoint that returns tokens to the IDE: `/api/lex`, `/api/parse`, `/api/semantic`, `/api/icg`. Each token is enriched with `'description': get_token_description(token.type, token.value)` before being sent over the wire.

**Stage:** Display only — never used by parser/semantic/ICG/interpreter.

**Special handling for negative literals:** GAL writes negatives as `~5`, but the lexer emits them as `Token('intlit', '~5', ...)` (the type stays `'intlit'`, the value carries the `~`). When the IDE renders this, we want it labeled as **"negative integer"** to make the distinction clear in the lexeme table. The two `if` checks at the top of the function handle this.

**Defense answer:** *"This is purely a display function. It maps internal token types to user-facing labels for the lexeme view. It's never on the execution path."*

---

## 5. LINE-BY-LINE / BLOCK-BY-BLOCK EXPLANATION

### 5.1 `Position.__init__`

```python
def __init__(self, index, ln, col=0):
    self.index = index
    self.ln = ln
    self.col = col
```

**What this block does:** Stores three integers describing where in the source we are.

**Why this logic is needed:** Three coordinates are tracked, not just one, because:
- `index` (0-based character offset) is used internally by the lexer to slice the source string.
- `ln` (1-based line) and `col` (0-based column) are used in error messages, where humans count lines from 1.

**What data is being changed:** The new `Position` instance gets three field values.

**Defense answer:** *"`index` is for the lexer's bookkeeping; `ln` and `col` are for human-readable error messages. We separate them because the line/column are 1-based for humans but the index is 0-based for slicing."*

### 5.2 `Position.advance(current_char)`

```python
def advance(self, current_char):
    self.index += 1
    self.col += 1
    if current_char == '\n':
        self.ln += 1
        self.col = 0
    return self
```

**What this block does:** Moves the position forward by one character. If the character we just consumed was a newline, the line counter ticks up and the column resets.

**Why this logic is needed:** Without per-character advancement, line numbers in errors would be wrong. The crucial observation is the position is updated **based on the character we just consumed**, not on the next one. So when `\n` is the current char and we advance, the position now points to the **start of the new line**.

**What happens next:** The lexer reads the next character at `self.source_code[self.pos.index]`.

**Defense answer:** *"`advance()` is called once per character. It bumps the index and column. If the character was a newline, it increments the line and resets the column to 0 for the new line. This is how every error message in the compiler ultimately knows its line and column."*

### 5.3 `LexicalError.as_string()`

```python
def as_string(self):
    self.details = self.details.replace('\n', '\\n')
    return f"LEXICAL error line {self.pos.ln} col {self.pos.col} {self.details}"
```

**What this block does:** Formats the error as a single line, escaping any embedded newlines in the description.

**Why this logic is needed:** Errors are sometimes generated with multi-line context strings; we want them rendered as a single line in the IDE's error console.

**Edge case:** Calling `as_string()` twice mutates `self.details` once (first call replaces `\n`, second call has nothing to replace). This is harmless but technically not idempotent. *I would mark this as needs-verification if a panelist asks — it does not affect correctness.*

**Defense answer:** *"This produces the standard error string that the IDE displays in the error pane: `'LEXICAL error line 4 col 7: invalid character'`. The format is consistent across all error types so the frontend can parse and display it uniformly."*

### 5.4 The `Token` class

```python
class Token:
    def __init__(self, type_, value=None, line=1, col=0):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col
```

**What this block does:** Defines the data shape for every token in the compiler.

**Why this logic is needed:** Every later stage will read these four fields and only these four fields. There is no inheritance, no abstract method — just data.

**The trailing parameter pattern:** `type_` (with the trailing underscore) is named that way because `type` is a Python builtin and shadowing it in a constructor argument would cause subtle bugs if the class internals ever called `type(self.value)` later.

**Defense answer:** *"A token is just four fields: type, value, line, column. We deliberately keep it dumb. The behavior — display, comparison, parsing — happens in the layers that consume the token, not on the token itself. This separation lets the same `Token` class flow through all five compiler stages unchanged."*

### 5.5 The token-type constants (block view)

```python
TT_RW_SEED = 'seed'      # the word `seed` in source becomes Token('seed', 'seed', ...)
TT_PLUS = '+'            # the symbol `+` becomes Token('+', '+', ...)
TT_INTEGERLIT = 'intlit' # the digits `42` become Token('intlit', '42', ...)
TT_IDENTIFIER = 'id'     # the word `myVar` becomes Token('id', 'myVar', ...)
TT_EOF = 'EOF'           # synthetic end-of-input marker
```

**What this block does:** Establishes the 60-or-so distinct token types the compiler recognizes.

**Why this logic is needed:** Without these constants, the lexer would scatter raw string literals like `'seed'`, `'+'`, `'EOF'` throughout its body, and a typo in any one would silently break recognition. By naming them as Python constants, typos become `NameError`s the IDE catches immediately.

**Why the keywords are stored as themselves:** `TT_RW_SEED = 'seed'`, not `'KW_SEED'`. The benefit: when you read a `Token`, you can immediately see "oh this is the `seed` keyword" without needing a translation table. The cost: identifiers and keywords share a namespace of comparison strings, but since identifiers always have type `'id'` (never the keyword text), there's no collision.

**Defense answer:** *"The token-type system is the agreement between the lexer and every later stage. We use plain strings rather than enums for two reasons: hashability (needed for the LL(1) predict-set dictionary), and readability (the parser's grammar productions reference `'seed'` directly, which matches the source-language keyword)."*

---

## 6. DEFENSE QUESTION PREPARATION

**Q: Why do you have a separate `Position` class instead of just passing line/column integers around?**

> "Three reasons. First, the lexer copies positions when it begins a multi-character token — `pos = self.pos.copy()` — so an error message can point to the *start* of an unclosed string, not the end. A separate class makes that copy operation atomic. Second, every error in the system carries a position; centralizing it into one class means we change the format in one place. Third, we may extend it later (e.g., adding the file name when we support multi-file programs) without touching every call site."

**Q: Why doesn't `Token` have an `__eq__` or `__repr__`?**

> "Intentional. Token comparisons in our codebase are always against a specific field — `token.type == 'seed'`, never `token == something`. Defining `__eq__` would invite ambiguous comparisons that compare across fields. For display, we use `_display_value(token.value)` and `get_token_description(token.type, token.value)` so we have controlled formatting in the IDE."

**Q: How do you tell a keyword apart from an identifier?**

> "The lexer scans an alphanumeric run, then checks if the resulting string is in our keyword set. If yes, the token type is the keyword text itself (e.g., `'seed'`); if no, the token type is `'id'` and the identifier text becomes the value. So `seed` produces `Token('seed', 'seed', …)` while `seedling` produces `Token('id', 'seedling', …)`. This collision-free scheme works because the parser's grammar only accepts `'id'` where an identifier is expected, never a keyword string."

**Q: Why are token types strings, not an enum?**

> "Three reasons: hashability — they're keys in the LL(1) predict-set dictionary; mirror-readability — the grammar productions in `cfg.py` use the same strings as terminals, so the grammar reads like the source language; and zero overhead — no enum-attribute access on every comparison. The `TT_*` Python names act as a self-documenting catalogue."

**Q: What does the `~` prefix in a token's value mean?**

> "GAL uses `~` for negative literals. When the lexer sees `~5`, it produces `Token('intlit', '~5', …)` — the type stays `intlit` (because it's still an integer), but the value carries the tilde. The interpreter's literal-parser detects the leading `~` and converts it to Python's `-` before computing. This design avoids needing a separate `unary minus` grammar production."

**Q: What is `LexicalError.as_string()` and where is it used?**

> "It produces the user-facing error string in our standard format: `LEXICAL error line N col M: details`. It's called when assembling the error list that `server.py` returns to the IDE. The format is consistent across the whole compiler — every layer's error type produces a similar string so the IDE can color and place them uniformly."

**Q: Why are some `delim` constants apparently unused?**

> "Each `delim` set corresponds one-to-one with a row in the regular-definition table from our compiler proposal. The actively-used ones drive lookahead checks in the scanner. The others are kept as **living documentation** that ties the implementation to the spec. Removing them would lose that traceability. They cost us nothing at runtime."

**Q: What happens if the same source text could match two different tokens (e.g., `==` and `=`)?**

> "This is the classic 'maximal munch' problem. We resolve it by ordering: the scanner checks the longer pattern first. When the current char is `=`, the lexer peeks at the next char. If the next is also `=`, we emit `==`; otherwise `=`. Same logic for `<=`, `>=`, `!=`, `&&`, `||`, `++`, `--`, `+=`, `-=`, `*=`, `/=`, `%=`. There are no ambiguous cases that survive the maximal-munch rule."

**Q: Could a malformed source crash the lexer?**

> "No. Every error path constructs a `LexicalError` and `continue`s scanning. The lexer never raises — it only collects errors into a list and returns them alongside whatever tokens it managed to recognize. Even an unclosed multi-line comment is recovered: we report the unclosed-comment error and treat everything from `/*` to EOF as comment text. The server then short-circuits the pipeline because `lex_errors` is non-empty."

---

## 7. SIMPLE WALKTHROUGH EXAMPLE

Sample code:

```
root() {
    seed age = 10;
    plant(age);
    reclaim;
}
```

How **tokens and errors** are produced:

The lexer scans this text and produces a list of `Token` objects. Here is the complete stream (with line and column hints):

| `type` | `value` | `line` | `col` |
|---|---|---|---|
| `'root'` | `'root'` | 1 | 0 |
| `'('` | `'('` | 1 | 4 |
| `')'` | `')'` | 1 | 5 |
| `'{'` | `'{'` | 1 | 7 |
| `'\n'` | `'\n'` | 1 | 8 |
| `'seed'` | `'seed'` | 2 | 4 |
| `'id'` | `'age'` | 2 | 9 |
| `'='` | `'='` | 2 | 13 |
| `'intlit'` | `'10'` | 2 | 15 |
| `';'` | `';'` | 2 | 17 |
| `'\n'` | `'\n'` | 2 | 18 |
| `'plant'` | `'plant'` | 3 | 4 |
| `'('` | `'('` | 3 | 9 |
| `'id'` | `'age'` | 3 | 10 |
| `')'` | `')'` | 3 | 13 |
| `';'` | `';'` | 3 | 14 |
| `'\n'` | `'\n'` | 3 | 15 |
| `'reclaim'` | `'reclaim'` | 4 | 4 |
| `';'` | `';'` | 4 | 11 |
| `'\n'` | `'\n'` | 4 | 12 |
| `'}'` | `'}'` | 5 | 0 |
| `'EOF'` | `''` | 5 | 1 |

A few observations:

- Keywords like `root`, `seed`, `plant`, `reclaim` carry their own keyword-string as the type AND the value.
- The identifier `age` has type `'id'` — same word `age` appears both in the declaration and the use, but each occurrence becomes a separate `Token` with its own line/column.
- `10` becomes `Token('intlit', '10', 2, 15)`. The value is the **string** `'10'` at this stage; the conversion to the Python integer `10` happens later in the interpreter.
- Newlines are emitted as `Token('\n', '\n', …)` tokens. The parser is configured with `skip_token_types={'\n'}`, so it ignores these — but they exist in the stream so that the lexer's line counter advances and so that the lexer can use them as delimiters.
- The synthetic `EOF` token at the end has empty value and is produced by the lexer to mark "no more input."

`errors` is the empty list `[]` because this code is well-formed.

**If the user typed `seed age @ 10;` instead:** when the scanner sees `@`, it doesn't match any token rule. It builds:

```python
LexicalError(pos=Position(index=10, ln=2, col=8), details="Invalid character '@'")
```

…appends it to `errors`, calls `advance()` to skip past `@`, and continues scanning. The token list still contains everything before and after `@`, but `errors` is non-empty. `server.py` sees this and short-circuits the pipeline at the lexical stage.

---

## 8. DEFENSE-READY EXPLANATION (memorize this)

> "**The token and error layer is the foundation of the entire compiler.** It defines three classes: `Position`, which tracks index, line, and column for precise error reporting; `LexicalError`, which packages a position and a description into a structured error record; and `Token`, which is the four-field data carrier — type, value, line, column — that flows through every stage from the lexer to the interpreter. **It also defines roughly 60 token-type constants** that every later stage reads to identify what each token represents — keywords like `seed` and `pollinate`, operators like `+` and `==`, and meta-types like `id`, `intlit`, `dbllit`, `EOF`. **These constants are plain strings**, not enums, because they double as terminals in our LL(1) grammar and as keys in the parser's predict-set table — readability and hashability without enum overhead. **The `Token` class is intentionally minimal — no methods, no comparisons, no display logic** — so that the parser, semantic analyzer, ICG, and interpreter can read tokens cheaply and the IDE can render them uniformly via the helper `get_token_description`. **Errors and positions stay structured** all the way to the IDE so the frontend can highlight the exact line and column of any problem."

---

*Next file in the defense-prep series: `lexer.py` (the `Lexer` class itself) — character scanning, token recognition, every kind of literal, and how lexical errors are reported and recovered.*
