#!/usr/bin/env python3
"""Validate typed semantic inspector history and migrated World Map consumers."""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / "world-map" / "3d-inspector-router.js"
TEST = ROOT / "scripts" / "test_world_map_inspector_router.mjs"
CONSUMER_TEST = ROOT / "scripts" / "test_world_map_inspector_consumers.mjs"
LIFECYCLE = ROOT / "world-map" / "3d-panel-lifecycle.js"
PLACES = ROOT / "world-map" / "3d-places.js"
SUBDIVISIONS = ROOT / "world-map" / "3d-subdivisions.js"


def main() -> int:
    errors: list[str] = []
    for path in (ROUTER, TEST, CONSUMER_TEST, LIFECYCLE, PLACES, SUBDIVISIONS):
        if not path.exists():
            errors.append(f"missing inspector-router file: {path.relative_to(ROOT)}")
    if errors:
        print("WORLD MAP INSPECTOR ROUTER VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    router = ROUTER.read_text(encoding="utf-8", errors="replace")
    lifecycle = LIFECYCLE.read_text(encoding="utf-8", errors="replace")
    places = PLACES.read_text(encoding="utf-8", errors="replace")
    subdivisions = SUBDIVISIONS.read_text(encoding="utf-8", errors="replace")
    for token in (
        "function createInspectorRouter",
        "function setBaseline",
        "function open",
        "function back",
        "function current",
        "function state",
        "potato-atlas-inspector-change",
        "window.__potatoAtlasInspector",
    ):
        if token not in router:
            errors.append(f"inspector router missing interface marker: {token}")
    if "__potatoAtlasLoadModule?.('Inspector Router', './3d-inspector-router.js')" not in lifecycle:
        errors.append("panel lifecycle must preload the shared Inspector Router before Places/subdivisions")

    for label, source, node_type in (("Places", places, "place"), ("Subdivisions", subdivisions, "subdivision")):
        for token in (
            "const inspector = window.__potatoAtlasInspector",
            "inspector.setBaseline(",
            "inspector.open(",
            "inspector.back()",
            f"type:'{node_type}'",
        ):
            if token not in source:
                errors.append(f"{label} inspector migration missing marker: {token}")
        if "panelSnapshot" in source:
            errors.append(f"{label} must not retain raw panelSnapshot state after inspector migration")

    node = shutil.which("node")
    if not node:
        errors.append("node executable unavailable; cannot run inspector-router regressions")
    else:
        for path in (ROUTER, PLACES, SUBDIVISIONS):
            result = subprocess.run([node, "--check", str(path)], cwd=ROOT, text=True, capture_output=True, check=False)
            if result.returncode:
                errors.append(f"JavaScript syntax failed for {path.relative_to(ROOT)}: " + (result.stderr.strip() or result.stdout.strip()))
        for test_path, label in ((TEST, "inspector-router"), (CONSUMER_TEST, "inspector-consumer")):
            result = subprocess.run([node, str(test_path)], cwd=ROOT, text=True, capture_output=True, check=False)
            if result.returncode:
                errors.append(f"{label} regression failed: " + (result.stderr.strip() or result.stdout.strip()))

    print("World Map inspector router:")
    print("- typed semantic history")
    print("- deterministic parent restoration")
    print("- serializable state snapshots")
    print("- Places/subdivisions render live semantic parents instead of raw HTML snapshots")
    print(f"Errors: {len(errors)}")
    if errors:
        print("WORLD MAP INSPECTOR ROUTER VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("WORLD MAP INSPECTOR ROUTER VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
