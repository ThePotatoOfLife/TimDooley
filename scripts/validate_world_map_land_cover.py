#!/usr/bin/env python3
"""Validate the lazy ESA WorldCover visual land-cover layer."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "world-map-physical-layers.json"
LAND = ROOT / "world-map" / "3d-physical-land-cover.js"
RUNTIME = ROOT / "world-map" / "3d-physical-layers.js"


def main() -> int:
    errors: list[str] = []
    manifest = {}
    if not MANIFEST.exists():
        errors.append("missing physical layer manifest")
    else:
        try:
            manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"invalid physical layer manifest: {exc}")

    entries = {row.get("id"): row for row in manifest.get("entries", []) if isinstance(row, dict)}
    row = entries.get("physical.land-cover") or {}
    if row.get("availability") != "current": errors.append("physical.land-cover must be current")
    if row.get("load_policy") != "on_demand": errors.append("physical.land-cover must remain on_demand")
    if row.get("kind") != "module": errors.append("physical.land-cover must be module-backed")
    if row.get("module") != "./3d-physical-land-cover.js": errors.append("physical.land-cover must point to ./3d-physical-land-cover.js")
    if row.get("controller") != "__potatoAtlasLandCover": errors.append("physical.land-cover controller is not pinned")
    source = row.get("source") or {}
    if source.get("provider") != "ESA WorldCover": errors.append("land cover provider must be ESA WorldCover")
    if "2021" not in str(source.get("dataset", "")) or "v200" not in str(source.get("version", "")):
        errors.append("land cover must pin WorldCover 2021 v200")
    if "WMS" not in str(source.get("delivery", "")):
        errors.append("land cover must document WMS delivery")

    if not LAND.exists():
        errors.append("missing world-map/3d-physical-land-cover.js")
    else:
        text = LAND.read_text(encoding="utf-8", errors="replace")
        for token in (
            "https://services.terrascope.be/wms/v2",
            "WORLDCOVER_2021_MAP",
            "{bbox-epsg-3857}",
            "type: 'raster'",
            "tileSize: 256",
            "raster-opacity",
            "countries-fill",
            "atlasLandCoverLegend",
            "Tree cover",
            "Grassland",
            "Bare / sparse vegetation",
            "Permanent water bodies",
            "__potatoAtlasLandCover",
            "enable",
            "disable",
        ):
            if token not in text:
                errors.append(f"land-cover module missing {token}")
        if "new MutationObserver(" in text or "setInterval(" in text:
            errors.append("land-cover module must not poll or observe the DOM")
        if "queryRenderedFeatures" in text or "pixel" in text.lower() and "analysis" in text.lower():
            errors.append("WMS RGB land cover must not pretend to provide pixel analysis")
        node = shutil.which("node")
        if node:
            result = subprocess.run([node, "--check", str(LAND)], capture_output=True, text=True)
            if result.returncode:
                errors.append("land-cover JavaScript syntax failed: " + (result.stderr.strip() or result.stdout.strip()))

    if RUNTIME.exists() and "__potatoAtlasLandCover" not in RUNTIME.read_text(encoding="utf-8", errors="replace"):
        errors.append("physical runtime missing land-cover controller compatibility marker")

    if errors:
        print("WORLD MAP LAND COVER VALIDATION FAILED")
        for error in errors: print("-", error)
        return 1

    print("WORLD MAP LAND COVER VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
