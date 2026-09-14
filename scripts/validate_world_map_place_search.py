#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBDIVISIONS = ROOT / "world-map" / "3d-subdivisions.js"
LIFECYCLE = ROOT / "world-map" / "3d-panel-lifecycle.js"
PLACE_SEARCH = ROOT / "world-map" / "3d-place-search.js"
CAPITALS = ROOT / "data" / "world-capitals.geo.json"
SOURCE_VALIDATOR = ROOT / "scripts" / "validate_world_map_source.py"


def require(condition, message):
    if not condition:
        raise SystemExit(f"PLACE SEARCH CONTRACT FAILED: {message}")


def validate_city_snapshot():
    require(CAPITALS.exists(), "existing pinned world-capitals snapshot must remain available")
    payload = json.loads(CAPITALS.read_text(encoding="utf-8"))
    features = payload.get("features", []) if isinstance(payload, dict) else []
    require(payload.get("type") == "FeatureCollection", "world-capitals must remain GeoJSON")
    require(len(features) >= 150, f"world-capitals coverage unexpectedly low: {len(features)}")
    primary = 0
    non_primary = 0
    for feature in features:
        props = feature.get("properties") or {}
        coords = (feature.get("geometry") or {}).get("coordinates") or []
        require(props.get("name") and props.get("iso3"), "every searchable city needs name + ISO3")
        require(len(coords) >= 2 and all(isinstance(v, (int, float)) for v in coords[:2]),
                f"invalid city coordinates for {props.get('name')}")
        primary += props.get("primary") is True
        non_primary += props.get("primary") is False
    require(primary >= 100, f"primary capital coverage unexpectedly low: {primary}")
    require(non_primary >= 5, f"expected selected non-primary cities in existing snapshot: {non_primary}")


def main():
    require(PLACE_SEARCH.exists(), "world-map/3d-place-search.js must exist")
    validate_city_snapshot()

    subdivisions = SUBDIVISIONS.read_text(encoding="utf-8")
    lifecycle = LIFECYCLE.read_text(encoding="utf-8")
    place_search = PLACE_SEARCH.read_text(encoding="utf-8")
    source_validator = SOURCE_VALIDATOR.read_text(encoding="utf-8")

    require("search(query)" in subdivisions, "subdivision owner must expose search(query)")
    require("__potatoAtlasSubdivisions" in place_search, "place search must route subdivisions through their owner")
    require("__potatoAtlasSelection" in place_search, "place search must route countries through the canonical selection owner")
    require("Find place…" in place_search and "aria-label" in place_search,
            "place search must upgrade the existing input copy/accessibility")
    require("addEventListener('keydown'" in place_search and "true" in place_search,
            "place search must own Enter in capture phase without rewriting the core app")
    require("__potatoAtlasLoadModule" in lifecycle and "3d-place-search.js" in lifecycle,
            "place search must be loaded through the existing lifecycle helper")
    require("window.__potatoAtlasPlaceSearch" in place_search, "place search must publish its focused API")
    require("validate_world_map_place_search" in source_validator,
            "canonical World Map source validator must run this contract")

    require("../data/world-capitals.geo.json" in place_search,
            "city search must reuse the existing pinned Natural Earth snapshot")
    require("searchCities" in place_search and "focusCity" in place_search,
            "place search must expose explicit city search/focus behavior")
    require("searchParams.set('place'" in place_search and "searchParams.delete('place'" in place_search,
            "city selection must own a stable ?place= deep-link state")
    require("atlas-place-selection" in place_search,
            "searched cities need a visible selected-place marker, including non-primary cities")

    forbidden = ("nominatim", "mapbox.com/geocoding", "maps.googleapis.com/maps/api/geocode")
    lowered = place_search.lower()
    require(not any(token in lowered for token in forbidden), "place search must not depend on a live geocoder")

    print("World Map place-search contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
