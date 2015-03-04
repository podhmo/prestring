# -*- coding:utf-8 -*-
import unittest
from evilunit import test_target


@test_target("prestring.python:PythonModule")
class Tests(unittest.TestCase):
    def test_from_statement(self):
        m = self._makeOne(indent="@")
        m.from_("foo", "a", "b")
        m.from_("boo", "x")
        m.from_("foo", "c")
        result = str(m).split("\n")
        expected = ["from foo import(", "@a,", "@b,", "@c", ")", "from boo import x"]
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
