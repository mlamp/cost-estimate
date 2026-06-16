"""Tests for the bytecode optimizer passes."""

import unittest

from stacklang import compile_source
from stacklang.opcodes import Op
from stacklang.optimizer import optimize
from stacklang.vm import VM


def ops(code):
    return [i.op for i in code.code]


def run(code):
    vm = VM()
    vm.run(code)
    return vm.output


class OptimizerTests(unittest.TestCase):
    def test_constant_folding(self):
        code = compile_source("print 1 + 2 * 3;")
        before = run(compile_source("print 1 + 2 * 3;"))
        opt = optimize(code)
        # folding must preserve observable behaviour
        self.assertEqual(run(opt), before)
        self.assertEqual(run(opt), ["7"])

    def test_folding_reduces_instructions(self):
        code = compile_source("print 2 + 3;")
        opt = optimize(code)
        self.assertLessEqual(len(opt.code), len(code.code))

    def test_peephole_preserves_loops(self):
        src = "let i = 0; while (i < 3) { i = i + 1; } print i;"
        code = compile_source(src)
        opt = optimize(code)
        self.assertEqual(run(opt), ["3"])

    def test_jump_targets_remapped(self):
        src = "if (1 < 2) { print 1; } else { print 2; }"
        opt = optimize(compile_source(src))
        self.assertEqual(run(opt), ["1"])

    def test_idempotent(self):
        code = compile_source("print 4 + 5 + 6;")
        once = optimize(code)
        twice = optimize(once)
        self.assertEqual(ops(once), ops(twice))


if __name__ == "__main__":
    unittest.main()
