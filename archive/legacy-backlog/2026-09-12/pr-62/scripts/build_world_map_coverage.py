#!/usr/bin/env python3
"""Derive World Map coverage from actual canonical content rather than stored counters."""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "countries" / "index.json"
COUNTRIES = ROOT / "data" / "countries"
ENTITIES = ROOT / "data" / "world-map-entities.json"
CHAINS = ROOT / "data" / "world-system-chains.json"
GATEWAYS = ROOT / "data" / "world-map-gateways.json"
OUT = ROOT / "data" / "world-map-coverage-ledger.json"

DOMAIN_PATHS = {
    "strategic_geography": ("deepening", "layers", "strategic_geography"),
    "energy": ("energy_and_resources",),
    "logistics": ("deepening", "layers", "logistics_graph"),
    "trade": ("trade_and_value_chains",),
    "digital": ("deepening", "layers", "digital_sovereignty"),
    "dependencies": ("deepening", "layers", "dependency_graph"),
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _meaningful(value) -> bool:
    if value is None or value == "":
        return False
    if isinstance(value, dict):
        return any(_meaningful(v) for v in value.values())
    if isinstance(value, (list, tuple, set)):
        return any(_meaningful(v) for v in value)
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
            if key in {"source", "source_url", "sources"}:
                if isinstance(child, str) and child.strip():
                    found.add(child.strip())
                elif isinstance(child, list):
                    for row in child:
                        if isinstance(row, str) and row.strip():
                            found.add(row.strip())
            _collect_sources(child, found)
    elif isinstance(value, list):
        for child in value:
            _collect_sources(child, found)


def derive_record_coverage(record: dict) -> dict:
    observations = record.get("observations") if isinstance(record.get("observations"), dict) else {}
    observation_count = sum(1 for row in observations.values() if _meaningful(row))
    relationships = record.get("relationships") if isinstance(record.get("relationships"), list) else []
    relationship_count = sum(1 for row in relationships if _meaningful(row))
    sources: set[str] = set()
    _collect_sources(record, sources)

    domains = {}
    for domain, path in DOMAIN_PATHS.items():
        value = _nested(record, path)
        if not _meaningful(value):
            domains[domain] = "missing"
        elif isinstance(value, dict) and any(not _meaningful(v) for v in value.values()):
            domains[domain] = "partial"
        else:
            domains[domain] = "represented"

    return {
        "observations": {"represented": observation_count, "state": "represented" if observation_count else "missing"},
        "relationships": {"represented": relationship_count, "state": "represented" if relationship_count else "missing"},
        "provenance": {"source_records": len(sources), "state": "represented" if sources else "missing"},
        "domains": domains,
    }


def audit_country_owners(index_rows: list[dict], country_files: list[Path]) -> dict:
    canonical_by_code = {str(row.get("iso3") or "").upper(): row.get("id") for row in index_rows}
    files_by_code: dict[str, list[str]] = defaultdict(list)
    identity_mismatches = []
    for path in country_files:
        try:
            data = load(path)
        except Exception:
            continue
        identity = data.get("identity") if isinstance(data.get("identity"), dict) else {}
        code = str(identity.get("iso3") or data.get("iso3") or "").upper()
        if code:
            files_by_code[code].append(path.name)
            canonical_id = canonical_by_code.get(code)
            record_id = identity.get("id") or data.get("country_id")
            if canonical_id and record_id and record_id != canonical_id:
                identity_mismatches.append({"iso3": code, "file": path.name, "canonical_id": canonical_id, "record_id": record_id})
    duplicates = {code: sorted(paths) for code, paths in files_by_code.items() if code in canonical_by_code and len(paths) > 1}
    return {"duplicates": duplicates, "identity_mismatches": identity_mismatches}


def build_coverage_ledger() -> dict:
    index = load(INDEX)
    rows = index.get("countries", [])
    if len(rows) != 195:
        raise RuntimeError(f"expected canonical 195-country index; found {len(rows)}")
    entities = load(ENTITIES).get("entities", {})
    chains = load(CHAINS).get("chains", {})
    gateways = load(GATEWAYS).get("gateways", {})

    owner_audit = audit_country_owners(rows, list(COUNTRIES.glob("*.json")))
    result = {}
    for row in rows:
        code = row["iso3"]
        record = load(COUNTRIES / f"{row['id']}.json")
        coverage = derive_record_coverage(record)
        chain_ids = sorted(cid for cid, chain in chains.items() if code in (chain.get("members") or []))
        gateway_ids = sorted(gid for gid, gateway in gateways.items() if code in (gateway.get("countries") or []))
        reasons = []
        if code in owner_audit["duplicates"]:
            reasons.append("integrity defect")
        if gateway_ids:
            reasons.append("gateway adjacency")
        if len(chain_ids) >= 2:
            reasons.append("multi-chain connector")
        if any(coverage["domains"].get(d) == "missing" for d in ("dependencies", "logistics", "digital", "energy")):
            reasons.append("missing dependency/infrastructure domains")
        if not reasons:
            reasons.append("general descriptive gaps")
        result[code] = {
            "id": row["id"],
            "name": row.get("name"),
            **coverage,
            "systems": {"chains": chain_ids, "gateways": gateway_ids},
            "priority_reasons": reasons,
            "quality_flags": ["duplicate-iso3-record"] if code in owner_audit["duplicates"] else [],
        }

    for code, entity in entities.items():
        if entity.get("render_status") != "current":
            continue
        result[code] = {
            "id": entity.get("id"),
            "name": entity.get("name"),
            "canonical_country": False,
            "observations": {"represented": int(bool(entity.get("population"))) + int(bool(entity.get("area"))), "state": "represented" if entity.get("population") or entity.get("area") else "missing"},
            "relationships": {"represented": len(entity.get("relationships") or []), "state": "represented" if entity.get("relationships") else "missing"},
            "provenance": {"source_records": int(bool(entity.get("population", {}).get("source"))) + int(bool(entity.get("area", {}).get("source"))), "state": "represented"},
            "domains": {"strategic_geography": "partial", "energy": "unknown", "logistics": "unknown", "trade": "unknown", "digital": "unknown", "dependencies": "unknown"},
            "systems": {"chains": sorted(cid for cid, chain in chains.items() if code in (chain.get("members") or [])), "gateways": sorted(gid for gid, gateway in gateways.items() if code in (gateway.get("countries") or []))},
            "priority_reasons": ["registered non-country entity"],
            "quality_flags": [],
        }

    return {
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy": {"country_count": 195, "missing_is_zero": False, "ranking_is_operational_not_geopolitical": True},
        "owner_audit": owner_audit,
        "entities": result,
    }


def build_coverage_file(path: Path = OUT) -> dict:
    payload = build_coverage_ledger()
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    payload = build_coverage_file()
    print(json.dumps({"entities": len(payload["entities"]), "duplicates": payload["owner_audit"]["duplicates"], "output": str(OUT.relative_to(ROOT))}, indent=2))
