#!/usr/bin/env python3
"""Validate derived measurements for current measurable spatial overlays."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "world-map-spatial-overlays.json"
MEASUREMENTS = ROOT / "data" / "world-map-spatial-measurements.json"
UI = ROOT / "world-map" / "3d-spatial-overlay-ui.js"


def load(path: Path, errors: list[str]):
    if not path.is_file():
        errors.append(f"missing required file: {path.relative_to(ROOT)}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
        return {}


def main() -> int:
    errors: list[str] = []
    manifest = load(MANIFEST, errors)
    measurements = load(MEASUREMENTS, errors)
    rows = measurements.get("features") or {}

    for entry in manifest.get("entries") or []:
        if entry.get("availability") != "current" or not entry.get("measurable"):
            continue
        for feature_id in entry.get("feature_ids") or []:
            row = rows.get(feature_id)
            if not isinstance(row, dict):
                errors.append(f"missing measurement record for {feature_id}")
                continue
            for key in ("geometry_version", "geometry_type", "bbox", "component_count", "method", "measurement_policy"):
                if key not in row:
                    errors.append(f"measurement {feature_id} missing {key}")
            if row.get("geometry_type") in {"Polygon", "MultiPolygon"}:
                for key in ("area_sq_km", "perimeter_km"):
                    if key not in row:
                        errors.append(f"polygon measurement {feature_id} missing {key}")
            if row.get("geometry_type") in {"LineString", "MultiLineString"} and "length_km" not in row:
                errors.append(f"line measurement {feature_id} missing length_km")

    ui = UI.read_text(encoding="utf-8", errors="replace") if UI.is_file() else ""
    for token in ("world-map-spatial-measurements.json", "Geometry-derived", "area_sq_km", "length_km"):
        if token not in ui:
            errors.append(f"spatial overlay inspector missing measurement marker: {token}")

    if errors:
        print("World Map spatial measurement validation FAILED:")
        for error in errors:
            print(f" - {error}")
        return 1

    print(f"World Map spatial measurement validation passed: {len(rows)} measured feature(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
