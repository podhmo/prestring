# type: ignore
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
        expected = ["from foo import (", "@a,", "@b,", "@c", ")", "from boo import x"]
        self.assertEqual(result, expected)

    def test_def_with_typed(self):
        from prestring.utils import LazyArguments, LazyKeywords

        m = self._makeOne()
        with m.def_(
            "sum",
            LazyArguments(["x"], types={"x": int}),
            LazyKeywords({"y": 0}, types={"y": int}),
            return_type=int,
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
