import json
import logging
import dataclasses
import pathlib
from prestring.utils import reify
from prestring.naming import snakecase
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

    @reify
    def package_dirname(self):
        return snakecase(self.name)

    def read_text(self, name: str) -> str:
        with open(pathlib.Path(self.here).parent / "templates/gitignore") as rf:
            return (
                rf.read()
                .replace("<<c.name>>", str(self.name))
                .replace("<<c.version>>", str(self.version))
                .replace("<<c.package_dirname>>", str(self.package_dirname))
            )


def gen(rootpath: str, c: Context) -> None:
    with output(str(pathlib.Path(rootpath) / c.name)) as fs:
        with fs.open(".gitignore", "w") as wf:
            wf.write(c.read_text("templates/gitignore"))
        with fs.open("README.rst", "w") as wf:
            wf.write(f"""{c.name}\n========================================""")
        with fs.open("CHANGES.rst", "w") as wf:
            wf.write("")
        with fs.open(f"{c.package_dirname}/__init__.py", "w") as wf:
            wf.write("")
        with fs.open(f"{c.package_dirname}/tests/__init__.py", "w") as wf:
            wf.write("")
        with fs.open("setup.py", "w") as wf:
            wf.write(c.read_text("templates/setup.py"))


def run(root_path: str, *, config: str) -> None:
    with open(config, "r") as rf:
        data = json.load(rf)
    c = Context(**data)
    logging.basicConfig(level=logging.INFO)
    gen(root_path, c)


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description=None)
    parser.print_usage = parser.print_help
    parser.add_argument("root_path")
    parser.add_argument("--config", required=True)
    args = parser.parse_args(argv)
    run(**vars(args))


if __name__ == "__main__":
    main()
