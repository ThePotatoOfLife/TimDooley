#!/usr/bin/env python3
"""Validate the universal fast-access layer in source assets and the built site."""
from __future__ import annotations
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"_site"
errors=[]

def read(path:Path)->str:
    if not path.exists():
        errors.append(f"missing {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8",errors="replace")

js=read(ROOT/"app/site-access.js")
css=read(ROOT/"app/site-access.css")
patch=read(ROOT/"scripts/patch_public_navigation.py")
contract_text=read(ROOT/"data/house/site-access.json")
try:
    contract=json.loads(contract_text) if contract_text else {}
except json.JSONDecodeError as exc:
    errors.append(f"invalid data/house/site-access.json: {exc}")
    contract={}

for token in (
    "Current World","World Map","CIA — Characters, Incidents & Associations","Mud Bank / Dooley Welfare","People & Cases",
    "data/house/site-access.json","data/house/public-surfaces.json","data/house/room-inhabitants.json","data/house/rooms.json",
    "site-access-dock","site-access-panel",
):
    if token not in js and token not in css:
        errors.append(f"quick-access assets missing required marker: {token}")

for token in ("inject_site_access","patch_site_access","app/site-access.css","app/site-access.js"):
    if token not in patch:
        errors.append(f"public navigation projection missing marker: {token}")

entries={row.get("id"):row for row in contract.get("entries",[]) if isinstance(row,dict) and row.get("id")}
for required_id in ("news","world-map","tim","house","rooms","cia-character-archive","mud-bank","intelligence-cia","economy","tts","claims","public-witness","hours"):
    if required_id not in entries:
        errors.append(f"site-access contract missing curated entry: {required_id}")
required_aliases={
    "cia-character-archive":("cia","character archive","dossiers"),
    "mud-bank":("mud bank","dooley welfare","karma bank"),
    "intelligence-cia":("central intelligence agency","intelligence desk"),
    "economy":("fed","federal reserve","ecb","eurosystem","debt","bonds","obligations"),
    "tts":("tts","read aloud","text to speech"),
    "claims":("claims","statements"),
    "public-witness":("public witness","public record"),
}
for entry_id,aliases in required_aliases.items():
    hay=" ".join(str(x).lower() for x in entries.get(entry_id,{}).get("aliases",[]))
    for alias in aliases:
        if alias not in hay:
            errors.append(f"site-access {entry_id} missing alias: {alias}")
groups=contract.get("groups",{})
for group_name in ("go_now","find","direct_doors"):
    for entry_id in groups.get(group_name,[]):
        if entry_id not in entries:
            errors.append(f"site-access group {group_name} references unknown entry: {entry_id}")

for token in ("label===t","priority(e)","site-access-context","await loadIndex()","returnFocus"):
    if token not in js and token not in css:
        errors.append(f"quick-access behavior missing regression marker: {token}")

if "changed.update(patch_project_compass(OUT))" in patch:
    errors.append("legacy Project Compass must not be injected alongside the quick-access dock")

if OUT.exists():
    required=[
        "index.html","tim-dooley/index.html","world/index.html","news/index.html",
        "house/index.html","rooms/index.html","science/index.html","religion/index.html",
        "shadow-farm/index.html","world-map/index.html"
    ]
    for rel in required:
        text=read(OUT/rel)
        for asset in ("site-access.css","site-access.js"):
            if asset not in text:
                errors.append(f"{rel} missing generated {asset}")
    world=read(OUT/"world/index.html")
    if 'href="../news/">Current World</a>' not in world:
        errors.append("World must expose Current World in first-screen local navigation")
    home=read(OUT/"index.html")
    nav_start=home.find('<nav class="page-nav home-nav"')
    nav_end=home.find("</nav>",nav_start)
    if nav_start>=0 and nav_end>=0:
        first_nav=home[nav_start:nav_end]
        if first_nav.count("<a ")>5:
            errors.append("Home first-screen navigation exceeds compact local-link budget")
    if "/rooms/potatoverse-canon/beings/cia/" not in js:
        errors.append("CIA character archive direct route missing from quick access")
    if "/rooms/potatoverse-canon/beings/cia/bank/" not in js:
        errors.append("Mud Bank direct route missing from quick access")
    if "/shadow-farm/#intelligence-desk" not in js:
        errors.append("real-world Intelligence Desk direct route missing from quick access")

if errors:
    print("SITE ACCESS VALIDATION FAILED")
    for e in errors: print("-",e)
    raise SystemExit(1)

print("SITE ACCESS VALIDATION PASSED: fixed dock, direct News/Map/CIA/Mud Bank access, compact local nav and generated coverage are aligned.")
