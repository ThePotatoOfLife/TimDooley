#!/usr/bin/env python3
"""Validate the ordinary World Map UI stays flat, map-first and collision-free."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "world-map" / "index.html"
UI = ROOT / "world-map" / "3d-ui.js"
COUNTRY_CARD = ROOT / "world-map" / "3d-country-card.js"


def read(path: Path, errors: list[str]) -> str:
    if not path.is_file():
        errors.append(f"missing required World Map UI file: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    errors: list[str] = []
    html = read(INDEX, errors)
    ui = read(UI, errors)
    country_card = read(COUNTRY_CARD, errors)

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

    if errors:
        print("World Map UI shell validation FAILED:")
        for error in errors:
            print(f" - {error}")
        return 1

    print("World Map UI shell validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
