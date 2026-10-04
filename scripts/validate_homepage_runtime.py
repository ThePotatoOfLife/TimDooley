#!/usr/bin/env python3
"""Guard the reader-first homepage shell and its lightweight optional runtime."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "index.html"
HOME_CSS = ROOT / "app" / "home-page.css"
HOME_RUNTIME = ROOT / "app" / "home-page-runtime.js"
PROJECT_SYNTHESIS = ROOT / "data" / "house" / "project-synthesis.json"

CURRENT_HOME_IDS = (
    "start-in-a-minute",
    "home-seedbed",
    "three-potato-paths",
    "home-relearning",
    "what-we-are-doing",
    "home-growth-rings",
    "how-did-you-get-here",
    "best-first-reads",
    "world-glimpse",
    "why-this-archive",
    "materialized-now",
    "reader-routing",
    "follow-tim",
)

RETIRED_HOME_MARKERS = (
    'id="project-substance"',
    'id="reality-cases"',
    'id="working-capabilities"',
    'id="foundation-rooms"',
    'id="tim-son-bible"',
    'id="structure-handoff"',
    'id="route-comparison"',
    'id="foundation-landscape"',
    "home-page-projection.js",
)

def main() -> int:
    errors: list[str] = []
    if not HOME.exists():
        print("HOMEPAGE RUNTIME VALIDATION FAILED\n- missing index.html")
        return 1

    home = HOME.read_text(encoding="utf-8", errors="replace")
    runtime = HOME_RUNTIME.read_text(encoding="utf-8", errors="replace") if HOME_RUNTIME.exists() else ""
    home_css = HOME_CSS.read_text(encoding="utf-8", errors="replace") if HOME_CSS.exists() else ""

    if not HOME_CSS.exists():
        errors.append("homepage scoped stylesheet missing: app/home-page.css")
    else:
        for marker in (".home-page{", ".home-hero{", ".reader-routing{"):
            if marker not in home_css:
                errors.append(f"homepage stylesheet missing core scoped rule: {marker}")
        if "\\n@media" in home_css:
            errors.append("homepage stylesheet contains a literal escaped newline before a media query")
        if "!important" in home_css:
            errors.append("homepage stylesheet must not rely on !important specificity escalation")
    if not re.search(r'href=["\']app/home-page\.css\?v=[A-Za-z0-9._-]+["\']', home):
        errors.append("homepage does not load a versioned scoped app/home-page.css asset")
    if re.search(r"<style>[\\s\\S]*?\\.home-", home):
        errors.append("homepage-specific CSS drifted back into an inline <style> block")

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

    for section_id in CURRENT_HOME_IDS:
        if f'id="{section_id}"' not in home:
            errors.append(f"homepage missing current reader-first section: {section_id}")

    for retired in RETIRED_HOME_MARKERS:
        if retired in home:
            errors.append(f"homepage reintroduced retired dashboard/teaching marker: {retired}")
        if retired == "home-page-projection.js" and retired in runtime:
            errors.append("homepage runtime still loads retired specialist projection machinery")

    if 'class="public-doors"' not in home:
        errors.append("homepage missing broad public Doors")
    if 'id="best-first-reads"' not in home:
        errors.append("homepage missing substantial first-read corridor")
    if 'id="world-glimpse"' not in home:
        errors.append("homepage missing compact world/structure glimpse")
    if 'id="reader-routing"' not in home:
        errors.append("homepage missing restrained archive-tool routing")

    if not PROJECT_SYNTHESIS.exists():
        errors.append("missing project synthesis for homepage contract")
    else:
        try:
            synthesis = json.loads(PROJECT_SYNTHESIS.read_text(encoding="utf-8"))
            projection = synthesis.get("homepage_projection", {})
            hierarchy = projection.get("hierarchy", [])
            sections = {x.get("id") for x in projection.get("sections", []) if isinstance(x, dict)}
            for section_id in CURRENT_HOME_IDS:
                if section_id not in hierarchy:
                    errors.append(f"homepage projection hierarchy missing current section: {section_id}")
                if section_id not in sections:
                    errors.append(f"homepage projection registry missing current section: {section_id}")
            for retired_id in ("project-substance","reality-cases","working-capabilities","foundation-rooms","structure-handoff","route-comparison","foundation-landscape"):
                if retired_id in hierarchy or retired_id in sections:
                    errors.append(f"homepage projection still registers retired section: {retired_id}")
            runtime_contract = projection.get("runtime_input_contract", {})
            if "app/home-page-projection.js" not in set(runtime_contract.get("retired_homepage_runtime_inputs", [])):
                errors.append("homepage contract must explicitly retire app/home-page-projection.js")
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"cannot read homepage project synthesis: {exc}")

    if "home-page-projection.js" in runtime:
        errors.append("live homepage runtime still references retired home-page-projection.js")
    if "reality-cases" in runtime or "route-comparison" in runtime:
        errors.append("live homepage runtime still targets retired specialist-section ids")

    if "data-news-feed" in home:
        for marker in ("loadStyleNear(newsTarget", "loadScriptNear(newsTarget"):
            if marker not in runtime:
                errors.append(f"homepage optional news runtime missing lazy-load marker: {marker}")

    if errors:
        print("HOMEPAGE RUNTIME VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("HOMEPAGE RUNTIME VALIDATION PASSED: reader-first Home is static-first, multi-realm, and free of retired dashboard projections.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
