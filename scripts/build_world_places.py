#!/usr/bin/env python3
"""Build same-origin World Map place snapshots from GeoNames and capital data."""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = (
    "geonameid", "name", "asciiname", "alternatenames", "latitude", "longitude",
    "feature_class", "feature_code", "country_code", "cc2", "admin1_code", "admin2_code",
    "admin3_code", "admin4_code", "population", "elevation", "dem", "timezone",
    "modification_date",
)
RUNTIME_BUDGET = {
    "partition_max_bytes": 2_097_152,
    "rendered_max_partitions": 2,
    "cache_max_partitions": 6,
    "cache_max_bytes": 8_388_608,
    "global_major_max_bytes": 5_242_880,
    "global_major_max_features": 5000,
}


def country_maps(path: Path) -> tuple[dict[str, str], dict[str, str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("countries") or payload
    by2 = {
        str(row["iso2"]).upper(): str(row["iso3"]).upper()
        for row in rows if row.get("iso2") and row.get("iso3")
    }
    names = {
        str(row["iso3"]).upper(): str(row.get("name") or row["iso3"])
        for row in rows if row.get("iso3")
    }
    return by2, names


def parse_geonames_line(line: str) -> dict[str, str]:
    parts = line.rstrip("\n").split("\t")
    if len(parts) < len(FIELDS):
        parts += [""] * (len(FIELDS) - len(parts))
    return dict(zip(FIELDS, parts[: len(FIELDS)]))


def normalize_place(row: dict[str, str], iso2_to_iso3: dict[str, str], refresh_date: str) -> dict | None:
    iso2 = str(row.get("country_code") or "").upper()
    iso3 = iso2_to_iso3.get(iso2)
    if not iso3:
        return None
    try:
        lat = float(row["latitude"])
        lon = float(row["longitude"])
    except (TypeError, ValueError):
        return None
    try:
        raw_population = int(row.get("population") or 0)
    except (TypeError, ValueError):
        raw_population = 0
    population = raw_population if raw_population > 0 else None
    aliases = [value.strip() for value in str(row.get("alternatenames") or "").split(",") if value.strip()]
    feature_code = str(row.get("feature_code") or "")
    national = feature_code == "PPLC"
    capital_status = "national" if national else ("admin" if feature_code.startswith("PPLA") else "none")
    tier = 1 if national or (population or 0) >= 5_000_000 else 2 if (population or 0) >= 1_000_000 else 3 if (population or 0) >= 500_000 else 4
    geoname_id = str(row.get("geonameid") or "")
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "properties": {
            "id": f"gn:{geoname_id}",
            "name": row.get("name") or row.get("asciiname"),
            "ascii_name": row.get("asciiname") or row.get("name"),
            "aliases": aliases,
            "country_iso2": iso2,
            "country_iso3": iso3,
            "admin1_code": row.get("admin1_code") or None,
            "admin2_code": row.get("admin2_code") or None,
            "feature_class": row.get("feature_class") or None,
            "feature_code": feature_code or None,
            "population": population,
            "population_period": None,
            "population_source": "GeoNames" if population is not None else None,
            "population_source_id": f"gn:{geoname_id}" if population is not None else None,
            "capital_status": capital_status,
            "is_national_capital": national,
            "source": "GeoNames",
            "source_record_id": f"gn:{geoname_id}",
            "source_modified_date": row.get("modification_date") or None,
            "dataset_refresh_date": refresh_date,
            "wikidata_id": None,
            "importance_tier": tier,
            "min_zoom": 1.0 if tier == 1 else 2.4 if tier == 2 else 3.5 if tier == 3 else 5.2,
        },
    }


def normalized_name(value: object) -> str:
    return " ".join(str(value or "").casefold().split())


def coordinate_distance(a: list[float], b: list[float]) -> float:
    return math.hypot(float(a[0]) - float(b[0]), float(a[1]) - float(b[1]))


def merge_capitals(features: list[dict], capitals: dict, refresh_date: str) -> list[dict]:
    by_key = {
        (feature["properties"]["country_iso3"], normalized_name(feature["properties"]["name"])): feature
        for feature in features
    }
    for capital in capitals.get("features", []):
        props = capital.get("properties") or {}
        iso3 = str(props.get("iso3") or "").upper()
        coords = (capital.get("geometry") or {}).get("coordinates")
        if not iso3 or not isinstance(coords, list) or len(coords) < 2:
            continue
        key = (iso3, normalized_name(props.get("name")))
        found = by_key.get(key)
        if not found:
            candidates = [
                feature for feature in features
                if feature["properties"]["country_iso3"] == iso3
                and coordinate_distance(feature["geometry"]["coordinates"], coords) <= 0.25
            ]
            if candidates:
                found = min(candidates, key=lambda feature: coordinate_distance(feature["geometry"]["coordinates"], coords))
        if found:
            found_props = found["properties"]
            found_props["is_national_capital"] = True
            found_props["capital_status"] = "national"
            found_props["importance_tier"] = min(int(found_props.get("importance_tier") or 4), 2)
            found_props["min_zoom"] = min(float(found_props.get("min_zoom") or 5.2), 2.4)
            continue

        capital_id = f"capital:{iso3}:{normalized_name(props.get('name')).replace(' ', '-')}"
        feature = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [float(coords[0]), float(coords[1])]},
            "properties": {
                "id": capital_id,
                "name": props.get("name") or iso3,
                "ascii_name": props.get("name") or iso3,
                "aliases": [],
                "country_iso2": None,
                "country_iso3": iso3,
                "admin1_code": None,
                "admin2_code": None,
                "feature_class": "P",
                "feature_code": "PPLC",
                "population": None,
                "population_period": None,
                "population_source": None,
                "population_source_id": None,
                "capital_status": "national",
                "is_national_capital": True,
                "source": "existing capital snapshot",
                "source_record_id": capital_id,
                "source_modified_date": None,
                "dataset_refresh_date": refresh_date,
                "wikidata_id": props.get("wikidata_id"),
                "importance_tier": 2,
                "min_zoom": 2.4,
            },
        }
        features.append(feature)
        by_key[key] = feature
    return features


def choose_global_major(features: list[dict]) -> list[dict]:
    chosen = {
        feature["properties"]["id"]: feature
        for feature in features
        if feature["properties"].get("is_national_capital")
        or (feature["properties"].get("population") or 0) >= 500_000
    }
    by_country: defaultdict[str, list[dict]] = defaultdict(list)
    for feature in features:
        by_country[feature["properties"]["country_iso3"]].append(feature)
    for rows in by_country.values():
        ranked = sorted(rows, key=lambda feature: feature["properties"].get("population") or -1, reverse=True)
        for feature in ranked[:2]:
            chosen.setdefault(feature["properties"]["id"], feature)
    return sorted(chosen.values(), key=lambda feature: (feature["properties"]["country_iso3"], feature["properties"]["name"]))


def place_type(properties: dict) -> str:
    if properties.get("is_national_capital") or properties.get("capital_status") == "national":
        return "Capital"
    population = properties.get("population")
    if population is not None and int(population) < 50_000:
        return "Town"
    return "City"


def compact_search_records(features: list[dict]) -> list[dict]:
    ranked = sorted(
        features,
        key=lambda feature: (
            -(int((feature.get("properties") or {}).get("population") or 0)),
            str((feature.get("properties") or {}).get("country_iso3") or ""),
            str((feature.get("properties") or {}).get("name") or ""),
            str((feature.get("properties") or {}).get("id") or ""),
        ),
    )
    rank_by_id = {
        str((feature.get("properties") or {}).get("id") or ""): rank
        for rank, feature in enumerate(ranked, start=1)
    }
    records: list[dict] = []
    for feature in features:
        props = feature.get("properties") or {}
        place_id = str(props.get("id") or "")
        iso3 = str(props.get("country_iso3") or "").upper()
        aliases = []
        seen_aliases: set[str] = set()
        for value in [props.get("ascii_name"), *(props.get("aliases") or [])]:
            alias = str(value or "").strip()
            key = alias.casefold()
            if not alias or key == str(props.get("name") or "").casefold() or key in seen_aliases:
                continue
            seen_aliases.add(key)
            aliases.append(alias)
            if len(aliases) >= 8:
                break
        records.append({
            "id": place_id,
            "name": props.get("name") or props.get("ascii_name") or place_id,
            "aliases": aliases,
            "country_iso3": iso3,
            "type": place_type(props),
            "capital_status": props.get("capital_status") or "none",
            "population_rank": rank_by_id.get(place_id),
            "partition": iso3,
        })
    return sorted(records, key=lambda row: (row["population_rank"] or 10**9, row["id"]))


def write_geojson(path: Path, features: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"type": "FeatureCollection", "features": features}
    path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def build_outputs(features: list[dict], out_dir: Path, refresh_date: str, selected: set[str] | None = None) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    generated_features = [
        feature for feature in features
        if not selected or feature["properties"]["country_iso3"] in selected
    ]
    major = choose_global_major(generated_features)
    major_path = out_dir / "global-major.geo.json"
    write_geojson(major_path, major)

    grouped: defaultdict[str, list[dict]] = defaultdict(list)
    for feature in generated_features:
        grouped[feature["properties"]["country_iso3"]].append(feature)

    countries: dict[str, dict] = {}
    for iso3, rows in sorted(grouped.items()):
        rel = f"countries/{iso3}.geo.json"
        path = out_dir / rel
        write_geojson(path, rows)
        countries[iso3] = {"path": rel, "count": len(rows), "bytes": path.stat().st_size}

    index = {
        "schema_version": "1.1.0",
        "source": "GeoNames cities5000",
        "license": "CC BY 4.0",
        "attribution": "GeoNames",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset_refresh_date": refresh_date,
        "total_place_count": len(generated_features),
        "runtime_budget": dict(RUNTIME_BUDGET),
        "global_major": {"path": "global-major.geo.json", "count": len(major), "bytes": major_path.stat().st_size},
        "countries": countries,
        "search_records": compact_search_records(generated_features),
    }
    (out_dir / "index.json").write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def resolve_inputs(args: argparse.Namespace, parser: argparse.ArgumentParser) -> tuple[Path, Path, Path, str]:
    if args.fixture:
        fixture = args.fixture
        geonames = fixture / "geonames-cities-sample.txt"
        capitals = fixture / "capitals-sample.geo.json"
        country_index = args.country_index or ROOT / "data" / "countries" / "index.json"
        refresh_date = args.refresh_date or "fixture"
    else:
        missing = [
            flag for flag, value in (
                ("--geonames", args.geonames),
                ("--capitals", args.capitals),
                ("--country-index", args.country_index),
                ("--refresh-date", args.refresh_date),
            ) if not value
        ]
        if missing:
            parser.error(f"production build requires {', '.join(missing)}")
        geonames = args.geonames
        capitals = args.capitals
        country_index = args.country_index
        refresh_date = args.refresh_date

    for path, label in ((geonames, "GeoNames input"), (capitals, "capital input"), (country_index, "country index")):
        if not path.exists():
            parser.error(f"{label} not found: {path}")
    return geonames, capitals, country_index, refresh_date


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, help="Use checked-in GeoNames/capital fixture files from this directory")
    parser.add_argument("--geonames", type=Path)
    parser.add_argument("--capitals", type=Path)
    parser.add_argument("--country-index", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--refresh-date")
    parser.add_argument("--countries", default="")
    args = parser.parse_args()

    geonames_path, capitals_path, country_index_path, refresh_date = resolve_inputs(args, parser)
    iso2_to_iso3, _ = country_maps(country_index_path)
    features: list[dict] = []
    for line in geonames_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        feature = normalize_place(parse_geonames_line(line), iso2_to_iso3, refresh_date)
        if feature:
            features.append(feature)

    capitals = json.loads(capitals_path.read_text(encoding="utf-8"))
    merge_capitals(features, capitals, refresh_date)
    selected = {value.strip().upper() for value in args.countries.split(",") if value.strip()} or None
    build_outputs(features, args.output, refresh_date, selected)


if __name__ == "__main__":
    main()
