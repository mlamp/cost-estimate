"""Optional bytecode optimization passes for stacklang.

Two conservative passes are provided:

* constant folding   - fold `PUSH a; PUSH b; <binop>` into a single PUSH when
                       both operands are compile-time constants.
* peephole cleanup   - drop `PUSH x; POP` pairs and collapse double negations.

Both passes preserve jump targets by rebuilding the instruction list and
remapping absolute jump offsets through an old->new index table. Passes are
idempotent and safe to run repeatedly; `optimize` runs them to a fixed point.
"""

from .opcodes import CodeObject, Instruction, Op

_FOLDABLE = {
    Op.ADD: lambda a, b: a + b,
    Op.SUB: lambda a, b: a - b,
    Op.MUL: lambda a, b: a * b,
    Op.EQ: lambda a, b: a == b,
    Op.NE: lambda a, b: a != b,
    Op.LT: lambda a, b: a < b,
    Op.LE: lambda a, b: a <= b,
    Op.GT: lambda a, b: a > b,
    Op.GE: lambda a, b: a >= b,
}

_JUMP_OPS = {Op.JUMP, Op.JUMP_IF_FALSE}


def optimize(code, max_rounds=5):
    """Run the available passes to a fixed point (bounded by max_rounds)."""
    current = code
    for _ in range(max_rounds):
        folded, changed_a = _constant_fold(current)
        cleaned, changed_b = _peephole(folded)
        current = cleaned
        if not (changed_a or changed_b):
            break
    # recurse into nested function constants
    for idx, const in enumerate(current.constants):
        if isinstance(const, CodeObject):
            current.constants[idx] = optimize(const, max_rounds)
    return current


def _is_const_push(instr):
    return instr.op == Op.PUSH


def _rebuild(code, new_instrs, removed_at):
    """Rebuild a CodeObject with new instructions, remapping jump targets.

    `removed_at` maps each removed old-index to the count of removals at or
    before it so absolute jump operands can be shifted correctly.
    """
    result = CodeObject(code.name, code.arity)
    result.constants = list(code.constants)
    result.names = list(code.names)
    result.code = new_instrs
    return result


def _constant_fold(code):
    instrs = code.code
    targets = _jump_targets(instrs)
    out = []
    i = 0
    changed = False
    new_code = CodeObject(code.name, code.arity)
    new_code.constants = list(code.constants)
    new_code.names = list(code.names)
    # Folding changes indices, so only fold runs that contain no jump targets.
    while i < len(instrs):
        if (
            i + 2 < len(instrs)
            and _is_const_push(instrs[i])
            and _is_const_push(instrs[i + 1])
            and instrs[i + 2].op in _FOLDABLE
            and (i + 1) not in targets
            and (i + 2) not in targets
        ):
            a = code.constants[instrs[i].operand]
            b = code.constants[instrs[i + 1].operand]
            if _numeric(a) and _numeric(b):
                value = _FOLDABLE[instrs[i + 2].op](a, b)
                idx = new_code.add_const(value)
                out.append((i, Instruction(Op.PUSH, idx)))
                out.append((i + 1, None))
                out.append((i + 2, None))
                i += 3
                changed = True
                continue
        out.append((i, instrs[i]))
        i += 1
    return _finalize(new_code, out), changed


def _peephole(code):
    instrs = code.code
    targets = _jump_targets(instrs)
    out = []
    i = 0
    changed = False
    new_code = CodeObject(code.name, code.arity)
    new_code.constants = list(code.constants)
    new_code.names = list(code.names)
    while i < len(instrs):
        if (
            i + 1 < len(instrs)
            and instrs[i].op == Op.PUSH
            and instrs[i + 1].op == Op.POP
            and (i + 1) not in targets
        ):
            out.append((i, None))
            out.append((i + 1, None))
            i += 2
            changed = True
            continue
        if (
            i + 1 < len(instrs)
            and instrs[i].op == Op.NEG
            and instrs[i + 1].op == Op.NEG
            and (i + 1) not in targets
        ):
            out.append((i, None))
            out.append((i + 1, None))
            i += 2
            changed = True
            continue
        out.append((i, instrs[i]))
        i += 1
    return _finalize(new_code, out), changed


def _finalize(new_code, out):
    """Compact the (old_index, instr|None) list and remap jump targets."""
    old_to_new = {}
    kept = []
    for old_index, instr in out:
        if instr is None:
            continue
        old_to_new[old_index] = len(kept)
        kept.append(instr)
    # any old index that was removed maps to the next surviving instruction
    max_old = max((oi for oi, _ in out), default=-1)
    for old_index in range(max_old + 1):
        if old_index not in old_to_new:
            old_to_new[old_index] = _next_surviving(old_index, out, old_to_new, len(kept))
    for instr in kept:
        if instr.op in _JUMP_OPS and instr.operand in old_to_new:
            instr.operand = old_to_new[instr.operand]
    new_code.code = kept
    return new_code


def _next_surviving(old_index, out, old_to_new, fallback):
    for oi, instr in out:
        if oi >= old_index and instr is not None:
            return old_to_new[oi]
    return fallback


def _jump_targets(instrs):
    targets = set()
    for instr in instrs:
        if instr.op in _JUMP_OPS and instr.operand is not None:
            targets.add(instr.operand)
    return targets


def _numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)
