"""stacklang: a tiny stack-based bytecode language and virtual machine.

Pipeline: source -> Lexer -> Parser -> Compiler -> CodeObject -> VM.
"""

from .compiler import compile_program
from .lexer import tokenize
from .parser import parse
from .vm import VM

__version__ = "0.1.0"


def run_source(source, output=None):
    """Compile and execute source text, returning the VM's output lines."""
    tokens = tokenize(source)
    program = parse(tokens)
    code = compile_program(program)
    vm = VM(output=output)
    vm.run(code)
    return vm.output


def compile_source(source):
    """Compile source text to a CodeObject without executing it."""
    return compile_program(parse(tokenize(source)))
