import typing as t
import sys
from lib2to3 import pytree
from lib2to3 import pygram
from lib2to3.pgen2 import driver
from lib2to3.pgen2 import token
from lib2to3.pgen2.parse import ParseError

default_driver = driver.Driver(
    pygram.python_grammar_no_print_statement, convert=pytree.convert
)

Node = t.Union[pytree.Node, pytree.Leaf]


def parse_string(
    code: str, parser_driver: driver.Driver = default_driver, *, debug: bool = True
) -> pytree.Node:
    tree = parser_driver.parse_string(code, debug=debug)
    return t.cast(pytree.Node, tree)  # xxx


def parse_file(
    filename: str, parser_driver: driver.Driver = default_driver, *, debug: bool = True
) -> pytree.Node:
    try:
        tree = parser_driver.parse_file(filename, debug=debug)
        return t.cast(pytree.Node, tree)  # xxx
    except ParseError as e:
        if "bad input:" not in repr(e):  # work around
            raise
        with open(filename) as rf:
            body = rf.read()
        return parse_string(body + "\n", parser_driver=parser_driver, debug=debug)


def node_name(node: Node) -> str:
    # Nodes with values < 256 are tokens. Values >= 256 are grammar symbols.
    if node.type < 256:
        return token.tok_name[node.type]
    else:
        return pygram.python_grammar.number2symbol[node.type]


type_repr = pytree.type_repr


def node_fullname(node: Node) -> str:
    typ = type_repr(node.type)
    if typ == "funcdef":
        return "{}[name={}]".format(
            node_name(node), repr(node.children[1].value)  # type:ignore
        )
    elif typ == "classdef":
        return "{}[name={}]".format(
            node_name(node), repr(node.children[1].value)  # type:ignore
        )
    elif typ == "typedargslist":
        return "{}[args={}]".format(
            node_name(node),
            " ".join(
                [
                    repr(c.value)  # type:ignore
                    if hasattr(c, "value")
                    else repr(node_fullname(c))
                    for c in node.children
                ]
            ),
        )
    else:
        return node_name(node)


def _dump_node_to_string(node: Node) -> str:
    if isinstance(node, pytree.Leaf):
        fmt = "{name}({value}) [lineno={lineno}, column={column}, prefix={prefix}]"
        return fmt.format(
            name=node_fullname(node),
            value=repr(node.value),
            lineno=node.lineno,
            column=node.column,
            prefix=repr(node.prefix),
        )
    else:
        fmt = "{node} [{len} children]"
        return fmt.format(node=node_fullname(node), len=len(node.children))


# from yapf
class PyTreeVisitor:
    def visit(self, node: Node) -> None:
        method = "visit_{0}".format(node_name(node))
        if hasattr(self, method):
            # Found a specific visitor for this node
            if getattr(self, method)(node):
                return

        # for performance, not using isinstance()
        if hasattr(node, "value"):  # Leaf
            self.default_leaf_visit(node)  # type: ignore
        else:
            self.default_node_visit(node)  # type: ignore

    def default_node_visit(self, node: pytree.Node) -> None:
        for child in node.children:
            self.visit(child)

    def default_leaf_visit(self, leaf: pytree.Leaf) -> None:
        pass


class PyTreeDumper(PyTreeVisitor):
    def __init__(
        self,
        *,
        target_stream: t.IO[str] = sys.stdout,
        tostring: t.Callable[[Node], str] = _dump_node_to_string
    ) -> None:
        self._target_stream = target_stream
        self._current_indent = 0
        self._tostring = tostring

    def _dump_string(self, s: str) -> None:
        self._target_stream.write("{0}{1}\n".format(" " * self._current_indent, s))

    def default_node_visit(self, node: pytree.Node) -> None:
        self._dump_string(self._tostring(node))
        self._current_indent += 2
        super().default_node_visit(node)
        self._current_indent -= 2

    def default_leaf_visit(self, leaf: pytree.Leaf) -> None:
        self._dump_string(self._tostring(leaf))


class StrictPyTreeVisitor(PyTreeVisitor):
    def default_node_visit(self, node: pytree.Node) -> None:
        method = "visit_{0}".format(node_name(node))
        if not hasattr(self, method):
            raise NotImplementedError(method)

    def default_leaf_visit(self, node: pytree.Leaf) -> None:
        method = "visit_{0}".format(node_name(node))
        if not hasattr(self, method):
            raise NotImplementedError(method)


def dump_tree(
    tree: pytree.Node,
    stream: t.IO[str] = sys.stdout,
    tostring: t.Callable[[Node], str] = _dump_node_to_string,
) -> None:
    dumper = PyTreeDumper(target_stream=stream, tostring=tostring)
    dumper.visit(tree)


if __name__ == "__main__":
    import sys

    if len(sys.argv) <= 1:
        print("python -m prestring.python.parse <file>", file=sys.stderr)
        sys.exit(1)

    tree = parse_file(sys.argv[1])
    dump_tree(tree)
