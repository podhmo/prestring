from prestring.js import Module

m = Module()

m.stmt("""const program = require("commander")""")
m.stmt("""const fs = require("fs")""")
m.stmt("""const marked = require("marked")""")
m.sep()

with m.block.chain("program") as sm:
    sm(""".option("--gfm", "gfm mode is activated")""")
    sm(""".option("-S", "--sanitize", "sanitization")""")

m.sep()
m.sep()
m.stmt("""program.parse(process.argv)""")
m.stmt("""const filePath = program.args[0]""")
m.sep()

with m.brace("const markedOptions = ") as sm:
    sm("gfm: false")
    sm("sanitize: false")
    sm("...program.opts()")
m.sep()

with m.brace("""fs.readFile(filePath, {"encoding": "utf-8"}, (err, file) => """, end="})"):
    with m.if_("err"):
        m.stmt("""console.error(err)""")
        m.stmt("""process.exit(err.code)""")
        m.return_()
    with m.brace("""const html = marked(file,""", end="})") as sm:
        sm("gfm: markedOptions.gfm")
        sm("sanitize: markedOptions.sanitize")
    m.stmt("""console.log(html)""")
print(m)
