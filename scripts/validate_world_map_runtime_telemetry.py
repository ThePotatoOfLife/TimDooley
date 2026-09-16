#!/usr/bin/env python3
"""Validate bounded World Map runtime observability without duplicate map lifecycle ownership."""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "world-map" / "3d-runtime-telemetry.js"
BOOTSTRAP = ROOT / "world-map" / "3d-bootstrap.js"
TEST = ROOT / "scripts" / "test_world_map_runtime_telemetry.mjs"


def main() -> int:
    errors: list[str] = []
    for path in (MODULE, BOOTSTRAP, TEST):
        if not path.exists():
            errors.append(f"missing runtime telemetry file: {path.relative_to(ROOT)}")
    if errors:
        print("WORLD MAP RUNTIME TELEMETRY VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    module = MODULE.read_text(encoding="utf-8", errors="replace")
    bootstrap = BOOTSTRAP.read_text(encoding="utf-8", errors="replace")
    for token in (
        "function createRuntimeTelemetry",
        "sourceCount",
        "layerCount",
        "visibleLayerCount",
        "sourceTypes",
        "layerTypes",
        "interaction",
        "style",
        "tooltip",
        "sampleCount",
        "potato-atlas-module-ready",
        "potato-atlas-style-generation",
        "potato-atlas-ui-layout-change",
        "window.__potatoAtlasRuntimeTelemetry",
    ):
        if token not in module:
            errors.append(f"runtime telemetry missing contract marker: {token}")
    if "map.on('styledata'" in module or 'map.on("styledata"' in module:
        errors.append("runtime telemetry must consume Style Lifecycle events instead of adding another styledata listener")
    if "loadAfterPaint('Runtime Telemetry', './3d-runtime-telemetry.js')" not in bootstrap:
        errors.append("bootstrap must load Runtime Telemetry after the control-plane foundation")

    node = shutil.which("node")
    if not node:
        errors.append("node executable unavailable; cannot run runtime telemetry regression")
    else:
        result = subprocess.run([node, "--check", str(MODULE)], cwd=ROOT, text=True, capture_output=True, check=False)
        if result.returncode:
            errors.append(f"JavaScript syntax failed for {MODULE.relative_to(ROOT)}: " + (result.stderr.strip() or result.stdout.strip()))
        result = subprocess.run([node, str(TEST)], cwd=ROOT, text=True, capture_output=True, check=False)
        if result.returncode:
            errors.append("runtime telemetry regression failed: " + (result.stderr.strip() or result.stdout.strip()))

    print("World Map runtime telemetry:")
    print("- active source/layer and visible-layer counts")
    print("- source/layer type breakdowns")
    print("- Interaction Router registry/dispatch diagnostics")
    print("- Style Lifecycle generation/restore diagnostics")
    print("- Tooltip generation/invalidation/stale-suppression diagnostics")
    print("- refreshes through existing custom lifecycle events only")
    print(f"Errors: {len(errors)}")
    if errors:
        print("WORLD MAP RUNTIME TELEMETRY VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("WORLD MAP RUNTIME TELEMETRY VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
