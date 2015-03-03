# -*- coding:utf-8 -*-
from prestring.python import PythonModule

m = PythonModule()

subm = m.submodule("# this is import area ######")
m.stmt("############################")
m.sep()
m.stmt("do_action()")
m.sep()
m.stmt("use_foo_module()")
subm.stmt("from foo import Foo")
m.sep()
m.stmt("do_action()")


print(m)
"""
# this is import area ######
from foo import Foo
############################

do_action()

use_foo_module()

do_action()
"""
