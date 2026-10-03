#!/usr/bin/env python3
"""Validate financial institution gap-closure topology."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TOPO=ROOT/"data"/"world-financial-institution-topology.json"
FINANCE=ROOT/"data"/"world-financial-system-foundation.json"
REGISTRY=ROOT/"data"/"world-map-layer-registry.json"

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    d=load(TOPO)
    assert d["id"]=="world-financial-institution-topology"
    assert d["status"]=="active-gap-closure"
    layer_ids={x["id"] for x in d["layers"]}
    required_layers={
        "holder-side-data",
        "official-liquidity-and-multilateral-finance",
        "market-infrastructure",
        "rules-supervision-resolution",
        "identity-and-ownership",
        "large-nonbank-capital-pools",
    }
    assert required_layers <= layer_ids

    nodes={}
    for layer in d["layers"]:
        for node in layer.get("nodes",[]):
            nid=node["id"]
            assert nid not in nodes, f"duplicate node {nid}"
            nodes[nid]=node

    for required in ("imf-pip","imf","ibrd","eib","nib","ebrd","swift","cls","euroclear","clearstream","fsb","bcbs","cpmi","gleif","gpfg-nbim","atp"):
        assert required in nodes, f"missing critical topology node {required}"

    source_ids={x["id"] for x in d["sources"]}
    for node in nodes.values():
        refs=[]
        if node.get("source_id"): refs.append(node["source_id"])
        refs.extend(node.get("source_ids",[]))
        for ref in refs:
            assert ref in source_ids, f"{node['id']} references unknown source {ref}"

    assert "Messaging is not settlement" in d["design_rule"]
    assert "custody" in d["design_rule"].lower()
    assert "beneficial ownership" in d["design_rule"].lower()

    finance=load(FINANCE)
    assert finance.get("institution_topology")=="data/world-financial-institution-topology.json"

    registry=load(REGISTRY)
    ids={x["id"] for x in registry["entries"]}
    for required in (
        "finance.multilateral-lenders",
        "finance.market-infrastructure",
        "finance.regulatory-standards",
        "finance.institutional-investors",
        "relation.portfolio-holdings",
        "relation.multilateral-finance",
    ):
        assert required in ids, f"missing map registry entry {required}"

    print("Financial institution topology: PASS")
    print(f"  layers: {len(d['layers'])}")
    print(f"  nodes: {len(nodes)}")
    print(f"  sources: {len(d['sources'])}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
