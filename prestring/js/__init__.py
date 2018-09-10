import contextlib
import logging
from .. import Module as _Module
from .. import NEWLINE
from ..utils import (
    LazyCall,
    LazyFormat,
    LazyRStrip,
    LazyArgumentsAndKeywords,
    UnRepr,
)
logger = logging.getLogger(__name__)


def make_params(args, kwargs):
    if not kwargs and len(args) == 1 and hasattr(args[0], "append_tail"):
        return args[0]
    return LazyArgumentsAndKeywords(args, kwargs)


class JSModule(_Module):
    def __init__(self, *args, autosemicolon=True, **kwargs):
        if "indent" not in kwargs:
            kwargs["indent"] = "  "
        self.semicolon = ";" if autosemicolon else ""
        super(JSModule, self).__init__(*args, **kwargs)

    def sep(self):
        self.body.append(NEWLINE)

    def stmt(self, fmt, *args, semicolon=None, comment=None, **kwargs):
        if semicolon is None:
            semicolon = self.semicolon
        fmt = LazyFormat("{}{}", fmt, semicolon)
        if comment is not None:
            fmt = LazyFormat("{} // {}", fmt, comment)
        return super().stmt(fmt, *args, **kwargs)

    __call__ = stmt
    call = staticmethod(LazyCall)
    symbol = var = staticmethod(UnRepr)  # hmm

    def assign(self, lhs, rhs):
        self.stmt(LazyFormat("{} = {}", lhs, rhs))

    def return_(self, stmt=None):
        if not stmt:
            self.stmt("return")
        else:
            return self.stmt("return {}".format(stmt))

    @property
    def block(self):
        return Block(self)

    brace = block  # hmm

    def if_(self, condition):
        """
        if (<condition>) {
          ...
        }
        """
        return block_for_sematics(self, LazyFormat("if ({})", condition), end="}", semicolon="")

    def else_(self):
        """
        else {
          ...
        }
        """
        return block_for_sematics(self, "else", end="}", semicolon="")

    def else_if(self, condition):
        """
        else if (<condition>) {
          ...
        }
        """
        return block_for_sematics(
            self, LazyFormat("else if ({})", condition), end="}", semicolon=""
        )

    elif_ = else_if

    def class_(self, name, extends=None):
        """
        class <name> {
          ...
        }
        """
        if extends is None:
            return block_for_sematics(self, LazyFormat("class {}", name), end="}", semicolon="\n")
        else:
            return block_for_sematics(
                self, LazyFormat("class {} extends {}", name, extends), end="}", semicolon="\n"
            )

    def method(self, name, *args, **kwargs):
        """
        <name>(<params>) {
          ...
        }
        """
        return block_for_sematics(
            self, LazyFormat("{}({})", name, make_params(args, kwargs)), end="}", semicolon="\n"
        )

    def comment(self, comment):
        self.stmt(LazyFormat("// {}", comment))


class Block:
    def __init__(self, m):
        self.m = m

    @contextlib.contextmanager
    def chain(self, header):
        """
        <header>
          .<chain0>
          .<chain1>
          ...
          .<chainN>;
        """
        m = self.m.submodule(newline=True)
        m.semicolon = ""  # disabled
        m.body.append(header)
        m.body.append(NEWLINE)
        with m.scope():
            yield m
            m.unnewline()
            m.stmt(";")

    def call(self, header, *, semicolon=";"):
        """
        <header> {
          <arg0>,
          <arg1>,
          ...
          <argN>
        });
        """
        # todo: rename
        return self.brace(header, end="})", semicolon=semicolon)

    @contextlib.contextmanager
    def __call__(self, header, *, end="}", semicolon=";"):
        """
        <header> {
          <arg0>,
          <arg1>,
          ...
          <argN>
        };
        """
        m = self.m
        m.body.append(header)
        m.body.append(" {")
        m.body.append(NEWLINE)
        with m.scope():
            subm = self.m.submodule(newline=False)
            subm.semicolon = ","
            yield subm
            if not subm.body.is_empty:
                subm.unnewline()
                subm.body.append(LazyRStrip(subm.body.pop(), ","))
                subm.body.append(NEWLINE)
        m.stmt(end, semicolon=semicolon)


@contextlib.contextmanager
def block_for_sematics(m, value=None, *, end="}", semicolon=None):
    if value is None:
        m.stmt("{")
    else:
        m.body.append(value)
        m.body.append(" {")
        m.body.append(NEWLINE)
    with m.scope():
        yield
    m.stmt(end, semicolon=semicolon)


Module = JSModule
