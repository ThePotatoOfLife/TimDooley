#!/usr/bin/env python3
"""Require Atlas roads to resolve against both Nodes and registered Artifacts."""
from __future__ import annotations

from atlas_runtime import build_runtime
from atlas_model import by_id


def relation(node: dict, target: str) -> dict:
    for row in node.get("relations", []):
        if row.get("target") == target:
            return row
    raise SystemExit(f"ATLAS RELATION RESOLUTION FAILED: missing relation {node.get('id')} -> {target}")


def require_artifact(node: dict, target: str, artifact_id: str) -> None:
    row = relation(node, target)
    if row.get("resolved") is not True:
        raise SystemExit(f"ATLAS RELATION RESOLUTION FAILED: unresolved Artifact target {target}")
    if row.get("resolved_kind") != "artifact":
        raise SystemExit(f"ATLAS RELATION RESOLUTION FAILED: {target} resolved as {row.get('resolved_kind')}")
    if row.get("artifact_id") != artifact_id:
        raise SystemExit(f"ATLAS RELATION RESOLUTION FAILED: {target} expected Artifact {artifact_id}")


def main() -> int:
    runtime = build_runtime()
    nodes = by_id(runtime)
    require_artifact(nodes["heaven-spirit-father"], "developmental-genealogy", "developmental-genealogy")
    require_artifact(nodes["root-system"], "THE-TURNING-APRIL-2025.md", "turning-april-2025")
    node_relation = relation(nodes["root-system"], "geometry-vesica-pisces-mandorla")
    if node_relation.get("resolved_kind") != "node" or node_relation.get("resolved") is not True:
        raise SystemExit("ATLAS RELATION RESOLUTION FAILED: Node target no longer resolves as node")
    print("ATLAS RELATION RESOLUTION PASSED: Node and Artifact targets resolve without ambiguity")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
