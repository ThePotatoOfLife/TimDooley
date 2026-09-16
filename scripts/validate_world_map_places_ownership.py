#!/usr/bin/env python3
"""Validate Places interaction ownership and collision-aware label layout."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLACES = ROOT / "world-map" / "3d-places.js"
TESTS = (
    ROOT / "scripts" / "test_world_map_places_interaction_ownership.mjs",
    ROOT / "scripts" / "test_world_map_place_label_density.mjs",
)


def main() -> int:
    errors: list[str] = []
    for path in (PLACES, *TESTS):
        if not path.is_file():
            errors.append(f"missing required file: {path.relative_to(ROOT)}")

    node = shutil.which("node")
    if not node:
        errors.append("node executable unavailable; cannot run Places ownership regressions")
    elif not errors:
        syntax = subprocess.run([node, "--check", str(PLACES)], cwd=ROOT, text=True, capture_output=True, check=False)
        if syntax.returncode:
            errors.append("3d-places.js syntax failed: " + (syntax.stderr or syntax.stdout).strip())
        for test in TESTS:
            result = subprocess.run([node, str(test)], cwd=ROOT, text=True, capture_output=True, check=False)
            if result.returncode:
                errors.append(f"{test.name} failed: " + (result.stderr or result.stdout).strip())

    if errors:
        print("WORLD MAP PLACES OWNERSHIP VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    print("WORLD MAP PLACES OWNERSHIP VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
