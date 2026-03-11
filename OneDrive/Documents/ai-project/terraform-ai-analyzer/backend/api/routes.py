from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.schemas import (
    ScanRequest,
    ScanResponse,
    UploadRequest,
    UploadResponse,
    UpgradeRequest,
    UpgradeResponse,
)
from api.storage import load_result, load_upload, new_id, save_upload, scan_workspace
from graph_engine.builder import build_dependency_graph, graph_insights
from parser.terraform_parser import parse_terraform
from pipeline.run_scan import run_full_scan
from ai_engine.upgrade import run_ai_upgrade

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
def upload(req: UploadRequest) -> UploadResponse:
    upload_id = save_upload(req.terraform_code)
    return UploadResponse(upload_id=upload_id)


@router.post("/scan", response_model=ScanResponse)
def scan(req: ScanRequest) -> ScanResponse:
    terraform_code = req.terraform_code
    if terraform_code is None and req.upload_id:
        terraform_code = load_upload(req.upload_id)
        if terraform_code is None:
            raise HTTPException(status_code=404, detail="upload_id not found")

    if not terraform_code or not terraform_code.strip():
        raise HTTPException(status_code=400, detail="terraform_code or upload_id is required")

    result = run_full_scan(terraform_code=terraform_code)
    return ScanResponse(scan_id=result.scan_id)


@router.get("/results/{scan_id}")
def results(scan_id: str):
    data = load_result(scan_id)
    if data is None:
        raise HTTPException(status_code=404, detail="scan_id not found")
    return data


@router.post("/ai/upgrade", response_model=UpgradeResponse)
def ai_upgrade(req: UpgradeRequest) -> UpgradeResponse:
    terraform_code = req.terraform_code
    if not terraform_code or not terraform_code.strip():
        raise HTTPException(status_code=400, detail="terraform_code is required")

    # Reuse the isolated scan workspace pattern for safety.
    upgrade_id = new_id("upgrade")
    workdir = scan_workspace(upgrade_id)
    (workdir / "main.tf").write_text(terraform_code, encoding="utf-8")

    parsed = parse_terraform(workdir=workdir)
    graph = build_dependency_graph(parsed_resources=parsed.get("resources", []))
    graph_summary = graph_insights(graph)

    ai = run_ai_upgrade(
        terraform_code=terraform_code,
        terraform_struct=parsed,
        graph_summary=graph_summary,
    )
    return UpgradeResponse(
        upgraded_code=ai.get("upgraded_code", terraform_code),
        suggestions=ai.get("suggestions", []),
    )

