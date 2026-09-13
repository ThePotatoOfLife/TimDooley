#!/usr/bin/env python3
"""Validate the ordinary World Map UI stays map-first, unified and collision-free."""
from __future__ import annotations

import re
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


def read(path: Path, errors: list[str]) -> str:
    if not path.is_file():
        errors.append(f"missing required World Map UI file: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


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

    if html:
        header_match = re.search(r'<header[^>]+class=["\'][^"\']*top[^"\']*["\'][^>]*>(.*?)</header>', html, re.I | re.S)
        header = header_match.group(1) if header_match else ""
        if not header:
            errors.append("World Map must expose one canonical top header")
        if 'id="atlasWorldBarHost"' not in header and "id='atlasWorldBarHost'" not in header:
            errors.append("World Map header must reserve atlasWorldBarHost for the registry controls from first paint")
        for menu_id in ("layersMenu", "traceMenu", "timeMenu", "viewMenu"):
            pattern = rf'<details[^>]+id=["\']{re.escape(menu_id)}["\'][^>]*\bhidden\b'
            if not re.search(pattern, html, re.I):
                errors.append(f"legacy control host {menu_id} must start hidden so it cannot flash before registry UI adoption")
        for token in ('id="compare"', 'id="panelToggle"'):
            if token not in header:
                errors.append(f"World Map header must keep core browse control visible: {token}")
        if 'id="moreMenu"' in html or "id='moreMenu'" in html:
            errors.append("World Map must not hide the Home link inside a fifth collapsible More menu")
        if not re.search(r'<a[^>]+class=["\'][^"\']*top-home[^"\']*["\'][^>]+href=["\']\.\./["\']', html, re.I):
            errors.append("World Map top navigation must expose Home as a direct link")

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
            "Coverage", "Period", "Current map view",
        ):
            if token not in world_bar:
                errors.append(f"unified header/current-view contract missing marker: {token}")
        if "host.appendChild(bar)" not in world_bar:
            errors.append("registry toolbar must render inside its stable header host")
        if "mapwrap" in world_bar and "querySelector('.mapwrap')" in world_bar:
            errors.append("registry toolbar must no longer install itself into the map canvas")
        for token in ("data-relation-mode", "setRelationMode", "Money", "Systems", "Institutions"):
            if token not in world_bar:
                errors.append(f"ordinary Relations menu must provide actionable connection filters: {token}")

    if active_view:
        for token in ("atlas-time-change", "timeState", "refreshSerial", "potato-atlas-active-view-change"):
            if token not in active_view:
                errors.append(f"authoritative active-view state missing synchronization marker: {token}")

    if bootstrap:
        if "declareDormant('Time', './3d-time.js'" not in bootstrap:
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

    if errors:
        print("World Map UI shell validation FAILED:")
        for error in errors:
            print(f" - {error}")
        return 1

    print("World Map UI shell validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
