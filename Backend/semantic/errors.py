import re

_REDUNDANT_PREFIX = re.compile(r'^(Semantic Error|Syntax Error|Type Mismatch|Runtime Error)\s*:?\s*', re.IGNORECASE)


class SemanticError(Exception):
    def __init__(self, message, line):
        super().__init__(message)
        clean = _REDUNDANT_PREFIX.sub('', str(message)).strip()
        self.message = f"SEMANTIC error line {line}: {clean}"

    def __str__(self):
        return self.message
