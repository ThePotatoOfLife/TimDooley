#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load(rel:str)->dict:
    path=ROOT/rel
    if not path.exists(): raise SystemExit(f'SON OWNER FAILED: missing {rel}')
    value=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value,dict): raise SystemExit(f'SON OWNER FAILED: bad object {rel}')
    return value

def main()->int:
    owner=load('knowledge/core/son.json')
    if owner.get('id')!='son': raise SystemExit('SON OWNER FAILED: owner id')
    sections=owner.get('sections')
    required={'identity','development','ordeal','death_and_door','father_son_distinction','comparison','embodiment','boundary'}
    if not isinstance(sections,dict) or not required<=set(sections): raise SystemExit('SON OWNER FAILED: sections')
    registry=load('data/atlas-registry.json')
    nodes={str(n.get('id')):n for n in registry.get('nodes',[]) if isinstance(n,dict)}
    node=nodes.get('son')
    if not node: raise SystemExit('SON OWNER FAILED: missing Node')
    if node.get('owner_path')!='knowledge/core/son.json': raise SystemExit('SON OWNER FAILED: owner path')
    if node.get('north_parent')!='potatoverse-master-framework': raise SystemExit('SON OWNER FAILED: North parent')
    artifacts=load('data/atlas-artifacts.json').get('artifacts',[])
    refs={str(a.get('source_path')) for a in artifacts if isinstance(a,dict) and 'son' in a.get('node_refs',[])}
    expected={'son-timeline.json','knowledge/timeline/son-tree-oneness-experience.json','knowledge/traditions/thomas-twin-of-christ.json','knowledge/traditions/biblical-overlap-atlas.json'}
    if not expected<=refs: raise SystemExit('SON OWNER FAILED: specialist Depth records')
    print('SON OWNER PASSED')
    return 0

if __name__=='__main__': raise SystemExit(main())
