#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ROOMS=ROOT/'data/house/rooms.json'
SURFACES=ROOT/'data/house/public-surfaces.json'
TOPOLOGY=ROOT/'knowledge/research/potato-house-master/public-route-topology.json'
EXPECTED=('home','tim','religion','philosophy','science','world','timeline','explore','sources','world-map','politics','north','world-systems','bible')

def load(path):
    return json.loads(path.read_text(encoding='utf-8'))

def main():
    errors=[]
    try:
        rooms=load(ROOMS); surfaces=load(SURFACES); topology=load(TOPOLOGY)
    except Exception as exc:
        print(f'POTATO HOUSE TOPOLOGY VALIDATION FAILED\n- {exc}')
        return 1
    room_ids={x['id'] for x in rooms.get('rooms',[]) if isinstance(x,dict) and x.get('id')}
    surface_rows=surfaces.get('surfaces',[])
    by={x['id']:x for x in surface_rows if isinstance(x,dict) and x.get('id')}
    rows=topology.get('records',[])
    ids=tuple(x.get('surface_id') for x in rows if isinstance(x,dict))
    if ids!=EXPECTED: errors.append(f'topology order invalid: {ids!r}')
    for row in rows:
        if not isinstance(row,dict): continue
        sid=row.get('surface_id'); surface=by.get(sid)
        if not surface: errors.append(f'unknown surface {sid}'); continue
        if row.get('canonical_route')!=surface.get('canonical_route'): errors.append(f'route mismatch {sid}')
        if row.get('surface_type')!=surface.get('surface_type'): errors.append(f'type mismatch {sid}')
        if set(row.get('room_ids',[]))!=set(surface.get('primary_room_ids',[])): errors.append(f'Room mismatch {sid}')
        hub=row.get('primary_hub_id')
        if hub is not None and hub not in by: errors.append(f'unknown hub {hub}')
        for rid in row.get('room_ids',[]):
            if rid not in room_ids: errors.append(f'{sid} unknown Room {rid}')
    if errors:
        print('POTATO HOUSE TOPOLOGY VALIDATION FAILED')
        for error in errors: print('-',error)
        return 1
    print('POTATO HOUSE TOPOLOGY VALIDATION PASSED: 14 canonical public surfaces')
    return 0

if __name__=='__main__': raise SystemExit(main())
