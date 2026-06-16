"""Hand-written lexer that turns source text into a token stream.

The lexer is a simple single-pass state machine over the raw characters. It
tracks line and column positions so that downstream errors can point at the
offending location in the original source.
"""

from .errors import LexError
from .tokens import KEYWORDS, Token, TokenType

_SINGLE = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
    "%": TokenType.PERCENT,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,
    ",": TokenType.COMMA,
    ";": TokenType.SEMI,
}


class Lexer:
    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    def _peek(self, offset=0):
        idx = self.pos + offset
        if idx < len(self.source):
            return self.source[idx]
        return ""

    def _advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def _add(self, type_, value):
        self.tokens.append(Token(type_, value, self.line, self.column))

    def tokenize(self):
        while self.pos < len(self.source):
            ch = self._peek()
            if ch in " \t\r\n":
                self._advance()
                continue
            if ch == "#":
                self._skip_comment()
                continue
            if ch.isdigit() or (ch == "." and self._peek(1).isdigit()):
                self._number()
                continue
            if ch.isalpha() or ch == "_":
                self._identifier()
                continue
            if ch == '"':
                self._string()
                continue
            if self._operator():
                continue
            raise LexError("unexpected character {!r}".format(ch), self.line, self.column)
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens

    def _skip_comment(self):
        while self.pos < len(self.source) and self._peek() != "\n":
            self._advance()

    def _number(self):
        start = self.pos
        seen_dot = False
        while self.pos < len(self.source):
            ch = self._peek()
            if ch.isdigit():
                self._advance()
            elif ch == "." and not seen_dot:
                seen_dot = True
                self._advance()
            else:
                break
        text = self.source[start:self.pos]
        value = float(text) if seen_dot else int(text)
        self._add(TokenType.NUMBER, value)

    def _identifier(self):
        start = self.pos
        while self.pos < len(self.source):
            ch = self._peek()
            if ch.isalnum() or ch == "_":
                self._advance()
            else:
                break
        text = self.source[start:self.pos]
        type_ = KEYWORDS.get(text, TokenType.IDENT)
        self._add(type_, text)

    def _string(self):
        self._advance()  # opening quote
        chars = []
        while self.pos < len(self.source) and self._peek() != '"':
            ch = self._advance()
            if ch == "\\":
                nxt = self._advance()
                chars.append(self._escape(nxt))
            else:
                chars.append(ch)
        if self.pos >= len(self.source):
            raise LexError("unterminated string", self.line, self.column)
        self._advance()  # closing quote
        self._add(TokenType.STRING, "".join(chars))

    def _escape(self, ch):
        table = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\"}
        if ch not in table:
            raise LexError("invalid escape \\{}".format(ch), self.line, self.column)
        return table[ch]

    def _operator(self):
        two = self.source[self.pos:self.pos + 2]
        mapping_two = {
            "==": TokenType.EQ,
            "!=": TokenType.NE,
            "<=": TokenType.LE,
            ">=": TokenType.GE,
        }
        if two in mapping_two:
            self._advance()
            self._advance()
            self._add(mapping_two[two], two)
            return True
        ch = self._peek()
        if ch == "=":
            self._advance()
            self._add(TokenType.ASSIGN, "=")
            return True
        if ch == "<":
            self._advance()
            self._add(TokenType.LT, "<")
            return True
        if ch == ">":
            self._advance()
            self._add(TokenType.GT, ">")
            return True
        if ch in _SINGLE:
            self._advance()
            self._add(_SINGLE[ch], ch)
            return True
        return False


def tokenize(source):
    """Convenience wrapper returning the full token list."""
    return Lexer(source).tokenize()
