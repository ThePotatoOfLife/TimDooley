#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ROOMS=ROOT/'data/house/rooms.json'; ROOM_SCHEMA=ROOT/'schemas/house-room-registry.schema.json'
SURFACES=ROOT/'data/house/public-surfaces.json'; SURFACE_SCHEMA=ROOT/'schemas/house-public-surface-registry.schema.json'
TOPOLOGY=ROOT/'knowledge/research/potato-house-master/public-route-topology.json'
HOUSE_TOPOLOGY=ROOT/'data/house/topology.json'
CONCEPT_TOPOLOGY=ROOT/'data/house/concept-topology.json'; CONCEPT_TOPOLOGY_SCHEMA=ROOT/'schemas/house-concept-topology.schema.json'
TOPOLOGY_FIXTURE=ROOT/'data/house/topology-golden-fixture.json'
TOPOLOGY_CONTEXT_JS=ROOT/'app/topology-context.js'
TOPOLOGY_CONTEXT_PAGES={
    ROOT/'religion/index.html':('potato-of-life','father','son','spirit','door'),
    ROOT/'philosophy/index.html':('seed','root','door','spiral','fruit','garden'),
    ROOT/'life-body/index.html':('potato','eye','seed','root','spirit'),
    ROOT/'science/index.html':('plane','axis','cross','spiral'),
}
ROOM_IDS=('potatoverse-canon','archive-sources','time-history','traditions-texts','science-formal-models','life-body','world-systems','culture-information','works','research-lab')
GATEWAYS=('tim','religion','philosophy','science','world')
GATEWAY_ROUTES=('/tim-dooley/','/religion/','/philosophy/','/science/','/world/')
REQUIRED_SURFACES={
    'story':'/tim-dooley/story/',
    'collection':'/corporium/',
    'works':'/works/',
    'questions':'/questions/',
    'index-a-z':'/index-a-z/',
    'context':'/context/',
    'interpretive-justice':'/philosophy/interpretive-justice.html',
    'trinity':'/religion/trinity/',
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
    for sid in p.get('secondary_global_ids',[]):
        if sid not in by: errors.append(f'secondary_global_ids references unknown surface {sid}')
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


def validate_concept_topology(errors,rooms,surfaces):
    data=load(CONCEPT_TOPOLOGY,errors); sch=load(CONCEPT_TOPOLOGY_SCHEMA,errors)
    if data and sch: schema(data,sch,'concept_topology',errors)
    if not data: return
    room_ids={x.get('id') for x in rooms.get('rooms',[]) if isinstance(x,dict)}
    surface_ids={x.get('id') for x in surfaces.get('surfaces',[]) if isinstance(x,dict)}
    orientations=set(data.get('field_orientations',[]))
    roles=set(data.get('topology_roles',[]))
    regimes=set(data.get('boundary_regimes',[]))
    ids=[]; by={}
    for row in data.get('concepts',[]):
        if not isinstance(row,dict): continue
        cid=row.get('id'); ids.append(cid); by[cid]=row
        for value in row.get('field_orientation',[]):
            if value not in orientations: errors.append(f'concept {cid} unknown field orientation {value}')
        for value in row.get('topology_roles',[]):
            if value not in roles: errors.append(f'concept {cid} unknown topology role {value}')
        regime=row.get('boundary_regime')
        if regime is not None and regime not in regimes: errors.append(f'concept {cid} unknown boundary regime {regime}')
        for rid in row.get('room_ids',[]):
            if rid not in room_ids: errors.append(f'concept {cid} unknown Room {rid}')
        for sid in row.get('public_surface_ids',[]):
            if sid not in surface_ids: errors.append(f'concept {cid} unknown public surface {sid}')
    if len(ids)!=len(set(ids)): errors.append('concept topology ids must be unique')
    required={'potato-of-life','father','son','source-field','manifestation-field','door','plane','axis','cross','eye','face','spirit','potato','seed','root','tree','mountain','ladder','spiral','fruit','garden','shell-cube','swamp'}
    missing=sorted(required-set(ids))
    if missing: errors.append('concept topology missing core operators: '+', '.join(missing))
    cross=by.get('cross',{})
    if 'intersection' not in cross.get('topology_roles',[]) or 'shared' not in cross.get('field_orientation',[]):
        errors.append('Cross must remain a shared intersection operator')
    door=by.get('door',{})
    if 'overlap' not in door.get('topology_roles',[]) or 'shared' not in door.get('field_orientation',[]):
        errors.append('Door must remain a shared overlap operator')
    manifestation=by.get('manifestation-field',{})
    if manifestation.get('boundary_regime')=='shell-cube':
        errors.append('Manifestation field must not collapse into Shell/Cube regime')
    relation_type_ids=[x.get('id') for x in data.get('relation_types',[]) if isinstance(x,dict)]
    relation_types=set(relation_type_ids)
    if len(relation_type_ids)!=len(relation_types): errors.append('concept topology relation type ids must be unique')
    relation_ids=[]; relation_rows=[]
    for rel in data.get('relations',[]):
        if not isinstance(rel,dict): continue
        relation_rows.append(rel); relation_ids.append(rel.get('id'))
        if rel.get('from') not in by: errors.append(f'relation {rel.get("id")} unknown source concept {rel.get("from")}')
        if rel.get('to') not in by: errors.append(f'relation {rel.get("id")} unknown target concept {rel.get("to")}')
        if rel.get('type') not in relation_types: errors.append(f'relation {rel.get("id")} unknown relation type {rel.get("type")}')
    if len(relation_ids)!=len(set(relation_ids)): errors.append('concept topology relation ids must be unique')
    required_relations={
        ('door','source-field','intersection-of'),
        ('door','manifestation-field','intersection-of'),
        ('plane','door','sections'),
        ('cross','door','located-within'),
        ('ladder','door','orders'),
        ('root','tree','supports'),
        ('tree','fruit','differentiates-into'),
        ('fruit','seed','returns-as'),
        ('potato-of-life','father','expresses-through'),
        ('potato-of-life','son','expresses-through'),
        ('potato-of-life','spirit','expresses-through'),
        ('father','source-field','oriented-toward'),
        ('son','manifestation-field','oriented-toward'),
        ('son','door','specializes-as'),
    }
    actual_relations={(x.get('from'),x.get('to'),x.get('type')) for x in relation_rows}
    relation_by_id={x.get('id'):x for x in relation_rows if x.get('id')}
    missing_relations=sorted(required_relations-actual_relations)
    if missing_relations: errors.append('concept topology missing core relations: '+', '.join(map(str,missing_relations)))

    traversal_ids=[]; traversal_by={}
    for row in data.get('canonical_traversals',[]):
        if not isinstance(row,dict): continue
        tid=row.get('id'); traversal_ids.append(tid); traversal_by[tid]=row
        sequence=row.get('concept_sequence',[])
        for cid in sequence:
            if cid not in by: errors.append(f'traversal {tid} unknown concept {cid}')
        relation_ids=row.get('relation_ids',[])
        for rid in relation_ids:
            if rid not in relation_by_id: errors.append(f'traversal {tid} unknown relation {rid}')
        used=set()
        for rid in relation_ids:
            rel=relation_by_id.get(rid,{})
            used.update((rel.get('from'),rel.get('to')))
        missing_nodes=sorted({cid for cid in sequence if cid not in used})
        if missing_nodes: errors.append(f'traversal {tid} sequence concepts not covered by relations: {missing_nodes}')
    if len(traversal_ids)!=len(set(traversal_ids)): errors.append('canonical traversal ids must be unique')

    fixture=load(TOPOLOGY_FIXTURE,errors)
    if fixture:
        for cid in fixture.get('required_concepts',[]):
            if cid not in by: errors.append(f'topology fixture missing required concept: {cid}')
        for rel in fixture.get('required_relations',[]):
            sig=(rel.get('from'),rel.get('to'),rel.get('type'))
            if sig not in actual_relations: errors.append(f'topology fixture missing required relation: {sig}')
        for rel in fixture.get('forbidden_relations',[]):
            sig=(rel.get('from'),rel.get('to'),rel.get('type'))
            if sig in actual_relations: errors.append(f'topology fixture forbidden relation present: {sig}')
        for inv in fixture.get('textual_invariants',[]):
            cid=inv.get('concept'); token=str(inv.get('contains','')).casefold()
            row=by.get(cid,{})
            hay=' '.join(str(row.get(k,'')) for k in ('operation','boundary')).casefold()
            if token and token not in hay: errors.append(f'topology fixture textual invariant failed: {cid} must contain {inv.get("contains")!r}')
        for tid in fixture.get('required_traversals',[]):
            if tid not in traversal_by: errors.append(f'topology fixture missing required traversal: {tid}')

    if not TOPOLOGY_CONTEXT_JS.is_file():
        errors.append('missing shared topology context runtime: app/topology-context.js')
    else:
        runtime=TOPOLOGY_CONTEXT_JS.read_text(encoding='utf-8',errors='replace')
        for marker in ('data-house-topology-context','data-house-concepts','data-house-topology-traversals','canonical_traversals','relation_types','relations','slice(0,6)','House context'):
            if marker not in runtime: errors.append(f'topology context runtime missing marker: {marker}')
        if 'document.querySelectorAll' not in runtime or 'fetch(src)' not in runtime:
            errors.append('topology context runtime must progressively enhance declared page regions from canonical topology data')

    trinity_page=ROOT/'religion/trinity/index.html'
    if not trinity_page.is_file():
        errors.append('missing Potato of Life Trinity specialist reader')
    else:
        text=trinity_page.read_text(encoding='utf-8',errors='replace')
        for marker in ('THE POTATO','One Potato of Life','data-house-concepts="potato-of-life,father,son,spirit,door"','../../app/topology-context.js','../../house/#operators'):
            if marker not in text: errors.append(f'religion/trinity/index.html missing Trinity reader marker: {marker}')

    paths_page=ROOT/'paths/index.html'
    if not paths_page.is_file():
        errors.append('missing Paths reader for topology traversals')
    else:
        text=paths_page.read_text(encoding='utf-8',errors='replace')
        for marker in ('data-house-topology-traversals','../app/topology-context.js','../house/#operators','Topology traversals'):
            if marker not in text: errors.append(f'paths/index.html missing topology traversal marker: {marker}')

    for page,expected in TOPOLOGY_CONTEXT_PAGES.items():
        if not page.is_file():
            errors.append(f'missing topology context page: {page.relative_to(ROOT)}'); continue
        text=page.read_text(encoding='utf-8',errors='replace')
        if 'data-house-topology-context' not in text:
            errors.append(f'{page.relative_to(ROOT)} missing opt-in topology context region')
        m=re.search(r'data-house-concepts=["\']([^"\']+)["\']',text)
        declared=tuple(x.strip() for x in (m.group(1).split(',') if m else []) if x.strip())
        if declared!=expected: errors.append(f'{page.relative_to(ROOT)} topology concepts drifted: {declared!r}')
        for cid in declared:
            if cid not in by: errors.append(f'{page.relative_to(ROOT)} topology context references unknown concept {cid}')
        if '../app/topology-context.js' not in text:
            errors.append(f'{page.relative_to(ROOT)} missing shared topology context runtime include')
        if '../house/#operators' not in text:
            errors.append(f'{page.relative_to(ROOT)} topology context must retain a no-JS House fallback link')


def validate_symbolic_planes(errors,rooms):
    data=load(HOUSE_TOPOLOGY,errors)
    if not data: return
    projection=data.get('symbolic_planes')
    if not isinstance(projection,dict):
        errors.append('house topology missing symbolic_planes projection'); return
    rows=projection.get('planes',[])
    ids=[x.get('id') for x in rows if isinstance(x,dict)]
    expected=['heaven-plane','world-plane','below-plane']
    if ids!=expected: errors.append('symbolic planes must remain ordered heaven-plane, world-plane, below-plane')
    room_ids={x.get('id') for x in rooms.get('rooms',[]) if isinstance(x,dict)}
    for row in rows:
        if not isinstance(row,dict): continue
        pid=row.get('id')
        for key in ('primary_room_ids','crossing_room_ids'):
            for rid in row.get(key,[]):
                if rid not in room_ids: errors.append(f'{pid} references unknown Room {rid}')
        if not row.get('navigation'): errors.append(f'{pid} must expose navigation routes')
        if not row.get('subjects'): errors.append(f'{pid} must expose subject groupings')
    below=next((x for x in rows if isinstance(x,dict) and x.get('id')=='below-plane'),{})
    text_blob=' '.join(projection.get('projection_rules',[]))+' '+below.get('description','')
    if 'not identical with Earth' not in text_blob and 'not Earth' not in text_blob:
        errors.append('Below Plane boundary must preserve distinction from Earth/Manifestation')
    world=next((x for x in rows if isinstance(x,dict) and x.get('id')=='world-plane'),{})
    if 'Plane' not in world.get('aliases',[]):
        errors.append('World Plane must preserve Plane alias')
    compass=data.get('symbolic_compass')
    if not isinstance(compass,dict):
        errors.append('symbolic compass missing'); return
    directions=compass.get('directions',[])
    expected_dirs=['n','ne','e','se','s','sw','w','nw']
    if [x.get('id') for x in directions if isinstance(x,dict)]!=expected_dirs:
        errors.append('symbolic compass directions/order must remain N, NE, E, SE, S, SW, W, NW')
    expected_rooms=['potatoverse-canon','traditions-texts','science-formal-models','life-body','world-systems','culture-information','time-history','archive-sources']
    if [x.get('room_id') for x in directions if isinstance(x,dict)]!=expected_rooms:
        errors.append('symbolic compass Room mapping drifted')
    if compass.get('center',{}).get('room_id')!='research-lab':
        errors.append('symbolic compass center must remain Research Lab')
    if compass.get('outer_ring',{}).get('room_id')!='works':
        errors.append('symbolic compass outer ring must remain Works/Fruit')
    for row in directions:
        if not isinstance(row,dict): continue
        focus=row.get('focus_by_plane',{})
        for pid in ('heaven-plane','world-plane','below-plane'):
            if pid not in focus: errors.append(f'compass direction {row.get("id")} missing {pid} focus')
        for sid in row.get('subroom_ids',[]):
            if not isinstance(sid,str) or not sid: errors.append(f'compass direction {row.get("id")} has invalid subroom id')
    rules=' '.join(compass.get('entity_projection_rule',[])).casefold()
    for token in ('historically rooted','does not create several entities','not synonyms','potatoverse mappings'):
        if token not in rules: errors.append(f'symbolic compass entity projection rule missing boundary: {token}')

def main():
    errors=[]; rooms=validate_rooms(errors); surfaces=validate_surfaces(errors,rooms); validate_concept_topology(errors,rooms,surfaces); validate_symbolic_planes(errors,rooms)
    if errors:
        print('POTATO HOUSE GOVERNANCE VALIDATION FAILED'); [print('-',e) for e in errors]; return 1
    print('POTATO HOUSE GOVERNANCE VALIDATION PASSED: Rooms, surfaces, semantic topology, three planes, cardinal compass, reader corridor and route authority converge'); return 0

if __name__=='__main__': raise SystemExit(main())