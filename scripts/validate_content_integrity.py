#!/usr/bin/env python3
"""Second-pass content audit for accidental unfinished-work markers and broken references."""
from __future__ import annotations
import json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ERRORS=[]
_TERMS=["TO"+"DO","FIX"+"ME","T"+"BD","T"+"BA","COMING"+" SOON","UNDER"+" CONSTRUCTION"]
BAD_TERMS=re.compile(r"\b(?:"+"|".join(map(re.escape,_TERMS))+r")\b",re.I)

def load(rel):
    p=ROOT/rel
    try: return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        ERRORS.append(f"Invalid JSON: {rel}: {e}"); return {}

def main():
    nations=load("data/nations.json").get("nations",[])
    if len(nations)!=195: ERRORS.append(f"nations.json has {len(nations)} records; expected 195")
    levels=load("data/33-level-framework.json").get("levels",[])
    if len(levels)!=33: ERRORS.append(f"33-level-framework.json has {len(levels)} levels; expected 33")
    if [x.get("number") for x in levels] != list(range(1,34)): ERRORS.append("33-level-framework.json levels must be numbered 1 through 33 without gaps")
    tree=load("data/tree.json")
    nodes=load("data/nodes.json").get("nodes",[]); children=load("data/tree-child-records.json").get("records",[]); support=load("data/tree-support-records.json").get("records",[])
    known={x.get("id") for x in nodes+children+support if x.get("id")} | {"33-levels"}
    for level in tree.get("levels",[]):
        for child in level.get("children",[]):
            if child not in known: ERRORS.append(f"Tree child has no registered record: {level.get('id')} -> {child}")
    backend=load("data/backend.json")
    for name,path in backend.get("endpoints",{}).items():
        if isinstance(path,str) and not (ROOT/path).exists(): ERRORS.append(f"Backend endpoint {name} points to missing file: {path}")
    extensions={".html",".js",".css",".json",".py",".yml",".yaml"}; ignored={".git","node_modules","vendor"}
    for p in ROOT.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in extensions or any(part in ignored for part in p.parts): continue
        try: text=p.read_text(encoding="utf-8",errors="replace")
        except Exception: continue
        for m in BAD_TERMS.finditer(text):
            line=text.count("\n",0,m.start())+1; ERRORS.append(f"Unfinished-work marker in {p.relative_to(ROOT)}:{line}")
    for p in list(ROOT.glob("*.html"))+list((ROOT/"data").glob("*.json")):
        if p.is_file() and p.stat().st_size==0: ERRORS.append(f"Empty publishing/data file: {p.relative_to(ROOT)}")
    print(f"Content integrity errors: {len(ERRORS)}")
    for e in ERRORS[:200]: print("ERROR:",e)
    return 1 if ERRORS else 0

if __name__=="__main__": raise SystemExit(main())
