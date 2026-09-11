#!/usr/bin/env python3
"""Validate the second composable World Atlas functionality slice.

This gate is intentionally source-level: it verifies that richer membership,
statistics, relation filtering and country-card/query contracts remain wired
through the registry/compositor rather than reintroducing parallel UI systems.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "world-atlas-layer-registry.json"
WORLD = ROOT / "data" / "world-relational-map.json"
COMPOSITOR = ROOT / "world-map" / "3d-compositor.js"
WORLD_BAR = ROOT / "world-map" / "3d-world-bar.js"
COUNTRY_CARD = ROOT / "world-map" / "3d-country-card.js"
SELECTION = ROOT / "world-map" / "3d-country-selection.js"
FACTS_BUILDER = ROOT / "scripts" / "build_world_country_facts.py"

CURRENT_GROUPS = {
    "group.eu": "EU",
    "group.usmca": "USMCA",
    "group.asean": "ASEAN",
    "group.mercosur": "MERCOSUR",
    "group.gcc": "GCC",
    "group.sco": "SCO",
    "group.g7": "G7",
    "group.g20": "G20",
    "group.oecd": "OECD",
    "group.schengen": "Schengen",
    "group.euro-area": "Euro_Area",
}
CURRENT_STATS = {
    "stat.gdp",
    "stat.gdp-per-capita",
    "stat.real-growth",
    "stat.inflation",
    "stat.unemployment",
    "stat.debt-to-gdp",
}
CURRENT_RELATIONS = {
    "relation.trade",
    "relation.ownership",
    "relation.funding",
    "relation.energy",
    "relation.infrastructure",
    "relation.security",
    "relation.research",
    "relation.technology",
}
EXPECTED_COUNTS = {
    "EU": 27,
    "USMCA": 3,
    "ASEAN": 11,
    "MERCOSUR": 5,
    "GCC": 6,
    "SCO": 10,
    "G7": 7,
    "G20": 19,
    "OECD": 38,
    "Schengen": 29,
    "Euro_Area": 21,
}


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"cannot read {path.relative_to(ROOT)}: {exc}")


def require(text: str, markers: tuple[str, ...], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        fail(f"{label} missing markers: {missing}")


def syntax_check(path: Path) -> None:
    node = shutil.which("node")
    if not node:
        return
    text = path.read_text(encoding="utf-8")
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", encoding="utf-8", delete=False) as handle:
        handle.write(text)
        temp = Path(handle.name)
    try:
        result = subprocess.run([node, "--check", str(temp)], capture_output=True, text=True)
        if result.returncode:
            fail(f"{path.name} syntax failed: {result.stderr.strip() or result.stdout.strip()}")
    finally:
        temp.unlink(missing_ok=True)


def main() -> None:
    for path in (REGISTRY, WORLD, COMPOSITOR, WORLD_BAR, COUNTRY_CARD, SELECTION, FACTS_BUILDER):
        if not path.exists():
            fail(f"missing {path.relative_to(ROOT)}")

    registry = load(REGISTRY)
    world = load(WORLD)
    entries = {row.get("id"): row for row in registry.get("entries", [])}
    memberships = world.get("empirical_memberships", {})

    for entry_id, membership_key in CURRENT_GROUPS.items():
        entry = entries.get(entry_id)
        if not entry or entry.get("availability") != "current":
            fail(f"{entry_id} must be current")
        if entry.get("source_path") != f"empirical_memberships.{membership_key}":
            fail(f"{entry_id} must resolve through empirical_memberships.{membership_key}")
        group = memberships.get(membership_key)
        if not isinstance(group, dict):
            fail(f"world map missing empirical_memberships.{membership_key}")
        members = group.get("members")
        if not isinstance(members, list) or len(members) != EXPECTED_COUNTS[membership_key]:
            fail(f"{membership_key} expected {EXPECTED_COUNTS[membership_key]} country members; found {len(members) if isinstance(members, list) else 'invalid'}")
        if not isinstance(group.get("source"), str) or not group["source"].startswith("http"):
            fail(f"{membership_key} needs an external source URL")

    for entry_id in CURRENT_STATS:
        entry = entries.get(entry_id)
        if not entry or entry.get("availability") != "current":
            fail(f"{entry_id} must be current")
        if entry.get("source_owner") != "data/world-country-facts.json":
            fail(f"{entry_id} must consume the same-origin world-country-facts runtime projection")
        if not str(entry.get("source_path", "")).startswith("countries.*.indicators."):
            fail(f"{entry_id} needs an indicators source_path")

    for entry_id in CURRENT_RELATIONS:
        entry = entries.get(entry_id)
        if not entry or entry.get("availability") != "current":
            fail(f"{entry_id} must be current")
        relation_types = entry.get("relation_types")
        if not isinstance(relation_types, list) or not relation_types:
            fail(f"{entry_id} needs relation_types metadata")

    compositor = COMPOSITOR.read_text(encoding="utf-8")
    require(compositor, (
        "WORLD_FACTS_URL",
        "async function scalarValue",
        "async function hasMembership",
        "async function membershipsFor",
        "async function applyRuntimeScalar",
        "queryMode === 'all'",
        "matches.length !== setEntries.length",
        "potato-atlas-query-change",
    ), COMPOSITOR.name)

    builder = FACTS_BUILDER.read_text(encoding="utf-8")
    require(builder, (
        '"indicators"',
        '"gdp"',
        '"gdp_per_capita"',
        '"real_growth"',
        '"inflation"',
        '"unemployment"',
        '"debt_to_gdp"',
    ), FACTS_BUILDER.name)

    selection = SELECTION.read_text(encoding="utf-8")
    require(selection, (
        "function activeRelationTypes",
        "function relationMatches",
        "potato-atlas-layer-change",
    ), SELECTION.name)

    bar = WORLD_BAR.read_text(encoding="utf-8")
    require(bar, (
        "relation.auto",
        "clearRelationLayers",
        "data-layer-option",
    ), WORLD_BAR.name)

    card = COUNTRY_CARD.read_text(encoding="utf-8")
    require(card, (
        "membershipsFor",
        "scalarValue",
        "Active sets",
    ), COUNTRY_CARD.name)

    for path in (COMPOSITOR, WORLD_BAR, COUNTRY_CARD, SELECTION):
        syntax_check(path)

    print(
        "PASS: composable Atlas functionality "
        f"({len(CURRENT_GROUPS)} groups, {len(CURRENT_STATS)} statistics, {len(CURRENT_RELATIONS)} relation filters)"
    )


if __name__ == "__main__":
    main()
