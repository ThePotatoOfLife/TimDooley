#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ROOMS=ROOT/'data/house/rooms.json'; ROOM_SCHEMA=ROOT/'schemas/house-room-registry.schema.json'
SURFACES=ROOT/'data/house/public-surfaces.json'; SURFACE_SCHEMA=ROOT/'schemas/house-public-surface-registry.schema.json'
TOPOLOGY=ROOT/'knowledge/research/potato-house-master/public-route-topology.json'
HOUSE_TOPOLOGY=ROOT/'data/house/topology.json'
PROJECT_CENTER=ROOT/'data/house/project-center.json'
CROSSCUTTING_LENSES=ROOT/'data/house/crosscutting-lenses.json'
LIVING_PROJECT_MAP=ROOT/'data/house/living-project-map.json'
PROJECT_SYNTHESIS=ROOT/'data/house/project-synthesis.json'
SHADOW_OVERLAY=ROOT/'knowledge/core/shadow-integration-overlay.json'
GARDEN_REGIME=ROOT/'knowledge/core/garden-regime-mechanics.json'
REPAIR_FORGE=ROOT/'knowledge/core/repair-forge-protocol.json'
FRUIT_ATLAS=ROOT/'knowledge/core/fruit-consequence-evaluation-atlas.json'
TREE_BRANCHING=ROOT/'knowledge/core/tree-branching-pruning-atlas.json'
KNOWLEDGE_FORK=ROOT/'knowledge/core/knowledge-fork-discernment-atlas.json'
HISTORY_REVISION=ROOT/'data/house/history-canon-revision-protocol.json'
WORKS_FRUIT=ROOT/'data/house/works-fruit-contract.json'
LOCAL_CENTERS=ROOT/'data/house/local-center-interface-patterns.json'
POTATO_CENTER_PAGE=ROOT/'potato-of-life/index.html'
ORIENTATION_POPULATION=ROOT/'data/house/orientation-population.json'
TREE_PLANE_ROUTING=ROOT/'data/house/tree-plane-routing.json'
SEED_SPIRAL_ROUTING=ROOT/'data/house/seed-spiral-routing.json'
NAVIGATION_MANIFEST=ROOT/'data/house/navigation-manifest.json'
RELIGIOUS_BRANCH_ATLAS=ROOT/'data/house/religious-symbolic-branch-atlas.json'
PROVIDENCE_STRUCTURE=ROOT/'data/house/providence-pillars-esoteric-structure.json'
LAYER_TERRAIN_ATLAS=ROOT/'data/house/layer-terrain-regime-atlas.json'
PLACEMENT_MATRIX=ROOT/'data/house/placement-matrix.json'
SUBROOMS=ROOT/'data/house/subrooms.json'
SPECIALIST_SUBVIEWS=ROOT/'data/house/specialist-subviews.json'
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
HOME_SPINE=(
    'class="project-spine"',
    'aria-label="Homepage learning path"',
    'id="learn-the-structure"',
    'id="homeTeachingNav"',
    'data-teach="whole"',
    'data-teach="coordinates"',
    'data-teach="planes"',
    'data-teach="terrain-regime"',
    'data-teach="living-systems"',
    'data-teach="operators"',
    'data-teach="inhabitants"',
    "fetch('data/house/layer-terrain-regime-atlas.json')",
    "fetch('data/house/concept-topology.json')",
    'Direction alone does not decide Life or Strife',
    'id="axisLevelTabs"',
    'Eleven transformation regimes',
    'D1–D11 are not eleven literal floors',
    "fetch('data/axis-flow-contract.json')",
    'id="project-motion"',
    'id="materialized-now"',
    'id="reality-cases"',
    'id="working-capabilities"',
    'data-home-stat="rooms"',
    'data-home-stat="foundations"',
    'data-home-stat="cases"',
    'data-home-stat="below"',
    'data-cycle="knowledge"',
    'data-cycle="generative"',
    'href="potato-of-life/"',
    'href="house/"',
    'href="rooms/"',
    'href="explore/"',
    'class="public-doors"',
    'href="tim-dooley/"',
    'href="religion/"',
    'href="philosophy/"',
    'href="science/"',
    'href="world/"',
    'Seed</b><i>→</i><b>Foundation</b><i>→</i><b>Root</b><i>→</i><b>Tree</b><i>→</i><b>Fruit</b><i>→</i><b>Memory</b><i>→</i><b>Return</b>',
    'href="timeline/"',
    'href="works/"',
    'href="context/source-authority/"',
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
    for marker in HOME_SPINE:
        if marker not in text: errors.append(f'index.html missing project-spine marker: {marker}')
    nav=re.search(r'<nav class="public-doors"[^>]*>(.*?)</nav>',text,flags=re.I|re.S)
    if not nav: errors.append('index.html missing canonical public-doors nav')
    else:
        hrefs=re.findall(r'href=["\']([^"\']+)["\']',nav.group(1),flags=re.I)
        if hrefs!=[x.lstrip('/') for x in GATEWAY_ROUTES]: errors.append(f'homepage public-door routes drifted: {hrefs!r}')

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



def validate_specialist_subviews(errors,surfaces):
    data=load(SPECIALIST_SUBVIEWS,errors)
    if not data: return
    surface_ids={x.get('id') for x in surfaces.get('surfaces',[]) if isinstance(x,dict) and x.get('id')}
    subrooms=load(SUBROOMS,errors)
    room_ids={x.get('id') for x in subrooms.get('subrooms',[]) if isinstance(x,dict) and x.get('id')}
    ids=[]; routes=[]
    for row in data.get('records',[]):
        if not isinstance(row,dict):
            errors.append('specialist subview record must be object'); continue
        sid=row.get('id'); route=row.get('route'); parent=row.get('parent_surface_id')
        ids.append(sid); routes.append(route)
        if not sid or not isinstance(sid,str): errors.append('specialist subview missing id')
        if not route or not str(route).startswith('/'): errors.append(f'specialist subview {sid} invalid route')
        if parent not in surface_ids: errors.append(f'specialist subview {sid} unknown parent surface {parent}')
        if row.get('classification') not in {'living-specialist','historical-source','generated-view','compatibility','duplicate-candidate'}:
            errors.append(f'specialist subview {sid} invalid classification')
        for rid in row.get('room_ids',[]):
            if rid not in room_ids: errors.append(f'specialist subview {sid} unknown nested Room {rid}')
        source=ROOT/str(route).strip('/')/'index.html' if str(route).endswith('/') else ROOT/str(route).lstrip('/')
        if not source.exists(): errors.append(f'specialist subview {sid} missing source route {route}')
        for owner in row.get('current_owner_refs',[]):
            if not (ROOT/owner).exists(): errors.append(f'specialist subview {sid} missing current owner ref {owner}')
    if len(ids)!=len(set(ids)): errors.append('specialist subview ids must be unique')
    if len(routes)!=len(set(routes)): errors.append('specialist subview routes must be unique')
    if set(routes) & {x.get('canonical_route') for x in surfaces.get('surfaces',[]) if isinstance(x,dict)}:
        errors.append('specialist subview route must not duplicate a main public surface route')

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
    if compass.get('center',{}).get('node_id')!='axis':
        errors.append('symbolic compass spatial center must remain Axis')
    if compass.get('center',{}).get('inner_ring_room_id')!='research-lab':
        errors.append('Research Lab must remain the inner Forge ring around Axis')
    if compass.get('semantic_center',{}).get('node_id')!='potato-of-life':
        errors.append('symbolic compass semantic center must remain Potato of Life')
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
    tree=data.get('symbolic_tree_ecology')
    if not isinstance(tree,dict):
        errors.append('symbolic tree ecology missing'); return
    fork=tree.get('central_fork',{})
    if 'upstream of both Life and Strife' not in fork.get('principle',''):
        errors.append('Tree of Knowledge must remain upstream of Life and Strife')
    zone_ids=[x.get('id') for x in tree.get('zones',[]) if isinstance(x,dict)]
    expected_zones=['roots','trunk','life-branches','strife-branches','canopy']
    if zone_ids!=expected_zones:
        errors.append('symbolic tree ecology zones/order drifted')
    foundations=[x.get('id') for x in tree.get('religious_foundations',[]) if isinstance(x,dict)]
    if foundations!=['own-tradition','reception','motif','project-map']:
        errors.append('religious foundation reading order drifted')
    guards=' '.join(x.get('guard','') for x in tree.get('zones',[]) if isinstance(x,dict)).casefold()
    for token in ('not classify peoples','does not assert literal divinity','separate categories','not a universal claim'):
        if token not in guards:
            errors.append(f'symbolic tree ecology missing guard: {token}')
    akashic=tree.get('akashic_tree_view',{})
    if 'does not assert a literal Akashic Record' not in akashic.get('boundary',''):
        errors.append('Akashic Tree view must remain an archive metaphor rather than evidence claim')


def validate_orientation_population(errors,rooms):
    population=load(ORIENTATION_POPULATION,errors); subrooms=load(SUBROOMS,errors)
    if not population or not subrooms: return
    sub_ids=[x.get('id') for x in subrooms.get('subrooms',[]) if isinstance(x,dict)]
    rows=population.get('room_population',[])
    ids=[x.get('id') for x in rows if isinstance(x,dict)]
    if ids!=sub_ids:
        errors.append('orientation population must cover every nested Room exactly in registry order')
    compass_dirs={'n','ne','e','se','s','sw','w','nw','center','outer','crosscutting'}
    plane_ids={'heaven-plane','world-plane','below-plane'}
    zone_ids={'roots','trunk','life-branches','strife-branches','canopy'}
    for row in rows:
        if not isinstance(row,dict): continue
        rid=row.get('id')
        if row.get('compass_direction') not in compass_dirs: errors.append(f'orientation population {rid} invalid compass direction')
        if not set(row.get('plane_ids',[]))<=plane_ids: errors.append(f'orientation population {rid} invalid plane')
        if not set(row.get('tree_zone_ids',[]))<=zone_ids: errors.append(f'orientation population {rid} invalid tree zone')
        if row.get('visibility') not in {'landmark','room-detail','archive-only'}: errors.append(f'orientation population {rid} invalid visibility')
    landmark_ids=[x.get('id') for x in population.get('landmarks',[]) if isinstance(x,dict)]
    if len(landmark_ids)!=len(set(landmark_ids)): errors.append('orientation landmark ids must be unique')
    if len(population.get('landmarks',[]))>24: errors.append('orientation landmarks should remain sparse; move excess nodes to Room detail or archive-only')
    rules=' '.join(population.get('rules',[])).casefold()
    for token in ('do not change knowledge ownership','compass shows landmarks sparingly','remain rooted in their own traditions','not the moral essence'):
        if token not in rules: errors.append(f'orientation population missing governance rule: {token}')


def validate_tree_plane_routing(errors):
    data=load(TREE_PLANE_ROUTING,errors)
    if not data: return
    if data.get('master_rule')!='Planes are standing surfaces. Trees are vertical branching routes. Rooms are subject owners. Entities and traditions are inhabitants/subjects with anchors and projections. Corridors are typed relations between them.':
        errors.append('tree-plane routing master rule drifted')
    center=data.get('centerline',{})
    if center.get('id')!='axis': errors.append('Axis must remain exact centerline')
    if center.get('inner_ring',{}).get('room_id')!='research-lab': errors.append('Research Lab must remain inner Forge ring')
    if center.get('outer_ring',{}).get('room_id')!='works': errors.append('Works must remain outer Fruit ring')
    plane_ids=[x.get('id') for x in data.get('planes',[]) if isinstance(x,dict)]
    if plane_ids!=['heaven-plane','world-plane','below-plane']: errors.append('tree-plane routing plane order drifted')
    organisms={x.get('id'):x for x in data.get('vertical_organisms',[]) if isinstance(x,dict)}
    for oid in ('akashic-tree','tree-of-knowledge','tree-of-life','tree-of-strife'):
        if oid not in organisms: errors.append(f'tree-plane routing missing {oid}')
    life=organisms.get('tree-of-life',{})
    if life.get('spans')!=['below-plane','world-plane','heaven-plane']: errors.append('Tree of Life must span all three planes')
    strife=organisms.get('tree-of-strife',{})
    if strife.get('spans')!=['below-plane','world-plane']: errors.append('Tree of Strife must span Below and World')
    if 'Roots of Ash are a principal root-state' not in strife.get('ash_rule',''): errors.append('Roots of Ash relation to Tree of Strife must remain explicit')
    subjects=' '.join(x.get('rule','') for x in data.get('subject_placement_rules',[]) if isinstance(x,dict)).casefold()
    for token in ('do not infer literal demonic identity','own-tradition','do not merge them with demonology','observable control/capture mechanisms'):
        if token not in subjects: errors.append(f'tree-plane subject placement boundary missing: {token}')


def validate_seed_spiral_routing(errors):
    data=load(SEED_SPIRAL_ROUTING,errors)
    if not data: return
    pivot=data.get('geometry',{}).get('seed_pivot',{})
    if pivot.get('id')!='C_S': errors.append('Seed Junction must remain C_S')
    if 'Seed-of-Death ↔ Seed-of-Life' not in pivot.get('role',''): errors.append('C_S must retain Seed Death/Life transition role')
    states={x.get('id'):x for x in data.get('seed_states',[]) if isinstance(x,dict)}
    for sid in ('seed-of-death','seed-of-life','fruit-seed'):
        if sid not in states: errors.append(f'seed spiral routing missing {sid}')
    routes={x.get('id'):x for x in data.get('spiral_routes',[]) if isinstance(x,dict)}
    for rid in ('rooting-spiral','drain-spiral','sprouting-spiral','repair-spiral','return-spiral'):
        if rid not in routes: errors.append(f'seed spiral routing missing {rid}')
    if routes.get('rooting-spiral',{}).get('vertical_sign')!='negative': errors.append('Rooting Spiral must remain downward/generative')
    if routes.get('drain-spiral',{}).get('vertical_sign')!='negative': errors.append('Drain Spiral must remain downward/degenerative')
    if routes.get('sprouting-spiral',{}).get('vertical_sign')!='positive': errors.append('Sprouting Spiral must remain upward/generative')
    if routes.get('return-spiral',{}).get('vertical_sign')!='negative': errors.append('Return Spiral must remain downward/generative return')
    laws=' '.join(data.get('placement_laws',[])).casefold()
    for token in ('states/transitions of generative potential','not the deepest point','downward spiral can be rooting','upward spiral can be life','ring and spiral must remain distinct'):
        if token not in laws: errors.append(f'seed spiral routing missing law: {token}')
    if data.get('ring',{}).get('vertical_sign')!='zero': errors.append('Ring must remain zero axial displacement')


def validate_navigation_consolidation(errors):
    manifest=load(NAVIGATION_MANIFEST,errors); atlas=load(RELIGIOUS_BRANCH_ATLAS,errors)
    if not manifest or not atlas: return
    owners=[x.get('owner') for x in manifest.get('authorities',[]) if isinstance(x,dict)]
    required_owners={
        'data/house/rooms.json','data/house/subrooms.json','data/house/holdings.json',
        'data/house/topology.json','data/house/concept-topology.json',
        'data/house/orientation-population.json','data/house/tree-plane-routing.json',
        'data/house/seed-spiral-routing.json','data/axis-flow-contract.json',
        'data/house/religious-symbolic-branch-atlas.json','data/house/project-center.json','knowledge/core/root-system.json'
    }
    missing=sorted(required_owners-set(owners))
    if missing: errors.append('navigation manifest missing authorities: '+', '.join(missing))
    branches={x.get('id') for x in atlas.get('branches',[]) if isinstance(x,dict)}
    node_rows=[x for x in atlas.get('nodes',[]) if isinstance(x,dict)]
    node_ids=[x.get('id') for x in node_rows]
    if len(node_ids)!=len(set(node_ids)): errors.append('religious branch atlas node ids must be unique')
    room_data=load(SUBROOMS,errors)
    room_ids={x.get('id') for x in room_data.get('subrooms',[]) if isinstance(x,dict)}
    planes={'heaven-plane','world-plane','below-plane'}
    vis={'landmark','room-detail','archive-only'}
    for node in node_rows:
        nid=node.get('id')
        if node.get('branch_id') not in branches: errors.append(f'branch atlas {nid} unknown branch {node.get("branch_id")}')
        for rid in node.get('room_ids',[]):
            if rid not in room_ids: errors.append(f'branch atlas {nid} unknown Room {rid}')
        if not set(node.get('planes',[]))<=planes: errors.append(f'branch atlas {nid} invalid plane')
        if node.get('visibility') not in vis: errors.append(f'branch atlas {nid} invalid visibility')
        for source in node.get('source_files',[]):
            if source.startswith('data/') or source.startswith('knowledge/'):
                if not (ROOT/source).is_file(): errors.append(f'branch atlas {nid} missing source file {source}')
    by=set(node_ids)
    for edge in atlas.get('corridors',[]):
        if not isinstance(edge,dict): continue
        if edge.get('from') not in by or edge.get('to') not in by:
            errors.append(f'branch atlas corridor references unknown node: {edge}')
    branch_ids={x.get('id') for x in atlas.get('branches',[]) if isinstance(x,dict)}
    if 'death-passage' not in branch_ids: errors.append('death-passage branch missing')
    if 'garden-waters' not in branch_ids: errors.append('garden-waters branch missing')
    nodes_by_id={x.get('id'):x for x in node_rows}
    for nid in ('duat','sheol','hades-realm','hel-realm','hall-two-truths'):
        if nodes_by_id.get(nid,{}).get('branch_id')!='death-passage': errors.append(f'{nid} must remain in death-passage rather than demonological branch')
    for nid in ('eden-gan-eden','eden-four-rivers','eden-cherubim-gate'):
        if nodes_by_id.get(nid,{}).get('branch_id')!='garden-waters': errors.append(f'{nid} must remain in garden-waters branch')
    rule=atlas.get('epistemic_rule','').casefold()
    for token in ('own historical/textual tradition','navigation/comparative projections','not proof of literal identity'):
        if token not in rule: errors.append(f'religious branch atlas missing epistemic boundary: {token}')
    if len(node_rows)>80: errors.append('religious branch atlas should remain curated; split deeper population into archive-only registries before exceeding 80 primary nodes')


def validate_providence_structure(errors):
    data=load(PROVIDENCE_STRUCTURE,errors)
    if not data: return
    ids={x.get('id') for x in data.get('historical_findings',[]) if isinstance(x,dict)}
    for rid in ('great-seal-reverse','eye-providence','jachin-boaz-biblical','jachin-boaz-masonic','1776-coincidence-boundary'):
        if rid not in ids: errors.append(f'Providence/pillars atlas missing historical finding {rid}')
    corr={x.get('id') for x in data.get('structural_correspondences',[]) if isinstance(x,dict)}
    for rid in ('twin-pillars-door','pyramid-mountain','eye-above-pyramid','providence-vs-surveillance','base-date-provenance'):
        if rid not in corr: errors.append(f'Providence/pillars atlas missing structural correspondence {rid}')
    rules=' '.join(data.get('anti_conspiracy_rules',[])).casefold()
    for token in ('shared symbols do not prove','shared date does not prove','later masonic or occult adoption does not backdate','eye imagery does not by itself prove','comparative interpretations'):
        if token not in rules: errors.append(f'Providence/pillars atlas missing boundary: {token}')


def validate_layer_terrain_atlas(errors):
    data=load(LAYER_TERRAIN_ATLAS,errors)
    if not data: return
    categories={x.get('id') for x in data.get('categories',[]) if isinstance(x,dict)}
    required={'whole','coordinate','standing-plane','terrain','regime','organism','material-state','threshold','perceptual-layer','process','route','inhabitant'}
    if categories!=required: errors.append('layer terrain atlas category set drifted')
    nodes={x.get('id'):x for x in data.get('nodes',[]) if isinstance(x,dict)}
    for nid in ('potato-of-life','mountain','pyramid','garden','swamp','shadow','roots','tree-of-knowledge','tree-of-life','tree-of-strife','mud','ash','soil','door-pillars','eye','forge','spiral-family'):
        if nid not in nodes: errors.append(f'layer terrain atlas missing {nid}')
    expectations={
        'mountain':'terrain','pyramid':'terrain','garden':'regime','swamp':'terrain','shadow':'perceptual-layer',
        'tree-of-life':'organism','tree-of-strife':'organism','mud':'material-state','ash':'material-state',
        'soil':'material-state','door-pillars':'threshold','eye':'perceptual-layer','forge':'process','spiral-family':'route'
    }
    for nid,cat in expectations.items():
        if nodes.get(nid,{}).get('category')!=cat: errors.append(f'layer terrain atlas {nid} must remain {cat}')
    diffs=' '.join(data.get('crucial_differences',[])).casefold()
    for token in ('below is a reader plane','shadow is an occlusion','literal wetlands are not','mountain is terrain','garden is a generative regime','roots are not strife'):
        if token not in diffs: errors.append(f'layer terrain atlas missing distinction: {token}')


def validate_placement_matrix(errors):
    data=load(PLACEMENT_MATRIX,errors)
    if not data: return
    fam=[x for x in data.get('family_rules',[]) if isinstance(x,dict)]
    ids=[x.get('id') for x in fam]
    required={'heaven-realm','underworld-realm','world-tree','sacred-mountain','temple-city','cave-labyrinth','river-water','gate-door','pillar-axis','serpent-dragon','angel-messenger','demon-adversary','throne-crown','star-planet','judgment-weighing','burial-resurrection'}
    if not required<=set(ids): errors.append('placement matrix missing required family rules: '+', '.join(sorted(required-set(ids))))
    categories={'whole','coordinate','standing-plane','terrain','regime','organism','material-state','threshold','perceptual-layer','process','route','inhabitant'}
    planes={'heaven-plane','world-plane','below-plane'}
    for row in fam:
        if row.get('default_category') not in categories: errors.append(f'placement family {row.get("id")} invalid default category')
        if not set(row.get('default_planes',[]))<=planes: errors.append(f'placement family {row.get("id")} invalid default plane')
        if not row.get('do_not'): errors.append(f'placement family {row.get("id")} missing confusion boundary')
    precedence=data.get('precedence',[])
    if not precedence or not precedence[0].startswith('own-tradition'): errors.append('placement precedence must start with own-tradition / primary-source meaning')
    if data.get('output_contract',{}).get('unresolved_destination')!='research-lab/open-questions': errors.append('unresolved placements must route to Research Lab/Open Questions')


def validate_project_center(errors):
    data=load(PROJECT_CENTER,errors)
    if not data: return
    centers=data.get('center_distinctions',{})
    if centers.get('semantic_center',{}).get('id')!='potato-of-life':
        errors.append('semantic project center must remain Potato of Life')
    if centers.get('spatial_center',{}).get('id')!='axis':
        errors.append('spatial navigation center must remain Axis')
    rings=[x for x in data.get('rings',[]) if isinstance(x,dict)]
    ids=[x.get('id') for x in rings]
    expected=['r0-nucleus','r1-core-structure','r2-living-metabolism','r3-project-domains','r4-comparative-mirrors','r5-archive']
    if ids!=expected: errors.append('project center ring order drifted')
    nucleus=next((x for x in rings if x.get('id')=='r0-nucleus'),{})
    if nucleus.get('node_ids')!=['potato-of-life','father','son','spirit']:
        errors.append('project nucleus must remain Potato of Life / Father / Son / Spirit')
    rules=' '.join(data.get('promotion_rules',[])).casefold()
    for token in ('comparative node cannot enter ring 0–2','volume of sources does not determine centrality','semantic center is potato of life','home should explain ring 0–1'):
        if token not in rules: errors.append(f'project center missing promotion boundary: {token}')


def validate_crosscutting_lenses(errors):
    data=load(CROSSCUTTING_LENSES,errors)
    if not data: return
    expected=['motion','polarity','memory-history','social-formation','embodiment-spirit','practice-path']
    ids=[x.get('id') for x in data.get('lenses',[]) if isinstance(x,dict)]
    if ids!=expected: errors.append('cross-cutting lens order/set drifted')
    rule=data.get('master_rule','').casefold()
    for token in ('does not change who owns the knowledge','does not create a new ontological level'):
        if token not in rule: errors.append(f'cross-cutting lenses missing boundary: {token}')
    mirror_text=' '.join(str(m.get('boundary','')) for lens in data.get('lenses',[]) if isinstance(lens,dict) for m in lens.get('comparative_mirrors',[]) if isinstance(m,dict)).casefold()
    for token in ('not a hidden potatoverse spiral','not evidence that daoism encodes','does not present a literal supernatural akashic record','should not be rewritten as potatoism'):
        if token not in mirror_text: errors.append(f'cross-cutting comparative boundary missing: {token}')
    if not POTATO_CENTER_PAGE.is_file(): errors.append('missing public Potato of Life center reader')
    else:
        page=POTATO_CENTER_PAGE.read_text(encoding='utf-8',errors='replace')
        for marker in ('id="definition"','id="literal-potato"','id="structure"','id="metabolism"','id="lenses"','id="rooms"'):
            if marker not in page: errors.append(f'Potato center reader missing {marker}')


def validate_living_project_map(errors):
    data=load(LIVING_PROJECT_MAP,errors)
    if not data: return
    systems=[x for x in data.get('systems',[]) if isinstance(x,dict)]
    ids=[x.get('id') for x in systems]
    expected=['organism','spirit-relation','memory-history','culture-formation']
    if ids!=expected: errors.append('living project system set/order drifted')
    room_data=load(SUBROOMS,errors)
    room_ids={x.get('id') for x in room_data.get('subrooms',[]) if isinstance(x,dict)}
    parent_rooms={'potatoverse-canon','archive-sources','time-history','traditions-texts','science-formal-models','life-body','world-systems','culture-information','works','research-lab'}
    for row in systems:
        sid=row.get('id')
        for rid in row.get('subroom_ids',[])+row.get('crossing_subroom_ids',[]):
            if rid not in room_ids: errors.append(f'living project {sid} unknown subroom {rid}')
        for rid in row.get('primary_room_ids',[]):
            if rid not in parent_rooms: errors.append(f'living project {sid} unknown primary Room {rid}')
    spirit=next((x for x in systems if x.get('id')=='spirit-relation'),{})
    if spirit.get('primary_room_ids')!=['potatoverse-canon']:
        errors.append('Spirit must remain center-native project canon relation, not a new Room owner')
    anti=' '.join(data.get('anti_redundancy',[])).casefold()
    for token in ('do not create a spirit room','do not create a memory realm','do not make culture synonymous with strife','do not turn body metaphors into anatomy'):
        if token not in anti: errors.append(f'living project missing anti-redundancy rule: {token}')
    routes=data.get('public_routes',{})
    required_routes={
        'center':'potato-of-life/',
        'organism':'life-body/',
        'spirit':'potato-of-life/spirit/',
        'memory':'history/',
        'culture':'context/culture/',
        'research':'research-lab/'
    }
    if routes!=required_routes: errors.append('living project public routes drifted')
    for rel in required_routes.values():
        p=ROOT/rel/'index.html' if rel.endswith('/') else ROOT/rel
        if not p.is_file(): errors.append(f'living project public route missing: {rel}')


def validate_project_synthesis(errors):
    data=load(PROJECT_SYNTHESIS,errors)
    if not data: return
    waves=[x.get('id') for x in data.get('development_waves',[]) if isinstance(x,dict)]
    expected=['ownership-foundation','spatial-house','living-routes','comparative-expansion','center-refocus','reader-lenses','living-project','whole-project-lifecycle','symbol-depth-inhabitation','purpose-discovery','concrete-revelations','entity-crystallization','foundation-below-consolidation','public-home-convergence']
    if waves!=expected: errors.append('project synthesis development wave order drifted')
    rooms=[x.get('room_id') for x in data.get('room_pairings',[]) if isinstance(x,dict)]
    sub=load(SUBROOMS,errors)
    expected_rooms=[x.get('id') for x in sub.get('subrooms',[]) if isinstance(x,dict)]
    if set(rooms)!=set(expected_rooms): errors.append('project synthesis Room pairings must cover every nested Room')
    for row in data.get('room_pairings',[]):
        if not row.get('contribution'): errors.append(f'project synthesis Room missing contribution: {row.get("room_id")}')
        if not row.get('hands'): errors.append(f'project synthesis Room missing handoff: {row.get("room_id")}')
    scoped=data.get('scoped_centers',{})
    levels={x.get('id'):x for x in scoped.get('levels',[]) if isinstance(x,dict)}
    if levels.get('semantic-global',{}).get('center')!='potato-of-life': errors.append('scoped center semantic-global must remain Potato of Life')
    if levels.get('spatial-global',{}).get('center')!='axis': errors.append('scoped center spatial-global must remain Axis')
    p0=data.get('depth_program',{}).get('active_p0',[])
    required_p0=['door-liminality','spirit-relation','culture-formation-control','axis-local-centers','fruit-consequence','tree-branching']
    if p0!=required_p0: errors.append('project synthesis P0 depth programme drifted')
    hp=data.get('homepage_projection',{})
    teaching=[x.get('id') for x in hp.get('teaching_sequence',[]) if isinstance(x,dict)]
    expected_teaching=['whole','coordinates','planes','terrain-regime','living-systems','operators','inhabitants']
    if teaching!=expected_teaching: errors.append('homepage teaching sequence drifted')
    axis_teaching=hp.get('axis_teaching',{})
    if axis_teaching.get('invariant')!='Axis is the global orientation line, not the Tree, Ladder, Mountain or a truth hierarchy.':
        errors.append('homepage Axis teaching invariant drifted')
    movement=axis_teaching.get('movement_rule','')
    if 'Up/down direction alone does not determine value' not in movement:
        errors.append('homepage Axis movement rule must preserve non-moral direction')
    runtime=set(hp.get('runtime_sources',[]))
    for path in ('data/house/layer-terrain-regime-atlas.json','data/house/concept-topology.json','data/axis-flow-contract.json'):
        if path not in runtime: errors.append(f'homepage projection missing teaching runtime source: {path}')


def validate_depth_crystallization(errors):
    required_paths=[SHADOW_OVERLAY,GARDEN_REGIME,REPAIR_FORGE,FRUIT_ATLAS,TREE_BRANCHING,KNOWLEDGE_FORK,HISTORY_REVISION,WORKS_FRUIT,LOCAL_CENTERS]
    for p in required_paths:
        if not p.is_file(): errors.append(f'missing crystallized operator/contract: {p.relative_to(ROOT)}')
    synth=load(PROJECT_SYNTHESIS,errors)
    if not synth: return
    dp=synth.get('depth_program',{})
    p1=[x.get('id') for x in dp.get('completed_p1',[]) if isinstance(x,dict)]
    if p1!=['shadow-integration','providence-pillar-genealogy','selected-cosmographies']:
        errors.append('P1 depth completion set/order drifted')
    p2=[x.get('id') for x in dp.get('completed_p2',[]) if isinstance(x,dict)]
    expected_p2=['garden-regime-mechanics','history-canon-revision-protocol','works-fruit-instrumentation','local-center-interface-patterns','repair-forge-protocol','knowledge-fork-discernment']
    if p2!=expected_p2: errors.append('P2 depth completion set/order drifted')
    p3=dp.get('next_p3',[])
    if 'instrument-existing-works-with-fruit-contract' not in p3 or 'prune-or-merge-low-yield-duplicate-atlases' not in p3:
        errors.append('P3 must remain population/instrumentation focused')
    loop=synth.get('lifecycle_crystallization',{}).get('route',[])
    if loop!=['knowledge','discernment','door','tree/garden','fruit','history/revision','repair/forge','seed/return']:
        errors.append('crystallized lifecycle route drifted')

def main():
    errors=[]
    rooms=validate_rooms(errors)
    surfaces=validate_surfaces(errors,rooms)
    validate_specialist_subviews(errors,surfaces)
    validate_concept_topology(errors,rooms,surfaces)
    validate_project_center(errors)
    validate_symbolic_planes(errors,rooms)
    validate_orientation_population(errors,rooms)
    validate_tree_plane_routing(errors)
    validate_seed_spiral_routing(errors)
    validate_navigation_consolidation(errors)
    validate_providence_structure(errors)
    validate_layer_terrain_atlas(errors)
    validate_placement_matrix(errors)
    validate_project_synthesis(errors)
    validate_depth_crystallization(errors)
    if errors:
        print('POTATO HOUSE GOVERNANCE VALIDATION FAILED')
        [print('-',e) for e in errors]
        return 1
    print('POTATO HOUSE GOVERNANCE VALIDATION PASSED: project center, Rooms, topology, planes, routes, population and comparative layers converge')
    return 0

if __name__=='__main__': raise SystemExit(main())