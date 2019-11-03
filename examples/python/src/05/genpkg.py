import sys
import logging
import dataclasses
import pathlib
from prestring.output import output


@dataclasses.dataclass
class Context:
    name: str = dataclasses.field(
        default="foo-bar", metadata={"description": "package name"}
    )
    version: str = dataclasses.field(
        default="0.0.0", metadata={"description": "version"}
    )
    here: str = __file__

    def read_text(self, name: str) -> str:
        with open(pathlib.Path(self.here).parent / "templates/gitignore") as rf:
            return (
                rf.read()
                .replace("<<c.name>>", str(self.name))
                .replace("<<c.version>>", str(self.version))
            )


def gen(rootpath: str, c: Context) -> None:
    with output(str(pathlib.Path(rootpath) / c.name)) as fs:
        with fs.open(".gitignore", "w") as wf:
            wf.write(c.read_text("templates/gitignore"))
        with fs.open("README.rst", "w") as wf:
            wf.write(f"""{c.name}\n========================================""")
        with fs.open("CHANGES.rst", "w") as wf:
            wf.write("")
        with fs.open("__init__.py", "w") as wf:
            wf.write("")
        with fs.open("tests/__init__.py", "w") as wf:
            wf.write("")
        with fs.open("setup.py", "w") as wf:
            wf.write(c.read_text("templates/setup.py"))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    root_path = sys.argv[1]
    c = Context()
    gen(root_path, c)
