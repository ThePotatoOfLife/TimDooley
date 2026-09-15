#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SURFACES=ROOT/'data/house/public-surfaces.json'
BRIDGE=ROOT/'data/frontend-atlas-bridge.json'
COVERAGE=ROOT/'data/backend-coverage-map.json'
ATLAS=ROOT/'data/atlas-manifest.json'
EXPECTED=('tim','religion','philosophy','science','world')

def load(path): return json.loads(path.read_text(encoding='utf-8'))

def strip(route): return '/'+str(route).strip('/')+'/'

def main():
    errors=[]
    try:
        surfaces=load(SURFACES); bridge=load(BRIDGE); coverage=load(COVERAGE); atlas=load(ATLAS)
    except Exception as exc:
        print(f'POTATO HOUSE COMPATIBILITY VALIDATION FAILED\n- {exc}')
        return 1
    if surfaces.get('authority')!='public-route-identity':
        errors.append('public-surfaces authority must remain public-route-identity')
    by={x['id']:x for x in surfaces.get('surfaces',[]) if isinstance(x,dict) and x.get('id')}
    doors=bridge.get('public_doors',{})
    if tuple(doors)!=EXPECTED: errors.append(f'frontend bridge door order invalid: {tuple(doors)!r}')
    for sid in EXPECTED:
        expected=by.get(sid,{}).get('canonical_route')
        actual=strip(doors.get(sid,''))
        if expected!=actual: errors.append(f'frontend bridge route mismatch {sid}: {actual!r} != {expected!r}')
    if coverage.get('frontend_contract')!='data/frontend-atlas-bridge.json':
        errors.append('backend coverage frontend_contract must remain data/frontend-atlas-bridge.json')
    if atlas.get('public_route_registry')!='data/house/public-surfaces.json':
        errors.append('atlas manifest public_route_registry must be data/house/public-surfaces.json')
    if atlas.get('public_manifest')!='manifest.json':
        errors.append('atlas manifest public_manifest must remain manifest.json for archive branch/pathway semantics')
    if atlas.get('frontend_projection')!='data/frontend-atlas-bridge.json':
        errors.append('atlas manifest frontend_projection must remain data/frontend-atlas-bridge.json')
    requirements=' '.join(bridge.get('integrity_requirements',[]))
    if 'World is the fifth public domain' not in requirements:
        errors.append('frontend bridge must preserve World-as-fifth-domain integrity requirement')
    if errors:
        print('POTATO HOUSE COMPATIBILITY VALIDATION FAILED')
        for error in errors: print('-',error)
        return 1
    print('POTATO HOUSE COMPATIBILITY VALIDATION PASSED: House route identity, archive manifest, bridge and coverage roles agree')
    return 0

if __name__=='__main__': raise SystemExit(main())
