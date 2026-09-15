#!/usr/bin/env python3
"""Validate coordinated World Map UI placement and Physical World runtime contracts."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAYOUT = ROOT / "world-map" / "3d-ui-layout.js"
PHYSICAL = ROOT / "world-map" / "3d-physical-layers.js"
MANIFEST = ROOT / "data" / "world-map-physical-layers.json"
AXIS = ROOT / "world-map" / "3d-axis-depth.js"
WORLD_BAR = ROOT / "world-map" / "3d-world-bar.js"
UI = ROOT / "world-map" / "3d-ui.js"


def main() -> int:
    errors: list[str] = []
    for path in (LAYOUT, PHYSICAL, MANIFEST, AXIS, WORLD_BAR, UI):
        if not path.exists():
            errors.append(f"missing required World Map architecture file: {path.relative_to(ROOT)}")

    if LAYOUT.exists():
        text = LAYOUT.read_text(encoding="utf-8", errors="replace")
        for token in (
            "__potatoAtlasUILayout", "right-inspector", "left-status", "canvas-control",
            "register", "unregister", "setVisible", "getState", "refresh", "atlasUILeftStatus",
        ):
            if token not in text:
                errors.append(f"UI layout coordinator missing {token}")

    if PHYSICAL.exists():
        text = PHYSICAL.read_text(encoding="utf-8", errors="replace")
        for token in (
            "world-map-physical-layers.json", "load_policy", "on_demand",
            "potato-atlas-physical-change", "__potatoAtlasPhysicalLayers",
        ):
            if token not in text:
                errors.append(f"Physical runtime missing {token}")

    if MANIFEST.exists():
        try:
            manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"invalid physical layer manifest: {exc}")
            manifest = {}
        entries = manifest.get("entries") or []
        by_id = {row.get("id"): row for row in entries if isinstance(row, dict)}
        terrain = by_id.get("physical.terrain") or {}
        if terrain.get("availability") != "current":
            errors.append("physical.terrain must be current")
        if terrain.get("load_policy") != "on_demand":
            errors.append("physical.terrain must remain on_demand")
        for overlay_id in ("physical.water.base", "physical.water.hydrology", "physical.land-cover", "physical.aridity"):
            if overlay_id not in by_id:
                errors.append(f"physical manifest missing provider-ready slot {overlay_id}")

    if AXIS.exists():
        axis = AXIS.read_text(encoding="utf-8", errors="replace")
        if "right:12px;top:62px;width:170px;height:476px" in axis:
            errors.append("Axis navigator still owns an independent overlapping right-side rectangle")
        for token in ("right-inspector", "__potatoAtlasUILayout"):
            if token not in axis:
                errors.append(f"Axis navigator is not coordinated through {token}")

    if WORLD_BAR.exists():
        world_bar = WORLD_BAR.read_text(encoding="utf-8", errors="replace")
        for token in ("Physical", "data-physical-layer", "__potatoAtlasPhysicalLayers", "left-status"):
            if token not in world_bar:
                errors.append(f"World Bar missing coordinated/Physical marker: {token}")

    if UI.exists():
        ui = UI.read_text(encoding="utf-8", errors="replace")
        for token in ("__potatoAtlasUILayout", "left-status", "atlasTimeState"):
            if token not in ui:
                errors.append(f"Progressive UI missing layout marker: {token}")

    if errors:
        print("WORLD MAP UI LAYOUT VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    print("WORLD MAP UI LAYOUT VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
