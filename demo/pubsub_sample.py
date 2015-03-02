# -*- coding:utf-8 -*-
from prestring.python import PythonModule

m = PythonModule()

pub = m.stmt("# this is import area ######")
m.stmt("############################")
m.sep()
m.stmt("do_action()")
m.sep()
m.stmt("use_foo_module()")
pub.stmt("from foo import Foo")
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
