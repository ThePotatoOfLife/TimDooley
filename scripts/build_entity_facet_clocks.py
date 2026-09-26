#!/usr/bin/env python3
"""Build entity facet clocks from dated/period-tagged ledger evidence."""
from __future__ import annotations
import json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/"knowledge/story/entity-facet-ledger.json"
OUT=ROOT/"knowledge/story/entity-facet-clocks.json"
RANK={"period":1,"month":2,"day":3}

def parsed(value):
    if not value: return None
    text=str(value)
    m=re.search(r"(20\d{2})-(\d{2})-(\d{2})",text)
    if m:
        return {"display":m.group(0),"key":(int(m.group(1)),int(m.group(2)),int(m.group(3))),"precision":"day","year":int(m.group(1))}
    m=re.search(r"(20\d{2})-(\d{2})",text)
    if m:
        return {"display":m.group(0),"key":(int(m.group(1)),int(m.group(2)),0),"precision":"month","year":int(m.group(1))}
    m=re.search(r"(20\d{2})",text)
    if m:
        return {"display":text,"key":(int(m.group(1)),0,0),"precision":"period","year":int(m.group(1))}
    return None

def earliest(items):
    xs=[x for x in items if x]
    xs.sort(key=lambda x:(x["key"],-RANK[x["precision"]]))
    return xs[0] if xs else None

def latest(items):
    xs=[x for x in items if x]
    xs.sort(key=lambda x:(x["key"],RANK[x["precision"]]),reverse=True)
    return xs[0] if xs else None

def dedupe_year(items):
    xs=sorted((x for x in items if x),key=lambda x:x["key"])
    out=[]
    for x in xs:
        if out and out[-1]["year"]==x["year"]:
            if RANK[x["precision"]]>RANK[out[-1]["precision"]]:
                out[-1]=x
        else:
            out.append(x)
    return out

ledger=json.loads(LEDGER.read_text(encoding="utf-8"))
out={"id":"entity-facet-clocks","version":"1.1.0","updated":ledger.get("updated"),"rule":"Derived only from dated/period-tagged ledger material. Mixed precision is normalized; coarse and precise clocks in the same year do not create fake transitions. Null means no reliable clock.","entities":{}}
for eid,e in ledger.get("entities",{}).items():
    beats=[parsed(b.get("date")) or parsed(b.get("period")) for b in e.get("story_beats",[])]
    fs=e.get("first_seen") or {}
    explicit=parsed(fs.get("date")) or parsed(fs.get("period"))
    first=explicit or earliest(beats)
    last=latest(beats+([explicit] if explicit else []))
    titles=[]; gifts=[]; roles=[]
    for f in e.get("facets",[]):
        t=parsed(f.get("scope")) or parsed(f.get("provenance"))
        if f.get("type")=="title" and t: titles.append(t)
        if f.get("type") in {"capability","signature_trait","scene_power","species_trait"} and t: gifts.append(t)
        if f.get("type")=="role" and t: roles.append(t)
    for b in e.get("story_beats",[]):
        t=parsed(b.get("date")) or parsed(b.get("period"))
        if not t: continue
        label=b.get("label","")
        if re.search(r"title|called|named",label,re.I): titles.append(t)
        if re.search(r"wing|eyes|gift|power|levitat|movement|ability|spudforce",label,re.I): gifts.append(t)
        roles.append(t)
    role_clocks=dedupe_year(roles)
    out["entities"][eid]={
      "label":e.get("label"),
      "first_seen":first["display"] if first else None,
      "first_seen_precision":first["precision"] if first else None,
      "last_seen":last["display"] if last else None,
      "last_seen_precision":last["precision"] if last else None,
      "first_title":(earliest(titles) or {}).get("display"),
      "first_gift":(earliest(gifts) or {}).get("display"),
      "first_role_clock":role_clocks[0]["display"] if role_clocks else None,
      "first_role_change":role_clocks[1]["display"] if len(role_clocks)>1 else None,
      "source":"knowledge/story/entity-facet-ledger.json"
    }
OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(f"Wrote {len(out['entities'])} entity clocks")
