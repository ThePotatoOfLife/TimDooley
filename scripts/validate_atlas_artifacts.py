#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ARTIFACTS=ROOT/'data/atlas-artifacts.json'
REGISTRY=ROOT/'data/atlas-registry.json'
KINDS={'primary_source','conversation','timeline_event','research_note','documentary_source','comparative_source','creative_work','dataset','version','collection','observation'}
STATUSES={'active','candidate','legacy','archive_only'}
VISIBILITY={'public','internal'}


def main()->int:
    doc=json.loads(ARTIFACTS.read_text(encoding='utf-8'))
    reg=json.loads(REGISTRY.read_text(encoding='utf-8'))
    nodes={str(n.get('id')) for n in reg.get('nodes',[]) if isinstance(n,dict) and n.get('id')}
    artifacts=doc.get('artifacts',[])
    if not isinstance(artifacts,list): raise SystemExit('ATLAS ARTIFACTS FAILED: artifacts must be a list')
    ids=[]
    for a in artifacts:
        if not isinstance(a,dict): raise SystemExit('ATLAS ARTIFACTS FAILED: artifact must be object')
        aid=str(a.get('id','')); ids.append(aid)
        if len(aid)<3: raise SystemExit('ATLAS ARTIFACTS FAILED: invalid id')
        if a.get('kind') not in KINDS: raise SystemExit(f'ATLAS ARTIFACTS FAILED: bad kind {aid}')
        if a.get('status') not in STATUSES: raise SystemExit(f'ATLAS ARTIFACTS FAILED: bad status {aid}')
        if a.get('visibility') not in VISIBILITY: raise SystemExit(f'ATLAS ARTIFACTS FAILED: bad visibility {aid}')
        path=ROOT/str(a.get('source_path',''))
        if not path.exists(): raise SystemExit(f'ATLAS ARTIFACTS FAILED: missing source_path {aid}: {path}')
        if len(str(a.get('summary','')).strip())<20: raise SystemExit(f'ATLAS ARTIFACTS FAILED: short summary {aid}')
        if not isinstance(a.get('epistemic_classes'),list) or not a['epistemic_classes']: raise SystemExit(f'ATLAS ARTIFACTS FAILED: epistemic classes {aid}')
        if not isinstance(a.get('node_refs'),list): raise SystemExit(f'ATLAS ARTIFACTS FAILED: node_refs {aid}')
        missing=[ref for ref in a['node_refs'] if ref not in nodes]
        if missing: raise SystemExit(f'ATLAS ARTIFACTS FAILED: unknown node refs {aid}: {missing}')
        prov=a.get('provenance')
        if not isinstance(prov,dict) or not str(prov.get('basis','')).strip(): raise SystemExit(f'ATLAS ARTIFACTS FAILED: provenance {aid}')
        route=a.get('public_route')
        if route is not None and (not isinstance(route,str) or not route.startswith('/') or not route.endswith('/')): raise SystemExit(f'ATLAS ARTIFACTS FAILED: public route {aid}')
    if len(ids)!=len(set(ids)): raise SystemExit('ATLAS ARTIFACTS FAILED: duplicate ids')
    print(f'ATLAS ARTIFACTS PASSED: {len(artifacts)} artifacts')
    return 0

if __name__=='__main__': raise SystemExit(main())
