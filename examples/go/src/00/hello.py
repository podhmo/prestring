from prestring.go import Module

m = Module()
m.package('main')

with m.import_group() as import_:
    import_('fmt')
    import_("os")

m.comment("Hello is print Hello")
with m.func('Hello', "name string"):
    m.stmt('fmt.Printf("%s: Hello", name)')


with m.func('main'):
    m.stmt('var name string')
    with m.if_('len(os.Args) > 1'):
        m.stmt('name = os.Args[1]')
    with m.else_():
        m.stmt('name = "foo"')

    m.comment('with block')
    with m.block():
        m.stmt("Hello(name)")


print(m)
