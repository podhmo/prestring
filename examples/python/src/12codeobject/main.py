from prestring.python import Module
from prestring.codeobject import CodeObjectModule

m = Module()
co = CodeObjectModule(m)
re = co.import_("re")
sys = co.import_("sys")

m.sep()
pattern = co.let(
    "pattern",
    re.compile(
        r"^(?P<label>DEBUG|INFO|WARNING|ERROR|CRITICAL):\s*(?P<message>\S+)",
        re.IGNORECASE,
    ),
)

print_ = co.symbol("print")
with m.for_("line", sys.stdin) as line:
    matched = co.let("matched", pattern.search(line))
    with m.if_(f"{matched} is not None"):
        m.stmt(print_(matched.groupdict()))
print(m)
