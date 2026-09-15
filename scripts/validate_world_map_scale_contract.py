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
LAYER_TEST = ROOT / "scripts" / "test_world_map_scale_layer_ownership.mjs"
SUBDIVISIONS = ROOT / "world-map" / "3d-subdivisions.js"
PLACES = ROOT / "world-map" / "3d-places.js"

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
}


def main() -> int:
    errors: list[str] = []
    for path in (CONTRACT, MODULE, LIFECYCLE, TEST, LAYER_TEST, SUBDIVISIONS, PLACES):
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
    subdivisions = SUBDIVISIONS.read_text(encoding="utf-8", errors="replace")
    places = PLACES.read_text(encoding="utf-8", errors="replace")

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

    for text, label, required, forbidden in (
        (
            subdivisions,
            "subdivisions",
            (
                "const scale = await scaleRuntime()",
                "scale.threshold('subdivisions', 'render')",
                "scale.threshold('subdivisions', 'label')",
                "scale.bandThreshold('subnational')",
            ),
            ("minzoom:3.4", "minzoom:4.25"),
        ),
        (
            places,
            "Places",
            (
                "const scale = await scaleRuntime()",
                "scale.threshold('places-detail', 'render')",
                "scale.threshold('places-detail', 'label')",
            ),
            ("minzoom:4.2", "minzoom:5.0"),
        ),
    ):
        for token in required:
            if token not in text:
                errors.append(f"{label} does not consume shared scale threshold: {token}")
        for token in forbidden:
            if token in text:
                errors.append(f"{label} still duplicates raw scale threshold: {token}")

    node = shutil.which("node")
    if not node:
        errors.append("node executable unavailable; cannot run scale-contract regression")
    else:
        for path in (MODULE, SUBDIVISIONS, PLACES):
            syntax = subprocess.run([node, "--check", str(path)], cwd=ROOT, text=True, capture_output=True, check=False)
            if syntax.returncode:
                errors.append(f"{path.relative_to(ROOT)} syntax failed: " + (syntax.stderr.strip() or syntax.stdout.strip()))
        for path, label in ((TEST, "scale-contract"), (LAYER_TEST, "scale layer ownership")):
            result = subprocess.run([node, str(path)], cwd=ROOT, text=True, capture_output=True, check=False)
            if result.returncode:
                errors.append(f"{label} regression failed: " + (result.stderr.strip() or result.stdout.strip()))

    print("World Map scale contract:")
    print("- bands: world → macro-region → region → country → subnational → local")
    print("- phases: load / render / label / interact")
    print("- hysteresis: 0.12 zoom")
    print("- Places detail and subdivisions loading/layer thresholds share one owner")
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
