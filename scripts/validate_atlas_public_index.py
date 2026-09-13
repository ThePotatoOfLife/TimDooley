#!/usr/bin/env python3
"""Validate the generated, non-authoritative public Atlas machine index."""
from __future__ import annotations

import json
from pathlib import Path

from atlas_runtime import build_runtime

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
INDEX = OUT / "data" / "atlas-index.json"


def fail(message: str) -> None:
    raise SystemExit(f"ATLAS PUBLIC INDEX FAILED: {message}")


def main() -> int:
    if not INDEX.exists():
        fail("_site/data/atlas-index.json missing")
    doc = json.loads(INDEX.read_text(encoding="utf-8"))
    runtime = build_runtime()
    if doc.get("schema_version") != "1.0.0":
        fail("schema version")
    if doc.get("root_id") != runtime.get("root_id"):
        fail("root mismatch")
    nodes = doc.get("nodes")
    if not isinstance(nodes, list) or len(nodes) != len(runtime.get("nodes", [])):
        fail("node count mismatch")
    ids = {str(node.get("id")) for node in nodes if isinstance(node, dict)}
    runtime_ids = {str(node.get("id")) for node in runtime.get("nodes", []) if isinstance(node, dict)}
    if ids != runtime_ids:
        fail("node identity mismatch")
    forbidden = {"owner_path", "sections", "owner_id", "owner_title"}
    for node in nodes:
        if forbidden & set(node):
            fail(f"backend-only fields leaked for {node.get('id')}")
        for field in ("id", "title", "route", "summary", "children", "views", "relations", "artifacts"):
            if field not in node:
                fail(f"{node.get('id')} missing {field}")
        route = str(node.get("route", ""))
        page = OUT / route.strip("/") / "index.html"
        if not route.startswith("/atlas/") or not page.exists():
            fail(f"missing generated page for {node.get('id')}")
    views = doc.get("views")
    if not isinstance(views, list) or len(views) != len(runtime.get("views", [])):
        fail("view projection mismatch")
    print(f"ATLAS PUBLIC INDEX PASSED: {len(nodes)} nodes, {len(views)} views")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
