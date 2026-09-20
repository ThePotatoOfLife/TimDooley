#!/usr/bin/env python3
"""Validate the dormant World Map conflict-snapshot contract."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data" / "world-map-conflict-snapshot-contract.json"
SPATIAL = ROOT / "data" / "world-map-spatial-overlays.json"
SURFACES = ROOT / "data" / "world-map-layer-surfaces.json"

EXPECTED_MEANINGS = {
    "control_area_snapshot",
    "contested_area_snapshot",
    "historical_front_snapshot",
    "humanitarian_access_snapshot",
    "event_aggregate",
    "damage_assessment",
}
REQUIRED_SNAPSHOT_FIELDS = {
    "snapshot_id","conflict_id","geometry_meaning","observed_start","observed_end",
    "published_at","temporal_precision","source_ids","confidence","status_note",
    "not_live","administrative_independence",
}


def main() -> int:
    errors: list[str] = []
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    spatial = json.loads(SPATIAL.read_text(encoding="utf-8"))
    surfaces = json.loads(SURFACES.read_text(encoding="utf-8"))

    if contract.get("owner") != "data/world-map-spatial-overlays.json:conflict.context":
        errors.append("conflict contract must point to the canonical spatial conflict owner")

    if set(contract.get("snapshot_required_fields") or []) != REQUIRED_SNAPSHOT_FIELDS:
        errors.append("snapshot_required_fields drifted")

    meanings = set((contract.get("geometry_meanings") or {}).keys())
    if meanings != EXPECTED_MEANINGS:
        errors.append(f"geometry_meanings drifted: {sorted(meanings)}")

    if contract.get("status") != "active-schema-dormant-data":
        errors.append("conflict contract must remain dormant until reviewed geometry exists")

    policy = contract.get("activation_policy") or {}
    for key in (
        "requires_reviewed_geometry",
        "requires_nonempty_source_ids",
        "requires_not_live_true",
        "requires_administrative_independence_true",
    ):
        if policy.get(key) is not True:
            errors.append(f"activation policy must require {key}")

    if policy.get("time_dimension_owner") != "window.__potatoAtlasTime":
        errors.append("conflict snapshots must bind to the canonical Time dimension owner")

    display = contract.get("display_contract") or {}
    required_visible = set(display.get("required_visible_context") or [])
    for token in ("geometry meaning","observation date or range","source attribution","confidence","not-live boundary"):
        if token not in required_visible:
            errors.append(f"display contract missing visible context: {token}")

    boundary = str(display.get("required_boundary_text") or "")
    for token in ("dated","source-attributed","does not replace administrative geography","not live tactical tracking"):
        if token not in boundary:
            errors.append(f"conflict boundary text missing: {token}")

    entries = {row.get("id"): row for row in spatial.get("entries") or []}
    conflict = entries.get("conflict.context") or {}
    if conflict.get("family") != "conflict.context":
        errors.append("spatial manifest lost conflict.context family")
    if conflict.get("epistemic_type") != "event_observed":
        errors.append("conflict.context must remain event_observed")
    if conflict.get("availability") != "planned":
        errors.append("conflict.context must remain planned without reviewed geometry")
    if conflict.get("feature_ids"):
        errors.append("conflict.context must not own geometry before reviewed snapshots are committed")
    status_note = str(conflict.get("status_note") or "")
    for token in ("delayed", "dated", "No live tracking"):
        if token not in status_note:
            errors.append(f"conflict.context status note missing boundary token: {token}")

    plane = next((row for row in surfaces.get("persistent_planes") or [] if row.get("id") == "geography-overlays"), None)
    if not plane:
        errors.append("Geography overlay plane missing")
    else:
        rules = " ".join(plane.get("rules") or [])
        if "overlap never implies equivalence" not in rules:
            errors.append("Geography plane lost overlap-separation rule")

    time_dim = next((row for row in surfaces.get("dimensions") or [] if row.get("id") == "time"), None)
    if not time_dim or time_dim.get("owner") != "window.__potatoAtlasTime":
        errors.append("Time dimension owner drifted")

    for rule in contract.get("separation_rules") or []:
        if not isinstance(rule, str) or not rule.strip():
            errors.append("separation_rules must be non-empty strings")

    if errors:
        print("WORLD MAP CONFLICT SNAPSHOT CONTRACT FAILED")
        for error in errors:
            print("-", error)
        return 1

    print("WORLD MAP CONFLICT SNAPSHOT CONTRACT PASSED")
    print("Schema ready; no live/tactical geometry promoted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
