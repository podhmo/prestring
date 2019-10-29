# -*- coding:utf-8 -*-
from prestring.python import PythonModule

m = PythonModule()


def fizzbuzz(i):
    r = []
    if i % 3 == 0:
        r.append("fizz")
    if i % 5 == 0:
        r.append("buzz")
    return "".join(r) if r else i


def genfizzbuzz(m, beg, end):
    def genfn():
        with m.def_("fizzbuzz", "n"):
            with m.if_("n == {}".format(beg)):
                m.return_(repr(fizzbuzz(beg)))

            for i in range(beg + 1, end + 1):
                with m.elif_("n == {}".format(i)):
                    m.return_(repr(fizzbuzz(i)))

            with m.else_():
                m.raise_("NotImplementedError('hmm')")

    def genmain():
        with m.main():
            m.import_("sys")
            m.stmt("print(fizzbuzz(int(sys.argv[1])))")

    genfn()
    genmain()
    return m


if __name__ == "__main__":
    import sys

    try:
        beg, end = sys.argv[1:]
    except ValueError:
        beg, end = 1, 100
    m = PythonModule()
    print(genfizzbuzz(m, int(beg), int(end)))
