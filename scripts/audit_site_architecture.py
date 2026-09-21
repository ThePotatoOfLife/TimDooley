#!/usr/bin/env python3
"""Audit whole-site reader architecture without turning style heuristics into brittle release gates."""
from __future__ import annotations
import json, re
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin, urlsplit

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"data"/"house"/"public-surfaces.json"
REPORT=ROOT/".quality-logs"/"site-architecture-audit.json"
STYLE_SCRIPT=re.compile(r"<(?:style|script)\\b[\\s\\S]*?</(?:style|script)>",re.I)
HREF=re.compile(r'href=[\\"\\']([^\\"\\']+)[\\"\\']',re.I)
BUTTON=re.compile(r"<button\\b",re.I); NAV=re.compile(r"<nav\\b",re.I)
H1=re.compile(r"<h1\\b",re.I); H2=re.compile(r"<h2\\b",re.I)
EXTERNAL=("http://","https://","//","mailto:","tel:","javascript:","data:","blob:")
BUDGETS={
 "home":{"pre_links":20,"pre_buttons":6,"total_links":100},
 "hub":{"pre_links":14,"pre_buttons":8,"total_links":120},
 "guide":{"pre_links":14,"pre_buttons":10,"total_links":100},
 "explorer":{"pre_links":16,"pre_buttons":20,"total_links":140},
 "evidence":{"pre_links":14,"pre_buttons":10,"total_links":100},
 "subject":{"pre_links":14,"pre_buttons":10,"total_links":100},
}
SPECIAL_BUDGETS={
 "news":{"pre_links":16,"pre_buttons":40,"total_links":140},
 "world-map":{"pre_links":20,"pre_buttons":35,"total_links":160},
}

def source_path(route:str)->Path:
    path=route.split("#",1)[0].split("?",1)[0]
    if path=="/": return ROOT/"index.html"
    rel=path.lstrip("/")
    return ROOT/rel/"index.html" if rel.endswith("/") else ROOT/rel

def normalize_route(value:str)->str:
    path=urlsplit(value).path or "/"
    if not path.startswith("/"): path="/"+path
    tail=path.rsplit("/",1)[-1]
    if "." not in tail and not path.endswith("/"): path+="/"
    return path

def resolve_href(base_route:str,href:str):
    raw=href.strip()
    if not raw or raw.startswith("#") or raw.startswith(EXTERNAL): return None
    return normalize_route(urlsplit(urljoin("https://example.invalid"+base_route,raw)).path)

def count_before(text:str,index:int,regex)->int:
    return len(regex.findall(text[:index])) if index>=0 else 0

def main()->int:
    data=json.loads(REGISTRY.read_text(encoding="utf-8"))
    rows=[r for r in data.get("surfaces",[]) if isinstance(r,dict) and r.get("status")=="active"]
    by_id={r["id"]:r for r in rows}; route_to_id={}
    errors=[]; warnings=[]; metrics=[]
    for row in rows:
        sid=row["id"]; route=normalize_route(row.get("canonical_route") or row.get("route") or "/")
        if route in route_to_id: errors.append(f"duplicate canonical route {route}: {route_to_id[route]} and {sid}")
        route_to_id[route]=sid
        if not str(row.get("reader_job") or "").strip(): errors.append(f"{sid} has no reader_job")
        parent=row.get("primary_parent")
        if parent is not None and parent not in by_id: errors.append(f"{sid} references missing active parent {parent}")
    registered_routes=set(route_to_id); target_sets={}
    for row in rows:
        sid=row["id"]; route=normalize_route(row.get("canonical_route") or row.get("route") or "/")
        path=source_path(route)
        if not path.is_file():
            errors.append(f"{sid} source surface missing: {path.relative_to(ROOT)}"); continue
        visible=STYLE_SCRIPT.sub("",path.read_text(encoding="utf-8",errors="replace"))
        h1=H1.search(visible); h2=H2.search(visible); hrefs=HREF.findall(visible)
        first_h2=h2.start() if h2 else len(visible)
        pre_links=count_before(visible,first_h2,HREF); pre_buttons=count_before(visible,first_h2,BUTTON)
        internal=[resolve_href(route,h) for h in hrefs]; internal=[x for x in internal if x]
        registered_targets={x for x in internal if x in registered_routes and x!=route}; target_sets[sid]=registered_targets
        counts=Counter(internal); repeated=sorted((t,c) for t,c in counts.items() if c>=4)
        budget=SPECIAL_BUDGETS.get(sid,BUDGETS.get(row.get("surface_type"),BUDGETS["guide"]))
        over={"pre_links":max(0,pre_links-budget["pre_links"]),"pre_buttons":max(0,pre_buttons-budget["pre_buttons"]),"total_links":max(0,len(hrefs)-budget["total_links"])}
        if any(over.values()): warnings.append({"code":"density-budget","surface":sid,"detail":over,"observed":{"pre_links":pre_links,"pre_buttons":pre_buttons,"total_links":len(hrefs)},"budget":budget})
        if repeated: warnings.append({"code":"repeated-destination","surface":sid,"targets":repeated[:12]})
        if not h1: warnings.append({"code":"missing-h1","surface":sid})
        if len(registered_targets)>18: warnings.append({"code":"high-registered-outdegree","surface":sid,"count":len(registered_targets)})
        metrics.append({"id":sid,"route":route,"surface_type":row.get("surface_type"),"visibility":row.get("visibility"),"reader_job":row.get("reader_job"),"source":path.relative_to(ROOT).as_posix(),"hrefs":len(hrefs),"buttons":len(BUTTON.findall(visible)),"navs":len(NAV.findall(visible)),"pre_substance_links":pre_links,"pre_substance_buttons":pre_buttons,"registered_outdegree":len(registered_targets),"registered_targets":sorted(registered_targets)})
    overlaps=[]; ids=sorted(target_sets)
    for i,left in enumerate(ids):
        a=target_sets[left]
        if len(a)<5: continue
        for right in ids[i+1:]:
            b=target_sets[right]
            if len(b)<5: continue
            union=a|b; score=len(a&b)/len(union) if union else 0.0
            if score>=0.70: overlaps.append({"left":left,"right":right,"jaccard":round(score,3),"shared":sorted(a&b)})
    report={"version":"1.0.0","registry_version":data.get("version"),"surface_count":len(rows),"errors":errors,"warnings":warnings,"overlap_pairs":overlaps,"metrics":metrics,"notes":["Density budgets are page-type heuristics, not release-failure thresholds.","Registered outdegree counts only links to other registered public surfaces; deep records and anchors remain separate.","Overlap is a review signal for redundant reader jobs, not proof that two surfaces should merge."]}
    REPORT.parent.mkdir(parents=True,exist_ok=True); REPORT.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(f"SITE ARCHITECTURE AUDIT: {len(rows)} active surfaces · {len(errors)} errors · {len(warnings)} warnings · {len(overlaps)} high-overlap pairs")
    for item in warnings[:12]: print(f"- WARN {item['code']}: {item.get('surface',item.get('left','site'))}")
    if len(warnings)>12: print(f"- ... {len(warnings)-12} additional warnings in {REPORT.relative_to(ROOT)}")
    for item in overlaps[:8]: print(f"- OVERLAP {item['left']} ↔ {item['right']}: {item['jaccard']}")
    if errors:
        for error in errors: print("- ERROR",error)
        return 1
    return 0

if __name__=="__main__": raise SystemExit(main())
