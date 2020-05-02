from prestring.go.codeobject import gofile


m = gofile("main")

with m.func("main"):
    m.stmt('println("hello")')

print(m)
