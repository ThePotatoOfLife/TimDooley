#!/usr/bin/env python3
"""Fast structural validation for the religious-adjacent research layer."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERRORS = []

def load(rel):
    path = ROOT / rel
    if not path.exists():
        ERRORS.append(f"missing: {rel}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        ERRORS.append(f"invalid JSON: {rel}: {exc}")
        return {}

def unique_ids(records, label):
    values = [r.get("id") for r in records if isinstance(r, dict)]
    if len(values) != len(records): ERRORS.append(f"{label}: non-object or missing id")
    if len(values) != len(set(values)): ERRORS.append(f"{label}: duplicate ids")
    return set(values)

def main():
    required = [
        "data/religious-adjacent/records.json","data/religious-adjacent/index.json",
        "data/religious-adjacent/deep-expansions.json","data/religious-adjacent/deep-expansions-2.json",
        "data/religious-adjacent/deep-expansions-3.json","data/religious-adjacent/relationships.json",
        "data/religious-adjacent/graph-external-nodes.json","data/religious-adjacent/integrity-audit.json",
        "data/blueprints/religious-adjacent-blueprint.json","data/blueprints/mystery-cult-blueprint.json",
        "data/blueprints/occult-order-blueprint.json"]
    data = {p: load(p) for p in required}
    base = data["data/religious-adjacent/records.json"].get("records", [])
    index = data["data/religious-adjacent/index.json"]
    if len(base) != 22: ERRORS.append(f"base records: {len(base)} != 22")
    base_ids = unique_ids(base, "base records")
    expansion_files = [("data/religious-adjacent/deep-expansions.json",7),("data/religious-adjacent/deep-expansions-2.json",8),("data/religious-adjacent/deep-expansions-3.json",8)]
    expanded_ids = set()
    for rel, expected in expansion_files:
        records = data[rel].get("records", [])
        if len(records) != expected: ERRORS.append(f"{rel}: {len(records)} != {expected}")
        ids = unique_ids(records, rel)
        overlap = expanded_ids & ids
        if overlap: ERRORS.append(f"duplicate deep expansion across files: {sorted(overlap)}")
        expanded_ids |= ids
    if len(expanded_ids) != 23: ERRORS.append(f"unique deep expansions: {len(expanded_ids)} != 23")
    if not expanded_ids.issubset(base_ids | {"modern-satanism-cluster"}): ERRORS.append("deep expansion contains an unregistered id")
    if index.get("base_record_count") != 22: ERRORS.append("index base_record_count is stale")
    if index.get("deep_expansion_total") != 23: ERRORS.append("index deep_expansion_total is stale")
    external = data["data/religious-adjacent/graph-external-nodes.json"].get("nodes", [])
    external_ids = unique_ids(external, "external graph nodes")
    if len(external) != 12: ERRORS.append(f"external graph nodes: {len(external)} != 12")
    graph = data["data/religious-adjacent/relationships.json"]
    nodes, edges = graph.get("nodes", []), graph.get("edges", [])
    graph_ids = unique_ids(nodes, "graph nodes")
    if len(nodes) != 23: ERRORS.append(f"graph nodes: {len(nodes)} != 23")
    if graph.get("node_count") != len(nodes): ERRORS.append("graph node_count mismatch")
    if graph.get("edge_count") != len(edges): ERRORS.append("graph edge_count mismatch")
    allowed = graph_ids | external_ids
    for i, edge in enumerate(edges):
        if edge.get("from") not in allowed or edge.get("to") not in allowed: ERRORS.append(f"graph edge {i} has dangling endpoint")
        if not edge.get("relation") or not edge.get("basis") or not edge.get("evidence"): ERRORS.append(f"graph edge {i} lacks relationship evidence metadata")
    audit = data["data/religious-adjacent/integrity-audit.json"].get("summary", {})
    if audit.get("base_records_found") != 22: ERRORS.append("audit base count is stale")
    if audit.get("deep_expansion_records") != 23: ERRORS.append("audit deep-expansion count is stale")
    if audit.get("base_records_without_deep_expansion") != 0: ERRORS.append("audit still reports base records without deep expansion")
    if audit.get("dangling_graph_edges") != 0: ERRORS.append("audit reports dangling graph edges")
    print(f"base={len(base)} deep={len(expanded_ids)} graph_nodes={len(nodes)} external={len(external)} edges={len(edges)} errors={len(ERRORS)}")
    for error in ERRORS: print(f"ERROR: {error}")
    return 1 if ERRORS else 0

if __name__ == "__main__": raise SystemExit(main())
