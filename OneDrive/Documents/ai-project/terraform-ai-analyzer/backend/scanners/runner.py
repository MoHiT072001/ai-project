from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Optional


class ToolMissing(Exception):
    pass


def which(binary: str) -> str:
    p = shutil.which(binary)
    if not p:
        raise ToolMissing(f"{binary} not found on PATH")
    return p


def run_cmd(
    args: list[str],
    cwd: Path,
    timeout_s: int = 120,
    env: Optional[dict[str, str]] = None,
) -> tuple[int, str, str]:
    # args must be a list to avoid shell injection. Never use shell=True.
    p = subprocess.run(
        args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=timeout_s,
        env=env,
        shell=False,
    )
    return p.returncode, p.stdout, p.stderr


def try_parse_json(text: str) -> Any:
    try:
        return json.loads(text)
    except Exception:
        return None

