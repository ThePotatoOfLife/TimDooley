#!/usr/bin/env python3
"""Validate typed semantic inspector history, URL hydration and migrated World Map consumers."""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / "world-map" / "3d-inspector-router.js"
URL_BRIDGE = ROOT / "world-map" / "3d-inspector-url.js"
TEST = ROOT / "scripts" / "test_world_map_inspector_router.mjs"
URL_TEST = ROOT / "scripts" / "test_world_map_inspector_url.mjs"
CONSUMER_TEST = ROOT / "scripts" / "test_world_map_inspector_consumers.mjs"
LIFECYCLE = ROOT / "world-map" / "3d-panel-lifecycle.js"
BOOTSTRAP = ROOT / "world-map" / "3d-bootstrap.js"
PLACES = ROOT / "world-map" / "3d-places.js"
SUBDIVISIONS = ROOT / "world-map" / "3d-subdivisions.js"
ADL = ROOT / "world-map" / "3d-adl-heat.js"
MUD = ROOT / "world-map" / "3d-mud-below-us.js"
SPATIAL_UI = ROOT / "world-map" / "3d-spatial-overlay-ui.js"
AXIS = ROOT / "world-map" / "3d-axis.js"
AXIS_DEPTH = ROOT / "world-map" / "3d-axis-depth.js"


def main() -> int:
    errors: list[str] = []
    for path in (ROUTER, URL_BRIDGE, TEST, URL_TEST, CONSUMER_TEST, LIFECYCLE, BOOTSTRAP, PLACES, SUBDIVISIONS, ADL, MUD, SPATIAL_UI, AXIS, AXIS_DEPTH):
        if not path.exists():
            errors.append(f"missing inspector-router file: {path.relative_to(ROOT)}")
    if errors:
        print("WORLD MAP INSPECTOR ROUTER VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    router = ROUTER.read_text(encoding="utf-8", errors="replace")
    url_bridge = URL_BRIDGE.read_text(encoding="utf-8", errors="replace")
    lifecycle = LIFECYCLE.read_text(encoding="utf-8", errors="replace")
    bootstrap = BOOTSTRAP.read_text(encoding="utf-8", errors="replace")
    places = PLACES.read_text(encoding="utf-8", errors="replace")
    subdivisions = SUBDIVISIONS.read_text(encoding="utf-8", errors="replace")
    adl = ADL.read_text(encoding="utf-8", errors="replace")
    mud = MUD.read_text(encoding="utf-8", errors="replace")
    spatial_ui = SPATIAL_UI.read_text(encoding="utf-8", errors="replace")
    axis = AXIS.read_text(encoding="utf-8", errors="replace")
    axis_depth = AXIS_DEPTH.read_text(encoding="utf-8", errors="replace")
    for token in ("function createInspectorRouter", "function setBaseline", "function open", "function back", "function current", "function state", "potato-atlas-inspector-change", "window.__potatoAtlasInspector"):
        if token not in router:
            errors.append(f"inspector router missing interface marker: {token}")
    for token in ("function encodeInspectorPath", "function decodeInspectorPath", "function deriveInspectorPathFromUrl", "function createInspectorUrlBridge", "potato-atlas-inspector-change", "searchParams.set('inspect'", "window.__potatoAtlasInspectorUrl"):
        if token not in url_bridge:
            errors.append(f"inspector URL bridge missing interface marker: {token}")
    if "__potatoAtlasLoadModule?.('Inspector Router', './3d-inspector-router.js')" not in lifecycle:
        errors.append("panel lifecycle must preload the shared Inspector Router before Places/subdivisions")
    if "__potatoAtlasLoadModule?.('Inspector URL', './3d-inspector-url.js')" not in lifecycle:
        errors.append("panel lifecycle must preload typed Inspector URL hydration before Places/subdivisions")
    if "loadAfterPaint('Inspector URL', './3d-inspector-url.js')" not in bootstrap:
        errors.append("bootstrap must hydrate typed inspector URL state before Country selection")
    if bootstrap.find("loadAfterPaint('Inspector URL', './3d-inspector-url.js')") > bootstrap.find("loadAfterPaint('Country selection', './3d-country-selection.js')"):
        errors.append("typed Inspector URL hydration must boot before Country selection reads URL state")

    for label, source, node_type in (("Places", places, "place"), ("Subdivisions", subdivisions, "subdivision")):
        for token in ("function inspectorRouter()", "inspector.setBaseline(", "inspector.open(", "inspector.back()", f"type:'{node_type}'"):
            if token not in source:
                errors.append(f"{label} inspector migration missing marker: {token}")
        if "panelSnapshot" in source:
            errors.append(f"{label} must not retain raw panelSnapshot state after inspector migration")

    for token in (
        "const inspector = window.__potatoAtlasInspector",
        "type:'evidence'",
        "type:'evidence-record'",
        "owner:'adl-heat'",
        "parent:{ type:'subdivision'",
    ):
        if token not in adl:
            errors.append(f"ADL typed inspector migration missing marker: {token}")
    if "'evidence'" not in url_bridge or "'evidence-record'" not in url_bridge:
        errors.append("Inspector URL hierarchy must include typed evidence nodes")

    for label, source, node_type, owner in (
        ("Mud/Below", mud, "project-case", "mud-below-us"),
        ("Spatial Overlay UI", spatial_ui, "spatial-overlay", "spatial-overlay-ui"),
    ):
        for token in ("const inspector = window.__potatoAtlasInspector", "inspector.open(", f"type:'{node_type}'", f"owner:'{owner}'"):
            if token not in source:
                errors.append(f"{label} typed inspector migration missing marker: {token}")

    for label, source, node_type, owner in (
        ("Axis", axis, "axis", "axis"),
        ("Axis Depth", axis_depth, "axis-depth", "axis-depth"),
    ):
        for token in ("const inspector = window.__potatoAtlasInspector", "inspector.open(", f"type:'{node_type}'", f"owner:'{owner}'"):
            if token not in source:
                errors.append(f"{label} typed inspector migration missing marker: {token}")
    if "['country','subdivision','place','evidence','evidence-record','project-case','spatial-overlay','axis','axis-depth']" not in url_bridge:
        errors.append("Inspector URL hierarchy must include project/spatial/Axis node types")

    node = shutil.which("node")
    if not node:
        errors.append("node executable unavailable; cannot run inspector-router regressions")
    else:
        for path in (ROUTER, URL_BRIDGE, PLACES, SUBDIVISIONS, ADL, MUD, SPATIAL_UI, AXIS, AXIS_DEPTH):
            result = subprocess.run([node, "--check", str(path)], cwd=ROOT, text=True, capture_output=True, check=False)
            if result.returncode:
                errors.append(f"JavaScript syntax failed for {path.relative_to(ROOT)}: " + (result.stderr.strip() or result.stdout.strip()))
        for test_path, label in ((TEST, "inspector-router"), (URL_TEST, "inspector-url"), (CONSUMER_TEST, "inspector-consumer")):
            result = subprocess.run([node, str(test_path)], cwd=ROOT, text=True, capture_output=True, check=False)
            if result.returncode:
                errors.append(f"{label} regression failed: " + (result.stderr.strip() or result.stdout.strip()))

    print("World Map inspector router:")
    print("- typed semantic history")
    print("- deterministic parent restoration")
    print("- serializable state snapshots")
    print("- typed inspect= URL projection with legacy country/subdivision/place hydration")
    print("- Places, subdivisions, ADL evidence, Mud/Below, Spatial Overlays and Axis surfaces use typed semantic inspector nodes")
    print(f"Errors: {len(errors)}")
    if errors:
        print("WORLD MAP INSPECTOR ROUTER VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("WORLD MAP INSPECTOR ROUTER VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
