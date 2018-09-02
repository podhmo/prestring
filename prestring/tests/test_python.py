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
        expected = ["from foo import (", "@a,", "@b,", "@c,", ")", "from boo import x"]
        self.assertEqual(result, expected)

    def test_short_call(self):
        m = self._makeOne(indent="@", width=100)
        m.call("f", "x", "y", "z='foo'")
        result = str(m)
        self.assertEqual(result, "f(x, y, z='foo')")

    def test_long_long_call(self):
        m = self._makeOne(indent="@", width=100)
        m.call(
            "SomeLongNameClass",
            "x",
            "y",
            "long long argument 0",
            "long long argument 1",
            "long long argument 2",
            "long long argument 3",
        )
        expected = [
            "SomeLongNameClass(",
            '@x,',
            '@y,',
            "@long long argument 0,",
            "@long long argument 1,",
            "@long long argument 2,",
            "@long long argument 3)",
        ]
        result = str(m).split("\n")
        self.assertEqual(result, expected)

    def test_def_with_typed(self):
        from prestring.utils import LazyArguments, LazyKeywords
        m = self._makeOne()
        with m.def_(
            "sum",
            LazyArguments(["x"], types={"x": int}),
            LazyKeywords({
                "y": 0
            }, types={"y": int}),
            return_type=int
        ):
            m.stmt("return x + y")

        expected = """
def sum(x: int, y: int = 0) -> int:
    return x + y
        """.strip()
        result = str(m)
        self.assertEqual(result, expected)

    def test_def_empty_params(self):
        from prestring.utils import LazyArgumentsAndKeywords
        m = self._makeOne()
        with m.def_("sum", LazyArgumentsAndKeywords()):
            m.stmt("return x + y")

        expected = """
def sum():
    return x + y
        """.strip()
        result = str(m)
        self.assertEqual(result, expected)

    def test_def_params__after_changed__added(self):
        from prestring.utils import LazyArgumentsAndKeywords
        m = self._makeOne()
        params = LazyArgumentsAndKeywords()
        with m.def_("sum", params):
            m.stmt("return x + y")

        params.append("x")
        expected = """
def sum(x):
    return x + y
        """.strip()

        result = str(m)
        self.assertEqual(result, expected)

    def test_method_empty_params(self):
        from prestring.utils import LazyArgumentsAndKeywords
        m = self._makeOne()
        with m.method("sum", LazyArgumentsAndKeywords()):
            m.stmt("return x + y")

        expected = """
def sum(self):
    return x + y
        """.strip()
        result = str(m)
        self.assertEqual(result, expected)

    def test_method_params__after_changed__added(self):
        from prestring.utils import LazyArgumentsAndKeywords
        m = self._makeOne()
        params = LazyArgumentsAndKeywords()
        with m.method("sum", params):
            m.stmt("return x + y")

        params.append("x")
        expected = """
def sum(self, x):
    return x + y
        """.strip()

        result = str(m)
        self.assertEqual(result, expected)
