#!/usr/bin/env python3
"""Validate deep archive drawers against the live canonical corpus."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DRAWERS=ROOT/"data/house/room-archive-drawers.json"
SUBROOMS=ROOT/"data/house/subrooms.json"

def resolve(route: str) -> bool:
    clean=route.lstrip("/").split("#",1)[0].split("?",1)[0]
    target=ROOT/clean
    if target.is_dir():
        target=target/"index.html"
    return target.exists()

def main()->int:
    errors=[]
    data=json.loads(DRAWERS.read_text(encoding="utf-8"))
    sub=json.loads(SUBROOMS.read_text(encoding="utf-8"))
    room_ids={r.get("id") for r in sub.get("subrooms",[]) if isinstance(r,dict)}
    seen=set()
    for row in data.get("drawers",[]):
        did=row.get("id")
        if not did:
            errors.append("drawer missing id"); continue
        if did in seen: errors.append(f"duplicate drawer id: {did}")
        seen.add(did)
        prefix=str(row.get("scope_prefix") or "")
        if not prefix.startswith("knowledge/") or not prefix.endswith("/"):
            errors.append(f"{did}: invalid scope_prefix {prefix!r}")
            continue
        actual=[p for p in (ROOT/prefix).glob("*") if p.is_file() and p.suffix.lower() in {".json",".md"}]
        declared=row.get("record_count")
        if declared!=len(actual):
            errors.append(f"{did}: record_count={declared} but live top-level corpus count is {len(actual)} under {prefix}")
        rooms=row.get("room_ids") or []
        if not rooms: errors.append(f"{did}: no Room placements")
        for rid in rooms:
            if rid not in room_ids: errors.append(f"{did}: unknown Room {rid}")
        landing=str(row.get("landing_href") or "")
        if landing and not landing.startswith(("http://","https://","#")) and not resolve(landing):
            errors.append(f"{did}: landing target missing: {landing}")
        entries=row.get("entries") or []
        if len(entries)<3:
            errors.append(f"{did}: expected at least 3 representative entries")
        entry_seen=set()
        for entry in entries:
            path=str(entry.get("path") or "")
            if not path:
                errors.append(f"{did}: representative entry missing path"); continue
            if path in entry_seen: errors.append(f"{did}: duplicate representative entry {path}")
            entry_seen.add(path)
            if not (ROOT/path).is_file():
                errors.append(f"{did}: representative record missing: {path}")
            if prefix and not path.startswith(prefix):
                errors.append(f"{did}: representative record outside declared corpus prefix: {path}")
        if not str(row.get("summary") or "").strip(): errors.append(f"{did}: missing summary")
        if not str(row.get("boundary") or "").strip(): errors.append(f"{did}: missing boundary")
    if errors:
        print("ROOM ARCHIVE DRAWER VALIDATION FAILED")
        for e in errors: print("-",e)
        return 1
    print(f"Room archive drawers: PASS · {len(seen)} deep corpora integrated")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
