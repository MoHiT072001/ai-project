from __future__ import annotations

from pathlib import Path
from typing import Any

from scanners.runner import ToolMissing, run_cmd, try_parse_json, which


def run(workdir: Path) -> list[dict[str, Any]]:
    try:
        which("tflint")
    except ToolMissing as e:
        return [
            {
                "id": "tool:tflint_missing",
                "severity": "low",
                "category": "tooling",
                "resource": "tflint",
                "description": str(e),
                "recommendation": "Install TFLint and ensure `tflint` is on PATH.",
            }
        ]

    rc, out, err = run_cmd(["tflint", "--format", "json"], cwd=workdir, timeout_s=180)
    data = try_parse_json(out) or {}
    issues: list[dict[str, Any]] = []
    for i, item in enumerate(data.get("issues") or []):
        rule = item.get("rule") or "tflint"
        msg = item.get("message") or "TFLint issue"
        rng = item.get("range") or {}
        filename = rng.get("filename") or "terraform"
        issues.append(
            {
                "id": f"tflint:{rule}:{i}",
                "severity": "low",
                "category": "static",
                "resource": filename,
                "description": msg,
                "recommendation": "Review the TFLint finding and adjust the configuration.",
            }
        )

    if rc != 0 and not issues:
        issues.append(
            {
                "id": "tflint:failed",
                "severity": "medium",
                "category": "tooling",
                "resource": "tflint",
                "description": (err or out or "tflint failed").strip(),
                "recommendation": "Run `tflint --format json` locally to inspect the full error.",
            }
        )
    return issues

