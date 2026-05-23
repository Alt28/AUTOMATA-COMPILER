# ============================================================================
# SEMANTIC PACKAGE - Symbol table + tree-walking AST validator
# ============================================================================
# Public API:
#     from semantic import SymbolTable, validate_ast, ASTValidator
# ============================================================================

from .symbol_table import SymbolTable  # noqa: F401
from .analyzer import ASTValidator, validate_ast  # noqa: F401
