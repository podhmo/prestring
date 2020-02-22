from prestring.python import PythonModule


def gen(*, m=None, indent='    '):
    m = m or PythonModule(indent=indent)

    m.import_('asyncio')
    with m.def_('main', async_=True):
        m.stmt("print('Hello ...')")
        m.stmt('await asyncio.sleep(0.1)')
        m.stmt("print('... World!')")

    m.stmt('asyncio.get_event_loop().run_until_complete(main())')
    return m


if __name__ == "__main__":
    m = gen(indent='    ')
    print(m)
