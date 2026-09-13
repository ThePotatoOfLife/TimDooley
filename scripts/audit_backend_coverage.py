#!/usr/bin/env python3
"""Audit repository backend ownership, duplicate IDs and graph reachability.

This audit is report-first. It scans both structured data and the knowledge
corpus, then distinguishes files already serving as Atlas canonical owners or
Depth Artifacts from knowledge records that remain outside the Atlas registry.
Malformed JSON remains an actionable warning so one damaged research file
cannot block unrelated repository changes.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
KNOWLEDGE=ROOT/"knowledge"
COVERAGE=DATA/"backend-coverage-map.json"
BRIDGE=DATA/"global-graph-bridge.json"
MANIFEST=DATA/"atlas-manifest.json"
BACKEND=DATA/"backend.json"
ATLAS_REGISTRY=DATA/"atlas-registry.json"
ATLAS_ARTIFACTS=DATA/"atlas-artifacts.json"

PLACEHOLDER_ENDPOINTS={"<id>","<country-id>","<slug>"}
DATE_LIKE_RE=re.compile(
    r"^(?:"
    r"\d{4}"
    r"|\d{4}-\d{2}"
    r"|\d{4}-\d{2}-\d{2}(?:[T ][0-9:.+-]+Z?)?"
    r"|\d{4}(?:-|/|–|—)\d{4}"
    r")$"
)
MACHINE_ID_RE=re.compile(r"^[a-z0-9][a-z0-9._:-]*(?:/[a-z0-9._:-]+)*$")
EXTERNAL_PREFIXES=("http://","https://","www.","doi:","urn:","mailto:","ftp://")


def load(path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def iter_json_files():
    files=[]
    for root in (DATA,KNOWLEDGE):
        if root.exists():
            files.extend(root.rglob("*.json"))
    return sorted(set(files))


def object_ids(value):
    if isinstance(value,dict):
        if isinstance(value.get("id"),str) and value["id"].strip():
            yield value["id"].strip()
        keys={"records","nodes","items","entries","observations","relationships","edges","sources","waves","dimensions","layers","links"}
        for key in keys:
            if key in value:
                yield from object_ids(value[key])
        for key,child in value.items():
            if key not in keys and isinstance(child,(dict,list)):
                yield from object_ids(child)
    elif isinstance(value,list):
        for item in value:
            yield from object_ids(item)


def relationship_endpoints(value):
    if isinstance(value,dict):
        source=value.get("source") or value.get("from") or value.get("subject")
        target=value.get("target") or value.get("to") or value.get("object")
        if isinstance(source,str) and isinstance(target,str):
            yield source.strip(),target.strip()
        for child in value.values():
            if isinstance(child,(dict,list)):
                yield from relationship_endpoints(child)
    elif isinstance(value,list):
        for item in value:
            yield from relationship_endpoints(item)


def collect_registered_files(obj):
    found=set()
    if isinstance(obj,dict):
        for key,value in obj.items():
            if key in {"file","files","endpoint","source","owner","backend","canonicalManifest","maintenanceWorkflow"}:
                if isinstance(value,str) and value.startswith(("data/","knowledge/","docs/")):
                    found.add(value)
                elif isinstance(value,list):
                    found.update(x for x in value if isinstance(x,str) and x.startswith(("data/","knowledge/","docs/")))
            found|=collect_registered_files(value)
    elif isinstance(obj,list):
        for item in obj:
            found|=collect_registered_files(item)
    return found


def matches_pattern(path,patterns):
    for pattern in patterns:
        if "*" in pattern:
            if re.match("^"+re.escape(pattern).replace(r"\*",".*")+"$",path):
                return True
        elif path==pattern:
            return True
    return False


def json_error_detail(path,exc):
    try:
        lines=path.read_text(encoding="utf-8").splitlines()
    except Exception:
        lines=[]
    start=max(1,exc.lineno-2)
    end=min(len(lines),exc.lineno+2)
    return {
        "file":path.relative_to(ROOT).as_posix(),
        "line":exc.lineno,
        "column":exc.colno,
        "message":exc.msg,
        "context":[{"line":n,"text":lines[n-1][:500]} for n in range(start,end+1)],
    }


def atlas_files():
    registry=load(ATLAS_REGISTRY) if ATLAS_REGISTRY.exists() else {}
    artifacts=load(ATLAS_ARTIFACTS) if ATLAS_ARTIFACTS.exists() else {}
    canonical={
        row.get("owner_path")
        for row in registry.get("nodes",[])
        if isinstance(row,dict) and row.get("status")=="active" and isinstance(row.get("owner_path"),str)
    }
    depth={
        row.get("source_path")
        for row in artifacts.get("artifacts",[])
        if isinstance(row,dict) and row.get("status")=="active" and isinstance(row.get("source_path"),str)
    }
    return {x for x in canonical if x},{x for x in depth if x}


def classify_unresolved_endpoint(endpoint):
    """Classify an unresolved endpoint by shape, without pretending shape proves intent."""
    value=endpoint.strip()
    lower=value.lower()
    if not value or value in PLACEHOLDER_ENDPOINTS:
        return "placeholder"
    if lower.startswith(EXTERNAL_PREFIXES) or "://" in lower:
        return "external_reference"
    if DATE_LIKE_RE.fullmatch(value):
        return "date_like"
    if MACHINE_ID_RE.fullmatch(value):
        return "candidate_machine_id"
    return "human_label"


def main():
    coverage=load(COVERAGE)
    bridge=load(BRIDGE)
    manifest=load(MANIFEST)
    backend=load(BACKEND)
    atlas_canonical_owner_files,atlas_artifact_source_files=atlas_files()

    coverage_patterns=[x["file"] for x in coverage.get("layers",[]) if isinstance(x,dict) and isinstance(x.get("file"),str)]
    coverage_patterns += [x for x in coverage.get("datasets",{}) if isinstance(x,str)]
    registered=collect_registered_files(manifest)|collect_registered_files(backend)|set(coverage_patterns)

    files=iter_json_files()
    file_paths={p.relative_to(ROOT).as_posix() for p in files}
    data_paths={p for p in file_paths if p.startswith("data/")}
    knowledge_paths={p for p in file_paths if p.startswith("knowledge/")}

    unmapped_data=sorted(p for p in data_paths if not matches_pattern(p,coverage_patterns) and p not in registered)
    atlas_connected=atlas_canonical_owner_files|atlas_artifact_source_files
    unmapped_knowledge=sorted(p for p in knowledge_paths if p not in atlas_connected and p not in registered)

    id_locations={}
    content_hashes={}
    endpoint_files={}
    invalid_json=[]
    for path in files:
        rel=path.relative_to(ROOT).as_posix()
        raw=path.read_bytes()
        content_hashes.setdefault(hashlib.sha256(raw).hexdigest(),[]).append(rel)
        try:
            value=json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            invalid_json.append(json_error_detail(path,exc))
            continue
        except UnicodeDecodeError as exc:
            invalid_json.append({"file":rel,"line":None,"column":None,"message":f"UTF-8 decode error: {exc}","context":[]})
            continue
        for ident in object_ids(value):
            id_locations.setdefault(ident,[]).append(rel)
        for source,target in relationship_endpoints(value):
            if source:
                endpoint_files.setdefault(source,[]).append(rel)
            if target:
                endpoint_files.setdefault(target,[]).append(rel)

    duplicate_ids={k:sorted(set(v)) for k,v in id_locations.items() if len(set(v))>1}
    knowledge_duplicate_ids={}
    knowledge_index_mirror_ids={}
    knowledge_peer_duplicate_ids={}
    for ident,locations in duplicate_ids.items():
        knowledge_locations=sorted(p for p in locations if p.startswith("knowledge/"))
        if len(knowledge_locations)<=1:
            continue
        knowledge_duplicate_ids[ident]=knowledge_locations
        index_locations=[p for p in knowledge_locations if p.startswith("knowledge/indexes/")]
        peer_locations=[p for p in knowledge_locations if not p.startswith("knowledge/indexes/")]
        if index_locations and peer_locations:
            knowledge_index_mirror_ids[ident]={
                "indexes":index_locations,
                "owners_or_peers":peer_locations,
            }
        if len(peer_locations)>1:
            knowledge_peer_duplicate_ids[ident]=peer_locations

    exact_duplicates={k:sorted(v) for k,v in content_hashes.items() if len(v)>1}
    bridge_ids={x.get("id") for x in bridge.get("explicit_bridges",[]) if isinstance(x,dict)}
    registry_ids=set()
    graph_registry=DATA/"graph-registry.json"
    if graph_registry.exists():
        registry_ids.update(object_ids(load(graph_registry)))
    node_ids=set()
    nodes=DATA/"nodes.json"
    if nodes.exists():
        node_ids.update(object_ids(load(nodes)))
    declared_ids=set(id_locations)
    known_graph_ids=bridge_ids|registry_ids|node_ids|declared_ids
    relationship_only=sorted(
        i for i in endpoint_files
        if i not in known_graph_ids and i not in PLACEHOLDER_ENDPOINTS
    )

    unresolved_classes={
        "candidate_machine_id":[],
        "external_reference":[],
        "human_label":[],
        "date_like":[],
    }
    for endpoint in relationship_only:
        kind=classify_unresolved_endpoint(endpoint)
        if kind in unresolved_classes:
            unresolved_classes[kind].append(endpoint)

    candidate_unresolved_machine_ids=sorted(unresolved_classes["candidate_machine_id"])
    external_reference_ids=sorted(unresolved_classes["external_reference"])
    human_label_endpoints=sorted(unresolved_classes["human_label"])
    date_like_endpoints=sorted(unresolved_classes["date_like"])

    report={
        "version":"2.2.0",
        "files_scanned":len(files),
        "data_files_scanned":len(data_paths),
        "knowledge_files_scanned":len(knowledge_paths),
        "registered_or_covered_files":sum(1 for p in file_paths if matches_pattern(p,coverage_patterns) or p in registered or p in atlas_connected),
        "unmapped_files":sorted(set(unmapped_data)|set(unmapped_knowledge)),
        "unmapped_data_files":unmapped_data,
        "unmapped_knowledge_files":unmapped_knowledge,
        "atlas_canonical_owner_files":sorted(atlas_canonical_owner_files),
        "atlas_artifact_source_files":sorted(atlas_artifact_source_files),
        "invalid_json":invalid_json,
        "duplicate_ids":{k:v for k,v in sorted(duplicate_ids.items())},
        "knowledge_duplicate_ids":{k:v for k,v in sorted(knowledge_duplicate_ids.items())},
        "knowledge_index_mirror_ids":{k:v for k,v in sorted(knowledge_index_mirror_ids.items())},
        "knowledge_peer_duplicate_ids":{k:v for k,v in sorted(knowledge_peer_duplicate_ids.items())},
        "duplicate_signal_counts":{
            "knowledge_duplicates":len(knowledge_duplicate_ids),
            "index_mirrors":len(knowledge_index_mirror_ids),
            "peer_duplicates":len(knowledge_peer_duplicate_ids),
        },
        "exact_duplicate_file_contents":exact_duplicates,
        "relationship_only_unresolved_ids":relationship_only,
        "candidate_unresolved_machine_ids":candidate_unresolved_machine_ids,
        "external_reference_ids":external_reference_ids,
        "human_label_endpoints":human_label_endpoints,
        "date_like_endpoints":date_like_endpoints,
        "unresolved_endpoint_counts":{
            "all":len(relationship_only),
            "candidate_machine_ids":len(candidate_unresolved_machine_ids),
            "external_references":len(external_reference_ids),
            "human_labels":len(human_label_endpoints),
            "date_like":len(date_like_endpoints),
        },
        "bridge_explicit_ids":len(bridge_ids),
        "graph_registry_ids":len(registry_ids),
        "node_ids":len(node_ids),
        "declared_ids":len(declared_ids),
        "notes":[
            "Knowledge files outside the Atlas owner/Artifact registries are a consolidation frontier, not automatic errors or deletion targets.",
            "Duplicate IDs are diagnostics, not automatic deletion targets: indexes, overlays, country layers and research expansions can legitimately repeat IDs.",
            "knowledge_duplicate_ids preserves the broad knowledge-level inventory for compatibility.",
            "knowledge_index_mirror_ids separates likely navigation/index mirrors from ownership pressure; an index repeating a canonical record ID is usually expected.",
            "knowledge_peer_duplicate_ids is the higher-signal ownership queue: the same ID appears in multiple non-index knowledge files and deserves canonical-owner review.",
            "Exact duplicate files are candidates for consolidation after consumer migration.",
            "relationship_only_unresolved_ids is retained as the compatibility inventory; candidate_unresolved_machine_ids is the higher-signal graph-debt queue.",
            "External references, human-readable labels and date-like endpoints are reported separately so they do not inflate machine-ID cleanup pressure.",
            "Endpoint classes are shape-based diagnostics, not semantic truth; a candidate machine ID still requires owner/provenance review before promotion or removal.",
            "A relationship endpoint is considered resolved when its ID is declared by valid data or knowledge records.",
            "Coverage layers provide broad ownership for generated data families; Atlas Node/Artifact registries provide explicit ownership/depth for knowledge records.",
            "Invalid JSON is an actionable warning in this inventory audit and must not block unrelated project changes or deployment; the file is excluded from parsed ownership calculations until repaired.",
        ],
    }
    (DATA/"backend-coverage-report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
