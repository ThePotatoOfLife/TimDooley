#!/usr/bin/env python3
"""Validate coordinated World Map UI placement and Physical World runtime contracts."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAYOUT = ROOT / "world-map" / "3d-ui-layout.js"
PHYSICAL = ROOT / "world-map" / "3d-physical-layers.js"
MANIFEST = ROOT / "data" / "world-map-physical-layers.json"
PANEL_LIFECYCLE = ROOT / "world-map" / "3d-panel-lifecycle.js"
TERRAIN = ROOT / "world-map" / "3d-physical-terrain.js"
RENDER_STACK_VALIDATOR = ROOT / "scripts" / "validate_world_map_render_stack.py"
MAP_STATE_VALIDATOR = ROOT / "scripts" / "validate_world_map_map_state.py"
WATER_VALIDATOR = ROOT / "scripts" / "validate_world_map_physical_water.py"
SURFACE_FOCUS_VALIDATOR = ROOT / "scripts" / "validate_world_map_physical_surface_focus.py"
LAND_COVER_VALIDATOR = ROOT / "scripts" / "validate_world_map_land_cover.py"
DESERTS_VALIDATOR = ROOT / "scripts" / "validate_world_map_deserts.py"
HYDROLOGY_VALIDATOR = ROOT / "scripts" / "validate_world_map_hydrology.py"
PLACES_VALIDATOR = ROOT / "scripts" / "validate_world_places.py"
PLACES_PIPELINE_VALIDATOR = ROOT / "scripts" / "validate_world_places_fixture_pipeline.py"


def check_node(path: Path, errors: list[str]) -> None:
    node = shutil.which("node")
    if not node or not path.exists():
        return
    result = subprocess.run([node, "--check", str(path)], capture_output=True, text=True)
    if result.returncode:
        errors.append(f"JavaScript syntax failed for {path.relative_to(ROOT)}: {result.stderr.strip() or result.stdout.strip()}")


def main() -> int:
    errors: list[str] = []
    for path in (LAYOUT, PHYSICAL, MANIFEST, PANEL_LIFECYCLE, TERRAIN, RENDER_STACK_VALIDATOR, MAP_STATE_VALIDATOR, WATER_VALIDATOR, SURFACE_FOCUS_VALIDATOR, LAND_COVER_VALIDATOR, DESERTS_VALIDATOR, HYDROLOGY_VALIDATOR, PLACES_VALIDATOR, PLACES_PIPELINE_VALIDATOR):
        if not path.exists():
            errors.append(f"missing required World Map architecture file: {path.relative_to(ROOT)}")

    for path in (LAYOUT, PHYSICAL, PANEL_LIFECYCLE, TERRAIN):
        check_node(path, errors)

    if LAYOUT.exists():
        text = LAYOUT.read_text(encoding="utf-8", errors="replace")
        for token in (
            "__potatoAtlasUILayout", "right-inspector", "left-status", "canvas-control",
            "register", "unregister", "setVisible", "getState", "refresh", "atlasUILeftStatus",
            "atlasWorldContext", "atlasTimeState", "axisDepthNavigator", "axisCompactToggle",
            "main-inspector", "world-context", "time-state", "axis-compact",
            "atlas-axis-inspector-nav", "@media(max-width:900px)",
        ):
            if token not in text:
                errors.append(f"UI layout coordinator missing {token}")

    if PHYSICAL.exists():
        text = PHYSICAL.read_text(encoding="utf-8", errors="replace")
        for token in (
            "world-map-physical-layers.json", "load_policy", "on_demand",
            "potato-atlas-physical-change", "__potatoAtlasPhysicalLayers", "atlasPhysicalMenu",
            "data-physical-layer", "aria-pressed", "searchParams.set('physical'", "Physical world",
        ):
            if token not in text:
                errors.append(f"Physical runtime missing {token}")
        if "3d-physical-terrain.js" in text and "ensureModule" not in text:
            errors.append("Physical runtime may reference Terrain only through the on-demand module path")

    if MANIFEST.exists():
        try:
            manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"invalid physical layer manifest: {exc}")
            manifest = {}
        entries = manifest.get("entries") or []
        by_id = {row.get("id"): row for row in entries if isinstance(row, dict)}
        terrain = by_id.get("physical.terrain") or {}
        if terrain.get("availability") != "current": errors.append("physical.terrain must be current")
        if terrain.get("load_policy") != "on_demand": errors.append("physical.terrain must remain on_demand")
        if terrain.get("kind") != "module": errors.append("physical.terrain must be represented as a lazy module")
        for overlay_id in ("physical.water.base", "physical.land-cover", "physical.aridity", "physical.water.hydrology"):
            row = by_id.get(overlay_id) or {}
            if row.get("availability") not in {"planned", "current"}:
                errors.append(f"{overlay_id} must be planned or current")
        land_note = str((by_id.get("physical.land-cover") or {}).get("status_note") or "").lower()
        if "not the same thing as desert" not in land_note:
            errors.append("land-cover contract must distinguish bare/sparse vegetation from desert")
        hydro_note = str((by_id.get("physical.water.hydrology") or {}).get("status_note") or "").lower()
        if "sacred" not in hydro_note:
            errors.append("hydrology contract must remain independent from sacred river overlays")

    if PANEL_LIFECYCLE.exists():
        lifecycle = PANEL_LIFECYCLE.read_text(encoding="utf-8", errors="replace")
        for token in ("UI Layout", "./3d-ui-layout.js", "Physical World", "./3d-physical-layers.js"):
            if token not in lifecycle:
                errors.append(f"panel lifecycle missing architecture loader marker: {token}")
        if "./3d-physical-terrain.js" in lifecycle:
            errors.append("Terrain must not be loaded directly during ordinary panel lifecycle startup")

    if TERRAIN.exists():
        terrain = TERRAIN.read_text(encoding="utf-8", errors="replace")
        for token in ("raster-dem", "hillshade", "setTerrain", "ensureSources", "window.__potatoAtlasTerrain"):
            if token not in terrain:
                errors.append(f"Terrain module missing behavior marker: {token}")
        if "atlasTerrainToggle" in terrain or "installControl" in terrain:
            errors.append("Terrain module must not inject a second legacy control after Physical menu migration")
        if "terrain=1" in terrain or "searchParams.set('terrain'" in terrain:
            errors.append("Terrain module must not own legacy URL state after Physical runtime migration")

    validators = (
        ("render stack", RENDER_STACK_VALIDATOR, ()),
        ("map state / physical mixer", MAP_STATE_VALIDATOR, ()),
        ("physical water", WATER_VALIDATOR, ()),
        ("physical surface focus", SURFACE_FOCUS_VALIDATOR, ()),
        ("land cover", LAND_COVER_VALIDATOR, ()),
        ("deserts", DESERTS_VALIDATOR, ()),
        ("hydrology", HYDROLOGY_VALIDATOR, ()),
        # Production Places data is a separate generated-data gate. The UI/layout
        # contract verifies that the runtime remains safe and dormant without it.
        ("places runtime", PLACES_VALIDATOR, ("--runtime-only",)),
        # The deterministic fixture pipeline proves builder -> generated data ->
        # data validator without depending on a live GeoNames download in CI.
        ("places fixture pipeline", PLACES_PIPELINE_VALIDATOR, ()),
    )
    for label, validator, args in validators:
        if validator.exists():
            result = subprocess.run([sys.executable, str(validator), *args], capture_output=True, text=True)
            if result.returncode:
                errors.append(f"{label} contract failed: " + (result.stdout.strip() or result.stderr.strip()))

    if errors:
        print("WORLD MAP UI LAYOUT VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    print("WORLD MAP UI LAYOUT VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
