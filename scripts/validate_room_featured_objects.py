#!/usr/bin/env python3
"""Validate editorial featured-object selections for nested Rooms."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FEATURED=ROOT/"data/house/room-featured-objects.json"
INHABITANTS=ROOT/"data/house/room-inhabitants.json"
SUBROOMS=ROOT/"data/house/subrooms.json"

def main()->int:
    errors=[]
    feat=json.loads(FEATURED.read_text(encoding="utf-8"))
    inhab=json.loads(INHABITANTS.read_text(encoding="utf-8"))
    subs=json.loads(SUBROOMS.read_text(encoding="utf-8"))
    rooms={r.get("id") for r in subs.get("subrooms",[]) if isinstance(r,dict)}
    by_id={r.get("id"):r for r in inhab.get("inhabitants",[]) if isinstance(r,dict)}
    active_rooms={r.get("id") for r in subs.get("subrooms",[]) if isinstance(r,dict) and r.get("status")=="active"}
    seen_rooms=set()

    for row in feat.get("rooms",[]):
        rid=row.get("room_id")
        if rid not in rooms:
            errors.append(f"featured selection references unknown Room: {rid}")
            continue
        if rid in seen_rooms:
            errors.append(f"duplicate featured selection block for Room: {rid}")
        seen_rooms.add(rid)
        ids=row.get("object_ids") or []
        if not (3 <= len(ids) <= 6):
            errors.append(f"{rid}: expected 3-6 featured objects, found {len(ids)}")
        if len(ids)!=len(set(ids)):
            errors.append(f"{rid}: duplicate object ids in featured set")
        for oid in ids:
            obj=by_id.get(oid)
            if not obj:
                errors.append(f"{rid}: featured object does not exist: {oid}")
                continue
            if rid not in (obj.get("room_ids") or []):
                errors.append(f"{rid}: featured object is not placed in this Room: {oid}")
            if not str(obj.get("summary") or "").strip():
                errors.append(f"{rid}: featured object lacks summary: {oid}")
            if not str(obj.get("route") or "").strip():
                errors.append(f"{rid}: featured object lacks direct route: {oid}")

    missing=sorted(active_rooms-seen_rooms)
    if missing:
        errors.append("active Rooms missing editorial featured sets: "+", ".join(missing))

    if errors:
        print("ROOM FEATURED OBJECT VALIDATION FAILED")
        for e in errors: print("-",e)
        return 1
    print(f"Room featured objects: PASS · {len(seen_rooms)}/{len(active_rooms)} active Rooms curated")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
