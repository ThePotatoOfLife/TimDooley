#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load(rel:str)->dict:
    path=ROOT/rel
    if not path.exists(): raise SystemExit(f'TREE OWNER FAILED: missing {rel}')
    value=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value,dict): raise SystemExit(f'TREE OWNER FAILED: bad object {rel}')
    return value

def main()->int:
    owner=load('knowledge/core/tree-of-life.json')
    if owner.get('id')!='tree-of-life': raise SystemExit('TREE OWNER FAILED: owner id')
    required={'definition','life_cycle','memory','renewal','branching','nourishment','relation_to_potato','boundary'}
    sections=owner.get('sections')
    if not isinstance(sections,dict) or not required<=set(sections): raise SystemExit('TREE OWNER FAILED: sections')
    registry=load('data/atlas-registry.json')
    nodes={str(n.get('id')):n for n in registry.get('nodes',[]) if isinstance(n,dict)}
    node=nodes.get('tree-of-life')
    if not node: raise SystemExit('TREE OWNER FAILED: missing Node')
    if node.get('owner_path')!='knowledge/core/tree-of-life.json': raise SystemExit('TREE OWNER FAILED: owner path')
    if node.get('north_parent')!='potato-of-life': raise SystemExit('TREE OWNER FAILED: North parent')
    artifacts=load('data/atlas-artifacts.json').get('artifacts',[])
    matches=[a for a in artifacts if isinstance(a,dict) and a.get('source_path')=='data/tree-concept-records.json' and 'tree-of-life' in a.get('node_refs',[])]
    if len(matches)!=1: raise SystemExit('TREE OWNER FAILED: tree concept Depth record')
    print('TREE OWNER PASSED')
    return 0

if __name__=='__main__': raise SystemExit(main())
