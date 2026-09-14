#!/usr/bin/env python3
"""Compact high-resolution subdivision geometry for browser presentation.

Canonical provenance stays on each feature. This step changes only presentation
geometry, using topology-preserving Shapely simplification and an explicit byte cap.
Run after build_world_subdivisions.py when refreshing high-resolution partitions.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from shapely.geometry import mapping, shape
except ImportError as exc:  # pragma: no cover - exercised by build environment
    raise SystemExit("compact_world_subdivisions.py requires Shapely: python -m pip install shapely") from exc

DENMARK_SIMPLIFY_TOLERANCE = 0.001
DENMARK_MAX_BYTES = 3 * 1024 * 1024


def compact_feature_collection(payload: dict, *, tolerance: float, max_bytes: int) -> dict:
    if payload.get("type") != "FeatureCollection" or not isinstance(payload.get("features"), list):
        raise RuntimeError("subdivision runtime is not a GeoJSON FeatureCollection")
    for feature in payload["features"]:
        geometry = feature.get("geometry")
        if not geometry:
            continue
        original = shape(geometry)
        simplified = original.simplify(tolerance, preserve_topology=True)
        if simplified.is_empty or not simplified.is_valid:
            raise RuntimeError(f"simplification produced invalid geometry for {(feature.get('properties') or {}).get('id')}")
        feature["geometry"] = mapping(simplified)
        props = feature.setdefault("properties", {})
        props["presentation_geometry"] = {
            "method": "Shapely topology-preserving simplify",
            "tolerance_degrees": tolerance,
            "source_geometry_unchanged_at_origin": True,
        }
    metadata = payload.setdefault("metadata", {})
    metadata["presentation_geometry"] = {
        "method": "Shapely topology-preserving simplify",
        "tolerance_degrees": tolerance,
        "purpose": "bounded browser rendering; source provenance remains the official geometry source",
    }
    text = json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n"
    size = len(text.encode("utf-8"))
    if size > max_bytes:
        raise RuntimeError(f"compacted subdivision runtime is {size} bytes; cap is {max_bytes}")
    payload["_serialized_text"] = text
    payload["_serialized_bytes"] = size
    return payload


def compact_denmark(path: Path) -> int:
    payload = json.loads(path.read_text(encoding="utf-8"))
    result = compact_feature_collection(
        payload,
        tolerance=DENMARK_SIMPLIFY_TOLERANCE,
        max_bytes=DENMARK_MAX_BYTES,
    )
    text = result.pop("_serialized_text")
    size = result.pop("_serialized_bytes")
    path.write_text(text, encoding="utf-8")
    return size


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path, help="directory containing generated subdivision partitions")
    args = parser.parse_args()
    path = args.directory / "DNK.geo.json"
    if not path.exists():
        raise SystemExit(f"missing Denmark partition: {path}")
    before = path.stat().st_size
    after = compact_denmark(path)
    print(json.dumps({"partition":"DNK","before_bytes":before,"after_bytes":after,"cap_bytes":DENMARK_MAX_BYTES}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
