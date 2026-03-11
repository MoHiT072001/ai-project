from __future__ import annotations

from pathlib import Path
from typing import Any

from scanners.runner import ToolMissing, run_cmd, try_parse_json, which


def run(workdir: Path) -> list[dict[str, Any]]:
    try:
        which("terraform")
    except ToolMissing as e:
        return [
            {
                "id": "tool:terraform_missing",
                "severity": "low",
                "category": "tooling",
                "resource": "terraform",
                "description": str(e),
                "recommendation": "Install Terraform and ensure `terraform` is on PATH.",
            }
        ]

    # Ensure init so validate can run. This is best-effort and may fail without providers.
    run_cmd(["terraform", "init", "-input=false", "-no-color"], cwd=workdir, timeout_s=180)

    rc, out, err = run_cmd(
        ["terraform", "validate", "-no-color", "-json"],
        cwd=workdir,
        timeout_s=120,
    )
    data = try_parse_json(out) or {}
    diags = data.get("diagnostics") or []
    issues: list[dict[str, Any]] = []
    for d in diags:
        sev = d.get("severity") or "error"
        severity = "high" if sev in {"error"} else "medium"
        summary = d.get("summary") or "Terraform validation issue"
        detail = d.get("detail") or ""
        address = "terraform"
        if isinstance(d.get("range"), dict):
            address = f'{d["range"].get("filename","terraform")}'

        issues.append(
            {
                "id": f"terraform_validate:{summary}",
                "severity": severity,
                "category": "static",
                "resource": address,
                "description": (summary + (f" — {detail}" if detail else "")).strip(),
                "recommendation": "Fix the Terraform configuration so `terraform validate` passes.",
            }
        )

    if rc != 0 and not issues:
        issues.append(
            {
                "id": "terraform_validate:failed",
                "severity": "medium",
                "category": "tooling",
                "resource": "terraform",
                "description": (err or out or "terraform validate failed").strip(),
                "recommendation": "Run `terraform validate` locally to inspect the full error.",
            }
        )
    return issues

