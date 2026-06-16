"""Textual assembler: parse `.sasm` listings into a CodeObject and back.

This gives the toolchain a stable, inspectable on-disk format and a second
front end (besides the source compiler) that targets the same VM. Format:

    .const 0 42
    .name  0 x
    0000 PUSH 0
    0001 DEFINE 0
    0002 HALT
"""

from .errors import AssembleError
from .opcodes import HAS_OPERAND, NAME_TO_OP, CodeObject, Instruction


def assemble(text):
    code = CodeObject()
    pending = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith(";"):
            continue
        if line.startswith(".const"):
            _directive_const(code, line, lineno)
            continue
        if line.startswith(".name"):
            _directive_name(code, line, lineno)
            continue
        pending.append((lineno, line))
    for lineno, line in pending:
        _instruction(code, line, lineno)
    return code


def _directive_const(code, line, lineno):
    parts = line.split(None, 2)
    if len(parts) < 3:
        raise AssembleError("malformed .const directive", lineno)
    idx = int(parts[1])
    value = _parse_literal(parts[2], lineno)
    _ensure_size(code.constants, idx)
    code.constants[idx] = value


def _directive_name(code, line, lineno):
    parts = line.split(None, 2)
    if len(parts) < 3:
        raise AssembleError("malformed .name directive", lineno)
    idx = int(parts[1])
    _ensure_size(code.names, idx)
    code.names[idx] = parts[2]


def _instruction(code, line, lineno):
    parts = line.split()
    # optional leading offset label like 0000
    if parts and parts[0].isdigit() and len(parts) > 1 and parts[1] in NAME_TO_OP:
        parts = parts[1:]
    mnemonic = parts[0]
    if mnemonic not in NAME_TO_OP:
        raise AssembleError("unknown mnemonic {!r}".format(mnemonic), lineno)
    op = NAME_TO_OP[mnemonic]
    if op in HAS_OPERAND:
        if len(parts) < 2:
            raise AssembleError("{} requires an operand".format(mnemonic), lineno)
        code.code.append(Instruction(op, int(parts[1])))
    else:
        code.code.append(Instruction(op))


def _parse_literal(text, lineno):
    text = text.strip()
    if text == "nil":
        return None
    if text == "true":
        return True
    if text == "false":
        return False
    if text.startswith('"') and text.endswith('"'):
        return text[1:-1]
    try:
        if "." in text:
            return float(text)
        return int(text)
    except ValueError:
        raise AssembleError("bad literal {!r}".format(text), lineno)


def _ensure_size(lst, idx):
    while len(lst) <= idx:
        lst.append(None)
