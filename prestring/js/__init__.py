import contextlib
import logging
from .. import Module as _Module
from .. import (
    NEWLINE,
    LazyFormat,
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
        if semicolon and not fmt.endswith(semicolon):
            fmt = LazyFormat("{}{}", fmt, semicolon)
        return super().stmt(fmt, *args, **kwargs)

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

    def call(self, header):
        return self._block(header, end="});")

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
