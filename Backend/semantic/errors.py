

class SemanticError(Exception):
    def __init__(self, message, line):
        super().__init__(message)
        self.message = f"Ln {line} {message}"

    def __str__(self):
        return self.message
