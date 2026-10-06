#!/usr/bin/env python3
"""Validate the named World Map camera-scale contract and live ownership."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data" / "world-map-scale-contract.json"
MODULE = ROOT / "world-map" / "3d-scale.js"
LIFECYCLE = ROOT / "world-map" / "3d-panel-lifecycle.js"
TEST = ROOT / "scripts" / "test_world_map_scale_contract.mjs"
ADL_SCALE_TEST = ROOT / "scripts" / "test_world_map_adl_scale_ownership.mjs"

EXPECTED_BANDS = [
    ("world", 0),
    ("macro-region", 2.5),
    ("region", 3.4),
    ("country", 4.2),
    ("subnational", 5.8),
    ("local", 8.0),
]
EXPECTED_CAPABILITIES = {
    "subdivisions": {"load": 3.4, "render": 3.4, "label": 4.25, "interact": 3.4},
    "places-detail": {"load": 4.2, "render": 4.2, "label": 5.0, "interact": 4.2},
    "adl-heat-points": {"render": 4.2, "interact": 4.2},
    "physical-water-detail": {"load": 3.4, "render": 3.4},
    "physical-hydrology": {"load": 4.0, "render": 4.0},
    "hydrology-rivers-medium": {"load": 5.2},
    "hydrology-rivers-fine": {"load": 6.7},
    "hydrology-rivers-detailed": {"load": 8.2},
}


def main() -> int:
    errors: list[str] = []
    for path in (CONTRACT, MODULE, LIFECYCLE, TEST):
        if not path.exists():
            errors.append(f"missing scale-contract file: {path.relative_to(ROOT)}")
    if errors:
        for error in errors:
            print("-", error)
        return 1

    try:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    except Exception as exc:
        print("WORLD MAP SCALE CONTRACT VALIDATION FAILED")
        print("- invalid scale contract:", exc)
        return 1

    module = MODULE.read_text(encoding="utf-8", errors="replace")
    lifecycle = LIFECYCLE.read_text(encoding="utf-8", errors="replace")

    bands = [(row.get("id"), row.get("min_zoom")) for row in contract.get("bands", [])]
    if bands != EXPECTED_BANDS:
        errors.append(f"named scale bands changed unexpectedly: {bands!r}")
    if contract.get("hysteresis") != 0.12:
        errors.append("scale hysteresis must remain 0.12 for the first migration wave")
    if contract.get("capabilities") != EXPECTED_CAPABILITIES:
        errors.append("first-wave capability thresholds must preserve existing visible thresholds")

    for token in (
        "function createScaleRuntime",
        "function bandForZoom",
        "function bandThreshold",
        "function transition",
        "function capabilityActive",
        "function threshold",
        "window.__potatoAtlasScale",
        "potato-atlas-scale-ready",
    ):
        if token not in module:
            errors.append(f"scale runtime missing interface marker: {token}")

    for token in (
        "__potatoAtlasLoadModule?.('Scale', './3d-scale.js')",
        "capabilityActive('places-detail', 'load'",
        "capabilityActive('subdivisions', 'load'",
        "placesDetailScaleActive",
        "subdivisionsScaleActive",
    ):
        if token not in lifecycle:
            errors.append(f"panel lifecycle does not consume shared scale contract: {token}")
    for legacy in ("map.getZoom() < 4.2", "map.getZoom() < 3.4"):
        if legacy in lifecycle:
            errors.append(f"panel lifecycle still owns duplicate raw zoom threshold: {legacy}")

    node = shutil.which("node")
    if not node:
        errors.append("node executable unavailable; cannot run scale-contract regression")
    else:
        syntax = subprocess.run([node, "--check", str(MODULE)], cwd=ROOT, text=True, capture_output=True, check=False)
        if syntax.returncode:
            errors.append("3d-scale.js syntax failed: " + (syntax.stderr.strip() or syntax.stdout.strip()))
        for test_path, label in (
            (TEST, "scale-contract"),
            (ADL_SCALE_TEST, "ADL point scale ownership"),
        ):
            if not test_path.exists():
                errors.append(f"missing scale regression: {test_path.relative_to(ROOT)}")
                continue
            result = subprocess.run([node, str(test_path)], cwd=ROOT, text=True, capture_output=True, check=False)
            if result.returncode:
                errors.append(f"{label} regression failed: " + (result.stderr.strip() or result.stdout.strip()))

    print("World Map scale contract:")
    print("- bands: world → macro-region → region → country → subnational → local")
    print("- phases: load / render / label / interact")
    print("- hysteresis: 0.12 zoom")
    print("- consumers: Places · subdivisions · physical water detail · hydrology request density")
    print(f"Errors: {len(errors)}")
    if errors:
        print("WORLD MAP SCALE CONTRACT VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("WORLD MAP SCALE CONTRACT VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
