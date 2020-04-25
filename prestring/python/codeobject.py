from prestring.python import Module as _Module
from prestring.codeobject import CodeObjectModuleMixin, Symbol


__all__ = ["Module", "Symbol"]


class Module(CodeObjectModuleMixin, _Module):
    assign_op = "="
