#!/usr/bin/env python3
"""Validate the public Rooms middle-floor navigation contract."""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_PRIMARY = [
    "tim-dooley/",
    "religion/",
    "philosophy/",
    "science/",
    "world/",
]

REQUIRED_HOME_ROOM_LINKS = {
    "context/culture/": "Culture",
    "history/": "History",
    "politics/": "Politics",
    "law/": "Law",
    "economy/": "Economy",
    "world-systems/": "World Systems",
    "context/source-authority/": "Sources",
    "rooms/": "All Rooms",
}

REQUIRED_SURFACES = {
    "rooms": "/rooms/",
    "history": "/history/",
    "law": "/law/",
    "economy": "/economy/",
}

WORLD_LINKS = (
    "../world-map/",
    "../politics/",
    "../law/",
    "../economy/",
    "../world-systems/",
    "../context/culture/",
    "../history/",
    "../north/",
    "../context/source-authority/",
)

ROOM_PAGE_CONTRACTS = {
    "rooms/index.html": ("rooms", "Rooms"),
    "history/index.html": ("history", "History"),
    "law/index.html": ("law", "Law"),
    "economy/index.html": ("economy", "Economy"),
}

EXPECTED_PUBLIC_ROOMS = {
    "culture": "context/culture/",
    "history": "history/",
    "politics": "politics/",
    "law": "law/",
    "economy": "economy/",
    "world_systems": "world-systems/",
    "sources": "context/source-authority/",
    "rooms": "rooms/",
}

DEEP_RECORDS = {
    "law/index.html": "knowledge/legal/mai-mercado-2016-research-index.md",
    "economy/index.html": "knowledge/economics/tim-dooley-inflation-ledger.md",
}

EXPECTED_BACKEND_FAMILIES = {
    "legal": {"global_route": "law/", "canonical_owner": "knowledge/legal/"},
    "economics": {"global_route": "economy/", "canonical_owner": "knowledge/economics/"},
}


def load_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def primary_hrefs(home: str) -> list[str]:
    match = re.search(r'<nav\s+class=["\']sections["\'][^>]*>(.*?)</nav>', home, flags=re.I | re.S)
    if not match:
        return []
    return re.findall(r'href=["\']([^"\']+)["\']', match.group(1), flags=re.I)


def main() -> int:
    errors: list[str] = []

    home_path = ROOT / "index.html"
    if not home_path.exists():
        errors.append("missing homepage index.html")
        home = ""
    else:
        home = home_path.read_text(encoding="utf-8", errors="replace")

    primary = primary_hrefs(home)
    if primary != EXPECTED_PRIMARY:
        errors.append(f"homepage primary Doors drifted: expected {EXPECTED_PRIMARY!r}; got {primary!r}")

    if "Explore the Rooms" not in home:
        errors.append("homepage missing distinct 'Explore the Rooms' corridor")
    for href, label in REQUIRED_HOME_ROOM_LINKS.items():
        if f'href="{href}"' not in home and f"href='{href}'" not in home:
            errors.append(f"homepage Rooms corridor missing route {href} ({label})")
    corridor = re.search(r'<section\s+class=["\']rooms-corridor["\'][^>]*>(.*?)</section>', home, flags=re.I | re.S)
    if not corridor or "cult" not in corridor.group(1).lower():
        errors.append("homepage Rooms corridor must name cult/high-control culture explicitly")

    page_text: dict[str, str] = {}
    for relative, (surface_id, label) in ROOM_PAGE_CONTRACTS.items():
        path = ROOT / relative
        if not path.exists():
            errors.append(f"missing public Room page: {relative}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        page_text[relative] = text
        if f'data-reader-surface="{surface_id}"' not in text:
            errors.append(f"{relative} missing data-reader-surface={surface_id!r}")
        if label.lower() not in text.lower():
            errors.append(f"{relative} does not identify itself as {label}")
        if "context/source-authority/" not in text:
            errors.append(f"{relative} must route to Sources & Evidence")
        if "explore/" not in text:
            errors.append(f"{relative} must route to Explore/deep archive")

    rooms_text = page_text.get("rooms/index.html", "")
    if "cult" not in rooms_text.lower() or "high-control" not in rooms_text.lower():
        errors.append("Rooms directory must expose cult/high-control analysis by name")

    for relative, record_path in DEEP_RECORDS.items():
        text = page_text.get(relative, "")
        target = f"../explore/#record={quote(record_path, safe='')}"
        if target not in text:
            errors.append(f"{relative} must deep-link its specialist record through Explore: {record_path}")
        if not (ROOT / record_path).is_file():
            errors.append(f"deep Room record does not exist: {record_path}")

    world_path = ROOT / "world" / "index.html"
    if not world_path.exists():
        errors.append("missing World gateway: world/index.html")
    else:
        world = world_path.read_text(encoding="utf-8", errors="replace")
        for href in WORLD_LINKS:
            if href not in world:
                errors.append(f"World gateway missing Rooms subject route {href}")

    try:
        surfaces = load_json("data/house/public-surfaces.json")
        topology = load_json("knowledge/research/potato-house-master/public-route-topology.json")
        bridge = load_json("data/frontend-atlas-bridge.json")
        manifest = load_json("manifest.json")
    except Exception as exc:
        errors.append(f"could not load Rooms projection contracts: {exc}")
        surfaces = topology = bridge = manifest = {}

    surface_rows = {
        row.get("id"): row
        for row in surfaces.get("surfaces", [])
        if isinstance(row, dict) and row.get("id")
    }
    topology_rows = {
        row.get("surface_id"): row
        for row in topology.get("records", [])
        if isinstance(row, dict) and row.get("surface_id")
    }

    for surface_id, route in REQUIRED_SURFACES.items():
        row = surface_rows.get(surface_id)
        if not row:
            errors.append(f"House registry missing active public surface {surface_id}")
            continue
        if row.get("canonical_route") != route:
            errors.append(f"House registry route mismatch for {surface_id}: {row.get('canonical_route')!r} != {route!r}")
        if row.get("status") != "active":
            errors.append(f"House registry surface {surface_id} must be active")
        if row.get("knowledge_owner") is not False:
            errors.append(f"Rooms guide {surface_id} must not become a knowledge owner")
        topo = topology_rows.get(surface_id)
        if not topo:
            errors.append(f"route topology missing surface {surface_id}")
            continue
        if topo.get("canonical_route") != route:
            errors.append(f"route topology mismatch for {surface_id}")
        if topo.get("room_ids") != row.get("primary_room_ids"):
            errors.append(f"route topology Room drift for {surface_id}")

    if tuple(bridge.get("public_doors", {})) != ("tim", "religion", "philosophy", "science", "world"):
        errors.append("frontend bridge must retain exactly the five canonical public Doors")
    if bridge.get("public_rooms") != EXPECTED_PUBLIC_ROOMS:
        errors.append(f"frontend bridge public_rooms must equal {EXPECTED_PUBLIC_ROOMS!r}")

    backend = bridge.get("backend_family_projection", {})
    for family, expected in EXPECTED_BACKEND_FAMILIES.items():
        row = backend.get(family)
        if not isinstance(row, dict):
            errors.append(f"frontend bridge missing {family} backend-family projection")
            continue
        for field, value in expected.items():
            if row.get(field) != value:
                errors.append(f"frontend bridge {family}.{field} must be {value!r}")

    world_branch = next((row for row in manifest.get("branches", []) if row.get("id") == "world"), {})
    world_records = set(world_branch.get("records", []))
    for record_path in DEEP_RECORDS.values():
        if record_path not in world_records:
            errors.append(f"World manifest must register deep Room record for Explore: {record_path}")

    if errors:
        print("PUBLIC ROOMS VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PUBLIC ROOMS VALIDATION PASSED: five Doors preserved; subject Rooms and deep Law/Economy records are directly discoverable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
