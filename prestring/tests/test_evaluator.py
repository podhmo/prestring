# -*- coding:utf-8 -*-
from evilunit import test_target
import unittest


@test_target("prestring:Evaluator")
class EvalatorTests(unittest.TestCase):
    def _makeOne(self, indent=" "):
        from io import StringIO
        return self._getTarget()(StringIO(), indent=indent)

    def test_flatten_string(self):
        target = self._makeOne()
        script = ["foo", "bar", "boo"]
        target.evaluate(script)

        result = str(target)
        self.assertEqual(result, "foo\nbar\nboo")

    def test_flatten_prestring(self):
        from prestring import PreString

        target = self._makeOne()
        script = [PreString("foo"), PreString("bar"), PreString("boo")]
        target.evaluate(script)

        result = str(target)
        self.assertEqual(result, "foo\nbar\nboo")

    def test_indented_string(self):
        target = self._makeOne(indent="@")
        script = ["foo", ["bar", "boo"], "yey"]
        target.evaluate(script)
        result = str(target).split("\n")
        self.assertEqual(result, ["foo", "@bar", "@boo", "yey"])

    def test_indented_string2(self):
        target = self._makeOne(indent="@")
        script = ["foo", ["bar", ["boo"], "bar"], "yey", [["beh"]]]
        target.evaluate(script)
        result = str(target).split("\n")
        self.assertEqual(result, ["foo", "@bar", "@@boo", "@bar", "yey", "@@beh"])

    def test_indented_string3(self):
        target = self._makeOne(indent="@")
        script = [[["foo", "bar"]]]
        target.evaluate(script)
        result = str(target).split("\n")
        self.assertEqual(result, ["@@foo", "@@bar"])

