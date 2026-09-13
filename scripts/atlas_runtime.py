#!/usr/bin/env python3
"""Assemble Node orientation with reader blocks, road metadata and Artifacts."""
from __future__ import annotations
import json,re
from collections import defaultdict
from pathlib import Path
from typing import Any

from atlas_model import build_model as build_orientation_model
from atlas_adapters import adapt

ROOT=Path(__file__).resolve().parents[1]
RELATIONS=ROOT/'data/atlas-relation-types.json'
RELATION_MAP=ROOT/'data/atlas-relation-map.json'
ARTIFACTS=ROOT/'data/atlas-artifacts.json'


def load(path:Path)->Any:return json.loads(path.read_text(encoding='utf-8'))
def key(value:str)->str:return re.sub(r'[^a-z0-9]+','_',value.lower()).strip('_') or 'related'


def artifact_aliases(artifacts:list[dict[str,Any]])->dict[str,dict[str,Any]]:
    """Return only unambiguous Artifact lookup aliases.

    Artifact ID is always an alias. Source path and basename are convenient
    compatibility aliases for older owner relations that predate the Artifact
    registry. Ambiguous aliases are deliberately dropped rather than guessed.
    """
    candidates:dict[str,list[dict[str,Any]]]=defaultdict(list)
    for artifact in artifacts:
        aliases={str(artifact.get('id') or '').strip()}
        source=str(artifact.get('source_path') or '').strip()
        if source:
            aliases.add(source)
            aliases.add(Path(source).name)
        for alias in aliases:
            if alias:candidates[alias].append(artifact)
    return {alias:rows[0] for alias,rows in candidates.items() if len(rows)==1}


def build_runtime()->dict[str,Any]:
    model=build_orientation_model()
    relation_doc=load(RELATIONS);mapping_doc=load(RELATION_MAP);artifact_doc=load(ARTIFACTS)
    relation_types={str(row['id']):dict(row) for row in relation_doc.get('types',[]) if isinstance(row,dict) and row.get('id')}
    explicit_map={str(row['raw']):str(row['canonical']) for row in mapping_doc.get('mappings',[]) if isinstance(row,dict) and row.get('raw') and row.get('canonical')}
    artifacts=[dict(row) for row in artifact_doc.get('artifacts',[]) if isinstance(row,dict)]
    artifact_lookup=artifact_aliases(artifacts)
    artifacts_by_node={str(node['id']):[] for node in model.get('nodes',[])}
    for artifact in artifacts:
        for node_id in artifact.get('node_refs',[]):
            if node_id in artifacts_by_node:artifacts_by_node[node_id].append(artifact)
    for rows in artifacts_by_node.values():rows.sort(key=lambda row:(str(row.get('date_or_period') or ''),str(row.get('title') or '')))
    for node in model.get('nodes',[]):
        owner=load(ROOT/str(node['owner_path']))
        node['sections']=adapt(owner,str(node['id'])) if isinstance(owner,dict) else []
        normalized=[]
        for rel in node.get('relations',[]):
            raw_type=str(rel.get('type') or 'related')
            relation_id=explicit_map.get(raw_type) or key(raw_type)
            spec=relation_types.get(relation_id)
            enriched=dict(rel)
            if enriched.get('resolved'):
                enriched['resolved_kind']='node'
                enriched['node_id']=enriched.get('target')
            else:
                artifact=artifact_lookup.get(str(enriched.get('target') or ''))
                if artifact:
                    enriched.update({
                        'resolved':True,
                        'resolved_kind':'artifact',
                        'artifact_id':artifact.get('id'),
                        'artifact_title':artifact.get('title'),
                        'route':artifact.get('public_route'),
                    })
            enriched.update({'canonical_type':relation_id if spec else None,'label':spec.get('label') if spec else raw_type.replace('_',' ').replace('-',' ').title(),'orientation':spec.get('orientation') if spec else 'lateral','provisional_type':spec is None,'mapped_explicitly':raw_type in explicit_map})
            normalized.append(enriched)
        node['relations']=normalized
        node['artifacts']=artifacts_by_node.get(str(node['id']),[])
    model['schema_version']='1.4.0';model['relation_types']=list(relation_types.values());model['relation_map']=explicit_map;model['artifacts']=artifacts
    return model

if __name__=='__main__':print(json.dumps(build_runtime(),indent=2,ensure_ascii=False))
