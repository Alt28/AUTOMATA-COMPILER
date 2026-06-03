# AUTO: Imports a module used by this file.
import re

# AUTO: Sets `_REDUNDANT_PREFIX`.
_REDUNDANT_PREFIX = re.compile(r'^(Runtime Error|Semantic Error|Type Mismatch|Syntax Error)\s*:?\s*', re.IGNORECASE)


# AUTO: Defines class `ReturnValue`.
class ReturnValue(Exception):

    # AUTO: Defines function `__init__`.
    def __init__(self, value):
        # AUTO: Sets `self.value`.
        self.value = value


# AUTO: Defines class `_CancelledError`.
class _CancelledError(Exception):
    # AUTO: Does nothing for this required block.
    pass


# AUTO: Defines class `InterpreterError`.
class InterpreterError(Exception):

    # AUTO: Defines function `__init__`.
    def __init__(self, message, line):
        # AUTO: Calls `super`.
        super().__init__(message)
        # AUTO: Sets `clean`.
        clean = _REDUNDANT_PREFIX.sub('', str(message)).strip()
        # AUTO: Checks this condition.
        if line is not None and str(line) != "":
            # AUTO: Sets `self.message`.
            self.message = f"RUNTIME error line {line}: {clean}"
        # AUTO: Runs when previous condition did not pass.
        else:
            # AUTO: Sets `self.message`.
            self.message = clean

    # AUTO: Defines function `__str__`.
    def __str__(self):
        # AUTO: Returns this result to the caller.
        return self.message


# AUTO: Defines class `InterpreterInputRequest`.
class InterpreterInputRequest(Exception):

    # AUTO: Defines function `__init__`.
    def __init__(self, prompt, line):
        # AUTO: Sets `self.prompt`.
        self.prompt = prompt
        # AUTO: Sets `self.line`.
        self.line = line
