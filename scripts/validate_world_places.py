#!/usr/bin/env python3
"""Validate the scale-aware World Map Places contract."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = ROOT / "data" / "world-places"
BUILDER = ROOT / "scripts" / "build_world_places.py"
PLACES = ROOT / "world-map" / "3d-places.js"
SEARCH = ROOT / "world-map" / "3d-search.js"
MAP_STATE = ROOT / "world-map" / "3d-map-state.js"
SUBDIVISIONS = ROOT / "world-map" / "3d-subdivisions.js"


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
    if major.get("type") != "FeatureCollection" or not isinstance(major.get("features"), list):
        errors.append("global-major.geo.json must be a GeoJSON FeatureCollection")
        return
    features = major["features"]
    if len(features) > 5000:
        errors.append(f"global-major feature budget exceeded: {len(features)} > 5000")
    if major_path.stat().st_size > 5 * 1024 * 1024:
        errors.append("global-major file budget exceeded: > 5 MiB")

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
    for iso3, descriptor in countries.items():
        path = data_dir / str((descriptor or {}).get("path") or "")
        if not path.exists():
            errors.append(f"Places partition indexed for {iso3} is missing: {path}")


def validate_runtime(errors: list[str]) -> None:
    require_tokens(BUILDER, ("--fixture", "geonames-cities-sample.txt", "capitals-sample.geo.json"), errors)
    require_tokens(PLACES, (
        "__potatoAtlasPlaces", "setVisible", "focus", "current", "search", "clear", "status",
        "atlas-places-major-points", "atlas-places-major-labels",
        "atlas-places-detail-points", "atlas-places-detail-labels",
        "context-network", "__potatoAtlasOverlayHandled", "Open country",
        "convergeLegacyCapitals", "potato-atlas-capitals-ready",
    ), errors)
    require_tokens(SEARCH, (
        "__potatoAtlasSearch", "Country", "Capital", "City", "Town", "typeRank", "compareResults",
    ), errors)
    require_tokens(MAP_STATE, ("places", "subdivision"), errors)
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
    parser.add_argument("--allow-runtime-missing", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
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
