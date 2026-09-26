#!/usr/bin/env python3
"""Validate the three-floor universal site elevator data contract."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECTION = ROOT / "data" / "house" / "elevator-spatial-projection.json"
ROOMS = ROOT / "data" / "house" / "rooms.json"

EXPECTED_LEVELS = ["heaven", "plane", "below"]
REPRESENTATIVE_CONTEXTS = {
    "/": ("plane", "potatoverse-canon"),
    "/tim-dooley/": ("plane", "potatoverse-canon"),
    "/potato-of-life/": ("heaven", "potatoverse-canon"),
    "/religion/": ("heaven", "traditions-texts"),
    "/science/": ("plane", "science-formal-models"),
    "/politics/": ("plane", "world-systems"),
    "/economy/": ("plane", "world-systems"),
    "/context/culture/": ("plane", "culture-information"),
    "/shadow-farm/": ("below", "culture-information"),
    "/context/source-authority/": ("below", "archive-sources"),
    "/research-lab/": ("below", "research-lab"),
    "/works/": ("heaven", "works"),
    "/timeline/": ("plane", "time-history"),
    "/below/": ("below", None),
}


def load_json(path: Path, errors: list[str]) -> dict:
    if not path.exists():
        errors.append(f"missing required file: {path.relative_to(ROOT)}")
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read {path.relative_to(ROOT)}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path.relative_to(ROOT)} must contain a JSON object")
        return {}
    return value


def main() -> int:
    errors: list[str] = []
    projection = load_json(PROJECTION, errors)
    room_contract = load_json(ROOMS, errors)

    active_rooms = {
        row.get("id"): row
        for row in room_contract.get("rooms", [])
        if isinstance(row, dict) and row.get("status") == "active" and row.get("id")
    }
    if len(active_rooms) != 10:
        errors.append(f"expected exactly 10 active governed Rooms, got {len(active_rooms)}")

    levels = [row for row in projection.get("levels", []) if isinstance(row, dict)]
    level_ids = [row.get("id") for row in levels]
    if level_ids != EXPECTED_LEVELS:
        errors.append(f"elevator levels must equal {EXPECTED_LEVELS}, got {level_ids}")
    if "world" in level_ids:
        errors.append("legacy world elevator level must be renamed to plane")

    dwellings = [row for row in projection.get("dwellings", []) if isinstance(row, dict)]
    dwelling_by_id = {row.get("id"): row for row in dwellings if row.get("id")}
    if set(dwelling_by_id) != set(active_rooms):
        missing = sorted(set(active_rooms) - set(dwelling_by_id))
        extra = sorted(set(dwelling_by_id) - set(active_rooms))
        errors.append(f"elevator dwellings must match active Rooms exactly; missing={missing}, extra={extra}")

    allowed = set(EXPECTED_LEVELS)
    for room_id in sorted(active_rooms):
        row = dwelling_by_id.get(room_id)
        if not row:
            continue
        primary = row.get("primary_level")
        projections = row.get("projections")
        if primary not in allowed:
            errors.append(f"{room_id}: primary_level must be one of {EXPECTED_LEVELS}, got {primary!r}")
        if not isinstance(projections, list) or not projections:
            errors.append(f"{room_id}: projections must be a non-empty list")
            continue
        bad = sorted(set(projections) - allowed)
        if bad:
            errors.append(f"{room_id}: unsupported projections {bad}")
        if primary and primary not in projections:
            errors.append(f"{room_id}: primary_level {primary!r} must also appear in projections")

    contexts = [row for row in projection.get("route_contexts", []) if isinstance(row, dict)]
    by_match = {row.get("match"): row for row in contexts if row.get("match")}
    for row in contexts:
        match = row.get("match")
        level_id = row.get("level_id")
        room_id = row.get("room_id")
        if not isinstance(match, str) or not match.startswith("/"):
            errors.append(f"route context has invalid match {match!r}")
        if level_id not in allowed:
            errors.append(f"{match}: route context level_id must be one of {EXPECTED_LEVELS}, got {level_id!r}")
        if room_id is not None and room_id not in active_rooms:
            errors.append(f"{match}: route context references unknown Room {room_id!r}")

    for route, (level_id, room_id) in REPRESENTATIVE_CONTEXTS.items():
        row = by_match.get(route)
        if not row:
            errors.append(f"missing representative route context: {route}")
            continue
        if row.get("level_id") != level_id or row.get("room_id") != room_id:
            errors.append(
                f"{route}: expected ({level_id!r}, {room_id!r}), "
                f"got ({row.get('level_id')!r}, {row.get('room_id')!r})"
            )

    if errors:
        print(f"SITE ELEVATOR DATA VALIDATION FAILED: {len(errors)} issue(s)")
        for error in errors:
            print(f"- {error}")
        return 1

    print("SITE ELEVATOR DATA VALIDATION PASSED")
    print("3 floors · 10 Rooms · representative route contexts verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
