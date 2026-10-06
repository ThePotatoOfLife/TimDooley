#!/usr/bin/env python3
"""Ensure every country in the canonical index has one substantive node file.

This creates only missing records. Reusable schema lives in the country blueprint;
country files are for actual identity, observations, relationships, history,
research queues and provenance. It never creates per-country null scaffolds.
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
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    index = load(INDEX)
    blueprint = load(BLUEPRINT)
    countries = index["countries"]
    now = datetime.now(timezone.utc).isoformat()
    blueprint_version = blueprint.get("version", "unknown")
    created = 0

    for c in countries:
        path = OUT / f"{c['id']}.json"
        if path.exists():
            continue
        record = {
            "record_version": "1.1.0",
            "record_type": "country",
            "status": "instantiated",
            "identity": {"id": c["id"], "name": c["name"], "iso2": c["iso2"], "iso3": c["iso3"]},
            "blueprint": index["blueprint"],
            "blueprint_version": blueprint_version,
            "coverage": {"node_instantiated": True, "blueprint_inherited": True, "observations": 0, "relationships": 0, "sources": 0, "research_status": "ready-for-source-enrichment"},
            "observations": {},
            "relationships": [],
            "history": [],
            "research_queue": [
                "national statistical office", "constitution and legal framework", "head of state and government",
                "parliament and electoral system", "religious composition and denominations", "historical timeline",
                "public finance and debt", "trade and value chains", "energy and natural resources", "infrastructure",
                "health and education", "labour and migration", "military and public security institutions",
                "science and technology", "media and digital systems", "international memberships and treaties",
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

    print(json.dumps({"countries_seen": len(countries), "nodes_created": created}, ensure_ascii=False))


if __name__ == "__main__":
    main()
