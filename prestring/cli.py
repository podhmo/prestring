from prestring.utils import LazyFormat


def main_transform(*, transform, Module, filename=None, name="gen", OutModule):
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--tab", action="store_true")
    parser.add_argument("--eval", action="store_true")
    parser.add_argument("--indent", default=None, type=int)
    parser.add_argument("file", nargs="?")

    args = parser.parse_args()
    args.indent = args.indent or (1 if args.tab else 4)
    indent = ("\t" if args.tab else " ") * args.indent

    m = run_transform(
        args.file or filename,
        transform=transform,
        Module=Module,
        name=name,
        OutModule=OutModule,
        indent=indent,
    )
    if not args.eval:
        print(m)
        return

    import tempfile
    import runpy

    with tempfile.NamedTemporaryFile(mode="w", prefix="prestring", suffix=".py") as wf:
        print(m, file=wf)
        wf.flush()
        runpy.run_path(wf.name, run_name="__main__")


def run_transform(filename: str, *, transform, Module, name="gen", OutModule, indent):
    m = Module()
    m.stmt("from {} import {}", OutModule.__module__, OutModule.__name__)
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
