"""Round-trip tests for bytecode serialization and native builtins."""

import unittest

from stacklang import compile_source, run_source
from stacklang.serialize import SerializeError, dumps, loads
from stacklang.vm import VM


def run_code(code):
    vm = VM()
    vm.run(code)
    return vm.output


class SerializeTests(unittest.TestCase):
    def test_roundtrip_simple(self):
        code = compile_source("print 6 * 7;")
        restored = loads(dumps(code))
        self.assertEqual(run_code(restored), ["42"])

    def test_roundtrip_with_function(self):
        src = "func sq(n) { return n * n; } print sq(9);"
        restored = loads(dumps(compile_source(src)))
        self.assertEqual(run_code(restored), ["81"])

    def test_bad_version(self):
        with self.assertRaises(SerializeError):
            loads('{"version": 999, "code": []}')

    def test_invalid_json(self):
        with self.assertRaises(SerializeError):
            loads("{not json")


class BuiltinTests(unittest.TestCase):
    def test_abs_and_max(self):
        self.assertEqual(run_source("print abs(-5);"), ["5"])
        self.assertEqual(run_source("print max(3, 8);"), ["8"])

    def test_sqrt(self):
        self.assertEqual(run_source("print sqrt(16);"), ["4"])

    def test_string_helpers(self):
        self.assertEqual(run_source('print upper("hi");'), ["HI"])
        self.assertEqual(run_source('print len("hello");'), ["5"])


if __name__ == "__main__":
    unittest.main()
