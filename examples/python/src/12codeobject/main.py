from prestring.python import Module
from prestring.codeobject import CodeObjectModule

m = Module()
co = CodeObjectModule(m)
re = m.import_("re")
sys = m.import_("sys")

m.sep()
pattern = co.let(
    "pattern",
    re.compile(
        r"^(?P<label>DEBUG|INFO|WARNING|ERROR|CRITICAL):\s*(?P<message>\S+)",
        re.IGNORECASE,
    ),
)


with m.for_("line", sys.stdin):
    matched = co.let("matched", pattern.search(co.symbol("line")))
    with m.if_(f"{matched} is not None"):
        m.stmt(co.symbol("print")(matched.groupdict()))
print(m)
