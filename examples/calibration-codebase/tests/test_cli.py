"""Tests for the command-line interface dispatch."""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from stacklang.cli import main


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def _write(self, name, content):
        path = os.path.join(self.tmp, name)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
        return path

    def _capture(self, argv):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(argv)
        return code, buf.getvalue()

    def test_run(self):
        path = self._write("p.stk", "print 2 + 3;")
        code, output = self._capture(["run", path])
        self.assertEqual(code, 0)
        self.assertIn("5", output)

    def test_dis(self):
        path = self._write("p.stk", "print 1;")
        code, output = self._capture(["dis", path])
        self.assertEqual(code, 0)
        self.assertIn("PRINT", output)

    def test_check_ok(self):
        path = self._write("p.stk", "let x = 1; print x;")
        code, output = self._capture(["check", path])
        self.assertEqual(code, 0)
        self.assertIn("ok", output)

    def test_check_error(self):
        path = self._write("p.stk", "print missing;")
        code, _ = self._capture(["check", path])
        self.assertEqual(code, 1)

    def test_pprint(self):
        path = self._write("p.stk", "print 1 + 2;")
        code, output = self._capture(["pprint", path])
        self.assertEqual(code, 0)
        self.assertIn("program", output)

    def test_asm(self):
        path = self._write("m.sasm", ".const 0 6\n.const 1 7\nPUSH 0\nPUSH 1\nMUL\nPRINT\nHALT\n")
        code, output = self._capture(["asm", path])
        self.assertEqual(code, 0)
        self.assertIn("42", output)

    def test_no_command(self):
        code, _ = self._capture([])
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
