"""Tests for the disassembler output format."""

import unittest

from stacklang import compile_source
from stacklang.disassembler import disassemble


class DisassemblerTests(unittest.TestCase):
    def test_header_present(self):
        text = disassemble(compile_source("print 1;"))
        self.assertIn("== <main>", text)

    def test_push_const_detail(self):
        text = disassemble(compile_source("print 42;"))
        self.assertIn("PUSH", text)
        self.assertIn("42", text)

    def test_jump_detail(self):
        text = disassemble(compile_source("if (1) print 1;"))
        self.assertIn("JUMP_IF_FALSE", text)
        self.assertIn("->", text)

    def test_name_detail(self):
        text = disassemble(compile_source("let x = 1;"))
        self.assertIn("DEFINE", text)
        self.assertIn("x", text)

    def test_nested_function_disassembled(self):
        text = disassemble(compile_source("func f(a) { return a; }"))
        self.assertIn("== f", text)
        self.assertIn("RET", text)

    def test_halt_emitted(self):
        text = disassemble(compile_source("print 1;"))
        self.assertIn("HALT", text)


if __name__ == "__main__":
    unittest.main()
