def transform_main(*, transform_file, Module, argv=None, name="gen"):
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args(argv)

    m = Module()
    m.g = m.submodule()
    m.g.from_("prestring.python", "Module")
    m.g.stmt("m = Module()  # noqa")

    with m.def_(name, "*", "m=None"):
        m.stmt("m = m or Module()")
        m = transform_file(args.file, m=m)

    with m.if_('__name__ == "__main__"'):
        m.stmt("{}()", name)
    print(str(m))
