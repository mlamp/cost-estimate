"""Serialize a compiled CodeObject to a plain dict (JSON-ready) and back.

This lets a program be compiled once and re-loaded without re-parsing. Nested
function CodeObjects are serialized recursively. The format is intentionally
simple and stable so the on-disk representation can be inspected by hand.
"""

import json

from .errors import StackLangError
from .opcodes import CodeObject, Instruction, Op

_FORMAT_VERSION = 1


class SerializeError(StackLangError):
    """Raised when a serialized chunk cannot be decoded."""


def to_dict(code):
    return {
        "version": _FORMAT_VERSION,
        "name": code.name,
        "arity": code.arity,
        "constants": [_encode_const(c) for c in code.constants],
        "names": list(code.names),
        "code": [_encode_instr(i) for i in code.code],
    }


def from_dict(data):
    if not isinstance(data, dict):
        raise SerializeError("expected a serialized object")
    version = data.get("version")
    if version != _FORMAT_VERSION:
        raise SerializeError("unsupported format version {}".format(version))
    code = CodeObject(data.get("name", "<main>"), data.get("arity", 0))
    code.constants = [_decode_const(c) for c in data.get("constants", [])]
    code.names = list(data.get("names", []))
    code.code = [_decode_instr(i) for i in data.get("code", [])]
    return code


def dumps(code, indent=2):
    return json.dumps(to_dict(code), indent=indent)


def loads(text):
    try:
        data = json.loads(text)
    except ValueError as exc:
        raise SerializeError("invalid JSON: {}".format(exc))
    return from_dict(data)


def _encode_const(value):
    if isinstance(value, CodeObject):
        return {"__code__": to_dict(value)}
    if value is None or isinstance(value, (bool, int, float, str)):
        return {"v": value}
    raise SerializeError("cannot serialize constant of type {}".format(type(value).__name__))


def _decode_const(entry):
    if "__code__" in entry:
        return from_dict(entry["__code__"])
    return entry["v"]


def _encode_instr(instr):
    if instr.operand is None:
        return [instr.op.name]
    return [instr.op.name, instr.operand]


def _decode_instr(entry):
    if not entry:
        raise SerializeError("empty instruction entry")
    name = entry[0]
    try:
        op = Op[name]
    except KeyError:
        raise SerializeError("unknown opcode {!r}".format(name))
    operand = entry[1] if len(entry) > 1 else None
    return Instruction(op, operand)
