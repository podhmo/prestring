import typing as t


def _make_key(k0: t.Any, k1: t.Any, *, sep: str = "/") -> str:
    if k1 is None:
        return str(k0)
    return "{}{}{}".format(k0, sep, k1)


def flatten(
    d: t.Union[t.List[t.Any], t.Tuple[t.Any, ...], t.Dict[t.Any, t.Any], str, bytes],
    *,
    sep: str = "/"
) -> t.Dict[t.Optional[str], t.Any]:
    if isinstance(d, (list, tuple)):
        return {
            _make_key(i, k, sep=sep): v
            for i, row in enumerate(d)
            for k, v in flatten(row).items()
        }
    elif isinstance(d, dict):
        return {
            _make_key(k, k2, sep=sep): v2
            for k, v in d.items()
            for k2, v2 in flatten(v, sep=sep).items()
        }
    elif hasattr(d, "__next__") and not isinstance(d, (bytes, str)):
        return flatten(list(d), sep=sep)
    else:
        return {None: d}
