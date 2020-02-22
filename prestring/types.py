import typing as t
import typing_extensions as tx
from . import ModuleT
from prestring import _Sentinel
from prestring.utils import LazyFormat


class ModuleLike(tx.Protocol):
    def unnewline(self) -> None:
        ...

    def submodule(
        self,
        value: t.Any = ...,
        newline: bool = ...,
        factory: t.Optional[t.Callable[..., ModuleT]] = None,
    ) -> ModuleT:
        ...

    def stmt(
        self, fmt: t.Union[str, _Sentinel, LazyFormat], *args: t.Any, **kwargs: t.Any
    ) -> ModuleT:
        ...

    def scope(self) -> t.ContextManager[None]:
        ...

    def append(self, value: t.Any) -> None:
        ...

    def insert_before(self, value: t.Any) -> None:
        ...

    def insert_after(self, value: t.Any) -> None:
        ...

    def __str__(self) -> str:
        ...
