

# AUTO: Defines class `LexicalError`.
class LexicalError:

    # AUTO: Defines function `__init__`.
    def __init__(self, pos, details):
        # AUTO: Sets `self.pos`.
        self.pos = pos
        # AUTO: Sets `self.details`.
        self.details = details

    # AUTO: Defines function `as_string`.
    def as_string(self):
        # AUTO: Sets `self.details`.
        self.details = self.details.replace('\n', '\\n')
        # AUTO: Returns this result to the caller.
        return f"LEXICAL error line {self.pos.ln} col {self.pos.col} {self.details}"
