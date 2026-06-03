# AUTO: Imports a module used by this file.
import re

# AUTO: Sets `_REDUNDANT_PREFIX`.
_REDUNDANT_PREFIX = re.compile(r'^(Semantic Error|Syntax Error|Type Mismatch|Runtime Error)\s*:?\s*', re.IGNORECASE)


# AUTO: Defines class `SemanticError`.
class SemanticError(Exception):
    # AUTO: Defines function `__init__`.
    def __init__(self, message, line):
        # AUTO: Calls `super`.
        super().__init__(message)
        # AUTO: Sets `clean`.
        clean = _REDUNDANT_PREFIX.sub('', str(message)).strip()
        # AUTO: Sets `self.message`.
        self.message = f"SEMANTIC error line {line}: {clean}"

    # AUTO: Defines function `__str__`.
    def __str__(self):
        # AUTO: Returns this result to the caller.
        return self.message
