#!/usr/bin/env python3
"""Second-pass content audit for unfinished markers, references and canonical architecture records."""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; ERRORS=[]
_TERMS=["TO"+"DO","FIX"+"ME","T"+"BD","T"+"BA","COMING"+" SOON","UNDER"+" CONSTRUCTION"]
BAD_TERMS=re.compile(r"\b(?:"+"|".join(map(re.escape,_TERMS))+r")\b",re.I)

def load(rel):
    p=ROOT/rel
    try:return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:ERRORS.append(f"Invalid JSON: {rel}: {e}");return {}

def main():
    nations=load("data/nations.json").get("nations",[])
    if len(nations)!=195:ERRORS.append(f"nations.json has {len(nations)} records; expected 195")
    levels=load("data/33-level-framework.json").get("levels",[])
    if len(levels)!=33:ERRORS.append(f"33-level-framework.json has {len(levels)} levels; expected 33")
    if [x.get("number") for x in levels]!=list(range(1,34)):ERRORS.append("33-level-framework.json levels must be numbered 1 through 33 without gaps")
    tree=load("data/tree.json"); nodes=load("data/nodes.json").get("nodes",[]); children=load("data/tree-child-records.json").get("records",[]); support=load("data/tree-support-records.json").get("records",[])
    known={x.get("id") for x in nodes+children+support if x.get("id")}|{"33-levels"}
    for level in tree.get("levels",[]):
        for child in level.get("children",[]):
            if child not in known:ERRORS.append(f"Tree child has no registered record: {level.get('id')} -> {child}")
    backend=load("data/backend.json")
    for name,path in backend.get("endpoints",{}).items():
        if isinstance(path,str) and not(ROOT/path).exists():ERRORS.append(f"Backend endpoint {name} points to missing file: {path}")
    manifest=load("data/atlas-manifest.json")
    for required in ("data/tree.json","data/project-workflow.json","data/backend.json","data/entanglement.json","data/axis-topology.json","data/hawkins-scale.json"):
        if not (ROOT/required).exists():ERRORS.append(f"Canonical architecture file missing: {required}")
    flat_manifest={x for layer in manifest.get("layers",{}).values() if isinstance(layer,dict) for x in layer.get("files",[])}
    for required in ("data/entanglement.json","data/axis-topology.json","data/hawkins-scale.json"):
        if required not in flat_manifest:ERRORS.append(f"Manifest does not register canonical file: {required}")
    graph=load("data/graph-registry.json"); graph_ids={x.get("id") for x in graph.get("records",[])}
    for rid in ("entanglement","axis-topology","hawkins-scale","trajectory","path-dependence","threshold","phase-transition","connection","coupling","flow","feedback","cycle","networks","dependencies","topology","phases","outcome"):
        if rid in {x.get("id") for x in children}:continue
        if rid not in graph_ids and rid not in known:ERRORS.append(f"Canonical relational ID is not registered: {rid}")
    axis=load("data/axis-topology.json")
    if set(axis.get("terrain",{}))!={"axis","mountain","plane","mud","swamp","roots","drain","door"}:ERRORS.append("Axis topology terrain vocabulary is incomplete")
    ent=load("data/entanglement.json")
    required_ent={"coupling","dependency","correlation","distance","feedback","topology","trajectory","phase"}
    if not required_ent.issubset(set(ent.get("dimensions",[]))):ERRORS.append("Entanglement schema is missing required dimensions")
    haw=load("data/hawkins-scale.json")
    if len(haw.get("levels",[]))!=17:ERRORS.append("Hawkins scale must contain 17 principal levels")
    if haw.get("physical_frequency_guardrail") is not True:ERRORS.append("Hawkins physical-frequency guardrail must be true")
    if haw.get("electromagnetic_mapping") not in ("symbolic_only","not_supported_as_physical_mapping"):ERRORS.append("Hawkins electromagnetic mapping must remain non-physical")
    workflow=load("data/project-workflow.json")
    if not any(x.get("id")=="emotion-state" for x in workflow.get("phases",[])):ERRORS.append("Workflow missing emotion-state phase")
    if not any(x.get("id")=="release-audit" for x in workflow.get("phases",[])):ERRORS.append("Workflow missing release-audit phase")
    extensions={".html",".js",".css",".json",".py",".yml",".yaml"}; ignored={".git","node_modules","vendor"}
    for p in ROOT.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in extensions or any(part in ignored for part in p.parts):continue
        try:text=p.read_text(encoding="utf-8",errors="replace")
        except Exception:continue
        for m in BAD_TERMS.finditer(text):ERRORS.append(f"Unfinished-work marker in {p.relative_to(ROOT)}:{text.count(chr(10),0,m.start())+1}")
    for p in list(ROOT.glob("*.html"))+list((ROOT/"data").glob("*.json")):
        if p.is_file() and p.stat().st_size==0:ERRORS.append(f"Empty publishing/data file: {p.relative_to(ROOT)}")
    print(f"Content integrity errors: {len(ERRORS)}")
    for e in ERRORS[:200]:print("ERROR:",e)
    return 1 if ERRORS else 0
if __name__=="__main__":raise SystemExit(main())
