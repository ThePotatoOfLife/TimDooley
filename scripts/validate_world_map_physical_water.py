#!/usr/bin/env python3
"""Validate the lazy, scale-adaptive Natural Earth physical-water context."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "world-map-physical-layers.json"
RUNTIME = ROOT / "world-map" / "3d-physical-layers.js"
WATER = ROOT / "world-map" / "3d-physical-water.js"
PINNED_NE_SHA = "ca96624a56bd078437bca8184e78163e5039ad19"


def main() -> int:
    errors: list[str] = []

    if not MANIFEST.exists():
        errors.append("missing physical layer manifest")
        manifest = {}
    else:
        try:
            manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"invalid physical layer manifest: {exc}")
            manifest = {}

    entries = {row.get("id"): row for row in manifest.get("entries", []) if isinstance(row, dict)}
    water = entries.get("physical.water.base") or {}
    if water.get("availability") != "current": errors.append("physical.water.base must be current")
    if water.get("load_policy") != "on_demand": errors.append("physical.water.base must remain on_demand")
    if water.get("kind") != "module": errors.append("physical.water.base must be module-backed")
    if water.get("module") != "./3d-physical-water.js": errors.append("physical.water.base must point to ./3d-physical-water.js")
    source = water.get("source") or {}
    if source.get("provider") != "Natural Earth": errors.append("physical.water.base must name Natural Earth as provider")
    dataset = str(source.get("dataset", ""))
    if "1:110m" not in dataset or "1:50m" not in dataset:
        errors.append("physical.water.base must document both 1:110m overview and 1:50m regional detail")
    if "seam-safe" not in dataset.lower():
        errors.append("physical.water.base must document the seam-safe ocean base")
    if PINNED_NE_SHA not in str(source.get("version", "")):
        errors.append("physical.water.base must pin the Natural Earth source commit")

    if not WATER.exists():
        errors.append("missing world-map/3d-physical-water.js")
    else:
        text = WATER.read_text(encoding="utf-8", errors="replace")
        for token in (
            PINNED_NE_SHA,
            "ne_110m_rivers_lake_centerlines.geojson",
            "ne_110m_lakes.geojson",
            "ne_110m_coastline.geojson",
            "ne_50m_rivers_lake_centerlines.geojson",
            "ne_50m_lakes.geojson",
            "ne_50m_coastline.geojson",
            "atlas-physical-water-ocean-grid",
            "atlas-physical-water-land-mask",
            "buildOceanMesh",
            "OCEAN_SOURCE",
            "landMask",
            "physical-surface",
            "physical-water",
            "physical-line",
            "buffer: 0",
            "scale.threshold('physical-water-detail', 'load')",
            "ensureDetailSources",
            "detailInstalled",
            "zoomend",
            "visibility",
            "__potatoAtlasPhysicalWater",
            "enable",
            "disable",
        ):
            if token not in text:
                errors.append(f"physical water module missing {token}")
        for forbidden in ("ne_110m_ocean.geojson", "ne_50m_ocean.geojson"):
            if forbidden in text:
                errors.append(f"physical water must not load globe-spanning Natural Earth ocean polygon: {forbidden}")
        if "map.getZoom() >= DETAIL_ZOOM" not in text:
            errors.append("physical water detail must be zoom-gated")
        if "const DETAIL_ZOOM = 3.4" in text:
            errors.append("physical water must not own a duplicate raw 3.4 detail threshold")
        detail_has_native_minzoom = "const minZoom = detail ? DETAIL_ZOOM : 0;" in text
        syncs_only_after_zoom = "map.on('zoomend'" in text and "map.on('zoom'," not in text
        if detail_has_native_minzoom and syncs_only_after_zoom:
            errors.append("physical water detail must not combine native DETAIL_ZOOM minzoom with zoomend-only visibility switching; it creates a transient water gap while zooming out")
        if "new MutationObserver(" in text or "setInterval(" in text:
            errors.append("physical water module must not poll or observe the DOM")
        node = shutil.which("node")
        if node:
            result = subprocess.run([node, "--check", str(WATER)], capture_output=True, text=True)
            if result.returncode:
                errors.append("physical water JavaScript syntax failed: " + (result.stderr.strip() or result.stdout.strip()))

    if not RUNTIME.exists():
        errors.append("missing physical layer runtime")
    else:
        runtime = RUNTIME.read_text(encoding="utf-8", errors="replace")
        for token in ("controller", "__potatoAtlasPhysicalWater"):
            if token not in runtime:
                errors.append(f"physical runtime missing generic module controller marker: {token}")

    if errors:
        print("WORLD MAP PHYSICAL WATER VALIDATION FAILED")
        for error in errors: print("-", error)
        return 1

    print("WORLD MAP PHYSICAL WATER VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
