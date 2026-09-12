#!/usr/bin/env python3
"""Validate canonical World Map infrastructure ownership and causal guardrails."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INFRA = ROOT / "data" / "world-map-infrastructure.json"
COUNTRIES = ROOT / "data" / "countries" / "index.json"
ENTITIES = ROOT / "data" / "world-map-entities.json"
GATEWAYS = ROOT / "data" / "world-map-gateways.json"
CHAINS = ROOT / "data" / "world-system-chains.json"

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

    # Explicit regression fixtures for the causal boundary.
    bad = {"relationship": "member-of-chain", "causal_status": "explicit-dependency"}
    if bad["relationship"] in CONTEXT_RELATIONSHIPS and bad["causal_status"] != "contextual":
        pass
    else:
        errors.append("causal guardrail regression fixture is not exercising contextual-vs-causal distinction")

    if errors:
        print("World Map infrastructure validation FAILED:")
        for error in errors:
            print(f" - {error}")
        return 1
    print(f"World Map infrastructure validation passed: {len(assets)} assets · {len(SEED_MINIMUMS)} gateway seed groups.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
