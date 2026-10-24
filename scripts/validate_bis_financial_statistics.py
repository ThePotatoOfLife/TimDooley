#!/usr/bin/env python3
"""Validate BIS banking and bond data foundation."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/"data"/"bis-banking-bond-data.json"
FINANCE=ROOT/"data"/"world-financial-system-foundation.json"
REGISTRY=ROOT/"data"/"world-map-layer-registry.json"

def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))

def main() -> int:
    d=load(PATH)
    assert d["id"]=="bis-banking-bond-data"
    assert d["status"]=="active-foundation"
    assert set(d["release_metadata"])=={"lbs","cbs","dss","ids"}
    assert d["release_metadata"]["lbs"]["latest_reference_period"]=="2026-Q1"
    assert d["release_metadata"]["cbs"]["latest_reference_period"]=="2026-Q1"
    assert d["release_metadata"]["dss"]["latest_reference_period"]=="2026-Q1"
    assert d["release_metadata"]["ids"]["latest_reference_period"]=="2026-Q2"

    sem=d["dataset_semantics"]
    assert "residence" in sem["lbs"]["basis"]
    assert "unconsolidated" in sem["lbs"]["consolidation"]
    assert "nationality" in sem["cbs"]["basis"]
    assert "intragroup positions excluded" in sem["cbs"]["consolidation"]
    assert "holder" in sem["ids"]["holder_limitation"].lower()

    obs={x["observation_id"]:x for x in d["latest_global_observations"]}
    required={
        "bis-lbs-cross-border-claims-2026q1",
        "bis-lbs-cross-border-liabilities-2026q1",
        "bis-cbs-foreign-claims-2026q1",
        "bis-ids-outstanding-2026q2",
    }
    assert required <= set(obs)
    assert obs["bis-lbs-cross-border-claims-2026q1"]["value"]==47621.926
    assert obs["bis-cbs-foreign-claims-2026q1"]["value"]==43383.0
    assert obs["bis-ids-outstanding-2026q2"]["value"]==35096.3

    source_ids={x["id"] for x in d["source_layers"]}
    for x in d["latest_global_observations"]:
        assert x["source_id"] in source_ids
        assert x["reference_period"]
        assert x["unit"]
        assert x["evidence_status"].startswith("sourced")

    raws={x["dataset"]:x["url"] for x in d["ingestion_contract"]["raw_sources"]}
    assert set(raws)=={"LBS","CBS","DSS","IDS"}
    assert all(url.startswith("https://data.bis.org/static/bulk/") for url in raws.values())

    finance=load(FINANCE)
    assert finance.get("bis_data_foundation")=="data/bis-banking-bond-data.json"

    registry=load(REGISTRY)
    ids={x["id"] for x in registry["entries"]}
    for required_id in (
        "finance.bis-lbs",
        "finance.bis-cbs",
        "finance.bis-dss",
        "finance.bis-ids",
    ):
        assert required_id in ids, f"missing registry entry {required_id}"

    print("BIS banking and bond foundation: PASS")
    print(f"  observations: {len(d['latest_global_observations'])}")
    print(f"  datasets: {', '.join(d['release_metadata'])}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
