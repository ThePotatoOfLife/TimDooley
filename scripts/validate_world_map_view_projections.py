#!/usr/bin/env python3
"""Validate World Map active-view projection-loss and reconstructability disclosure."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data" / "world-map-view-projections.json"
ATLAS_CONTRACT = ROOT / "data" / "atlas-projection-contract.json"
ACTIVE_VIEW = ROOT / "world-map" / "3d-active-view.js"
WORLD_BAR = ROOT / "world-map" / "3d-world-bar.js"


def main() -> int:
    errors: list[str] = []
    try:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"WORLD MAP VIEW PROJECTION VALIDATION FAILED\n- cannot load contract: {exc}")
        return 1

    atlas = json.loads(ATLAS_CONTRACT.read_text(encoding="utf-8"))
    active = ACTIVE_VIEW.read_text(encoding="utf-8", errors="replace")
    bar = WORLD_BAR.read_text(encoding="utf-8", errors="replace")

    if contract.get("authority") != "data/atlas-projection-contract.json":
        errors.append("view projection contract must point to the shared Atlas projection authority")
    if "information_loss" not in atlas.get("projection_contract", {}).get("after", []):
        errors.append("Atlas projection contract no longer requires information_loss disclosure")
    if "source_path_back" not in atlas.get("projection_contract", {}).get("after", []):
        errors.append("Atlas projection contract no longer requires source_path_back disclosure")

    expected = {"country-scalar", "country-set", "active-country-relations", "country-comparison"}
    views = contract.get("views", {})
    missing = expected - set(views)
    if missing:
        errors.append(f"projection contract missing required views: {sorted(missing)}")

    allowed_reconstructability = set(contract.get("reconstructability_scale", {}))
    for view_id in sorted(expected & set(views)):
        row = views[view_id]
        if not row.get("operation"):
            errors.append(f"{view_id} missing operation")
        if not row.get("preserves"):
            errors.append(f"{view_id} missing preserves list")
        if not row.get("information_loss"):
            errors.append(f"{view_id} missing information_loss list")
        if row.get("reconstructability") not in allowed_reconstructability:
            errors.append(f"{view_id} has invalid reconstructability")
        if not row.get("source_path_back"):
            errors.append(f"{view_id} missing source_path_back")

    for token in (
        "VIEW_PROJECTIONS_URL",
        "projectionSummary",
        "informationLoss",
        "reconstructability",
        "sourcePaths",
        "country-scalar",
        "country-set",
        "active-country-relations",
        "country-comparison",
    ):
        if token not in active:
            errors.append(f"3d-active-view.js missing projection marker: {token}")

    for token in ("View omits", "Reconstructability", "projectionMeta?.informationLoss"):
        if token not in bar:
            errors.append(f"3d-world-bar.js missing projection disclosure marker: {token}")

    if errors:
        print("WORLD MAP VIEW PROJECTION VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    print("WORLD MAP VIEW PROJECTION VALIDATION PASSED")
    print("Active views disclose information loss and source-linked reconstructability.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
