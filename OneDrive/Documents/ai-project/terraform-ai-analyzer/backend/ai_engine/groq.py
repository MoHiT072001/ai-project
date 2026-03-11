from __future__ import annotations

import os
from typing import Any, Dict, List

import httpx


def _default_response(reason: str) -> dict[str, Any]:
    return {
        "architecture": [],
        "attack_paths": [],
        "blast_radius": [],
        "cost": [],
        "tooling_notes": [
            {
                "id": "ai:disabled",
                "severity": "low",
                "category": "tooling",
                "resource": "groq",
                "description": reason,
                "recommendation": "Set GROQ_API_KEY to enable AI reasoning.",
            }
        ],
    }


def run_ai_reasoning(terraform_struct: dict[str, Any], graph_summary: dict[str, Any]) -> dict[str, Any]:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return _default_response("GROQ_API_KEY is not set.")

    model = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
    base_url = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")

    system = (
        "You are an expert cloud security engineer and infrastructure architect. "
        "Analyze the provided Terraform resources and dependency graph summary. "
        "Return ONLY valid JSON matching the required schema. "
        "Be precise, avoid speculation, and prefer actionable recommendations."
    )

    schema = {
        "architecture": [
            {
                "id": "string",
                "severity": "low|medium|high|critical",
                "category": "architecture",
                "resource": "string",
                "description": "string",
                "recommendation": "string",
            }
        ],
        "attack_paths": [
            {
                "id": "string",
                "severity": "low|medium|high|critical",
                "category": "attack_path",
                "resource": "string",
                "description": "string",
                "recommendation": "string",
            }
        ],
        "blast_radius": [
            {
                "id": "string",
                "severity": "low|medium|high|critical",
                "category": "blast_radius",
                "resource": "string",
                "description": "string",
                "recommendation": "string",
            }
        ],
        "cost": [
            {
                "id": "string",
                "severity": "low|medium|high|critical",
                "category": "cost",
                "resource": "string",
                "description": "string",
                "recommendation": "string",
            }
        ],
        "tooling_notes": [],
    }

    user = {
        "task": "Terraform infrastructure review",
        "terraform": {
            "providers": terraform_struct.get("providers", []),
            "resources": terraform_struct.get("resources", []),
            "categorized_resources": terraform_struct.get("categorized_resources", {}),
        },
        "graph": graph_summary,
        "output_schema": schema,
        "instructions": [
            "Populate arrays with issues you find; use stable ids (e.g., ai:arch:1).",
            "If nothing found in a category, return an empty array for that category.",
            "Do not include any markdown, only JSON.",
        ],
    }

    payload = {
        "model": model,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": str(user)},
        ],
    }

    try:
        with httpx.Client(timeout=45) as client:
            r = client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json=payload,
            )
            r.raise_for_status()
            data = r.json()
            content = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )
    except Exception as e:
        return _default_response(f"Groq request failed: {e}")

    # Best-effort JSON parse. If the model returned invalid JSON, degrade gracefully.
    try:
        import json

        parsed = json.loads(content)
        if isinstance(parsed, dict):
            parsed.setdefault("architecture", [])
            parsed.setdefault("attack_paths", [])
            parsed.setdefault("blast_radius", [])
            parsed.setdefault("cost", [])
            parsed.setdefault("tooling_notes", [])
            return parsed
    except Exception:
        pass

    return _default_response("Groq returned non-JSON output; enable stricter prompts or inspect logs.")

