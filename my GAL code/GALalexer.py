
"""GrowALanguage Lexer (updated)
This lexer implements the lexical rules defined in the GrowALanguage specification.
See the project PDF/spec for language rules (identifiers, literals, comments, operators, and keywords).
"""

from dataclasses import dataclass
import re
from typing import List, Optional, Tuple, Any
import sys
import json
import argparse

SINGLE_CHAR_TOKENS = {
    '(': 'TT_OPPAR',
    ')': 'TT_CLPAR',
    '[': 'TT_OPBRA',
    ']': 'TT_CLBRA',
    '{': 'TT_OPCUR',
    '}': 'TT_CLCUR',
    ';': 'TT_SEMICOL',
    ',': 'TT_COMMA',
    '.': 'TT_DOT',
    '+': 'TT_PLUS',
    '-': 'TT_MINUS',
    '*': 'TT_MUL',
    '/': 'TT_DIV',
    '%': 'TT_MOD',
    '!': 'TT_NOT',
    '<': 'TT_LT',
    '>': 'TT_GT',
    '=': 'TT_IS',
    "'": 'TT_QT',
}

MULTI_CHAR_TOKENS = {
    '==': 'TT_EQ',
    '!=': 'TT_NEQ',
    '<=': 'TT_LTE',
    '>=': 'TT_GTE',
    '&&': 'TT_AND',
    '||': 'TT_OR',
    '++': 'TT_INC',
    '--': 'TT_DEC',
}

KEYWORDS = {
    'seed': 'TT_RW_SEED',
    'tree': 'TT_RW_TREE',
    'leaf': 'TT_RW_LEAF',
    'branch': 'TT_RW_BRANCH',
    'root': 'TT_RW_ROOT',
    'reclaim': 'TT_RW_RECLAIM',
    'pollinate': 'TT_RW_POLLINATE',
    'grow': 'TT_RW_GROW',
    'cultivate': 'TT_RW_CULTIVATE',
    'tend': 'TT_RW_TEND',
    'sprout': 'TT_RW_SPROUT',
    'bud': 'TT_RW_BUD',
    'wither': 'TT_RW_WITHER',
    'sunshine': 'TT_BOOL_TRUE',
    'frost': 'TT_BOOL_FALSE',
}

@dataclass
class Position:
    index: int
    ln: int
    def advance(self, current_char: Optional[str]) -> 'Position':
        self.index += 1
        if current_char == '\n':
            self.ln += 1
        return self
    def copy(self) -> 'Position':
        return Position(self.index, self.ln)

@dataclass
class Token:
    type: str
    value: Optional[Any] = None
    line: int = 1

class LexicalError(Exception):
    def __init__(self, pos: Position, details: str):
        self.pos = Position(pos.index, pos.ln)
        self.details = details.replace('\n', '\\n')
    def __str__(self):
        return f"Ln {self.pos.ln} Lexical Error: {self.details}"

class Lexer:
    IDENTIFIER_MAX_LEN = 16
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.pos = Position(-1, 1)
        self.current_char: Optional[str] = None
        self.advance()
    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.source_code[self.pos.index] if self.pos.index < len(self.source_code) else None
    def peek(self, n=1) -> Optional[str]:
        idx = self.pos.index + n
        return self.source_code[idx] if idx < len(self.source_code) else None
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char in ' \t\r':
            self.advance()
    def skip_comments(self, errors: List['LexicalError']) -> bool:
        if self.current_char == '/' and self.peek() == '/':
            while self.current_char is not None and self.current_char != '\n':
                self.advance()
            return True
        # Support shell-style line comments starting with '#'
        if self.current_char == '#':
            while self.current_char is not None and self.current_char != '\n':
                self.advance()
            return True
        if self.current_char == '/' and self.peek() == '*':
            self.advance(); self.advance()
            while True:
                if self.current_char is None:
                    errors.append(LexicalError(self.pos.copy(), "Unterminated multi-line comment '/* ...'"))
                    return True
                if self.current_char == '*' and self.peek() == '/':
                    self.advance(); self.advance()
                    break
                self.advance()
            return True
        return False
    def make_identifier_or_keyword(self) -> 'Token':
        start_pos = self.pos.copy()
        ident = ''
        while self.current_char is not None and re.match(r'[A-Za-z0-9_]', self.current_char):
            if len(ident) >= self.IDENTIFIER_MAX_LEN:
                ident += self.current_char
                self.advance()
                while self.current_char is not None and re.match(r'[A-Za-z0-9_]', self.current_char):
                    ident += self.current_char
                    self.advance()
                raise LexicalError(start_pos, f"Identifier '{ident}' exceeds maximum length of {self.IDENTIFIER_MAX_LEN} characters.")
            ident += self.current_char
            self.advance()
        if ident in KEYWORDS:
            return Token(KEYWORDS[ident], ident, start_pos.ln)
        return Token('TT_IDENTIFIER', ident, start_pos.ln)
    def make_number(self) -> 'Token':
        start_pos = self.pos.copy()
        num_str = ''
        is_float = False
        if self.current_char == '~':
            num_str += self.current_char
            self.advance()
            if self.current_char is None or not self.current_char.isdigit():
                raise LexicalError(start_pos, "Tilde '~' must precede a number (e.g., ~10).")
        digits_seen = False
        while self.current_char is not None and self.current_char.isdigit():
            digits_seen = True
            num_str += self.current_char
            self.advance()
        if self.current_char == '.' and (self.peek() or '').isdigit():
            is_float = True
            num_str += '.'
            self.advance()
            if self.current_char is None or not self.current_char.isdigit():
                raise LexicalError(start_pos, 'Decimal point must be followed by digits.')
            while self.current_char is not None and self.current_char.isdigit():
                num_str += self.current_char
                self.advance()
        if self.current_char is not None and self.current_char in 'eE':
            is_float = True
            num_str += self.current_char
            self.advance()
            if self.current_char in '+-':
                num_str += self.current_char
                self.advance()
            if self.current_char is None or not self.current_char.isdigit():
                raise LexicalError(start_pos, "Exponent 'e' must be followed by an integer exponent (e.g., 1.2e5).")
            while self.current_char is not None and self.current_char.isdigit():
                num_str += self.current_char
                self.advance()
        if not digits_seen and not is_float:
            raise LexicalError(start_pos, 'Invalid numeric literal.')
        tok_type = 'TT_FLOAT_LIT' if is_float or '.' in num_str or 'e' in num_str or 'E' in num_str else 'TT_INT_LIT'
        return Token(tok_type, num_str, start_pos.ln)
    def make_char(self) -> 'Token':
        start_pos = self.pos.copy()
        self.advance()
        if self.current_char is None:
            raise LexicalError(start_pos, 'Unterminated character literal.')
        if self.current_char == '\\':
            esc_start = self.pos.copy()
            self.advance()
            if self.current_char not in ["'", '\\', 'n', 't', 'r']:
                raise LexicalError(esc_start, 'Invalid escape sequence in character literal.')
            ch = '\\' + self.current_char
            self.advance()
        else:
            ch = self.current_char
            self.advance()
        if self.current_char != "'":
            raise LexicalError(start_pos, 'Character literal must contain exactly one character enclosed in single quotes.')
        self.advance()
        return Token('TT_CHAR_LIT', ch, start_pos.ln)
    def make_tokens(self) -> Tuple[List['Token'], List['LexicalError']]:
        tokens: List[Token] = []
        errors: List[LexicalError] = []
        while self.current_char is not None:
            if self.current_char in ' \t\r':
                self.skip_whitespace(); continue
            if self.current_char == '\n':
                tokens.append(Token('TT_NL', None, self.pos.ln)); self.advance(); continue
            if self.skip_comments(errors):
                continue
            if re.match(r'[A-Za-z_]', self.current_char or ''):
                try:
                    tokens.append(self.make_identifier_or_keyword())
                except LexicalError as e:
                    errors.append(e)
                continue
            if self.current_char.isdigit() or self.current_char == '~':
                try:
                    tokens.append(self.make_number())
                except LexicalError as e:
                    errors.append(e)
                continue
            if self.current_char == "'":
                try:
                    tokens.append(self.make_char())
                except LexicalError as e:
                    errors.append(e)
                continue
            two = (self.current_char or '') + (self.peek() or '')
            if two in MULTI_CHAR_TOKENS:
                tokens.append(Token(MULTI_CHAR_TOKENS[two], two, self.pos.ln))
                self.advance(); self.advance(); continue
            if self.current_char in SINGLE_CHAR_TOKENS:
                tokens.append(Token(SINGLE_CHAR_TOKENS[self.current_char], self.current_char, self.pos.ln))
                self.advance(); continue
            errors.append(LexicalError(self.pos.copy(), f"Unexpected character '{self.current_char}'"))
            self.advance()
        tokens.append(Token('TT_EOF', None, self.pos.ln))
        return tokens, errors

def lex(source_code: str) -> Tuple[List[Token], List[LexicalError]]:
    return Lexer(source_code).make_tokens()


def _tokens_to_json(tokens: List[Token]) -> List[dict]:
    return [{
        'type': t.type,
        'value': t.value,
        'line': t.line,
    } for t in tokens]


def _errors_to_json(errors: List[LexicalError]) -> List[str]:
    return [str(e) for e in errors]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='GrowALanguage Lexer CLI')
    parser.add_argument('-f', '--file', help='Path to source file to lex')
    parser.add_argument('-c', '--code', help='Inline source code string to lex')
    parser.add_argument('--no-json', action='store_true', help='Print human-readable output instead of JSON')
    args = parser.parse_args()

    if args.file:
        with open(args.file, 'r', encoding='utf-8') as fh:
            source = fh.read()
    elif args.code is not None:
        source = args.code
    else:
        # Read from stdin if neither file nor code provided
        source = sys.stdin.read()

    tokens, errors = lex(source)

    if args.no_json:
        # Human-readable
        for t in tokens:
            print(f"{t.line:>3}: {t.type:15} {t.value if t.value is not None else ''}")
        if errors:
            print('\nErrors:')
            for e in errors:
                print(f"- {e}")
        sys.exit(0 if not errors else 1)
    else:
        # Default JSON output compatible with frontend expectations
        out = {
            'tokens': _tokens_to_json(tokens),
            'errors': _errors_to_json(errors),
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
        sys.exit(0 if not errors else 1)
