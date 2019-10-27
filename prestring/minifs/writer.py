import typing as t
import sys
from io import StringIO
import logging
import os.path
import dataclasses

logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=False, unsafe_hash=False)
class Option:
    root: str
    prefix: str = ""
    suffix: str = ""
    cleanup: t.Optional[str] = None
    verbose: bool = False

    def fullpath(self, name: str) -> str:
        dirname, basename = os.path.split(name)
        fname = "{}{}".format(self.prefix, basename)
        return os.path.join(self.root, os.path.join(dirname, fname))

    def guess_action(self, fullpath: str) -> str:
        if os.path.exists(fullpath):
            return "update"
        else:
            return "create"

    def console_writer(self, *, cleanup=True):
        return ConsoleWriter(self)

    def writer(self, *, cleanup=True):
        return Writer(self, cleanup=cleanup_all if cleanup else None)


class Writer:
    def __init__(self, option: Option, *, cleanup=None):
        self.option = option
        self.cleanup = cleanup

    def write(self, name, file, *, _retry=False):
        fullpath = self.option.fullpath(name)
        logger.info("%s file path=%s", self.option.guess_action(fullpath), fullpath)
        try:
            with open(fullpath, "w") as wf:
                file.write(wf)
        except FileNotFoundError:
            if _retry:
                raise
            logger.info("create directory path=%s", os.path.dirname(fullpath))
            os.makedirs(os.path.dirname(fullpath), exist_ok=True)
            return self.write(name, file, _retry=True)

    def write_all(self, files):
        if self.cleanup is not None:
            self.cleanup(self.option)

        for name, f in files:
            self.write(name, f)


class ConsoleWriter:
    def __init__(self, option: Option, *, stdout=sys.stdout, stderr=sys.stderr):
        self.option = option
        self.stdout = stdout
        self.stderr = stderr

    def write(self, name, f, *, _retry=False):
        fullpath = self.option.fullpath(name)
        if not self.option.verbose:
            print(
                "{}: {}".format(self.option.guess_action(fullpath), fullpath),
                file=self.stdout,
            )
            return

        print("----------------------------------------", file=self.stderr)
        print(fullpath, file=self.stderr)
        print("----------------------------------------", file=self.stderr)
        self.stderr.flush()

        o = StringIO()
        f.write(o)
        print(
            "  ",
            o.getvalue().replace("\n", "\n  ").rstrip("  "),
            file=self.stdout,
            sep="",
            end="",
        )
        self.stdout.flush()
        print("----------------------------------------\n", file=self.stderr)
        self.stderr.flush()

    def write_all(self, files):
        for name, f in files:
            self.write(name, f)


def cleanup_all(option: Option):
    import shutil

    logger.info("cleanup %s", option.root)
    shutil.rmtree(option.root)  # todo: dryrun
