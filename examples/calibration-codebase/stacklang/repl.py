"""Interactive read-eval-print loop for stacklang."""

import sys

from .compiler import compile_program
from .errors import StackLangError
from .lexer import tokenize
from .parser import parse
from .vm import VM


BANNER = "stacklang REPL - type :help for commands, :quit to exit"


class Repl:
    def __init__(self, stream_in=None, stream_out=None):
        self.stdin = stream_in or sys.stdin
        self.stdout = stream_out or sys.stdout
        self.vm = VM()

    def _write(self, text):
        self.stdout.write(text)
        self.stdout.write("\n")

    def run(self):
        self._write(BANNER)
        while True:
            self.stdout.write(">>> ")
            self.stdout.flush()
            line = self.stdin.readline()
            if not line:
                break
            line = line.rstrip("\n")
            if not line.strip():
                continue
            if line.startswith(":"):
                if self._command(line):
                    break
                continue
            self._evaluate(line)

    def _command(self, line):
        cmd = line[1:].strip()
        if cmd in ("quit", "q", "exit"):
            return True
        if cmd in ("help", "h"):
            self._write("commands: :help :quit :reset")
        elif cmd == "reset":
            self.vm = VM()
            self._write("environment reset")
        else:
            self._write("unknown command {!r}".format(cmd))
        return False

    def _evaluate(self, line):
        if not line.rstrip().endswith(";"):
            line = line + ";"
        try:
            tokens = tokenize(line)
            program = parse(tokens)
            code = compile_program(program)
            before = len(self.vm.output)
            self.vm.run(code)
            for produced in self.vm.output[before:]:
                self._write(produced)
        except StackLangError as exc:
            self._write("error: {}".format(exc.formatted()))


def main():
    Repl().run()
    return 0
