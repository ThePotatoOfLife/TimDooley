#!/usr/bin/env python3
"""Validate canonical knowledge reachability through governed Room/House integration."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DRAWERS=ROOT/"data/house/room-archive-drawers.json"
INHABITANTS=ROOT/"data/house/room-inhabitants.json"
DOSSIERS=ROOT/"data/house/room-dossiers.json"
SHELVES=ROOT/"data/house/dwelling-featured-objects.json"
COVERAGE=ROOT/"data/house/corpus-surface-coverage.json"

SUFFIXES={".json",".md"}

def main()->int:
    errors=[]
    drawers=json.loads(DRAWERS.read_text(encoding="utf-8"))
    inhabitants=json.loads(INHABITANTS.read_text(encoding="utf-8"))
    dossiers=json.loads(DOSSIERS.read_text(encoding="utf-8"))
    shelves=json.loads(SHELVES.read_text(encoding="utf-8"))
    coverage=json.loads(COVERAGE.read_text(encoding="utf-8"))

    canonical=sorted(
        str(p.relative_to(ROOT))
        for p in (ROOT/"knowledge").rglob("*")
        if p.is_file() and p.suffix.lower() in SUFFIXES
    )
    canonical_set=set(canonical)
    reached=set()

    for row in drawers.get("drawers",[]):
        prefix=str(row.get("scope_prefix") or "")
        if prefix:
            reached.update(p for p in canonical if p.startswith(prefix))

    for row in inhabitants.get("inhabitants",[]):
        route=str(row.get("route") or "")
        if route.startswith("/knowledge/"):
            reached.add(route.lstrip("/").split("#",1)[0].split("?",1)[0])

    for room in dossiers.get("dossiers",[]):
        for item in ((room.get("knowledge_holdings") or {}).get("featured") or []):
            path=str(item.get("path") or "")
            if path.startswith("knowledge/"):
                reached.add(path)

    for shelf in shelves.get("shelves",[]):
        for item in shelf.get("objects",[]):
            href=str(item.get("href") or "")
            if href.startswith("knowledge/"):
                reached.add(href.split("#",1)[0].split("?",1)[0])

    reached={p for p in reached if p in canonical_set}

    exclusions=coverage.get("intentionally_excluded") or []
    excluded=set()
    for row in exclusions:
        prefix=str(row.get("prefix") or "")
        if not prefix:
            errors.append("coverage exclusion missing prefix")
            continue
        members={p for p in canonical if p.startswith(prefix)}
        excluded.update(members)
        declared=row.get("record_count")
        if declared!=len(members):
            errors.append(f"coverage exclusion {prefix} declares {declared} records but live corpus has {len(members)}")

    current=canonical_set-excluded
    missing=sorted(current-reached)
    if missing:
        errors.append("current canonical records are unreachable: "+", ".join(missing[:25])+(f" (+{len(missing)-25} more)" if len(missing)>25 else ""))

    totals=coverage.get("totals") or {}
    expected={
        "canonical_knowledge_records":len(canonical_set),
        "reachable_records":len(reached),
        "current_non_retired_records":len(current),
        "current_non_retired_reachable":len(current & reached),
        "intentionally_retired_unreachable":len(excluded-reached),
    }
    for key,value in expected.items():
        if totals.get(key)!=value:
            errors.append(f"coverage total drift: {key}={totals.get(key)} but live value is {value}")

    drawer_total=sum(int(row.get("record_count") or 0) for row in drawers.get("drawers",[]))
    structure=coverage.get("current_structure") or {}
    if structure.get("deep_archive_drawers")!=len(drawers.get("drawers",[])):
        errors.append("deep_archive_drawers count drift")
    if structure.get("records_covered_by_drawer_prefixes")!=len({p for p in canonical if any(p.startswith(str(row.get("scope_prefix") or "")) for row in drawers.get("drawers",[]))}):
        errors.append("records_covered_by_drawer_prefixes drift")
    if drawer_total < structure.get("records_covered_by_drawer_prefixes",0):
        errors.append("drawer declared record totals cannot be smaller than unique drawer-prefix coverage")

    if errors:
        print("CORPUS SURFACE COVERAGE VALIDATION FAILED")
        for e in errors: print("-",e)
        return 1

    print(f"Corpus reachability: PASS · {len(current & reached)}/{len(current)} current records reachable; {len(excluded-reached)} retired records intentionally outside current surfaces")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
