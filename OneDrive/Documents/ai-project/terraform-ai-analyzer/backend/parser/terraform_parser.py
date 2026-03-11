from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import hcl2


def _as_list(x: Any) -> list[Any]:
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return [x]


def _collect_providers(doc: dict[str, Any]) -> list[str]:
    providers: set[str] = set()
    for p in _as_list(doc.get("provider")):
        if isinstance(p, dict):
            providers.update(p.keys())
    return sorted(providers)


def _normalize_resource(resource_type: str, name: str, body: dict[str, Any]) -> dict[str, Any]:
    deps = []
    explicit = body.get("depends_on")
    if explicit is not None:
        for d in _as_list(explicit):
            if isinstance(d, str):
                deps.append(d)

    # Best-effort implicit dependencies via interpolation tokens: aws_x.y / module.x / data.x.y
    text = str(body)
    implicit = set(re.findall(r"\b(?:data\.)?([a-zA-Z0-9_]+)\.([a-zA-Z0-9_-]+)\b", text))
    for rtype, rname in implicit:
        # skip self-ish or common words
        if rtype in {"var", "local", "path", "terraform", "each", "count"}:
            continue
        deps.append(f"{rtype}.{rname}")

    r: dict[str, Any] = {
        "resource_type": resource_type,
        "name": name,
        "address": f"{resource_type}.{name}",
        "depends_on": sorted({d for d in deps if isinstance(d, str) and d}),
        "attributes": body,
    }

    if resource_type == "aws_instance":
        it = body.get("instance_type")
        if isinstance(it, str):
            r["instance_type"] = it
    if resource_type in {"aws_s3_bucket", "aws_s3_bucket_public_access_block"}:
        bn = body.get("bucket")
        if isinstance(bn, str):
            r["bucket"] = bn
    return r


def parse_terraform(workdir: Path) -> dict[str, Any]:
    resources: list[dict[str, Any]] = []
    providers: set[str] = set()
    raw_docs: list[dict[str, Any]] = []

    for tf in sorted(workdir.glob("*.tf")):
        with tf.open("r", encoding="utf-8") as f:
            doc = hcl2.load(f)
        raw_docs.append(doc)
        for p in _collect_providers(doc):
            providers.add(p)

        for block in _as_list(doc.get("resource")):
            if not isinstance(block, dict):
                continue
            for resource_type, instances in block.items():
                if not isinstance(instances, dict):
                    continue
                for name, body in instances.items():
                    if isinstance(body, dict):
                        resources.append(_normalize_resource(resource_type, name, body))

    categorized = {
        "networking": [],
        "iam": [],
        "compute": [],
        "storage": [],
        "other": [],
    }

    for r in resources:
        rt = r["resource_type"]
        if rt.startswith(("aws_vpc", "aws_subnet", "aws_route", "aws_internet_gateway", "aws_nat_gateway", "aws_security_group", "aws_network_acl")):
            categorized["networking"].append(r)
        elif rt.startswith(("aws_iam_",)):
            categorized["iam"].append(r)
        elif rt.startswith(("aws_instance", "aws_autoscaling_", "aws_launch_template", "aws_lb", "aws_ecs_", "aws_eks_")):
            categorized["compute"].append(r)
        elif rt.startswith(("aws_s3_", "aws_ebs_", "aws_db_", "aws_rds_", "aws_dynamodb_", "aws_elasticache_")):
            categorized["storage"].append(r)
        else:
            categorized["other"].append(r)

    return {
        "providers": sorted(providers),
        "resources": resources,
        "categorized_resources": categorized,
        "raw": raw_docs,
    }

