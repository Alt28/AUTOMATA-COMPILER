

class ReturnValue(Exception):

    def __init__(self, value):
        self.value = value


class _CancelledError(Exception):
    pass


class InterpreterError(Exception):

    def __init__(self, message, line):
        super().__init__(message)
        if line is not None:
            self.message = f"Ln {line} {message}"
        else:
            self.message = message

    def __str__(self):
        return self.message


class InterpreterInputRequest(Exception):

    def __init__(self, prompt, line):
        self.prompt = prompt
        self.line = line
