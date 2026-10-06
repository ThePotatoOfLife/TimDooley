#!/usr/bin/env python3
"""Validate recent-work integration ledger against live House registries and repository paths."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/"data/house/recent-work-integration-ledger.json"

def load(p): return json.loads(p.read_text(encoding="utf-8"))

def route_source_exists(route:str)->bool:
    if route.startswith(("http://","https://")): return True
    base=route.split("#",1)[0].split("?",1)[0]
    if base.startswith("/records/"): return True
    if base=="/": return (ROOT/"index.html").exists()
    rel=base.lstrip("/")
    p=ROOT/rel
    if base.endswith(".html"): return p.exists()
    return (p/"index.html").exists()

def main():
    errors=[]
    data=load(LEDGER)
    rooms=load(ROOT/"data/house/subrooms.json").get("subrooms",[])
    room_ids={x.get("id") for x in rooms if isinstance(x,dict)}
    surfaces=load(ROOT/"data/house/public-surfaces.json").get("surfaces",[])
    surface_ids={x.get("id") for x in surfaces if isinstance(x,dict)}
    inhabitants=load(ROOT/"data/house/room-inhabitants.json").get("inhabitants",[])
    object_ids={x.get("id") for x in inhabitants if isinstance(x,dict)}
    ids=[]
    for row in data.get("workstreams",[]):
        if not isinstance(row,dict): continue
        wid=row.get("id")
        ids.append(wid)
        if not wid or not row.get("title") or not row.get("status"):
            errors.append(f"integration row missing id/title/status: {wid}")
        for p in row.get("canonical_owners",[]):
            if not (ROOT/p).exists():
                errors.append(f"{wid} missing canonical owner path: {p}")
        for rid in row.get("room_ids",[]):
            if rid not in room_ids:
                errors.append(f"{wid} unknown Room: {rid}")
        for sid in row.get("public_surface_ids",[]):
            if sid not in surface_ids:
                errors.append(f"{wid} unknown public surface: {sid}")
        for oid in row.get("house_object_ids",[]):
            if oid not in object_ids:
                errors.append(f"{wid} unknown House object: {oid}")
        for p in row.get("validation",[]):
            if not (ROOT/p).exists():
                errors.append(f"{wid} missing validator/path: {p}")
        for route in row.get("routes",[]):
            if not route_source_exists(route):
                errors.append(f"{wid} route has no source/generated target: {route}")
    if len(ids)!=len(set(ids)):
        errors.append("recent-work integration ids must be unique")
    if errors:
        print("RECENT WORK INTEGRATION VALIDATION FAILED")
        for e in errors: print("-",e)
        return 1
    print(f"RECENT WORK INTEGRATION VALIDATION PASSED: {len(ids)} workstreams mapped through ownership / Rooms / surfaces / validation")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
