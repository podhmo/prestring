import typing as t
import contextlib
from io import StringIO
from prestring import Module as _Module
from prestring import (
    _Sentinel,
    NEWLINE,
    INDENT,
    UNINDENT,
    Sentence as Sentence,
    Evaluator as _Evaluator,
    Lexer as _Lexer,
    Parser as _Parser,
    Application as _Application,
)
from prestring import ModuleT as _ModuleT
from prestring.utils import LazyArgumentsAndKeywords
from prestring.utils import _type_value  # xxx
from ._codeobject import Symbol

PEPNEWLINE = _Sentinel(name="PEP-NEWLINE", kind="sep")


class PythonEvaluator(_Evaluator):
    def evaluate_newframe(self) -> None:
        self.io.write(self.newline)
        self.io.write(self.newline)

    def evaluate_newline(self, code: t.Any, i: int) -> None:
        self.io.write(self.newline)
        if i <= 0 and hasattr(code, "newline") and code.newline is PEPNEWLINE:
            self.io.write(self.newline)


def make_params(
    args: t.Sequence[t.Any], kwargs: t.Dict[str, t.Any]
) -> LazyArgumentsAndKeywords:
    if not kwargs and len(args) == 1 and hasattr(args[0], "append_tail"):
        # shortcut
        return args[0]  # type:ignore
    return LazyArgumentsAndKeywords(list(args), kwargs)


class PythonModule(_Module):
    def __init__(
        self,
        value: str = "",
        newline: str = "\n",
        indent: str = "    ",
        lexer: t.Optional[_Lexer] = None,
        parser: t.Optional[_Parser] = None,
        application: t.Optional[_Application] = None,
        width: int = 100,
        **kwargs: t.Any,
    ) -> None:
        self.width = width
        super().__init__(
            value, newline, indent, lexer=lexer, parser=parser, application=application
        )
        self.from_map: t.Dict[str, PythonModule] = {}  # module -> PythonModule
        self.imported_map: t.Dict[str, Symbol] = {}

    def submodule(
        self,
        value: t.Any = "",  # str,FromStatement,...
        newline: bool = True,
        factory: t.Optional[t.Callable[..., _ModuleT]] = None,
    ) -> _ModuleT:
        submodule = t.cast(
            PythonModule,
            super().submodule(value=value, newline=newline, factory=factory,),
        )  # xxx
        submodule.width = self.width
        return submodule  # type:ignore

    def create_evaulator(self) -> PythonEvaluator:
        return PythonEvaluator(StringIO(), newline=self.newline, indent=self.indent)

    def sep(self) -> None:
        self.body.append(PEPNEWLINE)

    @contextlib.contextmanager
    def with_(
        self, expr: t.Any, *, as_: t.Optional[t.Any] = None, async_: bool = False
    ) -> t.Iterator[None]:
        prefix = f"{'async ' if async_ else ''}with"
        if as_:
            self.stmt("{} {} as {}:", prefix, expr, as_)
        else:
            self.stmt("{} {}:", prefix, expr)
        with self.scope():
            yield

    @contextlib.contextmanager
    def def_(
        self,
        name: str,
        *args: t.Any,
        return_type: t.Optional[t.Any] = None,
        async_: bool = False,
        **kwargs: t.Any,
    ) -> t.Iterator[None]:
        params = make_params(args, kwargs)

        prefix = f"{'async ' if async_ else ''}def"
        if return_type is not None:
            self.stmt(
                "{} {}({}) -> {}:", prefix, name, params, _type_value(return_type)
            )
        else:
            self.stmt("{} {}({}):", prefix, name, params)
        with self.scope():
            yield
        self.sep()

    @contextlib.contextmanager
    def if_(self, expr: t.Any) -> t.Iterator[None]:
        self.stmt("if {}:", expr)
        with self.scope():
            yield

    def docstring(self, doc: str) -> None:
        self.stmt('"""')
        for line in doc.split("\n"):
            self.stmt(line)
        self.stmt('"""')

    @contextlib.contextmanager
    def unless(self, expr: t.Any) -> t.Iterator[None]:
        self.stmt("if not ({}):", expr)
        with self.scope():
            yield

    @contextlib.contextmanager
    def elif_(self, expr: t.Any) -> t.Iterator[None]:
        self.stmt("elif {}:", expr)
        with self.scope():
            yield

    @contextlib.contextmanager
    def else_(self) -> t.Iterator[None]:
        self.stmt("else:")
        with self.scope():
            yield

    @contextlib.contextmanager
    def for_(
        self, var: t.Any, iterator: t.Optional[t.Any] = None, *, async_: bool = False
    ) -> t.Iterator[None]:
        prefix = f"{'async ' if async_ else ''}for"
        if iterator is None:
            self.stmt("{prefix} {var}:", prefix=prefix, var=var)
        else:
            self.stmt(
                "{prefix} {var} in {iterator}:",
                prefix=prefix,
                var=var,
                iterator=iterator,
            )
        with self.scope():
            yield

    @contextlib.contextmanager
    def while_(self, expr: t.Any) -> t.Iterator[None]:
        self.stmt("while {expr}:", expr=expr)
        with self.scope():
            yield

    @contextlib.contextmanager
    def try_(self) -> t.Iterator[None]:
        self.stmt("try:")
        with self.scope():
            yield

    @contextlib.contextmanager
    def except_(
        self, expr: t.Optional[t.Any] = None, as_: t.Optional[t.Any] = None
    ) -> t.Iterator[None]:
        if expr:
            if as_ is not None:
                self.stmt("except {expr} as {as_}:", expr=expr, as_=as_)
            else:
                self.stmt("except {expr}:", expr=expr)
        else:
            self.stmt("except:")
        with self.scope():
            yield

    @contextlib.contextmanager
    def finally_(self) -> t.Iterator[None]:
        self.stmt("finally:")
        with self.scope():
            yield

    # class definition
    @contextlib.contextmanager
    def class_(
        self, name: t.Any, bases: t.Any = "", metaclass: t.Optional[t.Any] = None
    ) -> t.Iterator[None]:
        if not isinstance(bases, (list, tuple)):
            bases = [bases]
        args = [str(b) for b in bases if b]
        if metaclass is not None:
            args.append("metaclass={}".format(metaclass))
        if args:
            self.stmt("class {name}({args}):", name=name, args=", ".join(args))
        else:
            self.stmt("class {name}:", name=name)
        with self.scope():
            yield
        self.sep()

    def return_(self, expr: t.Any, *args: t.Any) -> None:
        self.stmt("return %s" % (expr,), *args)

    def import_(self, modname: t.Any, as_: t.Optional[t.Any] = None) -> Symbol:
        name = as_ or modname
        try:
            sym = self.imported_map[name]
            return sym
        except KeyError:
            # todo: considering self.import_unique
            suffix = ""
            if as_ is not None:
                suffix = "{} as {}".format(suffix, as_)

            self.stmt("import {}{}", modname, suffix)
            sym = self.imported_map[name] = Symbol(name)
            return sym

    def from_(self, modname: t.Any, *attrs: t.Any) -> "FromStatement":
        try:
            from_stmt: FromStatement = self.from_map[modname].body.tail()
            for sym in attrs:
                from_stmt.append(sym)
            return from_stmt
        except KeyError:
            from_stmt = FromStatement(modname)
            for sym in attrs:
                from_stmt.append(sym)
            self.from_map[modname] = self.submodule(from_stmt, newline=False)
            return from_stmt


class FromStatement:
    def __init__(self, modname: str, symbols: t.Sequence[str]) -> None:
        self.modname = modname
        self.symbols = list(symbols)

    # TODO: return symbol
    def import_(
        self, symbol: t.Any, *, as_: t.Optional[str] = None
    ) -> Symbol:  # TODO: support as_
        self.symbols.append(symbol)

    def stmt(self, s: str) -> t.Iterable[t.Any]:
        yield s
        yield NEWLINE

    def iterator_for_one_symbol(self, sentence: Sentence) -> t.Iterable[t.Any]:
        if not sentence.is_empty():
            yield NEWLINE
        yield from self.stmt("from {} import {}".format(self.modname, self.symbols[0]))

    def iterator_for_many_symbols(self, sentence: Sentence) -> t.Iterable[t.Any]:
        if not sentence.is_empty():
            yield NEWLINE
        yield from self.stmt("from {} import (".format(self.modname))
        yield INDENT

        symbols = []
        seen = set()
        for x in self.symbols:
            if x in seen:
                continue
            seen.add(x)
            symbols.append(x)

        for sym in symbols[:-1]:
            yield from self.stmt("{},".format(sym))
        if symbols:
            yield from self.stmt("{}".format(symbols[-1]))
        yield UNINDENT
        yield from self.stmt(")")

    def as_token(
        self, lexer: _Lexer, tokens: t.List[t.Any], sentence: Sentence
    ) -> Sentence:
        if not self.symbols:
            return Sentence()

        if len(self.symbols) == 1:
            lexer.loop(tokens, sentence, self.iterator_for_one_symbol(sentence))
        else:
            lexer.loop(tokens, sentence, self.iterator_for_many_symbols(sentence))
        return Sentence()


Module = PythonModule
