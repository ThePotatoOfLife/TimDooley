#!/usr/bin/env python3
"""Validate shared reduced-motion ownership across World Map camera transitions."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOTION = ROOT / "world-map" / "3d-motion.js"
HOVER = ROOT / "world-map" / "3d-hover.js"
INDEX = ROOT / "world-map" / "index.html"
TEST = ROOT / "scripts" / "test_world_map_reduced_motion.mjs"
CONSUMERS = (
    ROOT / "world-map" / "3d-app.js",
    ROOT / "world-map" / "3d-places.js",
    ROOT / "world-map" / "3d-subdivisions.js",
    ROOT / "world-map" / "3d-adl-heat.js",
    ROOT / "world-map" / "3d-mud-below-us.js",
    ROOT / "world-map" / "3d-axis.js",
    ROOT / "world-map" / "3d-axis-depth.js",
    ROOT / "world-map" / "3d-symbolic-operators.js",
)

def main() -> int:
    errors: list[str] = []
    for path in (MOTION, HOVER, INDEX, TEST, *CONSUMERS):
        if not path.is_file():
            errors.append(f"missing reduced-motion contract file: {path.relative_to(ROOT)}")
    if errors:
        print("WORLD MAP REDUCED MOTION VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    motion = MOTION.read_text(encoding="utf-8", errors="replace")
    for token in (
        "prefers-reduced-motion: reduce",
        "function prefersReducedMotion",
        "next.duration = 0",
        "next.animate = false",
        "function easeTo",
        "function fitBounds",
        "window.__potatoAtlasMotion",
    ):
        if token not in motion:
            errors.append(f"motion policy missing marker: {token}")

    hover = HOVER.read_text(encoding="utf-8", errors="replace")
    motion_boot = hover.find("await import(versionedModule('./3d-motion.js'))")
    app_boot = hover.find("await import(versionedModule('./3d-app.js'))")
    if motion_boot < 0 or app_boot < 0 or motion_boot > app_boot:
        errors.append("shared motion policy must preload before core 3d-app.js")

    for path in CONSUMERS:
        text = path.read_text(encoding="utf-8", errors="replace")
        if "__potatoAtlasMotion" not in text and "motion." not in text:
            errors.append(f"camera consumer does not use shared motion policy: {path.relative_to(ROOT)}")

    html = INDEX.read_text(encoding="utf-8", errors="replace")
    if "@media(prefers-reduced-motion:reduce)" not in html:
        errors.append("World Map shell must disable decorative transitions for reduced motion")

    node = shutil.which("node")
    if not node:
        errors.append("node executable unavailable; cannot run reduced-motion regression")
    else:
        syntax = subprocess.run([node, "--check", str(MOTION)], cwd=ROOT, text=True, capture_output=True, check=False)
        if syntax.returncode:
            errors.append("3d-motion.js syntax failed: " + (syntax.stderr.strip() or syntax.stdout.strip()))
        result = subprocess.run([node, str(TEST)], cwd=ROOT, text=True, capture_output=True, check=False)
        if result.returncode:
            errors.append("reduced-motion regression failed: " + (result.stderr.strip() or result.stdout.strip()))

    if errors:
        print("WORLD MAP REDUCED MOTION VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("WORLD MAP REDUCED MOTION VALIDATION PASSED")
    return 0

if __name__ == "__main__":
    sys.exit(main())
