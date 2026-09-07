#!/usr/bin/env python3
"""Audit backend ownership, duplicate IDs and graph reachability.

The repository intentionally contains schema, research, source, overlay and
canonical-record layers. This audit therefore distinguishes a legitimate
backend-only file from an orphan instead of requiring every JSON file to have
an HTML page.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
COVERAGE = DATA / "backend-coverage-map.json"
BRIDGE = DATA / "global-graph-bridge.json"
MANIFEST = DATA / "atlas-manifest.json"
BACKEND = DATA / "backend.json"


def load(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def iter_json_files():
    return sorted(DATA.rglob("*.json"))


def object_ids(value):
    """Yield plausible record IDs from nested JSON without treating every scalar as an ID."""
    if isinstance(value, dict):
        if isinstance(value.get("id"), str) and value["id"].strip():
            yield value["id"].strip()
        for key in ("records", "nodes", "items", "entries", "observations", "relationships", "edges", "sources", "waves", "dimensions", "layers", "links"):
            if key in value:
                yield from object_ids(value[key])
        for key, child in value.items():
            if key not in {"records", "nodes", "items", "entries", "observations", "relationships", "edges", "sources", "waves", "dimensions", "layers", "links"}:
                if isinstance(child, (dict, list)):
                    yield from object_ids(child)
    elif isinstance(value, list):
        for item in value:
            yield from object_ids(item)


def relationship_endpoints(value):
    if isinstance(value, dict):
        source = value.get("source") or value.get("from") or value.get("subject")
        target = value.get("target") or value.get("to") or value.get("object")
        if isinstance(source, str) and isinstance(target, str):
            yield source, target
        for child in value.values():
            if isinstance(child, (dict, list)):
                yield from relationship_endpoints(child)
    elif isinstance(value, list):
        for item in value:
            yield from relationship_endpoints(item)


def collect_registered_files(obj):
    found = set()
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in {"file", "files", "endpoint", "source", "owner", "backend", "canonicalManifest", "maintenanceWorkflow"}:
                if isinstance(value, str) and value.startswith(("data/", "docs/")):
                    found.add(value)
                elif isinstance(value, list):
                    found.update(x for x in value if isinstance(x, str) and x.startswith(("data/", "docs/")))
            found |= collect_registered_files(value)
    elif isinstance(obj, list):
        for item in obj:
            found |= collect_registered_files(item)
    return found


def matches_pattern(path: str, patterns):
    for pattern in patterns:
        if "*" in pattern:
            rx = "^" + re.escape(pattern).replace(r"\*", ".*") + "$"
            if re.match(rx, path):
                return True
        elif path == pattern:
            return True
    return False


def main():
    coverage = load(COVERAGE)
    bridge = load(BRIDGE)
    manifest = load(MANIFEST)
    backend = load(BACKEND)

    coverage_patterns = [x["file"] for x in coverage.get("layers", [])]
    registered = collect_registered_files(manifest) | collect_registered_files(backend) | set(coverage_patterns)

    files = iter_json_files()
    file_paths = {p.relative_to(ROOT).as_posix() for p in files}
    missing_owners = sorted(p for p in file_paths if not matches_pattern(p, coverage_patterns) and p not in registered)

    id_locations: dict[str, list[str]] = {}
    content_hashes: dict[str, list[str]] = {}
    endpoint_files = {}

    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        raw = path.read_bytes()
        content_hashes.setdefault(hashlib.sha256(raw).hexdigest(), []).append(rel)
        try:
            value = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise SystemExit(f"INVALID JSON: {rel}: {exc}")
        for ident in object_ids(value):
            id_locations.setdefault(ident, []).append(rel)
        for source, target in relationship_endpoints(value):
            endpoint_files.setdefault(source, []).append(rel)
            endpoint_files.setdefault(target, []).append(rel)

    duplicate_ids = {k: v for k, v in id_locations.items() if len(set(v)) > 1}
    exact_duplicates = {k: sorted(v) for k, v in content_hashes.items() if len(v) > 1}

    bridge_ids = {x.get("id") for x in bridge.get("explicit_bridges", []) if isinstance(x, dict)}
    registry_ids = set()
    graph_registry = DATA / "graph-registry.json"
    if graph_registry.exists():
        registry_ids.update(object_ids(load(graph_registry)))
    node_ids = set()
    nodes = DATA / "nodes.json"
    if nodes.exists():
        node_ids.update(object_ids(load(nodes)))
    known_graph_ids = bridge_ids | registry_ids | node_ids
    relationship_only = sorted(i for i in endpoint_files if i not in known_graph_ids and i not in {"<id>", "<country-id>", "<slug>"})

    # Research-only files are valid if explicitly declared in expansion/source/blueprint coverage.
    report = {
        "version": "1.0.0",
        "files_scanned": len(files),
        "registered_or_covered_files": sum(1 for p in file_paths if matches_pattern(p, coverage_patterns) or p in registered),
        "unmapped_files": missing_owners,
        "duplicate_ids": {k: sorted(set(v)) for k, v in sorted(duplicate_ids.items())},
        "exact_duplicate_file_contents": exact_duplicates,
        "relationship_only_unresolved_ids": relationship_only,
        "bridge_explicit_ids": len(bridge_ids),
        "graph_registry_ids": len(registry_ids),
        "node_ids": len(node_ids),
        "notes": [
            "Duplicate IDs are candidates, not automatic deletion targets: overlays and research expansions can legitimately repeat an ID when inheritance is explicit.",
            "Exact duplicate files are candidates for consolidation after consumer migration.",
            "Unresolved relationship endpoints are the strongest orphan signal and should either be promoted, bridged or removed.",
            "Schema and source files can remain backend-only when their owner and consumer are explicit."
        ]
    }
    out = DATA / "backend-coverage-report.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    critical = bool(duplicate_ids) or bool(relationship_only) or bool(missing_owners)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if critical:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
