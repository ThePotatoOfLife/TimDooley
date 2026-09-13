#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'data/atlas-relation-types.json'


def main()->int:
    doc=json.loads(PATH.read_text(encoding='utf-8'))
    orientations=doc.get('orientations',{})
    required={'north','lateral','structural_down','archival'}
    if not required<=set(orientations): raise SystemExit('ATLAS RELATIONS FAILED: missing orientations')
    types=doc.get('types',[])
    if not isinstance(types,list) or not types: raise SystemExit('ATLAS RELATIONS FAILED: types missing')
    ids=[str(t.get('id','')) for t in types if isinstance(t,dict)]
    if len(ids)!=len(set(ids)): raise SystemExit('ATLAS RELATIONS FAILED: duplicate type id')
    by={str(t['id']):t for t in types if isinstance(t,dict) and t.get('id')}
    for tid,t in by.items():
        orientation=t.get('orientation')
        if orientation not in required-{'north'}: raise SystemExit(f'ATLAS RELATIONS FAILED: bad orientation {tid}')
        inverse=t.get('inverse')
        if inverse not in by: raise SystemExit(f'ATLAS RELATIONS FAILED: missing inverse {tid}->{inverse}')
        if by[inverse].get('inverse')!=tid: raise SystemExit(f'ATLAS RELATIONS FAILED: inverse mismatch {tid}<->{inverse}')
        if not str(t.get('label','')).strip(): raise SystemExit(f'ATLAS RELATIONS FAILED: missing label {tid}')
    print(f'ATLAS RELATIONS PASSED: {len(by)} typed roads')
    return 0

if __name__=='__main__': raise SystemExit(main())
