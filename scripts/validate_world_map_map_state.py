#!/usr/bin/env python3
"""Validate World Map whole-state reset and Physical mixer contracts."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP_STATE = ROOT / "world-map" / "3d-map-state.js"
WORLD_BAR = ROOT / "world-map" / "3d-world-bar.js"
PHYSICAL = ROOT / "world-map" / "3d-physical-layers.js"
LIFECYCLE = ROOT / "world-map" / "3d-panel-lifecycle.js"
MANIFEST = ROOT / "data" / "world-map-physical-layers.json"
WATER = ROOT / "world-map" / "3d-physical-water.js"
HYDROLOGY = ROOT / "world-map" / "3d-physical-hydrology.js"
LAND_COVER = ROOT / "world-map" / "3d-physical-land-cover.js"
DESERTS = ROOT / "world-map" / "3d-physical-deserts.js"


def check_node(path: Path, errors: list[str]) -> None:
    node = shutil.which("node")
    if not node or not path.exists():
        return
    result = subprocess.run([node, "--check", str(path)], capture_output=True, text=True)
    if result.returncode:
        errors.append(f"JavaScript syntax failed for {path.relative_to(ROOT)}: {result.stderr.strip() or result.stdout.strip()}")


def require_tokens(path: Path, tokens: tuple[str, ...], label: str, errors: list[str]) -> str:
    if not path.exists():
        errors.append(f"missing {label}: {path.relative_to(ROOT)}")
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    for token in tokens:
        if token not in text:
            errors.append(f"{label} missing contract marker: {token}")
    return text


def main() -> int:
    errors: list[str] = []
    for path in (MAP_STATE, WORLD_BAR, PHYSICAL, LIFECYCLE, MANIFEST, WATER, HYDROLOGY, LAND_COVER, DESERTS):
        check_node(path, errors)

    map_state = require_tokens(MAP_STATE, (
        "__potatoAtlasMapState",
        "__potatoAtlasCompositor",
        "__potatoAtlasPhysicalLayers",
        "__potatoAtlasSpatialOverlays",
        "__potatoAtlasSelection",
        "clearAll",
        "keepView:true",
        "setRelationMode",
        "mode:'current'",
        "potato-atlas-map-state-reset",
        "failed",
        "preserved",
    ), "Map State coordinator", errors)
    for forbidden in ("jumpTo(", "flyTo(", "fitBounds(", "easeTo(", "setProjection("):
        if forbidden in map_state:
            errors.append(f"Map State coordinator must preserve camera/projection and may not call {forbidden}")

    bar = require_tokens(WORLD_BAR, (
        "atlasWorldReset",
        "__potatoAtlasMapState",
        ".reset?.()",
    ), "World Bar reset", errors)
    if "__potatoAtlasCompositor?.reset?.()" in bar:
        errors.append("World Bar reset must delegate to Map State coordinator, not compositor directly")

    require_tokens(LIFECYCLE, (
        "Map State",
        "./3d-map-state.js",
    ), "panel lifecycle", errors)

    physical = require_tokens(PHYSICAL, (
        "statusRecords",
        "function status(",
        "function setOpacity(",
        "function getOpacity(",
        "async function reset(",
        "potato-atlas-physical-layer-status",
        "data-physical-opacity",
        "Clear physical",
        "type=\"range\"",
        "enableResult === false",
    ), "Physical runtime/mixer", errors)
    if "new MutationObserver(" in physical or "setInterval(" in physical:
        errors.append("Physical mixer must not use MutationObserver or polling")

    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    except Exception as exc:
        errors.append(f"invalid physical manifest: {exc}")
        manifest = {}
    by_id = {row.get("id"): row for row in (manifest.get("entries") or []) if isinstance(row, dict)}
    for layer_id in ("physical.water.base", "physical.water.hydrology", "physical.land-cover", "physical.aridity"):
        value = (by_id.get(layer_id) or {}).get("default_opacity")
        if not isinstance(value, (int, float)) or not 0 <= float(value) <= 1:
            errors.append(f"{layer_id} must provide default_opacity in [0,1]")

    for path, label in (
        (WATER, "Water controller"),
        (HYDROLOGY, "Hydrology controller"),
        (LAND_COVER, "Land-cover controller"),
        (DESERTS, "Deserts controller"),
    ):
        text = require_tokens(path, ("setOpacity", "getOpacity", "Math.max(0", "Math.min(1"), label, errors)
        if "fetch(" in text:
            setter = text[text.find("function setOpacity"):text.find("function setOpacity") + 1200] if "function setOpacity" in text else ""
            if "fetch(" in setter:
                errors.append(f"{label} opacity setter must not refetch provider data")

    require_tokens(HYDROLOGY, (
        "physical.water.hydrology",
        "zoom-needed",
        "loading",
        "partial",
        "error",
        "potato-atlas-physical-layer-status",
    ), "Hydrology status reporting", errors)

    if errors:
        print("WORLD MAP MAP STATE / PHYSICAL MIXER VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    print("WORLD MAP MAP STATE / PHYSICAL MIXER VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
