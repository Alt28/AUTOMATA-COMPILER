# ============================================================================
# POSITION CLASS - Tracks current location in source code
# ============================================================================
# Extracted from lexer.py during the modular restructure.
# Shared by every compiler phase that needs to report source locations
# (lexer, parser, semantic analyzer, ICG, interpreter).
# ============================================================================


class Position:
    """Tracks the position (line, column, index) in the source code for error reporting"""

    def __init__(self, index, ln, col=0):
        self.index = index  # Character index in source code (0-based)
        self.ln = ln        # Line number (1-based)
        self.col = col      # Column number (0-based)

    def advance(self, current_char):
        """Advance to the next character, updating line/column numbers"""
        self.index += 1
        self.col += 1

        if current_char == '\n':  # New line detected
            self.ln += 1
            self.col = 0  # Reset column to start of line

        return self

    def copy(self):
        """Returns a copy of the current position (for error tracking)"""
        return Position(self.index, self.ln, self.col)
