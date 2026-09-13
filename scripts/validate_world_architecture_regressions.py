#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://thepotatooflife.github.io/TimDooley/"
errors: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


family_contracts = {
    "north/index.html": ("../world/", "../world-map/", "../politics/", "./", "../world-systems/"),
    "politics/index.html": ("../world/", "../world-map/", "./", "../north/", "../world-systems/"),
    "world-systems/index.html": ("../world/", "../world-map/", "../politics/", "../north/", "./"),
}

for rel, routes in family_contracts.items():
    text = (ROOT / rel).read_text(encoding="utf-8")
    for href in routes:
        require(href in text, f"{rel} missing World-family route: {href}")

north = (ROOT / "north/index.html").read_text(encoding="utf-8")
require("<title>North Axis — World Map</title>" not in north, "North title still makes World Map its parent")

world_map = (ROOT / "world-map/index.html").read_text(encoding="utf-8")
map_guard = (ROOT / "world-map/3d-boot-guard.js").read_text(encoding="utf-8")
map_navigation = world_map + "\n" + map_guard
for href in ("../world/", "../politics/", "../north/", "../world-systems/"):
    require(href in map_navigation, f"World Map missing World-family route: {href}")
require(
    'href="../explore/#branch=world">World systems</a>' not in map_navigation,
    "World Map still labels the Explore branch as World systems instead of routing to the sibling surface",
)

machine = json.loads((ROOT / "machine-index.json").read_text(encoding="utf-8"))
reader_urls = {
    row.get("topic"): row.get("url")
    for row in machine.get("primary_reader_urls", [])
    if isinstance(row, dict)
}
expected_machine_routes = {
    "World": BASE + "world/",
    "World Map": BASE + "world-map/",
    "Politics & Geopolitics": BASE + "politics/",
    "North Axis / North Programme": BASE + "north/",
    "World Systems": BASE + "world-systems/",
}
for topic, url in expected_machine_routes.items():
    require(reader_urls.get(topic) == url, f"machine-index.json missing or misrouting {topic}: expected {url}")

pages = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
require("['tim-dooley/','religion/','philosophy/','science/','world-map/']" not in pages, "Pages workflow still expects World Map as fifth homepage door")
for token in (
    "_site/world/index.html",
    "_site/politics/index.html",
    "_site/world-systems/index.html",
    "href=\"world/\"",
):
    require(token in pages, f"Pages workflow missing World architecture assertion: {token}")

if errors:
    print("WORLD ARCHITECTURE REGRESSION VALIDATION FAILED")
    for error in errors:
        print(f" - {error}")
    raise SystemExit(1)

print("WORLD ARCHITECTURE REGRESSION VALIDATION PASSED")
