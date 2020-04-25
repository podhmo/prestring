from prestring.go import Module as _Module
from prestring.codeobject import CodeObjectModuleMixin


class Module(CodeObjectModuleMixin, _Module):
    assign_op = ":="
