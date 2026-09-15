#!/usr/bin/env python3
"""Validate the World Map shared render-stack architecture."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDER_STACK = ROOT / "world-map" / "3d-render-stack.js"
PANEL = ROOT / "world-map" / "3d-panel-lifecycle.js"
PHYSICAL_MODULES = {
    "terrain": ROOT / "world-map" / "3d-physical-terrain.js",
    "water": ROOT / "world-map" / "3d-physical-water.js",
    "hydrology": ROOT / "world-map" / "3d-physical-hydrology.js",
    "land-cover": ROOT / "world-map" / "3d-physical-land-cover.js",
    "deserts": ROOT / "world-map" / "3d-physical-deserts.js",
}
SPATIAL = ROOT / "world-map" / "3d-spatial-overlays.js"
INFRASTRUCTURE = ROOT / "world-map" / "3d-infrastructure.js"


def check_node(path: Path, errors: list[str]) -> None:
    node = shutil.which("node")
    if not node or not path.exists():
        return
    result = subprocess.run([node, "--check", str(path)], capture_output=True, text=True)
    if result.returncode:
        errors.append(f"JavaScript syntax failed for {path.relative_to(ROOT)}: {result.stderr.strip() or result.stdout.strip()}")


def require_tokens(path: Path, tokens: tuple[str, ...], errors: list[str], label: str) -> str:
    if not path.exists():
        errors.append(f"missing {path.relative_to(ROOT)}")
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    for token in tokens:
        if token not in text:
            errors.append(f"{label} missing {token}")
    return text


def main() -> int:
    errors: list[str] = []

    render = require_tokens(
        RENDER_STACK,
        (
            "__potatoAtlasRenderStack", "register", "unregister", "reconcile", "state", "slotOrder",
            "physical-surface", "physical-water", "physical-line", "geography-context", "context-network", "selection-emphasis",
            "moveLayer", "potato-atlas-render-stack-change", "queueMicrotask",
            "potato-atlas-module-ready", "localeCompare",
            "function styleSnapshot", "orderIndex", "renderStackStyleSnapshots",
            "const styleLifecycle = window.__potatoAtlasStyleLifecycle",
            "styleLifecycle.register('render-stack'",
            "restore:() => schedule('style-generation')",
        ),
        errors,
        "render stack",
    )
    check_node(RENDER_STACK, errors)
    for forbidden in ("MutationObserver", "setInterval", "removeLayer(", "removeSource(", "setPaintProperty(", "zIndex", "map.on('styledata'"):
        if forbidden in render:
            errors.append(f"render stack must not own map data/paint/style lifecycle or arbitrary z-index state: found {forbidden}")
    if render:
        expected_order = ("physical-surface", "physical-water", "physical-line", "geography-context", "context-network", "selection-emphasis")
        positions = [render.find(repr(slot).replace('"', "'")) for slot in expected_order]
        if any(position < 0 for position in positions) or positions != sorted(positions):
            errors.append("render stack must declare canonical slot order bottom-to-top")
        move_start = render.find("function moveRegion")
        reconcile_start = render.find("function reconcile")
        move_body = render[move_start:reconcile_start] if move_start >= 0 and reconcile_start > move_start else ""
        if "map.getStyle()" in move_body or "styleOrder()" in move_body:
            errors.append("moveRegion must use the reconcile style snapshot instead of rebuilding style order per layer")
        reconcile_body = render[reconcile_start:] if reconcile_start >= 0 else ""
        if reconcile_body.count("styleSnapshot()") != 1:
            errors.append("each render-stack reconcile must capture exactly one style snapshot")

    lifecycle = require_tokens(
        PANEL,
        ("Render Stack", "./3d-render-stack.js", "Map State", "./3d-map-state.js", "Physical World", "./3d-physical-layers.js"),
        errors,
        "panel lifecycle",
    )
    check_node(PANEL, errors)
    if lifecycle and "./3d-render-stack.js" in lifecycle and "./3d-physical-layers.js" in lifecycle:
        if lifecycle.index("./3d-render-stack.js") > lifecycle.index("./3d-physical-layers.js"):
            errors.append("Render Stack must load before Physical World")

    expected_physical_slots = {
        "terrain": ("__potatoAtlasRenderStack", "physical-surface"),
        "land-cover": ("__potatoAtlasRenderStack", "physical-surface"),
        "water": ("__potatoAtlasRenderStack", "physical-water", "physical-line"),
        "deserts": ("__potatoAtlasRenderStack", "physical-surface", "physical-line"),
        "hydrology": ("__potatoAtlasRenderStack", "physical-surface", "physical-line"),
    }
    for label, path in PHYSICAL_MODULES.items():
        require_tokens(path, expected_physical_slots[label], errors, f"Physical {label}")
        check_node(path, errors)

    spatial = require_tokens(
        SPATIAL,
        ("__potatoAtlasRenderStack", "geography-context", "register"),
        errors,
        "spatial overlays",
    )
    check_node(SPATIAL, errors)
    if spatial and "country-labels" in spatial and "__potatoAtlasRenderStack" not in spatial:
        errors.append("spatial overlays still rely only on country-labels ordering")

    require_tokens(
        INFRASTRUCTURE,
        ("__potatoAtlasRenderStack", "context-network", "atlas-infrastructure-points"),
        errors,
        "infrastructure",
    )
    check_node(INFRASTRUCTURE, errors)

    if errors:
        print("WORLD MAP RENDER STACK VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    print("WORLD MAP RENDER STACK VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
