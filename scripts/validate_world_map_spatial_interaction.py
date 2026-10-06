#!/usr/bin/env python3
"""Validate spatial-overlay interaction ownership through the shared router."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST = ROOT / "scripts" / "test_world_map_spatial_interaction_ownership.mjs"
MODULE = ROOT / "world-map" / "3d-spatial-overlays.js"


def main() -> int:
    errors: list[str] = []
    for path in (TEST, MODULE):
        if not path.is_file():
            errors.append(f"missing required file: {path.relative_to(ROOT)}")

    node = shutil.which("node")
    if not node:
        errors.append("node executable unavailable; cannot run spatial interaction regression")
    elif not errors:
        syntax = subprocess.run([node, "--check", str(MODULE)], cwd=ROOT, text=True, capture_output=True, check=False)
        if syntax.returncode:
            errors.append("3d-spatial-overlays.js syntax failed: " + (syntax.stderr or syntax.stdout).strip())
        regression = subprocess.run([node, str(TEST)], cwd=ROOT, text=True, capture_output=True, check=False)
        if regression.returncode:
            errors.append("spatial interaction ownership regression failed: " + (regression.stderr or regression.stdout).strip())

    if errors:
        print("WORLD MAP SPATIAL INTERACTION VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    print("WORLD MAP SPATIAL INTERACTION VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
