import typing as t
import logging
import contextlib
from io import StringIO
from prestring.utils import (  # NOQA
    reify,
    LazyFormat,
    LazyArguments,
    LazyJoin,
    LazyKeywords,
    LazyKeywordsRepr,
    LazyArgumentsAndKeywords,
    NameStore,
)
from .types import Stringer

logger = logging.getLogger(__name__)
ModuleT = t.TypeVar("ModuleT", bound="Module")
StmtTargetType = t.Union[str, "_Sentinel", LazyFormat, Stringer]


class _Sentinel:
    __slots__ = ("name", "kind")

    def __init__(self, *, kind: str, name: str) -> None:
        self.kind = kind
        self.name = name

    def __repr__(self) -> str:
        return f"<{self.name}>"


NEWLINE = _Sentinel(name="NEWLINE", kind="sep")

INDENT = _Sentinel(name="INDENT", kind="indent")
UNINDENT = _Sentinel(name="UNINDENT", kind="indent")


class PreString:
    def __init__(self, value: t.Any, other: t.Optional[t.Any] = None) -> None:
        self.body = [value]
        if other is not None:
            self.body.append(other)

    def clear(self) -> None:
        self.body.clear()

    def __iadd__(self, value: t.Any) -> "PreString":
        self.body.append(value)
        return self

    def __add__(self, value: t.Any) -> "PreString":
        return self.__class__(self, value)

    def __iter__(self) -> t.Iterator[t.Any]:
        for v in self.body:
            if isinstance(v, PreString):
                yield from iter(v)
            else:
                yield v

    def __str__(self) -> str:
        return "".join(str(v) for v in self)

    def insert_before(self, value: t.Any) -> None:
        self.body.insert(0, value)

    def insert_after(self, value: t.Any) -> None:
        if getattr(self.body[-1], "kind", None) == "sep":
            self.body.pop()
            self.append(value)
            self.body.append(NEWLINE)
        else:
            self.append(value)

    def append(self, value: t.Any) -> None:
        self.body.append(value)

    def tail(self) -> t.Any:
        return self.body[-1]

    def pop(self) -> t.Any:
        return self.body.pop()

    def head(self) -> t.Any:
        return self.body[0]


class Sentence:
    def __init__(self) -> None:
        self.body: t.List[t.Any] = []
        self.newline = None

    def append(self, v: t.Any) -> "Sentence":
        self.body.append(v)
        return self

    def is_empty(self) -> bool:
        return all(x == "" for x in self.body)

    def __str__(self) -> str:
        return "".join(map(str, self.body))


class Lexer:
    def __init__(
        self,
        container_factory: t.Optional[t.Callable[[], t.List[t.Any]]],
        sentence_factory: t.Optional[t.Callable[[], Sentence]],
    ) -> None:
        self.container_factory = container_factory or list
        self.sentence_factory = sentence_factory or Sentence

    def lex(
        self,
        source: t.Iterable[t.Any],
        *,
        tokens: t.Optional[t.List[t.Any]] = None,
        sentence: t.Optional[Sentence] = None,
    ) -> t.List[t.Any]:
        r: t.List[t.Any] = tokens or self.container_factory()
        if sentence is None:
            sentence = self.sentence_factory()

        for v in source:
            if getattr(v, "kind", None) == "sep":
                sentence.newline = v
                r.append(sentence)
                sentence = self.sentence_factory()
            elif hasattr(v, "emit"):
                r.append(v)
            elif hasattr(v, "on_lex"):
                r = v.on_lex(self, r, sentence)
            elif v is INDENT or v is UNINDENT:
                r.append(v)
            else:
                sentence.append(v)

        if not sentence.is_empty():
            r.append(sentence)
        return r


class FrameList:
    def __init__(self) -> None:
        self.framelist: t.List[t.List[t.Any]] = [[]]
        self.level = 0
        self.current: t.List[t.Any] = self.framelist[-1]

    @t.overload  # noqa F811
    def __getitem__(self, k: int) -> t.List[t.Any]:
        ...

    @t.overload  # noqa F811
    def __getitem__(self, k: slice) -> t.Iterable[t.List[t.Any]]:  # noqa F811
        ...

    def __getitem__(  # noqa F811
        self, k: t.Union[int, slice]
    ) -> t.Union[t.List[t.Any], t.Iterable[t.List[t.Any]]]:
        return self.framelist[k]

    def push_frame(self) -> t.List[t.Any]:
        self.current = []
        self.level += 1
        target = self.framelist
        for i in range(self.level):
            target = target[-1]
        target.append(self.current)
        return self.current

    def pop_frame(self) -> t.List[t.Any]:
        current: t.List[t.Any] = []
        self.level -= 1
        target = self.framelist
        for i in range(self.level):
            target = target[-1]
        if not target[-1]:
            target.append(current)
        self.current = target[-1]
        return self.current


class Parser:
    def __init__(self, framelist_factory: t.Callable[[], FrameList]) -> None:
        self.framelist_factory = framelist_factory

    def parse(self, tokens: t.List[t.Union[_Sentinel, t.Any]]) -> FrameList:
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


class Emitter:
    def emit(self, framelist: FrameList, evaluator: "Evaluator") -> str:
        for frame in framelist[:-1]:
            evaluator.evaluate(frame)
            evaluator.do_newframe()
        evaluator.evaluate(framelist[-1])
        return str(evaluator)


class Evaluator:
    def __init__(self, io: StringIO, indent: str = "    ", newline: str = "\n"):
        self.io = io
        self.indent = indent
        self.newline = newline

    def evaluate(self, frame: t.Sequence[t.Any], i: int = 0) -> None:
        if not frame:
            return
        for code in frame[:-1]:
            self.do_code(code, i)
            self.do_newline(code, i)
        self.do_code(frame[-1], i)

    def do_code(
        self, code: t.Union[t.List[t.Any], t.Tuple[t.Any, ...], t.Any], i: int
    ) -> None:
        if isinstance(code, (list, tuple)):
            self.evaluate(code, i + 1)
        else:
            sentence = str(code)
            if sentence == "":
                return
            self.do_indent(i)
            self.io.write(sentence)  # Sentence is also ok.

    def do_newline(self, code: t.Any, i: int) -> None:
        self.io.write(self.newline)

    def do_newframe(self) -> None:
        self.io.write(self.newline)

    def do_indent(self, i: int) -> None:
        for _ in range(i):
            self.io.write(self.indent)

    def __str__(self) -> str:
        return self.io.getvalue().rstrip()


class Module:
    def create_body(self, value: t.Any, other: t.Optional[t.Any] = None) -> PreString:
        return PreString(value)

    def create_evaulator(self) -> Evaluator:
        return Evaluator(StringIO(), newline=self.newline, indent=self.indent)

    def __init__(
        self,
        value: str = "",
        *,
        newline: str = "\n",
        indent: str = "    ",
        lexer: t.Optional[Lexer] = None,
        parser: t.Optional[Parser] = None,
        emitter: t.Optional[Emitter] = None,
        on_lex: t.Optional[
            t.Callable[[Lexer, t.List[t.Any], Sentence], t.List[t.Any]]
        ] = None,
    ):
        self.body = self.create_body(value)
        self.indent = indent
        self.newline = newline
        self.lexer = lexer or Lexer(container_factory=list, sentence_factory=Sentence)
        self.parser = parser or Parser(framelist_factory=FrameList)
        self.emitter = emitter or Emitter()
        self.on_lex = on_lex or self.default_on_lex

    def clear(self) -> None:
        self.body.clear()

    def unnewline(self) -> None:
        if self.body.tail() == NEWLINE:
            self.body.pop()

    def submodule(
        self: ModuleT,
        value: t.Any = "",
        *,
        newline: bool = True,
        factory: t.Optional[t.Callable[..., ModuleT]] = None,
        on_lex: t.Optional[
            t.Callable[[Lexer, t.List[t.Any], Sentence], t.List[t.Any]]
        ] = None,
    ) -> ModuleT:
        factory_ = factory or self.__class__
        submodule = factory_(
            indent=self.indent,
            newline=self.newline,
            lexer=self.lexer,
            parser=self.parser,
            emitter=self.emitter,
            on_lex=on_lex,
        )
        if value == "" or not newline:
            submodule.append(value)
        else:
            submodule.stmt(value)
        self.body.append(submodule)
        return submodule

    def stmt(
        self: ModuleT, fmt: StmtTargetType, *args: t.Any, **kwargs: t.Any,
    ) -> ModuleT:
        if hasattr(fmt, "emit"):
            if getattr(fmt, "emit", None) is not None:  # Emittable
                assert not args
                assert not kwargs
                return fmt.emit(m=self)  # type: ignore
            else:
                fmt = str(fmt)

        if args or kwargs:
            self.body.append(self.format(fmt, *args, **kwargs))  # lazy format
        else:
            self.body.append(fmt)  # str
        self.body.append(NEWLINE)
        return self

    @contextlib.contextmanager
    def scope(self) -> t.Iterator[None]:
        try:
            self.body.append(INDENT)
            yield
        finally:
            self.body.append(UNINDENT)

    def insert_before(self, value: t.Any) -> None:
        self.body.insert_before(value)

    def append(self, value: t.Any) -> None:
        self.body.append(value)

    def insert_after(self, value: t.Any) -> None:
        self.body.insert_after(value)

    def __str__(self) -> str:
        evaluator = self.create_evaulator()
        tokens = self.lexer.lex(self.body)
        framelist = self.parser.parse(tokens)
        return self.emitter.emit(framelist, evaluator)

    def default_on_lex(
        self, lexer: Lexer, tokens: t.List[t.Any], sentence: Sentence
    ) -> t.List[t.Any]:
        return lexer.lex(self.body, tokens=tokens)

    format = LazyFormat
