#!/usr/bin/env python3
"""Validate the canonical World Map shortest-path investigation contract."""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "world-map" / "index.html"
APP = ROOT / "world-map" / "3d-pathfinder.js"
CARD = ROOT / "world-map" / "3d-country-card.js"
WORLD_BAR = ROOT / "world-map" / "3d-world-bar.js"
WORLD = ROOT / "data" / "world-relational-map.json"


def classify(edge: dict) -> str:
    types = edge.get("types") or []
    if any(t in {"trade","economic","fiscal","funding","investment","ownership"} for t in types): return "money"
    if any(t in {"energy","infrastructure"} for t in types): return "systems"
    if any(t in {"security","alliance","constitutional"} for t in types): return "institutions"
    if "project" in str(edge.get("layer") or ""): return "project"
    return "other"


def shortest(edges: list[dict], start: str, target: str, mode: str) -> list[str] | None:
    adjacency: dict[str, list[str]] = {}
    for edge in edges:
        if mode != "all" and classify(edge) != mode: continue
        adjacency.setdefault(edge["a"], []).append(edge["b"])
        adjacency.setdefault(edge["b"], []).append(edge["a"])
    for rows in adjacency.values(): rows.sort()
    queue = [start]; parent = {start: None}
    while queue:
        node = queue.pop(0)
        if node == target: break
        for nxt in adjacency.get(node, []):
            if nxt in parent: continue
            parent[nxt] = node; queue.append(nxt)
    if target not in parent: return None
    path = []; cursor = target
    while cursor is not None: path.append(cursor); cursor = parent[cursor]
    return list(reversed(path))


def main() -> int:
    errors: list[str] = []
    for path in (HTML, APP, CARD, WORLD_BAR, WORLD):
        if not path.exists(): errors.append(f"missing required path-finder file: {path.relative_to(ROOT)}")
    if errors:
        for item in errors: print("ERROR:", item)
        return 1

    js = APP.read_text(encoding="utf-8", errors="replace")
    card = CARD.read_text(encoding="utf-8", errors="replace")
    world_bar = WORLD_BAR.read_text(encoding="utf-8", errors="replace")
    world = json.loads(WORLD.read_text(encoding="utf-8"))

    required_js = (
        "window.__potatoAtlasSelection",
        "getRelationMode",
        "edgeMatchesRelationMode",
        "data-path-target",
        "function shortestPath",
        "searchParams.set('path'",
        "Shortest represented path",
        "not necessarily the shortest or strongest relationship in the real world",
    )
    for marker in required_js:
        if marker not in js: errors.append(f"pathfinder missing modern investigation marker: {marker}")
    for forbidden in ("$('#traceMenu .menu-pop')", "$('#relationType')", "REST Countries"):
        if forbidden in js: errors.append(f"pathfinder still depends on legacy UI/data path: {forbidden}")
    if 'data-country-action="path"' not in card:
        errors.append("country card must expose contextual Path to… action")
    if "Path to" in world_bar or "data-path" in world_bar:
        errors.append("Path must not become a permanent World Bar control")

    fixture = [
        {"a":"AAA","b":"BBB","types":["trade"],"layer":"empirical"},
        {"a":"BBB","b":"CCC","types":["energy"],"layer":"empirical"},
        {"a":"AAA","b":"DDD","types":["alliance"],"layer":"empirical"},
        {"a":"DDD","b":"CCC","types":["alliance"],"layer":"empirical"},
    ]
    if shortest(fixture,"AAA","CCC","all") not in (["AAA","BBB","CCC"],["AAA","DDD","CCC"]):
        errors.append("fixture: all-mode shortest path incorrect")
    if shortest(fixture,"AAA","CCC","money") is not None:
        errors.append("fixture: money mode should not connect AAA to CCC")
    if shortest(fixture,"AAA","CCC","systems") is not None:
        errors.append("fixture: systems mode should not connect AAA to CCC")
    if shortest(fixture,"AAA","CCC","institutions") != ["AAA","DDD","CCC"]:
        errors.append("fixture: institutions mode should route AAA→DDD→CCC")

    if not world.get("curated_edges"): errors.append("path finder has no curated world edges to traverse")
    if "new maplibregl.Map" in js or "addSource(" in js or "addLayer(" in js:
        errors.append("path finder should not create a second map renderer")

    node = shutil.which("node")
    if node:
        with tempfile.NamedTemporaryFile("w", suffix=".mjs", encoding="utf-8", delete=False) as handle:
            handle.write(js); tmp = Path(handle.name)
        try:
            result = subprocess.run([node, "--check", str(tmp)], text=True, capture_output=True)
            if result.returncode: errors.append("path-finder JavaScript syntax failed: " + (result.stderr.strip() or result.stdout.strip()))
        finally: tmp.unlink(missing_ok=True)

    print(f"Curated edges available: {len(world.get('curated_edges', []))}")
    print("Path contract: contextual card action · current selection API · shared relation filter · BFS · URL persistence · evidence boundary")
    if errors:
        print("WORLD MAP PATH FINDER VALIDATION FAILED")
        for error in errors: print("-", error)
        return 1
    print("WORLD MAP PATH FINDER VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
