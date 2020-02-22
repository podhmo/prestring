from prestring.python import Module

m = Module()
with m.def_("add", "x: int", "y: int=0", return_type="int"):
    m.return_("x + y")
print(m)
