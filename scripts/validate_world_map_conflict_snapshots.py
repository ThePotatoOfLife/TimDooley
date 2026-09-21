#!/usr/bin/env python3
"""Validate the dormant World Map conflict-snapshot contract."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data" / "world-map-conflict-snapshot-contract.json"
SPATIAL = ROOT / "data" / "world-map-spatial-overlays.json"
SURFACES = ROOT / "data" / "world-map-layer-surfaces.json"
SOURCES = ROOT / "data" / "world-map-conflict-sources"
IMPORTER = ROOT / "scripts" / "import_world_conflict_event_aggregate.py"
IMPORTER_TEST = ROOT / "scripts" / "test_world_map_conflict_event_aggregate.py"

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

    if contract.get("status") not in {"active-schema-dormant-data","active-schema-acquisition-ready"}:
        errors.append("conflict contract status must remain schema-only until reviewed geometry exists")

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

    if contract.get("source_contract_directory") != "data/world-map-conflict-sources":
        errors.append("conflict source-contract directory must remain canonical")
    if "scripts/import_world_conflict_event_aggregate.py" not in (contract.get("importers") or []):
        errors.append("conflict contract missing canonical event-aggregate importer")
    if not IMPORTER.is_file() or not IMPORTER_TEST.is_file():
        errors.append("conflict aggregate importer/test missing")
    if not SOURCES.is_dir():
        errors.append("conflict source-contract directory missing")
    else:
        source_files=sorted(SOURCES.glob("*.json"))
        if not source_files:
            errors.append("no conflict source acquisition contracts")
        for path in source_files:
            source=json.loads(path.read_text(encoding="utf-8"))
            if source.get("runtime_fetch_allowed") is not False:
                errors.append(f"{path.name}: conflict source acquisition must remain build-time only")
            if source.get("intended_geometry_meaning") not in EXPECTED_MEANINGS:
                errors.append(f"{path.name}: unsupported intended geometry meaning")
            if source.get("license") == "CC BY 4.0" and "UCDP" in str(source.get("owner") or ""):
                if source.get("status") != "source-verified-download-pending":
                    errors.append(f"{path.name}: unacquired UCDP source must remain download-pending")
                requirements=" ".join(source.get("promotion_requirements") or []).lower()
                for token in ("sha-256","coarse grid","raw event coordinates","administrative geography independent"):
                    if token not in requirements:
                        errors.append(f"{path.name}: promotion requirements missing {token}")
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

    if IMPORTER_TEST.is_file():
        result=subprocess.run([sys.executable,str(IMPORTER_TEST)],cwd=ROOT,capture_output=True,text=True)
        if result.returncode:
            errors.append("conflict event-aggregate importer regression failed: "+(result.stderr or result.stdout).strip())

    if errors:
        print("WORLD MAP CONFLICT SNAPSHOT CONTRACT FAILED")
        for error in errors:
            print("-", error)
        return 1

    print("WORLD MAP CONFLICT SNAPSHOT CONTRACT PASSED")
    print("Schema + guarded acquisition ready; no live/tactical geometry promoted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
