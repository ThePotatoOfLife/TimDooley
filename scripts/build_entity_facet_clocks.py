#!/usr/bin/env python3
"""Build entity facet clocks from dated/period-tagged ledger evidence."""
from __future__ import annotations
import json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/"knowledge/story/entity-facet-ledger.json"
OUT=ROOT/"knowledge/story/entity-facet-clocks.json"

def date_key(value):
    if not value:
        return None
    text=str(value)
    m=re.search(r"(20\d{2}-\d{2}-\d{2})",text)
    if m: return m.group(1)
    y=re.search(r"(20\d{2})",text)
    return y.group(1) if y else None

def earliest(values):
    vals=sorted(v for v in values if v)
    return vals[0] if vals else None

ledger=json.loads(LEDGER.read_text(encoding="utf-8"))
out={"id":"entity-facet-clocks","version":"1.0.0","updated":ledger.get("updated"),"rule":"Derived only from dated/period-tagged ledger material. Null means the archive does not yet have a reliable clock.","entities":{}}
for eid,e in ledger.get("entities",{}).items():
    first_seen=(e.get("first_seen") or {}).get("date") or (e.get("first_seen") or {}).get("period")
    titles=[]; gifts=[]; roles=[]
    for f in e.get("facets",[]):
        k=date_key(f.get("scope")) or date_key(f.get("provenance"))
        if f.get("type")=="title" and k: titles.append(k)
        if f.get("type") in {"capability","signature_trait","scene_power","species_trait"} and k: gifts.append(k)
        if f.get("type")=="role" and k: roles.append(k)
    for b in e.get("story_beats",[]):
        k=date_key(b.get("date")) or date_key(b.get("period"))
        label=b.get("label","")
        if k and re.search(r"title|called|named",label,re.I): titles.append(k)
        if k and re.search(r"wing|eyes|gift|power|levitat|movement|ability|spudforce",label,re.I): gifts.append(k)
        if k: roles.append(k)
    role_clocks=sorted(set(roles))
    out["entities"][eid]={
      "label":e.get("label"),
      "first_seen":first_seen,
      "first_title":earliest(titles),
      "first_gift":earliest(gifts),
      "first_role_clock":role_clocks[0] if role_clocks else None,
      "first_role_change":role_clocks[1] if len(role_clocks)>1 else None,
      "source":"knowledge/story/entity-facet-ledger.json"
    }
OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(f"Wrote {len(out['entities'])} entity clocks")
