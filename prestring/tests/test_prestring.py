# -*- coding:utf-8 -*-
from evilunit import test_target
import unittest


@test_target("prestring:PreString")
class PreStringTests(unittest.TestCase):
    def test0(self):
        target = self._makeOne("foo")
        self.assertEqual(str(target), "foo")

    def test1(self):
        target = self._makeOne("foo")
        result = target + "boo"
        self.assertEqual(str(result), "fooboo")

    def test2(self):
        target = self._makeOne("foo")
        result = target + self._makeOne("boo")
        self.assertEqual(str(result), "fooboo")

    def test3(self):
        target = self._makeOne("foo")
        target += "boo"
        self.assertEqual(str(target), "fooboo")

    def test4(self):
        target = self._makeOne("foo")
        target += self._makeOne("boo")
        self.assertEqual(str(target), "fooboo")

    def test5(self):
        target = self._makeOne("foo")
        result = target + self._makeOne("boo")
        result = result + result
        self.assertEqual(str(result), "fooboofooboo")

    def test6(self):
        target = self._makeOne("def f(n)")
        with target.scope():
            target.stmt("if n <= 0:")
            with target.scope():
                target.stmt("return 1")
            target.stmt("else:")
            with target.scope():
                target.stmt("return n * f(n - 1)")
        result = str(target).split("\n")
        expected = ["def f(n)", "    if n <= 0:", "        return 1", "    else:", "        return n * f(n - 1)", ""]
        self.assertEqual(result, expected)
