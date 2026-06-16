"""Lower the AST into a flat CodeObject of stack-machine instructions.

The compiler is a straightforward tree walk. Control flow is implemented with
forward jumps that are back-patched once the target offset is known, the
standard single-pass technique for a stack VM.
"""

from . import ast_nodes as ast
from .errors import CompileError
from .opcodes import CodeObject, Op

_BINARY_OPS = {
    "+": Op.ADD,
    "-": Op.SUB,
    "*": Op.MUL,
    "/": Op.DIV,
    "%": Op.MOD,
    "==": Op.EQ,
    "!=": Op.NE,
    "<": Op.LT,
    "<=": Op.LE,
    ">": Op.GT,
    ">=": Op.GE,
}


class Compiler:
    def __init__(self, name="<main>", arity=0):
        self.chunk = CodeObject(name, arity)

    def compile_program(self, program):
        for stmt in program.statements:
            self._statement(stmt)
        self.chunk.emit(Op.HALT)
        return self.chunk

    # -- statements ------------------------------------------------------
    def _statement(self, node):
        method = "_stmt_" + type(node).__name__
        handler = getattr(self, method, None)
        if handler is None:
            raise CompileError("cannot compile statement {}".format(type(node).__name__))
        handler(node)

    def _stmt_Let(self, node):
        self._expression(node.value)
        idx = self.chunk.add_name(node.name)
        self.chunk.emit(Op.DEFINE, idx)

    def _stmt_ExprStmt(self, node):
        self._expression(node.expr)
        self.chunk.emit(Op.POP)

    def _stmt_Print(self, node):
        self._expression(node.expr)
        self.chunk.emit(Op.PRINT)

    def _stmt_Block(self, node):
        for stmt in node.statements:
            self._statement(stmt)

    def _stmt_If(self, node):
        self._expression(node.condition)
        jump_false = self.chunk.emit(Op.JUMP_IF_FALSE, None)
        self._statement(node.then_branch)
        if node.else_branch is not None:
            jump_end = self.chunk.emit(Op.JUMP, None)
            self.chunk.patch(jump_false, len(self.chunk.code))
            self._statement(node.else_branch)
            self.chunk.patch(jump_end, len(self.chunk.code))
        else:
            self.chunk.patch(jump_false, len(self.chunk.code))

    def _stmt_While(self, node):
        loop_start = len(self.chunk.code)
        self._expression(node.condition)
        exit_jump = self.chunk.emit(Op.JUMP_IF_FALSE, None)
        self._statement(node.body)
        self.chunk.emit(Op.JUMP, loop_start)
        self.chunk.patch(exit_jump, len(self.chunk.code))

    def _stmt_FuncDef(self, node):
        sub = Compiler(node.name, len(node.params))
        for param in node.params:
            sub.chunk.add_name(param)
        for stmt in node.body.statements:
            sub._statement(stmt)
        sub.chunk.emit(Op.PUSH, sub.chunk.add_const(None))
        sub.chunk.emit(Op.RET)
        const_idx = self.chunk.add_const(sub.chunk)
        self.chunk.emit(Op.MAKE_FUNC, const_idx)
        name_idx = self.chunk.add_name(node.name)
        self.chunk.emit(Op.DEFINE, name_idx)

    def _stmt_Return(self, node):
        if node.value is not None:
            self._expression(node.value)
        else:
            self.chunk.emit(Op.PUSH, self.chunk.add_const(None))
        self.chunk.emit(Op.RET)

    # -- expressions -----------------------------------------------------
    def _expression(self, node):
        method = "_expr_" + type(node).__name__
        handler = getattr(self, method, None)
        if handler is None:
            raise CompileError("cannot compile expression {}".format(type(node).__name__))
        handler(node)

    def _expr_NumberLit(self, node):
        self.chunk.emit(Op.PUSH, self.chunk.add_const(node.value))

    def _expr_StringLit(self, node):
        self.chunk.emit(Op.PUSH, self.chunk.add_const(node.value))

    def _expr_BoolLit(self, node):
        self.chunk.emit(Op.PUSH, self.chunk.add_const(node.value))

    def _expr_NilLit(self, node):
        self.chunk.emit(Op.PUSH, self.chunk.add_const(None))

    def _expr_Identifier(self, node):
        idx = self.chunk.add_name(node.name)
        self.chunk.emit(Op.LOAD, idx)

    def _expr_Assign(self, node):
        self._expression(node.value)
        idx = self.chunk.add_name(node.name)
        self.chunk.emit(Op.STORE, idx)

    def _expr_Unary(self, node):
        self._expression(node.operand)
        if node.op == "-":
            self.chunk.emit(Op.NEG)
        elif node.op == "not":
            self.chunk.emit(Op.NOT)
        else:
            raise CompileError("unknown unary operator {}".format(node.op))

    def _expr_Binary(self, node):
        self._expression(node.left)
        self._expression(node.right)
        op = _BINARY_OPS.get(node.op)
        if op is None:
            raise CompileError("unknown binary operator {}".format(node.op))
        self.chunk.emit(op)

    def _expr_Logical(self, node):
        # short-circuit evaluation via conditional jumps
        self._expression(node.left)
        if node.op == "and":
            self.chunk.emit(Op.DUP)
            jump = self.chunk.emit(Op.JUMP_IF_FALSE, None)
            self.chunk.emit(Op.POP)
            self._expression(node.right)
            self.chunk.patch(jump, len(self.chunk.code))
        else:  # or
            self.chunk.emit(Op.DUP)
            self.chunk.emit(Op.NOT)
            jump = self.chunk.emit(Op.JUMP_IF_FALSE, None)
            self.chunk.emit(Op.POP)
            self._expression(node.right)
            self.chunk.patch(jump, len(self.chunk.code))

    def _expr_Call(self, node):
        self._expression(node.callee)
        for arg in node.args:
            self._expression(arg)
        self.chunk.emit(Op.CALL, len(node.args))


def compile_program(program):
    return Compiler().compile_program(program)
