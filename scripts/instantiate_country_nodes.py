#!/usr/bin/env python3
"""Instantiate one backend country record for every country in the canonical index.

This is intentionally conservative: it creates real graph nodes with identity,
blueprint inheritance, research coverage, provenance slots and relationship hooks.
It never invents observations. Later source adapters fill observations into the
same files while preserving the scaffold and history.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data/countries/index.json"
BLUEPRINT = ROOT / "data/countries-blueprint.json"
OUT = ROOT / "data/countries"


def load(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    index = load(INDEX)
    blueprint = load(BLUEPRINT)
    countries = index["countries"]
    now = datetime.now(timezone.utc).isoformat()
    blueprint_version = blueprint.get("version", "unknown")

    created = 0
    preserved = 0
    for c in countries:
        path = OUT / f"{c['id']}.json"
        existing = None
        if path.exists():
            try:
                existing = load(path)
            except Exception:
                existing = None
        if existing:
            existing.setdefault("blueprint", index["blueprint"])
            existing.setdefault("blueprint_version", blueprint_version)
            existing.setdefault("identity", {"id": c["id"], "name": c["name"], "iso2": c["iso2"], "iso3": c["iso3"]})
            existing.setdefault("coverage", {})
            existing["coverage"].setdefault("node_instantiated", True)
            existing["coverage"]["blueprint_inherited"] = True
            existing.setdefault("relationships", [])
            existing.setdefault("history", [])
            path.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            preserved += 1
            continue

        record = {
            "record_version": "1.0.0",
            "record_type": "country",
            "status": "instantiated",
            "identity": {
                "id": c["id"],
                "name": c["name"],
                "iso2": c["iso2"],
                "iso3": c["iso3"]
            },
            "blueprint": index["blueprint"],
            "blueprint_version": blueprint_version,
            "coverage": {
                "node_instantiated": True,
                "blueprint_inherited": True,
                "observations": 0,
                "relationships": 0,
                "sources": 0,
                "research_status": "ready-for-source-enrichment"
            },
            "observations": {},
            "relationships": [],
            "history": [],
            "research_queue": [
                "national statistical office",
                "constitution and legal framework",
                "head of state and government",
                "parliament and electoral system",
                "religious composition and denominations",
                "historical timeline",
                "public finance and debt",
                "trade and value chains",
                "energy and natural resources",
                "infrastructure",
                "health and education",
                "labour and migration",
                "military and public security institutions",
                "science and technology",
                "media and digital systems",
                "international memberships and treaties",
                "ownership and major institutions"
            ],
            "provenance": {
                "instantiated_at": now,
                "instantiation_method": "canonical country index + country blueprint",
                "observation_policy": "No value is invented merely to fill a field; absent evidence remains missing/stale."
            }
        }
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        created += 1

    state = {
        "generated_at": now,
        "canonical_scope": index["scope"],
        "countries_seen": len(countries),
        "nodes_created": created,
        "nodes_preserved": preserved,
        "blueprint": index["blueprint"],
        "rule": "Instantiation creates the graph node; source adapters are responsible for empirical enrichment."
    }
    (OUT / "instantiation-state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(state, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
