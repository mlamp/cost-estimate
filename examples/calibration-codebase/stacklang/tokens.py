"""Token definitions for the stacklang lexer."""

from enum import Enum


class TokenType(Enum):
    # literals
    NUMBER = "NUMBER"
    STRING = "STRING"
    IDENT = "IDENT"
    # keywords
    LET = "let"
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    FUNC = "func"
    RETURN = "return"
    PRINT = "print"
    TRUE = "true"
    FALSE = "false"
    NIL = "nil"
    # operators
    PLUS = "+"
    MINUS = "-"
    STAR = "*"
    SLASH = "/"
    PERCENT = "%"
    ASSIGN = "="
    EQ = "=="
    NE = "!="
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="
    AND = "and"
    OR = "or"
    NOT = "not"
    # punctuation
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    COMMA = ","
    SEMI = ";"
    EOF = "EOF"


KEYWORDS = {
    "let": TokenType.LET,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "func": TokenType.FUNC,
    "return": TokenType.RETURN,
    "print": TokenType.PRINT,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "nil": TokenType.NIL,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
}


class Token:
    __slots__ = ("type", "value", "line", "column")

    def __init__(self, type_, value, line, column):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return "Token({}, {!r}, {}:{})".format(
            self.type.name, self.value, self.line, self.column
        )

    def is_keyword(self):
        return self.type in KEYWORDS.values()
