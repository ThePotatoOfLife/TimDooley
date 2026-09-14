#!/usr/bin/env python3
"""Validate the optional World Map physical-terrain integration."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TERRAIN = ROOT / "world-map" / "3d-physical-terrain.js"
HOOK = ROOT / "world-map" / "3d-panel-lifecycle.js"


def main() -> int:
    errors: list[str] = []
    if not TERRAIN.exists():
        errors.append("missing world-map/3d-physical-terrain.js")
    else:
        text = TERRAIN.read_text(encoding="utf-8")
        for token in ("raster-dem", "hillshade", "setTerrain", "tilejson.json", "terrain=1", "atlasTerrainToggle", "countries-fill"):
            if token not in text:
                errors.append(f"terrain module missing {token}")
    if not HOOK.exists() or "Physical Terrain" not in HOOK.read_text(encoding="utf-8"):
        errors.append("terrain module is not registered from core")
    if errors:
        print("WORLD MAP TERRAIN VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("WORLD MAP TERRAIN VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
