from prestring import INDENT, UNINDENT
from prestring.text import Module


def transform(source: str, *, indent, m=None):
    if m is None:
        m = Module(indent=indent)
        m.g = m.submodule()

    history = [0]

    for line in source.splitlines():
        if line == "":
            m.stmt("m.sep()")
            continue

        lv = 0
        while line.startswith(indent):
            lv += 1
            line = line[len(indent) :]  # noqa E203

        prev_lv = history[-1]
        history.append(lv)
        while prev_lv < lv:
            m.stmt("with m.scope():")
            m.append(INDENT)
            lv -= 1
        while prev_lv > lv:
            m.append(UNINDENT)
            lv += 1

        if line == "":
            m.stmt("m.sep()")
        else:
            m.stmt("m.stmt({!r})", line)
    return m


if __name__ == "__main__":
    import sys
    from prestring.cli import main_transform
    from prestring.python import Module as PyModule

    main_transform(
        Module=PyModule,
        OutModule=Module,
        transform=transform,
        argv=sys.argv[1:] or [__file__],
    )
