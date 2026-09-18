#!/usr/bin/env python3
"""Build/check the derived public-route topology compatibility projection.

Canonical route identity lives in data/house/public-surfaces.json.
This file exists only for consumers that still expect the older topology ledger shape.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SURFACES = ROOT / "data/house/public-surfaces.json"
TOPOLOGY = ROOT / "knowledge/research/potato-house-master/public-route-topology.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_records(surface_doc: dict) -> list[dict]:
    gateways = set(surface_doc.get("primary_gateway_ids") or [])
    surface_by_id = {
        row.get("id"): row
        for row in surface_doc.get("surfaces") or []
        if isinstance(row, dict) and row.get("id")
    }
    records = []
    for row in surface_doc.get("surfaces") or []:
        if not isinstance(row, dict) or row.get("status") != "active":
            continue
        sid = row.get("id")
        parent = row.get("primary_parent")
        parent_row = surface_by_id.get(parent) or {}
        parent_can_hub = parent_row.get("surface_type") in {"hub", "explorer"} and parent != "home"
        primary_hub = sid if sid in gateways else (parent if parent_can_hub else None)
        records.append({
            "surface_id": sid,
            "surface_type": row.get("surface_type"),
            "canonical_route": row.get("canonical_route"),
            "primary_hub_id": primary_hub,
            "room_ids": row.get("primary_room_ids") or [],
            "specialist_view": sid != "home" and sid not in gateways,
            "migration_status": "current",
            "compatibility_routes": row.get("legacy_routes") or [],
        })
    return records


def build_document(surface_doc: dict, existing: dict) -> dict:
    return {
        "version": existing.get("version", "1.0.0"),
        "updated": surface_doc.get("updated"),
        "status": "derived compatibility projection",
        "authority": "derived-public-route-topology-projection",
        "canonical_source": "data/house/public-surfaces.json",
        "lifecycle_status": "compatibility-projection",
        "purpose": existing.get("purpose") or "Compatibility topology projection derived from the canonical House public-surface registry.",
        "room_registry": "data/house/rooms.json",
        "public_surface_registry": "data/house/public-surfaces.json",
        "generation_rule": "Route identity, canonical route, surface type and primary Room membership derive from data/house/public-surfaces.json. This file may retain only compatibility/topology representation; it must not independently redefine public route identity.",
        "retirement_target": "Remain generated while legacy consumers require this shape, then remove consumers and retire this file.",
        "records": build_records(surface_doc),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if the committed projection differs from generated state.")
    args = parser.parse_args()

    surfaces = load(SURFACES)
    existing = load(TOPOLOGY)
    generated = build_document(surfaces, existing)

    if args.check:
        if existing != generated:
            print("PUBLIC ROUTE TOPOLOGY PROJECTION DRIFT")
            return 1
        print(f"PUBLIC ROUTE TOPOLOGY PROJECTION OK: {len(generated['records'])} active surfaces")
        return 0

    TOPOLOGY.write_text(json.dumps(generated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {TOPOLOGY.relative_to(ROOT)} from {SURFACES.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
