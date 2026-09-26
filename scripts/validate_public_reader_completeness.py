#!/usr/bin/env python3
"""Validate the major public reader surfaces against the completeness contract."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"data/house/public-reader-completeness.json"
DWELLINGS=ROOT/"data/house/rooms.json"
SHELVES=ROOT/"data/house/dwelling-featured-objects.json"
JOURNEY=ROOT/"app/house-journey.js"

def has(path: Path, *needles: str) -> bool:
    text=path.read_text(encoding="utf-8",errors="replace")
    return all(n in text for n in needles)

def main()->int:
    errors=[]
    contract=json.loads(CONTRACT.read_text(encoding="utf-8"))
    if contract.get("version")!="1.0.0":
        errors.append("unexpected public reader completeness contract version")

    checks=[
      (ROOT/"index.html",["What is actually here","project-substance"]),
      (ROOT/"rooms/index.html",["Dwellings & Rooms"]),
      (ROOT/"house/index.html",["holdings-grid","interface-list"]),
      (ROOT/"explore/index.html",["Do not start with the archive. Start with a question.","Example journeys through the archive"]),
    ]
    for path,needles in checks:
        if not path.is_file():
            errors.append(f"missing reader surface: {path.relative_to(ROOT)}")
            continue
        if not has(path,*needles):
            errors.append(f"reader surface lost required substance markers: {path.relative_to(ROOT)}")

    js=JOURNEY.read_text(encoding="utf-8",errors="replace")
    for fn in ("installRoomsBestOf","installDwellingFeaturedObjects"):
        if fn not in js:
            errors.append(f"house journey lost reader completeness function: {fn}")

    rooms=json.loads(DWELLINGS.read_text(encoding="utf-8"))
    shelves=json.loads(SHELVES.read_text(encoding="utf-8"))
    shelf_ids={row.get("dwelling_id") for row in shelves.get("shelves",[]) if isinstance(row,dict)}
    for room in rooms.get("rooms",[]):
        if room.get("status")!="active": continue
        rid=room["id"]
        path=ROOT/"rooms"/rid/"index.html"
        if not path.is_file():
            errors.append(f"missing active Dwelling page: rooms/{rid}/index.html")
            continue
        text=path.read_text(encoding="utf-8",errors="replace")
        if "dwelling-reader" not in text:
            errors.append(f"{rid}: Dwelling lost substantive synthesis section")
        if "Epistemic rule" not in text:
            errors.append(f"{rid}: Dwelling lost epistemic boundary")
        if rid not in shelf_ids:
            errors.append(f"{rid}: Dwelling missing curated object shelf")

    if errors:
        print("PUBLIC READER COMPLETENESS VALIDATION FAILED")
        for e in errors: print("-",e)
        return 1
    print("Public reader completeness: PASS · home, Rooms, House, Explore and all active Dwellings retain their distinct reader jobs")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
