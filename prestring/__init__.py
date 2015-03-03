# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import contextlib
from io import StringIO


class Newline(object):
    pass


class Indent(object):
    pass


class UnIndent(object):
    pass

NEWLINE = Newline()
INDENT = Indent()
UNINDENT = UnIndent()


class PreString(object):
    def __init__(self, value, other=None):
        self.body = [value]
        if other is not None:
            self.body.append(other)

    def __iadd__(self, value):
        self.body.append(value)
        return self

    def __add__(self, value):
        return self.__class__(self, value)

    def __iter__(self):
        for v in self.body:
            if isinstance(v, PreString):
                yield from iter(v)
            else:
                yield v

    def __str__(self):
        return "".join(str(v) for v in self)

    def before(self, value):
        self.body.insert(0, value)

    def after(self, value):
        if isinstance(self.body[-1], Newline):
            self.body.pop()
            self.append(value)
            self.body.append(NEWLINE)
        else:
            self.append(value)

    def append(self, value):
        self.body.append(value)


class Sentence(object):
    def __init__(self):
        self.body = []
        self.newline = None

    def eat(self, v):
        self.body.append(v)
        return self

    def is_empty(self):
        return not self.body

    def __str__(self):
        return "".join(self.body)


class Lexer(object):
    def __init__(self, container_factory, sentence_factory):
        self.container_factory = container_factory or list
        self.sentence_factory = sentence_factory or Sentence

    def __call__(self, prestring):
        tokens = self.container_factory()
        sentence = self.sentence_factory()

        for v in prestring:
            if isinstance(v, Newline):
                sentence.newline = v
                tokens.append(sentence)
                sentence = self.sentence_factory()
            elif isinstance(v, Indent) or isinstance(v, UnIndent):
                tokens.append(v)
            else:
                sentence.eat(v)
        if not sentence.is_empty():
            tokens.append(sentence)
        return tokens


class FrameList(object):
    def __init__(self):
        self.framelist = [[]]
        self.level = 0
        self.current = self.framelist[-1]

    def __getitem__(self, k):
        return self.framelist[k]

    def push_frame(self):
        self.current = []
        self.level += 1
        target = self.framelist
        for i in range(self.level):
            target = target[-1]
        target.append(self.current)
        return self.current

    def pop_frame(self):
        current = []
        self.level -= 1
        target = self.framelist
        for i in range(self.level):
            target = target[-1]
        if not target[-1]:
            target.append(current)
        self.current = target[-1]
        return self.current


class Parser(object):
    def __init__(self, framelist_factory):
        self.framelist_factory = framelist_factory

    def __call__(self, tokens):
        framelist = self.framelist_factory()
        for v in tokens:
            if isinstance(v, Indent):
                framelist.push_frame()
            elif isinstance(v, UnIndent):
                framelist.pop_frame()
            else:
                framelist.current.append(v)
            # todo: command?
        return framelist


class Application(object):
    def __call__(self, framelist, evaluator):
        for frame in framelist[:-1]:
            evaluator.evaluate(frame)
            evaluator.evaluate_newframe()
        evaluator.evaluate(framelist[-1])
        return evaluator


class Evaluator(object):
    def __init__(self, io, indent="    ", newline="\n"):
        self.io = io
        self.indent = indent
        self.newline = newline

    def evaluate(self, frame, i=0):
        if not frame:
            return
        for code in frame[:-1]:
            self._evaluate(code, i)
            self.evaluate_newline(code, i)
        self._evaluate(frame[-1], i)

    def _evaluate(self, code, i):
        if isinstance(code, (list, tuple)):
            self.evaluate(code, i + 1)
        else:
            sentence = str(code)
            if sentence == "":
                return
            self.evaluate_indent(i)
            self.io.write(sentence)  # Sentence is also ok.

    def evaluate_newline(self, code, i):
        self.io.write(self.newline)

    def evaluate_newframe(self):
        self.io.write(self.newline)

    def evaluate_indent(self, i):
        for _ in range(i):
            self.io.write(self.indent)

    def __str__(self):
        return self.io.getvalue().rstrip()


class Module(object):
    def create_body(self, value, other=None):
        return PreString(value)

    def create_evaulator(self):
        return Evaluator(StringIO(), newline=self.newline, indent=self.indent)

    def __init__(self, value="", newline="\n", indent="    ", lexer=None, parser=None, application=None):
        self.body = self.create_body(value)
        self.indent = indent
        self.newline = newline
        self.lexer = lexer or Lexer(container_factory=list, sentence_factory=Sentence)
        self.parser = parser or Parser(framelist_factory=FrameList)
        self.application = application or Application()

    def submodule(self, value=""):
        submodule = self.__class__(indent=self.indent,
                                   newline=self.newline,
                                   lexer=self.lexer,
                                   parser=self.parser,
                                   application=self.application)
        if value == "":
            submodule.append(value)
        else:
            submodule.stmt(value)
        self.body.append(submodule.body)
        return submodule

    def stmt(self, value):
        self.body.append(value)
        self.body.append(NEWLINE)
        return self

    @contextlib.contextmanager
    def scope(self):
        self.body.append(INDENT)
        yield
        self.body.append(UNINDENT)

    def before(self, value):
        self.body.before(value)

    def append(self, value):
        self.body.append(value)

    def after(self, value):
        self.body.after(value)

    def __str__(self):
        evaluator = self.create_evaulator()
        tokens = self.lexer(self.body)
        framelist = self.parser(tokens)
        return str(self.application(framelist, evaluator))
