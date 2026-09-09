#!/usr/bin/env python3
"""Second-pass content audit for unfinished markers, references, schemas and canonical architecture records."""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; ERRORS=[]
_TERMS=["FIX"+"ME","T"+"BD","T"+"BA","COMING"+" SOON","UNDER"+" CONSTRUCTION"]
BAD_TERMS=re.compile(r"\b(?:"+"|".join(map(re.escape,_TERMS))+r")\b",re.I)
CONTROL_FILES={"data/depth-audit.json","scripts/validate_content_integrity.py"}
def load(rel):
    p=ROOT/rel
    try:return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:ERRORS.append(f"Invalid JSON: {rel}: {e}");return {}
def main():
    countries=load("data/countries/index.json").get("countries",[])
    if len(countries)!=195:ERRORS.append(f"countries/index.json has {len(countries)} records; expected 195")
    ids=[x.get("id") for x in countries]; iso3=[x.get("iso3") for x in countries]
    if len(ids)!=len(set(ids)):ERRORS.append("countries/index.json contains duplicate country IDs")
    if len(iso3)!=len(set(iso3)):ERRORS.append("countries/index.json contains duplicate ISO3 codes")
    levels=load("data/33-level-framework.json").get("levels",[])
    if len(levels)!=33:ERRORS.append(f"33-level-framework.json has {len(levels)} levels; expected 33")
    if [x.get("number") for x in levels]!=list(range(1,34)):ERRORS.append("33-level-framework.json levels must be numbered 1 through 33 without gaps")
    tree=load("data/tree.json"); nodes=load("data/nodes.json").get("nodes",[]); children=load("data/tree-child-records.json").get("records",[]); support=load("data/tree-support-records.json").get("records",[]); concepts=load("data/tree-concept-records.json").get("records",[])
    known={x.get("id") for x in nodes+children+support+concepts if x.get("id")}|{"33-levels"}
    for level in tree.get("levels",[]):
        for child in level.get("children",[]):
            if child not in known:ERRORS.append(f"Tree child has no registered record: {level.get('id')} -> {child}")
    backend=load("data/backend.json")
    for name,path in backend.get("endpoints",{}).items():
        if isinstance(path,str) and not(ROOT/path).exists():ERRORS.append(f"Backend endpoint {name} points to missing file: {path}")
    manifest=load("data/atlas-manifest.json"); flat_manifest={x for layer in manifest.get("layers",{}).values() if isinstance(layer,dict) for x in layer.get("files",[])}
    for required in ("data/tree.json","data/project-workflow.json","data/backend.json","data/entanglement.json","data/axis-topology.json","data/hawkins-scale.json","data/tree-concept-records.json"):
        if not (ROOT/required).exists():ERRORS.append(f"Canonical architecture file missing: {required}")
    for required in ("data/entanglement.json","data/axis-topology.json","data/hawkins-scale.json","data/tree-concept-records.json"):
        if required not in flat_manifest:ERRORS.append(f"Manifest does not register canonical file: {required}")
    research_path="data/research-carvings-2026-09.json"
    if not (ROOT/research_path).exists():ERRORS.append(f"Registered research layer missing: {research_path}")
    else:
        research=load(research_path); records=research.get("records",[])
        for rec in records:
            rid=rec.get("id","<missing-id>")
            for field in ("definition","context","mechanisms","dimensions","couplings","sources","project_extrapolations"):
                value=rec.get(field)
                if value in (None,"",[],{}):ERRORS.append(f"Research carving {rid} lacks substantive field: {field}")
        if not records:ERRORS.append("Research carving layer contains no records")
    graph=load("data/graph-registry.json"); graph_ids={x.get("id") for x in graph.get("records",[])}
    for rid in ("entanglement","axis-topology","hawkins-scale","trajectory","path-dependence","threshold","phase-transition","connection","coupling","flow","feedback","cycle","networks","dependencies","topology","phases","outcome"):
        if rid in {x.get("id") for x in children+concepts}:continue
        if rid not in graph_ids and rid not in known:ERRORS.append(f"Canonical relational ID is not registered: {rid}")
    axis=load("data/axis-topology.json")
    if set(axis.get("terrain",{}))!={"axis","mountain","plane","mud","swamp","roots","drain","door"}:ERRORS.append("Axis topology terrain vocabulary is incomplete")
    ent=load("data/entanglement.json"); required_ent={"source","target","relationship","distance","directionality","strength","dependency","coupling","correlation","causal_status","temporal_order","path_dependence","feedback","topology","boundary","trajectory","phase","counterfactual_sensitivity","evidence","confidence"}
    if not required_ent.issubset(set(ent.get("relational_dimensions",[]))):ERRORS.append("Entanglement schema is missing required relational dimensions")
    haw=load("data/hawkins-scale.json"); levels_h=haw.get("scale",haw.get("levels",[]))
    if len(levels_h)<17:ERRORS.append(f"Hawkins scale has {len(levels_h)} levels; expected at least 17 principal levels")
    if haw.get("physical_frequency_status")!="not_established":ERRORS.append("Hawkins physical-frequency guardrail must remain not_established")
    if "no validated one-to-one mapping" not in str(haw.get("em_spectrum_status","")).lower():ERRORS.append("Hawkins electromagnetic mapping must remain explicitly non-physical")
    workflow=load("data/project-workflow.json")
    phase_ids={x.get("id") for x in workflow.get("phases",[]) if isinstance(x,dict)}
    for phase in ("audit","canonicalize","deepen","potatoism-canon","spiritual-inquiry","evidence","website","release-audit"):
        if phase not in phase_ids:ERRORS.append(f"Workflow missing current phase: {phase}")
    extensions={".html",".js",".css",".json",".py",".yml",".yaml"}; ignored={".git","node_modules","vendor"}
    for p in ROOT.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in extensions or any(part in ignored for part in p.parts):continue
        rel=p.relative_to(ROOT).as_posix()
        if rel in CONTROL_FILES:continue
        try:text=p.read_text(encoding="utf-8",errors="replace")
        except Exception:continue
        for m in BAD_TERMS.finditer(text):ERRORS.append(f"Unfinished-work marker in {rel}:{text.count(chr(10),0,m.start())+1}")
    for p in list(ROOT.glob("*.html"))+list((ROOT/"data").glob("*.json")):
        if p.is_file() and p.stat().st_size==0:ERRORS.append(f"Empty publishing/data file: {p.relative_to(ROOT)}")
    print(f"Content integrity errors: {len(ERRORS)}")
    for e in ERRORS[:200]:print("ERROR:",e)
    return 1 if ERRORS else 0
if __name__=="__main__":raise SystemExit(main())
