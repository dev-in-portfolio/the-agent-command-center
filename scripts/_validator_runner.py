from __future__ import annotations

import contextlib
import io
import runpy
import shlex
import subprocess
import sys
from pathlib import Path


def run_validator_cmd(cmd: str, root: Path):
    has_shell_syntax = any(token in cmd for token in ["<<", "|", ">", "<"])
    if cmd.startswith("python3 ") and not has_shell_syntax:
        parts = shlex.split(cmd)
        if len(parts) == 2 and parts[1].endswith(".py"):
            script = root / parts[1]
            stdout_buf = io.StringIO()
            stderr_buf = io.StringIO()
            argv_before = sys.argv[:]
            try:
                sys.argv = parts[1:]
                with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
                    try:
                        runpy.run_path(str(script), run_name="__main__")
                        return stdout_buf.getvalue(), stderr_buf.getvalue(), 0
                    except SystemExit as exc:
                        code = exc.code if isinstance(exc.code, int) else 1
                        return stdout_buf.getvalue(), stderr_buf.getvalue(), code
            except Exception as exc:
                return stdout_buf.getvalue(), f"Execution error for {cmd}: {exc}", 1
            finally:
                sys.argv = argv_before

    result = subprocess.run(["bash", "-lc", cmd], cwd=root, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode
