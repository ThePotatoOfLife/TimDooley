#!/usr/bin/env python3
"""Validate the canonical World Finance Foundation."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOUNDATION = ROOT / "data" / "world-financial-system-foundation.json"
BLUEPRINT = ROOT / "data" / "blueprints" / "finance-debt-blueprint.json"
AXIS = ROOT / "data" / "world-axis-fields.json"

REQUIRED_CENTRAL_BANKS = {
    "federal-reserve",
    "ecb-eurosystem",
    "danmarks-nationalbank",
}
REQUIRED_CONCEPTS = {
    "general-government-gross-debt",
    "central-government-debt",
    "debt-held-by-public",
    "cross-border-bank-claim",
    "official-reserve-assets",
}
REQUIRED_SOURCES = {
    "fed-who-we-are",
    "ecb-escb-eurosystem",
    "dnb-exchange-rates",
    "eurostat-government-debt",
    "bis-debt-securities",
    "imf-cofer-dataset",
    "us-treasury-tic",
    "ec-eu-funding-plan-2026",
}

def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def unique_ids(rows: list[dict], label: str) -> set[str]:
    ids = [row.get("id") for row in rows]
    assert all(ids), f"{label}: every row needs id"
    assert len(ids) == len(set(ids)), f"{label}: duplicate ids"
    return set(ids)

def main() -> int:
    data = load(FOUNDATION)
    assert data["id"] == "world-financial-system-foundation"
    assert data["status"] == "active-foundation"
    assert data["updated"] == "2026-09-20"

    boundary = data.get("boundary", "").casefold()
    for token in ("empirical", "axis", "sovereignty", "legal authority"):
        assert token in boundary, f"foundation boundary must disclose {token!r}"

    cb_ids = unique_ids(data["central_banks"], "central_banks")
    assert REQUIRED_CENTRAL_BANKS <= cb_ids

    concept_ids = unique_ids(data["debt_concepts"], "debt_concepts")
    assert REQUIRED_CONCEPTS <= concept_ids

    source_ids = unique_ids(data["source_layers"], "source_layers")
    assert REQUIRED_SOURCES <= source_ids

    currencies = {row["id"]: row for row in data["currency_systems"]}
    assert {"USD", "EUR", "DKK"} <= set(currencies)
    eur_members = currencies["EUR"]["member_jurisdiction_iso3"]
    assert len(eur_members) == 21
    assert "BGR" in eur_members
    dkk_anchor = currencies["DKK"]["exchange_rate_anchor"]
    assert dkk_anchor["anchor_currency"] == "EUR"
    assert dkk_anchor["central_rate_dkk_per_eur"] == 7.46038

    source_refs = set()
    for section in (
        "central_banks",
        "currency_systems",
        "sovereign_and_supranational_issuers",
        "settlement_and_infrastructure",
    ):
        for row in data.get(section, []):
            source_refs.update(row.get("source_ids", []))
    for obs in data["observations"]:
        assert obs.get("concept_id") in concept_ids, f"unknown concept in {obs.get('id')}"
        assert obs.get("unit"), f"missing unit in {obs.get('id')}"
        assert obs.get("reference_period"), f"missing reference period in {obs.get('id')}"
        assert obs.get("source_id") in source_ids, f"unknown source in {obs.get('id')}"
        assert obs.get("evidence_status") == "sourced", f"seed observation must be sourced: {obs.get('id')}"
        source_refs.add(obs["source_id"])
    missing_source_refs = source_refs - source_ids
    assert not missing_source_refs, f"unregistered source ids: {sorted(missing_source_refs)}"

    levels = [row["level"] for row in data["creditor_resolution"]]
    assert levels == [1, 2, 3, 4, 5]
    tic_rows = [
        row for row in data["observations"]
        if row.get("concept_id") == "custody-reported-us-treasury-holdings"
    ]
    assert tic_rows and all(row.get("creditor_resolution_level") == 3 for row in tic_rows)

    bridge = data["north_axis_bridge"]
    assert bridge["axis_source"] == "data/world-axis-fields.json"
    assert "project" in bridge["mode"]
    assert "sovereignty" in bridge["boundary"].casefold() or "politically controlled" in bridge["boundary"].casefold()
    assert AXIS.exists()

    blueprint = load(BLUEPRINT)
    assert blueprint.get("canonical_foundation") == "data/world-financial-system-foundation.json"
    assert "custodies_for" in blueprint["record_schema"]["relationships"]
    assert "currency_area" in blueprint["record_schema"]["monetary_system"]

    print("World Finance Foundation: PASS")
    print(f"  central banks: {len(data['central_banks'])}")
    print(f"  currencies: {len(data['currency_systems'])}")
    print(f"  debt concepts: {len(data['debt_concepts'])}")
    print(f"  seed observations: {len(data['observations'])}")
    print(f"  sources: {len(data['source_layers'])}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
