"""The stack-based virtual machine that executes compiled CodeObjects.

Execution model: a single operand stack plus a call stack of frames. Each frame
holds its own instruction pointer, a reference to its CodeObject, and a local
environment chained to the enclosing global scope. Functions are first-class
Closure values placed on the operand stack.
"""

from .builtins import NativeFunction
from .errors import VMError
from .opcodes import CodeObject, Op


class Closure:
    def __init__(self, code, globals_env):
        self.code = code
        self.globals = globals_env

    def __repr__(self):
        return "<func {}/{}>".format(self.code.name, self.code.arity)


class Frame:
    __slots__ = ("code", "ip", "locals", "base")

    def __init__(self, code, locals_env, base):
        self.code = code
        self.ip = 0
        self.locals = locals_env
        self.base = base


class VM:
    def __init__(self, output=None):
        self.stack = []
        self.frames = []
        self.globals = {}
        self.output = output if output is not None else []

    # -- stack helpers ---------------------------------------------------
    def _push(self, value):
        self.stack.append(value)

    def _pop(self):
        if not self.stack:
            raise VMError("operand stack underflow")
        return self.stack.pop()

    def _peek(self):
        if not self.stack:
            raise VMError("operand stack empty")
        return self.stack[-1]

    # -- truthiness ------------------------------------------------------
    @staticmethod
    def _truthy(value):
        if value is None or value is False:
            return False
        if value == 0:
            return False
        if value == "":
            return False
        return True

    # -- entry -----------------------------------------------------------
    def run(self, code):
        from .builtins import install
        install(self.globals)
        frame = Frame(code, {}, 0)
        self.frames.append(frame)
        result = self._dispatch_loop()
        return result

    def _current(self):
        return self.frames[-1]

    def _resolve(self, frame, name):
        if name in frame.locals:
            return frame.locals[name]
        if name in self.globals:
            return self.globals[name]
        raise VMError("undefined name {!r}".format(name))

    def _dispatch_loop(self):
        while self.frames:
            frame = self._current()
            if frame.ip >= len(frame.code.code):
                self.frames.pop()
                continue
            instr = frame.code.code[frame.ip]
            frame.ip += 1
            handler = self._handlers.get(instr.op)
            if handler is None:
                raise VMError("unknown opcode {}".format(instr.op))
            stop = handler(self, frame, instr.operand)
            if stop is not None:
                return stop
        return None

    # -- individual opcode handlers --------------------------------------
    def _op_push(self, frame, operand):
        self._push(frame.code.constants[operand])

    def _op_pop(self, frame, operand):
        self._pop()

    def _op_dup(self, frame, operand):
        self._push(self._peek())

    def _op_add(self, frame, operand):
        b = self._pop(); a = self._pop()
        if isinstance(a, str) or isinstance(b, str):
            self._push("{}{}".format(a, b))
        else:
            self._push(a + b)

    def _op_sub(self, frame, operand):
        b = self._pop(); a = self._pop(); self._push(a - b)

    def _op_mul(self, frame, operand):
        b = self._pop(); a = self._pop(); self._push(a * b)

    def _op_div(self, frame, operand):
        b = self._pop(); a = self._pop()
        if b == 0:
            raise VMError("division by zero")
        self._push(a / b)

    def _op_mod(self, frame, operand):
        b = self._pop(); a = self._pop()
        if b == 0:
            raise VMError("modulo by zero")
        self._push(a % b)

    def _op_neg(self, frame, operand):
        self._push(-self._pop())

    def _op_eq(self, frame, operand):
        b = self._pop(); a = self._pop(); self._push(a == b)

    def _op_ne(self, frame, operand):
        b = self._pop(); a = self._pop(); self._push(a != b)

    def _op_lt(self, frame, operand):
        b = self._pop(); a = self._pop(); self._push(a < b)

    def _op_le(self, frame, operand):
        b = self._pop(); a = self._pop(); self._push(a <= b)

    def _op_gt(self, frame, operand):
        b = self._pop(); a = self._pop(); self._push(a > b)

    def _op_ge(self, frame, operand):
        b = self._pop(); a = self._pop(); self._push(a >= b)

    def _op_not(self, frame, operand):
        self._push(not self._truthy(self._pop()))

    def _op_load(self, frame, operand):
        name = frame.code.names[operand]
        self._push(self._resolve(frame, name))

    def _op_store(self, frame, operand):
        name = frame.code.names[operand]
        value = self._peek()
        if name in frame.locals:
            frame.locals[name] = value
        else:
            self.globals[name] = value

    def _op_define(self, frame, operand):
        name = frame.code.names[operand]
        value = self._pop()
        if len(self.frames) == 1:
            self.globals[name] = value
        else:
            frame.locals[name] = value

    def _op_jump(self, frame, operand):
        frame.ip = operand

    def _op_jump_if_false(self, frame, operand):
        if not self._truthy(self._pop()):
            frame.ip = operand

    def _op_make_func(self, frame, operand):
        code = frame.code.constants[operand]
        if not isinstance(code, CodeObject):
            raise VMError("MAKE_FUNC operand is not a code object")
        self._push(Closure(code, self.globals))

    def _op_call(self, frame, operand):
        argc = operand
        args = [self._pop() for _ in range(argc)][::-1]
        callee = self._pop()
        if isinstance(callee, NativeFunction):
            if callee.arity != argc:
                raise VMError(
                    "arity mismatch: native {} expects {} args, got {}".format(
                        callee.name, callee.arity, argc
                    )
                )
            self._push(callee(args))
            return None
        if not isinstance(callee, Closure):
            raise VMError("attempt to call non-function {!r}".format(callee))
        if callee.code.arity != argc:
            raise VMError(
                "arity mismatch: {} expects {} args, got {}".format(
                    callee.code.name, callee.code.arity, argc
                )
            )
        locals_env = {}
        for name, value in zip(callee.code.names[:argc], args):
            locals_env[name] = value
        self.frames.append(Frame(callee.code, locals_env, len(self.stack)))

    def _op_ret(self, frame, operand):
        value = self._pop()
        self.frames.pop()
        del self.stack[frame.base:]
        self._push(value)

    def _op_print(self, frame, operand):
        value = self._pop()
        self.output.append(self._format(value))

    def _op_halt(self, frame, operand):
        return ("halt", None)

    @staticmethod
    def _format(value):
        if value is None:
            return "nil"
        if value is True:
            return "true"
        if value is False:
            return "false"
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)


VM._handlers = {
    Op.PUSH: VM._op_push,
    Op.POP: VM._op_pop,
    Op.DUP: VM._op_dup,
    Op.ADD: VM._op_add,
    Op.SUB: VM._op_sub,
    Op.MUL: VM._op_mul,
    Op.DIV: VM._op_div,
    Op.MOD: VM._op_mod,
    Op.NEG: VM._op_neg,
    Op.EQ: VM._op_eq,
    Op.NE: VM._op_ne,
    Op.LT: VM._op_lt,
    Op.LE: VM._op_le,
    Op.GT: VM._op_gt,
    Op.GE: VM._op_ge,
    Op.NOT: VM._op_not,
    Op.LOAD: VM._op_load,
    Op.STORE: VM._op_store,
    Op.DEFINE: VM._op_define,
    Op.JUMP: VM._op_jump,
    Op.JUMP_IF_FALSE: VM._op_jump_if_false,
    Op.MAKE_FUNC: VM._op_make_func,
    Op.CALL: VM._op_call,
    Op.RET: VM._op_ret,
    Op.PRINT: VM._op_print,
    Op.HALT: VM._op_halt,
}
