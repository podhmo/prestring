# -*- coding:utf-8 -*-
from prestring.python import PythonModule

m = PythonModule()

with m.class_("Point", metaclass="InterfaceMeta"):
    with m.def_("__init__", "self", "value"):
        m.stmt("self.value = value")

    with m.def_("__str__", "self"):
        m.return_("self.value")


for n in range(1, 5):
    def rec(i):
        if i >= n:
            m.stmt("r.append(({}))".format(", ".join("x{}".format(j) for j in range(i))))
        else:
            with m.for_("x{}".format(i), "xs{}".format(i)):
                rec(i + 1)
    with m.def_("cross{}".format(n), *["xs{}".format(i) for i in range(n)]):
        m.stmt("r = []")
        rec(0)
        m.return_("r")

print(m)

# output
"""
class Point(object, metaclass=InterfaceMeta)
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


def cross1(xs0):
    r = []
    for x0 in xs0:
        r.append((x0))
    return r


def cross2(xs0, xs1):
    r = []
    for x0 in xs0:
        for x1 in xs1:
            r.append((x0, x1))
    return r


def cross3(xs0, xs1, xs2):
    r = []
    for x0 in xs0:
        for x1 in xs1:
            for x2 in xs2:
                r.append((x0, x1, x2))
    return r


def cross4(xs0, xs1, xs2, xs3):
    r = []
    for x0 in xs0:
        for x1 in xs1:
            for x2 in xs2:
                for x3 in xs3:
                    r.append((x0, x1, x2, x3))
    return r
"""
