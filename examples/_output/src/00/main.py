import logging
from prestring.python import Module
from prestring.output import output, cleanup_all # noqa

logging.basicConfig(level=logging.DEBUG)

with output(root="dst/00", fake=False, verbose=True) as fs:
    with fs.open("projects/x.txt", "w") as wf:
        print("hello x", file=wf)
        print("bye x", file=wf)

    with fs.open("projects/y.txt", "w") as wf:
        print("hello y", file=wf)
        print("bye y", file=wf)

    with fs.open("projects/z.py", "w", opener=Module) as m:
        with m.def_("hello"):
            m.stmt("print('hello')")
