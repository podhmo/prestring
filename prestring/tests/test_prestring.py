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
