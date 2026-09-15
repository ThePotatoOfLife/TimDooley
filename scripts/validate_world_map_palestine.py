#!/usr/bin/env python3
"""Regression checks for canonical Palestine geometry handling in the World Map."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPAIR = ROOT / "data" / "world-map-spatial" / "palestine-base-repair.geojson"
ALIASES = ROOT / "world-map" / "3d-geometry-aliases.js"


def main() -> int:
    errors: list[str] = []

    if not REPAIR.is_file():
        errors.append("missing repository-owned Palestine base repair geometry")
        repair = {}
    else:
        try:
            repair = json.loads(REPAIR.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"invalid Palestine repair GeoJSON: {exc}")
            repair = {}

    if repair.get("type") != "FeatureCollection":
        errors.append("Palestine base repair must be a GeoJSON FeatureCollection")
    features = repair.get("features") or []
    gaza = [f for f in features if (f.get("properties") or {}).get("component") == "Gaza Strip"]
    if len(gaza) != 1:
        errors.append("Palestine base repair must contain exactly one Gaza Strip component")
    elif (gaza[0].get("geometry") or {}).get("type") not in {"Polygon", "MultiPolygon"}:
        errors.append("Gaza Strip repair must use polygon geometry")
    else:
        props = gaza[0].get("properties") or {}
        if props.get("canonical_entity") != "PSE":
            errors.append("Gaza Strip repair must resolve to canonical entity PSE")
        if not props.get("source") or not props.get("source_version"):
            errors.append("Gaza Strip repair must pin source and source_version metadata")

    aliases = ALIASES.read_text(encoding="utf-8", errors="replace") if ALIASES.is_file() else ""
    for token in (
        "palestine-base-repair.geojson",
        "mergePalestineGeometry",
        "Gaza Strip",
        "MultiPolygon",
        "canonical_entity",
    ):
        if token not in aliases:
            errors.append(f"Palestine runtime repair missing marker: {token}")

    if errors:
        print("World Map Palestine validation FAILED:")
        for error in errors:
            print(f" - {error}")
        return 1

    print("World Map Palestine validation passed: PSE includes repository-owned Gaza repair semantics.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
