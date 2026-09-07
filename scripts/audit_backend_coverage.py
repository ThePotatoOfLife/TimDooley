#!/usr/bin/env python3
"""Audit backend ownership, duplicate IDs and graph reachability.

The audit is deliberately report-first: invalid JSON is a hard failure, while
ownership debt, duplicate IDs and unresolved relationship endpoints are emitted
as actionable inventory diagnostics. Those diagnostics are often legitimate in
overlays, indexes and research expansions and should not make CI unusable.
"""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
COVERAGE=DATA/"backend-coverage-map.json"
BRIDGE=DATA/"global-graph-bridge.json"
MANIFEST=DATA/"atlas-manifest.json"
BACKEND=DATA/"backend.json"

def load(path):
    with path.open(encoding="utf-8") as f:return json.load(f)

def iter_json_files():return sorted(DATA.rglob("*.json"))

def object_ids(value):
    if isinstance(value,dict):
        if isinstance(value.get("id"),str) and value["id"].strip():yield value["id"].strip()
        keys={"records","nodes","items","entries","observations","relationships","edges","sources","waves","dimensions","layers","links"}
        for key in keys:
            if key in value:yield from object_ids(value[key])
        for key,child in value.items():
            if key not in keys and isinstance(child,(dict,list)):yield from object_ids(child)
    elif isinstance(value,list):
        for item in value:yield from object_ids(item)

def relationship_endpoints(value):
    if isinstance(value,dict):
        source=value.get("source") or value.get("from") or value.get("subject")
        target=value.get("target") or value.get("to") or value.get("object")
        if isinstance(source,str) and isinstance(target,str):yield source,target
        for child in value.values():
            if isinstance(child,(dict,list)):yield from relationship_endpoints(child)
    elif isinstance(value,list):
        for item in value:yield from relationship_endpoints(item)

def collect_registered_files(obj):
    found=set()
    if isinstance(obj,dict):
        for key,value in obj.items():
            if key in {"file","files","endpoint","source","owner","backend","canonicalManifest","maintenanceWorkflow"}:
                if isinstance(value,str) and value.startswith(("data/","docs/")):found.add(value)
                elif isinstance(value,list):found.update(x for x in value if isinstance(x,str) and x.startswith(("data/","docs/")))
            found|=collect_registered_files(value)
    elif isinstance(obj,list):
        for item in obj:found|=collect_registered_files(item)
    return found

def matches_pattern(path,patterns):
    for pattern in patterns:
        if "*" in pattern:
            if re.match("^"+re.escape(pattern).replace(r"\*",".*")+"$",path):return True
        elif path==pattern:return True
    return False

def json_error_detail(path,exc):
    try:lines=path.read_text(encoding="utf-8").splitlines()
    except Exception:lines=[]
    start=max(1,exc.lineno-2); end=min(len(lines),exc.lineno+2)
    return {"file":path.relative_to(ROOT).as_posix(),"line":exc.lineno,"column":exc.colno,"message":exc.msg,"context":[{"line":n,"text":lines[n-1][:500]} for n in range(start,end+1)]}

def main():
    coverage=load(COVERAGE); bridge=load(BRIDGE); manifest=load(MANIFEST); backend=load(BACKEND)
    coverage_patterns=[x["file"] for x in coverage.get("layers",[]) if isinstance(x,dict) and isinstance(x.get("file"),str)]
    coverage_patterns += [x for x in coverage.get("datasets",{}) if isinstance(x,str)]
    registered=collect_registered_files(manifest)|collect_registered_files(backend)|set(coverage_patterns)
    files=iter_json_files(); file_paths={p.relative_to(ROOT).as_posix() for p in files}
    missing_owners=sorted(p for p in file_paths if not matches_pattern(p,coverage_patterns) and p not in registered)
    id_locations={}; content_hashes={}; endpoint_files={}; invalid_json=[]
    for path in files:
        rel=path.relative_to(ROOT).as_posix(); raw=path.read_bytes(); content_hashes.setdefault(hashlib.sha256(raw).hexdigest(),[]).append(rel)
        try:value=json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:invalid_json.append(json_error_detail(path,exc)); continue
        except UnicodeDecodeError as exc:invalid_json.append({"file":rel,"line":None,"column":None,"message":f"UTF-8 decode error: {exc}","context":[]}); continue
        for ident in object_ids(value):id_locations.setdefault(ident,[]).append(rel)
        for source,target in relationship_endpoints(value):endpoint_files.setdefault(source,[]).append(rel); endpoint_files.setdefault(target,[]).append(rel)
    duplicate_ids={k:v for k,v in id_locations.items() if len(set(v))>1}
    exact_duplicates={k:sorted(v) for k,v in content_hashes.items() if len(v)>1}
    bridge_ids={x.get("id") for x in bridge.get("explicit_bridges",[]) if isinstance(x,dict)}
    registry_ids=set(); graph_registry=DATA/"graph-registry.json"
    if graph_registry.exists():registry_ids.update(object_ids(load(graph_registry)))
    node_ids=set(); nodes=DATA/"nodes.json"
    if nodes.exists():node_ids.update(object_ids(load(nodes)))
    declared_ids=set(id_locations); known_graph_ids=bridge_ids|registry_ids|node_ids|declared_ids
    relationship_only=sorted(i for i in endpoint_files if i not in known_graph_ids and i not in {"<id>","<country-id>","<slug>"})
    report={"version":"1.3.0","files_scanned":len(files),"registered_or_covered_files":sum(1 for p in file_paths if matches_pattern(p,coverage_patterns) or p in registered),"unmapped_files":missing_owners,"invalid_json":invalid_json,"duplicate_ids":{k:sorted(set(v)) for k,v in sorted(duplicate_ids.items())},"exact_duplicate_file_contents":exact_duplicates,"relationship_only_unresolved_ids":relationship_only,"bridge_explicit_ids":len(bridge_ids),"graph_registry_ids":len(registry_ids),"node_ids":len(node_ids),"declared_ids":len(declared_ids),"notes":["Duplicate IDs are diagnostics, not automatic deletion targets: indexes, overlays, country layers and research expansions can legitimately repeat IDs.","Exact duplicate files are candidates for consolidation after consumer migration.","Unresolved relationship endpoints are inventory debt and should either be promoted, bridged or removed.","A relationship endpoint is considered resolved when its ID is declared by valid backend data.","Coverage layers provide broad ownership for generated dataset families; explicit dataset entries override the generic intent semantically.","Invalid JSON is the only hard CI failure in this audit because it prevents reliable interpretation of the backend."]}
    (DATA/"backend-coverage-report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,ensure_ascii=False))
    if invalid_json:raise SystemExit(1)

if __name__=="__main__":main()
