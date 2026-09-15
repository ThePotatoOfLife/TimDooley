#!/usr/bin/env python3
"""Build reproducible approximate measurements for World Map spatial overlays.

Uses spherical great-circle/area calculations from committed WGS84 coordinates.
These values describe the stored geometry only; they do not increase the epistemic
precision of historical, textual, or project-interpreted reconstructions.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "world-map-spatial-overlays.json"
OUT = ROOT / "data" / "world-map-spatial-measurements.json"
EARTH_RADIUS_KM = 6371.0088
METHOD = "spherical-haversine-chamberlain-v1"


def haversine(a, b):
    lon1, lat1 = map(math.radians, a)
    lon2, lat2 = map(math.radians, b)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(min(1.0, math.sqrt(h)))


def line_length(line):
    return sum(haversine(a, b) for a, b in zip(line, line[1:]))


def ring_area(ring):
    if len(ring) < 4:
        return 0.0
    total = 0.0
    for a, b in zip(ring, ring[1:]):
        lon1, lat1 = map(math.radians, a)
        lon2, lat2 = map(math.radians, b)
        total += (lon2 - lon1) * (2 + math.sin(lat1) + math.sin(lat2))
    return abs(total) * EARTH_RADIUS_KM * EARTH_RADIUS_KM / 2


def polygon_measure(polygon):
    if not polygon:
        return 0.0, 0.0
    outer = polygon[0]
    area = ring_area(outer)
    perimeter = line_length(outer)
    for hole in polygon[1:]:
        area -= ring_area(hole)
        perimeter += line_length(hole)
    return max(area, 0.0), perimeter


def flatten_points(value, out):
    if isinstance(value, list) and len(value) >= 2 and all(isinstance(v, (int, float)) for v in value[:2]):
        out.append(value[:2])
        return
    if isinstance(value, list):
        for child in value:
            flatten_points(child, out)


def bbox(geometry):
    points = []
    flatten_points(geometry.get("coordinates") or [], points)
    if not points:
        return None
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return [round(min(xs), 6), round(min(ys), 6), round(max(xs), 6), round(max(ys), 6)]


def measure(feature):
    geometry = feature.get("geometry") or {}
    props = feature.get("properties") or {}
    kind = geometry.get("type")
    coords = geometry.get("coordinates") or []
    row = {
        "geometry_version": props.get("geometry_version"),
        "geometry_type": kind,
        "bbox": bbox(geometry),
        "component_count": 1,
        "method": METHOD,
        "measurement_policy": props.get("measurement_policy"),
    }
    if kind == "Polygon":
        area, perimeter = polygon_measure(coords)
        row.update(area_sq_km=round(area, 1), perimeter_km=round(perimeter, 1))
    elif kind == "MultiPolygon":
        values = [polygon_measure(poly) for poly in coords]
        row["component_count"] = len(coords)
        row.update(area_sq_km=round(sum(v[0] for v in values), 1), perimeter_km=round(sum(v[1] for v in values), 1))
    elif kind == "LineString":
        row["length_km"] = round(line_length(coords), 1)
    elif kind == "MultiLineString":
        row["component_count"] = len(coords)
        row["length_km"] = round(sum(line_length(line) for line in coords), 1)
    return row


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    owners = {}
    output = {}
    for entry in manifest.get("entries") or []:
        if entry.get("availability") != "current" or not entry.get("measurable"):
            continue
        owner = ROOT / entry["geometry_owner"]
        if owner not in owners:
            data = json.loads(owner.read_text(encoding="utf-8"))
            owners[owner] = {f.get("properties", {}).get("feature_id"): f for f in data.get("features") or []}
        for feature_id in entry.get("feature_ids") or []:
            feature = owners[owner].get(feature_id)
            if feature:
                output[feature_id] = measure(feature)

    payload = {
        "schema_version": "1.0.0",
        "generated_from": "data/world-map-spatial-overlays.json and committed WGS84 geometry owners",
        "method": METHOD,
        "earth_radius_km": EARTH_RADIUS_KM,
        "precision_note": "Geometry-derived approximations. Measurements do not imply that textual, historical, ideological or project reconstructions are exact surveyed boundaries. source_extent_reference areas describe published reference extents, not the underlying basin area.",
        "features": output,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} with {len(output)} measured features.")


if __name__ == "__main__":
    main()
