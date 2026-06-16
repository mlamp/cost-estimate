"""Bytecode opcode definitions for the stack virtual machine."""

from enum import IntEnum


class Op(IntEnum):
    # stack / constants
    PUSH = 0       # operand: const index
    POP = 1
    DUP = 2
    # arithmetic
    ADD = 10
    SUB = 11
    MUL = 12
    DIV = 13
    MOD = 14
    NEG = 15
    # comparison / logic
    EQ = 20
    NE = 21
    LT = 22
    LE = 23
    GT = 24
    GE = 25
    NOT = 26
    # variables (operand: name index)
    LOAD = 30
    STORE = 31
    DEFINE = 32
    # control flow (operand: absolute instruction index)
    JUMP = 40
    JUMP_IF_FALSE = 41
    # functions
    CALL = 50      # operand: argument count
    RET = 51
    MAKE_FUNC = 52  # operand: const index of a CodeObject
    # io
    PRINT = 60
    HALT = 61


# opcodes that carry a single integer operand
HAS_OPERAND = {
    Op.PUSH,
    Op.LOAD,
    Op.STORE,
    Op.DEFINE,
    Op.JUMP,
    Op.JUMP_IF_FALSE,
    Op.CALL,
    Op.MAKE_FUNC,
}

NAME_TO_OP = {op.name: op for op in Op}


class Instruction:
    __slots__ = ("op", "operand")

    def __init__(self, op, operand=None):
        self.op = op
        self.operand = operand

    def __repr__(self):
        if self.operand is None:
            return self.op.name
        return "{} {}".format(self.op.name, self.operand)


class CodeObject:
    """A compiled chunk: a flat instruction list plus constant/name pools."""

    def __init__(self, name="<main>", arity=0):
        self.name = name
        self.arity = arity
        self.code = []
        self.constants = []
        self.names = []

    def add_const(self, value):
        # de-duplicate identical constants to keep the pool compact
        for idx, existing in enumerate(self.constants):
            if type(existing) is type(value) and existing == value:
                return idx
        self.constants.append(value)
        return len(self.constants) - 1

    def add_name(self, name):
        if name in self.names:
            return self.names.index(name)
        self.names.append(name)
        return len(self.names) - 1

    def emit(self, op, operand=None):
        self.code.append(Instruction(op, operand))
        return len(self.code) - 1

    def patch(self, index, operand):
        self.code[index].operand = operand
