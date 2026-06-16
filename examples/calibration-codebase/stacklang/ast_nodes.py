"""Abstract syntax tree node definitions.

Nodes are plain data classes; all behaviour lives in the compiler, which walks
this tree and emits bytecode. Keeping the AST behaviour-free makes it easy to
add alternative back ends (an interpreter, a pretty-printer) later.
"""


class Node:
    pass


class Program(Node):
    def __init__(self, statements):
        self.statements = statements


class NumberLit(Node):
    def __init__(self, value):
        self.value = value


class StringLit(Node):
    def __init__(self, value):
        self.value = value


class BoolLit(Node):
    def __init__(self, value):
        self.value = value


class NilLit(Node):
    pass


class Identifier(Node):
    def __init__(self, name):
        self.name = name


class Unary(Node):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand


class Binary(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right


class Logical(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right


class Assign(Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class Let(Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class ExprStmt(Node):
    def __init__(self, expr):
        self.expr = expr


class Print(Node):
    def __init__(self, expr):
        self.expr = expr


class Block(Node):
    def __init__(self, statements):
        self.statements = statements


class If(Node):
    def __init__(self, condition, then_branch, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch


class While(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body


class FuncDef(Node):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body


class Call(Node):
    def __init__(self, callee, args):
        self.callee = callee
        self.args = args


class Return(Node):
    def __init__(self, value):
        self.value = value
