#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIEWS = ROOT / "data" / "atlas-views.json"
REGISTRY = ROOT / "data" / "atlas-registry.json"


def main() -> int:
    views_doc = json.loads(VIEWS.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    views = views_doc.get("views", [])
    if not isinstance(views, list) or not views:
        raise SystemExit("ATLAS VIEWS FAILED: views must be a non-empty list")

    ids = [str(v.get("id", "")) for v in views if isinstance(v, dict)]
    routes = [str(v.get("route", "")) for v in views if isinstance(v, dict)]
    if len(ids) != len(set(ids)):
        raise SystemExit("ATLAS VIEWS FAILED: duplicate view id")
    if len(routes) != len(set(routes)):
        raise SystemExit("ATLAS VIEWS FAILED: duplicate view route")

    by_id = {str(v["id"]): v for v in views if isinstance(v, dict) and v.get("id")}
    for view_id, view in by_id.items():
        route = str(view.get("route", ""))
        if not route.startswith("/") or (route != "/" and not route.endswith("/")):
            raise SystemExit(f"ATLAS VIEWS FAILED: unstable route for {view_id}: {route}")
        if not str(view.get("title", "")).strip():
            raise SystemExit(f"ATLAS VIEWS FAILED: missing title for {view_id}")
        if not str(view.get("description", "")).strip():
            raise SystemExit(f"ATLAS VIEWS FAILED: missing description for {view_id}")
        if view.get("status") not in {"active", "legacy_view", "candidate"}:
            raise SystemExit(f"ATLAS VIEWS FAILED: invalid status for {view_id}")

    for node in registry.get("nodes", []):
        if not isinstance(node, dict):
            continue
        for view_id in node.get("views", []):
            if view_id not in by_id:
                raise SystemExit(f"ATLAS VIEWS FAILED: {node.get('id')} references unknown view {view_id}")

    print(f"ATLAS VIEWS PASSED: {len(by_id)} views")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
