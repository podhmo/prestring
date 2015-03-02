# -*- coding:utf-8 -*-
from evilunit import test_target
import unittest


@test_target("prestring:Env")
class EnvTests(unittest.TestCase):
    def test0(self):
        m = self._makeOne()
        m.stmt("foo")
        m.stmt("bar")
        self.assertEqual(str(m), "foo\nbar")

    def test1(self):
        m = self._makeOne()
        foo = m.stmt("foo")
        m.stmt("bar")
        foo.after("@")
        self.assertEqual(str(m), "foo@\nbar")

    def test2(self):
        m = self._makeOne()
        m.stmt("foo")
        m.push_state()
        m.stmt("boo")
        m.stmt("boo")
        m.pop_state()
        m.stmt("foo")
        result = str(m).replace("    ", "@").split("\n")
        self.assertEqual(result, ["foo", "@boo", "@boo", "foo"])

    def test3(self):
        m = self._makeOne()
        m.stmt("foo")
        m.push_state()
        m.stmt("boo")
        m.push_state()
        m.stmt("bar")
        m.pop_state()
        m.stmt("boo")
        m.pop_state()
        m.stmt("foo")
        result = str(m).replace("    ", "@").split("\n")
        self.assertEqual(result, ["foo", "@boo", "@@bar", "@boo", "foo"])

    def test_context(self):
        m = self._makeOne()
        m.stmt("foo")
        with m.scope():
            m.stmt("boo")
            with m.scope():
                m.stmt("bar")
            m.stmt("boo")
        m.stmt("foo")
        result = str(m).replace("    ", "@").split("\n")
        self.assertEqual(result, ["foo", "@boo", "@@bar", "@boo", "foo"])

    def test_pubsub(self):
        m = self._makeOne()
        pub = m.stmt("import foo")
        with m.scope():
            m.stmt("something")
            m.stmt("something")

        pub.subscribe("import bar")
        result = str(m).replace("    ", "@").split("\n")
        self.assertEqual(result, ["import foo", "import bar", "@something", "@something", ""])

    def test_pubsub__with_indented(self):
        m = self._makeOne()
        m.stmt("import foo")
        with m.scope():
            m.stmt("something")
            pub = m.stmt("import bar")
            m.stmt("something")

        pub.subscribe("import boo")
        result = str(m).replace("    ", "@").split("\n")
        self.assertEqual(result, ['import foo', '@something', '@import bar', '@import boo', '@something', ''])

    def test_pubsub__with_scope(self):
        m = self._makeOne()
        m.stmt("import foo")
        with m.scope():
            m.stmt("something")
            pub = m.stmt("#--- TBD ---")
            m.stmt("something")

        pub.subscribe("def boo()")
        with pub.scope():
            pub.subscribe("print('boo')")
        result = str(m).replace("    ", "@").split("\n")
        expected = ['import foo', '@something', '@#--- TBD ---', '@def boo()', "@@print('boo')", '@something', '']
        self.assertEqual(result, expected)
