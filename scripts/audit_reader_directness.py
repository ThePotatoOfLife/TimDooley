#!/usr/bin/env python3
"""Audit active public readers for maintenance-language leakage and exact repeated paragraphs.

This is intentionally advisory. Architectural pages may legitimately use terms such as
"projection" or "owner"; the report exists to make concentration and cross-page repetition
visible so editors can decide whether the reader is learning the subject or the filing system.
"""
from __future__ import annotations
import json, re
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SURFACES=ROOT/"data/house/public-surfaces.json"
OUT=ROOT/".quality-logs/reader-directness-audit.json"

TERMS=[
    "backend","projection","canonical owner","public surface","registry",
    "machine-readable","this page","this reader","the page should",
    "the reader should","the site should","the homepage","owner"
]

def route_to_path(route:str)->Path:
    if route=="/":
        return ROOT/"index.html"
    return ROOT/route.strip("/")/"index.html"

def strip_html(html:str)->str:
    html=re.sub(r"<script\b[\s\S]*?</script>"," ",html,flags=re.I)
    html=re.sub(r"<style\b[\s\S]*?</style>"," ",html,flags=re.I)
    return html

def paragraphs(html:str):
    body=strip_html(html)
    for m in re.finditer(r"<p\b[^>]*>([\s\S]*?)</p>",body,flags=re.I):
        txt=re.sub(r"<[^>]+>"," ",m.group(1))
        txt=re.sub(r"&[a-zA-Z0-9#]+;"," ",txt)
        txt=re.sub(r"\s+"," ",txt).strip()
        if len(txt)>=90:
            yield txt

def norm(txt:str)->str:
    return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9]+"," ",txt.lower())).strip()

def main():
    data=json.loads(SURFACES.read_text(encoding="utf-8"))
    surfaces=[s for s in data.get("surfaces",[]) if s.get("status")=="active"]
    report={"generated_by":"scripts/audit_reader_directness.py","terms":TERMS,"surfaces":[],"exact_duplicate_paragraphs":[]}
    dup=defaultdict(list)

    for s in surfaces:
        path=route_to_path(s["canonical_route"])
        if not path.exists():
            report["surfaces"].append({"id":s["id"],"route":s["canonical_route"],"missing_html":str(path.relative_to(ROOT))})
            continue
        html=path.read_text(encoding="utf-8")
        visible=strip_html(html)
        low=visible.lower()
        counts={t:low.count(t) for t in TERMS}
        paras=list(paragraphs(html))
        for p in paras:
            dup[norm(p)].append({"surface_id":s["id"],"route":s["canonical_route"],"text":p})
        report["surfaces"].append({
            "id":s["id"],"route":s["canonical_route"],"path":str(path.relative_to(ROOT)),
            "maintenance_term_hits":counts,
            "maintenance_hit_total":sum(counts.values()),
            "paragraph_count":len(paras)
        })

    for rows in dup.values():
        routes=sorted({r["route"] for r in rows})
        if len(routes)>1:
            report["exact_duplicate_paragraphs"].append({"routes":routes,"text":rows[0]["text"]})
    report["exact_duplicate_paragraphs"].sort(key=lambda x:(-len(x["text"]),x["routes"]))
    report["surfaces"].sort(key=lambda x:-x.get("maintenance_hit_total",0))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    for row in report["surfaces"][:12]:
        print(f"{row.get('maintenance_hit_total',0):3}  {row.get('route')}  {row.get('maintenance_term_hits',{})}")
    print(f"exact cross-surface duplicate paragraphs: {len(report['exact_duplicate_paragraphs'])}")

if __name__=="__main__":
    main()
