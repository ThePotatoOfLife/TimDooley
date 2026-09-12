#!/usr/bin/env python3
"""Validate browse-first country interaction, overlay continuity, and render ownership."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SELECTION = ROOT / "world-map" / "3d-country-selection.js"
CARD = ROOT / "world-map" / "3d-country-card.js"
PULSE = ROOT / "world-map" / "3d-country-pulse.js"
BAR = ROOT / "world-map" / "3d-world-bar.js"
COMPOSITOR = ROOT / "world-map" / "3d-compositor.js"
BRIDGE = ROOT / "world-map" / "3d-scalar-runtime-bridge.js"
ACTIVE_VIEW = ROOT / "world-map" / "3d-active-view.js"
BOOTSTRAP = ROOT / "world-map" / "3d-bootstrap.js"


def read(path: Path, errors: list[str]) -> str:
    if not path.exists():
        errors.append(f"missing required file: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def require(text: str, token: str, label: str, errors: list[str]) -> None:
    if token not in text:
        errors.append(f"{label} missing required browse-performance marker: {token}")


def reject(text: str, token: str, label: str, errors: list[str]) -> None:
    if token in text:
        errors.append(f"{label} still contains rejected legacy behavior: {token}")


def main() -> int:
    errors: list[str] = []
    selection = read(SELECTION, errors)
    card = read(CARD, errors)
    pulse = read(PULSE, errors)
    bar = read(BAR, errors)
    compositor = read(COMPOSITOR, errors)
    bridge = read(BRIDGE, errors)
    active_view = read(ACTIVE_VIEW, errors)
    bootstrap = read(BOOTSTRAP, errors)

    for token in (
        "let pinnedCodes = []",
        "function togglePinnedCountry",
        "function pinCountry",
        "function unpinCountry",
        "potato-atlas-pin-change",
        "searchParams.set('pins'",
        "event.originalEvent?.shiftKey",
        "activateCountry(code",
    ):
        require(selection, token, "world-map/3d-country-selection.js", errors)

    reject(selection, "toggleCountrySelection(code);", "world-map/3d-country-selection.js", errors)
    reject(selection, "selectedCodes.push(code)", "world-map/3d-country-selection.js", errors)

    for token in (
        "window.__potatoAtlasActiveView",
        "potato-atlas-active-view-change",
        "function forCountry",
        "status: 'unknown'",
    ):
        require(active_view, token, "world-map/3d-active-view.js", errors)

    require(bootstrap, "./3d-active-view.js", "world-map/3d-bootstrap.js", errors)

    for token in (
        "Map color",
        "Map view",
        "data-atlas-pin",
        "data-atlas-statistics",
        "potato-atlas-country-card-rendered",
    ):
        require(card, token, "world-map/3d-country-card.js", errors)

    require(pulse, "potato-atlas-inspector-rendered", "world-map/3d-country-pulse.js", errors)
    require(bar, "Color:", "world-map/3d-world-bar.js", errors)

    require(compositor, "scalarFeatureStateBatches", "world-map/3d-compositor.js", errors)
    require(bridge, "compatibility adapter", "world-map/3d-scalar-runtime-bridge.js", errors)
    reject(bridge, "map.setFeatureState", "world-map/3d-scalar-runtime-bridge.js", errors)
    reject(bridge, "map.setPaintProperty", "world-map/3d-scalar-runtime-bridge.js", errors)

    if errors:
        print("WORLD MAP BROWSE/PERFORMANCE VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    print("WORLD MAP BROWSE/PERFORMANCE VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
