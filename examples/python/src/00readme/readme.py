from prestring.python import PythonModule

m = PythonModule()

with m.class_("Point", metaclass="InterfaceMeta"):
    with m.def_("__init__", "self", "value"):
        m.stmt("self.value = value")

    with m.def_("__str__", "self"):
        m.return_("self.value")
print(m)
