# -*- coding:utf-8 -*-
import contextlib
from io import StringIO
from . import Module, Newline, NEWLINE, Evaluator
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


class PythonModule(Module):
    def create_evaulator(self):
        return PythonEvaluator(StringIO(), newline="\n", indent="    ")

    def stmt(self, fmt, *args, **kwargs):
        if args or kwargs:
            value = fmt.format(*args, **kwargs)
        else:
            value = fmt
        self.body.append(value)
        self.body.append(NEWLINE)

    def sep(self):
        self.body.append(NEWLINE)

    def pepsep(self):
        self.body.append(PEPNEWLINE)

    @contextlib.contextmanager
    def def_(self, name, *args, **kwargs):
        ps = list(args)
        ks = ["{}={}".format(str(k), str(v)) for k, v in kwargs.items()]
        ps.extend(ks)
        self.stmt("def {}({}):", name, ", ".join(ps))
        with self.scope():
            yield
        self.pepsep()

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
    def else_(self, expr):
        self.stmt("else {}:", expr)
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

    # class definition
    @contextlib.contextmanager
    def class_(self, name, bases=None, metaclass=None):
        if bases is None:
            bases = ["object"]
        args = ", ".join(str(b) for b in bases)
        if PY3:
            if metaclass is not None:
                args += ", metaclass={}".format(metaclass)
            self.stmt("class {name}({args})", name=name, args=args)
            with self.scope():
                yield
        else:
            self.stmt("class {name}({args})", name=name, args=args)
            with self.scope():
                if metaclass is not None:
                    self.stmt("__metaclass__ = {}".format(metaclass))
        self.sep()

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
        self.stmt("import %s" % (modname,))

    def from_(self, modname, *attrs):
        self.stmt("from %s import %s" % (modname, ", ".join(attrs)))

    def pass_(self):
        self.stmt("pass")
