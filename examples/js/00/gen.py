from prestring.js import Module

m = Module()

m.stmt("""const program = require("commander")""")
m.stmt("""const fs = require("fs")""")
m.sep()
m.stmt("""program.parse(process.argv)""")
m.stmt("""const filePath = program.args[0]""")
m.sep()
# hmm
with m.brace.call("""fs.readFile(filePath, (err, "utf8", file) => """):
    m.stmt("""console.log(file)""")
    with m.if_("err"):
        m.stmt("""console.error(err)""")
        m.stmt("""process.exit(err.code)""")
        m.return_()
    m.stmt("""console.log(file)""")
print(m)
