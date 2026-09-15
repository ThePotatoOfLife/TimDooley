#!/usr/bin/env python3
"""Validate the lazy Natural Earth physical-water context for the World Map."""
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
    if water.get("availability") != "current":
        errors.append("physical.water.base must be current")
    if water.get("load_policy") != "on_demand":
        errors.append("physical.water.base must remain on_demand")
    if water.get("kind") != "module":
        errors.append("physical.water.base must be module-backed")
    if water.get("module") != "./3d-physical-water.js":
        errors.append("physical.water.base must point to ./3d-physical-water.js")
    source = water.get("source") or {}
    if source.get("provider") != "Natural Earth":
        errors.append("physical.water.base must name Natural Earth as provider")
    if "1:110m" not in str(source.get("dataset", "")):
        errors.append("physical.water.base must document the 1:110m overview scale")
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
            "countries-line",
            "visibility",
            "__potatoAtlasPhysicalWater",
            "enable",
            "disable",
        ):
            if token not in text:
                errors.append(f"physical water module missing {token}")
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
        for error in errors:
            print("-", error)
        return 1

    print("WORLD MAP PHYSICAL WATER VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
