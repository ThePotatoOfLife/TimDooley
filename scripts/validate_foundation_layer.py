#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FILES={
    "timeline":ROOT/"data/house/foundation-timeline-wave-001.json",
    "blueprint":ROOT/"data/blueprints/foundation-blueprint.json",
    "registry":ROOT/"data/blueprint-registry.json",
    "integration":ROOT/"data/house/foundation-integration-contract.json",
    "surfaces":ROOT/"data/house/public-surfaces.json",
    "topology":ROOT/"knowledge/research/potato-house-master/public-route-topology.json",
}

def load(path:Path):
    return json.loads(path.read_text(encoding="utf-8"))

errors=[]
for name,path in FILES.items():
    if not path.is_file():
        errors.append(f"missing {name}: {path.relative_to(ROOT)}")

if not errors:
    timeline,blueprint,registry,integration,surfaces,topology=(load(FILES[k]) for k in ["timeline","blueprint","registry","integration","surfaces","topology"])
    record_paths=(integration.get("owners") or {}).get("records") or []
    record_docs=[]
    for rel in record_paths:
        path=ROOT/rel
        if not path.is_file():
            errors.append(f"Integration contract references missing Foundation record owner {rel}")
            continue
        record_docs.append(load(path))
    records=[r for doc in record_docs for r in (doc.get("records") or [])]
    ids=[r.get("id") for r in records]
    if any(not x for x in ids): errors.append("Foundation record missing id")
    if len(ids)!=len(set(ids)): errors.append("Duplicate Foundation IDs")

    allowed_events=set(blueprint.get("record_schema",{}).get("clocks",[]))
    required_clock_fields=set(blueprint.get("record_schema",{}).get("clocks_contract",[]))
    for r in records:
        clocks=r.get("clocks") or []
        if not clocks: errors.append(f"{r.get('id')}: no foundation clocks")
        if not (r.get("reproduction_mechanism") or r.get("foundation_rules") or r.get("load_bearing_rules")):
            errors.append(f"{r.get('id')}: missing reproduction/rule payload")
        for i,c in enumerate(clocks):
            missing=[k for k in ("date_or_range","event_type","precision","status","label","source") if k not in c]
            if missing: errors.append(f"{r.get('id')} clock[{i}] missing {', '.join(missing)}")
            if allowed_events and c.get("event_type") not in allowed_events:
                errors.append(f"{r.get('id')} clock[{i}] unknown event_type {c.get('event_type')}")
            if "year_start" not in c: errors.append(f"{r.get('id')} clock[{i}] missing year_start")

    event_keys=set()
    known=set(ids)
    for e in timeline.get("events") or []:
        fid=e.get("foundation_id")
        if fid not in known: errors.append(f"Timeline references unknown Foundation {fid}")
        key=(fid,e.get("date_or_range"),e.get("event_type"))
        if key in event_keys: errors.append(f"Duplicate timeline event {key}")
        event_keys.add(key)

    expected={(r.get("id"),c.get("date_or_range"),c.get("event_type")) for r in records for c in (r.get("clocks") or [])}
    missing=sorted(expected-event_keys)
    if missing: errors.append(f"Timeline missing {len(missing)} Foundation clock(s)")

    bp=next((x for x in registry.get("blueprints") or [] if x.get("id")=="foundation"),None)
    if not bp or bp.get("file")!="data/blueprints/foundation-blueprint.json":
        errors.append("Blueprint registry missing canonical Foundation blueprint")

    surf=next((x for x in surfaces.get("surfaces") or [] if x.get("id")=="foundation-timeline"),None)
    if not surf or surf.get("canonical_route")!="/timeline/foundations/":
        errors.append("Foundation Timeline public surface missing/drifted")
    topo=next((x for x in topology.get("records") or [] if x.get("surface_id")=="foundation-timeline"),None)
    if not topo or topo.get("canonical_route")!="/timeline/foundations/":
        errors.append("Foundation Timeline route topology missing/drifted")

    owners=integration.get("owners") or {}
    for k in ("ontology","reproduction","schema","records","timeline","canonical_map","graph_bridge"):
        if k not in owners: errors.append(f"Integration contract missing owner {k}")

if errors:
    print("Foundation layer validation FAILED")
    for e in errors: print(" -",e)
    raise SystemExit(1)
print("Foundation layer validation OK")
