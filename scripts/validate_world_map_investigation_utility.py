#!/usr/bin/env python3
"""Validate contextual World Map investigation entry points and shell discipline."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "world-map" / "3d-country-card.js"
PATHFINDER = ROOT / "world-map" / "3d-pathfinder.js"
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
    bar = read(WORLD_BAR, errors)
    bootstrap = read(BOOTSTRAP, errors)

    for token in ('data-country-action="details"','data-country-action="entity-trace"','data-country-action="path"','data-country-action="impact"'):
        if token not in card:
            errors.append(f"country card missing contextual investigation action: {token}")
    for token in ("window.__potatoAtlasPath", "data-path-target", "getRelationMode", "edgeMatchesRelationMode"):
        if token not in path:
            errors.append(f"Path module missing current investigation API marker: {token}")
    for forbidden in ("Path to", "Infrastructure", "Coverage", "Investigation"):
        if forbidden in bar:
            errors.append(f"World Bar must not gain permanent {forbidden} control")
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
