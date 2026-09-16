#!/usr/bin/env python3
"""Validate deterministic World Map interaction arbitration and migrated consumers."""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / "world-map" / "3d-interaction-router.js"
LIFECYCLE = ROOT / "world-map" / "3d-panel-lifecycle.js"
COUNTRY_INTERACTION = ROOT / "world-map" / "3d-country-interaction.js"
SUBDIVISIONS = ROOT / "world-map" / "3d-subdivisions.js"
PLACES = ROOT / "world-map" / "3d-places.js"
INFRASTRUCTURE = ROOT / "world-map" / "3d-infrastructure.js"
GATEWAYS = ROOT / "world-map" / "3d-gateways.js"
TEST = ROOT / "scripts" / "test_world_map_interaction_router.mjs"
COUNTRY_TEST = ROOT / "scripts" / "test_world_map_country_interaction_ownership.mjs"
CORE_TEST = ROOT / "scripts" / "test_world_map_core_interaction_ownership.mjs"
PLACES_TEST = ROOT / "scripts" / "test_world_map_places_interaction_ownership.mjs"
INFRASTRUCTURE_TEST = ROOT / "scripts" / "test_world_map_infrastructure_interaction_ownership.mjs"
GATEWAY_TEST = ROOT / "scripts" / "test_world_map_gateway_interaction_ownership.mjs"


def main() -> int:
    errors: list[str] = []
    for path in (ROUTER, LIFECYCLE, COUNTRY_INTERACTION, SUBDIVISIONS, PLACES, INFRASTRUCTURE, GATEWAYS, TEST, COUNTRY_TEST, CORE_TEST, PLACES_TEST, INFRASTRUCTURE_TEST, GATEWAY_TEST):
        if not path.exists():
            errors.append(f"missing interaction-router file: {path.relative_to(ROOT)}")
    if errors:
        print("WORLD MAP INTERACTION ROUTER VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    router = ROUTER.read_text(encoding="utf-8", errors="replace")
    lifecycle = LIFECYCLE.read_text(encoding="utf-8", errors="replace")
    country_interaction = COUNTRY_INTERACTION.read_text(encoding="utf-8", errors="replace")
    subdivisions = SUBDIVISIONS.read_text(encoding="utf-8", errors="replace")
    places = PLACES.read_text(encoding="utf-8", errors="replace")
    infrastructure = INFRASTRUCTURE.read_text(encoding="utf-8", errors="replace")
    gateways = GATEWAYS.read_text(encoding="utf-8", errors="replace")

    for token in (
        "function createInteractionRouter",
        "function register",
        "function unregister",
        "function resolve",
        "function dispatch",
        "clickPriority",
        "hoverPriority",
        "queryRenderedFeatures",
        "__potatoAtlasOverlayHandled",
        "window.__potatoAtlasInteraction",
    ):
        if token not in router:
            errors.append(f"interaction router missing interface marker: {token}")

    if "__potatoAtlasLoadModule?.('Interaction Router', './3d-interaction-router.js')" not in lifecycle:
        errors.append("panel lifecycle must preload the shared Interaction Router")

    for token in (
        "const interaction = window.__potatoAtlasInteraction",
        "interaction.register('countries'",
        "objectType:'country'",
        "clickPriority:10",
        "hoverPriority:10",
        "window.__potatoAtlasSelection?.current",
        "window.__potatoAtlasSelection?.clear?.()",
        "await window.goCountry?.(code)",
        "map.jumpTo(camera)",
        "window.__potatoAtlasCoreInteractions?.countryHub?.(feature)",
        "window.__potatoAtlasCoreInteractions?.semanticHub?.(feature)",
        "window.__potatoAtlasCoreInteractions?.traceHub?.(feature)",
        "window.__potatoAtlasCoreInteractions?.relation?.(feature)",
    ):
        if token not in country_interaction:
            errors.append(f"country interaction migration missing marker: {token}")
    if "Legacy core overlay actions remain direct until their dedicated migration" in country_interaction:
        errors.append("country interaction still documents retired core-overlay direct ownership")
    if "onClick:() => {}" in country_interaction:
        errors.append("core interaction registrations must not remain compatibility no-ops")
    if "map.on('click'" in country_interaction:
        errors.append("country interaction bridge must not attach a direct click listener")

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

    for token in (
        "const interaction = window.__potatoAtlasInteraction",
        "interaction.register('places'",
        "objectType:'place'",
        "clickPriority:80",
        "hoverPriority:80",
        "enabled:() => visible",
        "function bindFallbackLayerEvents()",
    ):
        if token not in places:
            errors.append(f"Places interaction migration missing marker: {token}")
    if "Degraded/direct-module fallback" not in places:
        errors.append("Places legacy listeners must be explicitly documented as degraded fallback")

    for token in (
        "const interaction = window.__potatoAtlasInteraction",
        "interaction.register('infrastructure'",
        "objectType:'infrastructure'",
        "clickPriority:70",
        "hoverPriority:70",
        "async function handleInfrastructureClick",
        "await showPopup(asset",
    ):
        if token not in infrastructure:
            errors.append(f"Infrastructure interaction migration missing marker: {token}")
    if "Degraded/direct-module fallback" not in infrastructure:
        errors.append("Infrastructure direct listener must be explicitly documented as degraded fallback")

    for token in (
        "const interaction = window.__potatoAtlasInteraction",
        "interaction.register('gateways'",
        "objectType:'gateway'",
        "clickPriority:75",
        "hoverPriority:75",
        "async function handleGatewayClick",
        "emitGateway(p.id, gateway)",
    ):
        if token not in gateways:
            errors.append(f"Gateway interaction migration missing marker: {token}")
    if "Degraded/direct-module fallback" not in gateways:
        errors.append("Gateway direct listener must be explicitly documented as degraded fallback")

    node = shutil.which("node")
    if not node:
        errors.append("node executable unavailable; cannot run interaction-router regressions")
    else:
        for path in (ROUTER, COUNTRY_INTERACTION, SUBDIVISIONS, PLACES, INFRASTRUCTURE, GATEWAYS):
            result = subprocess.run([node, "--check", str(path)], cwd=ROOT, text=True, capture_output=True, check=False)
            if result.returncode:
                errors.append(f"JavaScript syntax failed for {path.relative_to(ROOT)}: " + (result.stderr.strip() or result.stdout.strip()))
        for test_path, label in (
            (TEST, "interaction-router"),
            (COUNTRY_TEST, "Country interaction ownership"),
            (CORE_TEST, "Core interaction ownership"),
            (PLACES_TEST, "Places interaction ownership"),
            (INFRASTRUCTURE_TEST, "Infrastructure interaction ownership"),
            (GATEWAY_TEST, "Gateway interaction ownership"),
        ):
            result = subprocess.run([node, str(test_path)], cwd=ROOT, text=True, capture_output=True, check=False)
            if result.returncode:
                errors.append(f"{label} regression failed: " + (result.stderr.strip() or result.stdout.strip()))

    print("World Map interaction router:")
    print("- semantic priority independent of rendered-feature order")
    print("- disabled registrations cannot win")
    print("- compatibility event claim retained only for still-unmigrated handlers")
    print("- country polygons use router priority 10")
    print("- country hubs, semantic hubs, trace hubs and relation lines use router-owned semantic actions")
    print("- subdivisions use router on normal boots with degraded fallback")
    print("- Infrastructure uses router at priority 70 while preserving its persistent popup")
    print("- Gateways use router at priority 75 while preserving gateway-change lifecycle")
    print("- Places use router on normal boots with degraded fallback")
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
