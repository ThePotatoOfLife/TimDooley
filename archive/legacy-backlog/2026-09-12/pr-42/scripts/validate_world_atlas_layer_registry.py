#!/usr/bin/env python3
"""Validate the browser-facing World Atlas layer registry.

This validator is intentionally structural. Canonical data values remain owned by
other repository files; this checks that presentation metadata cannot silently
collapse semantic types or visual channels.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data" / "world-atlas-layer-registry.json"

ALLOWED_KINDS = {
    "set", "scalar", "composition", "network", "flow", "place",
    "derived", "context", "timeline",
}
ALLOWED_CHANNELS = {
    "fill", "pattern", "outline", "line", "point", "height",
    "card", "timeline", "scene",
}
ALLOWED_EPISTEMIC = {
    "observed", "derived", "project_interpretive", "scenario", "contextual",
}
ALLOWED_AVAILABILITY = {"current", "planned", "experimental", "retired"}


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> None:
    if not REGISTRY_PATH.exists():
        fail(f"missing {REGISTRY_PATH.relative_to(ROOT)}")

    try:
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON: {exc}")

    if registry.get("id") != "world-atlas-layer-registry":
        fail("registry id must be world-atlas-layer-registry")

    families = registry.get("families")
    entries = registry.get("entries")
    channels = registry.get("visual_channels")
    query_rules = registry.get("query_rules")
    if not isinstance(families, list) or not families:
        fail("families must be a non-empty list")
    if not isinstance(entries, list) or not entries:
        fail("entries must be a non-empty list")
    if not isinstance(channels, dict) or set(channels) != ALLOWED_CHANNELS:
        fail("visual_channels must declare exactly the supported channel ids")
    if not isinstance(query_rules, dict):
        fail("query_rules must be an object")
    if query_rules.get("selection_channel") != "outline":
        fail("selection_channel must remain outline")
    if query_rules.get("single_scalar_fill") is not True:
        fail("single_scalar_fill must be true")

    family_ids: set[str] = set()
    for family in families:
        fid = family.get("id")
        if not isinstance(fid, str) or not fid:
            fail("every family needs a non-empty id")
        if fid in family_ids:
            fail(f"duplicate family id {fid}")
        family_ids.add(fid)

    entry_ids: set[str] = set()
    current_count = 0
    for entry in entries:
        eid = entry.get("id")
        if not isinstance(eid, str) or not eid:
            fail("every entry needs a non-empty id")
        if eid in entry_ids:
            fail(f"duplicate entry id {eid}")
        entry_ids.add(eid)

        family = entry.get("family")
        if family not in family_ids:
            fail(f"{eid}: unknown family {family!r}")
        kind = entry.get("kind")
        channel = entry.get("visual_channel")
        epistemic = entry.get("epistemic_type")
        availability = entry.get("availability")
        if kind not in ALLOWED_KINDS:
            fail(f"{eid}: unsupported kind {kind!r}")
        if channel not in ALLOWED_CHANNELS:
            fail(f"{eid}: unsupported visual channel {channel!r}")
        if epistemic not in ALLOWED_EPISTEMIC:
            fail(f"{eid}: unsupported epistemic type {epistemic!r}")
        if availability not in ALLOWED_AVAILABILITY:
            fail(f"{eid}: unsupported availability {availability!r}")
        if not isinstance(entry.get("source_owner"), str) or not entry["source_owner"]:
            fail(f"{eid}: source_owner is required")
        if availability == "current":
            current_count += 1

        if kind == "set" and channel != "pattern":
            fail(f"{eid}: set entries must use the pattern channel")
        if kind == "scalar" and channel not in {"fill", "height"}:
            fail(f"{eid}: scalar entries must use fill or height")
        if kind in {"network", "flow"} and channel != "line":
            fail(f"{eid}: network/flow entries must use line")
        if kind == "place" and channel != "point":
            fail(f"{eid}: place entries must use point")
        if channel == "outline":
            fail(f"{eid}: outline is reserved for interaction/selection, not registry data")
        if kind == "scalar":
            for required in ("unit", "transform", "direction"):
                if not isinstance(entry.get(required), str) or not entry[required]:
                    fail(f"{eid}: scalar entry missing {required}")
        if epistemic == "project_interpretive" and not entry.get("notes") and family == "axis":
            fail(f"{eid}: Axis project interpretation requires boundary notes")

    required_current = {
        "axis.north", "axis.west", "axis.east", "axis.south",
        "group.nato", "group.brics", "group.aukus", "group.five-eyes",
        "religion.christian", "religion.muslim", "stat.population", "stat.area",
        "relation.auto",
    }
    missing = sorted(required_current - entry_ids)
    if missing:
        fail(f"required first-slice entries missing: {', '.join(missing)}")

    contracts = registry.get("source_contracts", {})
    for key in ("domains", "indicators", "country_method", "world_memberships", "demography", "placement"):
        value = contracts.get(key)
        if not isinstance(value, str) or not value:
            fail(f"source_contracts.{key} is required")

    print(
        "PASS: world atlas layer registry "
        f"({len(families)} families, {len(entries)} entries, {current_count} current)"
    )


if __name__ == "__main__":
    main()
