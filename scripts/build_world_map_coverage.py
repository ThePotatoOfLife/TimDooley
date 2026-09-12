#!/usr/bin/env python3
"""Derive World Map coverage from actual canonical content.

The coverage ledger is a maintenance/investigation aid, not a geopolitical score.
It measures what the repository currently represents, keeps missing evidence
explicit, and explains why a record may deserve enrichment.
"""
from __future__ import annotations

import importlib.util
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "countries" / "index.json"
COUNTRIES = ROOT / "data" / "countries"
ENTITIES = ROOT / "data" / "world-map-entities.json"
CHAINS = ROOT / "data" / "world-system-chains.json"
GATEWAYS = ROOT / "data" / "world-map-gateways.json"
INFRASTRUCTURE = ROOT / "data" / "world-map-infrastructure.json"
RUNTIME_BUILDER = ROOT / "scripts" / "build_world_map_runtime.py"
OUT = ROOT / "data" / "world-map-coverage-ledger.json"

VALID_STATES = {"represented", "partial", "missing", "unknown", "pending-source", "not-applicable"}
DOMAIN_PATHS = {
    "strategic_geography": [
        ("deepening", "layers", "strategic_geography"),
        ("geography",),
    ],
    "ports_logistics": [
        ("deepening", "layers", "logistics_graph"),
        ("transport_and_logistics",),
        ("ports_and_logistics",),
    ],
    "energy_resources_grid": [
        ("energy_and_resources",),
        ("deepening", "layers", "energy"),
    ],
    "trade_value_chains": [
        ("trade_and_value_chains",),
        ("deepening", "layers", "trade"),
    ],
    "digital_technology": [
        ("technology_and_digital",),
        ("deepening", "layers", "digital_sovereignty"),
    ],
    "infrastructure": [
        ("infrastructure",),
        ("deepening", "layers", "infrastructure"),
        ("deepening", "layers", "logistics_graph"),
    ],
}


def load(path: Path, default=None):
    if not path.is_file():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def _meaningful(value) -> bool:
    if value is None or value == "":
        return False
    if isinstance(value, dict):
        return any(_meaningful(child) for child in value.values())
    if isinstance(value, (list, tuple, set)):
        return any(_meaningful(child) for child in value)
    return True


def _nested(record: dict, path: tuple[str, ...]):
    value = record
    for key in path:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def _collect_sources(value, found: set[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"source", "source_url"} and isinstance(child, str) and child.strip():
                found.add(child.strip())
            elif key == "sources":
                if isinstance(child, str) and child.strip():
                    found.add(child.strip())
                elif isinstance(child, list):
                    for row in child:
                        if isinstance(row, str) and row.strip():
                            found.add(row.strip())
                        elif isinstance(row, dict):
                            _collect_sources(row, found)
            _collect_sources(child, found)
    elif isinstance(value, list):
        for child in value:
            _collect_sources(child, found)


def _period(value) -> str | None:
    if not isinstance(value, dict):
        return None
    for key in ("period", "reference_period", "year", "date", "as_of", "retrieved"):
        candidate = value.get(key)
        if candidate not in (None, ""):
            return str(candidate)
    return None


def _observation_freshness(observations: dict) -> dict:
    dated = 0
    undated = 0
    periods: list[str] = []
    for row in observations.values():
        if not _meaningful(row):
            continue
        period = _period(row)
        if period:
            dated += 1
            periods.append(period)
        else:
            undated += 1
    return {
        "dated": dated,
        "undated": undated,
        "period_min": min(periods) if periods else None,
        "period_max": max(periods) if periods else None,
        "state": "represented" if dated else ("partial" if undated else "missing"),
    }


def _domain_state(record: dict, paths: list[tuple[str, ...]]) -> str:
    values = [_nested(record, path) for path in paths]
    meaningful = [value for value in values if _meaningful(value)]
    if not meaningful:
        return "missing"
    for value in meaningful:
        if isinstance(value, dict) and value:
            present = sum(1 for child in value.values() if _meaningful(child))
            if 0 < present < len(value):
                return "partial"
    return "represented"


def derive_record_coverage(record: dict) -> dict:
    observations = record.get("observations") if isinstance(record.get("observations"), dict) else {}
    observation_count = sum(1 for row in observations.values() if _meaningful(row))
    relationships = record.get("relationships") if isinstance(record.get("relationships"), list) else []
    relationship_count = sum(1 for row in relationships if _meaningful(row))
    sources: set[str] = set()
    _collect_sources(record, sources)
    domains = {name: _domain_state(record, paths) for name, paths in DOMAIN_PATHS.items()}
    return {
        "observations": {
            "represented": observation_count,
            "state": "represented" if observation_count else "missing",
        },
        "freshness": _observation_freshness(observations),
        "relationships": {
            "represented": relationship_count,
            "state": "represented" if relationship_count else "missing",
        },
        "provenance": {
            "source_records": len(sources),
            "state": "represented" if sources else "missing",
        },
        "domains": domains,
    }


def audit_country_owners(index_rows: list[dict], country_files: list[Path]) -> dict:
    canonical_by_code = {str(row.get("iso3") or "").upper(): row.get("id") for row in index_rows}
    files_by_code: dict[str, list[str]] = defaultdict(list)
    identity_mismatches = []
    for path in country_files:
        if path.name == "index.json":
            continue
        try:
            data = load(path)
        except Exception:
            continue
        identity = data.get("identity") if isinstance(data.get("identity"), dict) else {}
        code = str(identity.get("iso3") or data.get("iso3") or "").upper()
        if not code:
            continue
        files_by_code[code].append(path.name)
        canonical_id = canonical_by_code.get(code)
        record_id = identity.get("id") or data.get("country_id")
        if canonical_id and record_id and record_id != canonical_id:
            identity_mismatches.append({
                "iso3": code,
                "file": path.name,
                "canonical_id": canonical_id,
                "record_id": record_id,
            })
    duplicates = {
        code: sorted(paths)
        for code, paths in files_by_code.items()
        if len(paths) > 1
    }
    return {
        "duplicate_iso3": duplicates,
        "duplicates": duplicates,
        "identity_mismatches": sorted(identity_mismatches, key=lambda row: (row["iso3"], row["file"])),
    }


def _load_runtime() -> dict:
    spec = importlib.util.spec_from_file_location("world_map_runtime_for_coverage", RUNTIME_BUILDER)
    if not spec or not spec.loader:
        raise RuntimeError("could not load scripts/build_world_map_runtime.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "build_runtime"):
        raise RuntimeError("World Map runtime builder must expose build_runtime()")
    return module.build_runtime()


def _groups_for(code: str, runtime: dict) -> list[str]:
    return sorted(
        group_id for group_id, group in (runtime.get("groups") or {}).items()
        if code in (group.get("members") or [])
    )


def _impact_for(code: str, canonical_country: bool, runtime: dict) -> dict:
    impact = runtime.get("impact") or {}
    nodes = impact.get("nodes") or {}
    edges = impact.get("edges") or []
    node_id = f"{'country' if canonical_country else 'territory'}:{code}"
    present = node_id in nodes
    incoming = [edge for edge in edges if edge.get("target") == node_id]
    outgoing = [edge for edge in edges if edge.get("source") == node_id]
    unresolved = 0
    for edge in outgoing:
        target = nodes.get(edge.get("target"), {})
        if target.get("kind") == "dependency-concept":
            unresolved += 1
    represented = len(incoming) + len(outgoing)
    return {
        "node": present,
        "represented_edges": represented,
        "incoming": len(incoming),
        "outgoing": len(outgoing),
        "unresolved_dependency_concepts": unresolved,
        "state": "represented" if present and represented else ("partial" if present else "missing"),
    }


def _asset_indexes(infrastructure: dict) -> tuple[dict[str, list[str]], dict[str, list[str]], dict[str, list[str]]]:
    by_entity: dict[str, list[str]] = defaultdict(list)
    by_gateway: dict[str, list[str]] = defaultdict(list)
    by_chain: dict[str, list[str]] = defaultdict(list)
    for asset_id, asset in (infrastructure.get("assets") or {}).items():
        for code in asset.get("countries", []) or []:
            by_entity[str(code).upper()].append(asset_id)
        for gateway_id in asset.get("gateway_ids", []) or []:
            by_gateway[str(gateway_id)].append(asset_id)
        for chain_id in asset.get("chain_ids", []) or []:
            by_chain[str(chain_id)].append(asset_id)
    return (
        {key: sorted(set(value)) for key, value in by_entity.items()},
        {key: sorted(set(value)) for key, value in by_gateway.items()},
        {key: sorted(set(value)) for key, value in by_chain.items()},
    )


def _system_context(code: str, runtime: dict) -> dict:
    country = (runtime.get("countries") or {}).get(code, {})
    systems = country.get("systems") or {}
    return {
        "capabilities": list(systems.get("capabilities") or []),
        "dependencies": list(systems.get("dependencies") or []),
        "builds": list(systems.get("builds") or []),
        "chains": list(systems.get("chains") or []),
        "gateways": list(systems.get("gateways") or []),
        "regional": list(systems.get("regional") or []),
    }


def _priority_reasons(*, quality_flags: list[str], gateway_ids: list[str], chain_ids: list[str], impact: dict, domains: dict) -> list[str]:
    reasons: list[str] = []
    if quality_flags:
        reasons.append("integrity defect")
    sparse_infrastructure = domains.get("infrastructure") in {"missing", "unknown", "partial"}
    if gateway_ids and sparse_infrastructure:
        reasons.append("gateway/infrastructure hinge with sparse data")
    if len(chain_ids) >= 2 and domains.get("energy_resources_grid") in {"missing", "unknown"}:
        reasons.append("multi-chain connector with missing dependencies")
    if impact.get("unresolved_dependency_concepts", 0):
        reasons.append("Impact node with unresolved concepts")
    if any(domains.get(name) in {"missing", "unknown"} for name in ("ports_logistics", "digital_technology", "infrastructure")):
        reasons.append("infrastructure domain gap")
    if not reasons:
        reasons.append("general descriptive gap")
    return reasons


def _source_revision(*sources: dict) -> str:
    dates = []
    for source in sources:
        value = source.get("updated") if isinstance(source, dict) else None
        if isinstance(value, str) and value.strip():
            dates.append(value.strip())
    return max(dates) if dates else "2026-09-12"


def build_coverage_ledger() -> dict:
    index = load(INDEX)
    rows = index.get("countries", [])
    if len(rows) != 195:
        raise RuntimeError(f"expected canonical 195-country index; found {len(rows)}")
    entity_source = load(ENTITIES)
    chain_source = load(CHAINS)
    gateway_source = load(GATEWAYS)
    infrastructure_source = load(INFRASTRUCTURE, {})
    entities = entity_source.get("entities", {})
    chains = chain_source.get("chains", {})
    gateways = gateway_source.get("gateways", {})
    runtime = _load_runtime()
    infra_by_entity, _, _ = _asset_indexes(infrastructure_source)

    owner_audit = audit_country_owners(rows, list(COUNTRIES.glob("*.json")))
    duplicate_codes = set(owner_audit.get("duplicate_iso3") or {})
    result: dict[str, dict] = {}

    for row in rows:
        code = str(row["iso3"]).upper()
        record = load(COUNTRIES / f"{row['id']}.json")
        coverage = derive_record_coverage(record)
        systems = _system_context(code, runtime)
        chain_ids = systems["chains"] or sorted(cid for cid, chain in chains.items() if code in (chain.get("members") or []))
        gateway_ids = systems["gateways"] or sorted(gid for gid, gateway in gateways.items() if code in (gateway.get("countries") or []))
        infrastructure_ids = infra_by_entity.get(code, [])
        if infrastructure_ids:
            coverage["domains"]["infrastructure"] = "represented"
            if coverage["domains"].get("ports_logistics") == "missing":
                coverage["domains"]["ports_logistics"] = "partial"
        impact = _impact_for(code, True, runtime)
        quality_flags = ["duplicate-iso3-record"] if code in duplicate_codes else []
        result[code] = {
            "id": row["id"],
            "name": row.get("name"),
            "canonical_country": True,
            **coverage,
            "institutions": {
                "memberships": _groups_for(code, runtime),
                "state": "represented" if _groups_for(code, runtime) else "missing",
            },
            "capabilities": {"represented": len(systems["capabilities"]), "state": "represented" if systems["capabilities"] else "missing"},
            "dependencies": {"represented": len(systems["dependencies"]), "state": "represented" if systems["dependencies"] else "missing"},
            "builds": {"represented": len(systems["builds"]), "state": "represented" if systems["builds"] else "missing"},
            "systems": {
                "chains": chain_ids,
                "gateways": gateway_ids,
                "regional": systems["regional"],
                "infrastructure": infrastructure_ids,
            },
            "impact": impact,
            "priority_reasons": _priority_reasons(
                quality_flags=quality_flags,
                gateway_ids=gateway_ids,
                chain_ids=chain_ids,
                impact=impact,
                domains=coverage["domains"],
            ),
            "quality_flags": quality_flags,
        }

    for code, entity in entities.items():
        code = str(code).upper()
        if entity.get("render_status") != "current":
            continue
        entity_record = dict(entity)
        pseudo_observations = {}
        if entity.get("population"):
            pseudo_observations["population"] = entity.get("population")
        if entity.get("area"):
            pseudo_observations["area"] = entity.get("area")
        entity_record["observations"] = pseudo_observations
        coverage = derive_record_coverage(entity_record)
        chain_ids = sorted(cid for cid, chain in chains.items() if code in (chain.get("members") or []))
        gateway_ids = sorted(gid for gid, gateway in gateways.items() if code in (gateway.get("countries") or []))
        infrastructure_ids = infra_by_entity.get(code, [])
        if infrastructure_ids:
            coverage["domains"]["infrastructure"] = "represented"
        impact = _impact_for(code, False, runtime)
        result[code] = {
            "id": entity.get("id"),
            "name": entity.get("name"),
            "canonical_country": False,
            **coverage,
            "institutions": {"memberships": _groups_for(code, runtime), "state": "represented" if _groups_for(code, runtime) else "unknown"},
            "capabilities": {"represented": 0, "state": "unknown"},
            "dependencies": {"represented": 0, "state": "unknown"},
            "builds": {"represented": 0, "state": "unknown"},
            "systems": {"chains": chain_ids, "gateways": gateway_ids, "regional": [], "infrastructure": infrastructure_ids},
            "impact": impact,
            "priority_reasons": ["registered non-country entity"],
            "quality_flags": [],
        }

    return {
        "version": "1.1.0",
        "generated_at": _source_revision(entity_source, chain_source, gateway_source, infrastructure_source),
        "purpose": "Descriptive coverage of what the current World Map repository actually represents; not a geopolitical or completion score.",
        "policy": {
            "country_count": 195,
            "missing_is_zero": False,
            "ranking_is_operational_not_geopolitical": True,
            "aggregate_score": "forbidden",
            "state_vocabulary": sorted(VALID_STATES),
        },
        "owner_audit": owner_audit,
        "entities": result,
    }


def build_coverage_file(path: Path = OUT) -> dict:
    payload = build_coverage_ledger()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    payload = build_coverage_file()
    canonical = sum(1 for row in payload["entities"].values() if row.get("canonical_country") is True)
    non_country = len(payload["entities"]) - canonical
    print(json.dumps({
        "countries": canonical,
        "registered_non_country_entities": non_country,
        "duplicates": payload["owner_audit"]["duplicate_iso3"],
        "output": str(OUT.relative_to(ROOT)),
    }, indent=2))
