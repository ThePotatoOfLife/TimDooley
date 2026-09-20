#!/usr/bin/env python3
"""Validate the shared World Map geospatial kernel and its behavioral regression."""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
KERNEL = ROOT / "world-map" / "3d-geo-kernel.js"
SUBDIVISIONS = ROOT / "world-map" / "3d-subdivisions.js"
TEST = ROOT / "scripts" / "test_world_map_geo_kernel.mjs"
CORE_FIT_WRAP_TEST = ROOT / "scripts" / "test_world_map_core_fit_wrap.mjs"
SUBDIVISION_WRAP_TEST = ROOT / "scripts" / "test_world_map_subdivision_wrap_fit.mjs"
SPATIAL_OVERLAY_WRAP_TEST = ROOT / "scripts" / "test_world_map_spatial_overlay_wrap_fit.mjs"


def main() -> int:
    errors: list[str] = []
    if not KERNEL.exists():
        errors.append("missing world-map/3d-geo-kernel.js")
        source = ""
    else:
        source = KERNEL.read_text(encoding="utf-8", errors="replace")

    subdivisions = SUBDIVISIONS.read_text(encoding="utf-8", errors="replace") if SUBDIVISIONS.exists() else ""
    if not subdivisions:
        errors.append("missing world-map/3d-subdivisions.js")
    elif "window.__potatoAtlasGeo =" in subdivisions:
        errors.append("subdivisions must consume, not publish, the Geo singleton")

    for token in (
        "normalizeLongitude",
        "shortestLongitudeDelta",
        "unwrapLongitude",
        "minimalLongitudeInterval",
        "antimeridianAwareBounds",
        "pointInGeometry",
        "haversineDistanceKm",
        "EARTH_MEAN_RADIUS_KM = 6371.0088",
        "window.__potatoAtlasGeo",
    ):
        if token not in source:
            errors.append(f"geospatial kernel missing required interface: {token}")

    node = shutil.which("node")
    if not node:
        errors.append("node executable unavailable; cannot run geospatial-kernel regression")
    else:
        for test_path, label in (
            (TEST, "geospatial-kernel"),
            (CORE_FIT_WRAP_TEST, "core country/compare wrap-safe fit"),
            (SUBDIVISION_WRAP_TEST, "subdivision wrap-safe fit"),
            (SPATIAL_OVERLAY_WRAP_TEST, "spatial overlay wrap-safe fit"),
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
    print("- canonical longitude normalization")
    print("- shortest wrapped longitude deltas")
    print("- antimeridian-aware minimum bounds")
    print("- point-in-polygon / multipolygon containment")
    print("- reference-relative longitude unwrapping")
    print("- mean-Earth haversine distance")
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
