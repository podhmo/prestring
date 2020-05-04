import typing as t
from prestring.go import Module as _Module
from prestring.go import ImportGroup, goname
from prestring.codeobject import CodeObjectModuleMixin, Symbol
from prestring.utils import reify

__all__ = ["Module", "Symbol", "gofile", "goname"]


class Module(CodeObjectModuleMixin, _Module):
    assign_op = ":="

    @reify
    def _toplevel_import_area(self) -> ImportGroup:
        with self.import_group() as ig:
            pass
        return ig

    def import_(self, path: str, as_: t.Optional[str] = None) -> Symbol:
        self._toplevel_import_area.import_(path, as_=as_)
        name = as_ or path.rsplit("/", 1)[-1]  # xxx (error in go-sqlite)
        return Symbol(name)


def gofile(name: str) -> Module:
    m = Module()
    m.package(name)
    m.import_("")
    return m
