# -*- coding:utf-8 -*-
import unittest
from evilunit import test_target


@test_target("prestring:LazyArguments")
class LazyArgumentsTests(unittest.TestCase):
    def test_it(self):
        target = self._makeOne([1, 2, 3])
        self.assertEqual(str(target), "1, 2, 3")

    def test_modified_after_rendeing__no_changed(self):
        target = self._makeOne([1, 2, 3])
        self.assertEqual(str(target), "1, 2, 3")
        target.args.append(4)
        self.assertEqual(str(target), "1, 2, 3")

    def test_modified_before_rendeing__changed(self):
        target = self._makeOne([1, 2, 3])
        target.args.append(4)
        self.assertEqual(str(target), "1, 2, 3, 4")


@test_target("prestring:LazyKeywords")
class LazyKeywordsTests(unittest.TestCase):
    def assert_unordered(self, xs, ys):
        self.assertEqual(tuple(sorted(xs.split(", "))), tuple(sorted(ys.split(", "))))

    def test_it(self):
        target = self._makeOne({"x": 1, "y": 2, "z": 3})
        self.assert_unordered(str(target), "x=1, y=2, z=3")

    def test_modified_after_rendeing__no_changed(self):
        target = self._makeOne({"x": 1, "y": 2, "z": 3})
        self.assert_unordered(str(target), "x=1, y=2, z=3")
        target.kwargs["a"] = "b"
        self.assert_unordered(str(target), "x=1, y=2, z=3")

    def test_modified_before_rendeing__changed(self):
        target = self._makeOne({"x": 1, "y": 2, "z": 3})
        target.kwargs["a"] = "b"
        self.assert_unordered(str(target), "x=1, y=2, z=3, a=b")


@test_target("prestring:LazyFormat")
class LazyFormatTests(unittest.TestCase):
    def test_it(self):
        fmt = "{}:{}"
        args = ("foo", "bar")
        self.assertEqual(str(self._makeOne(fmt, *args)), fmt.format(*args))

    def test_it2(self):
        fmt = "{x}:{y}"
        x, y = "foo", "bar"
        target = self._makeOne(fmt, x=x, y=y)
        self.assertEqual(str(target), fmt.format(x=x, y=y))

    def test_modified_after_rendeing__no_changed(self):
        fmt = "{x}:{y}"
        x, y = "foo", "bar"
        target = self._makeOne(fmt, x=x, y=y)
        self.assertEqual(str(target), fmt.format(x=x, y=y))
        target.fmt = "{x}:{z}"
        target.kwargs["z"] = "boo"
        self.assertEqual(str(target), fmt.format(x=x, y=y))

    def test_modified_before_rendeing__changed(self):
        fmt = "{x}:{y}"
        x, y = "foo", "bar"
        target = self._makeOne(fmt, x=x, y=y)
        target.fmt = fmt2 = "{x}:{z}"
        target.kwargs["z"] = "boo"
        self.assertEqual(str(target), fmt2.format(x=x, z="boo"))


class MixedTests(unittest.TestCase):
    def test_it(self):
        from prestring import LazyArguments, LazyKeywords, LazyFormat
        args = LazyArguments([LazyArguments([1, 2, 3]), LazyKeywords({"x": 1})])
        target = LazyFormat("{fnname}({args})", fnname="foo", args=args)
        self.assertEqual(str(target), "foo(1, 2, 3, x=1)")
