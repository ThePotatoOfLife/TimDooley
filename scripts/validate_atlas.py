#!/usr/bin/env python3
"""Validate the relationship-first atlas before deployment."""
from __future__ import annotations
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []
WARNINGS: list[str] = []

def load_json(path: Path):
    try:
        with path.open(encoding="utf-8") as f: return json.load(f)
    except Exception as exc:
        ERRORS.append(f"Invalid JSON: {path.relative_to(ROOT)} — {exc}"); return None

def check_exists(rel: str, required: bool = True):
    path = ROOT / rel
    if not path.exists(): (ERRORS if required else WARNINGS).append(f"Missing {'required' if required else 'optional'} path: {rel}"); return False
    return True

def check_beliefs():
    space=load_json(ROOT/"data/belief-space.json") or {}; backend=load_json(ROOT/"data/belief-backend.json") or {}; preg=load_json(ROOT/"data/political-lexicon.json") or {}; rreg=load_json(ROOT/"data/religious-lexicon.json") or {}; registry=load_json(ROOT/"data/belief-registry.json") or {}
    for rel in ["belief.html","political-compass.html","data/belief-space.json","data/belief-backend.json","data/belief-registry.json","data/political-lexicon.json","data/religious-lexicon.json"]: check_exists(rel)
    if not space.get("political",{}).get("axes") or not space.get("religious",{}).get("axes"): ERRORS.append("Belief space must define both political and religious three-axis models")
    political=preg.get("entries",[]); religious=rreg.get("entries",[])
    if not political: ERRORS.append("Political lexicon has no entries")
    if not religious: ERRORS.append("Religious lexicon has no entries")
    pids=[e[0] for e in political if isinstance(e,list) and len(e)>=2]; rids=[e[0] for e in religious if isinstance(e,list) and len(e)>=2]
    if len(pids)!=len(set(pids)): ERRORS.append("Political lexicon contains duplicate IDs")
    if len(rids)!=len(set(rids)): ERRORS.append("Religious lexicon contains duplicate IDs")
    if set(pids)&set(rids): ERRORS.append("Political and religious lexicons contain colliding IDs")
    for e in political:
        if not isinstance(e,list) or len(e)<5: ERRORS.append("Political lexicon entry has an invalid shape"); continue
        if not isinstance(e[2],(int,float)) or not isinstance(e[3],(int,float)): ERRORS.append(f"Political entry has invalid coordinates: {e[0]}")
        elif not all(-10<=float(v)<=10 for v in e[2:4]): ERRORS.append(f"Political coordinates outside -10..10: {e[0]}")
    if backend.get("individualRecord")!="belief.html?id=<slug>": ERRORS.append("Belief backend individualRecord route is incorrect")
    if registry.get("politics",{}).get("map")!="political-compass.html": WARNINGS.append("Belief registry politics map does not point to the belief-space UI")
    if registry.get("religion",{}).get("map")!="political-compass.html": WARNINGS.append("Belief registry religion map does not point to the belief-space UI")
    return len(political),len(religious)

def main()->int:
    backend=load_json(ROOT/"data/backend.json") or {}; endpoints=backend.get("endpoints",{}); required=set(backend.get("required",[]))
    for key,value in endpoints.items():
        rel=value if isinstance(value,str) else value.get("path","") if isinstance(value,dict) else ""
        if not rel: ERRORS.append(f"Backend endpoint has no path: {key}"); continue
        if check_exists(rel,key in required) and rel.endswith(".json"): load_json(ROOT/rel)
    nations=load_json(ROOT/"data/nations.json") or {}; country_index=load_json(ROOT/"data/countries/index.json") or {}; country_repair=load_json(ROOT/"data/countries/democratic-republic-of-the-congo.json") or {}; enrichment_index=load_json(ROOT/"data/country-enrichment-index.json") or {}; country_nodes=load_json(ROOT/"data/country-nodes.json") or {}; graph_registry=load_json(ROOT/"data/graph-registry.json") or {}; relationships=load_json(ROOT/"data/relationships.json") or {}; nodes=load_json(ROOT/"data/nodes.json") or {}; children=load_json(ROOT/"data/tree-child-records.json") or {}; tree=load_json(ROOT/"data/tree.json") or {}
    nation_rows=nations.get("nations",[]); country_rows=country_index.get("countries",[]); repair_id=country_repair.get("id"); base_country_rows=[x for x in country_rows if x.get("id")!=repair_id]; enriched_ids=enrichment_index.get("enriched_ids",[]); country_node_rows=country_nodes.get("nodes",[])
    if len(nation_rows)!=195: ERRORS.append(f"Canonical nation directory has {len(nation_rows)} records; expected 195")
    if len(base_country_rows)+(1 if repair_id else 0)!=195: ERRORS.append(f"Country layer has {len(base_country_rows)} base records + {1 if repair_id else 0} repair records; expected 195")
    nation_ids={x.get("id") for x in nation_rows}; country_ids={x.get("id") for x in base_country_rows}|({repair_id} if repair_id else set())
    if nation_ids!=country_ids: ERRORS.append("Canonical nation directory and repaired country layer do not contain the same country IDs")
    for cid in sorted(country_ids):
        if not (ROOT/"data/countries"/f"{cid}.json").exists(): ERRORS.append(f"Missing canonical country record: data/countries/{cid}.json")
    enriched_set=set(enriched_ids)
    if enriched_set-country_ids: ERRORS.append(f"Enrichment index contains unknown country IDs: {sorted(enriched_set-country_ids)}")
    node_country_ids={x.get("country_id") for x in country_node_rows}
    if node_country_ids!=enriched_set: ERRORS.append("Country graph nodes and enrichment index are out of sync")
    for cid in sorted(enriched_set):
        if not (ROOT/"data/countries"/f"{cid}-enrichment.json").exists(): ERRORS.append(f"Enrichment index points to missing overlay: {cid}-enrichment.json")
    graph_ids=set(x.get("id") for x in nodes.get("nodes",[]) if x.get("id")); graph_ids.update(x.get("id") for x in children.get("records",[]) if x.get("id")); graph_ids.update(x.get("id") for x in country_node_rows if x.get("id")); graph_ids.update(x.get("id") for x in graph_registry.get("records",[]) if x.get("id")); graph_ids.update(country_ids); graph_ids.update(nation_ids)
    tree_ids=set()
    for level in tree.get("levels",[]):
        if level.get("id"): tree_ids.add(level["id"])
        tree_ids.update(x for x in level.get("children",[]) if x)
    WARNINGS.extend(f"Tree references a record not yet promoted into the graph registry: {x}" for x in sorted(tree_ids-graph_ids))
    for rel in relationships.get("relationships",[]):
        if not rel.get("id"): ERRORS.append("Relationship without id")
        for side in ("source","target"):
            endpoint=rel.get(side)
            if endpoint and endpoint not in graph_ids: ERRORS.append(f"Relationship {rel.get('id','?')} has unknown {side}: {endpoint}")
    local_ref=re.compile(r'''(?:href|src)=["']([^"'#?]+)["']''',re.I)
    for html in ROOT.glob("*.html"):
        text=html.read_text(encoding="utf-8",errors="replace")
        for ref in local_ref.findall(text):
            if ref.startswith(("http://","https://","mailto:","javascript:","data:")): continue
            target=(ROOT/ref).resolve()
            try: target.relative_to(ROOT.resolve())
            except ValueError: continue
            if not target.exists(): WARNINGS.append(f"Local HTML reference does not exist: {html.name} → {ref}")
    if len(enriched_set)!=backend.get("countryLayer",{}).get("enrichedCount",len(enriched_set)): ERRORS.append("Backend countryLayer.enrichedCount disagrees with enrichment index")
    if len(country_node_rows)!=backend.get("countryLayer",{}).get("nodeCount",len(country_node_rows)): ERRORS.append("Backend countryLayer.nodeCount disagrees with country-nodes.json")
    pc,rc=check_beliefs()
    print(f"Canonical nations: {len(nation_rows)}/195"); print(f"Country layer: {len(country_ids)}/195"); print(f"Enrichment overlays: {len(enriched_set)}"); print(f"Country graph nodes: {len(country_node_rows)}"); print(f"Graph registry records: {len(graph_registry.get('records',[]))}"); print(f"Relationships checked: {len(relationships.get('relationships',[]))}"); print(f"Political beliefs: {pc} · Religious beliefs: {rc}"); print(f"Errors: {len(ERRORS)} · Warnings: {len(WARNINGS)}")
    for message in WARNINGS[:50]: print(f"WARNING: {message}")
    for message in ERRORS[:100]: print(f"ERROR: {message}")
    return 1 if ERRORS else 0
if __name__=="__main__": raise SystemExit(main())
