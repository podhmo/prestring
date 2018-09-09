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
    symbol = var = staticmethod(UnRepr)

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

    def if_(self, condition):
        return Block(self).if_(condition)

    brace = block

    def comment(self, comment):
        self.stmt(LazyFormat("// {}", comment))


class Block:
    def __init__(self, m):
        self.m = m

    def chain(self, header):
        subm = self.m.submodule(newline=True)
        subm.semicolon = ""  # disabled
        self.m = subm  # xxx: side-effect
        return self._chain(header)

    @contextlib.contextmanager
    def _chain(self, header):
        m = self.m
        m.body.append(header)
        m.body.append(NEWLINE)
        with m.scope():
            yield m
            m.unnewline()
            m.stmt(";")

    def object(self, header, *, semicolon=";"):
        """
        <header> {
          <arg0>,
          <arg1>,
          ...
          <argN>
        };
        """
        # todo: rename
        return self._call_block(header, end="}", semicolon=semicolon)

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
        return self._call_block(header, end="})", semicolon=semicolon)

    @contextlib.contextmanager
    def _call_block(self, header, *, end="})", semicolon=";"):
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

    def if_(self, header):
        return self._block(LazyFormat("if ({})", header), end="}", semicolon="")

    @contextlib.contextmanager
    def _block(self, value=None, *, end="}", semicolon=None):
        m = self.m
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
