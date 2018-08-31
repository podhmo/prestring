import itertools
from functools import partial
from collections import defaultdict


class reify(object):
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


class Caller(object):
    def __init__(self, name):
        self.name = name
        self.kwargs = LazyKeywords([])


class LazyArgumentsAndKeywords(object):
    def __init__(self, args=None, kwargs=None):
        self.args = LazyArguments(args or [])
        self.kwargs = LazyKeywords(kwargs or {})

    def append(self, val, type=None):
        self.args.args.append(val)
        if type is not None:
            self.args.types.append(type)

    def get(self, k):
        self.kwargs.kwargs.get(k)

    def set(self, k, v, type=None):
        self.kwargs.kwargs[k] = v
        if type is not None:
            self.kwargs.types[k] = type

    def __setitem__(self, k, v):
        self.kwargs[k] = v

    def __getitem__(self, k):
        return self.kwargs[k]

    def _string(self):
        r = []
        if len(self.args.args):
            r.append(self.args)
        if len(self.kwargs.kwargs):
            r.append(self.kwargs)
        return ", ".join(map(str, r))

    @reify
    def value(self):
        return self._string()

    def __str__(self):
        return self.value


def _type_value(v, nonetype=type(None)):
    # todo: support Optional
    if hasattr(v, "__origin__"):
        return "'{}'".format(v)
    return getattr(v, "__name__", v)


class LazyArguments(object):
    def __init__(self, args=None, types=None):
        self.args = args or []
        self.types = types or []

    def _string(self):
        args = []
        for name, typ in itertools.zip_longest(self.args, self.types):
            arg = name = str(name)
            if typ is not None:
                arg = "{}: {}".format(arg, _type_value(typ))
            args.append(arg)
        return ", ".join(args)

    @reify
    def value(self):
        return self._string()

    def __str__(self):
        return self.value


class LazyKeywords(object):
    def __init__(self, kwargs=None, types=None, defaults=None, raw=False):
        self.kwargs = kwargs or {}
        self.types = types or {}
        self.defaults = defaults or {}
        self._raw = raw

    def _string(self):
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
        return ", ".join(args)

    @reify
    def value(self):
        return self._string()

    def __str__(self):
        return self.value


LazyKeywordsRepr = partial(LazyKeywords, raw=True)


class LazyJoin(object):
    def __init__(self, sep, args):
        self.sep = sep
        self.args = args

    def _string(self):
        return self.sep.join(map(str, self.args))

    @reify
    def value(self):
        return self._string()

    def __str__(self):
        return self.value


class LazyFormat(object):
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


class NameStore(object):
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
