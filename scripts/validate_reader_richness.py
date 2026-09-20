#!/usr/bin/env python3
"""Validate the site-wide reader-richness projection without turning byte size into doctrine."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data/house/reader-richness-audit.json"
JOURNEY = ROOT / "app/house-journey.js"
INTERIORS = ROOT / "data/house/room-interiors.json"

def main() -> int:
    errors=[]
    for path in (AUDIT,JOURNEY,INTERIORS):
        if not path.is_file():
            errors.append(f"missing reader-richness owner: {path.relative_to(ROOT)}")
    if errors:
        print("READER RICHNESS VALIDATION FAILED")
        for error in errors: print("-",error)
        return 1

    audit=json.loads(AUDIT.read_text(encoding="utf-8"))
    journey=JOURNEY.read_text(encoding="utf-8",errors="replace")
    interiors=json.loads(INTERIORS.read_text(encoding="utf-8"))

    if audit.get("id")!="reader-richness-audit":
        errors.append("reader richness audit id changed or missing")
    contract=audit.get("quality_contract") or {}
    for key in ("minimum_experience","preferred_editorial_forms","anti_patterns"):
        if not contract.get(key):
            errors.append(f"reader richness quality contract missing {key}")

    for marker in (
        "room-richness",
        "data/house/room-dossiers.json",
        "data/house/holdings.json",
        "data/house/population-pulse.json",
        "The Room behind the doorway",
        "What actually belongs here",
        "Open the actual material",
        "What is still unfinished",
    ):
        if marker not in journey:
            errors.append(f"House journey reader-richness projection missing marker: {marker}")

    registered=[]
    for row in interiors.get("interiors") or interiors.get("rooms") or []:
        route=row.get("route") or ""
        if route.startswith("/rooms/inside/"):
            registered.append(route)
    if len(registered)<30:
        errors.append(f"expected broad nested-Room registry coverage; found {len(registered)} routes")

    missing_shell=[]
    for route in registered:
        rel=route.strip("/")+"/index.html"
        path=ROOT/rel
        if not path.is_file():
            missing_shell.append(rel)
            continue
        source=path.read_text(encoding="utf-8",errors="replace")
        if "app/house-journey.js" not in source:
            errors.append(f"{rel} does not load shared House journey/richness projection")
    if missing_shell:
        errors.append("registered nested Room shells missing: "+", ".join(missing_shell[:10]))

    wave=audit.get("first_authored_wave") or []
    if len(wave)<5:
        errors.append("reader richness audit lost the first authored enrichment wave")
    for row in wave:
        path=ROOT/str(row.get("path") or "")
        if not path.is_file():
            errors.append(f"authored richness page missing: {row.get('path')}")
        elif path.stat().st_size<3000:
            errors.append(f"authored richness page regressed to a thin shell: {row.get('path')}")

    if errors:
        print("READER RICHNESS VALIDATION FAILED")
        for error in errors: print("-",error)
        return 1
    print(f"Reader richness: PASS · {len(registered)} nested Rooms project dossier knowledge · {len(wave)} authored first-wave Rooms")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
