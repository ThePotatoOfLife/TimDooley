#!/usr/bin/env python3
"""Validate the modular shortest-path layer of the 3D World Relational Atlas."""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "world-map" / "3d.html"
APP = ROOT / "world-map" / "3d-pathfinder.js"
WORLD = ROOT / "data" / "world-relational-map.json"


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    for path in (HTML, APP, WORLD):
        if not path.exists():
            errors.append(f"missing required path-finder file: {path.relative_to(ROOT)}")
    if errors:
        for item in errors:
            print("ERROR:", item)
        return 1

    html = HTML.read_text(encoding="utf-8", errors="replace")
    js = APP.read_text(encoding="utf-8", errors="replace")
    world = json.loads(WORLD.read_text(encoding="utf-8"))

    # Path is an investigation tool owned by the module and mounted inside the
    # progressive Trace menu. The persistent map toolbar should stay sparse.
    html_markers = (
        'src="./3d-pathfinder.js"',
        'id="traceMenu"',
        'class="menu-pop"',
        'class="mapwrap"',
        'id="relationType"',
    )
    js_markers = (
        "$('#traceMenu .menu-pop')",
        "Shortest represented path",
        "function shortestPath",
        "const queue = [start]",
        "const seen = new Set([start])",
        "parent.set(step.next",
        "currentType()",
        "world-relational-map.json",
        "world-country-facts.json",
        "id = 'pathTarget'",
        "id = 'pathFind'",
        "id = 'pathResult'",
        "searchParams.set('path'",
        "window.closeAtlasPath",
        "onclick=\"goCountry(",
        "Shortest known relationship path",
        "not necessarily the shortest or strongest relationship in the real world",
        "not “no real-world relationship exists.”",
    )
    for marker in html_markers:
        if marker not in html:
            errors.append(f"3d.html missing path-finder architecture marker: {marker}")
    for marker in js_markers:
        if marker not in js:
            errors.append(f"3d-pathfinder.js missing behavior/boundary marker: {marker}")

    # Guard against the pre-progressive implementation, which attempted to use
    # a nested View-menu button as insertBefore() reference on the top toolbar.
    if "toolbar.insertBefore" in js or "const anchor = $('#tilt')" in js:
        errors.append("Path controls regressed to brittle persistent-toolbar insertion")

    if not world.get("curated_edges"):
        errors.append("path finder has no curated world edges to traverse")

    if "new maplibregl.Map" in js or "addSource(" in js or "addLayer(" in js:
        errors.append("path finder should not create a second map renderer")

    node = shutil.which("node")
    if node:
        with tempfile.NamedTemporaryFile("w", suffix=".mjs", encoding="utf-8", delete=False) as handle:
            handle.write(js)
            tmp = Path(handle.name)
        try:
            result = subprocess.run([node, "--check", str(tmp)], text=True, capture_output=True)
            if result.returncode:
                errors.append("path-finder JavaScript syntax failed: " + (result.stderr.strip() or result.stdout.strip()))
        finally:
            tmp.unlink(missing_ok=True)
    else:
        warnings.append("node unavailable; skipped path-finder JavaScript syntax check")

    print(f"Curated edges available: {len(world.get('curated_edges', []))}")
    print("Path contract: progressive Trace-menu UI · BFS shortest path · active typed filter · URL persistence · explicit evidence boundary")
    print(f"Errors: {len(errors)} · Warnings: {len(warnings)}")
    for warning in warnings:
        print("WARNING:", warning)
    if errors:
        print("WORLD MAP PATH FINDER VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("WORLD MAP PATH FINDER VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
