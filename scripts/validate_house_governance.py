#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ROOMS=ROOT/'data/house/rooms.json'; ROOM_SCHEMA=ROOT/'schemas/house-room-registry.schema.json'
SURFACES=ROOT/'data/house/public-surfaces.json'; SURFACE_SCHEMA=ROOT/'schemas/house-public-surface-registry.schema.json'
ROOM_IDS=('potatoverse-canon','archive-sources','time-history','traditions-texts','science-formal-models','life-body','world-systems','culture-information','works','research-lab')
GATEWAYS=('tim','religion','philosophy','science','world')
GATEWAY_ROUTES=('/tim-dooley/','/religion/','/philosophy/','/science/','/world/')

def load(path,errors):
    try:v=json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError: errors.append(f'missing required House contract: {path.relative_to(ROOT)}'); return {}
    except Exception as exc: errors.append(f'invalid JSON in {path.relative_to(ROOT)}: {exc}'); return {}
    if not isinstance(v,dict): errors.append(f'House contract must be object: {path.relative_to(ROOT)}'); return {}
    return v

def type_ok(v,t):
    checks={'object':dict,'array':list,'string':str,'boolean':bool,'integer':int,'number':(int,float)}
    if t=='null': return v is None
    return isinstance(v,checks.get(t,object)) and not (t in {'integer','number'} and isinstance(v,bool))

def schema(v,s,owner,errors):
    t=s.get('type')
    if isinstance(t,str) and not type_ok(v,t): errors.append(f'{owner} must be {t}'); return
    if isinstance(t,list) and not any(type_ok(v,x) for x in t): errors.append(f'{owner} type invalid'); return
    if 'const' in s and v!=s['const']: errors.append(f'{owner} must equal {s["const"]!r}')
    if 'enum' in s and v not in s['enum']: errors.append(f'{owner} enum invalid')
    if isinstance(v,str) and s.get('pattern') and not re.search(s['pattern'],v): errors.append(f'{owner} pattern invalid')
    if isinstance(v,dict):
        props=s.get('properties',{})
        for k in s.get('required',[]):
            if k not in v: errors.append(f'{owner} missing {k}')
        if s.get('additionalProperties') is False:
            for k in v:
                if k not in props: errors.append(f'{owner} unexpected {k}')
        for k,child in props.items():
            if k in v and isinstance(child,dict): schema(v[k],child,f'{owner}.{k}',errors)
    if isinstance(v,list):
        if len(v)<s.get('minItems',0): errors.append(f'{owner} too short')
        if 'maxItems' in s and len(v)>s['maxItems']: errors.append(f'{owner} too long')
        if s.get('uniqueItems') and len({json.dumps(x,sort_keys=True) for x in v})!=len(v): errors.append(f'{owner} items not unique')
        if isinstance(s.get('items'),dict):
            for i,x in enumerate(v): schema(x,s['items'],f'{owner}[{i}]',errors)

def validate_rooms(errors):
    r=load(ROOMS,errors); s=load(ROOM_SCHEMA,errors)
    if r and s: schema(r,s,'rooms',errors)
    rows=r.get('rooms',[]); ids=tuple(x.get('id') for x in rows if isinstance(x,dict))
    if ids!=ROOM_IDS: errors.append(f'Room IDs/order invalid: {ids!r}')
    known=set(ids)
    for row in rows:
        if isinstance(row,dict):
            for target in row.get('interfaces',[]):
                if target not in known: errors.append(f'Room {row.get("id")} unknown interface {target}')
    return r

def validate_surfaces(errors,rooms):
    p=load(SURFACES,errors); s=load(SURFACE_SCHEMA,errors)
    if p and s: schema(p,s,'public_surfaces',errors)
    rows=p.get('surfaces',[]); by={x.get('id'):x for x in rows if isinstance(x,dict) and x.get('id')}
    if tuple(p.get('primary_gateway_ids',[]))!=GATEWAYS: errors.append('primary_gateway_ids invalid')
    routes=tuple(by.get(x,{}).get('canonical_route') for x in GATEWAYS)
    if routes!=GATEWAY_ROUTES: errors.append(f'primary gateway routes invalid: {routes!r}')
    room_ids={x.get('id') for x in rooms.get('rooms',[]) if isinstance(x,dict)}; seen={}; legacy={}
    for sid,row in by.items():
        route=row.get('canonical_route')
        if route in seen: errors.append(f'duplicate canonical route {route}')
        seen[route]=sid
        for rid in row.get('primary_room_ids',[]):
            if rid not in room_ids: errors.append(f'{sid} unknown Room {rid}')
        parent=row.get('primary_parent')
        if parent is not None and parent not in by: errors.append(f'{sid} unknown parent {parent}')
        if row.get('is_view') and row.get('knowledge_owner'): errors.append(f'{sid} View cannot own knowledge')
        for route in row.get('legacy_routes',[]):
            if route in seen or route in legacy: errors.append(f'legacy route collision {route}')
            legacy[route]=sid
    return p

def main():
    errors=[]; rooms=validate_rooms(errors); validate_surfaces(errors,rooms)
    if errors:
        print('POTATO HOUSE GOVERNANCE VALIDATION FAILED'); [print('-',e) for e in errors]; return 1
    print('POTATO HOUSE GOVERNANCE VALIDATION PASSED: Rooms and public surfaces'); return 0

if __name__=='__main__': raise SystemExit(main())
