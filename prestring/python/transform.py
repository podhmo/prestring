from prestring.python import Module
from prestring.utils import (
    LazyJoin,
    LParams,
    LKwargs,
)
from lib2to3.pgen2 import token
from prestring.python.parse import (
    type_repr,
    StrictPyTreeVisitor,
)

# todo: import


class Accessor:
    def __init__(self, tree):
        self.tree = tree

    def is_def(self, node, _candidates=("funcdef", "classdef")):
        typ = type_repr(node.type)
        return typ in _candidates

    def to_arguments(self, node):
        typ = type_repr(node.type)
        if typ == "parameters":
            # '(', <typedargslist>, ')'
            children = node.children
            assert len(children) == 3
            assert children[0].value == "("
            node = children[1]
            assert children[2].value == ")"
            typ = type_repr(node.type)

        if typ == "typedargslist":
            argslist = node.children
        elif hasattr(node, "value"):  # leaf
            argslist = [node]
        else:
            raise ValueError("invalid type {}".format(typ))

        params = LParams(kwargs=LKwargs())
        itr = iter(argslist)
        while True:
            arg_name = None
            arg_type = None
            try:
                snode = next(itr)
                if type_repr(snode.type) == "tname":  # with type
                    len(snode.children) == "3"
                    arg_name = snode.children[0].value
                    assert snode.children[1].value == ":"
                    arg_type = snode.children[2].value
                else:
                    arg_name = snode.value

                arg_default = None
                snode = next(itr)  # or EOF
                if snode.value == ",":
                    pass
                elif snode.value == "=":
                    snode = next(itr)
                    arg_default = str(snode)
                    snode = next(itr)  # , or EOF
                    assert snode.value == ","
                else:
                    raise ValueError("invalid arglist {!r}".format(argslist))
            except StopIteration:
                break
            finally:
                if arg_name is not None:
                    if arg_default is None:
                        params.append(arg_name, type=arg_type)
                    else:
                        params.set(arg_name, arg_default, type=arg_type)
        return params


class Transformer(StrictPyTreeVisitor):
    def __init__(self, tree, m):
        self.accessor = Accessor(tree)
        self.m = m
        if not hasattr(self.m, "g"):
            self.m.g = self.m.submodule()

    def _visit_default(self, node):
        for child in node.children:
            self.visit(child)

    visit_file_input = visit_DEDENT = visit_ENDMARKER = _visit_default

    def visit_decorated(self, node):
        for snode in node.children[:-1]:
            assert type_repr(snode.type) == "decorator"
            self.m.stmt(
                "m.stmt({!r})", " ".join([str(x)
                                          for x in snode.children]).strip().replace("@ ", "@")
            )
        return self.visit(node.children[-1])

    def visit_classdef(self, node):
        children = node.children
        # 'class', <name>, <parameters>, ':',  <suite>,
        assert children[0].value == "class"
        name = children[1].value.strip()
        if hasattr(children[2], "value") and children[2].value == ":":
            body = children[3]
            args = [repr(name)]
        else:
            params = self.accessor.to_arguments(children[2])
            assert children[3].value == ":"
            body = children[4]
            args = [repr(name)]
            args.extend([repr(str(x)) for x in params.args._args()])
            args.extend([repr(str(x)) for x in params.kwargs._args()])

        # class Foo(x):
        #    pass
        #
        # is
        #
        # with m.class("Foo", 'x'):
        #     m.stmt("pass")
        self.m.stmt('with m.class_({}):'.format(LazyJoin(", ", args)))
        self.visit_suite(body)
        self.m.sep()
        return True  # break

    def visit_funcdef(self, node):
        children = node.children
        # 'def', <name>, <parameters>, ':',  <suite>,
        assert children[0].value == "def"
        name = children[1].value.strip()
        params = self.accessor.to_arguments(children[2])
        assert children[3].value == ":"
        body = children[4]

        # def foo(x:int, y:int=0) -> int:
        #    pass
        #
        # is
        #
        # with m.def_("foo", 'x: int', 'y: int = 0'):
        #     m.stmt("pass")

        args = [repr(name)]
        args.extend([repr(str(x)) for x in params.args._args()])
        args.extend([repr(str(x)) for x in params.kwargs._args()])
        self.m.stmt('with m.def_({}):'.format(LazyJoin(", ", args)))
        self.visit_suite(body)
        self.m.sep()
        return True  # break

    def _visit_block_stmt(self, node):
        children = node.children
        blocks = []  # (name, expr, body)
        st = 0
        for i, snode in enumerate(children):
            typ = type_repr(snode.type)
            if typ == "suite":
                assert children[i - 1].value == ":"
                blocks.append((children[st], children[st + 1:i - 1], children[i]))
                st = i + 1

        for (name, expr, body) in blocks:
            # todo: as support
            if expr:
                args = " ".join([str(x) for x in expr]).lstrip()
                self.m.stmt("with m.{}_({!r}):", name.value.lstrip(), args)
            elif hasattr(name, "value"):  # Leaf
                self.m.stmt("with m.{}_():", name.value.lstrip())
            else:
                typ = type_repr(name.type)
                if typ == "except_clause":
                    self.m.stmt(
                        "with m.{}_({!r}):",
                        name.children[0].value,
                        " ".join([str(x) for x in name.children[1:]]).lstrip(),
                    )
                else:
                    raise ValueError("unexpected blocks: {!r}, {!r}".format(name, expr))
            self.visit_suite(body)

    visit_if_stmt = visit_while_stmt = visit_for_stmt = visit_try_stmt = visit_with_stmt = _visit_block_stmt  # noqa

    def visit_suite(self, node):
        itr = iter(node.children)

        for snode in itr:
            typ = type_repr(snode.type)
            if typ == token.INDENT:
                break

        with self.m.scope():
            for snode in itr:
                self.visit(snode)

    def visit_simple_stmt(self, node):
        # docstring?
        children = node.children
        if hasattr(children[0], "value") and children[0].value.startswith(("'''", '"""')):
            docstring = "".join([snode.value for snode in children]).strip()
            if "\n" not in docstring:
                self.m.stmt("m.docstring({!r})", docstring.strip("\"'"))
            else:
                self.m.g.import_("textwrap")
                self.m.stmt('m.docstring(textwrap.dedent(')
                for line in docstring.split("\n"):
                    self.m.stmt(line)
                self.m.stmt("))")
        else:
            self.m.stmt("m.stmt({!r})", str(node).strip())


def transform(node, *, m=None, is_whole=None):
    is_whole = is_whole or m is None
    if m is None:
        m = Module()
        m.g = m.submodule()

    if is_whole:
        m.from_("prestring.python", "Module")
        m.stmt("m = Module()  # noqa")
        m.sep()

    t = Transformer(node, m=m)
    t.visit(node)

    if is_whole:
        m.stmt("print(m)")
    return m


def transform_string(source: str, *, m=None):
    from prestring.python.parse import parse_string
    return transform(parse_string(source), m=m)


def transform_file(fname: str, *, m=None):
    with open(fname) as rf:
        return transform_string(rf.read(), m=m)


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args(argv)
    print(transform_file(args.file))


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or [__file__])
