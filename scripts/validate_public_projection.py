#!/usr/bin/env python3
"""Validate the canonical backend -> frontend projection contract."""

from __future__ import annotations

import json
from pathlib import Path
from house_public_surfaces import primary_gateway_route_map, secondary_global_route_map

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_DOORS = {
    "tim": "tim-dooley/",
    "religion": "religion/",
    "philosophy": "philosophy/",
    "science": "science/",
    "world": "world/",
}

EXPECTED_INTERACTIVE_ROUTES = {
    "branch": "explore/#branch=<id>",
    "record": "explore/#record=<path>",
    "context": "explore/#context=<id>",
    "pathway": "explore/#path=<id>",
}

WORLD_SPECIALISTS = {
    "world-map/index.html": "World Map",
    "politics/index.html": "Politics",
    "north/index.html": "North",
    "world-systems/index.html": "World Systems",
}

WORLD_GATEWAY_LINKS = (
    "../world-map/",
    "../politics/",
    "../north/",
    "../world-systems/",
)


def load_json(relative_path: str):
    with (ROOT / relative_path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def contains_live_retired_reference(value) -> bool:
    if isinstance(value, str):
        lowered = value.lower()
        return "root.js" in lowered or "index.html#node=" in lowered
    if isinstance(value, list):
        return any(contains_live_retired_reference(item) for item in value)
    if isinstance(value, dict):
        return any(contains_live_retired_reference(item) for item in value.values())
    return False


def main() -> int:
    manifest = load_json("manifest.json")
    bridge = load_json("data/frontend-atlas-bridge.json")
    coverage = load_json("data/backend-coverage-map.json")
    atlas = load_json("data/atlas-manifest.json")
    surfaces = load_json("data/house/public-surfaces.json")

    errors: list[str] = []

    derived_doors={k:v.lstrip("/") for k,v in primary_gateway_route_map(ROOT).items()}
    if bridge.get("route_authority")!="data/house/public-surfaces.json":
        fail("frontend bridge must declare House public-surfaces as route authority", errors)
    if bridge.get("public_doors")!=derived_doors:
        fail(f"frontend bridge public_doors drifted from House authority: {bridge.get('public_doors')!r} != {derived_doors!r}", errors)
    derived_secondary={k:v.lstrip("/") for k,v in secondary_global_route_map(ROOT).items()}
    if bridge.get("global_secondary_surfaces")!=derived_secondary:
        fail(f"frontend bridge global_secondary_surfaces drifted from House authority: {bridge.get('global_secondary_surfaces')!r} != {derived_secondary!r}", errors)

    def norm_route(value: str) -> str:
        value = str(value or "").strip()
        if not value:
            return "/"
        if value.startswith("http://") or value.startswith("https://"):
            return value
        value = value.split("#", 1)[0].split("?", 1)[0]
        if not value.startswith("/"):
            value = "/" + value
        if "." not in value.rsplit("/", 1)[-1] and not value.endswith("/"):
            value += "/"
        return value

    authoritative_routes = {
        norm_route(row.get("canonical_route") or row.get("route"))
        for row in surfaces.get("surfaces", [])
        if isinstance(row, dict) and (row.get("canonical_route") or row.get("route"))
    }

    def require_surface_route(label: str, route: str) -> None:
        if not route or "{" in str(route):
            return
        normalized = norm_route(route)
        if normalized not in authoritative_routes:
            fail(f"{label} copies non-canonical public route {route!r}; public-surfaces.json is route authority", errors)

    public_doors = bridge.get("public_doors")
    if public_doors != EXPECTED_DOORS:
        fail(f"frontend bridge public_doors must equal {EXPECTED_DOORS!r}; got {public_doors!r}", errors)

    if isinstance(public_doors, dict) and "world_map" in public_doors:
        fail("World Map must be a specialist route, not the fifth primary public door", errors)

    for family_name in ("public_doors", "public_rooms", "global_secondary_surfaces"):
        family = bridge.get(family_name, {})
        if isinstance(family, dict):
            for key, route in family.items():
                require_surface_route(f"frontend bridge {family_name}.{key}", route)

    for branch_id, item in bridge.get("branch_projection", {}).items():
        if not isinstance(item, dict):
            continue
        for field in ("human_route", "global_route"):
            if item.get(field):
                require_surface_route(f"branch projection {branch_id}.{field}", item[field])

    for family_id, item in bridge.get("backend_family_projection", {}).items():
        if not isinstance(item, dict):
            continue
        for field in ("global_route", "deep_route"):
            route = item.get(field)
            if route and "#" not in str(route):
                require_surface_route(f"backend family {family_id}.{field}", route)

    world_page = ROOT / "world" / "index.html"
    if not world_page.exists():
        fail("World gateway is missing: world/index.html", errors)
    else:
        world_text = world_page.read_text(encoding="utf-8")
        for route in WORLD_GATEWAY_LINKS:
            if route not in world_text:
                fail(f"World gateway must link specialist route {route}", errors)

    for relative, label in WORLD_SPECIALISTS.items():
        path = ROOT / relative
        if not path.exists():
            fail(f"World specialist surface is missing: {relative}", errors)
            continue
        text = path.read_text(encoding="utf-8")
        if label.lower() not in text.lower():
            fail(f"World specialist surface {relative} must identify itself as {label}", errors)

    projection = bridge.get("branch_projection", {})
    allowed_status_keys = {"primary_door", "global_route", "backend_only"}
    branch_ids = [branch.get("id") for branch in manifest.get("branches", []) if branch.get("id")]
    missing = []
    malformed = []
    for branch_id in branch_ids:
        item = projection.get(branch_id)
        if not isinstance(item, dict):
            missing.append(branch_id)
            continue
        states = [key for key in allowed_status_keys if key in item]
        if len(states) != 1:
            malformed.append(branch_id)
            continue
        if "primary_door" in item and item["primary_door"] not in EXPECTED_DOORS:
            malformed.append(branch_id)
    if missing:
        fail(f"manifest branches missing projection entries: {', '.join(sorted(missing))}", errors)
    if malformed:
        fail("branch projection entries must have exactly one valid primary_door/global_route/backend_only state: " + ", ".join(sorted(malformed)), errors)

    world_projection = projection.get("world", {})
    if world_projection.get("primary_door") != "world" or world_projection.get("human_route") != "world/":
        fail("world branch must project through primary_door='world' with human_route='world/'", errors)

    north_projection = projection.get("north", {})
    if north_projection.get("primary_door") != "world" or north_projection.get("human_route") != "north/":
        fail("north branch must project through World while preserving human_route='north/'", errors)

    if projection.get("timeline", {}).get("global_route") != "timeline/":
        fail("timeline branch must use global_route='timeline/' while keeping Explore as its archive route", errors)
    if projection.get("corporium", {}).get("human_route") != "corporium/":
        fail("corporium branch must use human_route='corporium/'", errors)
    if projection.get("works", {}).get("human_route") != "works/":
        fail("works branch must use human_route='works/'", errors)
    if bridge.get("backend_family_projection", {}).get("culture", {}).get("global_route") != "context/culture/":
        fail("culture backend family must use global_route='context/culture/'", errors)

    bridge_routes = bridge.get("route_map", {})
    if any("index.html#node=" in str(value) for value in bridge_routes.values()):
        fail("frontend bridge still exposes retired index.html#node= record routing", errors)

    if contains_live_retired_reference(coverage):
        fail("backend coverage map still names retired root.js or index.html#node= as a live consumer", errors)

    live_route_metadata = (
        "data/belief-backend.json",
        "data/belief-registry.json",
        "data/country-fallback.json",
        "data/religious-layer-map.json",
        "data/axis-model.json",
        "data/global-graph-bridge.json",
    )
    for relative in live_route_metadata:
        path = ROOT / relative
        if not path.exists():
            continue
        payload = load_json(relative)
        if contains_live_retired_reference(payload):
            fail(f"{relative} still exposes retired root.js or index.html#node= routing", errors)

    interactive_routes = atlas.get("interactive_routes", {})
    if interactive_routes != EXPECTED_INTERACTIVE_ROUTES:
        fail(f"atlas interactive_routes must equal {EXPECTED_INTERACTIVE_ROUTES!r}; got {interactive_routes!r}", errors)

    reader_guide = (ROOT / "app" / "reader-guide.js").read_text(encoding="utf-8")
    if 'href="learn/"' in reader_guide or "href='learn/'" in reader_guide:
        fail("reader guide still routes to retired learn/ Start Here surface", errors)

    if (ROOT / "root.js").exists():
        fail("retired root.js reader artifact still exists; Explore is the only deep interactive reader", errors)

    if errors:
        print("Public projection validation FAILED")
        for error in errors:
            print(f" - {error}")
        return 1

    print(f"Public projection validation passed: {len(EXPECTED_DOORS)} doors, {len(branch_ids)} projected branches, World owns the fifth domain and mature readers own their human routes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
