import typing as t
import contextlib
import logging
import re
import warnings
from prestring import Module as _Module
from prestring.naming import titleize
from prestring import (
    NEWLINE,
    INDENT,
    UNINDENT,
    Sentence as Sentence,
    Lexer as _Lexer,
)

from prestring.utils import (
    LazyArguments,
    LazyFormat,
    LazyJoin,
)
from prestring.types import StrOrStringer

logger = logging.getLogger(__name__)
GoModuleT = t.TypeVar("GoModuleT", bound="GoModule")
GroupT = t.TypeVar("GroupT", bound="Group")


# TODO: remove import_group, const_group
class GoModule(_Module):
    def __init__(
        self,
        value: str = "",
        *,
        newline: str = "\n",
        indent: str = "\t",
        **kwargs: t.Any,
    ) -> None:
        super().__init__(value, newline=newline, indent=indent, **kwargs)

    def sep(self) -> None:
        self.body.append(NEWLINE)

    @contextlib.contextmanager
    def block(
        self,
        value: t.Union[None, str, LazyFormat] = None,
        *,
        end: str = "}",
        surround: bool = True,
    ) -> t.Iterator[None]:
        if value is None:
            self.stmt("{")
        else:
            self.body.append(value)
            self.body.append(" {")
            self.body.append(NEWLINE)
        with self.scope():
            yield
        if not end.startswith("}") and surround:
            end = "}" + end
        self.stmt(end)

    def comment(self, comment: StrOrStringer) -> None:
        self.stmt(LazyFormat("// {}", comment))

    def package(self, name: str) -> None:
        self.stmt("package {}".format(name))
        self.sep()

    def return_(self, name: StrOrStringer) -> None:
        self.stmt(LazyFormat("return {}", name))

    def new_type(self, name: str, value: t.Any) -> None:
        self.stmt(LazyFormat("type {} {}", name, value))
        self.sep()

    def type_alias(self, name: str, value: t.Any) -> None:
        self.stmt(LazyFormat("type {} = {}", name, value))
        self.sep()

    @contextlib.contextmanager
    def type_(self, name: t.Optional[str], *args: t.Any) -> t.Iterator[None]:
        with self.block(LazyFormat("type {} {}", name, LazyJoin(" ", list(args)))):
            yield
        self.sep()

    @contextlib.contextmanager
    def struct(self, name: str) -> t.Iterator[None]:
        with self.type_(name, "struct"):
            yield

    @contextlib.contextmanager
    def func(
        self, name: str, *args: t.Any, returns: str = "", return_: str = ""
    ) -> t.Iterator[None]:
        if return_:
            warnings.warn(
                "return_ option is deprecated. use returns", stacklevel=3,
            )
            returns = returns or return_

        if returns:
            returns = " " + returns.lstrip("")

        with self.block(
            LazyFormat("func {}({}){}", name, LazyArguments(list(args)), returns)
        ):
            yield
        self.sep()

    @contextlib.contextmanager
    def method(
        self, ob: str, name: str, *args: t.Any, returns: str = "", return_: str = ""
    ) -> t.Iterator[None]:
        if return_:
            warnings.warn(
                "return_ option is deprecated. use returns", stacklevel=3,
            )
            returns = returns or return_

        if returns:
            returns = " " + returns.lstrip("")

        with self.block(
            LazyFormat(
                "func ({}) {}({}){}", ob, name, LazyArguments(list(args)), returns
            )
        ):
            yield
        self.sep()

    @contextlib.contextmanager
    def if_(self, cond: str, *args: t.Any, **kwargs: t.Any) -> t.Iterator[None]:
        with self.block(LazyFormat("if " + cond + " ", *args, *kwargs)):
            yield

    @contextlib.contextmanager
    def elif_(self, cond: str, *args: t.Any, **kwargs: t.Any) -> t.Iterator[None]:
        self.unnewline()
        with self.block(LazyFormat(" else if" + cond + " ", *args, **kwargs)):
            yield

    @contextlib.contextmanager
    def for_(self, cond: str, *args: t.Any, **kwargs: t.Any) -> t.Iterator[None]:
        with self.block(LazyFormat("for " + cond + " ", *args, *kwargs)):
            yield

    @contextlib.contextmanager
    def else_(self) -> t.Iterator[None]:
        self.unnewline()
        with self.block(" else "):
            yield

    def select(self) -> "MultiBranchClause":
        m: GoModule = self.submodule("select", newline=False)
        return MultiBranchClause(m)

    def switch(self, cond: str) -> "MultiBranchClause":
        m: GoModule = self.submodule(LazyFormat("switch {}", cond), newline=False)
        return MultiBranchClause(m)

    def import_group(self) -> "ImportGroup":
        return ImportGroup(self, prefix="import")

    def const_group(self) -> "Group":
        return Group(self, prefix="const")


class MultiBranchClause:
    def __init__(self, m: GoModuleT) -> None:
        self.m = m

    def __getattr__(self, name: str) -> t.Any:
        return getattr(self.m, name)

    def __enter__(self) -> "MultiBranchClause":
        self.m.stmt(" {")
        return self

    @contextlib.contextmanager
    def case(self, value: t.Any) -> t.Iterator[GoModuleT]:
        self.m.stmt("case {}:".format(value))
        with self.m.scope():
            yield self.m

    def __exit__(
        self,
        exc: t.Optional[t.Type[BaseException]],
        value: t.Optional[BaseException],
        tb: t.Any,
    ) -> None:
        self.m.stmt("}")
        self.m.sep()

    @contextlib.contextmanager
    def default(self) -> t.Iterator[GoModuleT]:
        self.m.stmt("default:")
        with self.m.scope():
            yield self.m


class Group:
    def __init__(self, m: GoModule, *, prefix: StrOrStringer) -> None:
        self.m = m
        self.prefix = prefix
        self.outermodule: t.Optional[GoModule] = None
        self.innermodule: t.Optional[GoModule] = None
        self.added: t.Set[t.Any] = set()

    def __getattr__(self, name: str) -> t.Any:
        return getattr(self.outermodule, name)

    def __enter__(self: GroupT) -> GroupT:
        m = self.outermodule = self.m.submodule(
            self.prefix, newline=False, on_lex=self.on_lex
        )
        m.stmt(" (")
        m.body.append(INDENT)
        self.innermodule = m.submodule("", newline=False)
        return self

    def __call__(self, name: str) -> None:
        if name in self.added:
            return
        self.added.add(name)
        assert self.innermodule is not None
        self.innermodule.stmt(name)

    def __exit__(
        self,
        exc: t.Optional[t.Type[BaseException]],
        value: t.Optional[BaseException],
        tb: t.Any,
    ) -> None:
        m = self.outermodule
        assert m is not None
        m.body.append(UNINDENT)
        m.stmt(")")
        m.sep()

    def on_lex(
        self, lexer: _Lexer, tokens: t.List[t.Any], sentence: Sentence
    ) -> t.List[t.Any]:
        if self.outermodule is None or str(self.innermodule) == "":
            return tokens
        return lexer.lex(self.outermodule.body, tokens=tokens)


class ImportGroup(Group):
    def import_(self, name: str, as_: t.Optional[str] = None) -> None:
        if not name:
            return

        pair = (name, as_)
        if pair in self.added:
            return
        self.added.add(pair)
        assert self.innermodule is not None

        if as_ is None:
            self.innermodule.stmt('"{}"'.format(name))
        else:
            self.innermodule.stmt('{} "{}"'.format(as_, name))

    __call__ = import_


Module = GoModule


class NameFormatter:
    def format(
        self,
        s: str,
        num_rx: t.Pattern[str] = re.compile(r"\d{2,}"),
        exclude_rx: t.Pattern[str] = re.compile(
            r"[^a-z0-9]", re.IGNORECASE | re.MULTILINE
        ),
    ) -> str:
        if not s:
            return ""
        elif num_rx.match(s):
            return self.format("Num" + s)
        elif s[0] in self.NUMBERS:
            return self.format(self.NUMBERS[s[0]] + s[1:])
        else:
            return exclude_rx.sub("", self.proper_acronym(s))

    def proper_acronym(
        self,
        s: str,
        rx: t.Pattern[str] = re.compile(r"(?P<sep>^|[^a-zA-Z])(?P<frag>[a-z]+)", re.M),
        rx2: t.Pattern[str] = re.compile(r"(?P<sep>[A-Z])(?P<frag>[a-z]+)", re.M),
    ) -> str:
        return rx2.sub(self._proper_repl2, rx.sub(self._proper_repl1, s))

    NUMBERS = {
        "0": "Zero_",
        "1": "One_",
        "2": "Two_",
        "3": "Three_",
        "4": "Four_",
        "5": "Five_",
        "6": "Six_",
        "7": "Seven_",
        "8": "Eight_",
        "9": "Nine_",
    }

    # https://github.com/golang/lint/blob/39d15d55e9777df34cdffde4f406ab27fd2e60c0/lint.go#L695-L731
    COMMON_INITIALISMS = [
        "API",
        "ASCII",
        "CPU",
        "CSS",
        "DNS",
        "EOF",
        "GUID",
        "HTML",
        "HTTP",
        "HTTPS",
        "ID",
        "IP",
        "JSON",
        "LHS",
        "QPS",
        "RAM",
        "RHS",
        "RPC",
        "SLA",
        "SMTP",
        "SSH",
        "TCP",
        "TLS",
        "TTL",
        "UDP",
        "UI",
        "UID",
        "UUID",
        "URI",
        "URL",
        "UTF8",
        "VM",
        "XML",
        "XSRF",
        "XSS",
    ]

    def _proper_repl1(self, m: t.Match[str]) -> str:
        d = m.groupdict()
        if d["frag"].upper() in self.COMMON_INITIALISMS:
            return d["sep"] + d["frag"].upper()
        else:
            return d["sep"] + titleize(d["frag"])

    def _proper_repl2(self, m: t.Match[str]) -> str:
        d = m.groupdict()
        merged = d["sep"] + d["frag"]
        if merged.upper() in self.COMMON_INITIALISMS:
            return merged.upper()
        else:
            return merged


def goname(s: str, formatter: NameFormatter = NameFormatter()) -> str:
    return formatter.format(s)
