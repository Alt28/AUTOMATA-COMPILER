# ============================================================================
# LEXER PACKAGE - Public API for the lexical-analysis phase
# ============================================================================
# Re-exports everything needed by external callers (server.py, parser, tests).
# After the modular restructure, `from lexer import lex, Token, TT_RW_ROOT, ...`
# still works exactly as before — the Lexer class itself lives in
# lexer/scanner.py, while shared types live in tokens.py / positions.py /
# errors.py at the Backend/ root.
# ============================================================================

from .scanner import Lexer, lex                           # the FSM + main entry point

# Re-export shared types so old `from lexer import X` callers keep working.
from shared.tokens import *  # noqa: F401,F403  - TT_* constants
from shared.tokens import Token, get_token_description  # noqa: F401  - explicit
from lexer.positions import Position  # noqa: F401
from lexer.errors import LexicalError  # noqa: F401
