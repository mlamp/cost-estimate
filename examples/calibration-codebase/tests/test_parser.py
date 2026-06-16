"""Tests for the recursive-descent parser."""

import unittest

from stacklang import ast_nodes as ast
from stacklang.errors import ParseError
from stacklang.lexer import tokenize
from stacklang.parser import parse


def tree(source):
    return parse(tokenize(source))


class ParserTests(unittest.TestCase):
    def test_let(self):
        program = tree("let x = 1 + 2;")
        self.assertIsInstance(program.statements[0], ast.Let)
        self.assertIsInstance(program.statements[0].value, ast.Binary)

    def test_precedence(self):
        program = tree("let x = 1 + 2 * 3;")
        binary = program.statements[0].value
        self.assertEqual(binary.op, "+")
        self.assertEqual(binary.right.op, "*")

    def test_if_else(self):
        program = tree("if (x) print 1; else print 2;")
        node = program.statements[0]
        self.assertIsInstance(node, ast.If)
        self.assertIsNotNone(node.else_branch)

    def test_function(self):
        program = tree("func add(a, b) { return a + b; }")
        node = program.statements[0]
        self.assertIsInstance(node, ast.FuncDef)
        self.assertEqual(node.params, ["a", "b"])

    def test_call(self):
        program = tree("add(1, 2);")
        call = program.statements[0].expr
        self.assertIsInstance(call, ast.Call)
        self.assertEqual(len(call.args), 2)

    def test_invalid_assignment(self):
        with self.assertRaises(ParseError):
            tree("1 = 2;")

    def test_missing_semicolon(self):
        with self.assertRaises(ParseError):
            tree("let x = 1")


if __name__ == "__main__":
    unittest.main()
