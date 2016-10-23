# -*- coding:utf-8 -*-
import contextlib
import logging
from . import Module as _Module
from . import (
    INDENT,
    UNINDENT,
    NEWLINE
)
logger = logging.getLogger(__name__)


class GoModule(_Module):
    def __init__(self, *args, **kwargs):
        kwargs["indent"] = "\t"
        super(GoModule, self).__init__(*args, **kwargs)

    def sep(self):
        self.body.append(NEWLINE)

    @contextlib.contextmanager
    def block(self):
        self.stmt("{")
        with self.scope():
            yield
        self.stmt("}")

    def comment(self, *comments):
        for comment in comments:
            for s in comment.split("\n"):
                self.stmt("// {}".format(s))

    def package(self, name):
        self.stmt("package {}".format(name))
        self.sep()

    @contextlib.contextmanager
    def func(self, name, *args, return_=""):
        self.stmt("func {}({}) {}{{".format(name, ", ".join(args), return_))
        with self.scope():
            yield
        self.stmt("}")
        self.sep()

    @contextlib.contextmanager
    def if_(self, cond):
        self.body.append("if {} ".format(cond))
        with self.block():
            yield

    @contextlib.contextmanager
    def else_(self):
        self.unnewline()
        self.body.append(" else ")
        with self.block():
            yield

    def import_group(self):
        m = self.submodule("import", newline=False)
        return ImportGroup(m)

    def const_group(self):
        m = self.submodule("const", newline=False)
        return Group(m)


class Group(object):
    def __init__(self, m):
        self.m = m
        self.inner = []

    def __enter__(self):
        self.m.stmt(' (')
        self.m.body.append(INDENT)
        return self

    def __call__(self, name):
        self.inner.append(name)

    def write_inner(self, inner):
        for name in inner:
            self.m.stmt('{}'.format(name))

    def __exit__(self, *args, **kwargs):
        self.write_inner(self.inner)
        self.m.body.append(UNINDENT)
        self.m.stmt(')')
        self.m.sep()


class ImportGroup(Group):
    def write_inner(self, inner):
        for name in inner:
            self.m.stmt('"{}"'.format(name))

Module = GoModule
