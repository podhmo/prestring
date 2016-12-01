# -*- coding:utf-8 -*-
import unittest
from evilunit import test_function


@test_function("prestring.go:goname")
class GoNameTests(unittest.TestCase):
    def test_it(self):
        actual = self._callFUT("foo_id")
        expected = "FooID"
        self.assertEqual(actual, expected)

    def test_number(self):
        actual = self._callFUT("1times")
        expected = "OneTimes"
        self.assertEqual(actual, expected)

    def test_number_many(self):
        actual = self._callFUT("400times")
        expected = "Num400Times"
        self.assertEqual(actual, expected)
