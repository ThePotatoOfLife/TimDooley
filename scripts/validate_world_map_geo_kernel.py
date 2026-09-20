#!/usr/bin/env python3
"""Validate the shared World Map geospatial kernel and projection/wrap regressions."""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
KERNEL = ROOT / "world-map" / "3d-geo-kernel.js"
TEST = ROOT / "scripts" / "test_world_map_geo_kernel.mjs"
PROJECTION_TEST = ROOT / "scripts" / "test_world_map_projection_contract.mjs"
CORE_FIT_WRAP_TEST = ROOT / "scripts" / "test_world_map_core_fit_wrap.mjs"


def main() -> int:
    errors: list[str] = []
    if not KERNEL.exists():
        errors.append("missing world-map/3d-geo-kernel.js")
        source = ""
    else:
        source = KERNEL.read_text(encoding="utf-8", errors="replace")

    for token in (
        "normalizeLongitude",
        "canonicalWorldCopyLongitude",
        "canonicalWorldCopyPoint",
        "shortestLongitudeDelta",
        "unwrapLongitude",
        "minimalLongitudeInterval",
        "antimeridianAwareBounds",
        "haversineDistanceKm",
        "EARTH_MEAN_RADIUS_KM = 6371.0088",
        "window.__potatoAtlasGeo",
    ):
        if token not in source:
            errors.append(f"geospatial kernel missing required interface: {token}")

    node = shutil.which("node")
    if not node:
        errors.append("node executable unavailable; cannot run geospatial regressions")
    else:
        for test_path, label in (
            (TEST, "geospatial-kernel"),
            (PROJECTION_TEST, "projection/wrapped-identity"),
            (CORE_FIT_WRAP_TEST, "core country/compare wrap-safe fit"),
        ):
            if not test_path.exists():
                errors.append(f"missing {test_path.relative_to(ROOT)}")
                continue
            result = subprocess.run(
                [node, str(test_path)], cwd=ROOT, text=True, capture_output=True, check=False
            )
            if result.returncode:
                detail = (result.stderr or result.stdout).strip()
                errors.append(f"{label} regression failed: {detail}")

    print("World Map geospatial kernel:")
    print("- canonical longitude normalization and explicit wrapped-world identity")
    print("- shortest wrapped longitude deltas")
    print("- antimeridian-aware minimum bounds")
    print("- reference-relative longitude unwrapping")
    print("- mean-Earth haversine distance")
    print("- flat/globe projection lifecycle and URL persistence contract")
    print(f"Errors: {len(errors)}")
    if errors:
        print("WORLD MAP GEO KERNEL VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("WORLD MAP GEO KERNEL VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
