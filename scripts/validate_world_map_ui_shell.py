#!/usr/bin/env python3
"""Validate the ordinary World Map UI stays flat, map-first and collision-free."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "world-map" / "index.html"
UI = ROOT / "world-map" / "3d-ui.js"
WORLD_BAR = ROOT / "world-map" / "3d-world-bar.js"
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
    compositor = read(COMPOSITOR, errors)
    country_card = read(COUNTRY_CARD, errors)
    country_selection = read(COUNTRY_SELECTION, errors)

    if html:
        for menu_id, label in (
            ("layersMenu", "Layers"),
            ("traceMenu", "Analyze"),
            ("timeMenu", "Time"),
            ("viewMenu", "View"),
        ):
            pattern = rf'<details[^>]+id=["\']{re.escape(menu_id)}["\'][^>]*>\s*<summary>{re.escape(label)}</summary>'
            if not re.search(pattern, html, re.I):
                errors.append(f"World Map top navigation must expose direct {label!r} menu {menu_id}")

        if 'id="moreMenu"' in html or "id='moreMenu'" in html:
            errors.append("World Map must not hide the Home link inside a fifth collapsible More menu")
        if not re.search(r'<a[^>]+class=["\'][^"\']*top-home[^"\']*["\'][^>]+href=["\']\.\./["\']', html, re.I):
            errors.append("World Map top navigation must expose Home as a direct link")

    if ui:
        forbidden = ("atlasToolsMenu", "atlas-tools-root", "function installToolbox", "installToolbox();")
        for token in forbidden:
            if token in ui:
                errors.append(f"World Map UI must remain one level deep; nested toolbox marker still present: {token}")
        if ".time-state{top:auto!important;bottom:44px!important" not in ui:
            errors.append("historical time state must be stacked in the lower-left, above the persistent HUD")

    if country_card:
        compact = re.sub(r"\s+", "", country_card)
        if "#atlasCountryCard{position:absolute;left:10px;top:10px" not in compact:
            errors.append("country card must be anchored in the upper-left of the map")
        if "#atlasCountryCard{position:absolute;right:10px;top:10px" in compact:
            errors.append("country card still uses the old upper-right anchor")
        for token in (
            "Selected comparison",
            "Connections",
            "comparisonRows",
            "connectionRows",
            "land_area_km2",
            "potato-atlas-relation-mode-change",
        ):
            if token not in country_card:
                errors.append(f"country card must expose compact multi-country intelligence marker: {token}")

    if world_bar:
        compact = re.sub(r"\s+", "", world_bar)
        if "#atlasWorldBar{position:absolute;left:50%;top:10px;transform:translateX(-50%)" not in compact:
            errors.append("ordinary world toolbar must be centered at the top so it cannot collide with the upper-left country card")
        if "#atlasWorldContext{position:absolute;left:10px;bottom:10px" not in compact:
            errors.append("ordinary map context must occupy the lower-left information surface")
        for token in ("atlasWorldContext", "updateContext", "Current map view"):
            if token not in world_bar:
                errors.append(f"world toolbar must expose compact active-layer context marker: {token}")
        for token in ("data-relation-mode", "setRelationMode", "Money", "Systems", "Institutions"):
            if token not in world_bar:
                errors.append(f"ordinary Relations menu must provide actionable connection filters: {token}")

    if compositor:
        for token in ("atlas-query-outline", "atlasQueryMatch", "applyQueryHighlight"):
            if token not in compositor:
                errors.append(f"ANY/ALL set queries must have an explicit on-map result channel: {token}")

    if country_selection:
        for token in ("relationMode", "setRelationMode", "edgeMatchesRelationMode", "potato-atlas-relation-mode-change"):
            if token not in country_selection:
                errors.append(f"country selection must support bounded automatic relation filtering: {token}")

    if errors:
        print("World Map UI shell validation FAILED:")
        for error in errors:
            print(f" - {error}")
        return 1

    print("World Map UI shell validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
