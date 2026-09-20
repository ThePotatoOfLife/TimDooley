#!/usr/bin/env python3
"""Validate that House inhabitant routes resolve to source or declared generated surfaces."""
from __future__ import annotations
import json,re
from pathlib import Path
from urllib.parse import urlsplit,unquote

ROOT=Path(__file__).resolve().parents[1]
INH=ROOT/"data/house/room-inhabitants.json"

GENERATED_PREFIXES=("/records/",)
DYNAMIC_ANCHOR_SOURCES={
    "/tim-dooley/story/": (ROOT/"story-content",),
}
SOURCE_ROUTE_ALIASES={
    "/": ROOT/"index.html",
}

def load(p): return json.loads(p.read_text(encoding="utf-8"))

def source_path_for(route_path:str):
    if route_path in SOURCE_ROUTE_ALIASES: return SOURCE_ROUTE_ALIASES[route_path]
    rel=route_path.lstrip("/")
    if not rel: return ROOT/"index.html"
    if rel.endswith(".html"): return ROOT/rel
    return ROOT/rel/"index.html"

def has_anchor(text:str,anchor:str)->bool:
    a=re.escape(anchor)
    return re.search(rf'id=["\']{a}["\']',text,re.I) is not None or re.search(rf'name=["\']{a}["\']',text,re.I) is not None

def main():
    errors=[]
    rows=load(INH).get("inhabitants",[])
    for row in rows:
        if not isinstance(row,dict): continue
        rid=row.get("id","(unknown)")
        route=row.get("route")
        if not route:
            errors.append(f"{rid} has no route")
            continue
        if route.startswith(("http://","https://")):
            continue
        parts=urlsplit(route)
        path=unquote(parts.path or "/")
        if any(path.startswith(p) for p in GENERATED_PREFIXES):
            continue
        target=source_path_for(path)
        if not target.exists():
            errors.append(f"{rid} route missing source target: {route} -> {target.relative_to(ROOT)}")
            continue
        if parts.fragment:
            text=target.read_text(encoding="utf-8",errors="replace")
            if has_anchor(text,parts.fragment):
                continue
            ok=False
            for root in DYNAMIC_ANCHOR_SOURCES.get(path,()):
                if root.exists():
                    for html in root.rglob("*.html"):
                        if has_anchor(html.read_text(encoding="utf-8",errors="replace"),parts.fragment):
                            ok=True;break
                if ok: break
            if not ok:
                errors.append(f"{rid} route anchor missing: {route}")
    if errors:
        print("HOUSE INHABITANT ROUTE VALIDATION FAILED")
        for e in errors: print("-",e)
        return 1
    print(f"HOUSE INHABITANT ROUTE VALIDATION PASSED: {len(rows)} inhabitant routes resolve by source/generated rules")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
