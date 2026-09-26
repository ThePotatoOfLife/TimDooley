#!/usr/bin/env python3
"""Guard the homepage against all-or-nothing runtime enrichment failures."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "index.html"
HOME_CSS = ROOT / "app" / "home-page.css"
PROJECT_SYNTHESIS = ROOT / "data" / "house" / "project-synthesis.json"

REQUIRED_DATASETS = (
    "data/house/project-synthesis.json",
    "data/house/subrooms.json",
    "data/house/entity-dossiers-wave-001.json",
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

    if not HOME_CSS.exists():
        errors.append("homepage scoped stylesheet missing: app/home-page.css")
    else:
        home_css = HOME_CSS.read_text(encoding="utf-8", errors="replace")
        for marker in (".home-page{", ".home-hero{", ".reader-routing{"):
            if marker not in home_css:
                errors.append(f"homepage stylesheet missing core scoped rule: {marker}")
    if 'href="app/home-page.css?v=20260926d"' not in home:
        errors.append("homepage does not load the scoped app/home-page.css asset")
    if re.search(r"<style>[\\s\\S]*?\\.home-", home):
        errors.append("homepage-specific CSS drifted back into an inline <style> block")

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
            legacy_paths = {item.get("path") for item in runtime_contract.get("legacy_named_active_inputs", [])}
            for required_legacy in ("data/house/entity-dossiers-wave-001.json", "data/house/route-case-matrix-wave-001.json"):
                if required_legacy not in legacy_paths:
                    errors.append(f"homepage legacy-named active input lacks explicit disposition: {required_legacy}")
            for owner in ("project-spine", "learn-the-structure", "route-comparison", "foundation-landscape", "foundation-rooms", "materialized-now"):
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
        if marker not in home:
            errors.append(f"homepage runtime missing resilience marker: {marker}")

    if "home projection data unavailable" in home:
        errors.append("homepage runtime still contains the retired all-or-nothing projection failure")
    if re.search(r"\.every\(r=>r\.ok\).*home projection", home, flags=re.S):
        errors.append("homepage runtime still gates all projection data behind one response-ok check")

    retired_home_inputs = (
        "data/house/foundations-wave-001.json",
        "data/house/foundations-wave-002.json",
        "data/house/foundations-wave-003.json",
    )
    for path in retired_home_inputs:
        if f"loadJson('{path}')" in home:
            errors.append(f"homepage still loads retired wave input: {path}")

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
        "if(foundationRooms)setStat('foundations'",
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
