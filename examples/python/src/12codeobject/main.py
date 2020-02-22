from prestring.python.codeobject import Module

m = Module()
re = m.import_("re")
sys = m.import_("sys")

m.sep()
pattern = m.let(
    "pattern",
    re.compile(
        r"^(?P<label>DEBUG|INFO|WARNING|ERROR|CRITICAL):\s*(?P<message>\S+)",
        re.IGNORECASE,
    ),
)


with m.for_("line", sys.stdin):
    matched = m.let("matched", pattern.search(m.symbol("line")))
    with m.if_(f"{matched} is not None"):
        m.stmt(m.symbol("print")(matched.groupdict()))
print(m)
