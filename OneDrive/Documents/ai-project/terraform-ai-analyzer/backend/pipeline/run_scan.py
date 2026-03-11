from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from api.storage import new_id, save_result, scan_workspace
from parser.terraform_parser import parse_terraform
from scanners.aggregate import run_static_scanners
from policy_engine.opa import run_opa_policies
from graph_engine.builder import build_dependency_graph, graph_insights
from ai_engine.groq import run_ai_reasoning


@dataclass(frozen=True)
class ScanRun:
    scan_id: str


def run_full_scan(terraform_code: str) -> ScanRun:
    scan_id = new_id("scan")
    workdir = scan_workspace(scan_id)
    (workdir / "main.tf").write_text(terraform_code, encoding="utf-8")

    parsed = parse_terraform(workdir=workdir)
    graph = build_dependency_graph(parsed_resources=parsed["resources"])
    graph_summary = graph_insights(graph)

    static_issues = run_static_scanners(workdir=workdir)
    policy_issues = run_opa_policies(
        terraform_json=parsed,
        policies_root=workdir.parent.parent / "policies",
    )

    ai = run_ai_reasoning(terraform_struct=parsed, graph_summary=graph_summary)

    report: dict[str, Any] = {
        "scan_id": scan_id,
        "inputs": {
            "resource_count": len(parsed.get("resources", [])),
            "providers": parsed.get("providers", []),
        },
        "summary": ai.get("summary", {}),
        "changes": ai.get("changes", []),
        "migration_guide": ai.get("migration_guide", []),
        "recommendations": ai.get("recommendations", []),
        "static_issues": static_issues,
        "policy_violations": policy_issues,
        "graph": graph_summary,
        "ai_architecture_insights": ai.get("architecture", []),
        "ai_attack_paths": ai.get("attack_paths", []),
        "ai_blast_radius": ai.get("blast_radius", []),
        "ai_cost_optimizations": ai.get("cost", []),
        "tooling_notes": ai.get("tooling_notes", []),
    }
    save_result(scan_id, report)
    return ScanRun(scan_id=scan_id)

