from prestring.utils import LazyFormat


def main_transform(*, transform, Module, argv=None, name="gen", OutModule):
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--tab", action="store_true")
    parser.add_argument("--indent", default=4, type=int)
    args = parser.parse_args(argv)
    indent = ("\t" if args.tab else " ") * args.indent

    m = run_transform(
        args.file,
        transform=transform,
        Module=Module,
        name=name,
        OutModule=OutModule,
        indent=indent,
    )
    print(str(m))


def run_transform(filename: str, *, transform, Module, name="gen", OutModule, indent):
    m = Module()
    m.g = m.submodule()
    m.g.stmt("from {} import {}", OutModule.__module__, OutModule.__name__)
    m.sep()

    with m.def_(name, "*", "m=None", LazyFormat("indent={!r}", indent)):
        m.stmt("""m = m or {}(indent=indent)""", OutModule.__name__)
        m.sep()
        with open(filename) as rf:
            text = rf.read()
        m = transform(text, m=m, indent=indent)
        m.return_("m")

    with m.if_('__name__ == "__main__"'):
        m.stmt("m = {}(indent={!r})", name, indent)
        m.stmt("print(m)")

    return m
