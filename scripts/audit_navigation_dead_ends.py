#!/usr/bin/env python3
"""Advisory/guardrail audit for active public reader wayfinding."""
from pathlib import Path
import json,re,sys

ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/"data/house/public-surfaces.json"
OUT=ROOT/".quality-logs/navigation-dead-end-audit.json"

def route_path(route):
    route=(route or "/").strip()
    if route=="/":
        return ROOT/"index.html"
    clean=route.strip("/")
    if clean.endswith(".html"):
        return ROOT/clean
    return ROOT/clean/"index.html"

def main():
    data=json.loads(REG.read_text(encoding="utf-8"))
    rows=[]
    hard_errors=[]
    for s in data.get("surfaces",[]):
        if s.get("status")!="active":
            continue
        route=s.get("canonical_route","")
        p=route_path(route)
        if not p.exists():
            rows.append({"id":s.get("id"),"route":route,"missing":True})
            continue
        html=p.read_text(encoding="utf-8")
        nav=(re.search(r"<nav\b[\s\S]*?</nav>",html,re.I) or [None])[0]
        h1=(re.search(r"<h1\b[^>]*>([\s\S]*?)</h1>",html,re.I) or [None,None])[1]
        h1=re.sub(r"<[^>]+>"," ",h1 or "")
        h1=re.sub(r"\s+"," ",h1).strip()
        home_ok = route=="/" or bool(nav and re.search(r'href="(?:\.\./)*"|href="/?TimDooley/?(?:index\.html)?"',nav,re.I))
        literal_home = route=="/" or bool(nav and re.search(r">\s*(?:←\s*)?Home\s*</a>",nav,re.I))
        link_count=len(re.findall(r"<a\b",nav or "",re.I))
        rows.append({"id":s.get("id"),"route":route,"path":str(p.relative_to(ROOT)),"h1":h1,"nav_links":link_count,"home_route_detected":home_ok,"literal_home_label":literal_home})
        if route in {"/tim-dooley/","/potatoism/","/religion/","/philosophy/","/science/","/world/","/timeline/","/works/","/context/source-authority/"}:
            if not literal_home:
                hard_errors.append(f"{route} lacks literal Home in primary nav")
            if link_count < 3:
                hard_errors.append(f"{route} primary nav is too sparse ({link_count} links)")
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps({"generated_by":"scripts/audit_navigation_dead_ends.py","surfaces":rows,"hard_errors":hard_errors},indent=2)+"\n",encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"active surfaces: {len(rows)}; hard wayfinding errors: {len(hard_errors)}")
    if hard_errors:
        for e in hard_errors: print("- "+e)
        sys.exit(1)

if __name__=="__main__":
    main()
