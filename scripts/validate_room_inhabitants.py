#!/usr/bin/env python3
"""Validate Room inhabitants as concrete, openable reader objects."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SUBROOMS=ROOT/"data/house/subrooms.json"
INHABITANTS=ROOT/"data/house/room-inhabitants.json"

def main()->int:
    errors=[]
    subs=json.loads(SUBROOMS.read_text(encoding="utf-8"))
    data=json.loads(INHABITANTS.read_text(encoding="utf-8"))
    room_ids={r.get("id") for r in subs.get("subrooms",[]) if isinstance(r,dict) and r.get("id")}
    seen=set()
    per_room={rid:0 for rid in room_ids}
    for row in data.get("inhabitants",[]):
        if not isinstance(row,dict): continue
        iid=row.get("id")
        if not iid: errors.append("inhabitant missing id"); continue
        if iid in seen: errors.append(f"duplicate inhabitant id: {iid}")
        seen.add(iid)
        rooms=row.get("room_ids") or []
        if not rooms: errors.append(f"{iid}: no Room placement")
        for rid in rooms:
            if rid not in room_ids:
                errors.append(f"{iid}: unknown Room {rid}")
            else:
                per_room[rid]+=1
        route=str(row.get("route") or "").strip()
        if not route:
            errors.append(f"{iid}: no openable route")
        elif not route.startswith(("http://","https://","#")):
            target=ROOT/route.lstrip("/")
            if target.is_dir(): target=target/"index.html"
            # Hash/query portions may point into a real page.
            if not target.exists():
                clean=route.lstrip("/").split("#",1)[0].split("?",1)[0]
                target=ROOT/clean
                if target.is_dir(): target=target/"index.html"
            if not target.exists():
                errors.append(f"{iid}: route target does not exist: {route}")
        if not str(row.get("summary") or "").strip():
            errors.append(f"{iid}: missing reader summary")
        if not str(row.get("status_note") or "").strip():
            errors.append(f"{iid}: missing status boundary")
    empty=sorted(rid for rid,count in per_room.items() if count==0)
    if empty:
        errors.append("inhabited Rooms without any concrete object: "+", ".join(empty))
    if errors:
        print("ROOM INHABITANT VALIDATION FAILED")
        for e in errors: print("-",e)
        return 1
    print(f"Room inhabitants: PASS · {len(seen)} objects; all {len(room_ids)} Rooms have concrete contents")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
