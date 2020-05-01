import typing as t
import typing_extensions as tx


class Stringer(tx.Protocol):
    def __str__(self) -> str:
        ...


StrOrStringer = t.Union[str, Stringer]
