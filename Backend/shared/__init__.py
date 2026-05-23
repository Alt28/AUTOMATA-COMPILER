# ============================================================================
# SHARED PACKAGE - Cross-phase types used by every compiler stage
# ============================================================================
# Contains only the building blocks that genuinely cross phase boundaries:
#   - tokens     : TT_* constants, Token class, get_token_description
#                  (lexer creates, parser/semantic/icg/interpreter read)
#   - ast_nodes  : AST node class hierarchy
#                  (parser builds, semantic/icg/interpreter walk)
#
# Phase-private types live with their phase:
#   - lexer/positions.py    : Position class (lexer-owned)
#   - lexer/delimiters.py   : FSM character sets (lexer-only)
#   - lexer/errors.py       : LexicalError
#   - semantic/errors.py    : SemanticError
#   - interpreter/errors.py : InterpreterError, ReturnValue, etc.
# ============================================================================

from .tokens import *  # noqa: F401,F403 - TT_* constants
from .tokens import Token, get_token_description  # noqa: F401
from .ast_nodes import *  # noqa: F401,F403
