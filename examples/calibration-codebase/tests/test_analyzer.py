"""Tests for the static analyzer and the bytecode verifier."""

import unittest

from stacklang import compile_source
from stacklang.analyzer import analyze, has_errors
from stacklang.lexer import tokenize
from stacklang.parser import parse
from stacklang.verifier import verify


def diags(source):
    return analyze(parse(tokenize(source)))


class AnalyzerTests(unittest.TestCase):
    def test_clean_program(self):
        self.assertFalse(has_errors(diags("let x = 1; print x;")))

    def test_undefined_variable(self):
        d = diags("print y;")
        self.assertTrue(has_errors(d))

    def test_arity_mismatch(self):
        d = diags("func f(a) { return a; } print f(1, 2);")
        self.assertTrue(has_errors(d))

    def test_native_known(self):
        self.assertFalse(has_errors(diags("print sqrt(4);")))

    def test_assignment_to_undeclared_warns(self):
        d = diags("x = 5;")
        self.assertTrue(any(item.severity == "warning" for item in d))

    def test_function_scope(self):
        src = "func f(a) { return a + 1; } print f(2);"
        self.assertFalse(has_errors(diags(src)))


class VerifierTests(unittest.TestCase):
    def test_valid_program(self):
        self.assertEqual(verify(compile_source("print 1 + 2;")), [])

    def test_valid_function(self):
        src = "func sq(n) { return n * n; } print sq(4);"
        self.assertEqual(verify(compile_source(src)), [])

    def test_valid_loop(self):
        src = "let i = 0; while (i < 3) { i = i + 1; } print i;"
        self.assertEqual(verify(compile_source(src)), [])


if __name__ == "__main__":
    unittest.main()
