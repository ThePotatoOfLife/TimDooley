#!/usr/bin/env python3
"""Validate typed semantic inspector history for the World Map."""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / "world-map" / "3d-inspector-router.js"
TEST = ROOT / "scripts" / "test_world_map_inspector_router.mjs"
LIFECYCLE = ROOT / "world-map" / "3d-panel-lifecycle.js"


def main() -> int:
    errors: list[str] = []
    for path in (ROUTER, TEST, LIFECYCLE):
        if not path.exists():
            errors.append(f"missing inspector-router file: {path.relative_to(ROOT)}")
    if errors:
        print("WORLD MAP INSPECTOR ROUTER VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    router = ROUTER.read_text(encoding="utf-8", errors="replace")
    lifecycle = LIFECYCLE.read_text(encoding="utf-8", errors="replace")
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

    node = shutil.which("node")
    if not node:
        errors.append("node executable unavailable; cannot run inspector-router regression")
    else:
        result = subprocess.run([node, "--check", str(ROUTER)], cwd=ROOT, text=True, capture_output=True, check=False)
        if result.returncode:
            errors.append("inspector router JavaScript syntax failed: " + (result.stderr.strip() or result.stdout.strip()))
        result = subprocess.run([node, str(TEST)], cwd=ROOT, text=True, capture_output=True, check=False)
        if result.returncode:
            errors.append("inspector-router regression failed: " + (result.stderr.strip() or result.stdout.strip()))

    print("World Map inspector router:")
    print("- typed semantic history")
    print("- deterministic parent restoration")
    print("- serializable state snapshots")
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
