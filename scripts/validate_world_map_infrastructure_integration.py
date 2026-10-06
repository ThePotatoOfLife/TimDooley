#!/usr/bin/env python3
"""Cross-module contract for World Map infrastructure investigation integration."""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_BUILDER = ROOT / "scripts" / "build_world_map_runtime.py"
ENTITY_RUNTIME = ROOT / "world-map" / "3d-entity-runtime.js"
CHAIN = ROOT / "world-map" / "3d-chain-explorer.js"
GATEWAYS = ROOT / "world-map" / "3d-gateways.js"
IMPACT = ROOT / "world-map" / "3d-impact-trace.js"
INFRA = ROOT / "world-map" / "3d-infrastructure.js"


def read(path: Path) -> str:
    if not path.is_file():
        raise AssertionError(f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8", errors="replace")


def runtime() -> dict:
    spec = importlib.util.spec_from_file_location("world_map_runtime_integration_validation", RUNTIME_BUILDER)
    assert spec and spec.loader, "could not load runtime builder"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_runtime()


def main() -> int:
    errors: list[str] = []
    try:
        data = runtime()
    except Exception as exc:
        print("World Map infrastructure integration validation FAILED:")
        print(f" - runtime build failed: {exc}")
        return 1

    plane = data.get("infrastructure") or {}
    assets = plane.get("assets") or {}
    impact = data.get("impact") or {}
    nodes = impact.get("nodes") or {}
    edges = impact.get("edges") or []

    # Canonical reverse lookups must already support Chain and Gateway context.
    for chain_id, asset_ids in (plane.get("by_chain") or {}).items():
        unresolved = sorted(set(asset_ids) - set(assets))
        if unresolved:
            errors.append(f"by_chain.{chain_id} has unresolved infrastructure ids: {unresolved}")
    for gateway_id, asset_ids in (plane.get("by_gateway") or {}).items():
        unresolved = sorted(set(asset_ids) - set(assets))
        if unresolved:
            errors.append(f"by_gateway.{gateway_id} has unresolved infrastructure ids: {unresolved}")

    # Every infrastructure asset is a textual Impact node, but contextual association
    # alone must never generate an explicit dependency edge.
    for asset_id in assets:
        node_id = f"infrastructure:{asset_id}"
        if node_id not in nodes:
            errors.append(f"Impact graph missing infrastructure node {node_id}")
    contextual_only = {
        asset_id for asset_id, asset in assets.items()
        if (asset.get("relationships") or [])
        and all((row.get("causal_status") in {None, "contextual"}) for row in (asset.get("relationships") or []))
    }
    for asset_id in contextual_only:
        node_id = f"infrastructure:{asset_id}"
        if any(edge.get("source") == node_id and edge.get("causal_status") == "explicit-dependency" for edge in edges):
            errors.append(f"context-only infrastructure asset {asset_id} became an explicit dependency")

    entity_runtime = read(ENTITY_RUNTIME)
    for marker in ("impactNodeForInfrastructure", "infrastructureForChain", "infrastructureForGateway"):
        if marker not in entity_runtime:
            errors.append(f"shared runtime missing integration API marker: {marker}")

    chain = read(CHAIN)
    for marker in ("infrastructureForChain", "Infrastructure", "data-infrastructure-id"):
        if marker not in chain:
            errors.append(f"chain explorer missing linked-infrastructure marker: {marker}")

    gateways = read(GATEWAYS)
    for marker in ("infrastructureForGateway", "potato-atlas-gateway-change", "data-gateway-infrastructure-id"):
        if marker not in gateways:
            errors.append(f"gateway surface missing linked-infrastructure marker: {marker}")

    infra = read(INFRA)
    for marker in ("impactNodeForInfrastructure", "showImpact", "data-infrastructure-impact"):
        if marker not in infra:
            errors.append(f"infrastructure browser missing Impact integration marker: {marker}")
    if re.search(r"const\s+nodeId\s*=\s*`infrastructure:\$\{", infra):
        errors.append("infrastructure browser must use shared impactNodeForInfrastructure() instead of guessing node ids")

    impact_js = read(IMPACT)
    for marker in ("function nodeCode", "rowsHtml", "result.root.label"):
        if marker not in impact_js:
            errors.append(f"Impact presentation missing non-polygon-safe marker: {marker}")
    if "['country','territory'].includes(node?.kind)" not in impact_js:
        errors.append("Impact highlighting must remain polygon-only for country/territory nodes")

    if errors:
        print("World Map infrastructure integration validation FAILED:")
        for error in errors:
            print(f" - {error}")
        return 1

    print("World Map infrastructure integration validation passed: Chain/Gateway context, shared Impact lookup and causal guardrails are coherent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
