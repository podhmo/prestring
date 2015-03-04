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

    def test_short_call(self):
        m = self._makeOne(indent="@", width=100)
        m.call("f", "x", "y", "z='foo'")
        result = str(m)
        self.assertEqual(result, "f(x, y, z='foo')")

    def test_long_long_call(self):
        m = self._makeOne(indent="@", width=100)
        m.call("SomeLongNameClass", "x", "y", "long long argument 0", "long long argument 1", "long long argument 2", "long long argument 3")
        expected = [
            "SomeLongNameClass(", '@x,', '@y,',
            "@long long argument 0,",
            "@long long argument 1,",
            "@long long argument 2,",
            "@long long argument 3)"
        ]
        result = str(m).split("\n")
        self.assertEqual(result, expected)
