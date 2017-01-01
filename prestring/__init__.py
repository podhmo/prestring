# -*- coding:utf-8 -*-
import logging
import contextlib
from collections import defaultdict
from io import StringIO
from prestring.output import SeparatedOutput  # NOQA
logger = logging.getLogger(__name__)


class Newline(object):
    pass


NEWLINE = Newline()

INDENT = object()
UNINDENT = object()


class PreString(object):
    def __init__(self, value, other=None):
        self.body = [value]
        if other is not None:
            self.body.append(other)

    def clear(self):
        self.body.clear()

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

    def insert_before(self, value):
        self.body.insert(0, value)

    def insert_after(self, value):
        if isinstance(self.body[-1], Newline):
            self.body.pop()
            self.append(value)
            self.body.append(NEWLINE)
        else:
            self.append(value)

    def append(self, value):
        self.body.append(value)

    def tail(self):
        return self.body[-1]

    def pop(self):
        self.body.pop()

    def head(self):
        return self.body[0]


class Sentence(object):
    def __init__(self):
        self.body = []
        self.newline = None

    def eat(self, v):
        self.body.append(v)
        return self

    def is_empty(self):
        return all(x == "" for x in self.body)

    def __str__(self):
        return "".join(map(str, self.body))


class MultiSentence(object):
    def __init__(self, *lines):
        self.lines = lines

    def iterator(self, sentence):
        if not sentence.is_empty():
            yield NEWLINE
        for line in self.lines:
            yield line
            yield NEWLINE

    def as_token(self, lexer, tokens, sentence):
        lexer.loop(tokens, sentence, self.iterator(sentence))
        return Sentence()


class Lexer(object):
    def __init__(self, container_factory, sentence_factory):
        self.container_factory = container_factory or list
        self.sentence_factory = sentence_factory or Sentence

    def loop(self, tokens, sentence, iterator):
        for v in iterator:
            if isinstance(v, Newline):
                sentence.newline = v
                tokens.append(sentence)
                sentence = self.sentence_factory()
            elif hasattr(v, "as_token"):
                sentence = v.as_token(self, tokens, sentence)
            elif v is INDENT or v is UNINDENT:
                tokens.append(v)
            else:
                sentence.eat(v)
        return (tokens, sentence)

    def __call__(self, prestring):
        tokens = self.container_factory()
        sentence = self.sentence_factory()

        tokens, sentence = self.loop(tokens, sentence, prestring)
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
            if v is INDENT:
                framelist.push_frame()
            elif v is UNINDENT:
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

    def clear(self):
        self.body.clear()

    def unnewline(self):
        if self.body.tail() == NEWLINE:
            self.body.pop()

    def submodule(self, value="", newline=True, factory=None):
        factory = factory or self.__class__
        submodule = factory(indent=self.indent,
                            newline=self.newline,
                            lexer=self.lexer,
                            parser=self.parser,
                            application=self.application)
        if value == "" or not newline:
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
        try:
            self.body.append(INDENT)
            yield
        finally:
            self.body.append(UNINDENT)

    def insert_before(self, value):
        self.body.insert_before(value)

    def append(self, value):
        self.body.append(value)

    def insert_after(self, value):
        self.body.insert_after(value)

    def __str__(self):
        evaluator = self.create_evaulator()
        tokens = self.lexer(self.body)
        framelist = self.parser(tokens)
        return str(self.application(framelist, evaluator))


# utility
class reify(object):
    def __init__(self, wrapped):
        self.wrapped = wrapped
        try:
            self.__doc__ = wrapped.__doc__
        except:
            pass

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val


class Caller(object):
    def __init__(self, name):
        self.name = name
        self.kwargs = LazyKeywords([])


class LazyArgumentsAndKeywords(object):
    def __init__(self, args=None, kwargs=None):
        self.args = LazyArguments(args or [])
        self.kwargs = LazyKeywords(kwargs or {})

    def _string(self):
        r = []
        if len(self.args.args):
            r.append(self.args)
        if len(self.kwargs.kwargs):
            r.append(self.kwargs)
        return ", ".join(map(str, r))

    @reify
    def value(self):
        return self._string()

    def __str__(self):
        return self.value


class LazyArguments(object):
    def __init__(self, args=None):
        self.args = args or []

    def _string(self):
        return ", ".join(map(str, self.args))

    @reify
    def value(self):
        return self._string()

    def __str__(self):
        return self.value


class LazyKeywords(object):
    def __init__(self, kwargs=None):
        self.kwargs = kwargs or {}

    def _string(self):
        return ", ".join(["{}={}".format(str(k), str(v)) for k, v in sorted(self.kwargs.items())])

    @reify
    def value(self):
        return self._string()

    def __str__(self):
        return self.value


class LazyKeywordsRepr(LazyKeywords):
    def _string(self):
        return ", ".join(["{}={}".format(str(k), repr(v)) for k, v in sorted(self.kwargs.items())])


class LazyJoin(object):
    def __init__(self, sep, args):
        self.sep = sep
        self.args = args

    def _string(self):
        return self.sep.join(map(str, self.args))

    @reify
    def value(self):
        return self._string()

    def __str__(self):
        return self.value


class LazyFormat(object):
    def __init__(self, fmt, *args, **kwargs):
        self.fmt = fmt
        self.args = args
        self.kwargs = kwargs

    def _string(self):
        args = map(str, self.args)
        kwargs = {k: str(v) for k, v in self.kwargs.items()}
        return self.fmt.format(*args, **kwargs)

    @reify
    def value(self):
        return self._string()

    def __str__(self):
        return self.value


class NameStore(object):
    def __init__(self):
        self.c = defaultdict(int)
        self.value_map = {}  # (src_type, dst_type) => (name, i)

    def __contains__(self, value):
        return value in self.value_map

    def __setitem__(self, value, name):
        if value not in self.value_map:
            self.value_map[value] = self.get_name(value, name)
            self.c[name] += 1

    def __getitem__(self, value):
        return self.value_map[value]

    def get_name(self, value, name):
        try:
            return self[value]
        except KeyError:
            i = self.c[name]
            return self.new_name(name, i)

    def new_name(self, name, i):
        if i == 0:
            return name
        else:
            return "{}Dup{}".format(name, i)
