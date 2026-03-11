from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scanners.runner import ToolMissing, run_cmd, try_parse_json, which


def _deny_query() -> str:
    # Expect Rego policies to expose: package terraform_ai; deny[violation]
    return "data.terraform_ai.deny"


def run_opa_policies(terraform_json: dict[str, Any], policies_root: Path) -> list[dict[str, Any]]:
    try:
        which("opa")
    except ToolMissing as e:
        return [
            {
                "id": "tool:opa_missing",
                "severity": "low",
                "category": "tooling",
                "resource": "opa",
                "description": str(e),
                "recommendation": "Install OPA and ensure `opa` is on PATH.",
            }
        ]

    if not policies_root.exists():
        return []

    # OPA input is passed via stdin. We evaluate all policies under policies_root.
    rc, out, err = run_cmd(
        [
            "opa",
            "eval",
            "--format",
            "json",
            "--data",
            str(policies_root),
            _deny_query(),
        ],
        cwd=policies_root,
        timeout_s=60,
        env=None,
    )

    # Unfortunately `opa eval` doesn't read stdin unless `--input` is used. Write a temp file instead.
    # MVP approach: create a small input.json in policies_root/.tmp_input.json; call again.
    tmp = policies_root / ".tmp_input.json"
    try:
        tmp.write_text(json.dumps(terraform_json), encoding="utf-8")
        rc, out, err = run_cmd(
            [
                "opa",
                "eval",
                "--format",
                "json",
                "--data",
                str(policies_root),
                "--input",
                str(tmp),
                _deny_query(),
            ],
            cwd=policies_root,
            timeout_s=60,
        )
    finally:
        try:
            tmp.unlink(missing_ok=True)  # type: ignore[arg-type]
        except Exception:
            pass

    data = try_parse_json(out) or {}
    issues: list[dict[str, Any]] = []

    # Expected: {"result":[{"expressions":[{"value":[...]}]}]}
    results = data.get("result") or []
    values = []
    if results and isinstance(results, list):
        exprs = (results[0] or {}).get("expressions") or []
        if exprs and isinstance(exprs, list):
            values = (exprs[0] or {}).get("value") or []

    for i, v in enumerate(values if isinstance(values, list) else []):
        if not isinstance(v, dict):
            continue
        issues.append(
            {
                "id": v.get("id") or f"opa:violation:{i}",
                "severity": v.get("severity") or "high",
                "category": "policy",
                "resource": v.get("resource") or "terraform",
                "description": v.get("description") or "Policy violation",
                "recommendation": v.get("recommendation") or "Update the configuration to satisfy policy.",
            }
        )

    if rc != 0 and not issues:
        issues.append(
            {
                "id": "opa:failed",
                "severity": "medium",
                "category": "tooling",
                "resource": "opa",
                "description": (err or out or "opa eval failed").strip(),
                "recommendation": "Run `opa eval` locally to inspect the full error and policy syntax.",
            }
        )

    return issues

