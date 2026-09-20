#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LINEAGES=ROOT/"data/religious-foundation-lineages.json"
TIMELINE=ROOT/"data/religious-foundation-timeline.json"
GEOGRAPHY=ROOT/"data/religious-foundation-geography.json"
EVENTS=ROOT/"data/religious-foundation-events.json"

def load(path:Path):
    return json.loads(path.read_text(encoding="utf-8"))

errors=[]
for p in (LINEAGES,TIMELINE,GEOGRAPHY,EVENTS):
    if not p.is_file():
        errors.append(f"missing {p.relative_to(ROOT)}")

if not errors:
    a,t,g,e=map(load,(LINEAGES,TIMELINE,GEOGRAPHY,EVENTS))
    node_types=set((a.get("node_types") or {}).keys())
    edge_types=set((a.get("edge_types") or {}).keys())
    source_ids=set((a.get("source_registry") or {}).keys())
    nodes={}
    for fam in a.get("families") or []:
        for n in fam.get("nodes") or []:
            nid=n.get("id")
            if not nid: errors.append(f"{fam.get('id')}: node missing id"); continue
            if nid in nodes: errors.append(f"duplicate religious lineage node {nid}")
            nodes[nid]=n
            if n.get("node_type") not in node_types:
                errors.append(f"{nid}: unknown node_type {n.get('node_type')}")
            rel=n.get("relation_to_parent")
            if rel and rel not in edge_types:
                errors.append(f"{nid}: unknown relation_to_parent {rel}")
            clock=n.get("seed_clock") or {}
            for k in ("year_start","date_or_range","precision","status"):
                if k not in clock: errors.append(f"{nid}: seed_clock missing {k}")
            ys,ye=clock.get("year_start"),clock.get("year_end")
            if isinstance(ys,(int,float)) and isinstance(ye,(int,float)) and ye<ys:
                errors.append(f"{nid}: year_end precedes year_start")
            if not (n.get("origin") or {}).get("place"):
                errors.append(f"{nid}: missing origin place/distributed marker")
            for sid in n.get("sources") or []:
                if sid not in source_ids: errors.append(f"{nid}: unknown source id {sid}")

    for nid,n in nodes.items():
        for pid in n.get("parent_ids") or []:
            if pid not in nodes:
                errors.append(f"{nid}: unknown parent {pid}")

    # cycle detection on lineage parent edges
    visiting=set(); visited=set()
    def visit(nid,stack):
        if nid in visiting:
            errors.append("cycle in religious lineage: "+" -> ".join(stack+[nid])); return
        if nid in visited: return
        visiting.add(nid)
        for pid in nodes[nid].get("parent_ids") or []:
            if pid in nodes: visit(pid,stack+[nid])
        visiting.remove(nid); visited.add(nid)
    for nid in nodes: visit(nid,[])

    tev=t.get("events") or []
    tids=[e.get("node_id") for e in tev]
    if len(tids)!=len(set(tids)): errors.append("duplicate node_id in religious foundation timeline")
    if set(tids)!=set(nodes):
        errors.append(f"timeline node set drift: missing={sorted(set(nodes)-set(tids))[:10]} extra={sorted(set(tids)-set(nodes))[:10]}")
    known_events={x.get("id") for x in e.get("events") or []}
    for nid,n in nodes.items():
        for ev in n.get("event_anchors") or []:
            if ev.get("event_id") not in known_events:
                errors.append(f"{nid}: unknown event anchor {ev.get('event_id')}")
    gav=g.get("anchors") or []
    gids=[e.get("node_id") for e in gav]
    if len(gids)!=len(set(gids)): errors.append("duplicate node_id in religious foundation geography")
    if set(gids)!=set(nodes):
        errors.append(f"geography node set drift: missing={sorted(set(nodes)-set(gids))[:10]} extra={sorted(set(gids)-set(nodes))[:10]}")

if errors:
    print("Religious foundation lineage validation FAILED")
    for e in errors: print(" -",e)
    raise SystemExit(1)
print(f"Religious foundation lineage validation OK ({len(nodes)} nodes)")
