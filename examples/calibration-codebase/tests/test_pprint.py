"""Tests for the AST pretty-printer."""

import unittest

from stacklang.lexer import tokenize
from stacklang.parser import parse
from stacklang.pprint import pretty


def render(source):
    return pretty(parse(tokenize(source)))


class PrettyPrintTests(unittest.TestCase):
    def test_program_root(self):
        self.assertTrue(render("print 1;").startswith("(program"))

    def test_binary(self):
        text = render("print 1 + 2;")
        self.assertIn("(binary +", text)
        self.assertIn("(number 1)", text)

    def test_let(self):
        self.assertIn("(let x", render("let x = 1;"))

    def test_if_else(self):
        text = render("if (1) print 1; else print 2;")
        self.assertIn("(if", text)

    def test_while(self):
        self.assertIn("(while", render("while (1 < 2) print 1;"))

    def test_function(self):
        text = render("func f(a, b) { return a + b; }")
        self.assertIn("(func f [a b]", text)

    def test_call(self):
        self.assertIn("(call", render("f(1, 2);"))

    def test_logical(self):
        self.assertIn("(logical and", render("print 1 and 2;"))


if __name__ == "__main__":
    unittest.main()
