import sys
import logging
import dataclasses
import pathlib
from prestring.output import output


@dataclasses.dataclass
class Config:
    name: str = dataclasses.field(
        default="foo-bar", metadata={"description": "package name"}
    )
    version: str = dataclasses.field(
        default="0.0.0", metadata={"description": "version"}
    )


def gen(rootpath: str, c: Config) -> None:
    with output(rootpath) as fs:
        with fs.open(f"{c.name}/.gitignore", "w") as wf:
            with open(pathlib.Path(__file__).parent / "templates/gitignore") as rf:
                content = (
                    rf.read()
                    .replace("<<c.name>>", str(c.name))
                    .replace("<<c.version>>", str(c.version))
                )
            wf.write(content)

        with fs.open(f"{c.name}/README.rst", "w") as wf:
            wf.write(f"""{c.name}\n========================================""")
        with fs.open(f"{c.name}/CHANGES.rst", "w") as wf:
            wf.write("")
        with fs.open(f"{c.name}/{c.name}/__init__.py", "w") as wf:
            wf.write("")
        with fs.open(f"{c.name}/{c.name}/tests/__init__.py", "w") as wf:
            wf.write("")
        with fs.open(f"{c.name}/setup.py", "w") as wf:
            with open(pathlib.Path(__file__).parent / "templates/setup.py") as rf:
                content = (
                    rf.read()
                    .replace("<<c.name>>", str(c.name))
                    .replace("<<c.version>>", str(c.version))
                )
            wf.write(content)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    root_path = sys.argv[1]
    c = Config()
    gen(root_path, c)
