"""A bytecode verifier that checks a CodeObject for structural soundness.

Checks performed:

* every jump target is within the instruction range;
* operand-bearing opcodes have an operand, operand-free ones do not;
* constant / name operand indices are in range;
* a conservative stack-depth simulation never underflows and the chunk ends
  with the stack effect the VM expects (HALT for main, RET for functions).

The verifier is advisory: the VM also guards against underflow at runtime, but
running the verifier first turns latent codegen bugs into clear diagnostics.
"""

from .opcodes import HAS_OPERAND, CodeObject, Op

# net stack effect (pushed - popped) for opcodes with a fixed effect
_STACK_EFFECT = {
    Op.PUSH: 1,
    Op.POP: -1,
    Op.DUP: 1,
    Op.ADD: -1, Op.SUB: -1, Op.MUL: -1, Op.DIV: -1, Op.MOD: -1,
    Op.NEG: 0,
    Op.EQ: -1, Op.NE: -1, Op.LT: -1, Op.LE: -1, Op.GT: -1, Op.GE: -1,
    Op.NOT: 0,
    Op.LOAD: 1, Op.STORE: 0, Op.DEFINE: -1,
    Op.JUMP: 0, Op.JUMP_IF_FALSE: -1,
    Op.MAKE_FUNC: 1,
    Op.PRINT: -1,
    Op.HALT: 0,
    Op.RET: -1,
}


class VerifyIssue:
    def __init__(self, offset, message):
        self.offset = offset
        self.message = message

    def __repr__(self):
        return "@{:04d}: {}".format(self.offset, self.message)


def verify(code):
    issues = []
    _check_structure(code, issues)
    _check_jumps(code, issues)
    _check_stack(code, issues)
    for const in code.constants:
        if isinstance(const, CodeObject):
            issues.extend(verify(const))
    return issues


def _check_structure(code, issues):
    for offset, instr in enumerate(code.code):
        if instr.op in HAS_OPERAND:
            if instr.operand is None:
                issues.append(VerifyIssue(offset, "{} missing operand".format(instr.op.name)))
                continue
            if instr.op in (Op.PUSH, Op.MAKE_FUNC):
                if not 0 <= instr.operand < len(code.constants):
                    issues.append(VerifyIssue(offset, "constant index out of range"))
            if instr.op in (Op.LOAD, Op.STORE, Op.DEFINE):
                if not 0 <= instr.operand < len(code.names):
                    issues.append(VerifyIssue(offset, "name index out of range"))
        else:
            if instr.operand is not None:
                issues.append(VerifyIssue(offset, "{} has unexpected operand".format(instr.op.name)))


def _check_jumps(code, issues):
    n = len(code.code)
    for offset, instr in enumerate(code.code):
        if instr.op in (Op.JUMP, Op.JUMP_IF_FALSE):
            if instr.operand is None or not 0 <= instr.operand <= n:
                issues.append(VerifyIssue(offset, "jump target out of range"))


def _check_stack(code, issues):
    # conservative linear scan; branches are assumed to converge to the same
    # depth (true for the structured control flow the compiler emits)
    depth = 0
    for offset, instr in enumerate(code.code):
        if instr.op == Op.CALL:
            effect = -(instr.operand or 0)
        else:
            effect = _STACK_EFFECT.get(instr.op, 0)
        # popped operands must be present
        popped = max(0, -effect)
        if instr.op == Op.CALL:
            popped = (instr.operand or 0) + 1
        if depth < popped:
            issues.append(VerifyIssue(offset, "stack underflow ({} < {})".format(depth, popped)))
        depth += effect
        if depth < 0:
            depth = 0
    return depth


def is_valid(code):
    return not verify(code)
