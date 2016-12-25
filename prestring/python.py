# -*- coding:utf-8 -*-
import contextlib
from io import StringIO
from . import Module as _Module
from . import (
    Newline,
    NEWLINE,
    INDENT,
    UNINDENT,
    Evaluator,
    Sentence,
    LazyArguments,
    LazyKeywords,
    LazyArgumentsAndKeywords,
    LazyFormat
)
from .compat import PY3


PEPNEWLINE = Newline()


class PythonEvaluator(Evaluator):
    def evaluate_newframe(self):
        self.io.write(self.newline)
        self.io.write(self.newline)

    def evaluate_newline(self, code, i):
        self.io.write(self.newline)
        if i <= 0 and hasattr(code, "newline") and code.newline is PEPNEWLINE:
            self.io.write(self.newline)


class PythonModule(_Module):
    def __init__(self, *args, **kwargs):
        self.width = kwargs.pop("width", 100)
        self.import_unique = kwargs.pop("import_unique", False)
        super(PythonModule, self).__init__(*args, **kwargs)
        self.from_map = {}  # module -> PythonModule

    def submodule(self, value="", newline=True):
        submodule = super(PythonModule, self).submodule(value=value, newline=newline)
        submodule.width = self.width
        submodule.import_unique = self.import_unique
        return submodule

    def create_evaulator(self):
        return PythonEvaluator(StringIO(), newline=self.newline, indent=self.indent)

    def stmt(self, fmt, *args, **kwargs):
        if args or kwargs:
            value = LazyFormat(fmt, *args, **kwargs)
        else:
            value = fmt
        self.body.append(value)
        self.body.append(NEWLINE)

    def sep(self):
        self.body.append(PEPNEWLINE)

    def method(self, name, *args, **kwargs):
        return self.def_(name, "self", *args, **kwargs)

    @contextlib.contextmanager
    def with_(self, expr, as_=None):
        if as_:
            self.stmt(LazyFormat("with {} as {}:", expr, as_))
        else:
            self.stmt(LazyFormat("with {}:", expr))
        with self.scope():
            yield

    @contextlib.contextmanager
    def def_(self, name, *args, **kwargs):
        self.stmt(LazyFormat("def {}({}):", name, LazyArgumentsAndKeywords(args, kwargs)))
        with self.scope():
            yield
        self.sep()

    @contextlib.contextmanager
    def if_(self, expr):
        self.stmt("if {}:", expr)
        with self.scope():
            yield

    @contextlib.contextmanager
    def unless(self, expr):
        self.stmt("if not ({}):", expr)
        with self.scope():
            yield

    @contextlib.contextmanager
    def elif_(self, expr):
        self.stmt("elif {}:", expr)
        with self.scope():
            yield

    @contextlib.contextmanager
    def else_(self):
        self.stmt("else:")
        with self.scope():
            yield

    @contextlib.contextmanager
    def for_(self, var, iterator):
        self.stmt("for {var} in {iterator}:", var=var, iterator=iterator)
        with self.scope():
            yield

    @contextlib.contextmanager
    def while_(self, expr):
        self.stmt("while {expr}:", expr=expr)
        with self.scope():
            yield

    @contextlib.contextmanager
    def try_(self):
        self.stmt("try:")
        with self.scope():
            yield

    @contextlib.contextmanager
    def except_(self, expr=None):
        if expr:
            self.stmt("except {expr}:", expr=expr)
        else:
            self.stmt("except:")
        with self.scope():
            yield

    @contextlib.contextmanager
    def finally_(self):
        self.stmt("finally:")
        with self.scope():
            yield

    # class definition
    @contextlib.contextmanager
    def class_(self, name, bases=None, metaclass=None):
        if bases is None:
            bases = "object"
        if not isinstance(bases, (list, tuple)):
            bases = [bases]
        args = ", ".join(str(b) for b in bases)
        if PY3:
            if metaclass is not None:
                args += ", metaclass={}".format(metaclass)
            self.stmt("class {name}({args}):", name=name, args=args)
            with self.scope():
                yield
        else:
            self.stmt("class {name}({args}):", name=name, args=args)
            with self.scope():
                if metaclass is not None:
                    self.stmt("__metaclass__ = {}".format(metaclass))
        self.sep()

    @contextlib.contextmanager
    def main(self):
        with self.if_('__name__ == "__main__"'):
            yield

    # sentence
    def break_(self):
        self.stmt("break")

    def continue_(self):
        self.stmt("continue")

    def return_(self, expr, *args):
        self.stmt("return %s" % (expr,), *args)

    def yield_(self, expr, *args):
        self.stmt("yield %s" % (expr,), *args)

    def raise_(self, expr, *args):
        self.stmt("raise %s" % (expr,), *args)

    def import_(self, modname):
        # todo: considering self.import_unique
        self.stmt("import {}", modname)

    def from_(self, modname, *attrs):
        try:
            from_stmt = self.from_map[modname].body.tail()
            for sym in attrs:
                from_stmt.append(sym)
        except KeyError:
            self.from_map[modname] = self.submodule(FromStatement(modname, attrs, unique=self.import_unique), newline=False)

    @contextlib.contextmanager
    def hugecall(self, name):
        caller = Caller(name)
        yield caller
        self.call(caller.name, *caller.args)

    def call(self, name_, *args):
        oneline = LazyFormat("{}({})", name_, LazyArguments(args))
        if len(str(oneline._string())) <= self.width:
            self.stmt(oneline)
        else:
            self.body.append(MultiSentenceForCall(name_, *args))

    def pass_(self):
        self.stmt("pass")


class Caller(object):
    def __init__(self, name):
        self.name = name
        self.kwargs = LazyKeywords([])

    def add(self, **kwargs):
        for k, v in kwargs.items():
            self.kwargs.kwargs[k] = v


class FromStatement(object):
    def __init__(self, modname, symbols, unique=False):
        self.modname = modname
        self.symbols = list(symbols)
        self.unique = unique

    def append(self, symbol):
        self.symbols.append(symbol)

    def stmt(self, s):
        yield s
        yield NEWLINE

    def iterator_for_one_symbol(self, sentence):
        if not sentence.is_empty():
            yield NEWLINE
        yield from self.stmt("from {} import {}".format(self.modname, self.symbols[0]))

    def iterator_for_many_symbols(self, sentence):
        if not sentence.is_empty():
            yield NEWLINE
        yield from self.stmt("from {} import(".format(self.modname))
        yield INDENT
        if self.unique:
            symbols = tuple(sorted(set(self.symbols)))
        else:
            symbols = self.symbols
        for sym in symbols[:-1]:
            yield from self.stmt("{},".format(sym))
        yield from self.stmt("{}".format(symbols[-1]))
        yield UNINDENT
        yield from self.stmt(")")

    def as_token(self, lexer, tokens, sentence):
        if len(self.symbols) <= 1:
            lexer.loop(tokens, sentence, self.iterator_for_one_symbol(sentence))
        else:
            lexer.loop(tokens, sentence, self.iterator_for_many_symbols(sentence))
        return Sentence()


class MultiSentenceForCall(object):
    def __init__(self, name, *lines):
        self.name = name
        self.lines = lines

    def iterator(self, sentence):
        if not sentence.is_empty():
            yield NEWLINE
        yield LazyFormat("{}(", self.name)
        yield NEWLINE
        yield INDENT
        for line in self.lines[:-1]:
            yield LazyFormat("{},", line)
            yield NEWLINE
        yield LazyFormat("{})", self.lines[-1])
        yield NEWLINE
        yield UNINDENT

    def as_token(self, lexer, tokens, sentence):
        lexer.loop(tokens, sentence, self.iterator(sentence))
        return Sentence()


Module = PythonModule
