"""Error types shared across the stacklang toolchain."""


class StackLangError(Exception):
    """Base class for all stacklang errors."""

    def __init__(self, message, line=None, column=None):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self.formatted())

    def formatted(self):
        if self.line is not None and self.column is not None:
            return "{} at line {}, column {}".format(self.message, self.line, self.column)
        if self.line is not None:
            return "{} at line {}".format(self.message, self.line)
        return self.message


class LexError(StackLangError):
    """Raised when the source cannot be tokenized."""


class ParseError(StackLangError):
    """Raised when the token stream does not form a valid program."""


class CompileError(StackLangError):
    """Raised when an AST cannot be lowered to bytecode."""


class VMError(StackLangError):
    """Raised when the virtual machine hits an illegal state at runtime."""


class AssembleError(StackLangError):
    """Raised when textual assembly cannot be parsed."""
