"""Native built-in functions callable from stacklang programs.

A NativeFunction wraps a Python callable with a fixed arity so the VM can call
it through the same CALL opcode used for user-defined closures. The registry is
installed into the VM's global environment before execution.
"""

import math

from .errors import VMError


class NativeFunction:
    __slots__ = ("name", "arity", "fn")

    def __init__(self, name, arity, fn):
        self.name = name
        self.arity = arity
        self.fn = fn

    def __call__(self, args):
        return self.fn(*args)

    def __repr__(self):
        return "<native {}/{}>".format(self.name, self.arity)


def _checked(name, fn):
    def wrapper(*args):
        try:
            return fn(*args)
        except (ValueError, TypeError, ZeroDivisionError) as exc:
            raise VMError("native {} failed: {}".format(name, exc))
    return wrapper


def _abs(x):
    return abs(x)


def _max(a, b):
    return a if a >= b else b


def _min(a, b):
    return a if a <= b else b


def _sqrt(x):
    if x < 0:
        raise VMError("sqrt of negative number")
    return math.sqrt(x)


def _pow(base, exp):
    return math.pow(base, exp)


def _floor(x):
    return math.floor(x)


def _ceil(x):
    return math.ceil(x)


def _len(s):
    return len(s)


def _upper(s):
    return str(s).upper()


def _lower(s):
    return str(s).lower()


def _to_str(x):
    return str(x)


def _to_num(s):
    text = str(s)
    return float(text) if "." in text else int(text)


_REGISTRY = {
    "abs": NativeFunction("abs", 1, _checked("abs", _abs)),
    "max": NativeFunction("max", 2, _checked("max", _max)),
    "min": NativeFunction("min", 2, _checked("min", _min)),
    "sqrt": NativeFunction("sqrt", 1, _checked("sqrt", _sqrt)),
    "pow": NativeFunction("pow", 2, _checked("pow", _pow)),
    "floor": NativeFunction("floor", 1, _checked("floor", _floor)),
    "ceil": NativeFunction("ceil", 1, _checked("ceil", _ceil)),
    "len": NativeFunction("len", 1, _checked("len", _len)),
    "upper": NativeFunction("upper", 1, _checked("upper", _upper)),
    "lower": NativeFunction("lower", 1, _checked("lower", _lower)),
    "str": NativeFunction("str", 1, _checked("str", _to_str)),
    "num": NativeFunction("num", 1, _checked("num", _to_num)),
}


def install(globals_env):
    """Copy the native registry into a VM global environment."""
    for name, native in _REGISTRY.items():
        globals_env[name] = native
    return globals_env


def names():
    return sorted(_REGISTRY)
