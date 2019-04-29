from prestring.python import (
    Module,
    NEWLINE,
)
from prestring.utils import (
    LazyJoin,
    LazyArgumentsAndKeywords as LParams,
    LKwargs,
)
import lib2to3.pgen2.token as token
from prestring.python.parse import (
    type_repr,
    StrictPyTreeVisitor,
)

# todo: comment after ':'

# see: /usr/lib/python3.7/lib2to3/Grammar.txt


class Accessor:
    def __init__(self, tree):
        self.tree = tree

    def is_def(self, node, _candidates=("funcdef", "classdef")):
        typ = type_repr(node.type)
        return typ in _candidates

    def is_toplevel(self, node):
        return type_repr(node.parent.type) == "file_input"

    def import_contextually(self, m, node, name):
        if self.is_toplevel(node):
            m.g.stmt("m.import_({!r})", name)
        else:
            m.stmt("m.submodule().import_({!r})", name)

    def from_contextually(self, m, node, module, names):
        if self.is_toplevel(node):
            m.g.stmt("m.from_({!r}, {})", module, ", ".join([repr(x) for x in names]))
        else:
            m.stmt("m.submodule().from_({!r}, {})", module, ", ".join([repr(x) for x in names]))

    def emit_prefix_and_consuming(self, m, node):
        # output coment (prefix)
        if node.prefix:
            self.emit_comment(m, node.prefix)
            if node.children:
                node.prefix = ""  # xxx: consume

    def emit_comment(self, m, comment):
        if comment:
            for line in comment.split("\n"):
                line = line.lstrip(" ")
                if not line:
                    continue
                m.stmt("m.stmt({!r})", line)

    def emit_stmt_multiline(self, m, statement):
        for i, line in enumerate(statement.split("\n")):
            line = line.strip(" ")
            if not line:
                continue
            m.stmt("m.stmt({!r})", line)

    def to_arguments(self, node):
        typ = type_repr(node.type)
        if typ == "parameters":
            # '(', <typedargslist>, ')'
            children = node.children

            if len(children) == 2:
                return LParams(kwargs=LKwargs())

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
            prefix = ""
            try:
                snode = next(itr)
                if snode.type == token.DOUBLESTAR:
                    prefix = "**"
                    snode = next(itr)
                elif snode.type == token.STAR:
                    prefix = "*"
                    snode = next(itr)

                    if snode.type == token.COMMA:
                        params.append("*")
                        continue

                if type_repr(snode.type) == "tname":  # with type
                    len(snode.children) == "3"
                    arg_name = snode.children[0].value
                    assert snode.children[1].type == token.COLON
                    arg_type = str(snode.children[2]).strip()
                else:
                    arg_name = snode.value

                arg_default = None
                snode = next(itr)  # or EOF
                if snode.type == token.COMMA:
                    pass
                elif snode.type == token.EQUAL:
                    snode = next(itr)
                    arg_default = str(snode)
                    snode = next(itr)  # , or EOF
                    assert snode.type == token.COMMA
                else:
                    raise ValueError("invalid arglist {!r}".format(argslist))
            except StopIteration:
                break
            finally:
                if arg_name is not None:
                    if prefix:  # *args or **kwargs
                        params.append_tail(prefix + arg_name, type=arg_type)
                    elif arg_default is None:
                        params.append(arg_name, type=arg_type)
                    else:
                        params.set(arg_name, arg_default, type=arg_type)
        return params


class Transformer(StrictPyTreeVisitor):  # hai
    def __init__(self, tree, m):
        self.accessor = Accessor(tree)
        self.m = m
        if not hasattr(self.m, "g"):
            self.m.g = self.m.submodule()

    def _visit_default(self, node):
        self.accessor.emit_prefix_and_consuming(self.m, node)
        for snode in node.children:
            self.accessor.emit_prefix_and_consuming(self.m, snode)
            self.visit(snode)

    visit_DEDENT = visit_file_input = visit_ENDMARKER = _visit_default

    def visit_decorated(self, node):
        for snode in node.children[:-1]:
            assert type_repr(snode.type) == "decorator"
            self.m.stmt(
                "m.stmt({!r})", " ".join([str(x)
                                          for x in snode.children]).strip().replace("@ ", "@")
            )
        return self.visit(node.children[-1])

    def visit_classdef(self, node):
        # output coment (prefix)
        self.accessor.emit_prefix_and_consuming(self.m, node)

        # main process
        children = node.children
        assert children[0].value == "class"
        name = children[1].value.strip()
        if hasattr(children[2], "value"):
            if children[2].value == ":":  # 'class', <name>, ':'
                args = [repr(name)]
                body = children[3]
            elif children[2].value == "(":  # 'class', <name>, '(', <super>,')', ':':
                args = [repr(name), repr(str(children[3]).strip())]
                assert children[4].value == ")"
                assert children[5].value == ":"
                body = children[6]
        else:  # 'class', <name>, <parameters>, ':',  <suite>,
            params = self.accessor.to_arguments(children[2])
            assert children[3].value == ":"
            args = [repr(name)]
            args.extend([repr(str(x)) for x in params.args._args()])
            args.extend([repr(str(x)) for x in params.kwargs._args()])
            if params.tails is not None:
                args.extend([repr(str(x)) for x in params.tails._args()])
            body = children[4]

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
        # output coment (prefix)
        self.accessor.emit_prefix_and_consuming(self.m, node)
        # main process
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
        if params.tails is not None:
            args.extend([repr(str(x)) for x in params.tails._args()])
        self.m.stmt('with m.def_({}):'.format(LazyJoin(", ", args)))
        self.visit_suite(body)
        self.m.sep()
        return True  # break

    def _visit_block_stmt(self, node):
        # output coment (prefix)
        self.accessor.emit_prefix_and_consuming(self.m, node)

        # main process
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
            if expr:
                args = " ".join([str(x).strip() for x in expr]).lstrip()
                self.m.stmt("with m.{}_({!r}):", name.value.lstrip(), args)
            elif hasattr(name, "value"):  # Leaf
                self.m.stmt("with m.{}_():", name.value.lstrip())
            else:
                typ = type_repr(name.type)
                if typ == "except_clause":
                    self.m.stmt(
                        "with m.{}_({!r}):",
                        name.children[0].value,
                        " ".join([str(x).strip() for x in name.children[1:]]).lstrip(),
                    )
                else:
                    raise ValueError("unexpected blocks: {!r}, {!r}".format(name, expr))
            self.visit_suite(body)

    visit_if_stmt = visit_while_stmt = visit_for_stmt = visit_try_stmt = visit_with_stmt = _visit_block_stmt  # noqa

    def visit_suite(self, node):
        prefixes = []
        if node.prefix:
            prefixes.append(node)

        # main process
        itr = iter(node.children)

        found_indent = False
        for snode in itr:
            if snode.prefix:
                prefixes.append(snode)

            typ = type_repr(snode.type)
            if typ == token.INDENT:
                found_indent = True
                break

        if not found_indent:
            with self.m.scope():
                self.m.stmt("m.stmt({!r})", str(node).strip())
                return

        suffixes = []
        with self.m.scope():
            # output coment (prefix)
            comments = []
            for has_prefix_node in prefixes:
                comments.append(has_prefix_node.prefix)
                has_prefix_node.prefix = ""
            self.accessor.emit_comment(self.m, "\n".join(comments))

            for snode in itr:
                if snode.type == token.DEDENT:
                    suffixes.append(snode.prefix)
                    snode.prefix = ""
                self.visit(snode)

        # comment (suffix DEDENT)
        if suffixes:
            assert len(suffixes) == 1
            self.accessor.emit_comment(self.m, suffixes[0])

    def visit_simple_stmt(self, node):
        # output coment (prefix)
        self.accessor.emit_prefix_and_consuming(self.m, node)

        # main process
        children = node.children
        typ = type_repr(children[0].type)
        # docstring
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
            return

        # from x import (y, z) ?
        elif typ == "import_name":
            # 'import' <dotted_as_names>
            nodes = children[0].children

            assert nodes[0].value == "import"
            self.accessor.import_contextually(self.m, node, str(nodes[1]).strip())
            rest = nodes[2:]

        # import_name | import_from
        elif typ == "import_from":
            # 'from' <module> 'import' ('*' | '(' <import_asnames> ')' | <import_asnames>)
            nodes = children[0].children

            assert nodes[0].value == "from"
            module = str(nodes[1]).strip()
            for i in range(2, len(nodes)):
                if nodes[i].value == "import":
                    break
                module = module + nodes[i].value
            else:
                raise ValueError("invalid import: {!r}".format(nodes))

            assert nodes[i].value == "import"
            names = []
            for snode in nodes[i:]:
                typ = type_repr(snode.type)
                if typ == "import_as_names":
                    for ssnode in snode.children:
                        if type_repr(ssnode.type) == token.COMMA:
                            continue
                        names.append(str(ssnode).strip())
                elif typ == "import_as_name":
                    assert len(snode.children) == 3
                    names.append(str(snode).strip())
                elif typ == token.COMMA:
                    continue
                elif typ == token.LPAR:
                    continue
                elif typ == token.RPAR:
                    continue
                elif snode.value == "import":
                    continue
                else:
                    names.append(snode.value)
            self.accessor.from_contextually(self.m, node, module, names)
            rest = children[1:]
        else:
            rest = node.children

        if rest:
            self.accessor.emit_stmt_multiline(self.m, "".join([str(x) for x in rest]))


def transform(node, *, m=None, is_whole=None):
    is_whole = is_whole or m is None
    if m is None:
        m = Module()
        m.g = m.submodule()

    if is_whole:
        m.g.from_("prestring.python", "Module")
        m.g.stmt("m = Module()  # noqa")

    t = Transformer(node, m=m)
    t.visit(node)

    if len(m.g.imported_set) > 0:
        m.g.stmt("m.sep()")
        m.g.sep()

    if is_whole:
        m.stmt("print(m)")
    return m


def transform_string(source: str, *, m=None):
    from prestring.python.parse import parse_string
    t = parse_string(source)
    return transform(t, m=m)


def transform_file(fname: str, *, m=None):
    with open(fname) as rf:
        return transform_string(rf.read(), m=m)


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args(argv)
    m = transform_file(args.file)
    # import inspect
    # m = transform_string(inspect.getsource(main))
    print(str(m))


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or [__file__])
