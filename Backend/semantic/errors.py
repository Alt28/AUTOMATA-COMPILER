# ============================================================================
# SEMANTIC ERROR - Raised during AST construction / validation
# ============================================================================
# Raised by parser/builder.py (during AST construction) and by
# semantic/analyzer.py (during the final tree-walking validation pass).
# Includes the source line so the IDE can highlight the right location.
# ============================================================================


class SemanticError(Exception):
    def __init__(self, message, line):
        super().__init__(message)
        self.message = f"Ln {line} {message}"

    def __str__(self):
        return self.message
