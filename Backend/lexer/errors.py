

class LexicalError:

    def __init__(self, pos, details):
        self.pos = pos
        self.details = details

    def as_string(self):
        self.details = self.details.replace('\n', '\\n')
        return f"LEXICAL error line {self.pos.ln} col {self.pos.col} {self.details}"
