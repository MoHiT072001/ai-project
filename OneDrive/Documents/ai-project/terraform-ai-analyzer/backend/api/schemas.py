from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class UploadRequest(BaseModel):
    terraform_code: str = Field(..., min_length=1)


class UploadResponse(BaseModel):
    upload_id: str


class ScanRequest(BaseModel):
    terraform_code: Optional[str] = None
    upload_id: Optional[str] = None


class ScanResponse(BaseModel):
    scan_id: str


Severity = Literal["low", "medium", "high", "critical"]
IssueCategory = Literal["static", "policy", "architecture", "attack_path", "blast_radius", "cost", "tooling"]


class NormalizedIssue(BaseModel):
    id: str
    severity: Severity
    category: IssueCategory
    resource: str
    description: str
    recommendation: str

