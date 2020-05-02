import typing as t
import contextlib
import warnings
from io import StringIO
from prestring import Module as _Module
from prestring import ModuleT
from prestring import (
    StmtTargetType,
    _Sentinel,
    NEWLINE,
    INDENT,
    UNINDENT,
    Sentence as Sentence,
    Evaluator as _Evaluator,
    Lexer as _Lexer,
)
from prestring import ModuleT as _ModuleT
from prestring.utils import LazyArgumentsAndKeywords, LazyFormat
from prestring.utils import _type_value  # xxx
from prestring.codeobject import Symbol

PEPNEWLINE = _Sentinel(name="PEP-NEWLINE", kind="sep")


class PythonEvaluator(_Evaluator):
    def do_newframe(self) -> None:
        self.io.write(self.newline)
        self.io.write(self.newline)

    def do_newline(self, code: t.Any, i: int) -> None:
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
        *,
        newline: str = "\n",
        indent: str = "    ",
        width: int = 100,
        import_unique: t.Optional[bool] = None,
        **kwargs: t.Any,
    ) -> None:
        if import_unique is not None:
            warnings.warn("import_unique is omitted. ignored", stacklevel=2)

        self.width = width
        super().__init__(value, newline=newline, indent=indent, **kwargs)
        self.from_map: t.Dict[str, PythonModule] = {}  # module -> PythonModule
        self.imported_map: t.Dict[str, Symbol] = {}

    def submodule(
        self,
        value: t.Any = "",  # str,FromStatement,...
        *,
        newline: bool = True,
        factory: t.Optional[t.Callable[..., "PythonModule"]] = None,
        on_lex: t.Optional[
            t.Callable[[_Lexer, t.List[t.Any], Sentence], t.List[t.Any]]
        ] = None,
    ) -> _ModuleT:
        submodule = super().submodule(
            value=value, newline=newline, factory=factory, on_lex=on_lex
        )
        submodule.width = self.width
        return submodule  # type: ignore

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
    ) -> t.Iterator[Symbol]:
        params = make_params(args, kwargs)

        prefix = f"{'async ' if async_ else ''}def"
        if return_type is not None:
            self.stmt(
                "{} {}({}) -> {}:", prefix, name, params, _type_value(return_type)
            )
        else:
            self.stmt("{} {}({}):", prefix, name, params)
        with self.scope():
            yield Symbol(name)
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
    ) -> t.Iterator[Symbol]:
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
            yield Symbol(var)

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
    ) -> t.Iterator[Symbol]:
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
            yield Symbol(name)
        self.sep()

    def stmt(self, fmt: StmtTargetType, *args: t.Any, **kwargs: t.Any,) -> "ModuleT":
        await_ = kwargs.pop("await_", False)
        if not await_:
            return super().stmt(fmt, *args, **kwargs)  # type: ignore
        return super().stmt(LazyFormat("await {}", fmt), *args, **kwargs)  # type: ignore

    def return_(self, expr: t.Any, *args: t.Any, await_: bool = False) -> None:
        prefix = f"return {'await ' if await_ else ''}"
        self.stmt("{}{}", prefix, str(expr).format(*args))

    def import_(self, modname: str, as_: t.Optional[str] = None) -> Symbol:
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
            sym = self.imported_map[name] = Symbol(modname, as_=as_)
            return sym

    def from_(self, modname: str, *attrs: str) -> "FromStatement":
        try:
            from_stmt: FromStatement = self.from_map[modname].body.tail()
            for sym in attrs:
                from_stmt.import_(sym)
            return from_stmt
        except KeyError:
            from_stmt = FromStatement(modname)
            for sym in attrs:
                from_stmt.import_(sym)
            self.from_map[modname] = self.submodule(from_stmt, newline=False)
            return from_stmt


class FromStatement:
    def __init__(self, modname: str) -> None:
        self.modname = modname
        self.symbols: t.Dict[str, Symbol] = {}

    def import_(self, name: str, *, as_: t.Optional[str] = None) -> Symbol:
        sym = self.symbols.get(as_ or name)
        if sym is not None:
            return sym
        sym = self.symbols[as_ or name] = Symbol(name, as_=as_)
        return sym

    def iterator_for_one_symbol(self, sentence: Sentence) -> t.Iterable[t.Any]:
        if not sentence.is_empty():
            yield NEWLINE
        sym = next(iter(self.symbols.values()))
        suffix = ""
        if sym.as_ is not None:
            suffix = " as {}".format(sym.as_)
        yield "from {} import {}{}".format(self.modname, sym.name, suffix)
        yield NEWLINE

    def iterator_for_many_symbols(self, sentence: Sentence) -> t.Iterable[t.Any]:
        if not sentence.is_empty():
            yield NEWLINE
        yield "from {} import (".format(self.modname)
        yield NEWLINE

        yield INDENT

        for sym in self.symbols.values():
            suffix = ""
            if sym.as_ is not None:
                suffix = " as {}".format(sym.as_)
            yield "{}{},".format(sym.name, suffix)
            yield NEWLINE

        yield UNINDENT

        yield ")"
        yield NEWLINE

    def on_lex(
        self, lexer: _Lexer, tokens: t.List[t.Any], sentence: Sentence
    ) -> t.List[t.Any]:
        if not self.symbols:
            return tokens

        if len(self.symbols) == 1:
            return lexer.lex(self.iterator_for_one_symbol(sentence), tokens=tokens)
        else:
            return lexer.lex(self.iterator_for_many_symbols(sentence), tokens=tokens)


Module = PythonModule
