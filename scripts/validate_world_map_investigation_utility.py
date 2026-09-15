#!/usr/bin/env python3
"""Validate contextual World Map investigation entry points and shell discipline."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "world-map" / "3d-country-card.js"
PATHFINDER = ROOT / "world-map" / "3d-pathfinder.js"
IMPACT = ROOT / "world-map" / "3d-impact-trace.js"
CHAIN = ROOT / "world-map" / "3d-chain-explorer.js"
SURFACE = ROOT / "world-map" / "3d-investigation-surface.js"
SURFACE_OWNERSHIP_TEST = ROOT / "scripts" / "test_world_map_investigation_surface_ownership.mjs"
WORLD_BAR = ROOT / "world-map" / "3d-world-bar.js"
BOOTSTRAP = ROOT / "world-map" / "3d-bootstrap.js"


def read(path: Path, errors: list[str]) -> str:
    if not path.is_file():
        errors.append(f"missing investigation utility file: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    errors: list[str] = []
    card = read(CARD, errors)
    path = read(PATHFINDER, errors)
    impact = read(IMPACT, errors)
    chain = read(CHAIN, errors)
    surface = read(SURFACE, errors)
    bar = read(WORLD_BAR, errors)
    bootstrap = read(BOOTSTRAP, errors)

    for token in ('data-country-action="details"','data-country-action="entity-trace"','data-country-action="path"','data-country-action="impact"'):
        if token not in card:
            errors.append(f"country card missing contextual investigation action: {token}")
    for token in ("window.__potatoAtlasPath", "data-path-target", "getRelationMode", "edgeMatchesRelationMode"):
        if token not in path:
            errors.append(f"Path module missing current investigation API marker: {token}")

    surface_tokens = (
        "window.__potatoAtlasInvestigationSurface",
        "function register",
        "function open",
        "function close",
        "function active",
    )
    for token in surface_tokens:
        if token not in surface:
            errors.append(f"investigation surface missing coordination marker: {token}")

    for label, source, identifier in (
        ("Path", path, "path"),
        ("Impact", impact, "impact"),
        ("Chain", chain, "chain"),
    ):
        if f"register?.('{identifier}'" not in source and f"register('{identifier}'" not in source:
            errors.append(f"{label} must register with investigation surface coordinator")
        if f"open?.('{identifier}'" not in source and f"open('{identifier}'" not in source:
            errors.append(f"{label} must announce its temporary surface before rendering")

    if "surface?.close?.('chain')" not in chain and "surface.close('chain')" not in chain:
        errors.append("Chain direct clear must release investigation surface ownership")
    if "coordinated:true" not in chain:
        errors.append("Chain must support coordinator-driven close without recursion")

    surface_load = "loadAfterPaint('Investigation Surface', './3d-investigation-surface.js')"
    if surface_load not in bootstrap:
        errors.append("bootstrap must load the investigation surface coordinator during the interactive core")
    else:
        first = bootstrap.find(surface_load)
        specialist_loads = (
            ("Impact", "loadSpecialist('Impact Trace', './3d-impact-trace.js')"),
            ("Chain", "loadSpecialist('Functional Chains', './3d-chain-explorer.js')"),
        )
        for label, load_marker in specialist_loads:
            pos = bootstrap.find(load_marker)
            if pos < 0:
                errors.append(f"bootstrap must retain contextual {label} loading")
            elif first > pos:
                errors.append(f"investigation surface coordinator must load before {label}")

    forbidden_controls = (
        'data-family="path"', 'data-family="infrastructure"', 'data-family="coverage"', 'data-family="investigation"',
        "['path','Path']", "['infrastructure','Infrastructure']", "['coverage','Coverage']", "['investigation','Investigation']",
    )
    for marker in forbidden_controls:
        if marker in bar:
            errors.append(f"World Bar must not gain permanent investigation control: {marker}")
    if "3d-pathfinder.js" not in bootstrap and "3d-pathfinder.js" not in card:
        errors.append("Path must be loadable contextually from bootstrap or country card")

    node = shutil.which("node")
    if node:
        for module in (SURFACE, PATHFINDER, IMPACT, CHAIN, BOOTSTRAP, SURFACE_OWNERSHIP_TEST):
            if not module.is_file():
                continue
            result = subprocess.run([node, "--check", str(module)], text=True, capture_output=True)
            if result.returncode:
                errors.append(f"JavaScript syntax failed for {module.relative_to(ROOT)}: {result.stderr.strip() or result.stdout.strip()}")
        if SURFACE_OWNERSHIP_TEST.is_file():
            result = subprocess.run([node, str(SURFACE_OWNERSHIP_TEST)], cwd=ROOT, text=True, capture_output=True)
            if result.returncode:
                errors.append("investigation surface ownership regression failed: " + (result.stderr.strip() or result.stdout.strip()))
        else:
            errors.append(f"missing investigation surface ownership regression: {SURFACE_OWNERSHIP_TEST.relative_to(ROOT)}")

    if errors:
        print("World Map investigation utility validation FAILED:")
        for error in errors: print(f" - {error}")
        return 1
    print("World Map investigation utility validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
