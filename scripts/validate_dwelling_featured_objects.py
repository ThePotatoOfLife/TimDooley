#!/usr/bin/env python3
"""Validate curated featured-object shelves for every active top-level Dwelling."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ROOMS=ROOT/"data/house/rooms.json"
SHELVES=ROOT/"data/house/dwelling-featured-objects.json"

def main()->int:
    errors=[]
    rooms=json.loads(ROOMS.read_text(encoding="utf-8"))
    data=json.loads(SHELVES.read_text(encoding="utf-8"))
    active={r["id"] for r in rooms.get("rooms",[]) if r.get("status")=="active"}
    rows={r.get("dwelling_id"):r for r in data.get("shelves",[]) if isinstance(r,dict) and r.get("dwelling_id")}
    missing=sorted(active-set(rows))
    extra=sorted(set(rows)-active)
    if missing: errors.append("active Dwellings missing featured-object shelves: "+", ".join(missing))
    if extra: errors.append("unknown/inactive Dwelling shelves: "+", ".join(extra))
    for rid in sorted(active & set(rows)):
        row=rows[rid]
        objects=row.get("objects") or []
        if len(objects)<4:
            errors.append(f"{rid}: expected at least 4 featured objects, found {len(objects)}")
        seen=set()
        for obj in objects:
            title=str(obj.get("title") or "").strip()
            href=str(obj.get("href") or "").strip()
            if not title: errors.append(f"{rid}: featured object missing title")
            if not href:
                errors.append(f"{rid}: {title or '<untitled>'} missing href")
                continue
            if href in seen: errors.append(f"{rid}: duplicate featured href {href}")
            seen.add(href)
            if href.startswith(("http://","https://","#")): continue
            target=ROOT/href.lstrip("/")
            if target.is_dir(): target=target/"index.html"
            if not target.exists():
                errors.append(f"{rid}: featured target does not exist: {href}")
    if errors:
        print("DWELLING FEATURED-OBJECT VALIDATION FAILED")
        for e in errors: print("-",e)
        return 1
    print(f"Dwelling featured objects: PASS · {len(active)} active Dwellings covered")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
