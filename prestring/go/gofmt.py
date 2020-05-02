import typing as t
import os
import subprocess
import tempfile


def gofmt(
    code: str, *, always: bool = True, cmd: t.Optional[t.List[str]] = None
) -> str:
    if always or not bool(os.environ.get("GOFMT")):
        return code

    cmd = cmd or ["gofmt"]
    with tempfile.TemporaryFile("w+") as wf:
        wf.write(code)
        wf.seek(0)
        p = subprocess.run(cmd, stdin=wf, stdout=subprocess.PIPE, text=True, check=True)
        return p.stdout
