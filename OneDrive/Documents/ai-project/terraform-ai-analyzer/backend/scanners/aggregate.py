from __future__ import annotations

from pathlib import Path
from typing import Any

from scanners.checkov_scanner import run as run_checkov
from scanners.terraform_validate import run as run_terraform_validate
from scanners.tfsec_scanner import run as run_tfsec
from scanners.tflint_scanner import run as run_tflint


def run_static_scanners(workdir: Path) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    issues.extend(run_terraform_validate(workdir))
    issues.extend(run_tflint(workdir))
    issues.extend(run_tfsec(workdir))
    issues.extend(run_checkov(workdir))
    return issues

