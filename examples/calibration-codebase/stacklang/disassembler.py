"""Human-readable disassembly of a CodeObject, used by the CLI and tests."""

from .opcodes import HAS_OPERAND, CodeObject, Op


def disassemble(code, indent=0):
    lines = []
    pad = "  " * indent
    lines.append("{}== {} (arity {}) ==".format(pad, code.name, code.arity))
    for offset, instr in enumerate(code.code):
        if instr.op in HAS_OPERAND:
            detail = _operand_detail(code, instr.op, instr.operand)
            lines.append("{}{:04d} {:<14} {:>4}  {}".format(
                pad, offset, instr.op.name, instr.operand, detail))
        else:
            lines.append("{}{:04d} {}".format(pad, offset, instr.op.name))
    # recurse into nested function constants
    for const in code.constants:
        if isinstance(const, CodeObject):
            lines.append("")
            lines.append(disassemble(const, indent + 1))
    return "\n".join(lines)


def _operand_detail(code, op, operand):
    if op in (Op.PUSH, Op.MAKE_FUNC):
        value = code.constants[operand]
        if isinstance(value, CodeObject):
            return "; func {}".format(value.name)
        return "; {!r}".format(value)
    if op in (Op.LOAD, Op.STORE, Op.DEFINE):
        return "; {}".format(code.names[operand])
    if op in (Op.JUMP, Op.JUMP_IF_FALSE):
        return "; -> {:04d}".format(operand)
    if op == Op.CALL:
        return "; {} args".format(operand)
    return ""
