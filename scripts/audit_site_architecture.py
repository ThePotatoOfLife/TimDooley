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
STYLE_SCRIPT=re.compile(r"<(?:style|script)\b[\s\S]*?</(?:style|script)>",re.I)
ANCHOR_HREF=re.compile(r"""<a\b[^>]*href=["']([^"']+)["']""", re.I)
BUTTON=re.compile(r"<button\b",re.I); NAV=re.compile(r"<nav\b",re.I)
FIRST_NAV=re.compile(r"<nav\b[^>]*>([\s\S]*?)</nav>",re.I)
ANCHOR_FULL=re.compile(r"""<a\b[^>]*href=["']([^"']+)["'][^>]*>([\s\S]*?)</a>""",re.I)
TAG=re.compile(r"<[^>]+>")
H1=re.compile(r"<h1\b",re.I); H2=re.compile(r"<h2\b",re.I)
BASE_HREF=re.compile(r"""<base\b[^>]*href=["\']([^"\']+)["\']""",re.I)
VAGUE_STANDALONE_LABEL=re.compile(r"^(more|deep|explore|context|archive)\s*(?:→|↗)?$",re.I)
EXTERNAL=("http://","https://","//","mailto:","tel:","javascript:","data:","blob:")
PUBLIC_SCAN_EXCLUDE={".git",".github","_site","archive","docs","node_modules","components","vendor","scripts"}
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

def effective_base_route(route:str,raw_html:str)->str:
    match=BASE_HREF.search(raw_html)
    if not match: return route
    base=match.group(1).strip()
    if not base or base.startswith(EXTERNAL): return route
    return normalize_route(urlsplit(urljoin("https://example.invalid"+route,base)).path)

def resolve_href(base_route:str,href:str):
    raw=href.strip()
    if not raw or raw.startswith("#") or raw.startswith(EXTERNAL): return None
    return normalize_route(urlsplit(urljoin("https://example.invalid"+base_route,raw)).path)

def count_before(text:str,index:int,regex)->int:
    return len(regex.findall(text[:index])) if index>=0 else 0

def main()->int:
    errors=[]; warnings=[]; metrics=[]
    probe='<base href="../"><nav><a href="world/">World</a></nav><h1>Title</h1><h2>Section</h2><button>Go</button>'
    if not (ANCHOR_HREF.search(probe) and NAV.search(probe) and FIRST_NAV.search(probe) and H1.search(probe) and H2.search(probe) and BUTTON.search(probe)):
        errors.append("architecture audit regex self-check failed")
    if effective_base_route("/explore/",probe)!="/" or resolve_href(effective_base_route("/explore/",probe),"world/")!="/world/":
        errors.append("architecture audit base-href self-check failed")
    if not VAGUE_STANDALONE_LABEL.match("Explore") or VAGUE_STANDALONE_LABEL.match("Archive explorer"):
        errors.append("architecture audit vague-label self-check failed")
    if not named_open_matches_target("Open World Map",{"title":"World Map"}) or named_open_matches_target("Open Foundation Rooms",{"title":"House"}):
        errors.append("architecture audit promise-CTA self-check failed")
    data=json.loads(REGISTRY.read_text(encoding="utf-8"))
    rows=[r for r in data.get("surfaces",[]) if isinstance(r,dict) and r.get("status")=="active"]
    by_id={r["id"]:r for r in rows}; route_to_id={}
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
        raw=path.read_text(encoding="utf-8",errors="replace")
        visible=STYLE_SCRIPT.sub("",raw)
        link_base=effective_base_route(route,raw)
        h1=H1.search(visible); h2=H2.search(visible); hrefs=ANCHOR_HREF.findall(visible)
        first_h2=h2.start() if h2 else len(visible)
        pre_links=count_before(visible,first_h2,ANCHOR_HREF); pre_buttons=count_before(visible,first_h2,BUTTON)
        first_nav=FIRST_NAV.search(visible[:first_h2]); first_nav_links=len(ANCHOR_HREF.findall(first_nav.group(1))) if first_nav else 0
        pre_navs=count_before(visible,first_h2,NAV)
        mobile_stack_score=first_nav_links + pre_buttons + max(0,pre_navs-1)*2
        internal=[resolve_href(link_base,h) for h in hrefs]; internal=[x for x in internal if x]
        cta_rows=[]
        for href,label_html in ANCHOR_FULL.findall(visible):
            label=re.sub(r"\s+"," ",TAG.sub(" ",label_html)).strip()
            if VAGUE_STANDALONE_LABEL.match(label):
                warnings.append({"code":"vague-link-label","surface":sid,"label":label,"target":resolve_href(link_base,href)})
            if not re.match(r"^(read|open|enter)\b",label,re.I): continue
            target=resolve_href(link_base,href)
            if not target: continue
            target_id=route_to_id.get(target)
            target_row=(by_id.get(target_id) or {}) if target_id else {}
            target_job=target_row.get("reader_job") if target_id else None
            target_title=target_row.get("title") if target_id else None
            cta_rows.append({"label":label,"target":target,"target_surface":target_id,"target_title":target_title,"target_reader_job":target_job})
        registered_targets={x for x in internal if x in registered_routes and x!=route}; target_sets[sid]=registered_targets
        counts=Counter(internal); repeated=sorted((t,c) for t,c in counts.items() if c>=4)
        budget=SPECIAL_BUDGETS.get(sid,BUDGETS.get(row.get("surface_type"),BUDGETS["guide"]))
        over={"pre_links":max(0,pre_links-budget["pre_links"]),"pre_buttons":max(0,pre_buttons-budget["pre_buttons"]),"total_links":max(0,len(hrefs)-budget["total_links"])}
        if any(over.values()): warnings.append({"code":"density-budget","surface":sid,"detail":over,"observed":{"pre_links":pre_links,"pre_buttons":pre_buttons,"total_links":len(hrefs)},"budget":budget})
        if first_nav_links>4: warnings.append({"code":"first-nav-link-wall","surface":sid,"count":first_nav_links})
        if mobile_stack_score>12: warnings.append({"code":"mobile-precontent-stack","surface":sid,"score":mobile_stack_score,"first_nav_links":first_nav_links,"pre_buttons":pre_buttons,"pre_navs":pre_navs})
        if repeated: warnings.append({"code":"repeated-destination","surface":sid,"targets":repeated[:12]})
        if not h1: warnings.append({"code":"missing-h1","surface":sid})
        if len(registered_targets)>18: warnings.append({"code":"high-registered-outdegree","surface":sid,"count":len(registered_targets)})
        for cta in cta_rows:
            target_id=cta.get("target_surface")
            target_row=(by_id.get(target_id) or {}) if target_id else {}
            if target_id and target_row.get("surface_type") in {"hub","explorer"}:
                if named_open_matches_target(cta.get("label",""),target_row):
                    continue
                warnings.append({"code":"promise-cta-to-hub","surface":sid,**cta})
        runtime_href_literals=len(re.findall(r'href(?:=|\s*[:+])', raw, flags=re.I))-len(hrefs)
        metrics.append({"id":sid,"route":route,"surface_type":row.get("surface_type"),"visibility":row.get("visibility"),"reader_job":row.get("reader_job"),"source":path.relative_to(ROOT).as_posix(),"authored_anchor_hrefs":len(hrefs),"runtime_or_script_href_literals":max(0,runtime_href_literals),"buttons":len(BUTTON.findall(visible)),"navs":len(NAV.findall(visible)),"pre_substance_links":pre_links,"pre_substance_buttons":pre_buttons,"first_nav_links":first_nav_links,"pre_substance_navs":pre_navs,"mobile_precontent_stack_score":mobile_stack_score,"registered_outdegree":len(registered_targets),"registered_targets":sorted(registered_targets),"promise_ctas":cta_rows})
    overlaps=[]; ids=sorted(target_sets)
    for i,left in enumerate(ids):
        a=target_sets[left]
        if len(a)<5: continue
        for right in ids[i+1:]:
            b=target_sets[right]
            if len(b)<5: continue
            union=a|b; score=len(a&b)/len(union) if union else 0.0
            if score>=0.70: overlaps.append({"left":left,"right":right,"jaccard":round(score,3),"shared":sorted(a&b)})
    dead_ends=[]
    for row in rows:
        sid=row["id"]
        targets=target_sets.get(sid,set())
        parent=row.get("primary_parent")
        meaningful_targets={t for t in targets if route_to_id.get(t)!="home"}
        if not meaningful_targets and sid!="home":
            dead_ends.append({"surface":sid,"route":normalize_route(row.get("canonical_route") or row.get("route") or "/"),"parent":parent})
            warnings.append({"code":"registered-dead-end","surface":sid,"parent":parent})

    short_cycles=[]
    seen_cycles=set()
    for left,a_targets in target_sets.items():
        for right in a_targets:
            right_id=route_to_id.get(right)
            if not right_id or right_id==left: continue
            if normalize_route(by_id[left].get("canonical_route") or by_id[left].get("route") or "/") in target_sets.get(right_id,set()):
                key=tuple(sorted((left,right_id)))
                if key not in seen_cycles:
                    seen_cycles.add(key)
                    short_cycles.append({"length":2,"surfaces":list(key)})
    standalone=[]
    for path in ROOT.rglob("*.html"):
        rel_path=path.relative_to(ROOT)
        if rel_path.parts and rel_path.parts[0] in PUBLIC_SCAN_EXCLUDE:
            continue
        raw=path.read_text(encoding="utf-8",errors="replace")
        if "<main" not in raw.lower():
            continue
        if 'name="robots" content="noindex,follow"' in raw and ("location.replace(" in raw or 'http-equiv="refresh"' in raw.lower()):
            continue
        visible=STYLE_SCRIPT.sub("",raw)
        hrefs=ANCHOR_HREF.findall(visible)
        rel=rel_path.as_posix()
        base_route="/"+rel.rsplit("/",1)[0]+"/" if "/" in rel else "/"
        link_base=effective_base_route(base_route,raw)
        internal=[h for h in hrefs if resolve_href(link_base,h)]
        row={"surface":rel,"authored_links":len(hrefs),"internal_links":len(internal)}
        standalone.append(row)
        if not internal:
            warnings.append({"code":"authored-dead-end","surface":rel})

    report={"version":"1.2.0","registry_version":data.get("version"),"surface_count":len(rows),"errors":errors,"warnings":warnings,"overlap_pairs":overlaps,"dead_ends":dead_ends,"short_cycles":short_cycles,"authored_surfaces":standalone,"metrics":metrics,"notes":["Density budgets are page-type heuristics, not release-failure thresholds.","First-nav link-wall warns above four links; mobile pre-content stack score combines first-nav links, buttons and extra nav rows before the first substantive H2.","Registered outdegree counts only links to other registered public surfaces; deep records and anchors remain separate.","Two-way cycles are review signals: reciprocal orientation may be healthy, repeated hub bouncing may not be.","Overlap is a review signal for redundant reader jobs, not proof that two surfaces should merge.","Read/Enter CTAs and mismatched Open CTAs pointing to hub/explorer shells are review signals; a named Open X → X hub is treated as valid navigation.","Bare More/Deep/Explore/Context/Archive labels are flagged when they do not state destination intent."]}
    REPORT.parent.mkdir(parents=True,exist_ok=True); REPORT.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(f"SITE ARCHITECTURE AUDIT: {len(rows)} active surfaces · {len(errors)} errors · {len(warnings)} warnings · {len(overlaps)} high-overlap pairs")
    warning_counts=Counter(item.get("code","unknown") for item in warnings)
    if warning_counts:
        print("- Warning classes: " + " · ".join(f"{code}={count}" for code,count in sorted(warning_counts.items())))
    priority_codes={"authored-dead-end","registered-dead-end","promise-cta-to-hub","vague-link-label","first-nav-link-wall","mobile-precontent-stack"}
    priority_rank={"authored-dead-end":0,"registered-dead-end":1,"vague-link-label":2,"promise-cta-to-hub":3,"first-nav-link-wall":4,"mobile-precontent-stack":5}
    priority=sorted((item for item in warnings if item.get("code") in priority_codes),key=lambda item:(priority_rank.get(item.get("code"),99),item.get("surface","")))
    for item in priority[:30]:
        detail=item.get("label") or item.get("target") or item.get("count") or item.get("score") or ""
        print(f"- WARN {item['code']}: {item.get('surface',item.get('left','site'))}" + (f" · {detail}" if detail else ""))
    if len(priority)>30: print(f"- ... {len(priority)-30} additional priority warnings in {REPORT.relative_to(ROOT)}")
    for item in overlaps[:8]: print(f"- OVERLAP {item['left']} ↔ {item['right']}: {item['jaccard']}")
    if errors:
        for error in errors: print("- ERROR",error)
        return 1
    return 0

if __name__=="__main__": raise SystemExit(main())
