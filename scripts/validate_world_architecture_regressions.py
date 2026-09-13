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


family_routes = {
    "../world/": "World",
    "../world-map/": "Map",
    "../politics/": "Politics",
    "../north/": "North",
    "../world-systems/": "Systems",
}

for rel in ("north/index.html", "politics/index.html", "world-systems/index.html"):
    text = (ROOT / rel).read_text(encoding="utf-8")
    for href, label in family_routes.items():
        require(href in text, f"{rel} missing World-family route {label}: {href}")

north = (ROOT / "north/index.html").read_text(encoding="utf-8")
require("<title>North Axis — World Map</title>" not in north, "North title still makes World Map its parent")

world_map = (ROOT / "world-map/index.html").read_text(encoding="utf-8")
for href, label in family_routes.items():
    if href == "../world-map/":
        continue
    require(href in world_map, f"world-map/index.html missing World-family route {label}: {href}")
require(
    'href="../explore/#branch=world">World systems</a>' not in world_map,
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
