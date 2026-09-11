#!/usr/bin/env python3
"""Validate the semantic navigation integration for the 3D Atlas."""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "world-map" / "3d-capability-registry.js"
SPATIAL = ROOT / "world-map" / "3d-spatial-navigation.js"
BOOTSTRAP = ROOT / "world-map" / "3d-bootstrap.js"
HTML = ROOT / "world-map" / "3d.html"
UI = ROOT / "world-map" / "3d-ui.js"
APP = ROOT / "world-map" / "3d-app.js"
NETWORKS = ROOT / "world-map" / "3d-networks.js"
SELECTION = ROOT / "world-map" / "3d-selection-ui.js"
METRICS = ROOT / "world-map" / "3d-metric-dimensions.js"
FAITH = ROOT / "world-map" / "3d-demography-facets.js"


def check_js_syntax(path: Path, errors: list[str], warnings: list[str]) -> None:
    node = shutil.which("node")
    if not node:
        warnings.append(f"node unavailable; skipped syntax check for {path.relative_to(ROOT)}")
        return
    text = path.read_text(encoding="utf-8")
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", encoding="utf-8", delete=False) as handle:
        handle.write(text)
        temp = Path(handle.name)
    try:
        result = subprocess.run([node, "--check", str(temp)], capture_output=True, text=True)
        if result.returncode:
            errors.append(
                f"{path.relative_to(ROOT)} JavaScript syntax check failed: "
                + (result.stderr.strip() or result.stdout.strip())
            )
    finally:
        temp.unlink(missing_ok=True)


def require(text: str, markers: tuple[str, ...], label: str, errors: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"{label} missing marker: {marker}")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    if not REGISTRY.exists():
        errors.append("missing world-map/3d-capability-registry.js")
    else:
        text = REGISTRY.read_text(encoding="utf-8")
        require(text, (
            "window.__potatoAtlasCapabilities",
            "function register",
            "function activate",
            "function deactivate",
            "potato-atlas-capability-change",
            "potato-atlas-capability-registry-change",
            "baseSurface",
            "worldOverlays",
            "relationModes",
            "axisLens",
        ), "capability registry", errors)
        check_js_syntax(REGISTRY, errors, warnings)

    if not SPATIAL.exists():
        errors.append("missing world-map/3d-spatial-navigation.js")
    else:
        spatial = SPATIAL.read_text(encoding="utf-8")
        require(spatial, (
            "window.__potatoAtlasSpatialUI",
            "function openZone",
            "function closeZone",
            "function renderZone",
            "potato-atlas-zone-open",
            "potato-atlas-zone-close",
            "What is there?",
            "What connects it?",
            "How did it change?",
            "How are we interpreting it?",
        ), "spatial navigation", errors)
        check_js_syntax(SPATIAL, errors, warnings)

    if not HTML.exists():
        errors.append("missing world-map/3d.html")
    else:
        html = HTML.read_text(encoding="utf-8")
        require(html, (
            'id="atlasWorldZone"',
            'id="atlasRelationsZone"',
            'id="atlasTimeZone"',
            'id="atlasAxisZone"',
            'id="atlasUtilities"',
            'id="atlasWorldDrawer"',
            'id="atlasRelationsDrawer"',
            'id="atlasAxisZonePanel"',
            'id="atlasTimeZonePanel"',
            'id="atlasCompatibilityControls"',
            'aria-label="Open World data"',
            'aria-label="Open Relations"',
            'aria-label="Open Time"',
            'aria-label="Open Axis lenses"',
        ), "spatial shell", errors)
        visible_shell = html.split('id="atlasCompatibilityControls"', 1)[0]
        for forbidden in ('<summary>Layers</summary>', '<summary>Trace</summary>', '<summary>View</summary>', '>Inspect</button>'):
            if forbidden in visible_shell:
                errors.append(f"legacy implementation control is still visible in normal shell: {forbidden}")

    if not BOOTSTRAP.exists():
        errors.append("missing world-map/3d-bootstrap.js")
    else:
        bootstrap = BOOTSTRAP.read_text(encoding="utf-8")
        require(bootstrap, (
            "3d-capability-registry.js",
            "3d-spatial-navigation.js",
            "window.__potatoAtlasLoadModule = loadAfterPaint",
            "potato-atlas-zone-open",
            "zone === 'world'",
            "zone === 'relations'",
            "zone === 'time'",
            "zone === 'axis'",
        ), "bootstrap", errors)
        check_js_syntax(BOOTSTRAP, errors, warnings)

    if UI.exists():
        ui = UI.read_text(encoding="utf-8")
        if "installToolbox" in ui or "atlasToolsMenu" in ui:
            errors.append("progressive UI still rebuilds the legacy Tools accordion")
        require(ui, ("function setPanel", "function setFocus", "window.__potatoAtlasUI"), "progressive UI", errors)
        check_js_syntax(UI, errors, warnings)

    # World providers must register by meaning rather than renderer mechanics.
    if METRICS.exists():
        metrics = METRICS.read_text(encoding="utf-8")
        require(metrics, ("zone:'world'", "category:'Economy'", "category:'People & society'", "setSurface", "renewable_electricity"), "World metric provider", errors)
        check_js_syntax(METRICS, errors, warnings)
    if FAITH.exists():
        faith = FAITH.read_text(encoding="utf-8")
        require(faith, ("zone:'world'", "category:'Faith & culture'", "unaffiliated", "diversity"), "World faith provider", errors)
        check_js_syntax(FAITH, errors, warnings)
    if SELECTION.exists():
        selection = SELECTION.read_text(encoding="utf-8")
        require(selection, ("world:places:capitals", "Overview", "Relations", "Compare", "Change", "Sources"), "selection context", errors)
        check_js_syntax(SELECTION, errors, warnings)

    # Task 4 red contract: contextual UI must drive direct domain APIs rather than
    # synthesizing clicks on hidden legacy controls.
    if APP.exists():
        app = APP.read_text(encoding="utf-8")
        require(app, (
            "window.__potatoAtlasRelations",
            "setVisible",
            "setType",
            "expand",
            "collapseToImmediate",
            "getDepth",
            "window.__potatoAtlasCompare",
            "startWithCurrent",
            "getCodes",
            "isActive",
        ), "direct Relations/Compare API", errors)
        check_js_syntax(APP, errors, warnings)
    if NETWORKS.exists():
        networks = NETWORKS.read_text(encoding="utf-8")
        require(networks, ("zone:'relations'", "category:'Institutions & alliances'", "relationModes"), "Relations network provider", errors)
        check_js_syntax(NETWORKS, errors, warnings)

    for warning in warnings:
        print("WARNING:", warning)
    for error in errors:
        print("ERROR:", error)

    if errors:
        print(f"Spatial navigation validation failed with {len(errors)} error(s).")
        return 1
    print("Spatial navigation registry + semantic providers: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
