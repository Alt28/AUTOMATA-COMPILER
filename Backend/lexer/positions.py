

# AUTO: Defines class `Position`.
class Position:

    # AUTO: Defines function `__init__`.
    def __init__(self, index, ln, col=0):
        # AUTO: Sets `self.index`.
        self.index = index
        # AUTO: Sets `self.ln`.
        self.ln = ln
        # AUTO: Sets `self.col`.
        self.col = col

    # AUTO: Defines function `advance`.
    def advance(self, current_char):
        # AUTO: Adds into `self.index`.
        self.index += 1
        # AUTO: Adds into `self.col`.
        self.col += 1

        # AUTO: Checks this condition.
        if current_char == '\n':
            # AUTO: Adds into `self.ln`.
            self.ln += 1
            # AUTO: Sets `self.col`.
            self.col = 0

        # AUTO: Returns this result to the caller.
        return self

    # AUTO: Defines function `copy`.
    def copy(self):
        # AUTO: Returns this result to the caller.
        return Position(self.index, self.ln, self.col)
