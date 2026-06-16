"""End-to-end tests: source through to VM output."""

import unittest

from stacklang import run_source
from stacklang.assembler import assemble
from stacklang.errors import VMError
from stacklang.vm import VM


def out(source):
    return run_source(source)


class VMTests(unittest.TestCase):
    def test_arithmetic(self):
        self.assertEqual(out("print 1 + 2 * 3;"), ["7"])

    def test_division_float(self):
        self.assertEqual(out("print 7 / 2;"), ["3.5"])

    def test_variables(self):
        self.assertEqual(out("let x = 10; x = x + 5; print x;"), ["15"])

    def test_string_concat(self):
        self.assertEqual(out('print "a" + "b";'), ["ab"])

    def test_if_else(self):
        self.assertEqual(out("if (1 < 2) print 1; else print 0;"), ["1"])

    def test_while_loop(self):
        src = "let i = 0; let s = 0; while (i < 5) { s = s + i; i = i + 1; } print s;"
        self.assertEqual(out(src), ["10"])

    def test_function_call(self):
        src = "func sq(n) { return n * n; } print sq(6);"
        self.assertEqual(out(src), ["36"])

    def test_recursion(self):
        src = (
            "func fact(n) { if (n <= 1) { return 1; } return n * fact(n - 1); }"
            " print fact(5);"
        )
        self.assertEqual(out(src), ["120"])

    def test_short_circuit_and(self):
        self.assertEqual(out("print false and (1 / 0);"), ["false"])

    def test_division_by_zero(self):
        with self.assertRaises(VMError):
            out("print 1 / 0;")

    def test_assembler_roundtrip(self):
        text = ".const 0 21\n.const 1 2\nPUSH 0\nPUSH 1\nMUL\nPRINT\nHALT\n"
        code = assemble(text)
        vm = VM()
        vm.run(code)
        self.assertEqual(vm.output, ["42"])


if __name__ == "__main__":
    unittest.main()
