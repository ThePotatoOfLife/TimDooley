#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBDIVISIONS = ROOT / "world-map" / "3d-subdivisions.js"
LIFECYCLE = ROOT / "world-map" / "3d-panel-lifecycle.js"
PLACE_SEARCH = ROOT / "world-map" / "3d-place-search.js"
SOURCE_VALIDATOR = ROOT / "scripts" / "validate_world_map_source.py"


def require(condition, message):
    if not condition:
        raise SystemExit(f"PLACE SEARCH CONTRACT FAILED: {message}")


def main():
    require(PLACE_SEARCH.exists(), "world-map/3d-place-search.js must exist")

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

    forbidden = ("nominatim", "mapbox.com/geocoding", "maps.googleapis.com/maps/api/geocode")
    lowered = place_search.lower()
    require(not any(token in lowered for token in forbidden), "place search must not depend on a live geocoder")

    print("World Map place-search contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
