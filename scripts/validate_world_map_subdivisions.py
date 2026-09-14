#!/usr/bin/env python3
"""Validate the first generic subdivision integration surface."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_world_subdivisions.py"
MODULE = ROOT / "world-map" / "3d-subdivisions.js"
LIFECYCLE = ROOT / "world-map" / "3d-panel-lifecycle.js"
INDEX = ROOT / "data" / "world-subdivisions" / "index.json"
USA = ROOT / "data" / "world-subdivisions" / "USA.geo.json"
INTERACTION_TEST = ROOT / "scripts" / "test_world_map_subdivision_interaction.mjs"


def main() -> int:
    errors: list[str] = []
    required = (BUILDER, MODULE, LIFECYCLE, INDEX, USA, INTERACTION_TEST)
    for path in required:
        if not path.exists():
            errors.append(f"missing subdivision integration file: {path.relative_to(ROOT)}")
    if not errors:
        builder = BUILDER.read_text(encoding="utf-8")
        module = MODULE.read_text(encoding="utf-8")
        lifecycle = LIFECYCLE.read_text(encoding="utf-8")
        index = json.loads(INDEX.read_text(encoding="utf-8"))
        usa = json.loads(USA.read_text(encoding="utf-8"))
        for token in ("GENZ2025", "cb_2025_us_state_20m.zip", "NST-EST2025-ALLDATA.csv", "EXPECTED_US_UNITS = 51", "parse_state_kml", "federal district"):
            if token not in builder:
                errors.append(f"subdivision builder missing marker: {token}")
        for token in ("world-subdivisions/index.json", "USA.geo.json", "atlas-subdivision", "subdivision=", "potato-atlas-subdivision-select", "__potatoAtlasOverlayHandled", "pendingDeepLinkId"):
            if token not in module:
                errors.append(f"subdivision module missing marker: {token}")
        if "3d-subdivisions.js" not in lifecycle or "map.getZoom() < 3.4" not in lifecycle:
            errors.append("regional-scale lazy subdivision loading is not registered")
        descriptor = index.get("partitions", {}).get("USA", {})
        if descriptor.get("feature_count") != 51:
            errors.append("USA subdivision index must declare 51 first-wave features")
        features = usa.get("features", []) if usa.get("type") == "FeatureCollection" else []
        if len(features) != 51:
            errors.append(f"USA subdivision snapshot must contain 51 features; found {len(features)}")
        ids = [str((feature.get("properties") or {}).get("id") or "") for feature in features]
        if len(set(ids)) != 51 or not all(value.startswith("US-") for value in ids):
            errors.append("USA subdivision ids must be 51 unique US-* identifiers")
        dc = next((feature for feature in features if (feature.get("properties") or {}).get("id") == "US-DC"), None)
        if not dc or dc.get("properties", {}).get("subdivision_type") != "federal district":
            errors.append("District of Columbia must remain explicitly typed as a federal district")
        for feature in features:
            props = feature.get("properties") or {}
            population = props.get("population") or {}
            if not isinstance(population.get("value"), (int, float)) or population.get("value", 0) <= 0:
                errors.append(f"{props.get('id')}: missing positive population")
            if population.get("period") != 2025 or population.get("unit") != "persons" or not population.get("source"):
                errors.append(f"{props.get('id')}: incomplete population provenance")
            if not props.get("area_definition") or "ALAND" not in props.get("area_definition", ""):
                errors.append(f"{props.get('id')}: area provenance is not explicit")
        node = shutil.which("node")
        if node:
            checked = subprocess.run([node, "--check", str(MODULE)], capture_output=True, text=True)
            if checked.returncode:
                errors.append("3d-subdivisions.js syntax failed: " + (checked.stderr.strip() or checked.stdout.strip()))
            interaction = subprocess.run([node, str(INTERACTION_TEST)], capture_output=True, text=True)
            if interaction.returncode:
                errors.append("subdivision interaction regression failed: " + (interaction.stderr.strip() or interaction.stdout.strip()))
    if errors:
        print("WORLD MAP SUBDIVISION VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("WORLD MAP SUBDIVISION VALIDATION PASSED · USA 51/51 · state click refit loop guarded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
