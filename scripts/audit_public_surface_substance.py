#!/usr/bin/env python3
"""Audit public-surface substance against declared reader missions.

This is a prioritization diagnostic, not a truth/importance ranking. It asks
whether each registered public surface has enough static substance, object/source
anchors and degraded-mode value for the job it declares.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/".quality-logs"
OUT.mkdir(exist_ok=True)

TAG_RE=re.compile(r"<[^>]+>",re.S)
SCRIPT_STYLE_RE=re.compile(r"<(?:script|style)\b[^>]*>.*?</(?:script|style)>",re.I|re.S)
NAV_RE=re.compile(r"<nav\b[^>]*>.*?</nav>",re.I|re.S)
MAIN_RE=re.compile(r"<main\b[^>]*>(.*?)</main>",re.I|re.S)
H_RE=re.compile(r"<h[1-4]\b",re.I)
SECTION_RE=re.compile(r"<section\b",re.I)
LINK_RE=re.compile(r"<a\b[^>]*href=[\"']([^\"']+)[\"']",re.I)
FETCH_RE=re.compile(r"\bfetch\s*\(",re.I)
SCRIPT_SRC_RE=re.compile(r"<script\b[^>]*src=[\"']",re.I)
INSPECT_RE=re.compile(r"(?:^|/)(?:data|knowledge)/|\.json(?:[#?]|$)|source-authority|evidence",re.I)

def load(rel):
    return json.loads((ROOT/rel).read_text(encoding="utf-8"))

def route_file(route:str)->Path:
    route=(route or "/").strip()
    if route=="/":
        return ROOT/"index.html"
    clean=route.strip("/")
    if clean.endswith(".html"):
        return ROOT/clean
    return ROOT/clean/"index.html"

def text_only(raw:str)->str:
    raw=SCRIPT_STYLE_RE.sub(" ",raw)
    raw=NAV_RE.sub(" ",raw)
    raw=TAG_RE.sub(" ",raw)
    return " ".join(raw.split())

def main()->int:
    surfaces=load("data/house/public-surfaces.json").get("surfaces",[])
    missions=load("data/house/public-surface-missions.json").get("surfaces",{})
    rows=[]
    missing=[]
    for surface in surfaces:
        if not isinstance(surface,dict) or surface.get("status")!="active":
            continue
        sid=surface.get("id")
        route=surface.get("canonical_route") or surface.get("route") or "/"
        path=route_file(route)
        if not path.exists():
            missing.append({"surface_id":sid,"route":route,"expected_file":path.relative_to(ROOT).as_posix()})
            continue
        raw=path.read_text(encoding="utf-8",errors="replace")
        main_match=MAIN_RE.search(raw)
        authored=main_match.group(1) if main_match else raw
        static=SCRIPT_STYLE_RE.sub(" ",authored)
        static_no_nav=NAV_RE.sub(" ",static)
        visible=text_only(authored)
        links=LINK_RE.findall(static_no_nav)
        inspect_links=[href for href in links if INSPECT_RE.search(href)]
        mission=missions.get(sid,{})
        density=mission.get("density_intent")
        text_chars=len(visible)
        headings=len(H_RE.findall(static_no_nav))
        sections=len(SECTION_RE.findall(static_no_nav))
        link_count=len(links)
        fetch_count=len(FETCH_RE.findall(raw))
        script_count=len(SCRIPT_SRC_RE.findall(raw))
        flags=[]
        if text_chars<1800:
            flags.append("thin-static-body")
        elif text_chars<3500 and density in {"balanced","deep-but-tiered","deep-runtime","balanced-runtime"}:
            flags.append("light-for-declared-density")
        if fetch_count>=2 and text_chars<3500:
            flags.append("runtime-heavy-static-fallback-risk")
        if link_count>=35 and text_chars<4200:
            flags.append("directory-heavy-reader-risk")
        if density in {"balanced","deep-but-tiered","deep-runtime","balanced-runtime"} and len(inspect_links)==0:
            flags.append("weak-source-object-escape")
        if headings<3 and density not in {"compact","compact-runtime"}:
            flags.append("weak-static-structure")
        if sections==0 and density not in {"compact","focused"}:
            flags.append("no-authored-sections")
        severity=sum({
            "thin-static-body":4,
            "runtime-heavy-static-fallback-risk":3,
            "directory-heavy-reader-risk":2,
            "weak-source-object-escape":2,
            "light-for-declared-density":2,
            "weak-static-structure":1,
            "no-authored-sections":1,
        }.get(flag,1) for flag in flags)
        rows.append({
            "surface_id":sid,
            "title":surface.get("title"),
            "route":route,
            "surface_type":surface.get("surface_type"),
            "visibility":surface.get("visibility"),
            "primary_parent":surface.get("primary_parent"),
            "reader_job":surface.get("reader_job"),
            "density_intent":density,
            "metrics":{
                "static_text_chars":text_chars,
                "headings_h1_h4":headings,
                "sections":sections,
                "static_links":link_count,
                "inspect_source_object_links":len(inspect_links),
                "runtime_fetch_calls":fetch_count,
                "external_script_tags":script_count,
            },
            "flags":flags,
            "priority_weight":severity,
        })
    rows.sort(key=lambda r:(-r["priority_weight"],r["metrics"]["static_text_chars"],r["surface_id"]))
    report={
        "version":"1.0.0",
        "generated_from":"source HTML + data/house/public-surfaces.json + public-surface-missions.json",
        "purpose":"Prioritize public-surface development by static substance, degraded-mode usefulness, object/source escape and declared mission. Not a truth, importance or quality score.",
        "thresholds":{
            "thin_static_chars":1800,
            "runtime_risk":"2+ fetch() calls and <3500 static text characters",
            "directory_risk":"35+ static links and <4200 static text characters",
        },
        "surface_count":len(rows),
        "missing_source_pages":missing,
        "flagged_count":sum(1 for r in rows if r["flags"]),
        "priority_surfaces":[r for r in rows if r["flags"]][:20],
        "surfaces":rows,
    }
    (OUT/"public-surface-substance-audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if missing:
        print("PUBLIC SURFACE SUBSTANCE AUDIT FAILED")
        for row in missing:
            print("-",row)
        return 1
    print(f"PUBLIC SURFACE SUBSTANCE AUDIT: {len(rows)} active surfaces · {report['flagged_count']} heuristic flags")
    for row in report["priority_surfaces"][:12]:
        print(f"- {row['surface_id']}: weight={row['priority_weight']} flags={','.join(row['flags']) or 'none'} chars={row['metrics']['static_text_chars']}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
