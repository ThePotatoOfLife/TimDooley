#!/usr/bin/env python3
"""Normalize a reviewed ADM1 GeoJSON into the World Map subdivision contract.

This importer intentionally does not download sources and does not mutate
data/world-subdivisions/index.json. It turns one reviewed local GeoJSON into:
  1. a canonical <ISO3>.geo.json partition;
  2. a <ISO3>.partition.json descriptor sidecar for review/registry insertion.

Example:
  python scripts/import_world_adm1.py source.geojson \
    --iso3 RUS --parent-name Russia --id-prefix RU- \
    --name-field name_en --code-field iso_3166_2 \
    --default-type region --source-label "Natural Earth Admin-1" \
    --source-ref "nvkelso/natural-earth-vector@..." \
    --expected-count 83 --out-dir /tmp/adm1-review

The input must already be obtained/reviewed by the operator. This keeps external
acquisition separate from normalization and makes generated diffs reproducible.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "data" / "world-subdivisions"
DEFAULT_MAX_BYTES = 1_500_000

POLYGON_TYPES = {"Polygon", "MultiPolygon"}


def clean(value) -> str:
    return str(value or "").strip()


def field(props: dict, key: str | None) -> str:
    return clean(props.get(key)) if key else ""


def canonical_code(raw: str, iso3: str, id_prefix: str) -> str:
    value = clean(raw)
    if not value:
        raise ValueError("empty subdivision code")
    # Accept common ISO-3166-2 inputs such as RU-MOW while preserving only the
    # suffix because id_prefix owns the canonical partition namespace.
    if "-" in value:
        head, tail = value.split("-", 1)
        if head and tail and head.upper() != iso3[:2].upper() and not value.startswith(id_prefix):
            # Non-matching prefixed codes remain intact after sanitization; this
            # avoids silently rewriting a source namespace we do not understand.
            pass
        elif tail:
            value = tail
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-")
    if not value:
        raise ValueError(f"subdivision code normalizes empty: {raw!r}")
    return value.upper()


def geometry_ok(geometry: dict | None) -> bool:
    return isinstance(geometry, dict) and geometry.get("type") in POLYGON_TYPES and bool(geometry.get("coordinates"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_geojson", type=Path)
    parser.add_argument("--iso3", required=True)
    parser.add_argument("--parent-name", required=True)
    parser.add_argument("--id-prefix", required=True)
    parser.add_argument("--name-field", required=True)
    parser.add_argument("--code-field", required=True)
    parser.add_argument("--local-name-field")
    parser.add_argument("--type-field")
    parser.add_argument("--default-type", default="region")
    parser.add_argument("--source-label", required=True)
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--source-vintage", default="unknown")
    parser.add_argument("--representation-note", required=True)
    parser.add_argument("--expected-count", type=int)
    parser.add_argument("--viewport", nargs=4, type=float, metavar=("WEST","EAST","SOUTH","NORTH"))
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    args = parser.parse_args()

    iso3 = args.iso3.upper().strip()
    if not re.fullmatch(r"[A-Z]{3}", iso3):
        raise SystemExit("--iso3 must be exactly three ASCII letters")
    id_prefix = args.id_prefix.strip()
    if not id_prefix or not id_prefix.endswith("-"):
        raise SystemExit("--id-prefix must be non-empty and end with '-'")
    if args.max_bytes <= 0:
        raise SystemExit("--max-bytes must be positive")

    raw = args.source_geojson.read_bytes()
    source_sha256 = hashlib.sha256(raw).hexdigest()
    try:
        source = json.loads(raw.decode("utf-8-sig"))
    except Exception as exc:
        raise SystemExit(f"source is not valid UTF-8 GeoJSON: {exc}")
    if source.get("type") != "FeatureCollection" or not isinstance(source.get("features"), list):
        raise SystemExit("source must be a GeoJSON FeatureCollection")

    features: list[dict] = []
    seen_ids: set[str] = set()
    search_records: list[dict] = []

    for ordinal, feature in enumerate(source["features"], start=1):
        props = feature.get("properties") or {}
        name = field(props, args.name_field)
        raw_code = field(props, args.code_field)
        if not name:
            raise SystemExit(f"feature {ordinal}: missing name field {args.name_field!r}")
        if not raw_code:
            raise SystemExit(f"feature {ordinal} {name!r}: missing code field {args.code_field!r}")
        if not geometry_ok(feature.get("geometry")):
            raise SystemExit(f"feature {ordinal} {name!r}: geometry must be non-empty Polygon/MultiPolygon")
        try:
            code = canonical_code(raw_code, iso3, id_prefix)
        except ValueError as exc:
            raise SystemExit(f"feature {ordinal} {name!r}: {exc}")
        feature_id = f"{id_prefix}{code}"
        if feature_id in seen_ids:
            raise SystemExit(f"duplicate canonical subdivision id: {feature_id}")
        seen_ids.add(feature_id)

        local_name = field(props, args.local_name_field)
        subdivision_type = field(props, args.type_field) or args.default_type
        canonical_props = {
            "id": feature_id,
            "name": name,
            "code": code,
            "parent_iso3": iso3,
            "parent_name": args.parent_name,
            "subdivision_type": subdivision_type,
            "population": None,
            "population_status": "unknown-not-zero",
            "geometry_source": args.source_label,
            "geometry_source_ref": args.source_ref,
            "geometry_source_sha256": source_sha256,
            "geometry_source_vintage": args.source_vintage,
            "representation_note": args.representation_note,
        }
        if local_name and local_name != name:
            canonical_props["local_name"] = local_name

        features.append({
            "type": "Feature",
            "id": feature_id,
            "properties": canonical_props,
            "geometry": feature["geometry"],
        })
        search = {
            "id": feature_id,
            "name": name,
            "code": code,
            "subdivision_type": subdivision_type,
            "parent_iso3": iso3,
            "parent_name": args.parent_name,
        }
        if local_name and local_name != name:
            search["local_name"] = local_name
        search_records.append(search)

    if args.expected_count is not None and len(features) != args.expected_count:
        raise SystemExit(f"feature count drift: expected {args.expected_count}, got {len(features)}")

    features.sort(key=lambda item: (item["properties"]["name"].casefold(), item["properties"]["id"]))
    search_records.sort(key=lambda item: (item["name"].casefold(), item["id"]))

    partition = {
        "type": "FeatureCollection",
        "name": f"{args.parent_name} first-order administrative regions",
        "metadata": {
            "parent_iso3": iso3,
            "feature_count": len(features),
            "admin_level": 1,
            "status": "generated-geometry-first",
            "source_label": args.source_label,
            "source_ref": args.source_ref,
            "source_sha256": source_sha256,
            "source_vintage": args.source_vintage,
            "representation_note": args.representation_note,
            "population_status": "unknown-not-zero",
        },
        "features": features,
    }
    compact = json.dumps(partition, ensure_ascii=False, separators=(",", ":")) + "\n"
    encoded = compact.encode("utf-8")
    if len(encoded) > args.max_bytes:
        raise SystemExit(f"generated partition exceeds byte budget: {len(encoded)} > {args.max_bytes}")

    viewport = None
    if args.viewport:
        west, east, south, north = args.viewport
        if not (-180 <= west <= 180 and -180 <= east <= 180 and -90 <= south <= 90 and -90 <= north <= 90):
            raise SystemExit("--viewport coordinates are out of bounds")
        viewport = {"west": west, "east": east, "south": south, "north": north}

    descriptor = {
        "path": f"{iso3}.geo.json",
        "bytes": len(encoded),
        "feature_count": len(features),
        "admin_level": 1,
        "status": "review-required-generated-geometry-first",
        "source": args.source_label,
        "source_ref": args.source_ref,
        "source_sha256": source_sha256,
        "geometry_vintage": args.source_vintage,
        "population_status": "unknown-not-zero",
        "id_prefix": id_prefix,
        "parent_name": args.parent_name,
        "representation_note": args.representation_note,
        "search_records": search_records,
    }
    if viewport:
        descriptor["viewport_bounds"] = viewport

    args.out_dir.mkdir(parents=True, exist_ok=True)
    partition_path = args.out_dir / f"{iso3}.geo.json"
    descriptor_path = args.out_dir / f"{iso3}.partition.json"
    partition_path.write_text(compact, encoding="utf-8", newline="\n")
    descriptor_path.write_text(json.dumps(descriptor, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    print(f"WORLD MAP ADM1 IMPORT PASSED · {iso3} · {len(features)} features · {len(encoded)} bytes")
    print(f"source sha256: {source_sha256}")
    print(f"partition: {partition_path}")
    print(f"descriptor: {descriptor_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
