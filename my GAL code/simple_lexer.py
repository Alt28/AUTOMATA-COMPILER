from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class Token:
    type: str
    value: Optional[str]
    line: int


KEYWORDS = {
    'water', 'plant', 'seed', 'tree', 'branch', 'leaf', 'spring', 'harvest',
    'cultivate', 'grow', 'tend', 'root', 'variety', 'soil', 'prune', 'fertile',
    'sunshine', 'frost', 'pollinate', 'reclaim', 'skip', 'bundle', 'empty'
}

SYMBOLS_2 = {
    '==', '+=', '-=', '*=', '/=', '%=', '<=', '>=', '!=', '++', '--', '&&', '||'
}

SYMBOLS_1 = set("+-*/%=<>(){}[],;:![]~.")


def _is_ident_start(ch: str) -> bool:
    return ch.isalpha() or ch == '_'


def _is_ident_part(ch: str) -> bool:
    return ch.isalnum() or ch == '_'


def lex(source: str) -> Tuple[List[Token], List[str]]:
    tokens: List[Token] = []
    errors: List[str] = []

    i = 0
    n = len(source)
    line = 1
    col = 1

    def peek(offset=0):
        j = i + offset
        return source[j] if 0 <= j < n else ''

    def advance(k=1):
        nonlocal i, line, col
        for _ in range(k):
            if i < n:
                if source[i] == '\n':
                    line += 1
                    col = 1
                else:
                    col += 1
            i += 1

    # main loop
    while i < n:
        ch = peek()

        # whitespace
        if ch.isspace():
            advance()
            continue

        # comments: //... or /* ... */
        if ch == '/' and peek(1) == '/':
            advance(2)
            while i < n and peek() not in ('\n', '\r'):
                advance()
            continue
        if ch == '/' and peek(1) == '*':
            advance(2)
            closed = False
            while i < n:
                if peek() == '*' and peek(1) == '/':
                    advance(2)
                    closed = True
                    break
                advance()
            if not closed:
                errors.append(f"Lexical Error at line {line}, column {col}: Unterminated block comment")
            continue

        start_line, start_col = line, col

        # identifiers/keywords
        if _is_ident_start(ch):
            ident = []
            while _is_ident_part(peek()):
                ident.append(peek())
                advance()
            name = ''.join(ident)
            tok_type = name if name in KEYWORDS else 'idf'
            tokens.append(Token(tok_type, name, start_line))
            continue

        # numbers (optional ~ for negative)
        if ch == '~' and peek(1).isdigit():
            sign = '-'
            advance()
            ch = peek()
        else:
            sign = ''
        if ch.isdigit():
            num = []
            while peek().isdigit():
                num.append(peek())
                advance()
            if peek() == '.':
                num.append('.')
                advance()
                if not peek().isdigit():
                    errors.append(f"Lexical Error at line {start_line}, column {start_col}: Digit expected after '.'")
                while peek().isdigit():
                    num.append(peek())
                    advance()
                tokens.append(Token('dbllit', sign + ''.join(num), start_line))
            else:
                tokens.append(Token('intlit', sign + ''.join(num), start_line))
            continue

        # strings
        if ch == '"':
            advance()  # skip opening
            s = []
            ok = False
            while i < n:
                c = peek()
                if c == '"':
                    ok = True
                    advance()
                    break
                if c == '\n':
                    break
                if c == '\\':
                    advance()
                    esc = peek()
                    mapping = {'"': '"', '\\': '\\', 'n': '\n', 't': '\t', '0': '\0'}
                    s.append(mapping.get(esc, esc))
                    advance()
                else:
                    s.append(c)
                    advance()
            if not ok:
                errors.append(f"Lexical Error at line {start_line}, column {start_col}: Unterminated string literal")
            else:
                tokens.append(Token('strnglit', ''.join(s), start_line))
            continue

        # chars
        if ch == "'":
            advance()
            c = peek()
            if c == '\\':
                advance()
                esc = peek()
                mapping = {"'": "'", "\\": "\\", 'n': '\n', 't': '\t', '0': '\0'}
                val = mapping.get(esc, esc)
                advance()
            else:
                val = c
                advance()
            if peek() != "'":
                errors.append(f"Lexical Error at line {start_line}, column {start_col}: Unterminated character literal")
            else:
                advance()
                tokens.append(Token('chrlit', val, start_line))
            continue

        # two-char operators
        two = ch + peek(1)
        if two in SYMBOLS_2:
            tokens.append(Token(two, two, start_line))
            advance(2)
            continue

        # single-char symbols
        if ch in SYMBOLS_1:
            tokens.append(Token(ch, ch, start_line))
            advance()
            continue

        # unknown
        errors.append(f"Lexical Error at line {start_line}, column {start_col}: Illegal character: '{ch}'")
        advance()

    tokens.append(Token('EOF', 'EOF', line))
    return tokens, errors
