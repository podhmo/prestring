from prestring.python import PythonModule


def gen(*, m=None, indent='    '):
    m = m or PythonModule(indent=indent)

    import textwrap
    with m.def_('hello', 'name', '*', 'message: str =  "hello world"'):
        m.docstring(textwrap.dedent("""
        greeting message
        """).strip())
        m.stmt('print(f"{name}: {message}")')

    with m.if_('__name__ == "__main__"'):
        m.stmt('hello("foo")')
    return m


if __name__ == "__main__":
    m = gen(indent='    ')
    print(m)
