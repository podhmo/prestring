import typing as t
from functools import partial, update_wrapper
from collections import defaultdict
from .types import StrOrStringer

# TODO: move to langhelpers
# TODO: remove t.Any
T = t.TypeVar("T")


# stolen from pyramid
class reify(t.Generic[T]):
    """cached property"""

    def __init__(self, wrapped: t.Callable[[t.Any], T]):
        self.wrapped = wrapped
        update_wrapper(self, wrapped)  # type: ignore

    def __get__(
        self, inst: t.Optional[object], objtype: t.Optional[t.Type[t.Any]] = None
    ) -> T:
        if inst is None:
            return self  # type: ignore
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val


class Caller:
    def __init__(self, name: str) -> None:
        self.name = name
        self.kwargs = LazyKeywords()


class LazyArgumentsAndKeywords:
    args: "LazyArguments"
    kwargs: "LazyKeywords"
    tails: "t.Optional[LazyArguments]"

    def __init__(
        self,
        args: t.Optional[t.List[t.Any]] = None,
        kwargs: t.Optional[t.Dict[str, t.Any]] = None,
    ) -> None:
        if args is None:
            args = []
        if hasattr(args, "value"):
            self.args = args  # type: ignore
        else:
            self.args = LazyArguments(args)

        kwargs = kwargs or {}
        if hasattr(kwargs, "value"):
            self.kwargs = kwargs  # type: ignore
        else:
            self.kwargs = LazyKeywords(kwargs)

        self.tails = None

    def __bool__(self) -> bool:
        return bool(self.args) or bool(self.kwargs) or bool(self.tails)

    def append(self, val: t.Any, type: t.Optional[t.Any] = None) -> None:
        self.args.args.append(val)
        if type is not None:
            self.args.types[val] = type

    def append_tail(self, val: t.Any, type: t.Optional[t.Any] = None) -> None:
        if self.tails is None:
            self.tails = LazyArguments()
        self.tails.args.append(val)
        if type is not None:
            self.tails.types[val] = type

    def get(self, k: str) -> t.Optional[t.Any]:
        return self.kwargs.kwargs.get(k)

    def set(self, k: str, v: t.Any, type: t.Optional[t.Any] = None) -> None:
        self.kwargs.kwargs[k] = v
        if type is not None:
            self.kwargs.types[k] = type

    def __setitem__(self, k: str, v: t.Any) -> None:
        self.kwargs.kwargs[k] = v

    def __getitem__(self, k: str) -> t.Any:
        return self.kwargs.kwargs[k]

    def _args(self) -> t.Iterator[t.Any]:
        r: t.List[t.Any] = []
        if len(self.args.args):
            r.append(self.args)
        if len(self.kwargs.kwargs):
            r.append(self.kwargs)
        if self.tails is not None:
            r.append(self.tails)
        return map(str, r)

    @reify
    def value(self) -> str:
        return ", ".join(self._args())

    def __str__(self) -> str:
        return self.value


def _type_value(v: t.Any, nonetype: t.Type[t.Any] = type(None)) -> t.Union[str, t.Any]:
    # todo: support Optional
    if hasattr(v, "__origin__"):
        return "'{}'".format(v)
    return getattr(v, "__name__", v)


class UnRepr:
    def __init__(self, value: t.Any) -> None:
        self.value = value

    def __repr__(self) -> str:
        return str(self.value)


class LazyArguments:
    def __init__(
        self,
        args: t.Optional[t.List[t.Any]] = None,
        types: t.Optional[t.Dict[str, t.Any]] = None,
    ) -> None:
        self.args = args or []
        self.types = types or {}

    def __bool__(self) -> bool:
        return bool(self.args)

    @t.overload  # noqa F811
    def __setitem__(self, k: int, v: t.Any) -> None:
        ...

    @t.overload  # noqa F811
    def __setitem__(self, k: slice, v: t.Iterable[t.Any]) -> None:  # noqa F811
        ...

    def __setitem__(  # noqa F811
        self, k: t.Union[int, slice], v: t.Union[t.Any, t.Iterable[t.Any]]
    ) -> None:
        self.args[k] = v

    @t.overload  # noqa F811
    def __getitem__(self, k: int) -> t.Any:
        ...

    @t.overload  # noqa F811
    def __getitem__(self, k: slice) -> t.List[t.Any]:  # noqa F811
        ...

    def __getitem__(  # noqa F811
        self, k: t.Union[int, slice]
    ) -> t.Union[t.Any, t.List[t.Any]]:
        return self.args[k]

    def _args(self) -> t.List[str]:
        args = []
        for name in self.args:
            arg = name = str(name)
            typ = self.types.get(name)
            if typ is not None:
                arg = "{}: {}".format(arg, _type_value(typ))
            args.append(arg)
        return args

    @reify
    def value(self) -> str:
        return ", ".join(self._args())

    def __str__(self) -> str:
        return self.value


class LazyKeywords:
    def __init__(
        self,
        kwargs: t.Optional[t.Dict[str, t.Any]] = None,
        types: t.Optional[t.Dict[str, t.Any]] = None,
        raw: bool = False,
    ) -> None:
        self.kwargs = kwargs or {}
        self.types = types or {}
        self._raw = raw

    def __bool__(self) -> bool:
        return bool(self.kwargs)

    def __setitem__(self, k: str, v: t.Any) -> None:
        self.kwargs[k] = v

    def __getitem__(self, k: str) -> t.Any:
        return self.kwargs[k]

    def _args(self) -> t.List[str]:
        args = []
        for name, default in self.kwargs.items():
            if self._raw:
                default = repr(default)
            arg = name = str(name)
            typ = self.types.get(name)
            if typ is not None:
                arg = "{}: {} = {}".format(arg, _type_value(typ), default)
            else:
                arg = "{}={}".format(arg, default)
            args.append(arg)
        return args

    @reify
    def value(self) -> str:
        return ", ".join(self._args())

    def __str__(self) -> str:
        return self.value


LazyKeywordsRepr = partial(LazyKeywords, raw=True)

# shortname
LParams = LazyArgumentsAndKeywords
LArgs = LazyArguments
LKwargs = LazyKeywords


class LazyJoin:
    def __init__(
        self, sep: str, args: t.List[t.Any], *, trim_empty: bool = False
    ) -> None:
        self.sep = sep
        self.args = args
        self.trim_empty = trim_empty

    def _string(self) -> str:
        if self.trim_empty:
            return self.sep.join([str(x) for x in self.args if x])
        else:
            return self.sep.join(map(str, self.args))

    @reify
    def value(self) -> str:
        return self._string()

    def __str__(self) -> str:
        return self.value


class LazyFormat:
    def __init__(self, fmt: StrOrStringer, *args: t.Any, **kwargs: t.Any) -> None:
        self.fmt = fmt
        self.args = args
        self.kwargs = kwargs

    def _string(self) -> str:
        args = map(str, self.args)
        kwargs = {k: str(v) for k, v in self.kwargs.items()}
        return str(self.fmt).format(*args, **kwargs)

    @reify
    def value(self) -> str:
        return self._string()

    def __str__(self) -> str:
        return self.value


class NameStore:
    def __init__(self) -> None:
        self.c: t.Dict[str, int] = defaultdict(int)
        self.value_map: t.Dict[object, str] = {}

    def __contains__(self, value: object) -> bool:
        return value in self.value_map

    def __setitem__(self, value: object, name: str) -> None:
        if value not in self.value_map:
            self.value_map[value] = self.get_name(value, name)
            self.c[name] += 1

    def __getitem__(self, value: object) -> str:
        return self.value_map[value]

    def get_name(self, value: object, name: str) -> str:
        try:
            return self[value]
        except KeyError:
            i = self.c[name]
            return self.new_name(name, i)

    def new_name(self, name: str, i: int) -> str:
        if i == 0:
            return name
        else:
            return "{}Dup{}".format(name, i)
