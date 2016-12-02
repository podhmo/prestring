# -*- coding:utf-8 -*-
from evilunit import test_target
import unittest


@test_target("prestring:NameStore")
class NameStoreTests(unittest.TestCase):
    def test_same_thing_twice(self):
        target = self._makeOne()
        one = object()
        target[one] = "foo"
        self.assertEqual(target[one], "foo")
        target[one] = "foo"
        self.assertEqual(target[one], "foo")

    def test_same_name_but_another_key(self):
        target = self._makeOne()
        one = object()
        two = object()
        target[one] = "foo"
        self.assertEqual(target[one], "foo")
        target[two] = "foo"
        self.assertEqual(target[two], target.new_name("foo", 1))
        self.assertEqual(target[two], "fooDup1")

    def test_another_name(self):
        target = self._makeOne()
        one = object()
        two = object()
        target[one] = "foo"
        self.assertEqual(target[one], "foo")
        target[two] = "bar"
        self.assertEqual(target[two], "bar")
