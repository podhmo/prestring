import typing as t
from ._glob import glob
from ._flatten import flatten
from .writer import Option  # noqa

T = t.TypeVar("T")


class File:
    def __init__(self, name: str, content: t.Any):
        self.name = name
        self.content = content

    def __enter__(self):
        return self.content

    def __exit__(self, typ, val, tb):
        pass

    def __repr__(self):
        return "<{self.__class__.__name__} name={self.name!r}>".format(self=self)

    def write(self, wf):
        content = self.content
        if hasattr(content, "read"):
            if hasattr(content, "seek"):
                content.seek(0)
            content = content.read()
        print(content, file=wf, end="")


class MiniFS(t.Generic[T]):
    """in memory tiny file system like object"""

    fs: t.Dict[str, t.Any]  # recursive
    sep: str

    def __init__(
        self,
        *,
        sep="/",
        store: t.Optional[t.Dict[str, t.Any]] = None,
        default_factory=t.Callable[[str], t.Any],
        container_factory=File,
        writer=None,
    ):
        self._store = store or {}
        self.sep = sep

        self.default_factory = default_factory
        self.container_factory = container_factory
        self.writer = writer

    def open(self, name: str, mode: str, content: t.Optional[t.Any] = None) -> T:
        if mode == "r":
            return _access(self._store, name, sep=self.sep)
        elif mode == "w":
            content = self.container_factory(name, content or self.default_factory())
            _touch(self._store, name, content=content, force_create=True, sep=self.sep)
            return content
        else:
            raise ValueError(
                "unexpected mode: {!r}. supported mode is 'r' or 'w'".format(mode)
            )

    def walk(self) -> t.Iterable[T]:
        for row in flatten(self._store, sep=self.sep).items():
            yield row

    def glob(self, pattern: str) -> t.Iterable[T]:
        for row in glob(self._store, pattern, sep=self.sep):
            yield row

    def __enter__(self):
        return self

    def __exit__(self, typ, val, tb):
        if self.writer is not None:
            self.writer.write_all(self.walk())


def _touch(d: dict, filename, *, content="", sep="/", force_create=False):
    path = filename.split(sep)
    target = d
    for k in path[:-1]:
        try:
            target = target[k]
        except KeyError:
            if not force_create:
                raise FileNotFoundError(filename) from None
            target[k] = {}
            target = target[k]
    target[path[-1]] = content


def _access(d: dict, filename: str, *, sep="/"):
    path = filename.split(sep)
    target = d
    try:
        for k in path:
            target = target[k]
        return target
    except (KeyError, IndexError):
        raise FileNotFoundError(filename) from None
