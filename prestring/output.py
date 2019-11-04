import typing as t
import sys
import logging
import os.path
import dataclasses
import filecmp
from io import StringIO
from .minifs import MiniFS
from .utils import reify

logger = logging.getLogger(__name__)


def cleanup_all(output: "output"):
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
    use_console: bool = os.environ.get("CONSOLE", "") != ""
    nocheck: bool = os.environ.get("NOCHECK", "") != ""

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
        setup_logging(level=logging.INFO)  # xxx
        if self.use_console:
            return _ConsoleWriter(self)
        else:
            return _ActualWriter(self)

    def __enter__(self):
        return self.fs

    def __exit__(self, typ, val, tb):
        writer = self.writer
        if not self.use_console and self.cleanup is not None:
            self.cleanup(self)
        for name, f in self.fs.walk():
            writer.write(name, f)


class _ActualWriter:
    TMP_SUFFIX = "_TMP"

    def __init__(self, output: output):
        self.output = output

    def write(self, name, file):
        if self.output.nocheck:
            self._write_without_check(name, file)
        else:
            self._write_with_check(name, file)

    def _write_with_check(self, name: str, file):
        fullpath = self.output.fullpath(name)
        if not os.path.exists(fullpath):
            self._write_without_check(name, file, action="create")
        else:
            tmppath = fullpath + self.TMP_SUFFIX

            with open(tmppath, "w") as wf:
                file.write(wf)

            not_changed = filecmp.cmp(fullpath, tmppath, shallow=True)
            if not_changed:
                action = "no change"
                os.remove(tmppath)
                if self.output.verbose:
                    logger.info("[F]\t%s\t%s", action, fullpath)
            else:
                action = "update"
                os.replace(tmppath, fullpath)
                logger.info("[F]\t%s\t%s", action, fullpath)

    def _write_without_check(self, name: str, file, *, action=None, _retry=False):
        fullpath = self.output.fullpath(name)
        action = action or self.output.guess_action(fullpath)
        try:
            with open(fullpath, "w") as wf:
                file.write(wf)
            logger.info("[F]\t%s\t%s", action, fullpath)
        except FileNotFoundError:
            if _retry:
                raise
            logger.info("[D]\tcreate\t%s", os.path.dirname(fullpath))
            os.makedirs(os.path.dirname(fullpath), exist_ok=True)
            self._write_without_check(name, file, action="create", _retry=True)


class _ConsoleWriter:
    def __init__(self, output: output, *, stdout=sys.stdout, stderr=sys.stderr):
        self.output = output
        self.stdout = stdout
        self.stderr = stderr

    def write(self, name, f, *, _retry=False):
        fullpath = self.output.fullpath(name)
        if not self.output.verbose:
            logger.info("[F]\t%s\t%s", self.output.guess_action(fullpath), fullpath)
            return

        print(f"# {fullpath}", file=self.stdout)
        print(
            "\x1b[90m----------------------------------------\x1b[0m", file=self.stderr
        )
        self.stderr.flush()

        o = StringIO()
        f.write(o)
        print(
            "  ",
            o.getvalue().rstrip().replace("\n", "\n  ").rstrip("  "),
            file=self.stdout,
            sep="",
        )
        self.stdout.flush()
        print("\n", file=self.stderr)
        self.stderr.flush()


class _MarkdownWriter:
    def __init__(self, output: output, *, stdout=sys.stdout, stderr=sys.stderr):
        self.output = output
        self.stdout = stdout
        self.stderr = stderr

    def write(self, name, f, *, _retry=False):
        fullpath = self.output.fullpath(name)

        o = StringIO()
        f.write(o)
        content = o.getvalue().strip()

        print(f"## {fullpath}\n", file=self.stdout)
        self.stdout.flush()
        print("<details>\n", file=self.stderr)
        self.stderr.flush()
        print("```", file=self.stdout)
        print(content, file=self.stdout)
        print("```\n", file=self.stdout)
        self.stdout.flush()
        print("</details>\n", file=self.stderr)
        self.stderr.flush()
        self.stdout.flush()


def setup_logging(*, _logger=None, level=logging.INFO):
    _logger = _logger or logger
    if _logger.handlers:
        return
    h = logging.StreamHandler(sys.stderr)
    h.setFormatter(logging.Formatter(fmt="%(message)s"))
    _logger.addHandler(h)
    _logger.propagate = False
    logging.basicConfig(level=level)
