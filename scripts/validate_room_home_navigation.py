#!/usr/bin/env python3
"""Validate top-level Room home navigation after universal elevator rollout."""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ROOMS=ROOT/"data"/"house"/"rooms.json"
EXPECTED_PRIMARY_LABELS={
    "potatoverse-canon":"Open Religion →",
    "archive-sources":"Open Source Authority →",
    "time-history":"Open Timeline →",
    "traditions-texts":"Open Religion →",
    "science-formal-models":"Open Science →",
    "life-body":"Open Life & Body →",
    "world-systems":"Open World →",
    "culture-information":"Open Culture →",
    "works":"Open Works →",
    "research-lab":"Open Research Lab →",
}

NAV_RE=re.compile(r"<nav\b[^>]*>([\s\S]*?)</nav>",re.I)
LINK_RE=re.compile(r"<a\b[^>]*href=[\"']([^\"']+)[\"'][^>]*>([\s\S]*?)</a>",re.I)
TAG_RE=re.compile(r"<[^>]+>")

def text(fragment:str)->str:
    return re.sub(r"\s+"," ",TAG_RE.sub(" ",fragment)).strip()

def main()->int:
    errors=[]
    data=json.loads(ROOMS.read_text(encoding="utf-8"))
    active=[row for row in data.get("rooms",[]) if isinstance(row,dict) and row.get("status")=="active" and row.get("id")]
    if len(active)!=10:
        errors.append(f"expected 10 active Room homes, got {len(active)}")

    for room in active:
        room_id=room["id"]
        path=ROOT/"rooms"/room_id/"index.html"
        if not path.is_file():
            errors.append(f"{room_id}: missing Room homepage")
            continue
        source=path.read_text(encoding="utf-8",errors="replace")
        nav_match=NAV_RE.search(source)
        if not nav_match:
            errors.append(f"{room_id}: missing first local nav")
            continue
        links=[(href,text(label)) for href,label in LINK_RE.findall(nav_match.group(1))]
        labels=[label for _,label in links]
        if labels!=["All Rooms","House"]:
            errors.append(f"{room_id}: local nav must be exactly All Rooms + House, got {labels}")
        for href,label in links:
            if "elevator" in href.lower() or label.lower().startswith("elevator") or label.lower().startswith("home"):
                errors.append(f"{room_id}: local nav still duplicates universal/global navigation: {label} -> {href}")
        if "Stand inside this Dwelling in the Elevator" in source:
            errors.append(f"{room_id}: repeated 'Stand inside this Dwelling in the Elevator' action must be removed")
        if 'class="room-actions"' not in source:
            errors.append(f"{room_id}: Room actions container missing")
        expected_label=EXPECTED_PRIMARY_LABELS.get(room_id)
        if expected_label and expected_label not in source:
            errors.append(f"{room_id}: primary public action must use reader-facing label {expected_label!r}")
        if "Open primary public surface" in source:
            errors.append(f"{room_id}: internal 'primary public surface' terminology leaked into reader UI")

    if errors:
        print("ROOM HOME NAVIGATION VALIDATION FAILED")
        for error in errors: print("-",error)
        return 1
    print(f"Room home navigation: PASS · {len(active)} Room homes use All Rooms + House and defer elevator movement to the universal header")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
