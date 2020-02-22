import typing as t
import typing_extensions as tx
from prestring.utils import LazyFormat
from prestring import Module as BaseModule
from prestring.python import Module as PyModule

M = t.TypeVar("M", bound=PyModule)
OM = t.TypeVar("OM", bound=BaseModule)


class TransformFunction(tx.Protocol[OM]):
    def __call__(self, source: str, *, indent: str, m: t.Optional[OM] = ...) -> OM:
        ...


def main_transform(
    *,
    transform: TransformFunction[OM],
    Module: t.Type[M],
    filename: str,
    name: str = "gen",
    OutModule: t.Type[OM],
) -> None:
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


def run_transform(
    filename: str,
    *,
    transform: TransformFunction[OM],
    Module: t.Type[M],
    name: str = "gen",
    OutModule: t.Type[OM],
    indent: str,
) -> M:
    m = Module()
    m.stmt("from {} import {}", OutModule.__module__, OutModule.__name__)
    m.sep()

    with m.def_(name, "*", "m=None", LazyFormat("indent={!r}", indent)):
        m.stmt("""m = m or {}(indent=indent)""", OutModule.__name__)
        m.sep()
        with open(filename) as rf:
            text = rf.read()
        m = transform(text, m=m, indent=indent)  # type:ignore # xxx
        m.return_("m")

    with m.if_('__name__ == "__main__"'):
        m.stmt("m = {}(indent={!r})", name, indent)
        m.stmt("print(m)")

    return m
