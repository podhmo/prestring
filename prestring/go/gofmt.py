import typing as t
import sys
import os
import subprocess
import tempfile


def gofmt(
    code: str,
    *,
    always: bool = True,
    cmd: t.Optional[t.List[str]] = None,
    encoding: str = "utf-8"
) -> str:
    if always or not bool(os.environ.get("GOFMT")):
        return code

    cmd = cmd or ["gofmt"]
    with tempfile.TemporaryFile("w+") as wf:
        wf.write(code)
        wf.seek(0)

        # fixme
        if sys.version_info < (3, 7):
            p = subprocess.run(cmd, stdin=wf, stdout=subprocess.PIPE, check=True)
            return p.stdout.encode(encoding)
        else:
            p = subprocess.run(
                cmd, stdin=wf, stdout=subprocess.PIPE, text=True, check=True
            )
            return p.stdout
