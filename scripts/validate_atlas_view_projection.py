#!/usr/bin/env python3
"""Require the frontend bridge to project configurable Atlas Views, not five-door ontology."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "data/frontend-atlas-bridge.json"
VIEWS = ROOT / "data/atlas-views.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    bridge = load(BRIDGE)
    views_doc = load(VIEWS)
    views = {
        str(row.get("id")): row
        for row in views_doc.get("views", [])
        if isinstance(row, dict) and row.get("id")
    }

    projection = bridge.get("atlas_view_projection")
    if not isinstance(projection, dict):
        raise SystemExit("ATLAS VIEW PROJECTION FAILED: frontend bridge lacks atlas_view_projection")
    if projection.get("source") != "data/atlas-views.json":
        raise SystemExit("ATLAS VIEW PROJECTION FAILED: atlas-views.json must own public Room definitions")
    if projection.get("authority") != "view_registry":
        raise SystemExit("ATLAS VIEW PROJECTION FAILED: public projection authority must be view_registry")

    legacy = bridge.get("public_doors")
    if legacy is not None:
        if bridge.get("public_doors_status") != "compatibility_only":
            raise SystemExit("ATLAS VIEW PROJECTION FAILED: public_doors may remain only as compatibility_only")
        if not isinstance(legacy, dict):
            raise SystemExit("ATLAS VIEW PROJECTION FAILED: compatibility public_doors must remain a route map")
        for view_id, path in legacy.items():
            if view_id not in views:
                raise SystemExit(f"ATLAS VIEW PROJECTION FAILED: compatibility door {view_id} is not an Atlas View")
            expected = str(views[view_id].get("route", "")).strip("/") + "/"
            if path != expected:
                raise SystemExit(f"ATLAS VIEW PROJECTION FAILED: compatibility route drift for {view_id}")

    for branch_id, row in bridge.get("branch_projection", {}).items():
        if not isinstance(row, dict):
            continue
        primary = row.get("primary_view")
        if primary is not None and primary not in views:
            raise SystemExit(f"ATLAS VIEW PROJECTION FAILED: branch {branch_id} references unknown primary_view {primary}")

    requirements = " ".join(str(x).lower() for x in bridge.get("integrity_requirements", []))
    design_rule = str(bridge.get("design_rule", "")).lower()
    if "exactly five" in requirements or "exactly five" in design_rule:
        raise SystemExit("ATLAS VIEW PROJECTION FAILED: exact-five-door ontology remains in bridge contract")

    print(f"ATLAS VIEW PROJECTION PASS: {len(views)} configurable Views own public projection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
