#!/usr/bin/env python3
"""Validate the religious-adjacent research layer, expansions and relationship graph."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []


def load(rel: str):
    p = ROOT / rel
    if not p.exists():
        ERRORS.append(f"Missing required file: {rel}")
        return {}
    try:
        with p.open(encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        ERRORS.append(f"Invalid JSON: {rel} — {exc}")
        return {}


def walk_empty(value, path="root"):
    if isinstance(value, dict):
        for k, v in value.items():
            walk_empty(v, f"{path}.{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            walk_empty(v, f"{path}[{i}]")
    elif isinstance(value, str) and not value.strip():
        ERRORS.append(f"Blank string field: {path}")


def ids(records, label):
    out = []
    for i, record in enumerate(records):
        if not isinstance(record, dict) or not record.get("id"):
            ERRORS.append(f"{label}[{i}] has no id")
        else:
            out.append(record["id"])
    if len(out) != len(set(out)):
        dupes = sorted({x for x in out if out.count(x) > 1})
        ERRORS.append(f"Duplicate {label} ids: {dupes}")
    return set(out)


def main():
    base = load("data/religious-adjacent/records.json")
    index = load("data/religious-adjacent/index.json")
    audit = load("data/religious-adjacent/integrity-audit.json")
    graph = load("data/religious-adjacent/relationships.json")
    external = load("data/religious-adjacent/graph-external-nodes.json")
    manifest = load("data/religious-layer-manifest.json")

    blueprint_paths = [
        "data/blueprints/religious-adjacent-master.json",
        "data/blueprints/mystery-cult-master.json",
        "data/blueprints/occult-order-master.json",
    ]
    for p in blueprint_paths:
        load(p)

    base_records = base.get("records", []) if isinstance(base, dict) else []
    base_ids = ids(base_records, "base record")
    if len(base_records) != 22:
        ERRORS.append(f"Base adjacent record count is {len(base_records)}; expected 22")
    if index.get("base_record_count") != len(base_records):
        ERRORS.append("Adjacent index base_record_count does not match records.json")

    expansion_paths = [
        ("data/religious-adjacent/deep-expansions.json", 7),
        ("data/religious-adjacent/deep-expansions-2.json", 8),
        ("data/religious-adjacent/deep-expansions-3.json", 8),
    ]
    expanded_ids: set[str] = set()
    for rel, expected in expansion_paths:
        d = load(rel)
        records = d.get("records", []) if isinstance(d, dict) else []
        rid = ids(records, rel)
        if len(records) != expected:
            ERRORS.append(f"{rel} has {len(records)} records; expected {expected}")
        overlap = expanded_ids & rid
        if overlap:
            # Theosophical Society intentionally appears in two expansion layers only if this becomes a duplicate;
            # current architecture should not duplicate it.
            ERRORS.append(f"Duplicate deep-expansion ids across files: {sorted(overlap)}")
        expanded_ids |= rid
        for r in records:
            walk_empty(r, rel)

    # Theosophical Society was intentionally enriched twice in the historical pass; keep one canonical deep record.
    # Detect this as a bug rather than silently allowing two competing enrichments.
    if "theosophical-society" in expanded_ids and sum(
        "theosophical-society" in (load(rel).get("records", []) if isinstance(load(rel), dict) else [])
        for rel, _ in expansion_paths
    ) > 1:
        ERRORS.append("Theosophical Society appears in more than one deep-expansion file")

    if index.get("deep_expansion_total") != len(expanded_ids):
        ERRORS.append(f"Adjacent index deep_expansion_total={index.get('deep_expansion_total')} but union has {len(expanded_ids)} unique ids")

    external_records = external.get("nodes", []) if isinstance(external, dict) else []
    external_ids = ids(external_records, "external graph node")
    walk_empty(external, "graph-external-nodes")

    graph_nodes = graph.get("nodes", []) if isinstance(graph, dict) else []
    graph_node_ids = ids(graph_nodes, "graph node")
    edge_targets = set()
    for i, edge in enumerate(graph.get("edges", [])):
        if not isinstance(edge, dict):
            ERRORS.append(f"Graph edge {i} is not an object")
            continue
        for side in ("from", "to"):
            value = edge.get(side)
            if not value:
                ERRORS.append(f"Graph edge {i} missing {side}")
            else:
                edge_targets.add(value)
                if value not in graph_node_ids and value not in external_ids:
                    ERRORS.append(f"Graph edge {i} has unknown {side}: {value}")
        if not edge.get("relation") or not edge.get("basis") or not edge.get("evidence"):
            ERRORS.append(f"Graph edge {i} is missing relation, basis or evidence")

    if graph.get("node_count") != len(graph_nodes):
        ERRORS.append("Graph node_count does not match nodes array")
    if graph.get("edge_count") != len(graph.get("edges", [])):
        ERRORS.append("Graph edge_count does not match edges array")
    duplicate_edges = set()
    for edge in graph.get("edges", []):
        key = (edge.get("from"), edge.get("to"), edge.get("relation"), edge.get("basis"))
        if key in duplicate_edges:
            ERRORS.append(f"Duplicate graph edge: {key}")
        duplicate_edges.add(key)

    if not expanded_ids.issubset(base_ids | {"modern-satanism-cluster"}):
        unexpected = sorted(expanded_ids - base_ids - {"modern-satanism-cluster"})
        ERRORS.append(f"Deep expansion ids not represented by base registry or explicit cluster: {unexpected}")

    audit_summary = audit.get("summary", {})
    if audit_summary.get("base_records_expected") != 22:
        ERRORS.append("Integrity audit base_records_expected is not 22")
    if audit_summary.get("deep_expansion_records") != len(expanded_ids):
        ERRORS.append("Integrity audit deep-expansion count is stale")
    if audit_summary.get("graph_external_nodes") != len(external_ids):
        ERRORS.append("Integrity audit external-node count is stale")

    # Check all linked paths declared by the manifest/index.
    linked = [
        index.get("base_records"),
        index.get("relationship_graph"),
        index.get("external_graph_nodes"),
        index.get("audit"),
        manifest.get("adjacent_records"),
        manifest.get("adjacent_index"),
        manifest.get("adjacent_relationship_graph"),
        manifest.get("adjacent_external_graph_nodes"),
        manifest.get("adjacent_integrity_audit"),
    ]
    for rel in linked:
        if rel and not (ROOT / rel).exists():
            ERRORS.append(f"Declared linked path does not exist: {rel}")

    print(f"Base adjacent records: {len(base_records)}")
    print(f"Deep expansion records: {len(expanded_ids)}")
    print(f"Graph nodes: {len(graph_nodes)} + {len(external_ids)} external")
    print(f"Graph edges: {len(graph.get('edges', []))}")
    print(f"Errors: {len(ERRORS)}")
    for error in ERRORS:
        print("ERROR:", error)
    return 1 if ERRORS else 0


if __name__ == "__main__":
    raise SystemExit(main())
