import typing as t
from prestring.python import Module
from prestring.utils import LazyJoin, LazyArgumentsAndKeywords as LParams
from lib2to3 import pytree
import lib2to3.pgen2.token as token
from prestring.python.parse import type_repr, StrictPyTreeVisitor, node_name

# todo: comment after ':'

# see: /usr/lib/python3.7/lib2to3/Grammar.txt

Node = t.Union[pytree.Node, pytree.Leaf]


class Accessor:
    def __init__(self, tree: pytree.Node) -> None:
        self.tree = tree

    def is_def(
        self,
        node: pytree.Node,
        _candidates: t.Tuple[str, ...] = ("funcdef", "classdef"),
    ) -> bool:
        typ = type_repr(node.type)
        return typ in _candidates

    def is_file_node(self, node: Node) -> bool:
        if node.parent is None:
            return False
        return type_repr(node.parent.type) == "file_input"

    def import_contextually(self, m: Module, node: Node, name: str) -> None:
        if self.is_file_node(node):
            m.g.stmt("m.import_({!r})", name)  # type: ignore
        else:
            m.stmt("m.submodule().import_({!r})", name)

    def from_contextually(
        self, m: Module, node: Node, module: str, names: t.List[str]
    ) -> None:
        if self.is_file_node(node):
            m.g.stmt("m.from_({!r}, {})", module, ", ".join([repr(x) for x in names]))  # type: ignore
        else:
            m.stmt(
                "m.submodule().from_({!r}, {})",
                module,
                ", ".join([repr(x) for x in names]),
            )

    def emit_prefix_and_consuming(self, m: Module, node: Node) -> None:
        # output coment (prefix)
        if node.prefix:
            self.emit_comment(m, node.prefix)
            if node.children:
                node.prefix = ""  # xxx: consume

    def emit_comment(self, m: Module, comment: str) -> None:
        if comment:
            for line in comment.split("\n"):
                line = line.lstrip(" ")
                if not line:
                    continue
                m.stmt("m.stmt({!r})", line)

    def emit_stmt_multiline(self, m: Module, statement: str) -> None:
        for i, line in enumerate(statement.split("\n")):
            line = line.strip(" ")
            if not line:
                continue
            m.stmt("m.stmt({!r})", line)

    def to_arguments(self, node: Node) -> LParams:
        typ = type_repr(node.type)
        if typ == "parameters":
            # '(', <typedargslist>, ')'
            children = node.children

            if len(children) == 2:
                return LParams()

            assert len(children) == 3
            assert children[0].value == "("  # type:ignore
            node = children[1]
            assert children[2].value == ")"  # type:ignore
            typ = type_repr(node.type)

        if typ == "typedargslist":
            argslist = node.children
        elif typ == "tname":  # leaf : leaf  # with type
            argslist = [node]
        elif hasattr(node, "value"):  # leaf
            argslist = [node]
        else:
            raise ValueError("invalid type {}".format(typ))

        params = LParams()
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
                    assert len(snode.children) == 3
                    arg_name = snode.children[0].value  # type:ignore
                    assert snode.children[1].type == token.COLON
                    arg_type = str(snode.children[2]).strip()
                else:
                    arg_name = snode.value  # type:ignore

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


class Transformer(StrictPyTreeVisitor):
    def __init__(self, tree: pytree.Node, m: Module) -> None:
        self.accessor = Accessor(tree)
        self.m = m
        if not hasattr(self.m, "g"):
            self.m.g = self.m.submodule()  # type:ignore

    def _visit_default(self, node: pytree.Node) -> t.Optional[bool]:
        self.accessor.emit_prefix_and_consuming(self.m, node)
        for snode in node.children:
            self.accessor.emit_prefix_and_consuming(self.m, snode)
            self.visit(snode)
        return None

    visit_DEDENT = visit_file_input = visit_ENDMARKER = _visit_default

    def visit_decorated(self, node: pytree.Node) -> t.Optional[bool]:
        for snode in node.children[:-1]:
            assert type_repr(snode.type) == "decorator"
            self.m.stmt(
                "m.stmt({!r})",
                " ".join([str(x) for x in snode.children]).strip().replace("@ ", "@"),
            )
        self.visit(node.children[-1])
        return None

    def visit_classdef(self, node: pytree.Node) -> t.Optional[bool]:
        # output coment (prefix)
        self.accessor.emit_prefix_and_consuming(self.m, node)

        # main process
        children = node.children
        assert children[0].value == "class"  # type:ignore
        name = children[1].value.strip()  # type:ignore
        if hasattr(children[2], "value"):
            if children[2].value == ":":  # type: ignore # 'class', <name>, ':'
                args = [repr(name)]
                body = children[3]
            elif (
                children[2].value == "("  # type:ignore
            ):  # 'class', <name>, '(', <super>,')', ':':
                args = [repr(name), repr(str(children[3]).strip())]
                assert children[4].value == ")"  # type:ignore
                assert children[5].value == ":"  # type:ignore
                body = children[6]
        else:  # 'class', <name>, <parameters>, ':',  <suite>,
            params = self.accessor.to_arguments(children[2])
            assert children[3].value == ":"  # type:ignore
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
        self.m.stmt("with m.class_({}):".format(LazyJoin(", ", args)))
        self.visit_suite(body)
        self.m.sep()
        return True  # break

    def visit_funcdef(self, node: Node, *, async_: bool = False) -> t.Optional[bool]:
        # output coment (prefix)
        self.accessor.emit_prefix_and_consuming(self.m, node)
        # main process
        children = node.children
        # 'def', <name>, <parameters>, ':',  <suite>,
        assert children[0].value == "def"  # type: ignore
        name = children[1].value.strip()  # type: ignore
        params = self.accessor.to_arguments(children[2])

        if children[3].value == "->":  # type: ignore
            return_type: t.Optional[Node] = children[4]
            assert children[5].value == ":", children[3].value  # type: ignore
            body = children[6]
        else:
            return_type = None
            assert children[3].value == ":", children[3].value  # type: ignore
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

        suffix = ""
        if return_type is not None:
            suffix = ", return_type={!r}".format(str(return_type).lstrip(" "))
        if async_:
            suffix = "{}, async_=True".format(suffix)
        self.m.stmt("with m.def_({}{}):".format(LazyJoin(", ", args), suffix))

        self.visit_suite(body)
        self.m.sep()
        return True  # break

    def _visit_block_stmt(self, node: pytree.Node, *, async_: bool = False) -> None:
        # output coment (prefix)
        self.accessor.emit_prefix_and_consuming(self.m, node)

        # main process
        children = node.children
        blocks = []  # (name, expr, body)
        st = 0
        for i, snode in enumerate(children):
            typ = type_repr(snode.type)
            if typ == "suite":
                assert children[i - 1].value == ":"  # type: ignore
                blocks.append((children[st], children[st + 1 : i - 1], children[i]))
                st = i + 1

        for (name, expr, body) in blocks:
            suffix = ""
            if async_:
                suffix = ", async_=True"

            if expr:
                args = " ".join([str(x).strip() for x in expr]).lstrip()
                self.m.stmt("with m.{}_({!r}{}):", name.value.lstrip(), args, suffix)  # type: ignore
            elif hasattr(name, "value"):  # Leaf
                self.m.stmt("with m.{}_({}):", name.value.lstrip(), suffix)  # type: ignore
            else:
                typ = type_repr(name.type)
                if typ == "except_clause":
                    self.m.stmt(
                        "with m.{}_({!r}):",
                        name.children[0].value,  # type: ignore
                        " ".join([str(x).strip() for x in name.children[1:]]).lstrip(),
                    )
                else:
                    raise ValueError("unexpected blocks: {!r}, {!r}".format(name, expr))
            self.visit_suite(body)

    visit_if_stmt = (
        visit_while_stmt
    ) = visit_for_stmt = visit_try_stmt = visit_with_stmt = _visit_block_stmt  # noqa

    def visit_suite(self, node: Node) -> t.Optional[bool]:
        prefixes = []
        if node.prefix:
            prefixes.append(node)

        # main process
        itr = iter(node.children)

        found_indent = False
        for snode in itr:
            if snode.prefix:
                prefixes.append(snode)

            typ = snode.type
            if typ == token.INDENT:
                found_indent = True
                break

        if not found_indent:
            with self.m.scope():
                self.m.stmt("m.stmt({!r})", str(node).strip())
                return None

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
        return None

    def visit_simple_stmt(self, node: Node) -> t.Optional[bool]:
        # output coment (prefix)
        self.accessor.emit_prefix_and_consuming(self.m, node)

        # main process
        children = node.children
        typ = type_repr(children[0].type)
        # docstring
        if hasattr(children[0], "value") and children[0].value.startswith(  # type: ignore
            ("'''", '"""')
        ):
            docstring = "".join([snode.value for snode in children])  # type: ignore
            if "\n" not in docstring:
                self.m.stmt("m.docstring({!r})", docstring.strip("\"'"))
            else:
                quote_char = docstring[0]  # "'" or '"'
                docstring = docstring.strip("""'"\n \t""")

                self.m.g.import_("textwrap")  # type: ignore
                self.m.stmt("m.docstring(textwrap.dedent({}", quote_char * 3)
                for line in docstring.split("\n"):
                    self.m.stmt(line)
                self.m.append(quote_char * 3)
                self.m.stmt(").strip())")
            return None

        # from x import (y, z) ?
        elif typ == "import_name":
            # 'import' <dotted_as_names>
            nodes = children[0].children

            assert nodes[0].value == "import"  # type: ignore
            self.accessor.import_contextually(self.m, node, str(nodes[1]).strip())
            rest = nodes[2:]

        # import_name | import_from
        elif typ == "import_from":
            # 'from' <module> 'import' ('*' | '(' <import_asnames> ')' | <import_asnames>)
            nodes = children[0].children

            assert nodes[0].value == "from"  # type: ignore
            module = str(nodes[1]).strip()
            for i in range(2, len(nodes)):
                if nodes[i].value == "import":  # type: ignore
                    break
                module = module + nodes[i].value  # type: ignore
            else:
                raise ValueError("invalid import: {!r}".format(nodes))

            assert nodes[i].value == "import"  # type: ignore
            names = []
            for snode in nodes[i:]:
                typ = type_repr(snode.type)
                if typ == "import_as_names":
                    for ssnode in snode.children:
                        if ssnode.type == token.COMMA:
                            continue
                        names.append(str(ssnode).strip())
                elif typ == "import_as_name":
                    assert len(snode.children) == 3
                    names.append(str(snode).strip())
                elif typ == str(token.COMMA):
                    continue
                elif typ == str(token.LPAR):
                    continue
                elif typ == str(token.RPAR):
                    continue
                elif type_repr(snode.value) == "import":  # type: ignore
                    continue
                else:
                    names.append(snode.value)  # type: ignore
            self.accessor.from_contextually(self.m, node, module, names)
            rest = children[1:]
        else:
            rest = node.children

        if rest:
            self.accessor.emit_stmt_multiline(self.m, "".join([str(x) for x in rest]))
        return None

    def visit_async_stmt(self, node: Node) -> t.Optional[bool]:
        # ASYNC <node>
        assert len(node.children) == 2
        method = "visit_{0}".format(node_name(node.children[1]))
        getattr(self, method)(node.children[1], async_=True)
        return True  # break


def transform(source: str, *, indent: str, m: t.Optional[Module] = None) -> Module:
    from prestring.python.parse import parse_string

    if m is None:
        m = Module(indent=indent)
        m.g = m.submodule()  # type: ignore

    node = parse_string(source)

    t = Transformer(node, m=m)
    t.visit(node)
    return m
