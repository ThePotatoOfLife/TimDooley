#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ROOMS=ROOT/'data/house/rooms.json'; ROOM_SCHEMA=ROOT/'schemas/house-room-registry.schema.json'
SURFACES=ROOT/'data/house/public-surfaces.json'; SURFACE_SCHEMA=ROOT/'schemas/house-public-surface-registry.schema.json'
TOPOLOGY=ROOT/'knowledge/research/potato-house-master/public-route-topology.json'
ROOM_IDS=('potatoverse-canon','archive-sources','time-history','traditions-texts','science-formal-models','life-body','world-systems','culture-information','works','research-lab')
GATEWAYS=('tim','religion','philosophy','science','world')
GATEWAY_ROUTES=('/tim-dooley/','/religion/','/philosophy/','/science/','/world/')
REQUIRED_SURFACES={
    'story':'/tim-dooley/story/',
    'collection':'/corporium/',
    'works':'/works/',
    'great-book':'/great-book/',
    'questions':'/questions/',
    'index-a-z':'/index-a-z/',
    'context':'/context/',
    'interpretive-justice':'/philosophy/interpretive-justice.html',
}
WORKS_FILE=ROOT/'works/index.html'
WORKS_MARKERS=(
    'data-reader-surface="works"','Play &amp; Simulation','Writing &amp; Performance','Music &amp; Sound',
    'Visual &amp; Symbolic Art','Recovered &amp; Experimental Works','../tim-dooley/','../tim-dooley/story/',
    '../corporium/','../explore/#branch=works','../context/source-authority/',
)
HOME_FILE=ROOT/'index.html'
HOME_CORRIDOR=(
    '<strong>Ways in</strong>',
    'href="tim-dooley/story/">Story</a>',
    'href="timeline/">Timeline</a>',
    'href="corporium/">Collection</a>',
    'href="works/">Works</a>',
    'href="questions/"',
    'href="index-a-z/"',
    'href="explore/"',
    'href="context/source-authority/"',
    'href="tools/tts/"',
)
DISCOVERY_BUILDER=ROOT/'scripts/build_discovery.py'
AUTHORITY_BUILDER=ROOT/'scripts/build_site_authority.py'

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

def validate_works_reader(errors):
    if not WORKS_FILE.is_file():
        errors.append('registered Works surface missing source reader: works/index.html'); return
    text=WORKS_FILE.read_text(encoding='utf-8',errors='replace')
    for marker in WORKS_MARKERS:
        if marker not in text: errors.append(f'works/index.html missing reader marker: {marker}')
    lower=text.lower()
    if not ('does not automatically become doctrine' in lower and 'evidence' in lower):
        errors.append('works/index.html must preserve creative-work doctrine/evidence boundary')

def validate_home_corridor(errors):
    if not HOME_FILE.is_file(): errors.append('missing homepage index.html'); return
    text=HOME_FILE.read_text(encoding='utf-8',errors='replace')
    for marker in HOME_CORRIDOR:
        if marker not in text: errors.append(f'index.html missing Ways-in/utility marker: {marker}')
    nav=re.search(r'<nav class="sections"[^>]*>(.*?)</nav>',text,flags=re.I|re.S)
    if not nav: errors.append('index.html missing canonical sections nav')
    else:
        hrefs=re.findall(r'href=["\']([^"\']+)["\']',nav.group(1),flags=re.I)
        if hrefs!=[x.lstrip('/') for x in GATEWAY_ROUTES]: errors.append(f'homepage primary routes drifted: {hrefs!r}')

def validate_builder_authority(errors):
    checks=(
        (DISCOVERY_BUILDER,'PRIMARY_DOORS = (\n    ("tim"'),
        (AUTHORITY_BUILDER,'PRIMARY_ROUTES = {\n    "tim"'),
    )
    for path,legacy in checks:
        text=path.read_text(encoding='utf-8',errors='replace')
        if 'from house_public_surfaces import primary_gateway_rows' not in text:
            errors.append(f'{path.name} must consume House primary_gateway_rows')
        if legacy in text:
            errors.append(f'{path.name} must not maintain independent primary route table')

def validate_navigation_subsets(public_surfaces,by,errors):
    primary=set(public_surfaces.get('primary_gateway_ids',[]))
    for field in ('housebar_secondary_ids','footer_global_ids','secondary_global_ids'):
        values=public_surfaces.get(field,[])
        for sid in values:
            row=by.get(sid)
            if row is None:
                errors.append(f'{field} references unknown surface {sid}')
            elif row.get('status')!='active':
                errors.append(f'{field} references non-active surface {sid}')
    for field in ('housebar_secondary_ids','footer_global_ids'):
        overlap=sorted(primary & set(public_surfaces.get(field,[])))
        if overlap:
            errors.append(f'{field} must not duplicate primary Doors: {", ".join(overlap)}')
    housebar=public_surfaces.get('housebar_secondary_ids',[])
    if not housebar or housebar[0]!='great-book':
        errors.append('housebar_secondary_ids must keep Great Book as the first secondary path')

def validate_surfaces(errors,rooms):
    p=load(SURFACES,errors); s=load(SURFACE_SCHEMA,errors); topology=load(TOPOLOGY,errors)
    if p and s: schema(p,s,'public_surfaces',errors)
    rows=p.get('surfaces',[]); by={x.get('id'):x for x in rows if isinstance(x,dict) and x.get('id')}
    if tuple(p.get('primary_gateway_ids',[]))!=GATEWAYS: errors.append('primary_gateway_ids invalid')
    routes=tuple(by.get(x,{}).get('canonical_route') for x in GATEWAYS)
    if routes!=GATEWAY_ROUTES: errors.append(f'primary gateway routes invalid: {routes!r}')
    for sid,route in REQUIRED_SURFACES.items():
        if sid not in by: errors.append(f'missing required mature public surface: {sid}')
        elif by[sid].get('canonical_route')!=route: errors.append(f'{sid} canonical route must be {route}')
    if by.get('interpretive-justice',{}).get('primary_parent')!='philosophy':
        errors.append('Interpretive Justice specialist surface must live under Philosophy')
    validate_navigation_subsets(p,by,errors)
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
    topology_rows=topology.get('records',[])
    topology_by={x.get('surface_id'):x for x in topology_rows if isinstance(x,dict) and x.get('surface_id')}
    if len(topology_by)!=len(topology_rows): errors.append('topology contains duplicate or invalid surface_id records')
    active_ids={sid for sid,row in by.items() if row.get('status')=='active'}
    missing_topology=sorted(active_ids-set(topology_by)); extra_topology=sorted(set(topology_by)-active_ids)
    if missing_topology: errors.append('active public surfaces missing topology: '+', '.join(missing_topology))
    if extra_topology: errors.append('topology contains non-active/unknown surfaces: '+', '.join(extra_topology))
    for sid in sorted(active_ids & set(topology_by)):
        row=by[sid]; topo=topology_by[sid]
        if topo.get('canonical_route')!=row.get('canonical_route'): errors.append(f'{sid} topology route drift')
        if topo.get('surface_type')!=row.get('surface_type'): errors.append(f'{sid} topology surface_type drift')
        if topo.get('room_ids')!=row.get('primary_room_ids'): errors.append(f'{sid} topology Room drift')
    validate_works_reader(errors); validate_home_corridor(errors); validate_builder_authority(errors)
    return p

def main():
    errors=[]; rooms=validate_rooms(errors); validate_surfaces(errors,rooms)
    if errors:
        print('POTATO HOUSE GOVERNANCE VALIDATION FAILED'); [print('-',e) for e in errors]; return 1
    print('POTATO HOUSE GOVERNANCE VALIDATION PASSED: Rooms, surfaces, topology, navigation subsets, reader corridor and route authority converge'); return 0

if __name__=='__main__': raise SystemExit(main())
