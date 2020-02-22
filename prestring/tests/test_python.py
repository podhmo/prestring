# type: ignore
import unittest
from evilunit import test_target


@test_target("prestring.python:PythonModule")
class Tests(unittest.TestCase):
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

    def test_import(self):
        m = self._makeOne()

        got = m.import_("re")

        self.assertEqual(str(m), "import re")
        self.assertEqual(str(got), "re")

    def test_import_as(self):
        m = self._makeOne()

        got = m.import_("re", as_="r")

        self.assertEqual(str(m), "import re as r")
        self.assertEqual(str(got), "r")

    def test_import_attr(self):
        m = self._makeOne()

        got = m.import_("re").compile(".+")

        self.assertEqual(str(m), "import re")
        self.assertEqual(str(got), "re.compile('.+')")

    def test_import2(self):
        m = self._makeOne()

        got = m.import_("urllib.parse")

        self.assertEqual(str(m), "import urllib.parse")
        self.assertEqual(str(got), "urllib.parse")

    def test_import_attr2(self):
        m = self._makeOne()

        got = m.import_("urllib.parse").urlparse("https://example.net")

        self.assertEqual(str(m), "import urllib.parse")
        self.assertEqual(str(got), "urllib.parse.urlparse('https://example.net')")

    def test_from_(self):
        m = self._makeOne()

        got = m.from_("foo", "bar")
        self.assertEqual(str(m), "from foo import bar")
        self.assertEqual(str(got.import_("boo")), "boo")

    def test_from_as(self):
        m = self._makeOne()

        got = m.from_("foo", "bar")
        self.assertEqual(str(m), "from foo import bar")
        self.assertEqual(str(got.import_("boo", as_="b")), "b")

    def test_from_as2(self):
        m = self._makeOne()

        got = m.from_("foo", "bar")
        self.assertEqual(str(got.import_("boo", as_="b")), "b")
        self.assertEqual(str(got.import_("bee", as_="b2")), "b2")
        self.assertEqual(
            str(m), "from foo import (\n    bar,\n    boo as b,\n    bee as b2,\n)"
        )

    def test_from_statement(self):
        m = self._makeOne(indent="@")
        m.from_("foo", "a", "b")
        m.from_("boo", "x")
        m.from_("foo", "c")
        result = str(m).split("\n")
        expected = ["from foo import (", "@a,", "@b,", "@c,", ")", "from boo import x"]
        self.assertEqual(result, expected)
