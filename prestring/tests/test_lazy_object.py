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

    def test_with_types(self):
        target = self._makeOne(["x", "y"], types={"x": "int"})
        self.assertEqual(str(target), "x: int, y")

    def test_with_actual_types(self):
        target = self._makeOne(["x", "y", "*"], types={"x": int, "y": bool})
        self.assertEqual(str(target), "x: int, y: bool, *")

    def test_with_actual_types(self):
        try:
            import typing as t
            target = self._makeOne(
                ["x", "y", "z"],
                types={
                    "x": int,
                    "y": t.Optional[int],
                    "z": t.Sequence[t.Optional[int]]
                }
            )
            self.assertEqual(
                str(target),
                "x: int, y: 'typing.Union[int, NoneType]', z: 'typing.Sequence[typing.Union[int, NoneType]]'"
            )
        except ImportError:
            pass


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

    def test_with_types(self):
        target = self._makeOne({"x": 1, "y": 2, "z": 3}, types={"x": int, "z": int})
        self.assert_unordered(str(target), "x: int = 1, y=2, z: int = 3")


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
        from prestring import LazyFormat, LazyArgumentsAndKeywords
        args = LazyArgumentsAndKeywords([1, 2, 3], {"x": 1})
        target = LazyFormat("{fnname}({args})", fnname="foo", args=args)
        self.assertEqual(str(target), "foo(1, 2, 3, x=1)")

    def test_it_empty(self):
        from prestring import LazyFormat, LazyArgumentsAndKeywords
        args = LazyArgumentsAndKeywords([], {})
        target = LazyFormat("{fnname}({args})", fnname="foo", args=args)
        self.assertEqual(str(target), "foo()")

    def test_it_empty2(self):
        from prestring import LazyFormat, LazyArgumentsAndKeywords
        args = LazyArgumentsAndKeywords()
        target = LazyFormat("{fnname}({args})", fnname="foo", args=args)
        self.assertEqual(str(target), "foo()")

    def test_it_empty_kwargs(self):
        from prestring import LazyFormat, LazyArgumentsAndKeywords
        args = LazyArgumentsAndKeywords([1])
        target = LazyFormat("{fnname}({args})", fnname="foo", args=args)
        self.assertEqual(str(target), "foo(1)")

    def test_it_empty_args(self):
        from prestring import LazyFormat, LazyArgumentsAndKeywords
        args = LazyArgumentsAndKeywords(kwargs={"x": 1})
        target = LazyFormat("{fnname}({args})", fnname="foo", args=args)
        self.assertEqual(str(target), "foo(x=1)")
