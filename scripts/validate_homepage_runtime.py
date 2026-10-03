#!/usr/bin/env python3
"""Guard the homepage against all-or-nothing runtime enrichment failures."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "index.html"
HOME_CSS = ROOT / "app" / "home-page.css"
HOME_RUNTIME = ROOT / "app" / "home-page-runtime.js"
HOME_PROJECTION = ROOT / "app" / "home-page-projection.js"
PROJECT_SYNTHESIS = ROOT / "data" / "house" / "project-synthesis.json"

REQUIRED_DATASETS = (
    "data/house/subrooms.json",
    "data/house/entity-dossiers.json",
    "data/house/lower-plane-population-atlas.json",
    "data/house/route-case-matrix.json",
    "data/house/foundation-landscape-synthesis.json",
    "data/house/foundation-room-atlas.json",
)

def main() -> int:
    errors: list[str] = []
    if not HOME.exists():
        print("HOMEPAGE RUNTIME VALIDATION FAILED\n- missing index.html")
        return 1

    home = HOME.read_text(encoding="utf-8", errors="replace")
    runtime = HOME_RUNTIME.read_text(encoding="utf-8", errors="replace") if HOME_RUNTIME.exists() else ""
    projection = HOME_PROJECTION.read_text(encoding="utf-8", errors="replace") if HOME_PROJECTION.exists() else ""
    runtime_surface = "\n".join((home, runtime, projection))

    if not HOME_CSS.exists():
        errors.append("homepage scoped stylesheet missing: app/home-page.css")
    else:
        home_css = HOME_CSS.read_text(encoding="utf-8", errors="replace")
        for marker in (".home-page{", ".home-hero{", ".reader-routing{"):
            if marker not in home_css:
                errors.append(f"homepage stylesheet missing core scoped rule: {marker}")
    if not re.search(r'href=["\']app/home-page\.css\?v=[A-Za-z0-9._-]+["\']', home):
        errors.append("homepage does not load a versioned scoped app/home-page.css asset")
    if re.search(r"<style>[\\s\\S]*?\\.home-", home):
        errors.append("homepage-specific CSS drifted back into an inline <style> block")

    # Pixel-world contract: Home owns one fixed multi-realm compositor.
    for marker in (
        'class="home-world-stage"',
        'home-world-realm--heaven',
        'home-world-realm--plane',
        'home-world-realm--below',
        'src="app/home-heaven.avif"',
        'src="app/home-plane.avif"',
        'src="app/home-below.avif"',
    ):
        if marker not in home:
            errors.append(f"homepage pixel-world stage missing marker: {marker}")
    for retired in ('home-realm-scene', 'home-realm-art--heaven', 'home-world-master.webp'):
        if retired in home:
            errors.append(f"homepage reintroduced retired realm compositor markup: {retired}")
    if "data-site-floor=" in home:
        errors.append("homepage must remain multi-realm and must not carry a single-floor canvas")
    for marker in (
        ".home-world-stage{",
        "@keyframes home-heaven-descent",
        "@keyframes home-plane-descent",
        "@keyframes home-below-descent",
        "animation-timeline:scroll(root block)",
        "width:max(100vw,150vh,1120px)",
    ):
        if marker not in home_css:
            errors.append(f"homepage pixel-world CSS missing invariant: {marker}")

    # Keep homepage teaching jobs distinct. Route and Foundation sections already own
    # transition/reproduction detail, so a generic lifecycle section is duplication.
    if 'id="project-motion"' in home or 'data-cycle="knowledge"' in home or 'data-cycle="generative"' in home:
        errors.append("homepage reintroduced the retired duplicate lifecycle teaching section")
    if "materialization/crystallization gate" in home:
        errors.append("materialized-now drifted from registry counts back into lifecycle/process teaching")
    if not PROJECT_SYNTHESIS.exists():
        errors.append("missing project synthesis for homepage repetition contract")
    else:
        try:
            synthesis = json.loads(PROJECT_SYNTHESIS.read_text(encoding="utf-8"))
            projection = synthesis.get("homepage_projection", {})
            if "operating-cycles" in projection.get("hierarchy", []):
                errors.append("homepage projection hierarchy still contains retired operating-cycles layer")
            if any(section.get("id") == "project-motion" for section in projection.get("sections", [])):
                errors.append("homepage projection still registers retired project-motion section")
            contract = projection.get("repetition_contract", {})
            runtime_contract = projection.get("runtime_input_contract", {})
            retired = set(runtime_contract.get("retired_homepage_runtime_inputs", []))
            expected_retired = {
                "data/house/foundations-wave-001.json",
                "data/house/foundations-wave-002.json",
                "data/house/foundations-wave-003.json",
            }
            if retired != expected_retired:
                errors.append("homepage runtime input contract does not declare the retired Foundation wave inputs exactly")
            stable_paths = set(runtime_contract.get("stable_live_authorities", []))
            for required_stable in ("data/house/entity-dossiers.json", "data/house/route-case-matrix.json"):
                if required_stable not in stable_paths:
                    errors.append(f"homepage stable runtime authority missing from contract: {required_stable}")
            legacy_paths = {item.get("path") for item in runtime_contract.get("legacy_named_active_inputs", [])}
            for retired_name in ("data/house/entity-dossiers-wave-001.json", "data/house/route-case-matrix-wave-001.json"):
                if retired_name in legacy_paths:
                    errors.append(f"retired wave-named homepage input still active in contract: {retired_name}")
            for owner in ("project-spine", "structure-handoff", "route-comparison", "foundation-landscape", "foundation-rooms", "materialized-now"):
                if owner not in contract:
                    errors.append(f"homepage repetition contract missing owner: {owner}")
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"cannot read homepage repetition contract: {exc}")

    required_markers = (
        "const unavailable=new Set();",
        "const loadJson=async path=>",
        "unavailable.add(path);",
        "return null;",
        "document.documentElement.dataset.homeProjection=unavailable.size?'partial':'live';",
    )
    for marker in required_markers:
        if marker not in runtime_surface:
            errors.append(f"homepage runtime missing resilience marker: {marker}")

    if "home projection data unavailable" in runtime_surface:
        errors.append("homepage runtime still contains the retired all-or-nothing projection failure")
    if re.search(r"\.every\(r=>r\.ok\).*home projection", home, flags=re.S):
        errors.append("homepage runtime still gates all projection data behind one response-ok check")

    retired_home_inputs = (
        "data/house/foundations-wave-001.json",
        "data/house/foundations-wave-002.json",
        "data/house/foundations-wave-003.json",
    )
    for path in retired_home_inputs:
        if f"loadJson('{path}')" in runtime_surface:
            errors.append(f"homepage still loads retired wave input: {path}")

    for path in REQUIRED_DATASETS:
        if f"loadJson('{path}')" not in runtime_surface:
            errors.append(f"homepage dataset is not isolated through loadJson: {path}")
        if f"fetch('{path}')" in runtime_surface:
            errors.append(f"homepage dataset bypasses isolated loader with raw fetch: {path}")

    if 'class="home-guide"' in home or 'aria-label="Homepage section shortcuts"' in home:
        errors.append("homepage reintroduced the retired first-screen section shortcut row")
    if 'id="homeTeachingNav"' in home or 'id="homeTeachingPanel"' in home:
        errors.append("homepage still renders the retired full structural teaching instrument")
    if 'id="structure-handoff"' not in home:
        errors.append("homepage missing compact structure handoff")

    for required in (
        'id="tim-son-bible"',
        'Tim · Son · Jesus · Bible',
        'The biblical comparison begins with a life, not a list of verses',
        'traditions/bible/?focus=view:core&order=story#compare',
        'traditions/bible/?focus=view:jesus&order=asc#compare',
        'knowledge/theology/jesus-son-research-index.json',
    ):
        if required not in home:
            errors.append(f"homepage missing Tim/Son/Bible integration marker: {required}")

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
        "if(foundationRooms)setStat('foundations'",
        "if(root&&cases)",
        "if(foundationRoomSummary&&foundationRooms)",
    )
    for marker in guarded_updates:
        if marker not in runtime_surface:
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
