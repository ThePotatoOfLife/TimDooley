#!/usr/bin/env python3
"""Assemble Node orientation with road metadata and Archive Artifacts."""
from __future__ import annotations
import json,re
from pathlib import Path
from typing import Any

from atlas_model import build_model as build_orientation_model

ROOT=Path(__file__).resolve().parents[1]
RELATIONS=ROOT/'data/atlas-relation-types.json'
ARTIFACTS=ROOT/'data/atlas-artifacts.json'


def load(path:Path)->Any:return json.loads(path.read_text(encoding='utf-8'))
def key(value:str)->str:return re.sub(r'[^a-z0-9]+','_',value.lower()).strip('_') or 'related'


def build_runtime()->dict[str,Any]:
    model=build_orientation_model()
    relation_doc=load(RELATIONS); artifact_doc=load(ARTIFACTS)
    relation_types={str(row['id']):dict(row) for row in relation_doc.get('types',[]) if isinstance(row,dict) and row.get('id')}
    artifacts=[dict(row) for row in artifact_doc.get('artifacts',[]) if isinstance(row,dict)]
    artifacts_by_node={str(node['id']):[] for node in model.get('nodes',[])}
    for artifact in artifacts:
        for node_id in artifact.get('node_refs',[]):
            if node_id in artifacts_by_node:artifacts_by_node[node_id].append(artifact)
    for rows in artifacts_by_node.values():rows.sort(key=lambda row:(str(row.get('date_or_period') or ''),str(row.get('title') or '')))
    for node in model.get('nodes',[]):
        normalized=[]
        for rel in node.get('relations',[]):
            raw_type=str(rel.get('type') or 'related'); relation_id=key(raw_type); spec=relation_types.get(relation_id)
            enriched=dict(rel)
            enriched.update({'canonical_type':relation_id if spec else None,'label':spec.get('label') if spec else raw_type.replace('_',' ').replace('-',' ').title(),'orientation':spec.get('orientation') if spec else 'lateral','provisional_type':spec is None})
            normalized.append(enriched)
        node['relations']=normalized
        node['artifacts']=artifacts_by_node.get(str(node['id']),[])
    model['schema_version']='1.1.0';model['relation_types']=list(relation_types.values());model['artifacts']=artifacts
    return model

if __name__=='__main__':print(json.dumps(build_runtime(),indent=2,ensure_ascii=False))
