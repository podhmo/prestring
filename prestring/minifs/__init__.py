import typing as t
import typing_extensions as tx
import pathlib
from ._glob import glob
from ._flatten import flatten

T = t.TypeVar("T")
DefaultT = t.TypeVar("DefaultT")
Leaf = t.Union["File[T]"]  # the value, stored by nested dict
Content = t.Union[t.Any, t.IO[str]]


class NestedDict(tx.Protocol):
    def __getitem__(self, k: str) -> "NestedDict":
        ...

    def __setitem__(self, k: str, v: t.Union["Leaf[T]", "NestedDict"]) -> None:
        ...


class FlatDict(tx.Protocol[T]):
    def __getitem__(self, k: str) -> "Leaf[T]":
        ...

    def __setitem__(self, k: str, v: "Leaf[T]") -> None:
        ...


class File(t.Generic[T]):
    def __init__(self, name: str, content: T) -> None:
        self.name = name
        self.content = content

    def __enter__(self) -> T:
        return self.content

    def __exit__(
        self,
        exc: t.Optional[t.Type[BaseException]],
        value: t.Optional[BaseException],
        tb: t.Any,
    ) -> None:
        pass

    def __repr__(self) -> str:
        return "<{self.__class__.__name__} name={self.name!r}>".format(self=self)

    def write(self, wf: t.IO[str]) -> None:
        content = self.content
        if hasattr(content, "read"):
            if hasattr(content, "seek"):
                content.seek(0)  # type: ignore
            content = content.read()  # type: ignore
        print(content, file=wf, end="")


class MiniFS(t.Generic[DefaultT]):
    """in memory tiny file system like object"""

    store: NestedDict  # recursive
    sep: str

    def __init__(
        self,
        *,
        sep: str = "/",
        store: t.Optional[t.Dict[str, t.Any]] = None,
        opener: t.Callable[[], DefaultT],
        container_factory: t.Callable[..., File[T]] = File[T],
    ) -> None:
        self._store = store or {}
        self.sep = sep

        self.opener = opener
        self.container_factory = container_factory

    def open(
        self,
        name: t.Union[str, pathlib.Path],
        mode: str,
        *,
        opener: t.Optional[t.Callable[[], T]] = None,
    ) -> "Leaf[T]":
        name = str(name)
        if mode == "r":
            return _access(self._store, name, sep=self.sep)
        elif mode == "w":
            content = opener() if opener is not None else self.opener()
            content = self.container_factory(name, content)
            _touch(self._store, name, content=content, force_create=True, sep=self.sep)
            return content
        else:
            raise ValueError(
                "unexpected mode: {!r}. supported mode is 'r' or 'w'".format(mode)
            )

    def walk(self) -> t.Iterable[t.Tuple[t.Optional[str], t.Any]]:
        for row in flatten(self._store, sep=self.sep).items():
            yield row

    def glob(self, pattern: str) -> t.Iterable[t.Tuple[str, t.Any]]:
        for row in glob(self._store, pattern, sep=self.sep):
            yield row


def _touch(
    d: NestedDict,
    filename: str,
    *,
    content: "Leaf[T]",
    sep: str = "/",
    force_create: bool = False,
) -> None:
    path = filename.split(sep)
    target = d
    for k in path[:-1]:
        try:
            target = target[k]
        except KeyError:
            if not force_create:
                raise FileNotFoundError(filename) from None
            target[k] = {}  # type: ignore
            target = target[k]
    target[path[-1]] = content


def _access(d: NestedDict, filename: str, *, sep: str = "/") -> "Leaf[T]":
    path = filename.split(sep)
    target = d
    try:
        for k in path[:-1]:
            target = target[k]
        val: Leaf[T] = t.cast(FlatDict[T], target)[path[-1]]
        return val
    except (KeyError, IndexError):
        raise FileNotFoundError(filename) from None
