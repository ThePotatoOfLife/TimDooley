#!/usr/bin/env python3
"""Validate the scale-aware World Map Places contract."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = ROOT / "data" / "world-places"
BUILDER = ROOT / "scripts" / "build_world_places.py"
PLACES = ROOT / "world-map" / "3d-places.js"
SEARCH = ROOT / "world-map" / "3d-search.js"
MAP_STATE = ROOT / "world-map" / "3d-map-state.js"
PANEL_LIFECYCLE = ROOT / "world-map" / "3d-panel-lifecycle.js"
SUBDIVISIONS = ROOT / "world-map" / "3d-subdivisions.js"
SUBDIVISION_SEARCH_TEST = ROOT / "scripts" / "test_world_map_subdivision_search.mjs"
EXPECTED_RUNTIME_BUDGET = {
    "partition_max_bytes": 2_097_152,
    "rendered_max_partitions": 2,
    "cache_max_partitions": 6,
    "cache_max_bytes": 8_388_608,
    "global_major_max_bytes": 5_242_880,
    "global_major_max_features": 5000,
}
SEARCH_KEYS = {"id", "name", "aliases", "country_iso3", "type", "capital_status", "population_rank", "partition"}


def load_json(path: Path, errors: list[str]):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON {path}: {exc}")
        return None


def require_tokens(path: Path, tokens: tuple[str, ...], errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"missing required Places file: {path.relative_to(ROOT)}")
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    for token in tokens:
        if token not in text:
            errors.append(f"{path.relative_to(ROOT)} missing contract marker: {token}")


def validate_data(data_dir: Path, errors: list[str]) -> None:
    index_path = data_dir / "index.json"
    major_path = data_dir / "global-major.geo.json"
    for path in (index_path, major_path):
        if not path.exists():
            errors.append(f"missing Places data artifact: {path}")
    if not index_path.exists() or not major_path.exists():
        return

    index = load_json(index_path, errors) or {}
    major = load_json(major_path, errors) or {}
    if index.get("license") != "CC BY 4.0":
        errors.append("Places index must declare GeoNames license CC BY 4.0")
    if "GeoNames" not in str(index.get("attribution") or ""):
        errors.append("Places index must preserve GeoNames attribution")
    budget = index.get("runtime_budget") or {}
    if budget != EXPECTED_RUNTIME_BUDGET:
        errors.append(f"Places runtime budget must match canonical limits: {EXPECTED_RUNTIME_BUDGET}")
    if major.get("type") != "FeatureCollection" or not isinstance(major.get("features"), list):
        errors.append("global-major.geo.json must be a GeoJSON FeatureCollection")
        return
    features = major["features"]
    if len(features) > EXPECTED_RUNTIME_BUDGET["global_major_max_features"]:
        errors.append(f"global-major feature budget exceeded: {len(features)} > {EXPECTED_RUNTIME_BUDGET['global_major_max_features']}")
    if major_path.stat().st_size > EXPECTED_RUNTIME_BUDGET["global_major_max_bytes"]:
        errors.append("global-major file budget exceeded")
    major_descriptor = index.get("global_major") or {}
    if int(major_descriptor.get("bytes") or -1) != major_path.stat().st_size:
        errors.append("global-major descriptor bytes must match generated file size")
    if int(major_descriptor.get("count") or -1) != len(features):
        errors.append("global-major descriptor count must match generated feature count")

    seen: set[str] = set()
    for i, feature in enumerate(features):
        props = feature.get("properties") or {}
        place_id = str(props.get("id") or "")
        if not place_id:
            errors.append(f"global-major feature {i} missing stable id")
        elif place_id in seen:
            errors.append(f"duplicate global-major place id: {place_id}")
        seen.add(place_id)
        if not props.get("name"):
            errors.append(f"global-major feature {i} missing name")
        if not props.get("country_iso3"):
            errors.append(f"global-major feature {i} missing country_iso3")
        geom = feature.get("geometry") or {}
        coords = geom.get("coordinates") if geom.get("type") == "Point" else None
        if not (isinstance(coords, list) and len(coords) >= 2):
            errors.append(f"global-major feature {i} must have Point coordinates")
        for key in ("population", "population_period", "population_source", "dataset_refresh_date"):
            if key not in props:
                errors.append(f"global-major feature {place_id or i} missing provenance field: {key}")
        pop = props.get("population")
        if pop == 0:
            errors.append(f"global-major feature {place_id or i} uses numeric zero for missing population")
        if pop is not None and not props.get("population_source"):
            errors.append(f"global-major feature {place_id or i} has population without population_source")

    countries = index.get("countries") or {}
    partition_ids: set[str] = set()
    for iso3, descriptor in countries.items():
        path = data_dir / str((descriptor or {}).get("path") or "")
        if not path.exists():
            errors.append(f"Places partition indexed for {iso3} is missing: {path}")
            continue
        size = path.stat().st_size
        if int((descriptor or {}).get("bytes") or -1) != size:
            errors.append(f"Places partition {iso3} descriptor bytes do not match file size")
        if size > EXPECTED_RUNTIME_BUDGET["partition_max_bytes"]:
            errors.append(f"Places partition {iso3} exceeds partition byte budget: {size}")
        payload = load_json(path, errors) or {}
        rows = payload.get("features") if payload.get("type") == "FeatureCollection" else None
        if not isinstance(rows, list):
            errors.append(f"Places partition {iso3} must be a GeoJSON FeatureCollection")
            continue
        if int((descriptor or {}).get("count") or -1) != len(rows):
            errors.append(f"Places partition {iso3} descriptor count does not match file feature count")
        for feature in rows:
            place_id = str((feature.get("properties") or {}).get("id") or "")
            if place_id:
                partition_ids.add(place_id)

    search_records = index.get("search_records")
    if not isinstance(search_records, list) or not search_records:
        errors.append("Places index must provide compact search_records")
        search_records = []
    search_ids: set[str] = set()
    for i, row in enumerate(search_records):
        if not isinstance(row, dict):
            errors.append(f"search record {i} must be an object")
            continue
        missing = SEARCH_KEYS - set(row)
        if missing:
            errors.append(f"search record {i} missing keys: {', '.join(sorted(missing))}")
        place_id = str(row.get("id") or "")
        if not place_id:
            errors.append(f"search record {i} missing stable id")
        elif place_id in search_ids:
            errors.append(f"duplicate compact search id: {place_id}")
        search_ids.add(place_id)
        if "geometry" in row or "coordinates" in row:
            errors.append(f"search record {place_id or i} must not contain geometry")
        iso3 = str(row.get("country_iso3") or "").upper()
        if row.get("partition") != iso3 or iso3 not in countries:
            errors.append(f"search record {place_id or i} must point to an indexed ISO3 partition")
        rank = row.get("population_rank")
        if not isinstance(rank, int) or rank < 1:
            errors.append(f"search record {place_id or i} must have a positive integer population_rank")
    if partition_ids and search_ids != partition_ids:
        missing_search = partition_ids - search_ids
        stale_search = search_ids - partition_ids
        if missing_search:
            errors.append(f"compact search index missing {len(missing_search)} partition place ids")
        if stale_search:
            errors.append(f"compact search index references {len(stale_search)} absent partition place ids")


def validate_runtime(errors: list[str]) -> None:
    require_tokens(BUILDER, ("--fixture", "geonames-cities-sample.txt", "capitals-sample.geo.json", "RUNTIME_BUDGET", "search_records"), errors)
    require_tokens(PLACES, (
        "__potatoAtlasPlaces", "setVisible", "focus", "current", "search", "clear", "status",
        "atlas-places-major-points", "atlas-places-major-labels",
        "atlas-places-detail-points", "atlas-places-detail-labels",
        "context-network", "__potatoAtlasOverlayHandled", "Open country",
        "convergeLegacyCapitals", "potato-atlas-capitals-ready",
        "const inspector = window.__potatoAtlasInspector", "inspector.setBaseline(", "inspector.open(", "inspector.back()",
    ), errors)
    require_tokens(SEARCH, (
        "__potatoAtlasSearch", "Country", "Capital", "City", "Town", "typeRank", "compareResults",
        "world-subdivisions/index.json", "__potatoAtlasSubdivisions",
    ), errors)
    require_tokens(MAP_STATE, ("places", "subdivision"), errors)
    require_tokens(PANEL_LIFECYCLE, (
        "maybeLoadSelectedPlaces", "potato-atlas-country-card-rendered", "moveend", "loadCountry",
    ), errors)
    if not SUBDIVISION_SEARCH_TEST.exists():
        errors.append(f"missing subdivision search regression: {SUBDIVISION_SEARCH_TEST.relative_to(ROOT)}")
    if PLACES.exists():
        text = PLACES.read_text(encoding="utf-8", errors="replace")
        for retired in ("panelSnapshot", "restoreInspector", "captureInspector"):
            if retired in text:
                errors.append(f"Places must not reintroduce retired raw inspector state: {retired}")
    if SUBDIVISIONS.exists():
        text = SUBDIVISIONS.read_text(encoding="utf-8", errors="replace")
        if "atlasSubdivisionCard" in text:
            errors.append("Subdivisions must use the canonical #panel, not atlasSubdivisionCard")
        if "document.getElementById('panel')" not in text and 'document.getElementById("panel")' not in text:
            errors.append("Subdivisions must render inspection into canonical #panel")
    if SEARCH.exists():
        text = SEARCH.read_text(encoding="utf-8", errors="replace")
        stop_token = "event.stopImmediatePropagation();"
        submit_token = "await submit("
        if stop_token in text and submit_token in text and text.index(stop_token) > text.index(submit_token):
            errors.append("Unified search must claim Enter before awaiting async search so legacy country search cannot race it")
    node = shutil.which("node")
    if node and SUBDIVISION_SEARCH_TEST.exists():
        result = subprocess.run([node, str(SUBDIVISION_SEARCH_TEST)], capture_output=True, text=True)
        if result.returncode:
            errors.append("subdivision search regression failed: " + (result.stderr.strip() or result.stdout.strip()))
    for path in (PLACES, SEARCH):
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="replace")
            for forbidden in ("MutationObserver", "setInterval("):
                if forbidden in text:
                    errors.append(f"{path.relative_to(ROOT)} must not add {forbidden}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--data-only", action="store_true")
    parser.add_argument("--runtime-only", action="store_true")
    parser.add_argument("--allow-runtime-missing", action="store_true")
    args = parser.parse_args()

    if args.data_only and args.runtime_only:
        parser.error("--data-only and --runtime-only are mutually exclusive")

    errors: list[str] = []
    if not args.runtime_only:
        validate_data(args.data_dir, errors)
    if not args.data_only:
        runtime_errors: list[str] = []
        validate_runtime(runtime_errors)
        if args.allow_runtime_missing:
            runtime_errors = [e for e in runtime_errors if "missing required Places file" not in e]
        errors.extend(runtime_errors)

    if errors:
        print("WORLD PLACES VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("WORLD PLACES VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
