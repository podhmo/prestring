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
    def block(self, value=None):
        if value is None:
            self.stmt("{")
        else:
            self.stmt("{} {{".format(value))
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

    def return_(self, name):
        self.stmt("return {}".format(name))

    def type_alias(self, name, value):
        self.stmt("type {} {}".format(name, value))
        self.sep()

    @contextlib.contextmanager
    def type_(self, name, *args):
        with self.block("type {} {}".format(name, " ".join(args))):
            yield
        self.sep()

    @contextlib.contextmanager
    def func(self, name, *args, return_=""):
        with self.block("func {}({}) {}".format(name, ", ".join(args), return_)):
            yield
        self.sep()

    @contextlib.contextmanager
    def if_(self, cond):
        with self.block("if {} ".format(cond)):
            yield

    @contextlib.contextmanager
    def for_(self, cond):
        with self.block("for {} ".format(cond)):
            yield

    @contextlib.contextmanager
    def else_(self):
        self.unnewline()
        with self.block(" else "):
            yield

    def select(self):
        m = self.submodule('select', newline=False)
        return SelectClause(m)

    def import_group(self):
        m = self.submodule("import", newline=False)
        return ImportGroup(m)

    def const_group(self):
        m = self.submodule("const", newline=False)
        return Group(m)


class SelectClause(object):
    def __init__(self, m):
        self.m = m

    def __getattr__(self, name):
        return getattr(self.m, name)

    def __enter__(self):
        self.m.stmt(' {')
        return self

    @contextlib.contextmanager
    def case(self, value):
        self.m.stmt('case {}:'.format(value))
        with self.m.scope():
            yield

    def __exit__(self, *args, **kwargs):
        self.m.stmt('}')
        self.m.sep()


class Group(object):
    def __init__(self, m):
        self.m = m
        self.submodule = None

    def __getattr__(self, name):
        return getattr(self.m, name)

    def __enter__(self):
        self.m.stmt(' (')
        self.m.body.append(INDENT)
        self.submodule = self.m.submodule("", newline=False)
        return self

    def __call__(self, name):
        self.submodule.stmt('{}'.format(name))

    def __exit__(self, *args, **kwargs):
        self.m.body.append(UNINDENT)
        self.m.stmt(')')
        self.m.sep()


class ImportGroup(Group):
    def import_(self, name, as_=None):
        if as_ is None:
            self.submodule.stmt('"{}"'.format(name))
        else:
            self.submodule.stmt('{} "{}"'.format(as_, name))
    __call__ = import_

Module = GoModule
