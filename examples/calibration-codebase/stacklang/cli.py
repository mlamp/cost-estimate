"""Command-line entry point for the stacklang toolchain."""

import argparse
import sys

from . import __version__, run_source
from .assembler import assemble
from .compiler import compile_program
from .disassembler import disassemble
from .errors import StackLangError
from .lexer import tokenize
from .parser import parse
from .repl import Repl
from .vm import VM


def build_parser():
    parser = argparse.ArgumentParser(prog="stacklang", description="stacklang toolchain")
    parser.add_argument("--version", action="version", version="stacklang " + __version__)
    sub = parser.add_subparsers(dest="command")

    run_p = sub.add_parser("run", help="compile and execute a source file")
    run_p.add_argument("file")

    dis_p = sub.add_parser("dis", help="disassemble a source file")
    dis_p.add_argument("file")

    asm_p = sub.add_parser("asm", help="assemble and run a .sasm file")
    asm_p.add_argument("file")

    chk_p = sub.add_parser("check", help="statically analyze a source file")
    chk_p.add_argument("file")

    pp_p = sub.add_parser("pprint", help="pretty-print the AST of a source file")
    pp_p.add_argument("file")

    sub.add_parser("repl", help="start the interactive REPL")
    return parser


def _read(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def cmd_run(args):
    source = _read(args.file)
    for line in run_source(source):
        print(line)
    return 0


def cmd_dis(args):
    source = _read(args.file)
    code = compile_program(parse(tokenize(source)))
    print(disassemble(code))
    return 0


def cmd_asm(args):
    text = _read(args.file)
    code = assemble(text)
    vm = VM()
    vm.run(code)
    for line in vm.output:
        print(line)
    return 0


def cmd_check(args):
    from .analyzer import analyze, has_errors
    program = parse(tokenize(_read(args.file)))
    diagnostics = analyze(program)
    for diag in diagnostics:
        print("{}: {}".format(diag.severity, diag.message))
    if has_errors(diagnostics):
        return 1
    if not diagnostics:
        print("ok: no issues found")
    return 0


def cmd_pprint(args):
    from .pprint import pretty
    program = parse(tokenize(_read(args.file)))
    print(pretty(program))
    return 0


def cmd_repl(args):
    Repl().run()
    return 0


_DISPATCH = {
    "run": cmd_run,
    "dis": cmd_dis,
    "asm": cmd_asm,
    "check": cmd_check,
    "pprint": cmd_pprint,
    "repl": cmd_repl,
}


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 1
    handler = _DISPATCH[args.command]
    try:
        return handler(args)
    except StackLangError as exc:
        sys.stderr.write("error: {}\n".format(exc.formatted()))
        return 2
    except OSError as exc:
        sys.stderr.write("io error: {}\n".format(exc))
        return 2
