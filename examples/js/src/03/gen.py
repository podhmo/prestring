from prestring.js import Module

m = Module()

with m.try_():
    m.comment("throw custom exception")
    m.stmt("throw new Error('error')")
with m.catch("error"):
    m.stmt("console.log(error.message)", comment="error is thrown")
m.sep()

with m.function("assertPositiveNumber", "num"):
    with m.if_("num"):
        m.stmt("throw new Error(`${num} is not positive`)")
m.sep()

with m.for_("let i=0", "i<10", "i++"):
    m.stmt("console.log(i)")
print(m)
