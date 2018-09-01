from prestring.python import Module
m = Module()  # noqa
m.from_('prestring.python', 'Module', 'NEWLINE')
m.from_('prestring.utils', 'LazyJoin', 'LazyArgumentsAndKeywords as LParams', 'LKwargs')
m.import_('lib2to3.pgen2.token as token')
m.from_('prestring.python.parse', 'type_repr', 'StrictPyTreeVisitor')
m.sep()


m.stmt("# todo: comment after ':'")
m.stmt('# see: /usr/lib/python3.7/lib2to3/Grammar.txt')
with m.class_('Accessor'):
    with m.def_('__init__', 'self', 'tree'):
        m.stmt('self.tree = tree')

    with m.def_('is_def', 'self', 'node', '_candidates=("funcdef", "classdef")'):
        m.stmt('typ = type_repr(node.type)')
        m.stmt('return typ in _candidates')

    with m.def_('is_toplevel', 'self', 'node'):
        m.stmt('return type_repr(node.parent.type) == "file_input"')

    with m.def_('import_contextually', 'self', 'm', 'node', 'name'):
        with m.if_('self.is_toplevel(node)'):
            m.stmt('m.g.stmt("m.import_({!r})", name)')
        with m.else_():
            m.stmt('m.stmt("m.submodule().import_({!r})", name)')

    with m.def_('from_contextually', 'self', 'm', 'node', 'module', 'names'):
        with m.if_('self.is_toplevel(node)'):
            m.stmt('m.g.stmt("m.from_({!r}, {})", module, ", ".join([repr(x) for x in names]))')
        with m.else_():
            m.stmt('m.stmt("m.submodule().from_({!r}, {})", module, ", ".join([repr(x) for x in names]))')

    with m.def_('emit_prefix_and_consuming', 'self', 'm', 'node'):
        m.stmt('# output coment (prefix)')
        with m.if_('node.prefix'):
            m.stmt('self.emit_comment(m, node.prefix)')
            with m.if_('node.children'):
                m.stmt('node.prefix = ""  # xxx: consume')

    with m.def_('emit_comment', 'self', 'm', 'comment'):
        with m.if_('comment'):
            with m.for_('line in comment.split("\\n")'):
                m.stmt('line = line.lstrip(" ")')
                with m.if_('not line'):
                    m.stmt('continue')
                m.stmt('m.stmt("m.stmt({!r})", line)')

    with m.def_('emit_stmt_multiline', 'self', 'm', 'statement'):
        with m.for_('i, line in enumerate(statement.split("\\n"))'):
            m.stmt('line = line.strip(" ")')
            with m.if_('not line'):
                m.stmt('continue')
            m.stmt('m.stmt("m.stmt({!r})", line)')

    with m.def_('to_arguments', 'self', 'node'):
        m.stmt('typ = type_repr(node.type)')
        with m.if_('typ == "parameters"'):
            m.stmt("# '(', <typedargslist>, ')'")
            m.stmt('children = node.children')
            m.stmt('assert len(children) == 3')
            m.stmt('assert children[0].value == "("')
            m.stmt('node = children[1]')
            m.stmt('assert children[2].value == ")"')
            m.stmt('typ = type_repr(node.type)')
        with m.if_('typ == "typedargslist"'):
            m.stmt('argslist = node.children')
        with m.elif_('hasattr(node, "value")'):
            m.stmt('# leaf')
            m.stmt('argslist = [node]')
        with m.else_():
            m.stmt('raise ValueError("invalid type {}".format(typ))')
        m.stmt('params = LParams(kwargs=LKwargs())')
        m.stmt('itr = iter(argslist)')
        with m.while_('True'):
            m.stmt('arg_name = None')
            m.stmt('arg_type = None')
            with m.try_():
                m.stmt('snode = next(itr)')
                with m.if_('type_repr(snode.type) == "tname"'):
                    m.stmt('# with type')
                    m.stmt('len(snode.children) == "3"')
                    m.stmt('arg_name = snode.children[0].value')
                    m.stmt('assert snode.children[1].value == ":"')
                    m.stmt('arg_type = snode.children[2].value')
                with m.else_():
                    m.stmt('arg_name = snode.value')
                m.stmt('arg_default = None')
                m.stmt('snode = next(itr)  # or EOF')
                with m.if_('snode.value == ","'):
                    m.stmt('pass')
                with m.elif_('snode.value == "="'):
                    m.stmt('snode = next(itr)')
                    m.stmt('arg_default = str(snode)')
                    m.stmt('snode = next(itr)  # , or EOF')
                    m.stmt('assert snode.value == ","')
                with m.else_():
                    m.stmt('raise ValueError("invalid arglist {!r}".format(argslist))')
            with m.except_('StopIteration'):
                m.stmt('break')
            with m.finally_():
                with m.if_('arg_name is not None'):
                    with m.if_('arg_default is None'):
                        m.stmt('params.append(arg_name, type=arg_type)')
                    with m.else_():
                        m.stmt('params.set(arg_name, arg_default, type=arg_type)')
        m.stmt('return params')



with m.class_('Transformer', 'StrictPyTreeVisitor'):
    m.stmt('# hai')
    with m.def_('__init__', 'self', 'tree', 'm'):
        m.stmt('self.accessor = Accessor(tree)')
        m.stmt('self.m = m')
        with m.if_('not hasattr(self.m, "g")'):
            m.stmt('self.m.g = self.m.submodule()')

    with m.def_('_visit_default', 'self', 'node'):
        m.stmt('self.accessor.emit_prefix_and_consuming(self.m, node)')
        with m.for_('snode in node.children'):
            m.stmt('self.accessor.emit_prefix_and_consuming(self.m, snode)')
            m.stmt('self.visit(snode)')

    m.stmt('visit_DEDENT = visit_file_input = visit_ENDMARKER = _visit_default')
    with m.def_('visit_decorated', 'self', 'node'):
        with m.for_('snode in node.children[:-1]'):
            m.stmt('assert type_repr(snode.type) == "decorator"')
            m.stmt('self.m.stmt(')
            m.stmt('"m.stmt({!r})", " ".join([str(x)')
            m.stmt('for x in snode.children]).strip().replace("@ ", "@")')
            m.stmt(')')
        m.stmt('return self.visit(node.children[-1])')

    with m.def_('visit_classdef', 'self', 'node'):
        m.stmt('# output coment (prefix)')
        m.stmt('self.accessor.emit_prefix_and_consuming(self.m, node)')
        m.stmt('# main process')
        m.stmt('children = node.children')
        m.stmt('assert children[0].value == "class"')
        m.stmt('name = children[1].value.strip()')
        with m.if_('hasattr(children[2], "value")'):
            with m.if_('children[2].value == ":"'):
                m.stmt("# 'class', <name>, ':'")
                m.stmt('args = [repr(name)]')
                m.stmt('body = children[3]')
            with m.elif_('children[2].value == "("'):
                m.stmt("# 'class', <name>, '(', <super>,')', ':':")
                m.stmt('args = [repr(name), repr(children[3].value)]')
                m.stmt('assert children[4].value == ")"')
                m.stmt('assert children[5].value == ":"')
                m.stmt('body = children[6]')
        with m.else_():
            m.stmt("# 'class', <name>, <parameters>, ':',  <suite>,")
            m.stmt('params = self.accessor.to_arguments(children[2])')
            m.stmt('assert children[3].value == ":"')
            m.stmt('args = [repr(name)]')
            m.stmt('args.extend([repr(str(x)) for x in params.args._args()])')
            m.stmt('args.extend([repr(str(x)) for x in params.kwargs._args()])')
            m.stmt('body = children[4]')
        m.stmt('# class Foo(x):')
        m.stmt('#    pass')
        m.stmt('#')
        m.stmt('# is')
        m.stmt('#')
        m.stmt('# with m.class("Foo", \'x\'):')
        m.stmt('#     m.stmt("pass")')
        m.stmt('self.m.stmt(\'with m.class_({}):\'.format(LazyJoin(", ", args)))')
        m.stmt('self.visit_suite(body)')
        m.stmt('self.m.sep()')
        m.stmt('return True  # break')

    with m.def_('visit_funcdef', 'self', 'node'):
        m.stmt('# output coment (prefix)')
        m.stmt('self.accessor.emit_prefix_and_consuming(self.m, node)')
        m.stmt('# main process')
        m.stmt('children = node.children')
        m.stmt("# 'def', <name>, <parameters>, ':',  <suite>,")
        m.stmt('assert children[0].value == "def"')
        m.stmt('name = children[1].value.strip()')
        m.stmt('params = self.accessor.to_arguments(children[2])')
        m.stmt('assert children[3].value == ":"')
        m.stmt('body = children[4]')
        m.stmt('# def foo(x:int, y:int=0) -> int:')
        m.stmt('#    pass')
        m.stmt('#')
        m.stmt('# is')
        m.stmt('#')
        m.stmt('# with m.def_("foo", \'x: int\', \'y: int = 0\'):')
        m.stmt('#     m.stmt("pass")')
        m.stmt('args = [repr(name)]')
        m.stmt('args.extend([repr(str(x)) for x in params.args._args()])')
        m.stmt('args.extend([repr(str(x)) for x in params.kwargs._args()])')
        m.stmt('self.m.stmt(\'with m.def_({}):\'.format(LazyJoin(", ", args)))')
        m.stmt('self.visit_suite(body)')
        m.stmt('self.m.sep()')
        m.stmt('return True  # break')

    with m.def_('_visit_block_stmt', 'self', 'node'):
        m.stmt('# output coment (prefix)')
        m.stmt('self.accessor.emit_prefix_and_consuming(self.m, node)')
        m.stmt('# main process')
        m.stmt('children = node.children')
        m.stmt('blocks = []  # (name, expr, body)')
        m.stmt('st = 0')
        with m.for_('i, snode in enumerate(children)'):
            m.stmt('typ = type_repr(snode.type)')
            with m.if_('typ == "suite"'):
                m.stmt('assert children[i - 1].value == ":"')
                m.stmt('blocks.append((children[st], children[st + 1:i - 1], children[i]))')
                m.stmt('st = i + 1')
        with m.for_('(name, expr, body) in blocks'):
            with m.if_('expr'):
                m.stmt('args = " ".join([str(x).strip() for x in expr]).lstrip()')
                m.stmt('self.m.stmt("with m.{}_({!r}):", name.value.lstrip(), args)')
            with m.elif_('hasattr(name, "value")'):
                m.stmt('# Leaf')
                m.stmt('self.m.stmt("with m.{}_():", name.value.lstrip())')
            with m.else_():
                m.stmt('typ = type_repr(name.type)')
                with m.if_('typ == "except_clause"'):
                    m.stmt('self.m.stmt(')
                    m.stmt('"with m.{}_({!r}):",')
                    m.stmt('name.children[0].value,')
                    m.stmt('" ".join([str(x).strip() for x in name.children[1:]]).lstrip(),')
                    m.stmt(')')
                with m.else_():
                    m.stmt('raise ValueError("unexpected blocks: {!r}, {!r}".format(name, expr))')
            m.stmt('self.visit_suite(body)')

    m.stmt('visit_if_stmt = visit_while_stmt = visit_for_stmt = visit_try_stmt = visit_with_stmt = _visit_block_stmt  # noqa')
    with m.def_('visit_suite', 'self', 'node'):
        m.stmt('prefixes = []')
        with m.if_('node.prefix'):
            m.stmt('prefixes.append(node.prefix)')
            m.stmt('node.prefix = ""  # xxx')
        m.stmt('# main process')
        m.stmt('itr = iter(node.children)')
        with m.for_('snode in itr'):
            with m.if_('snode.prefix'):
                m.stmt('prefixes.append(snode.prefix)')
                m.stmt('snode.prefix = ""  # xxx')
            m.stmt('typ = type_repr(snode.type)')
            with m.if_('typ == token.INDENT'):
                m.stmt('resttext = str(snode).strip()')
                with m.if_('resttext.startswith("#")'):
                    m.stmt('v = self.m.body.pop()')
                    m.stmt('assert v == NEWLINE, v')
                    m.stmt('self.m.stmt("  {}".format(resttext))')
                m.stmt('break')
        m.stmt('suffixes = []')
        with m.with_('self.m.scope()'):
            m.stmt('# output coment (prefix)')
            m.stmt('self.accessor.emit_comment(self.m, "\\n".join(prefixes))')
            with m.for_('snode in itr'):
                with m.if_('snode.type == token.DEDENT'):
                    m.stmt('suffixes.append(snode.prefix)')
                    m.stmt('snode.prefix = ""')
                m.stmt('self.visit(snode)')
            m.stmt('# comment (suffix DEDENT)')
        with m.if_('suffixes'):
            m.stmt('assert len(suffixes) == 1')
            m.stmt('self.accessor.emit_comment(self.m, suffixes[0])')

    with m.def_('visit_simple_stmt', 'self', 'node'):
        m.stmt('# output coment (prefix)')
        m.stmt('self.accessor.emit_prefix_and_consuming(self.m, node)')
        m.stmt('# main process')
        m.stmt('children = node.children')
        m.stmt('typ = type_repr(children[0].type)')
        m.stmt('# docstring')
        with m.if_('hasattr(children[0], "value") and children[0].value.startswith(("\'\'\'", \'"""\'))'):
            m.stmt('docstring = "".join([snode.value for snode in children]).strip()')
            with m.if_('"\\n" not in docstring'):
                m.stmt('self.m.stmt("m.docstring({!r})", docstring.strip("\\"\'"))')
            with m.else_():
                m.stmt('self.m.g.import_("textwrap")')
                m.stmt("self.m.stmt('m.docstring(textwrap.dedent(')")
                with m.for_('line in docstring.split("\\n")'):
                    m.stmt('self.m.stmt(line)')
                m.stmt('self.m.stmt("))")')
            m.stmt('return')
        m.stmt('# from x import (y, z) ?')
        with m.elif_('typ == "import_name"'):
            m.stmt("# 'import' <dotted_as_names>")
            m.stmt('nodes = children[0].children')
            m.stmt('assert nodes[0].value == "import"')
            m.stmt('self.accessor.import_contextually(self.m, node, str(nodes[1]).strip())')
            m.stmt('rest = nodes[2:]')
        m.stmt('# import_name | import_from')
        with m.elif_('typ == "import_from"'):
            m.stmt("# 'from' <module> 'import' ('*' | '(' <import_asnames> ')' | <import_asnames>)")
            m.stmt('nodes = children[0].children')
            m.stmt('assert nodes[0].value == "from"')
            m.stmt('module = str(nodes[1]).strip()')
            m.stmt('assert nodes[2].value == "import"')
            m.stmt('names = []')
            with m.for_('snode in nodes[2:]'):
                m.stmt('typ = type_repr(snode.type)')
                with m.if_('typ == "import_as_names"'):
                    with m.for_('ssnode in snode.children'):
                        with m.if_('type_repr(ssnode.type) == token.COMMA'):
                            m.stmt('continue')
                        m.stmt('names.append(str(ssnode).strip())')
                with m.elif_('typ == token.COMMA'):
                    m.stmt('continue')
                with m.elif_('typ == token.LPAR'):
                    m.stmt('continue')
                with m.elif_('typ == token.RPAR'):
                    m.stmt('continue')
                with m.elif_('snode.value == "import"'):
                    m.stmt('continue')
                with m.else_():
                    m.stmt('names.append(snode.value)')
            m.stmt('self.accessor.from_contextually(self.m, node, module, names)')
            m.stmt('rest = children[1:]')
        with m.else_():
            m.stmt('rest = node.children')
        with m.if_('rest'):
            m.stmt('self.accessor.emit_stmt_multiline(self.m, "".join([str(x) for x in rest]))')



with m.def_('transform', 'node', '*', 'm=None', 'is_whole=None'):
    m.stmt('is_whole = is_whole or m is None')
    with m.if_('m is None'):
        m.stmt('m = Module()')
        m.stmt('m.g = m.submodule()')
    with m.if_('is_whole'):
        m.stmt('m.g.from_("prestring.python", "Module")')
        m.stmt('m.g.stmt("m = Module()  # noqa")')
    m.stmt('t = Transformer(node, m=m)')
    m.stmt('t.visit(node)')
    with m.if_('len(m.g.imported_set) > 0'):
        m.stmt('m.g.stmt("m.sep()")')
        m.stmt('m.g.sep()')
    with m.if_('is_whole'):
        m.stmt('m.stmt("print(m)")')
    m.stmt('return m')


with m.def_('transform_string', 'source: str', '*', 'm=None'):
    m.submodule().from_('prestring.python.parse', 'parse_string')
    m.stmt('t = parse_string(source)')
    m.stmt('return transform(t, m=m)')


with m.def_('transform_file', 'fname: str', '*', 'm=None'):
    with m.with_('open(fname) as rf'):
        m.stmt('return transform_string(rf.read(), m=m)')


with m.def_('main', 'argv=None'):
    m.submodule().import_('argparse')
    m.stmt('parser = argparse.ArgumentParser()')
    m.stmt('parser.add_argument("file")')
    m.stmt('args = parser.parse_args(argv)')
    m.stmt('m = transform_file(args.file)')
    m.stmt('# import inspect')
    m.stmt('# m = transform_string(inspect.getsource(main))')
    m.stmt('print(str(m))')


with m.if_('__name__ == "__main__"'):
    m.submodule().import_('sys')
    m.stmt('main(sys.argv[1:] or [__file__])')
print(m)
