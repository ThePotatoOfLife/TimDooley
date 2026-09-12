#!/usr/bin/env python3
"""Validate contextual World Map investigation entry points and shell discipline."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "world-map" / "3d-country-card.js"
PATHFINDER = ROOT / "world-map" / "3d-pathfinder.js"
IMPACT = ROOT / "world-map" / "3d-impact-trace.js"
SURFACE = ROOT / "world-map" / "3d-investigation-surface.js"
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
    if "register?.('path'" not in path and "register('path'" not in path:
        errors.append("Path must register with investigation surface coordinator")
    if "open?.('path'" not in path and "open('path'" not in path:
        errors.append("Path must announce its temporary surface before rendering")
    if "register?.('impact'" not in impact and "register('impact'" not in impact:
        errors.append("Impact must register with investigation surface coordinator")
    if "open?.('impact'" not in impact and "open('impact'" not in impact:
        errors.append("Impact must announce its temporary surface before rendering")
    surface_import = "3d-investigation-surface.js"
    if surface_import not in bootstrap:
        errors.append("bootstrap must load the investigation surface coordinator")
    else:
        first = bootstrap.find(surface_import)
        impact_pos = bootstrap.find("3d-impact-trace.js")
        if impact_pos >= 0 and first > impact_pos:
            errors.append("investigation surface coordinator must load before Impact")

    forbidden_controls = (
        'data-family="path"', 'data-family="infrastructure"', 'data-family="coverage"', 'data-family="investigation"',
        "['path','Path']", "['infrastructure','Infrastructure']", "['coverage','Coverage']", "['investigation','Investigation']",
    )
    for marker in forbidden_controls:
        if marker in bar:
            errors.append(f"World Bar must not gain permanent investigation control: {marker}")
    if "3d-pathfinder.js" not in bootstrap and "3d-pathfinder.js" not in card:
        errors.append("Path must be loadable contextually from bootstrap or country card")

    if errors:
        print("World Map investigation utility validation FAILED:")
        for error in errors: print(f" - {error}")
        return 1
    print("World Map investigation utility validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
