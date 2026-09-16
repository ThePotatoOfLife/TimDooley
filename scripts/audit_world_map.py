#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION="1.0"
RISK_WEIGHTS={"error":10,"warning":3,"note":0}
RISK_DOMAINS=("render_ownership","feature_state","style_lifecycle","event_lifecycle","popup_interaction","data_mutation","url_state","dom_ownership")
DEFAULT_RENDER_STACK_SLOTS=("physical-surface","physical-water","physical-line","geography-context","context-network","selection-emphasis")
HOVER_EVENTS={"mousemove","mouseenter","mouseover"}

def line_for(source,offset): return source.count("\n",0,offset)+1
def record(kind,resource,module,operation,line,confidence="high",**details): return {"kind":kind,"resource":resource,"module":module,"operation":operation,"line":line,"confidence":confidence,"details":details}
def discover_modules(root):
    world=root/"world-map"; return sorted(world.glob("3d-*.js")) if world.is_dir() else []
def _nearest_map_event(source,offset):
    hits=list(re.finditer(r"\bmap\.(?:on|once)\(\s*['\"]([^'\"]+)['\"]",source[:offset])); return hits[-1].group(1) if hits else None
def _browser_url_vars(source):
    if not re.search(r"\bhistory\.(?:replaceState|pushState)\s*\(",source): return set()
    return {m.group(1) for m in re.finditer(r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*new\s+URL\(\s*location\.href\s*\)",source)}
def _scheduled_microtask(source):
    return bool(re.search(r"\bfunction\s+schedule\s*\([^)]*\)\s*\{[\s\S]{0,1400}?\bqueueMicrotask\s*\(",source))

def scan_module(path,repo_root):
    source=path.read_text(encoding="utf-8"); module=path.relative_to(repo_root).as_posix(); out=[]
    specs=(("source_create",r"\b(?:map\.)?addSource\(\s*['\"]([^'\"]+)['\"]",lambda g:(f"source:{g[0]}","addSource")),("layer_create",r"\b(?:map\.)?addLayer\(\s*\{[\s\S]{0,500}?\bid\s*:\s*['\"]([^'\"]+)['\"]",lambda g:(f"layer:{g[0]}","addLayer")),("source_remove",r"\b(?:map\.)?removeSource\(\s*['\"]([^'\"]+)['\"]",lambda g:(f"source:{g[0]}","removeSource")),("layer_remove",r"\b(?:map\.)?removeLayer\(\s*['\"]([^'\"]+)['\"]",lambda g:(f"layer:{g[0]}","removeLayer")),("paint_write",r"\b(?:map\.)?setPaintProperty\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]",lambda g:(f"paint:{g[0]}:{g[1]}","setPaintProperty")),("layout_write",r"\b(?:map\.)?setLayoutProperty\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]",lambda g:(f"layout:{g[0]}:{g[1]}","setLayoutProperty")),("set_data",r"\b(?:map\.)?getSource\(\s*['\"]([^'\"]+)['\"]\s*\)\s*\??\.\s*setData\s*\(",lambda g:(f"set-data:{g[0]}","setData")),("public_api",r"\bwindow\.(__potatoAtlas[A-Za-z0-9_$]+)\s*=",lambda g:(f"api:{g[0]}","window-assign")),("dom_id",r"\b[A-Za-z_$][\w$]*\.id\s*=\s*['\"]([^'\"$]+)['\"]",lambda g:(f"dom:{g[0]}","dom-id")))
    for kind,pat,build in specs:
        for m in re.finditer(pat,source,re.M):
            resource,op=build(m.groups()); out.append(record(kind,resource,module,op,line_for(source,m.start())))
    for var in _browser_url_vars(source):
        for m in re.finditer(rf"\b{re.escape(var)}\.searchParams\.(?:set|delete)\(\s*['\"]([^'\"]+)['\"]",source): out.append(record("url_write",f"url:{m.group(1)}",module,"searchParams",line_for(source,m.start()),variable=var))
    scheduled_microtask=_scheduled_microtask(source)
    epat=re.compile(r"\bmap\.(?:on|once|off)\(\s*['\"]([^'\"]+)['\"](?:\s*,\s*['\"]([^'\"]+)['\"])?")
    for m in epat.finditer(source):
        event,layer=m.group(1),m.group(2); out.append(record("map_listener",f"map-event:{event}:{layer or 'global'}",module,"map-event",line_for(source,m.start()),event=event,layer=layer))
        if event=="styledata":
            ctx=source[max(0,m.start()-500):min(len(source),m.start()+1800)]; deferred="queueMicrotask" in ctx or ("schedule(" in ctx and scheduled_microtask)
            out.append(record("style_restore",f"style-restore:{module}",module,"styledata",line_for(source,m.start()),guarded=("restoring" in ctx),deferred=deferred))
    for m in re.finditer(r"\b(window|document)\.addEventListener\(\s*['\"]([^'\"]+)['\"]",source): out.append(record("dom_listener",f"dom-event:{m.group(1)}:{m.group(2)}",module,"addEventListener",line_for(source,m.start()),target=m.group(1),event=m.group(2)))
    fspat=re.compile(r"\bmap\.setFeatureState\(\s*\{[\s\S]{0,300}?\bsource\s*:\s*['\"]([^'\"]+)['\"][\s\S]{0,300}?\}\s*,\s*\{([\s\S]{0,400}?)\}\s*\)",re.M); keypat=re.compile(r"(?:^|,)\s*([A-Za-z_$][\w$]*)\s*:")
    for m in fspat.finditer(source):
        for km in keypat.finditer(m.group(2)):
            key=km.group(1); out.append(record("feature_state_write",f"feature-state:{m.group(1)}:{key}",module,"setFeatureState",line_for(source,m.start()),source=m.group(1),key=key))
    for pat in (re.compile(r"\b(?:renderStack|stack)\.register\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]"),re.compile(r"\b(?:renderStack|stack)\.register\(\s*['\"]([^'\"]+)['\"]\s*,\s*\{[\s\S]{0,250}?\bslot\s*:\s*['\"]([^'\"]+)['\"]")):
        for m in pat.finditer(source): out.append(record("render_stack",f"render-stack:{m.group(1)}",module,"register",line_for(source,m.start()),layer=m.group(1),slot=m.group(2)))
    for i,m in enumerate(re.finditer(r"new\s+maplibregl\.Popup\s*\(",source),1):
        event=_nearest_map_event(source,m.start()); ctx=source[max(0,m.start()-1200):min(len(source),m.end()+2200)]; out.append(record("popup",f"popup:{module}:{i}",module,"Popup",line_for(source,m.start()),transient=event in HOVER_EVENTS,trigger_event=event,has_hover_class="atlas-hover" in ctx))
    return sorted(out,key=lambda r:(r["module"],r["line"],r["kind"],r["resource"]))

def load_contract(path):
    if not path.exists(): return {"schema_version":SCHEMA_VERSION}
    payload=json.loads(path.read_text(encoding="utf-8"));
    if not isinstance(payload,dict): raise ValueError("World Map audit contract must be a JSON object")
    return payload
def finding(code,severity,domain,message,resources=None,modules=None,remediation=None):
    item={"code":code,"severity":severity,"domain":domain,"message":message,"resources":sorted(set(resources or [])),"modules":sorted(set(modules or []))};
    if remediation:item["remediation"]=remediation
    return item
def contract_shared(contract,rid,modules):
    entry=(contract.get("shared") or {}).get(rid); return isinstance(entry,dict) and bool(entry.get("rationale")) and modules<=set(entry.get("modules") or [])

def analyze(records,contract,existing_modules):
    findings=[]; by_resource=defaultdict(list)
    for row in records: by_resource[row["resource"]].append(row)
    ownership={rid:sorted({r["module"] for r in rows}) for rid,rows in sorted(by_resource.items())}
    for prefix,kind,code,domain,label in (("source:","source_create","duplicate-source-owner","render_ownership","literal source"),("layer:","layer_create","duplicate-layer-owner","render_ownership","literal layer"),("feature-state:","feature_state_write","feature-state-owner-collision","feature_state","feature-state key")):
        for rid,rows in sorted(by_resource.items()):
            if not rid.startswith(prefix): continue
            writers={r["module"] for r in rows if r["kind"]==kind and r["confidence"]=="high"}
            if len(writers)>1 and not contract_shared(contract,rid,writers): findings.append(finding(code,"error",domain,f"{label} has multiple uncontracted owners: {rid}",[rid],list(writers),"Declare intentional sharing with rationale or converge ownership."))
    owners=contract.get("owners") or {}
    if isinstance(owners,dict):
        for rid,mods in sorted(owners.items()):
            declared=mods if isinstance(mods,list) else [mods]
            for mod in declared:
                if mod not in existing_modules: findings.append(finding("declared-owner-module-missing","error","render_ownership",f"Declared owner module is absent: {mod}",[rid],[mod],"Update the owner or remove the stale declaration."))
            observed=set(ownership.get(rid) or [])
            if observed and not observed<=set(declared) and not contract_shared(contract,rid,observed): findings.append(finding("declared-owner-conflict","error","render_ownership",f"Observed owner contradicts canonical owner for {rid}",[rid],list(observed|set(declared)),"Converge the writer or document intentional sharing."))
    for section in ("shared","ignore"):
        entries=contract.get(section) or {}
        if not isinstance(entries,dict): continue
        for rid in sorted(entries):
            matched=rid in by_resource if section=="shared" else any(rid in row["resource"] for row in records)
            if not matched: findings.append(finding("stale-contract-entry","warning","render_ownership",f"Contract {section} entry no longer matches live inventory: {rid}",[rid],remediation="Remove or narrow the stale contract entry."))
    for row in records:
        if row["kind"]=="popup" and row["details"].get("transient") and not row["details"].get("has_hover_class"): findings.append(finding("transient-popup-class-missing","error","popup_interaction",f"Transient hover popup is not marked with .atlas-hover in {row['module']}",[row["resource"]],[row["module"]],"Add the canonical atlas-hover marker or classify the popup as persistent/click-owned."))
    style_rows=[r for r in records if r["kind"]=="style_restore"]; style_modules=sorted({r["module"] for r in style_rows}); cfg=contract.get("style_restoration") or {}; allowed=cfg.get("allowed_modules") if isinstance(cfg,dict) else None
    if isinstance(allowed,dict):
        for mod in style_modules:
            row=next(r for r in style_rows if r["module"]==mod)
            if mod not in allowed: findings.append(finding("unapproved-style-restorer","warning","style_lifecycle",f"Style restoration participant is not declared in the contract: {mod}",[row["resource"]],[mod],"Document the intentional restorer or converge it into an approved lifecycle owner."))
            elif not row["details"].get("deferred"): findings.append(finding("style-restorer-undeferred","warning","style_lifecycle",f"Approved style restorer is not deferred: {mod}",[row["resource"]],[mod],"Defer restoration so style mutation settles before resource recreation."))
            elif mod!="world-map/3d-render-stack.js" and not row["details"].get("guarded"): findings.append(finding("style-restorer-unguarded","warning","style_lifecycle",f"Approved physical style restorer lacks a reentrancy guard: {mod}",[row["resource"]],[mod],"Add a restoration guard."))
        for mod in sorted(set(allowed)-set(style_modules)): findings.append(finding("stale-style-restorer-contract","warning","style_lifecycle",f"Approved style restorer no longer participates in styledata: {mod}",[f"style-restore:{mod}"],[mod],"Remove the stale contract entry."))
    elif len(style_modules)>1: findings.append(finding("multiple-style-restorers","warning","style_lifecycle",f"{len(style_modules)} modules independently participate in styledata restoration.",[f"style-restore:{m}" for m in style_modules],style_modules,"Keep restoration idempotent and coordinated."))
    allowed_slots=set(contract.get("render_stack_slots") or DEFAULT_RENDER_STACK_SLOTS)
    for row in records:
        if row["kind"]=="render_stack" and row["details"].get("slot") not in allowed_slots: findings.append(finding("unknown-render-stack-slot","error","render_ownership",f"Unknown render-stack slot {row['details'].get('slot')!r} in {row['module']}",[row["resource"]],[row["module"]],"Use a canonical slot or extend the contract deliberately."))
    for prefix,kind,code,domain in (("set-data:","set_data","multiple-setdata-writers","data_mutation"),("url:","url_write","multiple-url-writers","url_state"),("dom:","dom_id","multiple-dom-creators","dom_ownership"),("api:","public_api","multiple-api-assigners","event_lifecycle")):
        for rid,rows in sorted(by_resource.items()):
            if not rid.startswith(prefix): continue
            mods={r["module"] for r in rows if r["kind"]==kind}
            if len(mods)>1 and not contract_shared(contract,rid,mods): findings.append(finding(code,"warning",domain,f"Mutable resource has multiple writers: {rid}",[rid],list(mods),"Confirm a canonical owner or declare intentional sharing with rationale."))
    findings.sort(key=lambda x:(0 if x["severity"]=="error" else 1 if x["severity"]=="warning" else 2,x["domain"],x["code"],x["message"])); return findings,ownership

def build_report(records,findings,ownership):
    inv=defaultdict(list)
    for row in records: inv[row["kind"]].append(row)
    inventory={k:sorted(v,key=lambda r:(r["resource"],r["module"],r["line"])) for k,v in sorted(inv.items())}; domains={d:0 for d in RISK_DOMAINS}
    for item in findings: domains[item["domain"]]=domains.get(item["domain"],0)+RISK_WEIGHTS.get(item["severity"],0)
    summary={"modules":len({r["module"] for r in records}),"resources":len(ownership),"errors":sum(i["severity"]=="error" for i in findings),"warnings":sum(i["severity"]=="warning" for i in findings),"notes":sum(i["severity"]=="note" for i in findings),"risk_score":min(100,sum(domains.values()))}; actions=[{"domain":d,"risk":s} for d,s in sorted(domains.items(),key=lambda p:(-p[1],p[0])) if s>0][:5]
    return {"schema_version":SCHEMA_VERSION,"generated_at":datetime.now(timezone.utc).isoformat(),"scope":"world-map","summary":summary,"inventory":inventory,"ownership":{k:ownership[k] for k in sorted(ownership)},"findings":findings,"risk_domains":dict(sorted(domains.items())),"next_actions":actions}
def parse_args(argv=None):
    p=argparse.ArgumentParser(); root=Path(__file__).resolve().parents[1]; p.add_argument("--root",type=Path,default=root); p.add_argument("--contract",type=Path); p.add_argument("--report",type=Path); return p.parse_args(argv)
def main(argv=None):
    args=parse_args(argv); root=args.root.resolve(); contract_path=(args.contract or root/"data/world-map-audit-contract.json").resolve(); report_path=(args.report or root/"world-map-audit-report.json").resolve()
    try:
        modules=discover_modules(root); records=[]
        for path in modules: records.extend(scan_module(path,root))
        records.sort(key=lambda r:(r["resource"],r["module"],r["line"],r["kind"])); contract=load_contract(contract_path); findings,ownership=analyze(records,contract,{p.relative_to(root).as_posix() for p in modules}); report=build_report(records,findings,ownership); report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    except (OSError,ValueError,json.JSONDecodeError) as exc: print(f"WORLD MAP ARCHITECTURE AUDIT FAILED TO RUN: {exc}",file=sys.stderr); return 2
    s=report["summary"]; print(f"WORLD MAP ARCHITECTURE AUDIT {'FAILED' if s['errors'] else 'PASSED'} · {s['modules']} modules · {s['resources']} resources · {s['errors']} errors · {s['warnings']} warnings · risk {s['risk_score']}")
    for item in report["findings"][:12]: print(f"- {item['severity'].upper()} {item['code']}: {item['message']}")
    return 1 if s["errors"] else 0
if __name__=="__main__": raise SystemExit(main())
