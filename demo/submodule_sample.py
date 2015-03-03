# -*- coding:utf-8 -*-
from prestring.python import PythonModule

m = PythonModule()

with m.def_("setup", "config"):
    import_area = m.submodule()
    m.sep()
    for k in ["a", "b", "c", "d", "e"]:
        import_area.from_(".plugins", "{}_plugin".format(k))
        m.stmt("config.activate({}_plugin)", k)


print(m)
"""
def setup(config):
    from .plugins import a_plugin
    from .plugins import b_plugin
    from .plugins import c_plugin
    from .plugins import d_plugin
    from .plugins import e_plugin

    config.activate(a_plugin)
    config.activate(b_plugin)
    config.activate(c_plugin)
    config.activate(d_plugin)
    config.activate(e_plugin)
"""
