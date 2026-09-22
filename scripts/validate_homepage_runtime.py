#!/usr/bin/env python3
"""Guard the homepage against all-or-nothing runtime enrichment failures."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "index.html"

REQUIRED_DATASETS = (
    "data/house/project-synthesis.json",
    "data/house/subrooms.json",
    "data/house/entity-dossiers-wave-001.json",
    "data/house/foundations-wave-001.json",
    "data/house/foundations-wave-002.json",
    "data/house/foundations-wave-003.json",
    "data/house/lower-plane-population-atlas.json",
    "data/house/layer-terrain-regime-atlas.json",
    "data/house/concept-topology.json",
    "data/axis-flow-contract.json",
    "data/house/route-case-matrix-wave-001.json",
    "data/house/foundation-landscape-synthesis.json",
    "data/house/foundation-room-atlas.json",
)

def main() -> int:
    errors: list[str] = []
    if not HOME.exists():
        print("HOMEPAGE RUNTIME VALIDATION FAILED\n- missing index.html")
        return 1

    home = HOME.read_text(encoding="utf-8", errors="replace")

    required_markers = (
        "const unavailable=new Set();",
        "const loadJson=async path=>",
        "unavailable.add(path);",
        "return null;",
        "document.documentElement.dataset.homeProjection=unavailable.size?'partial':'live';",
    )
    for marker in required_markers:
        if marker not in home:
            errors.append(f"homepage runtime missing resilience marker: {marker}")

    if "home projection data unavailable" in home:
        errors.append("homepage runtime still contains the retired all-or-nothing projection failure")
    if re.search(r"\.every\(r=>r\.ok\).*home projection", home, flags=re.S):
        errors.append("homepage runtime still gates all projection data behind one response-ok check")

    for path in REQUIRED_DATASETS:
        if f"loadJson('{path}')" not in home:
            errors.append(f"homepage dataset is not isolated through loadJson: {path}")
        if f"fetch('{path}')" in home:
            errors.append(f"homepage dataset bypasses isolated loader with raw fetch: {path}")

    if 'class="home-guide"' in home or 'aria-label="Homepage section shortcuts"' in home:
        errors.append("homepage reintroduced the retired first-screen section shortcut row")

    stale_loading = (
        "Loading Foundation landscape",
        "Loading Foundation Rooms",
        "Loading map-ready origins",
        "Loading current snapshots",
        '<span class="case-kind">Loading cases</span>',
    )
    for text in stale_loading:
        if text in home:
            errors.append(f"homepage static fallback still exposes indefinite loading copy: {text}")

    stable_fallbacks = (
        "Case registry",
        "Stable fallback",
        "Open Foundation Timeline",
        "Origin anchors and current snapshots enrich this view when available.",
    )
    for text in stable_fallbacks:
        if text not in home:
            errors.append(f"homepage missing meaningful no-JS/partial-data fallback: {text}")

    guarded_updates = (
        "if(rooms)setStat('rooms'",
        "if(cases)setStat('cases'",
        "if(below)setStat('below'",
        "if(f1&&f2&&f3)",
        "if(root&&cases)",
        "if(foundationRoomSummary&&foundationRooms)",
    )
    for marker in guarded_updates:
        if marker not in home:
            errors.append(f"homepage dynamic overwrite is not source-guarded: {marker}")

    if errors:
        print("HOMEPAGE RUNTIME VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("HOMEPAGE RUNTIME VALIDATION PASSED: static fallbacks are meaningful and dynamic datasets fail independently.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
