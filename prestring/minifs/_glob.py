import typing as t
import re
import fnmatch


class _Sentinel:
    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self):
        return "<{self.name}>".format(self=self)


# types
Key = t.Union[int, str]
Token = t.Union[_Sentinel, str, int, t.Callable[[str], bool]]

# constants
STAR = _Sentinel("*")
DBSTAR = _Sentinel("**")


def _parse(query: str, *, sep="/") -> t.Sequence[Token]:
    r = []
    for tk in query.split(sep):  # todo: shlex?
        if tk == "**":
            r.append(DBSTAR)
        elif tk == "*":
            r.append(STAR)
        elif "*" in tk or "?" in tk:
            r.append(re.compile(fnmatch.translate(tk)).match)
        else:
            r.append(tk)
    if r:
        assert r[-1] != DBSTAR
    return r


def _dig(
    d: t.Dict[t.Any, t.Any],
    tokens: t.Sequence[t.Union[_Sentinel, str]],
    *,
    path: t.Optional[t.List[Key]] = None,
) -> t.Iterable[t.Tuple[t.List[Key], t.Any, bool]]:  # (path, value, ok)
    if not tokens:
        yield path, d, True
        return
    if not d:
        return
    path = path or []
    tk = tokens[0]
    rest_tks = tokens[1:]

    if not hasattr(d, "keys"):
        yield path, d, False
        return

    if tk == DBSTAR:
        yield from _dig(d, rest_tks, path=path)
        for path, val, ok in _dig_next(d, tk, path):
            yield from _dig(val, tokens, path=path)
    else:
        for path, val, ok in _dig_next(d, tk, path):
            if ok:
                yield from _dig(val, rest_tks, path=path)
            else:
                yield path, val, ok


def _dig_next(
    d: t.Dict[Key, t.Any], tk: Token, path: t.List[Key]
) -> t.Iterable[t.Tuple[t.List[Key], t.Any, bool]]:  # (path, value, ok)
    if tk == STAR or tk == DBSTAR:
        for k, v in d.items():
            path.append(k)
            yield path, v, True
            path.pop()
    elif callable(tk):
        exists = False
        for k, v in d.items():
            if tk(k):
                exists = True
                path.append(k)
                yield path, d[k], True
                path.pop()
        if not exists:
            yield path, d, False
    else:
        if tk in d:
            path.append(tk)
            yield path, d[tk], True
            path.pop()
        else:
            yield path, d, False


def _fix(rows):
    return [(path[:], val, ok) for path, val, ok in rows]


def glob(d: t.Dict[str, t.Any], pattern: str, *, sep: str = "/"):
    tokens = _parse(pattern, sep=sep)
    seen = set()
    for path, sd, ok in _dig(d, tokens):
        if not ok:
            continue
        name = sep.join(path[:])
        if name in seen:
            continue
        seen.add(name)
        yield name, sd
