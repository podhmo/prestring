import typing as t
import contextlib
import logging
import re
from prestring import Module as _Module
from prestring.naming import titleize
from prestring import (
    NEWLINE,
    INDENT,
    UNINDENT,
    Lexer as _Lexer,
    Parser as _Parser,
    Application as _Application,
)

from prestring.utils import (
    LazyArguments,
    LazyFormat,
    LazyJoin,
)

logger = logging.getLogger(__name__)


# TODO: remove import_group, const_group
class GoModule(_Module):
    def __init__(
        self,
        value: str = "",
        newline: str = "\n",
        indent: str = "\t",
        lexer: t.Optional[_Lexer] = None,
        parser: t.Optional[_Parser] = None,
        application: t.Optional[_Application] = None,
        **kwargs: t.Any,
    ) -> None:
        super().__init__(
            value, newline, indent, lexer=lexer, parser=parser, application=application
        )

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

    def comment(self, comment: str) -> None:
        self.stmt(LazyFormat("// {}", comment))

    def package(self, name: str) -> None:
        self.stmt("package {}".format(name))
        self.sep()

    def return_(self, name: str) -> None:
        self.stmt(LazyFormat("return {}", name))

    def type_alias(self, name: str, value: t.Any) -> None:
        self.stmt(LazyFormat("type {} {}", name, value))
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
    def func(self, name: str, *args: t.Any, return_: str = "") -> t.Iterator[None]:
        with self.block(
            LazyFormat("func {}({}) {}", name, LazyArguments(list(args)), return_)
        ):
            yield
        self.sep()

    @contextlib.contextmanager
    def method(
        self, ob: str, name: str, *args: t.Any, return_: str = ""
    ) -> t.Iterator[None]:
        with self.block(
            LazyFormat(
                "func ({}) {}({}) {}", ob, name, LazyArguments(list(args)), return_
            )
        ):
            yield
        self.sep()

    @contextlib.contextmanager
    def if_(self, cond: str) -> t.Iterator[None]:
        with self.block(LazyFormat("if {} ", cond)):
            yield

    @contextlib.contextmanager
    def elif_(self, cond: str) -> t.Iterator[None]:
        self.unnewline()
        with self.block(LazyFormat(" else if {} ", cond)):
            yield

    @contextlib.contextmanager
    def for_(self, cond: str) -> t.Iterator[None]:
        with self.block(LazyFormat("for {} ", cond)):
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
        m: GoModule = self.submodule("import", newline=False)
        return ImportGroup(m)

    def const_group(self) -> "Group":
        m: GoModule = self.submodule("const", newline=False)
        return Group(m)


class MultiBranchClause:
    def __init__(self, m: GoModule) -> None:
        self.m = m

    def __getattr__(self, name: str) -> t.Any:
        return getattr(self.m, name)

    def __enter__(self) -> "MultiBranchClause":
        self.m.stmt(" {")
        return self

    @contextlib.contextmanager
    def case(self, value: t.Any) -> t.Iterator[GoModule]:
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
    def default(self) -> t.Iterator[GoModule]:
        self.m.stmt("default:")
        with self.m.scope():
            yield self.m


class Group:
    def __init__(self, m: GoModule) -> None:
        self.m = m
        self.submodule: t.Optional[GoModule] = None
        self.added: t.Set[t.Any] = set()

    def __getattr__(self, name: str) -> t.Any:
        return getattr(self.m, name)

    def __enter__(self) -> "Group":
        self.m.stmt(" (")
        self.m.body.append(INDENT)
        self.submodule = self.m.submodule("", newline=False)
        return self

    def __call__(self, name: str) -> None:
        if name in self.added:
            return
        self.added.add(name)
        assert self.submodule is not None
        self.submodule.stmt(name)

    def clear_ifempty(self) -> None:
        if self.submodule is None or str(self.submodule) == "":
            self.m.clear()

    def __exit__(
        self,
        exc: t.Optional[t.Type[BaseException]],
        value: t.Optional[BaseException],
        tb: t.Any,
    ) -> None:
        self.m.body.append(UNINDENT)
        self.m.stmt(")")
        self.m.sep()


class ImportGroup(Group):
    def import_(self, name: str, as_: t.Optional[str] = None) -> None:
        pair = (name, as_)
        if pair in self.added:
            return
        self.added.add(pair)
        assert self.submodule is not None
        if as_ is None:
            self.submodule.stmt('"{}"'.format(name))
        else:
            self.submodule.stmt('{} "{}"'.format(as_, name))

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
