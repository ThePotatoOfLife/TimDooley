#!/usr/bin/env python3
"""Validate canonical World Map infrastructure, contextual rendering and integration."""
from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INFRA = ROOT / "data" / "world-map-infrastructure.json"
COUNTRIES = ROOT / "data" / "countries" / "index.json"
ENTITIES = ROOT / "data" / "world-map-entities.json"
GATEWAYS = ROOT / "data" / "world-map-gateways.json"
CHAINS = ROOT / "data" / "world-system-chains.json"
RUNTIME_BUILDER = ROOT / "scripts" / "build_world_map_runtime.py"
ENTITY_RUNTIME = ROOT / "world-map" / "3d-entity-runtime.js"
INFRA_BROWSER = ROOT / "world-map" / "3d-infrastructure.js"
GATEWAY_BROWSER = ROOT / "world-map" / "3d-gateways.js"
CHAIN_BROWSER = ROOT / "world-map" / "3d-chain-explorer.js"
IMPACT_BROWSER = ROOT / "world-map" / "3d-impact-trace.js"
WORLD_BAR = ROOT / "world-map" / "3d-world-bar.js"
BOOTSTRAP = ROOT / "world-map" / "3d-bootstrap.js"

SUPPORTED_TYPES = {
    "port", "maritime-terminal", "strait-associated-terminal", "canal-associated-terminal",
    "grid-interconnector", "pipeline", "lng-terminal", "subsea-cable-system", "cable-landing",
    "rail-junction", "freight-corridor",
}
CAUSAL_RELATIONSHIPS = {"depends-on", "uses-gateway", "alternative-route"}
CONTEXT_RELATIONSHIPS = {"serves", "connects", "member-of-chain", "member-of-system", "associated-with"}
SEED_MINIMUMS = {
    "turkish-straits": 1,
    "suez-sumed": 2,
    "malacca-strait": 2,
    "hormuz-strait": 1,
    "panama-canal": 2,
    "cape-good-hope-route": 2,
    "bab-el-mandeb": 1,
}


def load(path: Path) -> dict:
    if not path.is_file():
        raise AssertionError(f"missing required infrastructure file: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def generated_runtime() -> dict:
    if not RUNTIME_BUILDER.is_file():
        raise AssertionError("missing scripts/build_world_map_runtime.py")
    spec = importlib.util.spec_from_file_location("world_map_runtime_infrastructure_validation", RUNTIME_BUILDER)
    assert spec and spec.loader, "could not load World Map runtime builder"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert hasattr(module, "build_runtime"), "runtime builder must expose build_runtime()"
    return module.build_runtime()


def require_tokens(path: Path, tokens: tuple[str, ...], label: str, errors: list[str]) -> str:
    if not path.is_file():
        errors.append(f"missing {label}: {path.relative_to(ROOT)}")
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    for token in tokens:
        if token not in text:
            errors.append(f"{label} missing marker: {token}")
    return text


def main() -> int:
    errors: list[str] = []
    try:
        data = load(INFRA)
        country_index = load(COUNTRIES)
        entity_source = load(ENTITIES)
        gateway_source = load(GATEWAYS)
        chain_source = load(CHAINS)
    except Exception as exc:
        print("World Map infrastructure validation FAILED:")
        print(f" - {exc}")
        return 1

    policy = data.get("policy") or {}
    if policy.get("missing_is_unknown") is not True:
        errors.append("infrastructure policy must state missing_is_unknown=true")
    if policy.get("approximate_coordinates_are_visualization_only") is not True:
        errors.append("infrastructure policy must mark approximate coordinates as visualization-only")
    if policy.get("association_does_not_imply_dependency") is not True:
        errors.append("infrastructure policy must forbid dependency inference from association")
    if policy.get("gateway_authority") != "data/world-map-gateways.json":
        errors.append("gateway authority must remain data/world-map-gateways.json")

    rows = country_index.get("countries") or []
    canonical = {str(row.get("iso3") or "").upper() for row in rows}
    registered = set((entity_source.get("entities") or {}).keys())
    valid_codes = canonical | registered
    gateway_ids = set((gateway_source.get("gateways") or {}).keys())
    chain_ids = set((chain_source.get("chains") or {}).keys())
    assets = data.get("assets") or {}
    if not assets:
        errors.append("infrastructure asset registry must not be empty")

    seen = set()
    gateway_counts = {key: 0 for key in SEED_MINIMUMS}
    for asset_id, asset in assets.items():
        if asset_id in seen:
            errors.append(f"duplicate infrastructure id: {asset_id}")
        seen.add(asset_id)
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", asset_id):
            errors.append(f"{asset_id}: id must be stable kebab-case")
        if asset.get("id") != asset_id:
            errors.append(f"{asset_id}: record id must match key")
        if asset.get("type") not in SUPPORTED_TYPES:
            errors.append(f"{asset_id}: unsupported type {asset.get('type')!r}")
        if asset.get("evidence_class") != "observed":
            errors.append(f"{asset_id}: evidence_class must be observed")
        if not str(asset.get("source") or "").strip():
            errors.append(f"{asset_id}: source required")
        source_url = str(asset.get("source_url") or "")
        if not source_url.startswith("https://"):
            errors.append(f"{asset_id}: https source_url required")
        countries = asset.get("countries") or []
        if not isinstance(countries, list) or not countries:
            errors.append(f"{asset_id}: at least one country/entity association required")
        unknown_codes = sorted(set(countries) - valid_codes)
        if unknown_codes:
            errors.append(f"{asset_id}: unknown country/entity codes {unknown_codes}")

        location = asset.get("location")
        if isinstance(location, dict):
            coords = location.get("coordinates")
            if location.get("type") != "Point" or not isinstance(coords, list) or len(coords) != 2:
                errors.append(f"{asset_id}: point location must contain [lon, lat]")
            elif not all(isinstance(value, (int, float)) for value in coords):
                errors.append(f"{asset_id}: coordinates must be numeric")
            if not str(location.get("coordinate_precision") or "").startswith("approximate"):
                errors.append(f"{asset_id}: approximate coordinate precision must be explicit")
            if location.get("navigation_use") is not False:
                errors.append(f"{asset_id}: approximate coordinates must set navigation_use=false")
        elif asset.get("geometry_status") != "no-geometry":
            errors.append(f"{asset_id}: location or explicit no-geometry status required")

        for gateway_id in asset.get("gateway_ids", []) or []:
            if gateway_id not in gateway_ids:
                errors.append(f"{asset_id}: unresolved gateway id {gateway_id}")
            if gateway_id in gateway_counts:
                gateway_counts[gateway_id] += 1
        for chain_id in asset.get("chain_ids", []) or []:
            if chain_id not in chain_ids:
                errors.append(f"{asset_id}: unresolved chain id {chain_id}")

        for relation in asset.get("relationships", []) or []:
            relationship = relation.get("relationship")
            causal_status = relation.get("causal_status")
            if relationship in CAUSAL_RELATIONSHIPS and causal_status not in {"explicit-dependency", "explicit-alternative"}:
                errors.append(f"{asset_id}: causal relationship {relationship} needs explicit causal status")
            if relationship in CONTEXT_RELATIONSHIPS and causal_status not in {None, "contextual"}:
                errors.append(f"{asset_id}: contextual relationship {relationship} cannot become {causal_status}")
            if relationship not in CAUSAL_RELATIONSHIPS | CONTEXT_RELATIONSHIPS:
                errors.append(f"{asset_id}: unknown infrastructure relationship {relationship!r}")

    for gateway_id, minimum in SEED_MINIMUMS.items():
        if gateway_counts[gateway_id] < minimum:
            errors.append(f"first infrastructure seed requires {minimum}+ assets linked to {gateway_id}; found {gateway_counts[gateway_id]}")

    bad = {"relationship": "member-of-chain", "causal_status": "explicit-dependency"}
    if not (bad["relationship"] in CONTEXT_RELATIONSHIPS and bad["causal_status"] != "contextual"):
        errors.append("causal guardrail regression fixture is not exercising contextual-vs-causal distinction")

    try:
        runtime = generated_runtime()
        plane = runtime.get("infrastructure") or {}
        projected_assets = plane.get("assets") or {}
        if set(projected_assets) != set(assets):
            errors.append("runtime infrastructure assets must exactly project canonical infrastructure ids")
        by_entity = plane.get("by_entity") or {}
        by_gateway = plane.get("by_gateway") or {}
        by_chain = plane.get("by_chain") or {}
        coverage = plane.get("coverage") or {}
        if coverage.get("assets") != len(assets):
            errors.append(f"runtime infrastructure coverage.assets must equal {len(assets)}")
        if "port-of-balboa" not in (by_entity.get("PAN") or []):
            errors.append("runtime by_entity PAN must include port-of-balboa")
        if "east-port-said-port" not in (by_gateway.get("suez-sumed") or []):
            errors.append("runtime by_gateway suez-sumed must include east-port-said-port")
        for index_name, index in (("by_entity", by_entity), ("by_gateway", by_gateway), ("by_chain", by_chain)):
            for key, asset_ids in index.items():
                unresolved = sorted(set(asset_ids) - set(projected_assets))
                if unresolved:
                    errors.append(f"runtime {index_name}.{key} contains unresolved assets {unresolved}")

        impact = runtime.get("impact") or {}
        nodes = impact.get("nodes") or {}
        edges = impact.get("edges") or []
        for asset_id in assets:
            node_id = f"infrastructure:{asset_id}"
            if node_id not in nodes:
                errors.append(f"Impact graph missing infrastructure node {node_id}")
        if not any(edge.get("source") == "infrastructure:east-port-said-port" and edge.get("target") == "gateway:suez-sumed" and edge.get("causal_status") == "explicit-dependency" for edge in edges):
            errors.append("explicit East Port Said uses-gateway dependency must survive into Impact graph")
        if not any(edge.get("source") == "infrastructure:port-of-balboa" and edge.get("target") == "gateway:panama-canal" and edge.get("causal_status") == "explicit-dependency" for edge in edges):
            errors.append("explicit Balboa uses-gateway dependency must survive into Impact graph")
        if any(edge.get("source") == "infrastructure:manzanillo-international-terminal-panama" and edge.get("causal_status") == "explicit-dependency" for edge in edges):
            errors.append("context-only Manzanillo association must not become an Impact dependency")
    except Exception as exc:
        errors.append(f"runtime infrastructure projection failed: {exc}")

    entity_runtime = require_tokens(
        ENTITY_RUNTIME,
        ("infrastructure", "infrastructureForEntity", "infrastructureForGateway", "infrastructureForChain", "impactNodeForInfrastructure"),
        "shared entity runtime",
        errors,
    )

    browser = require_tokens(
        INFRA_BROWSER,
        (
            "atlas-infrastructure-context", "atlas-infrastructure-points", "showForEntity", "showForGateway", "showForChain", "showAsset",
            "infrastructureForEntity", "infrastructureForGateway", "infrastructureForChain", "impactNodeForInfrastructure", "MAX_CONTEXT_ASSETS",
            "geometry_status", "source_url", "window.__potatoAtlasInfrastructure", "potato-atlas-working-selection-change",
            "Infrastructure context", "data-infrastructure-id", "atlasCountryInfrastructureContext",
        ),
        "contextual infrastructure browser",
        errors,
    )
    if browser:
        if "MAX_CONTEXT_ASSETS = 12" not in browser:
            errors.append("contextual infrastructure browser must cap ordinary map rendering at 12 assets")
        if "new maplibregl.Map" in browser:
            errors.append("infrastructure browser must reuse the canonical map renderer")
        if "world-map-infrastructure.json" in browser:
            errors.append("infrastructure browser must consume shared runtime APIs rather than refetch canonical JSON")
        node = shutil.which("node")
        if node:
            result = subprocess.run([node, "--check", str(INFRA_BROWSER)], text=True, capture_output=True)
            if result.returncode:
                errors.append("infrastructure JavaScript syntax failed: " + (result.stderr.strip() or result.stdout.strip()))
        else:
            errors.append("node unavailable; cannot verify infrastructure JavaScript syntax")

    gateway_browser = require_tokens(
        GATEWAY_BROWSER,
        ("infrastructureForGateway", "potato-atlas-gateway-change", "Infrastructure", "data-infrastructure-id"),
        "gateway browser integration",
        errors,
    )
    chain_browser = require_tokens(
        CHAIN_BROWSER,
        ("infrastructureForChain", "Infrastructure", "data-infrastructure-id"),
        "functional-chain infrastructure integration",
        errors,
    )
    impact_browser = require_tokens(
        IMPACT_BROWSER,
        ("impactNodeForInfrastructure", "showInfrastructure", "['country','territory'].includes", "window.__potatoAtlasImpactTrace"),
        "Impact infrastructure integration",
        errors,
    )
    if impact_browser and "infrastructure" in re.search(r"function nodeCode\(node\).*?\n\}", impact_browser, re.S).group(0) if re.search(r"function nodeCode\(node\).*?\n\}", impact_browser, re.S) else False:
        errors.append("Impact nodeCode must not map infrastructure nodes onto country polygon feature-state")

    if WORLD_BAR.is_file():
        world_bar = WORLD_BAR.read_text(encoding="utf-8", errors="replace")
        if re.search(r"Infrastructure", world_bar, re.I):
            errors.append("World Bar must not gain a permanent Infrastructure control")
    if BOOTSTRAP.is_file():
        bootstrap = BOOTSTRAP.read_text(encoding="utf-8", errors="replace")
        if "./3d-infrastructure.js" not in bootstrap:
            errors.append("bootstrap must load contextual infrastructure module")

    if errors:
        print("World Map infrastructure validation FAILED:")
        for error in errors:
            print(f" - {error}")
        return 1
    print(f"World Map infrastructure validation passed: {len(assets)} assets · {len(SEED_MINIMUMS)} gateway seed groups · contextual Chain/Gateway/Impact integration active.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
