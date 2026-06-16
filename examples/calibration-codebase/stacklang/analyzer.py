"""A lightweight static analyzer that runs before compilation.

It walks the AST and reports problems that the compiler would otherwise turn
into runtime errors: use of undefined variables, calls to unknown functions,
and obvious arity mismatches on directly-named calls. The analysis uses a
chain of lexical scopes; it is intentionally conservative and never rejects a
program that would actually run, only flags likely mistakes.
"""

from . import ast_nodes as ast
from . import builtins as natives


class Diagnostic:
    def __init__(self, severity, message, name=None):
        self.severity = severity
        self.message = message
        self.name = name

    def __repr__(self):
        return "{}: {}".format(self.severity.upper(), self.message)


class Scope:
    def __init__(self, parent=None):
        self.parent = parent
        self.vars = set()
        self.funcs = {}

    def declare_var(self, name):
        self.vars.add(name)

    def declare_func(self, name, arity):
        self.funcs[name] = arity

    def resolve_var(self, name):
        scope = self
        while scope is not None:
            if name in scope.vars or name in scope.funcs:
                return True
            scope = scope.parent
        return False

    def resolve_func(self, name):
        scope = self
        while scope is not None:
            if name in scope.funcs:
                return scope.funcs[name]
            scope = scope.parent
        return None


class Analyzer:
    def __init__(self):
        self.diagnostics = []
        self.global_scope = Scope()
        for name in natives.names():
            self.global_scope.declare_func(name, _native_arity(name))

    def analyze(self, program):
        for stmt in program.statements:
            self._statement(stmt, self.global_scope)
        return self.diagnostics

    def _error(self, message, name=None):
        self.diagnostics.append(Diagnostic("error", message, name))

    def _warn(self, message, name=None):
        self.diagnostics.append(Diagnostic("warning", message, name))

    # -- statements ------------------------------------------------------
    def _statement(self, node, scope):
        kind = type(node).__name__
        method = getattr(self, "_stmt_" + kind, None)
        if method is not None:
            method(node, scope)

    def _stmt_Let(self, node, scope):
        self._expression(node.value, scope)
        scope.declare_var(node.name)

    def _stmt_ExprStmt(self, node, scope):
        self._expression(node.expr, scope)

    def _stmt_Print(self, node, scope):
        self._expression(node.expr, scope)

    def _stmt_Block(self, node, scope):
        inner = Scope(scope)
        for stmt in node.statements:
            self._statement(stmt, inner)

    def _stmt_If(self, node, scope):
        self._expression(node.condition, scope)
        self._statement(node.then_branch, scope)
        if node.else_branch is not None:
            self._statement(node.else_branch, scope)

    def _stmt_While(self, node, scope):
        self._expression(node.condition, scope)
        self._statement(node.body, scope)

    def _stmt_FuncDef(self, node, scope):
        scope.declare_func(node.name, len(node.params))
        inner = Scope(scope)
        for param in node.params:
            inner.declare_var(param)
        for stmt in node.body.statements:
            self._statement(stmt, inner)

    def _stmt_Return(self, node, scope):
        if node.value is not None:
            self._expression(node.value, scope)

    # -- expressions -----------------------------------------------------
    def _expression(self, node, scope):
        kind = type(node).__name__
        method = getattr(self, "_expr_" + kind, None)
        if method is not None:
            method(node, scope)

    def _expr_Identifier(self, node, scope):
        if not scope.resolve_var(node.name) and scope.resolve_func(node.name) is None:
            self._error("use of undefined name {!r}".format(node.name), node.name)

    def _expr_Assign(self, node, scope):
        self._expression(node.value, scope)
        if not scope.resolve_var(node.name):
            self._warn("assignment to undeclared name {!r}".format(node.name), node.name)
            scope.declare_var(node.name)

    def _expr_Unary(self, node, scope):
        self._expression(node.operand, scope)

    def _expr_Binary(self, node, scope):
        self._expression(node.left, scope)
        self._expression(node.right, scope)

    def _expr_Logical(self, node, scope):
        self._expression(node.left, scope)
        self._expression(node.right, scope)

    def _expr_Call(self, node, scope):
        self._expression(node.callee, scope)
        for arg in node.args:
            self._expression(arg, scope)
        if isinstance(node.callee, ast.Identifier):
            arity = scope.resolve_func(node.callee.name)
            if arity is not None and arity != len(node.args):
                self._error(
                    "function {!r} expects {} args, got {}".format(
                        node.callee.name, arity, len(node.args)
                    ),
                    node.callee.name,
                )


def _native_arity(name):
    table = {
        "abs": 1, "max": 2, "min": 2, "sqrt": 1, "pow": 2, "floor": 1,
        "ceil": 1, "len": 1, "upper": 1, "lower": 1, "str": 1, "num": 1,
    }
    return table.get(name, 1)


def analyze(program):
    return Analyzer().analyze(program)


def has_errors(diagnostics):
    return any(d.severity == "error" for d in diagnostics)
