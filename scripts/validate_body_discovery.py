#!/usr/bin/env python3
"""Validate that canonical Life & Body knowledge remains discoverable across project surfaces."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load(rel):
    p=ROOT/rel
    if not p.exists():
        raise SystemExit(f"BODY DISCOVERY ERROR: missing {rel}")
    return json.loads(p.read_text(encoding="utf-8"))

def fail(msg):
    raise SystemExit(f"BODY DISCOVERY ERROR: {msg}")

def main():
    core=load("knowledge/indexes/core-index.json")
    manifest=load("manifest.json")
    body_index=load("knowledge/body/index.json")
    overlay=load("data/house/body-relational-overlay.json")
    inhabitants=load("data/house/room-inhabitants.json")
    subrooms=load("data/house/subrooms.json")
    holdings=load("data/house/holdings.json")
    source=load("knowledge/indexes/source-index.json")

    required={
      "vertebral-33-room-atlas":"knowledge/body/vertebral-33-room-atlas.json",
      "spinal-cord-microcircuit-atlas":"knowledge/body/spinal-cord-microcircuit-atlas.json",
      "cranial-brainstem-room-atlas":"knowledge/body/cranial-brainstem-room-atlas.json",
      "brain-room-deep-atlas":"knowledge/body/brain-room-deep-atlas.json",
      "neural-development-lineage-atlas":"knowledge/body/neural-development-lineage-atlas.json",
      "glia-neurovascular-barrier-atlas":"knowledge/body/glia-neurovascular-barrier-atlas.json",
      "cortical-celltype-parcellation-atlas":"knowledge/body/cortical-celltype-parcellation-atlas.json",
    }
    core_by_id={r.get("id"):r for r in core.get("records",[]) if isinstance(r,dict)}
    body_branch=next((b for b in manifest.get("branches",[]) if b.get("id")=="body"),None)
    if not body_branch: fail("manifest BODY branch missing")
    reading={r.get("path") for r in body_index.get("reading_order",[]) if isinstance(r,dict)}
    source_routes=set(source.get("canonical_source_routes",{}).get("body",[]))
    for rid,path in required.items():
        if not (ROOT/path).exists(): fail(f"canonical atlas missing: {path}")
        if core_by_id.get(rid,{}).get("path")!=path: fail(f"{rid} missing/misrouted in core-index")
        if path not in body_branch.get("records",[]): fail(f"{path} missing from manifest BODY branch")
        if path not in reading: fail(f"{path} missing from BODY reading order")
        if path not in source_routes: fail(f"{path} missing from BODY source routes")

    objects=overlay.get("objects",[])
    ids=[x.get("id") for x in objects if isinstance(x,dict)]
    if len(ids)!=len(set(ids)): fail("duplicate body-relational-overlay object IDs")
    for obj in objects:
        if not isinstance(obj,dict): continue
        if not obj.get("body_route","").startswith("/"): fail(f"{obj.get('id')} lacks absolute public body route")
        for owner in obj.get("canonical_owners",[]):
            if not (ROOT/owner).exists(): fail(f"{obj.get('id')} references missing owner {owner}")
        if not obj.get("room_ids"): fail(f"{obj.get('id')} has no Room lenses")
        if not obj.get("lens_tags"): fail(f"{obj.get('id')} has no typed lenses")

    inhabitant_ids={x.get("id") for x in inhabitants.get("inhabitants",[]) if isinstance(x,dict)}
    required_inhabitants={"body-thalamus-house","body-pineal-door","body-spinal-ladder","body-csf-river","body-neural-development","body-neurovascular-unit","body-cortical-celltypes"}
    missing=required_inhabitants-inhabitant_ids
    if missing: fail("House inhabitants missing: "+", ".join(sorted(missing)))

    room_by={x.get("id"):x for x in subrooms.get("subrooms",[]) if isinstance(x,dict)}
    for room in ("neurobiology","whole-body","symbolic-body-comparison"):
        if room not in room_by: fail(f"Life & Body nested Room missing: {room}")
    holding_by={x.get("room_id"):x for x in holdings.get("holdings",[]) if isinstance(x,dict)}
    for room in ("neurobiology","whole-body","symbolic-body-comparison"):
        if room not in holding_by: fail(f"House holdings missing for {room}")
        if holding_by[room].get("primary_file_count",0)<3: fail(f"{room} holdings unexpectedly thin")

    page=(ROOT/"life-body/index.html").read_text(encoding="utf-8")
    for needle in ("vertebral-33-room-atlas.json","brain-room-deep-atlas.json","id=\"cellular-depth\"","id=\"bodyFinder\"","body-relational-overlay.json"):
        if needle not in page: fail(f"Life & Body public page missing {needle}")

    app=(ROOT/"app/app.js").read_text(encoding="utf-8")
    if "(?:data|knowledge)" not in app or "registrySearch" not in app:
        fail("Explore does not expose knowledge-root record search")

    journey=(ROOT/"app/house-journey.js").read_text(encoding="utf-8")
    if "installRoomKnowledge" not in journey or "data/house/holdings.json" not in journey:
        fail("nested Room runtime does not expose live holdings/current routes")

    build=(ROOT/"scripts/build_discovery.py").read_text(encoding="utf-8")
    for needle in ("def core_records()","def body_objects()","record-discovery-index.json","body-discovery-index.json"):
        if needle not in build: fail(f"discovery builder missing {needle}")

    print(f"BODY discovery validation passed: {len(required)} core atlases, {len(objects)} overlay objects, cross-root Explore search and public discovery routes are wired.")

if __name__=="__main__":
    main()
