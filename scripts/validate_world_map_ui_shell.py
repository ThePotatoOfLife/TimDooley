#!/usr/bin/env python3
"""Validate the ordinary World Map UI stays map-first, unified and collision-free."""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "world-map" / "index.html"
UI = ROOT / "world-map" / "3d-ui.js"
WORLD_BAR = ROOT / "world-map" / "3d-world-bar.js"
ACTIVE_VIEW = ROOT / "world-map" / "3d-active-view.js"
BOOTSTRAP = ROOT / "world-map" / "3d-bootstrap.js"
COMPOSITOR = ROOT / "world-map" / "3d-compositor.js"
COUNTRY_CARD = ROOT / "world-map" / "3d-country-card.js"
COUNTRY_SELECTION = ROOT / "world-map" / "3d-country-selection.js"
PANEL_LIFECYCLE = ROOT / "world-map" / "3d-panel-lifecycle.js"
PLACES = ROOT / "world-map" / "3d-places.js"
SEARCH = ROOT / "world-map" / "3d-search.js"
SEARCH_CORE = ROOT / "world-map" / "3d-search-core.js"
PUBLIC_PATCH = ROOT / "scripts" / "patch_home_discovery.py"


def read(path: Path, errors: list[str]) -> str:
    if not path.is_file():
        errors.append(f"missing required World Map UI file: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def run_check(command: list[str], label: str, errors: list[str]) -> None:
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    if result.returncode:
        detail = (result.stdout + "\n" + result.stderr).strip()
        errors.append(f"{label} failed" + (f": {detail}" if detail else ""))


def main() -> int:
    errors: list[str] = []
    html = read(INDEX, errors)
    ui = read(UI, errors)
    world_bar = read(WORLD_BAR, errors)
    active_view = read(ACTIVE_VIEW, errors)
    bootstrap = read(BOOTSTRAP, errors)
    compositor = read(COMPOSITOR, errors)
    country_card = read(COUNTRY_CARD, errors)
    country_selection = read(COUNTRY_SELECTION, errors)
    panel_lifecycle = read(PANEL_LIFECYCLE, errors)
    places = read(PLACES, errors)
    search = read(SEARCH, errors)
    search_core = read(SEARCH_CORE, errors)
    public_patch = read(PUBLIC_PATCH, errors)

    if html:
        header_match = re.search(r'<header[^>]+class=["\'][^"\']*top[^"\']*["\'][^>]*>(.*?)</header>', html, re.I | re.S)
        header = header_match.group(1) if header_match else ""
        if not header:
            errors.append("World Map must expose one canonical top header")
        for token in ('id="compare"', 'id="panelToggle"'):
            if token not in header:
                errors.append(f"World Map header must keep core browse control visible: {token}")
        for menu_id in ("layersMenu", "traceMenu", "timeMenu", "viewMenu"):
            if f'id="{menu_id}"' not in html:
                errors.append(f"World Map source must retain compatibility control host {menu_id}")
        if 'id="moreMenu"' in html or "id='moreMenu'" in html:
            errors.append("World Map must not hide the Home link inside a fifth collapsible More menu")
        if not re.search(r'<a[^>]+class=["\'][^"\']*top-home[^"\']*["\'][^>]+href=["\']\.\./["\']', html, re.I):
            errors.append("World Map top navigation must expose Home as a direct link")

    if public_patch:
        for token in (
            'atlasWorldBarHost',
            'World map controls',
            "'<details class=\"menu\" id=\"layersMenu\">', '<details class=\"menu\" id=\"layersMenu\" hidden>'",
            "'<details class=\"menu\" id=\"traceMenu\">', '<details class=\"menu\" id=\"traceMenu\" hidden>'",
            "'<details class=\"menu\" id=\"timeMenu\">', '<details class=\"menu\" id=\"timeMenu\" hidden>'",
            "'<details class=\"menu\" id=\"viewMenu\">', '<details class=\"menu\" id=\"viewMenu\" hidden>'",
        ):
            if token not in public_patch:
                errors.append(f"public World Map first-paint projection missing unified-header marker: {token}")

    if ui:
        forbidden = ("atlasToolsMenu", "atlas-tools-root", "function installToolbox", "installToolbox();")
        for token in forbidden:
            if token in ui:
                errors.append(f"World Map UI must remain one level deep; nested toolbox marker still present: {token}")

    if country_card:
        compact = re.sub(r"\s+", "", country_card)
        if "#atlasCountryCard{position:absolute;left:10px;top:10px" not in compact:
            errors.append("country card must be anchored in the upper-left of the map")
        if "#atlasCountryCard{position:absolute;right:10px;top:10px" in compact:
            errors.append("country card still uses the old upper-right anchor")
        for token in (
            "Pinned comparison", "Connections", "comparisonRows", "connectionRows",
            "areaObservation", "populationObservation", "potato-atlas-relation-mode-change",
            "data-atlas-pin", "data-atlas-statistics", "Map color",
        ):
            if token not in country_card:
                errors.append(f"country card must expose compact browse/pin intelligence marker: {token}")

    if world_bar:
        compact = re.sub(r"\s+", "", world_bar)
        if "document.getElementById('atlasWorldBarHost')" not in world_bar and 'document.getElementById("atlasWorldBarHost")' not in world_bar:
            errors.append("registry toolbar must install into atlasWorldBarHost in the real header")
        if "#atlasWorldBar{position:absolute;left:50%;top:10px;transform:translateX(-50%)" in compact:
            errors.append("registry toolbar must not float over the map canvas")
        if "#atlasWorldBar{position:static" not in compact and "#atlasWorldBar{position:relative" not in compact:
            errors.append("registry toolbar must participate in stable header layout")
        for menu_id in ("traceMenu", "timeMenu", "viewMenu"):
            if f"adoptLegacyMenu('{menu_id}'" not in world_bar and f'adoptLegacyMenu("{menu_id}"' not in world_bar:
                errors.append(f"registry header must adopt existing {menu_id} controls instead of leaving a duplicate surface")
        for token in (
            "__potatoAtlasLoadModule", "3d-time.js", "potato-atlas-active-view-change",
            "atlas-time-change", "Projection", "Time", "Matches", "Pinned", "Connections",
            "Coverage", "Period", "Current map view", "Interior modules",
        ):
            if token not in world_bar:
                errors.append(f"unified header/current-view contract missing marker: {token}")
        if "host.appendChild(bar)" not in world_bar:
            errors.append("registry toolbar must render inside its stable header host")
        if "const host = document.querySelector('.mapwrap')" in world_bar:
            errors.append("registry toolbar must no longer use mapwrap as its toolbar host")
        for token in ("#atlasWorldBar #viewMenu #globe", "#atlasWorldBar #traceMenu #relations"):
            if token not in world_bar:
                errors.append(f"unified header must suppress legacy duplicate control: {token}")
        for token in ("data-relation-mode", "setRelationMode", "Money", "Systems", "Institutions"):
            if token not in world_bar:
                errors.append(f"ordinary Relations menu must provide actionable connection filters: {token}")
        if " · ${count}" in world_bar or "summary.textContent = count ?" in world_bar:
            errors.append("Groups, Religion and Stats menu labels must remain static when selections change")
        if "Relations · ${relationLabel(mode)}" in world_bar or "summary.textContent = mode === 'all' ? 'Relations'" in world_bar:
            errors.append("Relations menu label must remain static when its filter changes")
        if "#atlasWorldResult{min-width:72px;max-width:92px" in compact:
            errors.append("World Map result summary must not use a variable-width footprint")
        if "#atlasWorldResult{width:92px;flex:0 0 92px" not in world_bar:
            errors.append("World Map result summary must reserve one fixed header width")

    if active_view:
        for token in ("atlas-time-change", "timeState", "refreshSerial", "matchCount", "potato-atlas-active-view-change"):
            if token not in active_view:
                errors.append(f"authoritative active-view state missing synchronization marker: {token}")

    if bootstrap and "declareDormant('Time', './3d-time.js'" not in bootstrap:
        errors.append("Time should remain lazy but explicitly declared in bootstrap diagnostics")

    if compositor:
        for token in ("atlas-query-outline", "atlasQueryMatch", "applyQueryHighlight"):
            if token not in compositor:
                errors.append(f"ANY/ALL set queries must have an explicit on-map result channel: {token}")

    if country_selection:
        for token in (
            "relationMode", "setRelationMode", "edgeMatchesRelationMode",
            "potato-atlas-relation-mode-change", "pinnedCodes", "togglePinnedCountry",
            "potato-atlas-pin-change",
        ):
            if token not in country_selection:
                errors.append(f"country selection must support browse-first state and bounded automatic relation filtering: {token}")

    if panel_lifecycle:
        for token in ("./3d-search.js", "./3d-places.js", "searchParams.has('place')", "map.getZoom() < 3.2"):
            if token not in panel_lifecycle:
                errors.append(f"World Map progressive place/search lifecycle missing marker: {token}")

    if places:
        for token in ("world-cities.geo.json", "world-capitals.geo.json", "minimum_zoom", "__potatoAtlasPlaces", "potato-atlas-place-select", "potato-atlas-places-ready"):
            if token not in places:
                errors.append(f"World Map Places integration missing marker: {token}")

    if search:
        for token in ("3d-search-core.js", "__potatoAtlasSubdivisions", "__potatoAtlasPlaces", "stopImmediatePropagation", "Find country, state or city"):
            if token not in search:
                errors.append(f"World Map unified Search integration missing marker: {token}")
        if "ready:ensureRecords()" in search:
            errors.append("World Map unified Search must not eagerly load place/subdivision records")

    if search_core:
        for token in ("buildSearchRecords", "rankSearchRecords", "normalizeSearchText", "country", "subdivision", "city"):
            if token not in search_core:
                errors.append(f"World Map search core missing marker: {token}")

    node = shutil.which("node")
    if node:
        run_check([node, "--check", str(SEARCH_CORE)], "Search core syntax", errors)
        run_check([node, "--check", str(SEARCH)], "Search controller syntax", errors)
        run_check([node, "--check", str(PLACES)], "Places syntax", errors)
        run_check([node, str(ROOT / "scripts" / "test_world_map_search.mjs")], "Search ranking contract", errors)
    else:
        errors.append("node is required to validate World Map Places/Search JavaScript")

    run_check([sys.executable, "-m", "unittest", "scripts.test_world_cities_builder", "-v"], "City runtime builder tests", errors)
    run_check([sys.executable, str(ROOT / "scripts" / "validate_world_cities.py")], "City runtime validation", errors)
    run_check([sys.executable, str(ROOT / "scripts" / "validate_world_map_places.py")], "Places integration validation", errors)
    run_check([sys.executable, str(ROOT / "scripts" / "validate_world_map_search.py")], "Search integration validation", errors)

    if errors:
        print("World Map UI shell validation FAILED:")
        for error in errors:
            print(f" - {error}")
        return 1

    print("World Map UI shell validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
