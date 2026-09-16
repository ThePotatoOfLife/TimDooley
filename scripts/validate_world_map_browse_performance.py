#!/usr/bin/env python3
"""Validate browse-first country interaction, overlay continuity, and render ownership."""
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SELECTION = ROOT / "world-map" / "3d-country-selection.js"
COUNTRY_INTERACTION = ROOT / "world-map" / "3d-country-interaction.js"
CARD = ROOT / "world-map" / "3d-country-card.js"
PULSE = ROOT / "world-map" / "3d-country-pulse.js"
BAR = ROOT / "world-map" / "3d-world-bar.js"
COMPOSITOR = ROOT / "world-map" / "3d-compositor.js"
BRIDGE = ROOT / "world-map" / "3d-scalar-runtime-bridge.js"
ACTIVE_VIEW = ROOT / "world-map" / "3d-active-view.js"
BOOTSTRAP = ROOT / "world-map" / "3d-bootstrap.js"
BOOT_GUARD = ROOT / "world-map" / "3d-boot-guard.js"
BOOTSTRAP_STAGING_TEST = ROOT / "scripts" / "test_world_map_inspection_bootstrap_staging.mjs"
PANEL_LIFECYCLE = ROOT / "world-map" / "3d-panel-lifecycle.js"
SUBDIVISIONS = ROOT / "world-map" / "3d-subdivisions.js"
HOVER = ROOT / "world-map" / "3d-hover.js"
TOOLTIP = ROOT / "world-map" / "3d-tooltip.js"
HOVER_ARTIFACT_TEST = ROOT / "scripts" / "test_world_map_hover_artifacts.mjs"
TOOLTIP_LIFECYCLE_TEST = ROOT / "scripts" / "test_world_map_tooltip_lifecycle.mjs"
POINTER_DRAG_ARTIFACT_TEST = ROOT / "scripts" / "test_world_map_pointer_drag_artifacts.mjs"
CAPITAL_OWNERSHIP_TEST = ROOT / "scripts" / "test_world_map_capital_ownership.mjs"
OVERLAY_OVERLAP_TEST = ROOT / "scripts" / "test_world_map_overlay_overlap.mjs"
UI = ROOT / "world-map" / "3d-ui.js"
DEMOGRAPHY = ROOT / "world-map" / "3d-demography.js"
DIMENSIONS = ROOT / "world-map" / "3d-country-dimensions.js"
EVIDENCE = ROOT / "world-map" / "3d-evidence.js"
PROVENANCE = ROOT / "world-map" / "3d-provenance.js"


def read(path: Path, errors: list[str]) -> str:
    if not path.exists():
        errors.append(f"missing required file: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def require(text: str, token: str, label: str, errors: list[str]) -> None:
    if token not in text:
        errors.append(f"{label} missing required browse-performance marker: {token}")


def require_any(text: str, tokens: tuple[str, ...], label: str, errors: list[str]) -> None:
    if not any(token in text for token in tokens):
        errors.append(f"{label} missing required browse-performance marker alternatives: {' | '.join(tokens)}")


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


def run_node_regression(path: Path, errors: list[str], label: str) -> None:
    node = shutil.which("node")
    if not node:
        errors.append(f"node executable unavailable; cannot run {label}")
        return
    if not path.exists():
        errors.append(f"missing required regression: {path.relative_to(ROOT)}")
        return
    result = subprocess.run(
        [node, str(path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()
        errors.append(f"{label} failed: {detail}")


def main() -> int:
    errors: list[str] = []
    selection = read(SELECTION, errors)
    country_interaction = read(COUNTRY_INTERACTION, errors)
    card = read(CARD, errors)
    pulse = read(PULSE, errors)
    bar = read(BAR, errors)
    compositor = read(COMPOSITOR, errors)
    bridge = read(BRIDGE, errors)
    active_view = read(ACTIVE_VIEW, errors)
    bootstrap = read(BOOTSTRAP, errors)
    boot_guard = read(BOOT_GUARD, errors)
    panel_lifecycle = read(PANEL_LIFECYCLE, errors)
    subdivisions = read(SUBDIVISIONS, errors)
    hover = read(HOVER, errors)
    tooltip = read(TOOLTIP, errors)
    ui = read(UI, errors)
    demography = read(DEMOGRAPHY, errors)
    dimensions = read(DIMENSIONS, errors)
    evidence = read(EVIDENCE, errors)
    provenance = read(PROVENANCE, errors)

    for token in (
        "let pinnedCodes = []",
        "function togglePinnedCountry",
        "function pinCountry",
        "function unpinCountry",
        "potato-atlas-pin-change",
        "searchParams.set('pins'",
        "activateCountry(code",
    ):
        require(selection, token, "world-map/3d-country-selection.js", errors)
    for token in (
        "event?.originalEvent?.shiftKey",
        "selection?.togglePinnedCountry?.(code)",
        "onClick:(event, feature) => { void selectCountry(feature, event); }",
    ):
        require(country_interaction, token, "world-map/3d-country-interaction.js", errors)

    reject(selection, "function interceptPolygonClick", "world-map/3d-country-selection.js", errors)
    reject(selection, "function installClickInterception", "world-map/3d-country-selection.js", errors)
    reject(selection, "toggleCountrySelection(code);", "world-map/3d-country-selection.js", errors)
    reject(selection, "selectedCodes.push(code)", "world-map/3d-country-selection.js", errors)

    for token in (
        "window.__potatoAtlasActiveView",
        "potato-atlas-active-view-change",
        "function forCountry",
    ):
        require(active_view, token, "world-map/3d-active-view.js", errors)
    require_any(active_view, ("status: 'unknown'", "status:'unknown'"), "world-map/3d-active-view.js", errors)

    require(bootstrap, "./3d-active-view.js", "world-map/3d-bootstrap.js", errors)
    require(bootstrap, "loadAfterPaint('Panel lifecycle', './3d-panel-lifecycle.js')", "world-map/3d-bootstrap.js", errors)
    require(bootstrap, "declareDormant('Progressive UI', './3d-ui.js'", "world-map/3d-bootstrap.js", errors)
    reject(bootstrap, "loadAfterPaint('Progressive UI', './3d-ui.js')", "world-map/3d-bootstrap.js", errors)
    require(bootstrap, "specialistLazyLoads", "world-map/3d-bootstrap.js", errors)
    require(bootstrap, "potato-atlas-working-selection-change", "world-map/3d-bootstrap.js", errors)
    reject(bootstrap, "map.once('click', promoteInspectionOnce);", "world-map/3d-bootstrap.js", errors)

    for token in (
        "Map color",
        "Map view",
        "data-atlas-pin",
        "data-atlas-statistics",
        "potato-atlas-country-card-rendered",
    ):
        require(card, token, "world-map/3d-country-card.js", errors)

    require(pulse, "potato-atlas-inspector-rendered", "world-map/3d-country-pulse.js", errors)
    require(pulse, "&quot;'", "world-map/3d-country-pulse.js", errors)
    render_start = pulse.find("async function render")
    render_lock = pulse.find("rendering = true;", render_start)
    view_await = pulse.find("const view = await", render_start)
    if render_start < 0 or render_lock < 0 or view_await < 0 or render_lock > view_await:
        errors.append("world-map/3d-country-pulse.js must acquire the render lock before awaiting active-view context")

    require_any(bar, ("Color:", "<span>Color</span>"), "world-map/3d-world-bar.js", errors)
    require(bar, "Pinned", "world-map/3d-world-bar.js", errors)

    require(compositor, "scalarFeatureStateBatches", "world-map/3d-compositor.js", errors)
    require(compositor, "applyRuntimeEntityScalar", "world-map/3d-compositor.js", errors)
    require(bridge, "compatibility adapter", "world-map/3d-scalar-runtime-bridge.js", errors)
    require(bridge, "renderingOwner:'compositor'", "world-map/3d-scalar-runtime-bridge.js", errors)
    reject(bridge, "map.setFeatureState", "world-map/3d-scalar-runtime-bridge.js", errors)
    reject(bridge, "map.setPaintProperty", "world-map/3d-scalar-runtime-bridge.js", errors)

    for token in (
        "activeKey", "latestEvent", "resolvedHtml",
        "tooltip.nextGeneration('country')", "tooltip.show('country'",
        "tooltip.invalidate('country-leave')",
        "placesCanOwnCapitals", "potato-atlas-places-ready",
    ):
        require(hover, token, "world-map/3d-hover.js", errors)
    require(hover, "await import(versionedModule('./3d-tooltip.js'))", "world-map/3d-hover.js", errors)
    require(hover, "window.__potatoAtlasTooltip", "world-map/3d-hover.js", errors)
    reject(hover, "const popup = new maplibregl.Popup", "world-map/3d-hover.js", errors)
    reject(hover, "showPopup(event, await countryHtml(", "world-map/3d-hover.js", errors)

    for token in (
        "function createTooltipService",
        "nextGeneration", "staleSuppressions", "invalidate",
        "dragstart", "zoomstart", "rotatestart", "pitchstart",
        "potato-atlas-projection-change",
    ):
        require(tooltip, token, "world-map/3d-tooltip.js", errors)

    for token in (
        "potato-atlas-pointer-dragging",
        "POINTER_DRAG_THRESHOLD_PX",
        "suppressUntilMove",
        ".maplibregl-popup:has(.atlas-hover)",
        "pointerDragSuppressions",
    ):
        reject(boot_guard, token, "world-map/3d-boot-guard.js", errors)

    for token in ("function suspendCountryCard", "function restoreCountryCard", "potato-atlas-country-card-rendered"):
        require(evidence, token, "world-map/3d-evidence.js", errors)

    require(ui, "potato-atlas-panel-rendered", "world-map/3d-ui.js", errors)
    reject(ui, "new MutationObserver(", "world-map/3d-ui.js", errors)
    reject(ui, "setPaintProperty('countries-fill','fill-opacity'", "world-map/3d-ui.js", errors)

    for token in (
        "atlas-subdivisions-active",
        "atlas-subdivision-hit",
        "atlas-subdivision-line",
        "atlas-subdivision-label",
        "cacheEvictions",
        "renderedPartitions",
    ):
        require(subdivisions, token, "world-map/3d-subdivisions.js", errors)
    for token in ("SOURCE_PREFIX", "LINE_PREFIX", "HIT_PREFIX", "LABEL_PREFIX"):
        reject(subdivisions, token, "world-map/3d-subdivisions.js", errors)

    for token in ("function panelLifecycleKey", "potato-atlas-panel-rendered", "panelLifecycleRenders"):
        require(panel_lifecycle, token, "world-map/3d-panel-lifecycle.js", errors)
    if panel_lifecycle.count("new MutationObserver(") != 1:
        errors.append(f"world-map/3d-panel-lifecycle.js must construct exactly one active panel lifecycle observer; found {panel_lifecycle.count('new MutationObserver(')}")
    require(panel_lifecycle, "window.__potatoAtlasPanelLifecycle", "world-map/3d-panel-lifecycle.js", errors)
    for text, label in (
        (demography, "world-map/3d-demography.js"),
        (dimensions, "world-map/3d-country-dimensions.js"),
        (evidence, "world-map/3d-evidence.js"),
        (pulse, "world-map/3d-country-pulse.js"),
        (provenance, "world-map/3d-provenance.js"),
    ):
        require(text, "potato-atlas-panel-rendered", label, errors)
    for path in sorted((ROOT / "world-map").glob("3d-*.js")):
        if path == PANEL_LIFECYCLE:
            continue
        reject(read(path, errors), "new MutationObserver(", str(path.relative_to(ROOT)), errors)

    node_check((SELECTION, COUNTRY_INTERACTION, CARD, PULSE, BAR, COMPOSITOR, BRIDGE, ACTIVE_VIEW, BOOTSTRAP, BOOT_GUARD, BOOTSTRAP_STAGING_TEST, PANEL_LIFECYCLE, SUBDIVISIONS, HOVER, TOOLTIP, UI, DEMOGRAPHY, DIMENSIONS, EVIDENCE, PROVENANCE), errors)
    run_node_regression(TOOLTIP_LIFECYCLE_TEST, errors, "World Map tooltip lifecycle regression")
    run_node_regression(HOVER_ARTIFACT_TEST, errors, "World Map hover artifact regression")
    run_node_regression(POINTER_DRAG_ARTIFACT_TEST, errors, "World Map pointer-drag workaround retirement regression")
    run_node_regression(CAPITAL_OWNERSHIP_TEST, errors, "World Map capital ownership regression")
    run_node_regression(OVERLAY_OVERLAP_TEST, errors, "World Map overlay overlap regression")
    run_node_regression(BOOTSTRAP_STAGING_TEST, errors, "World Map inspection bootstrap staging regression")

    if errors:
        print("WORLD MAP BROWSE/PERFORMANCE VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    print("WORLD MAP BROWSE/PERFORMANCE VALIDATION PASSED")
    print("Browse + Pins · router-owned country clicks · shared motion-safe transient tooltip · no pointer-drag compatibility shim · fallback-only capitals · exclusive top-left overlays · single panel observer · single surface-opacity owner · bounded subdivisions/Places · staged lazy specialist stack")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
