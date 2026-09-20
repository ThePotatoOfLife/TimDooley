#!/usr/bin/env python3
"""Validate the site-wide reader-richness projection without turning byte size into doctrine."""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data/house/reader-richness-audit.json"
JOURNEY = ROOT / "app/house-journey.js"
INTERIORS = ROOT / "data/house/room-interiors.json"
SUBSTANCE = ROOT / "data/house/substance-first-projection-contract.json"
BUILD = ROOT / "scripts/build_site.py"
SURFACES = ROOT / "data/house/public-surfaces.json"

def plain_text(fragment: str) -> str:
    fragment=re.sub(r"<script\b[\s\S]*?</script>", " ", fragment, flags=re.I)
    fragment=re.sub(r"<style\b[\s\S]*?</style>", " ", fragment, flags=re.I)
    fragment=re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", fragment).strip()

def anchored_section(source: str, section_id: str) -> str:
    match=re.search(
        rf'<section\b[^>]*\bid=["\']{re.escape(section_id)}["\'][^>]*>([\s\S]*?)</section>',
        source,
        flags=re.I,
    )
    return match.group(1) if match else ""

def main() -> int:
    errors=[]
    for path in (AUDIT,JOURNEY,INTERIORS,SUBSTANCE,BUILD,SURFACES):
        if not path.is_file():
            errors.append(f"missing reader-richness owner: {path.relative_to(ROOT)}")
    if errors:
        print("READER RICHNESS VALIDATION FAILED")
        for error in errors: print("-",error)
        return 1

    audit=json.loads(AUDIT.read_text(encoding="utf-8"))
    journey=JOURNEY.read_text(encoding="utf-8",errors="replace")
    interiors=json.loads(INTERIORS.read_text(encoding="utf-8"))
    substance=json.loads(SUBSTANCE.read_text(encoding="utf-8"))
    build=BUILD.read_text(encoding="utf-8",errors="replace")
    surfaces=json.loads(SURFACES.read_text(encoding="utf-8"))

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

    if substance.get("id")!="substance-first-projection-contract":
        errors.append("substance-first projection contract id changed or missing")
    resolution=substance.get("paradox_resolution") or {}
    for key in ("frontend_priority","backend_authority","invisible_bonds","non_constraint","bidirectional_revision","materialization_rule"):
        if not resolution.get(key):
            errors.append(f"substance-first paradox resolution missing {key}")

    floor=((audit.get("thresholds") or {}).get("authored_section_floor") or {}).get("minimum_plain_text_characters",650)
    bindings=substance.get("pages") or []
    if len(bindings)<10:
        errors.append(f"substance-first contract has suspiciously few public page bindings: {len(bindings)}")
    for row in bindings:
        rel=str(row.get("page") or "")
        page=ROOT/rel
        if not page.is_file():
            errors.append(f"substance-bound public page missing: {rel}")
            continue
        source=page.read_text(encoding="utf-8",errors="replace")
        for anchor in row.get("anchors") or []:
            section_id=anchor.get("section_id")
            if section_id and f'id="{section_id}"' not in source and f"id='{section_id}'" not in source:
                errors.append(f"{rel} lost authored substance section #{section_id}")
            elif section_id:
                section=anchored_section(source,section_id)
                mass=len(plain_text(section))
                if mass < floor:
                    errors.append(f"{rel}#{section_id} regressed below authored substance floor: {mass} < {floor} plain-text characters")
            for owner in anchor.get("owner_paths") or []:
                if not (ROOT/owner).is_file():
                    errors.append(f"{rel} substance binding points to missing owner: {owner}")

    for marker_text in ("def inject_substance_bindings()", "data-house-substance-bindings", 'data-substance-policy="substance-first"'):
        if marker_text not in build:
            errors.append(f"build lost substance-first binding hook: {marker_text}")

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

    authored_groups = [
        audit.get("authored_history") or [],
        audit.get("second_authored_wave") or [],
        audit.get("third_authored_wave") or [],
        audit.get("fourth_authored_wave") or [],
    ]
    history=[row for group in authored_groups for row in group]
    seen_authored=set()
    for row in history:
        rel=str(row.get("path") or "")
        if not rel or rel in seen_authored:
            continue
        seen_authored.add(rel)
        path=ROOT/rel
        if not path.is_file():
            errors.append(f"authored richness page missing: {rel}")
            continue
        source=path.read_text(encoding="utf-8",errors="replace")
        mass=len(plain_text(source))
        if mass < 1800:
            errors.append(f"authored richness page regressed to a thin shell: {rel} has {mass} plain-text characters")
        if rel.startswith("rooms/inside/") and 'class="room-essay"' not in source:
            errors.append(f"authored nested Room lost its substantive essay marker: {rel}")
        if re.match(r"^rooms/[^/]+/index\.html$", rel) and rel != "rooms/objects/index.html" and 'class="dwelling-reader"' not in source:
            errors.append(f"authored Dwelling lost its narrative reader marker: {rel}")

    bound_pages={str(row.get("page") or "") for row in bindings}
    surface_rows=[row for row in surfaces.get("surfaces",[]) if isinstance(row,dict)]
    visible=[row for row in surface_rows if row.get("status")=="active" and row.get("visibility") in {"primary","secondary"}]
    for row in visible:
        route=row.get("canonical_route") or row.get("route") or "/"
        rel="index.html" if route=="/" else route.strip("/")+"/index.html"
        page=ROOT/rel
        if not page.is_file():
            errors.append(f"visible public surface missing reader file: {row.get('id')} -> {rel}")
            continue
        # Visible surfaces need substance either through an explicit binding or enough
        # authored page body to be more than a routing shell. This is deliberately
        # qualitative/lightweight and does not impose one layout.
        source=page.read_text(encoding="utf-8",errors="replace")
        mass=len(plain_text(source))
        if rel not in bound_pages and mass < 1800:
            errors.append(f"visible substance coverage too weak: {row.get('id')} has {mass} plain-text characters and no substance binding")

    if errors:
        print("READER RICHNESS VALIDATION FAILED")
        for error in errors: print("-",error)
        return 1
    print(f"Reader richness: PASS · {len(registered)} nested Rooms · {len(seen_authored)} authored pages protected · {len(bindings)} substance-bound public pages · {len(visible)} visible surfaces checked live")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
