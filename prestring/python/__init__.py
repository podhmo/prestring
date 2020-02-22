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
from prestring.utils import (
    LazyArguments,
    LazyFormat,
    LazyArgumentsAndKeywords,
    LazyJoin,
)
from prestring.utils import _type_value  # xxx

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
        import_unique: bool = False,
        **kwargs: t.Any,
    ) -> None:
        self.width = width
        self.import_unique = import_unique
        super().__init__(
            value, newline, indent, lexer=lexer, parser=parser, application=application
        )
        self.from_map: t.Dict[str, PythonModule] = {}  # module -> PythonModule
        self.imported_set: t.Set[str] = set()

    def submodule(
        self,
        value: t.Any = "",  # str,FromStatement,...
        newline: bool = True,
        factory: t.Optional[t.Callable[..., _ModuleT]] = None,
        *,
        import_unique: t.Optional[bool] = None,
    ) -> _ModuleT:
        submodule = t.cast(
            PythonModule,
            super().submodule(value=value, newline=newline, factory=factory,),
        )  # xxx
        submodule.width = self.width
        if import_unique is None:
            import_unique = self.import_unique
        submodule.import_unique = import_unique
        return submodule  # type:ignore

    def create_evaulator(self) -> PythonEvaluator:
        return PythonEvaluator(StringIO(), newline=self.newline, indent=self.indent)

    def sep(self) -> None:
        self.body.append(PEPNEWLINE)

    @contextlib.contextmanager
    def with_(self, expr: t.Any, as_: t.Optional[t.Any] = None) -> t.Iterator[None]:
        if as_:
            self.stmt("with {} as {}:", expr, as_)
        else:
            self.stmt("with {}:", expr)
        with self.scope():
            yield

    @contextlib.contextmanager
    def def_(
        self,
        name: str,
        *args: t.Any,
        return_type: t.Optional[t.Any] = None,
        **kwargs: t.Any,
    ) -> t.Iterator[None]:
        params = make_params(args, kwargs)
        if return_type is not None:
            self.stmt("def {}({}) -> {}:", name, params, _type_value(return_type))
        else:
            self.stmt("def {}({}):", name, params)
        with self.scope():
            yield
        self.sep()

    @contextlib.contextmanager
    def method(
        self,
        name: str,
        *args: t.Any,
        return_type: t.Optional[t.Any] = None,
        **kwargs: t.Any,
    ) -> t.Iterator[None]:
        params = LazyJoin(", ", ["self", make_params(args, kwargs)], trim_empty=True)
        if return_type is not None:
            self.stmt("def {}({}) -> {}:", name, params, _type_value(return_type))
        else:
            self.stmt("def {}({}):", name, params)
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
    def for_(self, var: t.Any, iterator: t.Optional[t.Any] = None) -> t.Iterator[None]:
        if iterator is None:
            self.stmt("for {var}:", var=var)
        else:
            self.stmt("for {var} in {iterator}:", var=var, iterator=iterator)
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

    @contextlib.contextmanager
    def main(self) -> t.Iterator[None]:
        with self.if_('__name__ == "__main__"'):
            yield

    # sentence
    def break_(self) -> None:
        self.stmt("break")

    def continue_(self) -> None:
        self.stmt("continue")

    def return_(self, expr: t.Any, *args: t.Any) -> None:
        self.stmt("return %s" % (expr,), *args)

    def yield_(self, expr: t.Any, *args: t.Any) -> None:
        self.stmt("yield %s" % (expr,), *args)

    def raise_(self, expr: t.Any, *args: t.Any) -> None:
        self.stmt("raise %s" % (expr,), *args)

    def import_(self, modname: t.Any, as_: t.Optional[t.Any] = None) -> None:
        if modname in self.imported_set:
            return
        self.imported_set.add(modname)
        # todo: considering self.import_unique
        if as_ is None:
            self.stmt("import {}", modname)
        else:
            self.stmt("import {} as {}", modname, as_)

    def from_(self, modname: t.Any, *attrs: t.Any) -> "FromStatement":
        try:
            self.imported_set.add(modname)
            from_stmt: FromStatement = self.from_map[modname].body.tail()
            for sym in attrs:
                from_stmt.append(sym)
        except KeyError:
            from_stmt = FromStatement(modname, attrs, unique=self.import_unique)
            self.from_map[modname] = self.submodule(from_stmt, newline=False)
        return from_stmt

    def call(self, name_: t.Any, *args: t.Any) -> None:
        oneline = LazyFormat("{}({})", name_, LazyArguments(list(args)))
        if len(str(oneline._string())) <= self.width:
            self.stmt(oneline)
        else:
            self.body.append(MultiSentenceForCall(name_, *args))

    def pass_(self) -> None:
        self.stmt("pass")


class FromStatement:
    def __init__(
        self, modname: str, symbols: t.Sequence[str], unique: bool = False
    ) -> None:
        self.modname = modname
        self.symbols = list(symbols)
        self.unique = unique

    def append(self, symbol: t.Any) -> None:  # TODO: support as_
        self.symbols.append(symbol)

    import_ = append  # alias

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
        if self.unique:
            symbols = sorted(set(self.symbols))
        else:
            symbols = self.symbols
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


class MultiSentenceForCall:
    def __init__(self, name: str, *lines: str) -> None:
        self.name = name
        self.lines = lines

    def iterator(self, sentence: Sentence) -> t.Iterator[t.Any]:
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

    def as_token(
        self, lexer: _Lexer, tokens: t.List[str], sentence: Sentence
    ) -> Sentence:
        lexer.loop(tokens, sentence, self.iterator(sentence))
        return Sentence()


Module = PythonModule
