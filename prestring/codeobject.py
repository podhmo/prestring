from functools import update_wrapper
import typing as t
import typing_extensions as tx
from prestring import StmtTargetType, ModuleT
from prestring.utils import LazyArgumentsAndKeywords, UnRepr
from .types import Stringer

InternalModuleT = t.TypeVar("InternalModuleT", bound="InternalModule")


class InternalModule(tx.Protocol):
    def stmt(self, fmt: StmtTargetType, *args: t.Any, **kwargs: t.Any) -> ModuleT:
        ...

    def import_(self, modname: str, as_: t.Optional[str] = None) -> "Symbol":
        ...

    assign_op: str  # e.g. "="


class CodeObjectModuleMixin:
    assign_op: str = "="

    # need: stmt and import_

    def let(self, name: str, val: t.Union[str, Stringer]) -> "Symbol":
        """like `<name> = ob`"""
        self.stmt("{} {} {}", name, self.assign_op, val)  # type: ignore
        return Symbol(name)

    def letN(
        self, names: t.Sequence[str], val: t.Union[str, Stringer],
    ) -> t.List["Symbol"]:
        """like `<name> = ob`"""
        self.stmt("{} {} {}", ", ".join(names), self.assign_op, val)  # type: ignore
        return [Symbol(name) for name in names]

    def setattr(self: InternalModule, co: "Emittable", name: str, val: t.Any) -> None:
        """like `<ob>.<name> = <val>`"""
        self.stmt("{}.{} = {}", co, name, as_value(val))

    def getattr(self, ob: t.Any, name: str) -> "Attr":
        """like `<ob>.<name>`"""
        return Attr(name, co=ob)

    def symbol(self, ob: t.Union[str, t.Any]) -> "Symbol":
        """like `<ob>`"""
        if isinstance(ob, str):
            return Symbol(ob)
        return Symbol(ob.__name__)


class CodeObjectModule(CodeObjectModuleMixin):
    def __init__(self, m: InternalModule, *, assign_op: str = "=") -> None:
        self.m = m
        self.assign_op = assign_op

    def stmt(self, fmt: StmtTargetType, *args: t.Any, **kwargs: t.Any) -> ModuleT:
        return self.m.stmt(fmt, *args, **kwargs)

    def import_(self, modname: str, as_: t.Optional[str] = None) -> "Symbol":
        return self.m.import_(modname, as_=as_)


class Emittable(tx.Protocol):
    def emit(self, *, m: InternalModule) -> InternalModule:
        ...


def as_value(
    val: t.Any,
) -> t.Union[t.Dict[str, t.Any], t.List[t.Any], t.Tuple[t.Any, ...], str, UnRepr]:
    if isinstance(val, dict):
        return {k: as_value(v) for k, v in val.items()}
    elif isinstance(val, (tuple, list)):
        return val.__class__([as_value(v) for v in val])
    elif hasattr(val, "emit"):
        return UnRepr(val)
    elif callable(val) and hasattr(val, "__name__"):
        return val.__name__  # type: ignore # todo: fullname
    else:
        return repr(val)


class Object(Emittable):
    def __init__(self, name: str, *, emit: t.Callable[..., InternalModuleT]) -> None:
        self.name = name
        self._emit = emit
        self._use_count = 0

    def __str__(self) -> str:
        return self.name

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> "Call":
        return Call(name=self.name, co=self, args=args, kwargs=kwargs)

    def emit(self, *, m: InternalModule) -> InternalModule:
        return self._emit(m, name=self.name)

    def __getattr__(self, name: str) -> "Attr":
        if self._use_count > 1:
            raise RuntimeError("assign to a variable")
        self._use_count += 1
        return Attr(name, co=self)


class Symbol:
    emit = None  # for stmt
    __slots__ = ("name", "as_")

    def __init__(self, name: str, as_: t.Optional[str] = None):
        self.name = name
        self.as_ = as_

    def __str__(self) -> str:
        return self.as_ or self.name

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> "Call":
        return Call(self.as_ or self.name, co=self, args=args, kwargs=kwargs)

    def __getattr__(self, name: str) -> "Attr":
        # if name == "emit":
        #     raise AttributeError(name)
        return Attr(name, co=self)


class Attr:
    emit = None  # for stmt

    def __init__(self, name: str, co: Stringer) -> None:
        self.name = name
        self._co = co

    def __str__(self) -> str:
        return f"{self._co}.{self.name}"

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> "Call":
        return Call(self.name, co=self, args=args, kwargs=kwargs)

    def __getattr__(self, name: str) -> "Attr":
        # if name == "emit":
        #     raise AttributeError(name)
        return Attr(name, co=self)


class Call:
    emit = None  # for stmt

    def __init__(
        self,
        name: str,
        *,
        co: Stringer,
        args: t.Tuple[t.Any, ...],
        kwargs: t.Dict[str, t.Any],
    ) -> None:
        self._name = name

        self._co = co
        self._args = args
        self._kwargs = kwargs

    def __str__(self) -> str:
        args = [as_value(v) for v in self._args]
        kwargs = {k: as_value(v) for k, v in self._kwargs.items()}
        lparams = LazyArgumentsAndKeywords(args, kwargs)
        return f"{self._co}({lparams})"

    def __getattr__(self, name: str) -> Attr:
        # if name == "emit":
        #     raise AttributeError(name)
        return Attr(name, co=self)

    @property
    def name(self) -> str:
        return str(self._co)


def codeobject(
    emit: t.Callable[[InternalModuleT, str], InternalModuleT],
    *,
    name: t.Optional[str] = None,
) -> Object:
    name = name or emit.__name__
    ob = Object(name, emit=emit)
    update_wrapper(ob, emit)
    return ob
