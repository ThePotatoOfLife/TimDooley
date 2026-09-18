#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ROOMS=ROOT/'data/house/rooms.json'
SUBROOMS=ROOT/'data/house/subrooms.json'
SCHEMA=ROOT/'schemas/house-subroom-registry.schema.json'
TOPOLOGY=ROOT/'data/house/topology.json'
SURFACES=ROOT/'data/house/public-surfaces.json'

def load(path):
    return json.loads(path.read_text(encoding='utf-8'))

def main():
    errors=[]
    try:
        rooms=load(ROOMS); sub=load(SUBROOMS); topo=load(TOPOLOGY); surfaces=load(SURFACES); schema=load(SCHEMA)
    except Exception as exc:
        print('HOUSE SUBROOM VALIDATION FAILED')
        print('-',exc)
        return 1

    parent_ids={x.get('id') for x in rooms.get('rooms',[]) if isinstance(x,dict)}
    rows=[x for x in sub.get('subrooms',[]) if isinstance(x,dict)]
    ids=[x.get('id') for x in rows]
    if len(ids)!=len(set(ids)): errors.append('duplicate nested Room IDs')
    if len(rows)<20: errors.append('nested Room registry is unexpectedly small')
    surface_ids={x.get('id') for x in surfaces.get('surfaces',[]) if isinstance(x,dict)}

    for row in rows:
        rid=row.get('id')
        if row.get('parent_room_id') not in parent_ids:
            errors.append(f'{rid} has unknown parent Room {row.get("parent_room_id")}')
        if row.get('kind')!='nested-room':
            errors.append(f'{rid} must remain kind=nested-room')
        if row.get('ownership_mode')!='delegated-scope':
            errors.append(f'{rid} must inherit ownership by delegated-scope')
        for adj in row.get('adjacent_subroom_ids',[]):
            if adj not in set(ids): errors.append(f'{rid} unknown adjacent nested Room {adj}')
        for sid in row.get('public_surface_ids',[]):
            if sid not in surface_ids: errors.append(f'{rid} unknown public surface {sid}')
        for root in row.get('knowledge_roots',[]):
            target=ROOT/root.rstrip('/')
            if not target.exists(): errors.append(f'{rid} missing knowledge root {root}')
        profile=row.get('topology_profile',{})
        allowed_coords={'within','here','up','down','out','across','through','state'}
        coords=set(profile.get('primary_coordinates',[]))
        if not coords: errors.append(f'{rid} missing primary topology coordinates')
        if coords-allowed_coords: errors.append(f'{rid} invalid topology coordinates: {sorted(coords-allowed_coords)}')
        if profile.get('macro_band') not in {x.get('id') for x in topo.get('bands',[]) if isinstance(x,dict)}:
            errors.append(f'{rid} unknown macro band {profile.get("macro_band")}')

    if topo.get('room_registry')!='data/house/rooms.json': errors.append('House topology Room registry drift')
    if topo.get('subroom_registry')!='data/house/subrooms.json': errors.append('House topology subroom registry drift')
    macro={x.get('id') for x in topo.get('macro_roles',[]) if isinstance(x,dict)}
    if macro!=parent_ids: errors.append('House topology macro roles must cover exactly the ten canonical Rooms')
    for band in topo.get('bands',[]):
        for rid in band.get('room_ids',[]):
            if rid not in parent_ids: errors.append(f'House topology band {band.get("id")} unknown Room {rid}')
    for edge in topo.get('strong_corridors',[]):
        if edge.get('from') not in parent_ids or edge.get('to') not in parent_ids:
            errors.append(f'House corridor has unknown Room endpoint: {edge}')
    if len(topo.get('eight_coordinate_address',[]))!=8:
        errors.append('House topology must preserve all eight relational coordinates')
    if schema.get('title')!='Potato House Nested Room Registry':
        errors.append('Nested Room schema title drift')

    if errors:
        print('HOUSE SUBROOM VALIDATION FAILED')
        for e in errors: print('-',e)
        return 1
    print(f'HOUSE SUBROOM VALIDATION PASSED: {len(rows)} nested Rooms beneath {len(parent_ids)} canonical Rooms')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
