from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.schemas import (
    ScanRequest,
    ScanResponse,
    UploadRequest,
    UploadResponse,
)
from api.storage import load_result, load_upload, save_upload
from pipeline.run_scan import run_full_scan

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

