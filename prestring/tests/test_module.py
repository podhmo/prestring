# -*- coding:utf-8 -*-
from evilunit import test_target
import unittest


@test_target("prestring:Module")
class ModuleTests(unittest.TestCase):
    def test_simple(self):
        m = self._makeOne()
        m.stmt("foo")
        m.stmt("bar")
        self.assertEqual(str(m), "foo\nbar")

    def test_insert_after_module(self):
        m = self._makeOne()
        module = m.stmt("foo")
        m.stmt("bar")
        module.insert_after("@")
        self.assertEqual(str(m), "foo\nbar@")

    def test_insert_after_submodule(self):
        m = self._makeOne()
        subm = m.submodule("foo")
        m.stmt("bar")
        subm.insert_after("@")
        self.assertEqual(str(m), "foo@\nbar")

    def test_stmt_submodule(self):
        m = self._makeOne()
        subm = m.submodule("foo")
        m.stmt("bar")
        subm.stmt("@")
        self.assertEqual(str(m), "foo\n@\nbar")

    def test_insert_before_submodule(self):
        m = self._makeOne()
        subm = m.submodule("foo")
        m.stmt("bar")
        subm.insert_before("@")
        self.assertEqual(str(m), "@foo\nbar")

    def test_indent(self):
        m = self._makeOne(indent="@")
        m.stmt("foo")
        with m.scope():
            m.stmt("boo")
            with m.scope():
                m.stmt("bar")
            m.stmt("boo")
        m.stmt("foo")
        result = str(m).split("\n")
        self.assertEqual(result, ["foo", "@boo", "@@bar", "@boo", "foo"])

    def test_submodule2(self):
        m = self._makeOne(indent="@")
        subm = m.submodule("import foo")
        with m.scope():
            m.stmt("something")
            m.stmt("something")

        subm.stmt("import bar")
        subm.stmt("import boo")
        result = str(m).split("\n")
        self.assertEqual(result, ["import foo", "import bar", "import boo", "@something", "@something"])

    def test_submodule__with_indent(self):
        m = self._makeOne(indent="@")
        m.stmt("import foo")
        with m.scope():
            m.stmt("something")
            subm = m.submodule("import bar")
            m.stmt("something")

        subm.stmt("import boo")
        result = str(m).split("\n")
        self.assertEqual(result, ['import foo', '@something', '@import bar', '@import boo', '@something'])

    def test_submodule__with_scope(self):
        m = self._makeOne(indent="@")
        m.stmt("import foo")
        with m.scope():
            m.stmt("something")
            subm = m.submodule("#--- TBD ---")
            m.stmt("something")

        subm.submodule("def boo()")
        with subm.scope():
            subm.submodule("print('boo')")
        result = str(m).split("\n")
        expected = ['import foo', '@something', '@#--- TBD ---', '@def boo()', "@@print('boo')", '@something']
        self.assertEqual(result, expected)
