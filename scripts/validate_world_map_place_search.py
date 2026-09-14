#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "world-map" / "index.html"
APP = ROOT / "world-map" / "3d-app.js"
SUBDIVISIONS = ROOT / "world-map" / "3d-subdivisions.js"
LIFECYCLE = ROOT / "world-map" / "3d-panel-lifecycle.js"
PLACE_SEARCH = ROOT / "world-map" / "3d-place-search.js"
WORKFLOW = ROOT / ".github" / "workflows" / "quality-checks.yml"


def require(condition, message):
    if not condition:
        raise SystemExit(f"PLACE SEARCH CONTRACT FAILED: {message}")


def main():
    require(PLACE_SEARCH.exists(), "world-map/3d-place-search.js must exist")

    index = INDEX.read_text(encoding="utf-8")
    app = APP.read_text(encoding="utf-8")
    subdivisions = SUBDIVISIONS.read_text(encoding="utf-8")
    lifecycle = LIFECYCLE.read_text(encoding="utf-8")
    place_search = PLACE_SEARCH.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")

    require('placeholder="Find place…"' in index, "existing search input must say Find place…")
    require('aria-label="Find place"' in index, "search input needs the unified accessible label")
    require("__potatoAtlasPlaceSearch" in app, "3d-app.js must delegate optional non-country search")
    require("search(query)" in subdivisions, "subdivision owner must expose search(query)")
    require("__potatoAtlasSubdivisions" in place_search, "place search must route subdivisions through their owner")
    require("__potatoAtlasLoadModule" in lifecycle and "3d-place-search.js" in lifecycle,
            "place search must be lazy-loaded through the existing lifecycle helper")
    require("window.__potatoAtlasPlaceSearch" in place_search, "place search must publish its focused API")
    require("node --check world-map/3d-place-search.js" in workflow,
            "existing quality workflow must syntax-check the place-search module")
    require("python scripts/validate_world_map_place_search.py" in workflow,
            "existing quality workflow must run this contract")

    forbidden = ("nominatim", "mapbox.com/geocoding", "maps.googleapis.com/maps/api/geocode")
    lowered = place_search.lower()
    require(not any(token in lowered for token in forbidden), "place search must not depend on a live geocoder")

    print("World Map place-search contract: OK")


if __name__ == "__main__":
    main()
