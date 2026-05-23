# ============================================================================
# LEXICAL ERROR - Raised by the lexer FSM on illegal characters / delimiters
# ============================================================================
# Stores a Position so the IDE can highlight the offending column.
# Lives next to the scanner because lexical errors are a pure lexer concern.
# ============================================================================


class LexicalError:
    """Stores information about a lexical error (position and description)"""

    def __init__(self, pos, details):
        self.pos = pos          # Position object where error occurred
        self.details = details  # Error description

    def as_string(self):
        """Returns the error message in readable string format"""
        self.details = self.details.replace('\n', '\\n')  # Escape newlines in error message
        return f"LEXICAL error line {self.pos.ln} col {self.pos.col} {self.details}"
