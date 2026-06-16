"""Recursive-descent parser with Pratt-style expression precedence.

Grammar (informal):

    program    := statement*
    statement  := letStmt | ifStmt | whileStmt | funcDef | returnStmt
                | printStmt | block | exprStmt
    letStmt    := 'let' IDENT '=' expression ';'
    exprStmt   := expression ';'
    expression := assignment
    assignment := IDENT '=' assignment | logic_or
    logic_or   := logic_and ('or' logic_and)*
    logic_and  := equality ('and' equality)*
    equality   := comparison (('==' | '!=') comparison)*
    comparison := term (('<' | '<=' | '>' | '>=') term)*
    term       := factor (('+' | '-') factor)*
    factor     := unary (('*' | '/' | '%') unary)*
    unary      := ('-' | 'not') unary | call
    call       := primary ('(' arguments? ')')*
    primary    := NUMBER | STRING | 'true' | 'false' | 'nil'
                | IDENT | '(' expression ')'
"""

from . import ast_nodes as ast
from .errors import ParseError
from .tokens import TokenType


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # -- token helpers ---------------------------------------------------
    def _peek(self):
        return self.tokens[self.pos]

    def _previous(self):
        return self.tokens[self.pos - 1]

    def _at_end(self):
        return self._peek().type == TokenType.EOF

    def _check(self, type_):
        return not self._at_end() and self._peek().type == type_

    def _advance(self):
        if not self._at_end():
            self.pos += 1
        return self._previous()

    def _match(self, *types):
        for type_ in types:
            if self._check(type_):
                self._advance()
                return True
        return False

    def _consume(self, type_, message):
        if self._check(type_):
            return self._advance()
        tok = self._peek()
        raise ParseError(message, tok.line, tok.column)

    # -- entry -----------------------------------------------------------
    def parse(self):
        statements = []
        while not self._at_end():
            statements.append(self._statement())
        return ast.Program(statements)

    # -- statements ------------------------------------------------------
    def _statement(self):
        if self._match(TokenType.LET):
            return self._let_statement()
        if self._match(TokenType.IF):
            return self._if_statement()
        if self._match(TokenType.WHILE):
            return self._while_statement()
        if self._match(TokenType.FUNC):
            return self._func_def()
        if self._match(TokenType.RETURN):
            return self._return_statement()
        if self._match(TokenType.PRINT):
            return self._print_statement()
        if self._match(TokenType.LBRACE):
            return self._block()
        return self._expression_statement()

    def _let_statement(self):
        name = self._consume(TokenType.IDENT, "expected variable name after 'let'")
        self._consume(TokenType.ASSIGN, "expected '=' in let binding")
        value = self._expression()
        self._consume(TokenType.SEMI, "expected ';' after let binding")
        return ast.Let(name.value, value)

    def _if_statement(self):
        self._consume(TokenType.LPAREN, "expected '(' after 'if'")
        condition = self._expression()
        self._consume(TokenType.RPAREN, "expected ')' after condition")
        then_branch = self._statement()
        else_branch = None
        if self._match(TokenType.ELSE):
            else_branch = self._statement()
        return ast.If(condition, then_branch, else_branch)

    def _while_statement(self):
        self._consume(TokenType.LPAREN, "expected '(' after 'while'")
        condition = self._expression()
        self._consume(TokenType.RPAREN, "expected ')' after condition")
        body = self._statement()
        return ast.While(condition, body)

    def _func_def(self):
        name = self._consume(TokenType.IDENT, "expected function name")
        self._consume(TokenType.LPAREN, "expected '(' after function name")
        params = []
        if not self._check(TokenType.RPAREN):
            params.append(self._consume(TokenType.IDENT, "expected parameter name").value)
            while self._match(TokenType.COMMA):
                params.append(self._consume(TokenType.IDENT, "expected parameter name").value)
        self._consume(TokenType.RPAREN, "expected ')' after parameters")
        self._consume(TokenType.LBRACE, "expected '{' before function body")
        body = self._block()
        return ast.FuncDef(name.value, params, body)

    def _return_statement(self):
        value = None
        if not self._check(TokenType.SEMI):
            value = self._expression()
        self._consume(TokenType.SEMI, "expected ';' after return value")
        return ast.Return(value)

    def _print_statement(self):
        value = self._expression()
        self._consume(TokenType.SEMI, "expected ';' after print")
        return ast.Print(value)

    def _block(self):
        statements = []
        while not self._check(TokenType.RBRACE) and not self._at_end():
            statements.append(self._statement())
        self._consume(TokenType.RBRACE, "expected '}' to close block")
        return ast.Block(statements)

    def _expression_statement(self):
        expr = self._expression()
        self._consume(TokenType.SEMI, "expected ';' after expression")
        return ast.ExprStmt(expr)

    # -- expressions -----------------------------------------------------
    def _expression(self):
        return self._assignment()

    def _assignment(self):
        expr = self._logic_or()
        if self._match(TokenType.ASSIGN):
            value = self._assignment()
            if isinstance(expr, ast.Identifier):
                return ast.Assign(expr.name, value)
            tok = self._previous()
            raise ParseError("invalid assignment target", tok.line, tok.column)
        return expr

    def _logic_or(self):
        expr = self._logic_and()
        while self._match(TokenType.OR):
            expr = ast.Logical("or", expr, self._logic_and())
        return expr

    def _logic_and(self):
        expr = self._equality()
        while self._match(TokenType.AND):
            expr = ast.Logical("and", expr, self._equality())
        return expr

    def _equality(self):
        expr = self._comparison()
        while self._match(TokenType.EQ, TokenType.NE):
            op = self._previous().value
            expr = ast.Binary(op, expr, self._comparison())
        return expr

    def _comparison(self):
        expr = self._term()
        while self._match(TokenType.LT, TokenType.LE, TokenType.GT, TokenType.GE):
            op = self._previous().value
            expr = ast.Binary(op, expr, self._term())
        return expr

    def _term(self):
        expr = self._factor()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op = self._previous().value
            expr = ast.Binary(op, expr, self._factor())
        return expr

    def _factor(self):
        expr = self._unary()
        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self._previous().value
            expr = ast.Binary(op, expr, self._unary())
        return expr

    def _unary(self):
        if self._match(TokenType.MINUS, TokenType.NOT):
            op = self._previous().value
            return ast.Unary(op, self._unary())
        return self._call()

    def _call(self):
        expr = self._primary()
        while self._match(TokenType.LPAREN):
            expr = self._finish_call(expr)
        return expr

    def _finish_call(self, callee):
        args = []
        if not self._check(TokenType.RPAREN):
            args.append(self._expression())
            while self._match(TokenType.COMMA):
                args.append(self._expression())
        self._consume(TokenType.RPAREN, "expected ')' after arguments")
        return ast.Call(callee, args)

    def _primary(self):
        if self._match(TokenType.NUMBER):
            return ast.NumberLit(self._previous().value)
        if self._match(TokenType.STRING):
            return ast.StringLit(self._previous().value)
        if self._match(TokenType.TRUE):
            return ast.BoolLit(True)
        if self._match(TokenType.FALSE):
            return ast.BoolLit(False)
        if self._match(TokenType.NIL):
            return ast.NilLit()
        if self._match(TokenType.IDENT):
            return ast.Identifier(self._previous().value)
        if self._match(TokenType.LPAREN):
            expr = self._expression()
            self._consume(TokenType.RPAREN, "expected ')' after expression")
            return expr
        tok = self._peek()
        raise ParseError("unexpected token {!r}".format(tok.value), tok.line, tok.column)


def parse(tokens):
    return Parser(tokens).parse()
