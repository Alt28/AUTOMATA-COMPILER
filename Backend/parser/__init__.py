# ============================================================================
# PARSER PACKAGE - Public API for syntax analysis + AST construction
# ============================================================================
# Re-exports LL1Parser so external callers (server.py) can keep using:
#     from parser import LL1Parser
# unchanged after the restructure.
#
# In a later phase (5b), parser/builder.py will hold build_ast and the parser
# will import it as a sibling rather than reaching across to GALsemantic.py.
# ============================================================================

from .parser import LL1Parser  # noqa: F401  - main public class
