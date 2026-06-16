"""Tests for the stacklang lexer."""

import unittest

from stacklang.errors import LexError
from stacklang.lexer import tokenize
from stacklang.tokens import TokenType


class LexerTests(unittest.TestCase):
    def types(self, source):
        return [t.type for t in tokenize(source)]

    def test_numbers(self):
        toks = tokenize("12 3.5")
        self.assertEqual(toks[0].value, 12)
        self.assertEqual(toks[1].value, 3.5)

    def test_keywords(self):
        types = self.types("let x = 1;")
        self.assertEqual(types[0], TokenType.LET)
        self.assertEqual(types[1], TokenType.IDENT)
        self.assertEqual(types[-1], TokenType.EOF)

    def test_operators(self):
        types = self.types("1 <= 2 == 3 != 4 >= 5")
        self.assertIn(TokenType.LE, types)
        self.assertIn(TokenType.EQ, types)
        self.assertIn(TokenType.NE, types)
        self.assertIn(TokenType.GE, types)

    def test_string_escapes(self):
        toks = tokenize('"a\\nb"')
        self.assertEqual(toks[0].value, "a\nb")

    def test_comment_skipped(self):
        types = self.types("# comment\nlet x = 1;")
        self.assertEqual(types[0], TokenType.LET)

    def test_unterminated_string(self):
        with self.assertRaises(LexError):
            tokenize('"oops')

    def test_bad_char(self):
        with self.assertRaises(LexError):
            tokenize("@")


if __name__ == "__main__":
    unittest.main()
