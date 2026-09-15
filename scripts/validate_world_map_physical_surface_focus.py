#!/usr/bin/env python3
"""Validate Physical surface legibility against country-fill tinting."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PHYSICAL = ROOT / "world-map" / "3d-physical-layers.js"


def main() -> int:
    errors: list[str] = []
    if not PHYSICAL.exists():
        errors.append("missing world-map/3d-physical-layers.js")
    else:
        text = PHYSICAL.read_text(encoding="utf-8", errors="replace")
        for token in (
            "SURFACE_FOCUS_IDS",
            "physical.land-cover",
            "physical.aridity",
            "syncCountrySurfaceTint",
            "countries-fill",
            "fill-opacity",
            "feature-state",
            "selected",
            "compare",
            "SURFACE_COUNTRY_OPACITY",
            "DEFAULT_COUNTRY_OPACITY",
        ):
            if token not in text:
                errors.append(f"Physical surface focus missing {token}")
        if "physical.terrain" in text.split("SURFACE_FOCUS_IDS", 1)[-1].split(";", 1)[0]:
            errors.append("Terrain must not trigger surface-focus country tinting")
        if "new MutationObserver(" in text or "setInterval(" in text:
            errors.append("Physical surface focus must not add polling or DOM observers")
        node = shutil.which("node")
        if node:
            result = subprocess.run([node, "--check", str(PHYSICAL)], capture_output=True, text=True)
            if result.returncode:
                errors.append("Physical runtime JavaScript syntax failed: " + (result.stderr.strip() or result.stdout.strip()))

    if errors:
        print("WORLD MAP PHYSICAL SURFACE FOCUS VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    print("WORLD MAP PHYSICAL SURFACE FOCUS VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
