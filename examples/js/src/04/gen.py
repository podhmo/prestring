from prestring.js import Module
m = Module()

with m.function("timeout", "timeoutMs"):
    with m.block("return new Promise((resolve) => ", end="})"):
        with m.block("setTimeout(() => ", end="}, timeoutMs)"):
            m.stmt("reject(new Error(`Timeout; ${timeoutMs}ms passed`))")

with m.function("dummyFetch", "path"):
    with m.block("return new Promise((resolve, reject) => ", end="})"):
        with m.block("setTimeout(() =>", end=", 1000 * Math.random()})"):
            with m.if_("path.startsWith('/resource')"):
                m.stmt("resolve({body: `Response body of ${path}`})")
            with m.else_():
                m.stmt("reject(new Error('NOT FOUND'))")

with m.block.call("Promise.race([", end="]})") as sm:
    sm("dummyFetch('/resource/data')")
    sm("timeout(5000)")
with m.block.call("x"):
    pass
# https://asciidwango.github.io/js-primer/basic/async/
print(m)
