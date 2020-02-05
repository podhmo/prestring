import typing as t
import re

# NOTE: duplicated with dictknife.naming


def snakecase(
    name: str,
    *,
    rx0: t.Pattern[str] = re.compile(r"(.)([A-Z][a-z]+)"),
    rx1: t.Pattern[str] = re.compile(r"([a-z0-9])([A-Z])"),
    separator: str = "_",
    other: str = "-",
) -> str:
    pattern = r"\1{}\2".format(separator)
    replaced = rx1.sub(pattern, rx0.sub(pattern, name)).lower()
    return replaced.replace(other, separator)


def kebabcase(
    name: str,
    *,
    rx0: t.Pattern[str] = re.compile(r"(.)([A-Z][a-z]+)"),
    rx1: t.Pattern[str] = re.compile(r"([a-z0-9])([A-Z])"),
    separator: str = "-",
    other: str = "_",
) -> str:
    pattern = r"\1{}\2".format(separator)
    replaced = rx1.sub(pattern, rx0.sub(pattern, name)).lower()
    return replaced.replace(other, separator)


def camelcase(name: str, *, soft: bool = True) -> str:
    if soft and name[0].isupper():
        return pascalcase(name)
    else:
        return untitleize(pascalcase(name))


def pascalcase(name: str, rx: t.Pattern[str] = re.compile(r"[\-_ ]")) -> str:
    return "".join(titleize(x) for x in rx.split(name))


def titleize(name: str) -> str:
    if not name:
        return name
    name = str(name)
    return "{}{}".format(name[0].upper(), name[1:])


def untitleize(name: str) -> str:
    if not name:
        return name
    return "{}{}".format(name[0].lower(), name[1:])
