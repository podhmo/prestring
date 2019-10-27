import typing as t
import sys
import logging
import os.path
import dataclasses
from io import StringIO
from .minifs import MiniFS
from .utils import reify

logger = logging.getLogger(__name__)


def cleanup_all(output: "Output"):
    import shutil

    logger.info("cleanup %s", output.root)
    shutil.rmtree(output.root, ignore_errors=True)  # todo: dryrun


@dataclasses.dataclass(frozen=False, unsafe_hash=False)
class output:
    root: str

    prefix: str = ""
    suffix: str = ""

    # for MiniFS
    opener: t.Callable[..., t.Any] = StringIO  # todo: typing
    sep: str = "/"
    store: t.Dict[str, t.Any] = dataclasses.field(default_factory=dict)

    cleanup: t.Optional[str] = None
    verbose: bool = os.environ.get("VERBOSE", "") != ""
    fake: bool = os.environ.get("FAKE", "") != ""

    def fullpath(self, name: str) -> str:
        dirname, basename = os.path.split(name)
        fname = "{}{}{}".format(self.prefix, basename, self.suffix)
        return os.path.join(self.root, os.path.join(dirname, fname))

    def guess_action(self, fullpath: str) -> str:
        if os.path.exists(fullpath):
            return "update"
        else:
            return "create"

    @reify
    def fs(self):
        return MiniFS(opener=self.opener, sep=self.sep)

    @reify
    def writer(self):
        if self.fake:
            return _ConsoleWriter(self)
        else:
            return _ActualWriter(self)

    def __enter__(self):
        return self.fs

    def __exit__(self, typ, val, tb):
        writer = self.writer
        if not self.fake and self.cleanup is not None:
            self.cleanup(self)
        for name, f in self.fs.walk():
            writer.write(name, f)


class _ActualWriter:
    def __init__(self, output: output):
        self.output = output

    def write(self, name, file, *, _retry=False):
        fullpath = self.output.fullpath(name)
        logger.info("%s file path=%s", self.output.guess_action(fullpath), fullpath)
        try:
            with open(fullpath, "w") as wf:
                file.write(wf)
        except FileNotFoundError:
            if _retry:
                raise
            logger.info("create directory path=%s", os.path.dirname(fullpath))
            os.makedirs(os.path.dirname(fullpath), exist_ok=True)
            return self.write(name, file, _retry=True)


class _ConsoleWriter:
    def __init__(self, output: output, *, stdout=sys.stdout, stderr=sys.stderr):
        self.output = output
        self.stdout = stdout
        self.stderr = stderr

    def write(self, name, f, *, _retry=False):
        fullpath = self.output.fullpath(name)
        if not self.output.verbose:
            print(
                "{}: {}".format(self.output.guess_action(fullpath), fullpath),
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
