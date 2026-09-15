#!/usr/bin/env python3
"""Validate optional World Map physical-terrain integration after Physical menu migration."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TERRAIN = ROOT / "world-map" / "3d-physical-terrain.js"
PHYSICAL = ROOT / "world-map" / "3d-physical-layers.js"
HOOK = ROOT / "world-map" / "3d-panel-lifecycle.js"
MANIFEST = ROOT / "data" / "world-map-physical-layers.json"


def main() -> int:
    errors: list[str] = []
    if not TERRAIN.exists():
        errors.append("missing world-map/3d-physical-terrain.js")
    else:
        text = TERRAIN.read_text(encoding="utf-8")
        for token in ("raster-dem", "hillshade", "setTerrain", "tilejson.json", "ensureSources", "countries-fill", "__potatoAtlasTerrain"):
            if token not in text:
                errors.append(f"terrain module missing {token}")
        if "atlasTerrainToggle" in text or "installControl" in text:
            errors.append("terrain module still injects a legacy View-menu control")
        if "terrain=1" in text:
            errors.append("terrain module still owns legacy terrain=1 URL state")
    if not PHYSICAL.exists():
        errors.append("missing world-map/3d-physical-layers.js")
    else:
        text = PHYSICAL.read_text(encoding="utf-8")
        for token in ("physical.terrain", "on_demand", "ensureModule", "__potatoAtlasTerrain", "atlasPhysicalMenu"):
            if token not in text:
                errors.append(f"Physical runtime missing Terrain integration marker {token}")
    if not MANIFEST.exists() or '"physical.terrain"' not in MANIFEST.read_text(encoding="utf-8"):
        errors.append("physical manifest does not register Terrain")
    if not HOOK.exists():
        errors.append("missing world-map/3d-panel-lifecycle.js")
    else:
        hook = HOOK.read_text(encoding="utf-8")
        if "Physical World" not in hook or "./3d-physical-layers.js" not in hook:
            errors.append("Physical World runtime is not registered from core")
        if "./3d-physical-terrain.js" in hook:
            errors.append("Terrain is still loaded directly at startup rather than on demand")
    if errors:
        print("WORLD MAP TERRAIN VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("WORLD MAP TERRAIN VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
