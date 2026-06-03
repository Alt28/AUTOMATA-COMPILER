
# AUTO: Imports names from another module.
from .scanner import Lexer, lex

# AUTO: Imports names from another module.
from shared.tokens import *  # noqa: F401,F403  - TT_* constants
# AUTO: Imports names from another module.
from shared.tokens import Token, get_token_description  # noqa: F401  - explicit
# AUTO: Imports names from another module.
from lexer.positions import Position  # noqa: F401
# AUTO: Imports names from another module.
from lexer.errors import LexicalError  # noqa: F401
