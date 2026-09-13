#!/usr/bin/env python3
"""Derive runtime Atlas data from curated orientation and View registries."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/'data/atlas-registry.json'
VIEWS=ROOT/'data/atlas-views.json'

def load_json(path:Path)->Any:return json.loads(path.read_text(encoding='utf-8'))

def owner_summary(owner:dict[str,Any],fallback:str)->str:
    for key in ('summary','purpose','description','definition','core_thesis'):
        value=owner.get(key)
        if isinstance(value,str) and value.strip(): return value.strip()
    sections=owner.get('sections')
    if isinstance(sections,dict):
        for section in sections.values():
            if isinstance(section,dict) and isinstance(section.get('text'),str) and section['text'].strip(): return section['text'].strip()
    return fallback.strip()

def owner_sections(owner:dict[str,Any])->list[dict[str,Any]]:
    sections=owner.get('sections')
    if not isinstance(sections,dict): return []
    out=[]
    for key,value in sections.items():
        if not isinstance(value,dict) or not isinstance(value.get('text'),str) or not value['text'].strip(): continue
        out.append({'id':str(key),'title':str(key).replace('_',' ').replace('-',' ').title(),'text':value['text'].strip(),'epistemic_class':value.get('epistemic_class',[]),'source_ids':value.get('source_ids',[])})
    return out

def normalize_relations(owner:dict[str,Any],routes:dict[str,str])->list[dict[str,Any]]:
    raw=owner.get('relationships')
    if not isinstance(raw,list): return []
    out=[]
    for item in raw:
        if not isinstance(item,dict) or not isinstance(item.get('target'),str) or not item['target'].strip(): continue
        target=item['target'].strip()
        out.append({'target':target,'type':str(item.get('type') or item.get('relationship') or 'related'),'description':str(item.get('description') or item.get('notes') or '').strip(),'epistemic_class':item.get('epistemic_class'),'resolved':target in routes,'route':routes.get(target)})
    return out

def build_model()->dict[str,Any]:
    registry=load_json(REGISTRY); views_doc=load_json(VIEWS)
    source_nodes=registry.get('nodes',[]); source_views=views_doc.get('views',[])
    if not isinstance(source_nodes,list): raise ValueError('atlas-registry.json nodes must be a list')
    if not isinstance(source_views,list): raise ValueError('atlas-views.json views must be a list')
    view_by_id={str(v['id']):dict(v) for v in source_views if isinstance(v,dict) and v.get('id')}
    active=[dict(n) for n in source_nodes if isinstance(n,dict) and n.get('status')=='active']
    seeds={str(n['id']):n for n in active}; routes={i:str(n.get('route','')) for i,n in seeds.items()}; root_id=str(registry.get('root_id',''))
    children={i:[] for i in seeds}
    for node_id,node in seeds.items():
        parent=node.get('north_parent')
        if isinstance(parent,str) and parent in children: children[parent].append(node_id)
    for values in children.values(): values.sort()
    result=[]
    for node_id,seed in seeds.items():
        owner=load_json(ROOT/str(seed['owner_path']))
        if not isinstance(owner,dict): raise ValueError(f"owner is not an object: {seed['owner_path']}")
        north=[]; current=node_id; seen=set()
        while current:
            if current in seen: raise ValueError(f'North cycle while deriving {node_id}')
            seen.add(current); north.append(current)
            if current==root_id: break
            parent=seeds[current].get('north_parent')
            if not isinstance(parent,str) or parent not in seeds: raise ValueError(f'Broken North path while deriving {node_id}')
            current=parent
        north.reverse()
        epistemic=owner.get('epistemic_classes') if isinstance(owner.get('epistemic_classes'),list) else seed.get('epistemic_classes',[])
        result.append({**seed,'title':str(owner.get('title') or owner.get('name') or seed.get('title') or node_id),'aliases':owner.get('aliases') if isinstance(owner.get('aliases'),list) else [],'summary':owner_summary(owner,str(seed.get('summary',''))),'epistemic_classes':epistemic,'sections':owner_sections(owner),'relations':normalize_relations(owner,routes),'children':children[node_id],'north_path':north,'view_details':[view_by_id[str(v)] for v in seed.get('views',[]) if str(v) in view_by_id],'owner_id':owner.get('id'),'owner_title':owner.get('title') or owner.get('name')})
    result.sort(key=lambda item:item['id'])
    return {'schema_version':'1.0.0','root_id':root_id,'views':list(view_by_id.values()),'nodes':result}

def by_id(model:dict[str,Any])->dict[str,dict[str,Any]]: return {str(n['id']):n for n in model.get('nodes',[])}

if __name__=='__main__': print(json.dumps(build_model(),indent=2,ensure_ascii=False))
