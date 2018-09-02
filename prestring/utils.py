from functools import partial
from collections import defaultdict


class reify:
    def __init__(self, wrapped):
        self.wrapped = wrapped
        try:
            self.__doc__ = wrapped.__doc__
        except:
            pass

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val


class Caller:
    def __init__(self, name):
        self.name = name
        self.kwargs = LazyKeywords([])


class LazyArgumentsAndKeywords:
    def __init__(self, args=None, kwargs=None):
        self.args = args or []
        if not hasattr(self.args, "value"):
            self.args = LazyArguments(self.args)
        self.kwargs = kwargs or {}
        if not hasattr(self.kwargs, "value"):
            self.kwargs = LazyKeywords(self.kwargs)
        self.tails = None

    def __bool__(self):
        return bool(self.args) or bool(self.kwargs) or bool(self.tails)

    def append(self, val, type=None):
        self.args.args.append(val)
        if type is not None:
            self.args.types[val] = type

    def append_tail(self, val, type=None):
        if self.tails is None:
            self.tails = LazyArguments()
        self.tails.args.append(val)
        if type is not None:
            self.tails.types[val] = type

    def get(self, k):
        self.kwargs.kwargs.get(k)

    def set(self, k, v, type=None):
        self.kwargs.kwargs[k] = v
        if type is not None:
            self.kwargs.types[k] = type

    def __setitem__(self, k, v):
        self.kwargs.kwargs[k] = v

    def __getitem__(self, k):
        return self.kwargs.kwargs[k]

    def _args(self):
        r = []
        if len(self.args.args):
            r.append(self.args)
        if len(self.kwargs.kwargs):
            r.append(self.kwargs)
        if self.tails is not None:
            r.append(self.tails)
        return map(str, r)

    @reify
    def value(self):
        return ", ".join(self._args())

    def __str__(self):
        return self.value


def _type_value(v, nonetype=type(None)):
    # todo: support Optional
    if hasattr(v, "__origin__"):
        return "'{}'".format(v)
    return getattr(v, "__name__", v)


class UnRepr:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str(self.value)


class LazyArguments:
    def __init__(self, args=None, types=None):
        self.args = args or []
        self.types = types or {}

    def __bool__(self):
        return bool(self.args)

    def __setitem__(self, k, v):
        self.args[k] = v

    def __getitem__(self, k):
        return self.args[k]

    def _args(self):
        args = []
        for name in self.args:
            arg = name = str(name)
            typ = self.types.get(name)
            if typ is not None:
                arg = "{}: {}".format(arg, _type_value(typ))
            args.append(arg)
        return args

    @reify
    def value(self):
        return ", ".join(self._args())

    def __str__(self):
        return self.value


class LazyKeywords:
    def __init__(self, kwargs=None, types=None, raw=False):
        self.kwargs = kwargs or {}
        self.types = types or {}
        self._raw = raw

    def __bool__(self):
        return bool(self.kwargs)

    def __setitem__(self, k, v):
        self.kwargs[k] = v

    def __getitem__(self, k):
        return self.kwargs[k]

    def _args(self):
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
    def value(self):
        return ", ".join(self._args())

    def __str__(self):
        return self.value


LazyKeywordsRepr = partial(LazyKeywords, raw=True)

# shortname
LParams = LazyArgumentsAndKeywords
LArgs = LazyArguments
LKwargs = LazyKeywords


class LazyJoin:
    def __init__(self, sep, args, *, trim_empty=False):
        self.sep = sep
        self.args = args
        self.trim_empty = trim_empty

    def _string(self):
        if self.trim_empty:
            return self.sep.join([str(x) for x in self.args if x])
        else:
            return self.sep.join(map(str, self.args))

    @reify
    def value(self):
        return self._string()

    def __str__(self):
        return self.value


class LazyFormat:
    def __init__(self, fmt, *args, **kwargs):
        self.fmt = fmt
        self.args = args
        self.kwargs = kwargs

    def _string(self):
        args = map(str, self.args)
        kwargs = {k: str(v) for k, v in self.kwargs.items()}
        return self.fmt.format(*args, **kwargs)

    @reify
    def value(self):
        return self._string()

    def __str__(self):
        return self.value


class NameStore:
    def __init__(self):
        self.c = defaultdict(int)
        self.value_map = {}  # (src_type, dst_type) => (name, i)

    def __contains__(self, value):
        return value in self.value_map

    def __setitem__(self, value, name):
        if value not in self.value_map:
            self.value_map[value] = self.get_name(value, name)
            self.c[name] += 1

    def __getitem__(self, value):
        return self.value_map[value]

    def get_name(self, value, name):
        try:
            return self[value]
        except KeyError:
            i = self.c[name]
            return self.new_name(name, i)

    def new_name(self, name, i):
        if i == 0:
            return name
        else:
            return "{}Dup{}".format(name, i)
