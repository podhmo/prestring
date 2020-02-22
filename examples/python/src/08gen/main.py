import logging
from prestring.python import Module
from prestring.output import output

logger = logging.getLogger(__name__)


def run(outdir: str) -> None:
    with output(outdir, opener=Module) as fs:
        with fs.open("user.py", "w") as m:
            m.import_("dataclasses")

            m.stmt("@dataclasses.dataclass")
            with m.class_("User"):
                m.stmt("name: str")
                m.stmt("age: int")

        with fs.open("group.py", "w") as m:
            m.import_("typing", as_="t")
            m.import_("dataclasses")

            m.from_(".user").import_("User")
            m.stmt("@dataclasses.dataclass")
            with m.class_("Group"):
                m.stmt("name: str")
                m.stmt(
                    "members: t.List[User] = dataclasses.field(default_factory=list)"
                )


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description=None)
    parser.print_usage = parser.print_help
    parser.add_argument("-o", "--outdir", required=False)
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO)
    run(**vars(args))


if __name__ == "__main__":
    main()
