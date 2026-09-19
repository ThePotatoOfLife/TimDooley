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
APP = ROOT / "world-map" / "3d-app.js"
TEST = ROOT / "scripts" / "test_world_map_scale_contract.mjs"

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
    "country-hubs": {"load": 0, "render": 3.2, "label": 4.0, "interact": 3.2},
    "semantic-interior": {"load": 3.2, "render": 3.6, "label": 4.6, "interact": 3.6},
    "country-relations": {"load": 0, "render": 2.0, "label": 2.0, "interact": 2.0},
    "physical-water-detail": {"load": 3.4, "render": 3.4, "label": 3.4, "interact": 3.4},
    "hydrology": {"load": 4.0, "render": 4.0, "label": 4.0, "interact": 4.0},
    "population-labels": {"load": 3.2, "render": 3.2, "label": 3.2, "interact": 3.2},
    "gateway-labels": {"load": 2.7, "render": 2.7, "label": 2.7, "interact": 2.7},
}


def main() -> int:
    errors: list[str] = []
    for path in (CONTRACT, MODULE, LIFECYCLE, APP, TEST):
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
    app = APP.read_text(encoding="utf-8", errors="replace")

    bands = [(row.get("id"), row.get("min_zoom")) for row in contract.get("bands", [])]
    if bands != EXPECTED_BANDS:
        errors.append(f"named scale bands changed unexpectedly: {bands!r}")
    if contract.get("hysteresis") != 0.12:
        errors.append("scale hysteresis must remain 0.12 for the first migration wave")
    if contract.get("capabilities") != EXPECTED_CAPABILITIES:
        errors.append("scale capability thresholds must match the centralized browsing contract")

    for token in (
        "function createScaleRuntime",
        "function bandForZoom",
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
    for token in (
        "scaleRuntime.threshold('country-hubs', 'render')",
        "scaleRuntime.threshold('country-hubs', 'label')",
        "scaleRuntime.threshold('semantic-interior', 'render')",
        "scaleRuntime.threshold('semantic-interior', 'label')",
        "scaleRuntime.threshold('country-relations', 'render')",
        "scaleRuntime.bandForZoom(map.getZoom())",
    ):
        if token not in app:
            errors.append(f"core renderer does not consume shared scale contract: {token}")
    for legacy in ("minzoom:3.2", "minzoom:3.6", "minzoom:4.6", "map.getZoom()<3.2"):
        if legacy in app:
            errors.append(f"core renderer still owns raw browsing threshold: {legacy}")

    node = shutil.which("node")
    if not node:
        errors.append("node executable unavailable; cannot run scale-contract regression")
    else:
        syntax = subprocess.run([node, "--check", str(MODULE)], cwd=ROOT, text=True, capture_output=True, check=False)
        if syntax.returncode:
            errors.append("3d-scale.js syntax failed: " + (syntax.stderr.strip() or syntax.stdout.strip()))
        result = subprocess.run([node, str(TEST)], cwd=ROOT, text=True, capture_output=True, check=False)
        if result.returncode:
            errors.append("scale-contract regression failed: " + (result.stderr.strip() or result.stdout.strip()))

    print("World Map scale contract:")
    print("- bands: world → macro-region → region → country → subnational → local")
    print("- phases: load / render / label / interact")
    print("- hysteresis: 0.12 zoom")
    print("- consumers: core browsing + Places + subdivisions + Physical Water + Hydrology")
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
