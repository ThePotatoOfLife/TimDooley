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
tts_drawer=read(ROOT/"app/tts-drawer.js")
patch=read(ROOT/"scripts/patch_public_navigation.py")
contract_text=read(ROOT/"data/house/site-access.json")
journey_text=read(ROOT/"data/house/access-journeys.json")
try:
    contract=json.loads(contract_text) if contract_text else {}
except json.JSONDecodeError as exc:
    errors.append(f"invalid data/house/site-access.json: {exc}")
    contract={}
try:
    journeys=json.loads(journey_text) if journey_text else {}
except json.JSONDecodeError as exc:
    errors.append(f"invalid data/house/access-journeys.json: {exc}")
    journeys={}

for token in (
    "Current World","World Map","Potatoverse CIA · Character Archive","U.S. CIA · Central Intelligence Agency","World Spiritual Bank / Mud Bank","People & Cases",
    "Project landmarks","data-site-access-menu","site-access-local-shortcuts",
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
    "cia-character-archive":("potatoverse cia","character archive","dossiers"),
    "mud-bank":("world spiritual bank","mud bank","dooley welfare","karma bank"),
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
# CIA namespace collision guard
project_cia=entries.get("cia-character-archive",{})
real_cia=entries.get("intelligence-cia",{})
if project_cia.get("label")!="Potatoverse CIA · Character Archive":
    errors.append("project CIA must use namespace-explicit global label")
if real_cia.get("label")!="U.S. CIA · Central Intelligence Agency":
    errors.append("real CIA must use namespace-explicit global label")
for row_id,row in (("cia-character-archive",project_cia),("intelligence-cia",real_cia)):
    aliases=[str(x).strip().lower() for x in row.get("aliases",[])]
    if "cia" in aliases:
        errors.append(f"{row_id} contains forbidden bare CIA alias")
disambig=(contract.get("disambiguation") or {}).get("cia") or {}
if disambig.get("prompt")!="Which CIA?":
    errors.append("bare CIA query must define an explicit two-door disambiguation")
if "Which CIA?" not in js:
    errors.append("site-access runtime missing CIA chooser")

groups=contract.get("groups",{})
landmarks=groups.get("landmarks",[])
if landmarks[:2]!=["cia-character-archive","mud-bank"]:
    errors.append("site-access landmarks must begin with Character Archive and World Spiritual Bank")
wayfinding=contract.get("wayfinding") or {}
if int(wayfinding.get("max_interactions_for_landmarks",99))>2:
    errors.append("landmark access exceeds two-interaction contract")

journey_rows=journeys.get("journeys",[]) if isinstance(journeys,dict) else []
if len(journey_rows)!=25:
    errors.append(f"access journey fixture count must be exactly 25, got {len(journey_rows)}")
for row in journey_rows:
    if int(row.get("max_activations",99))>2:
        errors.append(f"journey exceeds two-activation contract: {row.get('intent')}")
    if row.get("entry_id"):
        entry=entries.get(row.get("entry_id"))
        if not entry:
            errors.append(f"journey references unknown access entry: {row.get('entry_id')}")
            continue
        q=str(row.get("query","")).strip().lower()
        hay=" ".join([str(entry.get("label","")).lower(),*(str(x).lower() for x in entry.get("aliases",[]))])
        if q and q not in hay:
            errors.append(f"journey query does not resolve to expected entry {row.get('entry_id')}: {q}")
    elif row.get("disambiguation"):
        opts=row.get("disambiguation",[])
        for option in opts:
            if option not in entries:
                errors.append(f"journey disambiguation references unknown entry: {option}")
        if str(row.get("query","")).strip().lower()!="cia":
            errors.append("current access disambiguation fixture must be the bare CIA query")
    else:
        errors.append(f"journey lacks entry_id or disambiguation: {row.get('intent')}")

for group_name in ("go_now","find","direct_doors"):
    for entry_id in groups.get(group_name,[]):
        if entry_id not in entries:
            errors.append(f"site-access group {group_name} references unknown entry: {entry_id}")

for token in ("label===t","priority(e)","site-access-context","await loadIndex()","returnFocus","--site-access-clearance","resultLinks","focusResult","moveResultFocus","ArrowDown","ArrowUp","Home","End"):
    if token not in js and token not in css:
        errors.append(f"quick-access behavior missing regression marker: {token}")

for token in ("--site-access-clearance", "viewportHeight-clearance-44"):
    if token not in tts_drawer:
        errors.append(f"TTS selection control does not honor fixed access clearance: {token}")

if "@media(max-width:680px)" not in css or ".site-access-panel{bottom:52px;width:calc(100vw - 12px)" not in css:
    errors.append("site-access narrow-screen panel contract missing")

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
    news=read(OUT/"news/index.html")
    house=read(OUT/"house/index.html")
    if 'href="../news/">Current World</a>' not in world:
        errors.append("World must expose Current World in first-screen local navigation")
    nav_start=news.find('<nav class="page-nav" aria-label="News navigation">')
    nav_end=news.find("</nav>",nav_start)
    if nav_start>=0 and nav_end>=0 and news[nav_start:nav_end].count("<a ")!=1:
        errors.append("Current World local navigation duplicates global dock destinations")
    house_nav_start=house.find('<nav class="page-nav" aria-label="House structure">')
    house_nav_end=house.find("</nav>",house_nav_start)
    if house_nav_start>=0 and house_nav_end>=0:
        house_nav=house[house_nav_start:house_nav_end]
        if house_nav.count("<a ")!=2 or 'href="../rooms/">Rooms</a>' not in house_nav or 'href="../axis/">Living Axis</a>' not in house_nav:
            errors.append("House first navigation row must stay structural: Rooms + Living Axis only")
        for forbidden in ('../rooms/objects/', '../paths/', 'href="../">← Home</a>'):
            if forbidden in house_nav:
                errors.append(f"House top navigation duplicates global/named-object access: {forbidden}")
    first_nav_budgets={
        "tim-dooley/index.html":2,
        "religion/index.html":3,
        "philosophy/index.html":2,
        "science/index.html":2,
        "world/index.html":2,
        "north/index.html":2,
        "axis/index.html":3,
        "elevator/index.html":4,
        "paths/index.html":3,
        "politics/index.html":3,
        "tim-dooley/story/index.html":4,
        "timeline/index.html":2,
        "religion/trinity/index.html":3,
        "works/index.html":3,
        "world-systems/index.html":4,
        "timeline/foundations/index.html":2,
    }
    for rel,budget in first_nav_budgets.items():
        page=read(OUT/rel)
        nav_match=__import__("re").search(r"<nav\\b[^>]*>(.*?)</nav>",page,flags=__import__("re").I|__import__("re").S)
        if not nav_match:
            errors.append(f"{rel} missing first local navigation row")
        elif nav_match.group(1).count("<a ")>budget:
            errors.append(f"{rel} first navigation row exceeds specialist budget {budget}")
    specialist_parent_contracts={
        "context/index.html": ("source-authority/", 2),
        "context/source-authority/index.html": ("../", 2),
        "philosophy/interpretive-justice.html": ("./", 3),
    }
    for rel,(parent_href,budget) in specialist_parent_contracts.items():
        page=read(OUT/rel)
        nav_match=__import__("re").search(r"<nav\\b[^>]*>(.*?)</nav>",page,flags=__import__("re").I|__import__("re").S)
        if not nav_match:
            errors.append(f"{rel} missing specialist continuity navigation")
            continue
        nav=nav_match.group(1)
        if f'href="{parent_href}"' not in nav:
            errors.append(f"{rel} missing expected parent/owner handoff {parent_href}")
        if nav.count("<a ")>budget:
            errors.append(f"{rel} specialist continuity navigation exceeds budget {budget}")
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

print("SITE ACCESS VALIDATION PASSED: fixed dock, namespace-safe CIA routing, direct News/Map/World Spiritual Bank access, compact local nav and generated coverage are aligned.")
