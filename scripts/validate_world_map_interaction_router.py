#!/usr/bin/env python3
"""Validate deterministic World Map interaction arbitration and early-boot handoff."""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / "world-map" / "3d-interaction-router.js"
LIFECYCLE = ROOT / "world-map" / "3d-panel-lifecycle.js"
SUBDIVISIONS = ROOT / "world-map" / "3d-subdivisions.js"
BOOTSTRAP = ROOT / "world-map" / "3d-bootstrap.js"
APP = ROOT / "world-map" / "3d-app.js"
HANDOFF = ROOT / "world-map" / "3d-core-interaction-handoff.js"
HOVER = ROOT / "world-map" / "3d-hover.js"
COUNTRY = ROOT / "world-map" / "3d-country-selection.js"
TEST = ROOT / "scripts" / "test_world_map_interaction_router.mjs"
COMPAT_TEST = ROOT / "scripts" / "test_world_map_interaction_compatibility.mjs"


def main() -> int:
    errors: list[str] = []
    for path in (ROUTER, LIFECYCLE, SUBDIVISIONS, BOOTSTRAP, APP, HANDOFF, HOVER, COUNTRY, TEST, COMPAT_TEST):
        if not path.exists():
            errors.append(f"missing interaction-router file: {path.relative_to(ROOT)}")
    if errors:
        print("WORLD MAP INTERACTION ROUTER VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    router = ROUTER.read_text(encoding="utf-8", errors="replace")
    lifecycle = LIFECYCLE.read_text(encoding="utf-8", errors="replace")
    subdivisions = SUBDIVISIONS.read_text(encoding="utf-8", errors="replace")
    bootstrap = BOOTSTRAP.read_text(encoding="utf-8", errors="replace")
    app = APP.read_text(encoding="utf-8", errors="replace")
    handoff = HANDOFF.read_text(encoding="utf-8", errors="replace")
    hover = HOVER.read_text(encoding="utf-8", errors="replace")
    country = COUNTRY.read_text(encoding="utf-8", errors="replace")

    for token in (
        "function createInteractionRouter",
        "function register",
        "function unregister",
        "function resolve",
        "function dispatch",
        "clickPriority",
        "hoverPriority",
        "queryRenderedFeatures",
        "window.__potatoAtlasInteraction",
        "potato-atlas-interaction-ready",
    ):
        if token not in router:
            errors.append(f"interaction router missing interface marker: {token}")

    if "__potatoAtlasLoadModule?.('Interaction Router', './3d-interaction-router.js')" not in lifecycle:
        errors.append("panel lifecycle must retain the shared Interaction Router preload")

    for token in (
        "const interaction = window.__potatoAtlasInteraction",
        "if (interaction?.register)",
        "interaction.register('subdivisions'",
        "objectType:'subdivision'",
        "clickPriority:60",
        "hoverPriority:60",
    ):
        if token not in subdivisions:
            errors.append(f"subdivision interaction migration missing marker: {token}")
    if "Degraded/direct-module fallback" not in subdivisions:
        errors.append("subdivision legacy listener must be explicitly documented as degraded fallback")

    capture_index = bootstrap.find("await import(versionedModule('./3d-core-interaction-handoff.js'))")
    hover_index = bootstrap.find("await import(versionedModule('./3d-hover.js'))")
    if capture_index < 0 or hover_index < 0 or capture_index >= hover_index:
        errors.append("bootstrap must arm core interaction capture before the renderer boots")
    router_index = bootstrap.find("loadAfterPaint('Interaction Router', './3d-interaction-router.js')")
    country_index = bootstrap.find("loadAfterPaint('Country selection', './3d-country-selection.js')")
    if router_index < 0 or country_index < 0 or router_index >= country_index:
        errors.append("bootstrap must load Interaction Router before canonical country selection")

    if "map.on('click','countries-fill',handleCountryPolygonClick)" not in app:
        errors.append("canonical 3d-app renderer must remain in-place for the capture handoff")
    for token in (
        "function handoffCoreInteractions(interaction)",
        "interaction.register('core-country-fallback'",
        "interaction.register('core-country-hubs'",
        "interaction.register('core-semantic-hubs'",
        "interaction.register('core-trace-hubs'",
        "interaction.register('core-relations'",
        "map.off('click', layerId, listener)",
        "potato-atlas-core-ready",
        "potato-atlas-interaction-ready",
    ):
        if token not in handoff:
            errors.append(f"core interaction handoff missing marker: {token}")

    for token in (
        "const interaction = window.__potatoAtlasInteraction",
        "interaction.unregister('core-country-fallback')",
        "interaction.register('countries'",
        "objectType:'country'",
        "clickPriority:10",
    ):
        if token not in country:
            errors.append(f"country selection router migration missing marker: {token}")
    if "__potatoAtlasOverlayHandled = true" not in country:
        errors.append("country selection degraded fallback must still claim handled direct events")
    if "installClickInterception();" not in country:
        errors.append("country selection degraded fallback must still install the direct click interception path")

    for token in (
        "interaction.register('country-hover'",
        "interaction.register('legacy-capitals'",
        "Degraded/direct-module fallback",
    ):
        if token not in hover:
            errors.append(f"hover/capital router migration missing marker: {token}")

    node = shutil.which("node")
    if not node:
        errors.append("node executable unavailable; cannot run interaction-router regression")
    else:
        for path in (ROUTER, SUBDIVISIONS, APP, HANDOFF, HOVER, COUNTRY):
            result = subprocess.run([node, "--check", str(path)], cwd=ROOT, text=True, capture_output=True, check=False)
            if result.returncode:
                errors.append(f"JavaScript syntax failed for {path.relative_to(ROOT)}: " + (result.stderr.strip() or result.stdout.strip()))
        result = subprocess.run([node, str(TEST)], cwd=ROOT, text=True, capture_output=True, check=False)
        if result.returncode:
            errors.append("interaction-router regression failed: " + (result.stderr.strip() or result.stdout.strip()))
        result = subprocess.run([node, str(COMPAT_TEST)], cwd=ROOT, text=True, capture_output=True, check=False)
        if result.returncode:
            errors.append("interaction compatibility regression failed: " + (result.stderr.strip() or result.stdout.strip()))

    print("World Map interaction router:")
    print("- semantic priority independent of rendered-feature order")
    print("- disabled registrations cannot win")
    print("- pre-core capture hands direct click listeners to the shared router")
    print("- canonical 3d-app renderer remains in-place and unchanged")
    print("- country and legacy-capital interaction owned by the router on normal boots")
    print("- compatibility event claim retained only for degraded direct-handler fallback")
    print(f"Errors: {len(errors)}")
    if errors:
        print("WORLD MAP INTERACTION ROUTER VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("WORLD MAP INTERACTION ROUTER VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
