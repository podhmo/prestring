import contextlib
import logging
from .. import Module as _Module
from .. import NEWLINE
from ..utils import (
    LazyCall,
    LazyFormat,
    UnRepr,
)
logger = logging.getLogger(__name__)


class JSModule(_Module):
    def __init__(self, *args, autosemicolon=True, **kwargs):
        if "indent" not in kwargs:
            kwargs["indent"] = "  "
        self.semicolon = ";" if autosemicolon else ""
        super(JSModule, self).__init__(*args, **kwargs)

    def sep(self):
        self.body.append(NEWLINE)

    def stmt(self, fmt, *args, semicolon=None, **kwargs):
        if semicolon is None:
            semicolon = self.semicolon
        fmt = LazyFormat("{}{}", fmt, semicolon)
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

    def if_(self, header):
        """
        if (<header>) {
          ...
        }
        """
        return block_for_sematics(self, LazyFormat("if ({})", header), end="}", semicolon="")

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
                stmt = str(subm.body.pop())
                subm.body.append(stmt.rstrip(","))
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
