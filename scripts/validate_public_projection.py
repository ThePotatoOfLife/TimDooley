#!/usr/bin/env python3
"""Validate the canonical backend -> frontend projection contract.

This gate protects the five-door public architecture from drifting back toward the
retired single-index/root.js reader while ensuring every public archive branch has
an explicit human projection status.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_DOORS = {
    "tim": "tim-dooley/",
    "religion": "religion/",
    "philosophy": "philosophy/",
    "science": "science/",
    "world_map": "world-map/",
}

EXPECTED_INTERACTIVE_ROUTES = {
    "branch": "explore/#branch=<id>",
    "record": "explore/#record=<path>",
    "context": "explore/#context=<id>",
    "pathway": "explore/#path=<id>",
}


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

    errors: list[str] = []

    public_doors = bridge.get("public_doors")
    if public_doors != EXPECTED_DOORS:
        fail(
            f"frontend bridge public_doors must equal {EXPECTED_DOORS!r}; got {public_doors!r}",
            errors,
        )

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
        fail(
            "branch projection entries must have exactly one valid primary_door/global_route/backend_only state: "
            + ", ".join(sorted(malformed)),
            errors,
        )

    bridge_routes = bridge.get("route_map", {})
    if any("index.html#node=" in str(value) for value in bridge_routes.values()):
        fail("frontend bridge still exposes retired index.html#node= record routing", errors)

    if contains_live_retired_reference(coverage):
        fail("backend coverage map still names retired root.js or index.html#node= as a live consumer", errors)

    interactive_routes = atlas.get("interactive_routes", {})
    if interactive_routes != EXPECTED_INTERACTIVE_ROUTES:
        fail(
            f"atlas interactive_routes must equal {EXPECTED_INTERACTIVE_ROUTES!r}; got {interactive_routes!r}",
            errors,
        )

    reader_guide = (ROOT / "app" / "reader-guide.js").read_text(encoding="utf-8")
    if 'href="learn/"' in reader_guide or "href='learn/'" in reader_guide:
        fail("reader guide still routes to retired learn/ Start Here surface", errors)

    if errors:
        print("Public projection validation FAILED")
        for error in errors:
            print(f" - {error}")
        return 1

    print(
        "Public projection validation passed: "
        f"{len(EXPECTED_DOORS)} doors, {len(branch_ids)} projected branches, Explore owns deep interactive routing."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
