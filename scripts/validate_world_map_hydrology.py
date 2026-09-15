#!/usr/bin/env python3
"""Validate regional, viewport-bounded HydroBASINS/HydroRIVERS integration."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "world-map-physical-layers.json"
HYDRO = ROOT / "world-map" / "3d-physical-hydrology.js"
RUNTIME = ROOT / "world-map" / "3d-physical-layers.js"
DEDUPE = ROOT / "scripts" / "validate_world_map_hydrology_dedupe.py"


def main() -> int:
    errors: list[str] = []
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid/missing physical manifest: {exc}")
        manifest = {}

    rows = {r.get("id"): r for r in manifest.get("entries", []) if isinstance(r, dict)}
    row = rows.get("physical.water.hydrology") or {}
    if row.get("availability") != "current": errors.append("physical.water.hydrology must be current")
    if row.get("load_policy") != "on_demand": errors.append("hydrology must remain on_demand")
    if row.get("kind") != "module": errors.append("hydrology must be module-backed")
    if row.get("module") != "./3d-physical-hydrology.js": errors.append("hydrology module path is not pinned")
    if row.get("controller") != "__potatoAtlasHydrology": errors.append("hydrology controller is not pinned")
    source = row.get("source") or {}
    if "HydroSHEDS" not in str(source.get("provider", "")): errors.append("hydrology provider must name HydroSHEDS")
    if "HydroBASINS" not in str(source.get("dataset", "")) or "HydroRIVERS" not in str(source.get("dataset", "")):
        errors.append("hydrology dataset must document HydroBASINS and HydroRIVERS")
    note = str(row.get("status_note") or "").lower()
    for token in ("regional", "sacred", "viewport"):
        if token not in note: errors.append(f"hydrology status note missing {token}")

    if not HYDRO.exists():
        errors.append("missing world-map/3d-physical-hydrology.js")
    else:
        text = HYDRO.read_text(encoding="utf-8", errors="replace")
        for token in (
            "MIN_ZOOM = 4",
            "Hydrobasins/FeatureServer/2/query",
            "Optimized_Hyrdo/FeatureServer/0/query",
            "geometryType=esriGeometryEnvelope",
            "catch_skm",
            "AbortController",
            "moveend",
            "zoomend",
            "setData",
            "countries-fill",
            "__potatoAtlasHydrology",
            "enable",
            "disable",
            "hydrologyRequestKey",
            "shouldSkipHydrologyRequest",
            "hydrologyDeduplicatedRefreshes",
        ):
            if token not in text: errors.append(f"hydrology module missing {token}")
        if "new MutationObserver(" in text or "setInterval(" in text:
            errors.append("hydrology module must not poll or observe the DOM")
        if "map.getZoom() < MIN_ZOOM" not in text and "zoom < MIN_ZOOM" not in text:
            errors.append("hydrology requests must be blocked below regional zoom")
        node = shutil.which("node")
        if node:
            result = subprocess.run([node, "--check", str(HYDRO)], capture_output=True, text=True)
            if result.returncode:
                errors.append("hydrology JavaScript syntax failed: " + (result.stderr.strip() or result.stdout.strip()))

    if DEDUPE.exists():
        result = subprocess.run([sys.executable, str(DEDUPE)], capture_output=True, text=True)
        if result.returncode:
            errors.append("hydrology request-dedupe contract failed: " + (result.stdout.strip() or result.stderr.strip()))
    else:
        errors.append("missing hydrology request-dedupe validator")

    if RUNTIME.exists() and "__potatoAtlasHydrology" not in RUNTIME.read_text(encoding="utf-8", errors="replace"):
        errors.append("physical runtime missing hydrology controller marker")

    if errors:
        print("WORLD MAP HYDROLOGY VALIDATION FAILED")
        for error in errors: print("-", error)
        return 1
    print("WORLD MAP HYDROLOGY VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
