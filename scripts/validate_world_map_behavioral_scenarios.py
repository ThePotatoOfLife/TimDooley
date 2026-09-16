#!/usr/bin/env python3
"""Run integrated World Map behavioral scenarios across control-plane owners."""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
TEST = ROOT / "scripts" / "test_world_map_behavioral_scenario.mjs"


def main() -> int:
    errors: list[str] = []
    if not TEST.exists():
        errors.append(f"missing behavioral scenario: {TEST.relative_to(ROOT)}")
    node = shutil.which("node")
    if not node:
        errors.append("node executable unavailable; cannot run World Map behavioral scenario")
    elif TEST.exists():
        result = subprocess.run([node, str(TEST)], cwd=ROOT, text=True, capture_output=True, check=False)
        if result.returncode:
            errors.append("integrated behavioral scenario failed: " + (result.stderr.strip() or result.stdout.strip()))

    print("World Map behavioral scenario:")
    print("- antimeridian-safe wrapped geometry")
    print("- semantic overlap arbitration across country/overlay/subdivision/place")
    print("- drag/projection tooltip invalidation with stale-generation suppression")
    print("- typed inspector child/back transitions with URL convergence")
    print(f"Errors: {len(errors)}")
    if errors:
        print("WORLD MAP BEHAVIORAL SCENARIO VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("WORLD MAP BEHAVIORAL SCENARIO VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
