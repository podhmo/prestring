# -*- coding:utf-8 -*-
import contextlib
import logging
import re
from . import Module as _Module
from . import (
    INDENT,
    UNINDENT,
    NEWLINE,
    LazyFormat,
    LazyArguments,
    LazyJoin
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
            self.body.append(value)
            self.body.append(" {")
            self.body.append(NEWLINE)
        with self.scope():
            yield
        self.stmt("}")

    def comment(self, comment):
        self.stmt(LazyFormat("// {}", comment))

    def package(self, name):
        self.stmt("package {}".format(name))
        self.sep()

    def return_(self, name):
        self.stmt(LazyFormat("return {}", name))

    def type_alias(self, name, value):
        self.stmt(LazyFormat("type {} {}", name, value))
        self.sep()

    @contextlib.contextmanager
    def type_(self, name, *args):
        with self.block(LazyFormat("type {} {}", name, LazyJoin(" ", args))):
            yield
        self.sep()

    @contextlib.contextmanager
    def func(self, name, *args, return_=""):
        with self.block(LazyFormat("func {}({}) {}", name, LazyArguments(args), return_)):
            yield
        self.sep()

    @contextlib.contextmanager
    def method(self, ob, name, *args, return_=""):
        with self.block(LazyFormat("func ({}) {}({}) {}", ob, name, LazyArguments(args), return_)):
            yield
        self.sep()

    @contextlib.contextmanager
    def if_(self, cond):
        with self.block(LazyFormat("if {} ", cond)):
            yield

    @contextlib.contextmanager
    def elif_(self, cond):
        self.unnewline()
        with self.block(LazyFormat(" else if {} ", cond)):
            yield

    @contextlib.contextmanager
    def for_(self, cond):
        with self.block(LazyFormat("for {} ", cond)):
            yield

    @contextlib.contextmanager
    def else_(self):
        self.unnewline()
        with self.block(" else "):
            yield

    def select(self):
        m = self.submodule('select', newline=False)
        return MultiBranchClause(m)

    def switch(self, cond):
        m = self.submodule(LazyFormat('switch {}', cond), newline=False)
        return MultiBranchClause(m)

    def import_group(self):
        m = self.submodule("import", newline=False)
        return ImportGroup(m)

    def const_group(self):
        m = self.submodule("const", newline=False)
        return Group(m)


class MultiBranchClause(object):
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

    @contextlib.contextmanager
    def default(self):
        self.m.stmt('default:')
        with self.m.scope():
            yield


class Group(object):
    def __init__(self, m):
        self.m = m
        self.submodule = None
        self.added = set()

    def __getattr__(self, name):
        return getattr(self.m, name)

    def __enter__(self):
        self.m.stmt(' (')
        self.m.body.append(INDENT)
        self.submodule = self.m.submodule("", newline=False)
        return self

    def __call__(self, name):
        if name in self.added:
            return
        self.added.add(name)
        self.submodule.stmt(name)

    def clear_ifempty(self):
        if str(self.submodule) == "":
            self.m.clear()

    def __exit__(self, *args, **kwargs):
        self.m.body.append(UNINDENT)
        self.m.stmt(')')
        self.m.sep()


class ImportGroup(Group):
    def import_(self, name, as_=None):
        pair = (name, as_)
        if pair in self.added:
            return
        self.added.add(pair)
        if as_ is None:
            self.submodule.stmt('"{}"'.format(name))
        else:
            self.submodule.stmt('{} "{}"'.format(as_, name))
    __call__ = import_

Module = GoModule


# comfortable name expression for go.
def titlize(s):
    if not s:
        return s
    return s[0].upper() + s[1:]


class NameFormatter:
    def format(self, s,
               num_rx=re.compile("\d{2,}"),
               exclude_rx=re.compile("[^a-z0-9]", re.IGNORECASE | re.MULTILINE)):
        if not s:
            return ""
        elif num_rx.match(s):
            return self.format("Num" + s)
        elif s[0] in self.NUMBERS:
            return self.format(self.NUMBERS[s[0]] + s[1:])
        else:
            return exclude_rx.sub("", self.proper_acronym(s))

    def proper_acronym(self, s,
                       rx=re.compile("(?P<sep>^|[^a-zA-Z])(?P<frag>[a-z]+)", re.M),
                       rx2=re.compile("(?P<sep>[A-Z])(?P<frag>[a-z]+)", re.M)):
        return rx2.sub(self._proper_repl2, rx.sub(self._proper_repl1, s))

    NUMBERS = {
        '0': "Zero_", '1': "One_", '2': "Two_", '3': "Three_",
        '4': "Four_", '5': "Five_", '6': "Six_", '7': "Seven_",
        '8': "Eight_", '9': "Nine_"
    }

    # https://github.com/golang/lint/blob/39d15d55e9777df34cdffde4f406ab27fd2e60c0/lint.go#L695-L731
    COMMON_INITIALISMS = [
        "API", "ASCII", "CPU", "CSS", "DNS", "EOF", "GUID", "HTML", "HTTP",
        "HTTPS", "ID", "IP", "JSON", "LHS", "QPS", "RAM", "RHS", "RPC", "SLA",
        "SMTP", "SSH", "TCP", "TLS", "TTL", "UDP", "UI", "UID", "UUID", "URI",
        "URL", "UTF8", "VM", "XML", "XSRF", "XSS"
    ]

    def _proper_repl1(self, m):
        d = m.groupdict()
        if d["frag"].upper() in self.COMMON_INITIALISMS:
            return d["sep"] + d["frag"].upper()
        else:
            return d["sep"] + titlize(d["frag"])

    def _proper_repl2(self, m):
        d = m.groupdict()
        merged = d["sep"] + d["frag"]
        if merged.upper() in self.COMMON_INITIALISMS:
            return merged.upper()
        else:
            return merged


def goname(s, formatter=NameFormatter()):
    return formatter.format(s)
