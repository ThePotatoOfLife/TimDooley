#!/usr/bin/env python3
"""Validate browse-first country interaction, overlay continuity, and render ownership."""
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SELECTION = ROOT / "world-map" / "3d-country-selection.js"
CARD = ROOT / "world-map" / "3d-country-card.js"
PULSE = ROOT / "world-map" / "3d-country-pulse.js"
BAR = ROOT / "world-map" / "3d-world-bar.js"
COMPOSITOR = ROOT / "world-map" / "3d-compositor.js"
BRIDGE = ROOT / "world-map" / "3d-scalar-runtime-bridge.js"
ACTIVE_VIEW = ROOT / "world-map" / "3d-active-view.js"
BOOTSTRAP = ROOT / "world-map" / "3d-bootstrap.js"
UI = ROOT / "world-map" / "3d-ui.js"
DEMOGRAPHY = ROOT / "world-map" / "3d-demography.js"
DIMENSIONS = ROOT / "world-map" / "3d-country-dimensions.js"
EVIDENCE = ROOT / "world-map" / "3d-evidence.js"


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


def node_check(paths: tuple[Path, ...], errors: list[str]) -> None:
    node = shutil.which("node")
    if not node:
        errors.append("node executable unavailable; cannot syntax-check World Map browse modules")
        return
    for path in paths:
        if not path.exists():
            continue
        result = subprocess.run(
            [node, "--check", str(path)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode:
            detail = (result.stderr or result.stdout).strip()
            errors.append(f"JavaScript syntax failed for {path.relative_to(ROOT)}: {detail}")


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
    ui = read(UI, errors)
    demography = read(DEMOGRAPHY, errors)
    dimensions = read(DIMENSIONS, errors)
    evidence = read(EVIDENCE, errors)

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
    require(bootstrap, "specialistLazyLoads", "world-map/3d-bootstrap.js", errors)

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
    require(bar, "Pinned", "world-map/3d-world-bar.js", errors)

    require(compositor, "scalarFeatureStateBatches", "world-map/3d-compositor.js", errors)
    require(compositor, "applyRuntimeEntityScalar", "world-map/3d-compositor.js", errors)
    require(bridge, "compatibility adapter", "world-map/3d-scalar-runtime-bridge.js", errors)
    require(bridge, "renderingOwner:'compositor'", "world-map/3d-scalar-runtime-bridge.js", errors)
    reject(bridge, "map.setFeatureState", "world-map/3d-scalar-runtime-bridge.js", errors)
    reject(bridge, "map.setPaintProperty", "world-map/3d-scalar-runtime-bridge.js", errors)

    # One central panel observer owns legacy/core panel lifecycle detection. Feature
    # modules consume the explicit event rather than independently watching the DOM.
    for token in ("function panelLifecycleKey", "potato-atlas-panel-rendered", "panelLifecycleRenders"):
        require(ui, token, "world-map/3d-ui.js", errors)
    if ui.count("new MutationObserver(") != 1:
        errors.append(f"world-map/3d-ui.js must construct exactly one panel lifecycle observer; found {ui.count('new MutationObserver(')}")
    for text, label in (
        (demography, "world-map/3d-demography.js"),
        (dimensions, "world-map/3d-country-dimensions.js"),
        (evidence, "world-map/3d-evidence.js"),
        (pulse, "world-map/3d-country-pulse.js"),
    ):
        require(text, "potato-atlas-panel-rendered", label, errors)
        reject(text, "new MutationObserver(", label, errors)

    node_check((SELECTION, CARD, PULSE, BAR, COMPOSITOR, BRIDGE, ACTIVE_VIEW, BOOTSTRAP, UI, DEMOGRAPHY, DIMENSIONS, EVIDENCE), errors)

    if errors:
        print("WORLD MAP BROWSE/PERFORMANCE VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    print("WORLD MAP BROWSE/PERFORMANCE VALIDATION PASSED")
    print("Browse + Pins · active color/stat continuity · single scalar owner · lazy specialist stack · one panel lifecycle observer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
