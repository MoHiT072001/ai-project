from __future__ import annotations

from pathlib import Path
from typing import Any

from scanners.runner import ToolMissing, run_cmd, try_parse_json, which


_SEV_MAP = {
    "LOW": "low",
    "MEDIUM": "medium",
    "HIGH": "high",
    "CRITICAL": "critical",
}


def run(workdir: Path) -> list[dict[str, Any]]:
    try:
        which("checkov")
    except ToolMissing as e:
        return [
            {
                "id": "tool:checkov_missing",
                "severity": "low",
                "category": "tooling",
                "resource": "checkov",
                "description": str(e),
                "recommendation": "Install Checkov and ensure `checkov` is on PATH.",
            }
        ]

    rc, out, err = run_cmd(
        ["checkov", "-d", ".", "-o", "json", "--quiet"],
        cwd=workdir,
        timeout_s=300,
    )
    data = try_parse_json(out) or {}
    issues: list[dict[str, Any]] = []

    # Checkov JSON formats vary; handle common "results.failed_checks".
    results = data.get("results") or {}
    failed = results.get("failed_checks") or []
    for i, f in enumerate(failed):
        check_id = f.get("check_id") or "checkov"
        check_name = f.get("check_name") or "Checkov finding"
        file_path = f.get("file_path") or "terraform"
        resource = f.get("resource") or file_path
        sev = (f.get("severity") or "MEDIUM").upper()
        guideline = f.get("guideline") or ""
        issues.append(
            {
                "id": f"checkov:{check_id}:{i}",
                "severity": _SEV_MAP.get(sev, "medium"),
                "category": "static",
                "resource": str(resource),
                "description": (check_name + (f" ({guideline})" if guideline else "")).strip(),
                "recommendation": "Follow the Checkov guideline and remediate the configuration.",
            }
        )

    if rc != 0 and not issues:
        issues.append(
            {
                "id": "checkov:failed",
                "severity": "medium",
                "category": "tooling",
                "resource": "checkov",
                "description": (err or out or "checkov failed").strip(),
                "recommendation": "Run `checkov -d . -o json` locally to inspect the full error.",
            }
        )
    return issues

