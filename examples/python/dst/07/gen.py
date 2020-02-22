from prestring.python import PythonModule


def gen(*, m=None, indent='    '):
    m = m or PythonModule(indent=indent)

    with m.def_('fizzbuzz', 'n: int', return_type='str'):
        with m.if_('n % 3 == 0 and n % 5 == 0'):
            m.stmt('return "fizzbuzz"')
        with m.elif_('n % 3 == 0'):
            m.stmt('return "fizz"')
        with m.elif_('n % 5 == 0'):
            m.stmt('return "buzz"')
        with m.else_():
            m.stmt('return str(n)')

    with m.if_('__name__ == "__main__"'):
        m.stmt('print(", ".join(fizzbuzz(i) for i in range(1, 21)))')
    return m


if __name__ == "__main__":
    m = gen(indent='    ')
    print(m)
