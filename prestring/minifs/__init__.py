import typing as t
import pathlib
from ._glob import glob
from ._flatten import flatten

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

    store: t.Dict[str, t.Any]  # recursive
    sep: str

    def __init__(
        self,
        *,
        sep="/",
        store: t.Optional[t.Dict[str, t.Any]] = None,
        opener=t.Callable[[str], t.Any],
        container_factory=File,
    ):
        self._store = store or {}
        self.sep = sep

        self.opener = opener
        self.container_factory = container_factory

    def open(
        self,
        name: t.Union[str, pathlib.Path],
        mode: str,
        content: t.Optional[t.Any] = None,
        *,
        opener=None,
    ) -> T:
        name = str(name)
        if mode == "r":
            return _access(self._store, name, sep=self.sep)
        elif mode == "w":
            opener = opener or self.opener
            content = self.container_factory(name, content or opener())
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
