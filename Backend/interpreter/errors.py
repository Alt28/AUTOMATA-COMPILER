import re

_REDUNDANT_PREFIX = re.compile(r'^(Runtime Error|Semantic Error|Type Mismatch|Syntax Error)\s*:?\s*', re.IGNORECASE)


class ReturnValue(Exception):

    def __init__(self, value):
        self.value = value


class _CancelledError(Exception):
    pass


class InterpreterError(Exception):

    def __init__(self, message, line):
        super().__init__(message)
        clean = _REDUNDANT_PREFIX.sub('', str(message)).strip()
        if line is not None and str(line) != "":
            self.message = f"RUNTIME error line {line}: {clean}"
        else:
            self.message = clean

    def __str__(self):
        return self.message


class InterpreterInputRequest(Exception):

    def __init__(self, prompt, line):
        self.prompt = prompt
        self.line = line
