# ============================================================================
# RUNTIME / INTERPRETER ERRORS - Raised by the tree-walking interpreter
# ============================================================================
# Lives with the interpreter because these are pure runtime concerns:
#   - ReturnValue      : control-flow unwind for `reclaim <expr>;`
#   - _CancelledError  : raised when the user starts a new run mid-execution
#   - InterpreterError : standard runtime error (division by zero, etc.)
#   - InterpreterInputRequest : raised when water() needs input from the client
# ============================================================================


class ReturnValue(Exception):
    """Raised by 'reclaim <expr>;' to unwind out of a function with a value."""

    def __init__(self, value):
        self.value = value


class _CancelledError(Exception):
    """Raised when an interpreter is cancelled mid-execution."""
    pass


class InterpreterError(Exception):
    """All runtime errors raised by the interpreter inherit from this."""

    def __init__(self, message, line):
        super().__init__(message)
        if line is not None:
            self.message = f"Ln {line} {message}"
        else:
            self.message = message

    def __str__(self):
        return self.message


class InterpreterInputRequest(Exception):
    """Carries a prompt up the call stack when water() needs input."""

    def __init__(self, prompt, line):
        self.prompt = prompt
        self.line = line
