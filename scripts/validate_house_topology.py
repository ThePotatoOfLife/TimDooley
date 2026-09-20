#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from house_public_surfaces import derived_route_topology_records, load_public_surfaces

ROOT=Path(__file__).resolve().parents[1]
ROOMS=ROOT/'data/house/rooms.json'
SNAPSHOT=ROOT/'knowledge/research/potato-house-master/public-route-topology.json'

def load(path):
    return json.loads(path.read_text(encoding='utf-8'))

def main():
    errors=[]
    try:
        rooms=load(ROOMS)
        surfaces=load_public_surfaces(ROOT)
        rows=derived_route_topology_records(ROOT)
        snapshot=load(SNAPSHOT)
    except Exception as exc:
        print(f'POTATO HOUSE TOPOLOGY VALIDATION FAILED\n- {exc}')
        return 1

    room_ids={x['id'] for x in rooms.get('rooms',[]) if isinstance(x,dict) and x.get('id')}
    active=[x for x in surfaces.get('surfaces',[]) if isinstance(x,dict) and x.get('id') and x.get('status')=='active']
    expected=[x['id'] for x in active]
    ids=[x.get('surface_id') for x in rows]
    if ids!=expected:
        errors.append(f'derived topology order invalid: expected {expected!r}; got {ids!r}')

    by_surface={x['id']:x for x in active}
    for row in rows:
        sid=row.get('surface_id'); surface=by_surface.get(sid)
        if not surface:
            errors.append(f'derived topology contains unknown or non-active surface {sid}')
            continue
        if row.get('canonical_route')!=surface.get('canonical_route'): errors.append(f'derived route mismatch {sid}')
        if row.get('surface_type')!=surface.get('surface_type'): errors.append(f'derived type mismatch {sid}')
        if row.get('room_ids')!=surface.get('primary_room_ids'): errors.append(f'derived Room mismatch {sid}')
        for rid in row.get('room_ids',[]):
            if rid not in room_ids: errors.append(f'{sid} unknown Room {rid}')

    derivation=snapshot.get('derivation') or {}
    if snapshot.get('status')!='derived compatibility projection':
        errors.append('legacy route-topology snapshot must remain explicitly demoted')
    if derivation.get('authority')!='data/house/public-surfaces.json':
        errors.append('legacy route-topology snapshot must point to public-surfaces authority')
    if derivation.get('resolver')!='scripts/house_public_surfaces.py::derived_route_topology_records':
        errors.append('legacy route-topology snapshot must name the deterministic resolver')

    if errors:
        print('POTATO HOUSE TOPOLOGY VALIDATION FAILED')
        for error in errors: print('-',error)
        return 1
    print(f'POTATO HOUSE TOPOLOGY VALIDATION PASSED: {len(rows)} active public surfaces derived from one authority')
    return 0

if __name__=='__main__': raise SystemExit(main())
