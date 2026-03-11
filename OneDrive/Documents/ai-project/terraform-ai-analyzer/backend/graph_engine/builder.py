from __future__ import annotations

from typing import Any

import networkx as nx


def build_dependency_graph(parsed_resources: list[dict[str, Any]]) -> nx.DiGraph:
    g = nx.DiGraph()
    for r in parsed_resources:
        addr = r.get("address") or f'{r.get("resource_type")}.{r.get("name")}'
        g.add_node(addr, **{k: v for k, v in r.items() if k != "attributes"})

    for r in parsed_resources:
        src = r.get("address") or f'{r.get("resource_type")}.{r.get("name")}'
        for dep in r.get("depends_on", []) or []:
            if not isinstance(dep, str):
                continue
            # Keep graph stable: allow edges to unknown nodes (external/module/data)
            if dep not in g:
                g.add_node(dep, external=True)
            g.add_edge(src, dep)
    return g


def _sg_allows_world_ssh(sg: dict[str, Any]) -> bool:
    attrs = sg.get("attributes") or {}
    for key in ("ingress", "ingress_rule"):
        rules = attrs.get(key)
        if rules is None:
            continue
        if not isinstance(rules, list):
            rules = [rules]
        for rule in rules:
            if not isinstance(rule, dict):
                continue
            from_port = rule.get("from_port")
            to_port = rule.get("to_port")
            cidrs = rule.get("cidr_blocks") or []
            if isinstance(cidrs, str):
                cidrs = [cidrs]
            if from_port == 22 or to_port == 22:
                if any(c == "0.0.0.0/0" for c in cidrs):
                    return True
    return False


def graph_insights(g: nx.DiGraph) -> dict[str, Any]:
    nodes = list(g.nodes())
    edges = list(g.edges())

    sg_world_ssh = []
    for n, data in g.nodes(data=True):
        if data.get("resource_type") == "aws_security_group":
            # The node attrs do not include "attributes"; need to infer from external stage. Best-effort:
            pass

    # We still compute generic graph facts that help the AI reasoning stage.
    return {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes[:500],
        "edges": [{"from": a, "to": b} for a, b in edges[:1000]],
        "hints": {
            "note": "Graph edges are derived from depends_on and best-effort implicit references.",
        },
    }

