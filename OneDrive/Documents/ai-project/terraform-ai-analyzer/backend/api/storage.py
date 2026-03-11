from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


def _root_dir() -> Path:
    return Path(__file__).resolve().parents[2]  # .../backend


def uploads_dir() -> Path:
    return _root_dir().parent / "uploads"


def scans_dir() -> Path:
    return uploads_dir() / "scans"


def results_dir() -> Path:
    return uploads_dir() / "results"


def ensure_dirs() -> None:
    scans_dir().mkdir(parents=True, exist_ok=True)
    results_dir().mkdir(parents=True, exist_ok=True)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def save_upload(terraform_code: str) -> str:
    ensure_dirs()
    upload_id = new_id("upload")
    path = uploads_dir() / f"{upload_id}.tf"
    path.write_text(terraform_code, encoding="utf-8")
    return upload_id


def load_upload(upload_id: str) -> Optional[str]:
    path = uploads_dir() / f"{upload_id}.tf"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def scan_workspace(scan_id: str) -> Path:
    ensure_dirs()
    d = scans_dir() / scan_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_result(scan_id: str, payload: dict[str, Any]) -> None:
    ensure_dirs()
    payload = dict(payload)
    payload.setdefault("scan_id", scan_id)
    payload.setdefault("generated_at", datetime.now(timezone.utc).isoformat())
    out = results_dir() / f"{scan_id}.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_result(scan_id: str) -> Optional[dict[str, Any]]:
    path = results_dir() / f"{scan_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

