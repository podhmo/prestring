# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import contextlib
from io import StringIO


NEWLINE = object()
INDENT = object()
UNINDENT = object()


class PreString(object):
    def __init__(self, value, other=None):
        self.value = [value]
        if other is not None:
            self.value.append(other)

    def subscribe(self, value):
        self.value.append(NEWLINE)
        self.value.append(value)
        return self

    stmt = subscribe

    def __iadd__(self, value):
        self.value.append(value)
        return self

    @contextlib.contextmanager
    def scope(self):
        self.value.append(INDENT)
        yield
        self.value.append(UNINDENT)

    def apply(self):
        evalator = Evaluator()
        evalator._evaluate(self, 0)
        return evalator

    def __str__(self):
        return str(self.apply())

    def __add__(self, value):
        return PreString(self, value)

    newline = "\n"
    indent = "    "

    def iterate(self):
        for v in self.value:
            if isinstance(v, PreString):
                yield from v.iterate()
            else:
                yield v

    def before(self, value):
        self.value.insert(0, value)

    def after(self, value):
        self.value.append(value)


class HasScope(object):
    def __init__(self, evaluator_factory=None):
        self.evaluator_factory = evaluator_factory or Evaluator
        self.framelist = [[]]
        self.level = 0
        self.current = self.framelist[-1]

    def push_frame(self):
        self.current = []
        self.level += 1
        target = self.framelist
        for i in range(self.level):
            target = target[-1]
        target.append(self.current)
        return self.current

    def pop_frame(self):
        self.current = []
        self.level -= 1
        target = self.framelist
        for i in range(self.level):
            target = target[-1]
        target.append(self.current)
        return self.current

    @contextlib.contextmanager
    def scope(self):
        self.push_frame()
        yield
        self.pop_frame()


class Sentence(object):
    def __init__(self):
        self.value = []

    def eat(self, v):
        self.value.append(v)
        return self

    def __str__(self):
        return "".join(self.value)


class Env(HasScope):
    def __init__(self, evaluator_factory=None):
        super(Env, self).__init__()
        self.evaluator_factory = evaluator_factory or Evaluator

    def stmt(self, value):
        ps = PreString(value)
        self.current.append(ps)
        return ps

    def apply(self):
        evaluator = self.evaluator_factory()
        for frame in self.framelist[:-1]:
            evaluator.evaluate(frame)
            evaluator.evaluate_newline()
        evaluator.evaluate(self.framelist[-1])
        return evaluator

    def __str__(self):
        return str(self.apply())


class SubEnv(HasScope):
    def __init__(self, evaluator):
        super(SubEnv, self).__init__()
        self.evaluator = evaluator
        self.current.append(Sentence())

    def apply(self, tokens, i):
        for v in tokens:
            if v is NEWLINE:
                self.current.append(Sentence())
            elif v is INDENT:
                self.push_frame()
            elif v is UNINDENT:
                self.pop_frame()
            else:
                try:
                    self.current[-1].eat(v)
                except IndexError:
                    self.current.append(Sentence())
                    self.current[-1].eat(v)

        for frame in self.framelist[:-1]:
            self.evaluator.evaluate(frame, i)
        self.evaluator.evaluate(self.framelist[-1], i)
        return self.evaluator


class Evaluator(object):
    def __init__(self, io=None, newline="\n", indent="    "):
        self.io = io or StringIO()
        self.newline = newline
        self.indent = indent

    def _evaluate(self, code, i):
        if isinstance(code, PreString):
            SubEnv(self).apply(code.iterate(), i)
        elif isinstance(code, (list, tuple)):
            self.evaluate(code, i + 1)
        else:
            self.evaluate_indent(i)
            self.io.write(str(code))  # Sentence is also ok.

    def evaluate(self, frame, i=0):
        if not frame:
            return
        for code in frame[:-1]:
            self._evaluate(code, i)
            self.evaluate_newline()
        self._evaluate(frame[-1], i)

    def evaluate_newline(self):
        self.io.write(self.newline)

    def evaluate_indent(self, i):
        for _ in range(i):
            self.io.write(self.indent)

    def __str__(self):
        return self.io.getvalue()
