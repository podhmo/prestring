# -*- coding:utf-8 -*-
from prestring.python import PythonModule

m = PythonModule()

for n in range(1, 5):

    def rec(i):
        if i >= n:
            m.stmt(
                "r.append(({}))".format(", ".join("x{}".format(j) for j in range(i)))
            )
        else:
            with m.for_("x{}".format(i), "xs{}".format(i)):
                rec(i + 1)

    with m.def_("cross{}".format(n), *["xs{}".format(i) for i in range(n)]):
        m.stmt("r = []")
        rec(0)
        m.return_("r")

print(m)
