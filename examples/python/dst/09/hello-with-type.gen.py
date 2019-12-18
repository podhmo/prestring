from prestring.python import PythonModule


def gen(*, m=None, indent='    '):
    m = m or PythonModule(indent=indent)

    with m.def_('hello', 'name: str', return_type='str'):
        m.stmt('return f"hello, {name}"')

    return m


if __name__ == "__main__":
    m = gen(indent='    ')
    print(m)
