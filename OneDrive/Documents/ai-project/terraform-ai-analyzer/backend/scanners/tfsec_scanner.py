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
        which("tfsec")
    except ToolMissing as e:
        return [
            {
                "id": "tool:tfsec_missing",
                "severity": "low",
                "category": "tooling",
                "resource": "tfsec",
                "description": str(e),
                "recommendation": "Install tfsec and ensure `tfsec` is on PATH.",
            }
        ]

    rc, out, err = run_cmd(["tfsec", "--format", "json"], cwd=workdir, timeout_s=240)
    data = try_parse_json(out) or {}
    issues: list[dict[str, Any]] = []
    for i, r in enumerate(data.get("results") or []):
        rule_id = r.get("rule_id") or r.get("id") or "tfsec"
        sev = (r.get("severity") or "MEDIUM").upper()
        desc = r.get("description") or r.get("long_id") or "tfsec finding"
        res = r.get("resource") or "terraform"
        rec = r.get("resolution") or "Review tfsec guidance for this finding."
        issues.append(
            {
                "id": f"tfsec:{rule_id}:{i}",
                "severity": _SEV_MAP.get(sev, "medium"),
                "category": "static",
                "resource": res,
                "description": desc,
                "recommendation": rec,
            }
        )

    if rc != 0 and not issues:
        issues.append(
            {
                "id": "tfsec:failed",
                "severity": "medium",
                "category": "tooling",
                "resource": "tfsec",
                "description": (err or out or "tfsec failed").strip(),
                "recommendation": "Run `tfsec --format json` locally to inspect the full error.",
            }
        )
    return issues

