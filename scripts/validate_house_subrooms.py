#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ROOMS=ROOT/'data/house/rooms.json'
SUBROOMS=ROOT/'data/house/subrooms.json'
SCHEMA=ROOT/'schemas/house-subroom-registry.schema.json'
TOPOLOGY=ROOT/'data/house/topology.json'
INTERFACES=ROOT/'data/house/interfaces.json'
VOCAB=ROOT/'data/house/architectural-vocabulary.json'
PROJECTIONS=ROOT/'data/house/projections.json'
STRUCTURAL_CENSUS=ROOT/'data/house/structural-census.json'
POPULATION=ROOT/'data/house/population-contract.json'
POPULATION_PULSE=ROOT/'data/house/population-pulse.json'
FEDERATION_SCALE=ROOT/'data/house/federation-scale.json'
HOLDINGS=ROOT/'data/house/holdings.json'
COLLECTIONS=ROOT/'data/house/collections.json'
DATA_HOLDINGS=ROOT/'data/house/data-holdings.json'
ROOM_DOSSIERS=ROOT/'data/house/room-dossiers.json'
SURFACES=ROOT/'data/house/public-surfaces.json'
ROOM_INTERIORS=ROOT/'data/house/room-interiors.json'

def load(path):
    return json.loads(path.read_text(encoding='utf-8'))

def main():
    errors=[]
    try:
        rooms=load(ROOMS); sub=load(SUBROOMS); topo=load(TOPOLOGY); interfaces=load(INTERFACES); vocab=load(VOCAB); projections=load(PROJECTIONS); census=load(STRUCTURAL_CENSUS); population=load(POPULATION); pulse=load(POPULATION_PULSE); federation=load(FEDERATION_SCALE); holdings=load(HOLDINGS); collections=load(COLLECTIONS); data_holdings=load(DATA_HOLDINGS); dossiers=load(ROOM_DOSSIERS); surfaces=load(SURFACES); schema=load(SCHEMA); interiors=load(ROOM_INTERIORS)
    except Exception as exc:
        print('HOUSE SUBROOM VALIDATION FAILED')
        print('-',exc)
        return 1

    parent_ids={x.get('id') for x in rooms.get('rooms',[]) if isinstance(x,dict)}
    rows=[x for x in sub.get('subrooms',[]) if isinstance(x,dict)]
    ids=[x.get('id') for x in rows]
    if len(ids)!=len(set(ids)): errors.append('duplicate nested Room IDs')
    if len(rows)<20: errors.append('nested Room registry is unexpectedly small')
    interior_rows=[x for x in interiors.get('interiors',[]) if isinstance(x,dict)]
    if len(interior_rows)!=len(rows): errors.append('Room interior registry must cover every nested Room')
    if {x.get('subroom_id') for x in interior_rows}!={x.get('id') for x in rows}: errors.append('Room interior registry IDs drifted')
    aliases=interiors.get('route_aliases',{})
    for interior in interior_rows:
        rid=interior.get('subroom_id')
        route=interior.get('route','')
        slug=route.strip('/').split('/')[-1] if route else ''
        if rid==slug:
            if interior.get('route_alias_status')=='intentional': errors.append(f'{rid} declares unnecessary route alias')
            continue
        alias=aliases.get(rid)
        if not isinstance(alias,dict): errors.append(f'{rid} public route differs from internal id without route_aliases contract')
        else:
            if alias.get('route')!=route or alias.get('route_slug')!=slug: errors.append(f'{rid} route alias contract drift')
            if interior.get('route_slug')!=slug or interior.get('route_alias_status')!='intentional': errors.append(f'{rid} interior alias metadata drift')
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
    if topo.get('interface_registry')!='data/house/interfaces.json': errors.append('House topology interface registry drift')
    if topo.get('architectural_vocabulary')!='data/house/architectural-vocabulary.json': errors.append('House topology architectural vocabulary drift')
    if topo.get('projection_registry')!='data/house/projections.json': errors.append('House topology projection registry drift')
    projection_ids=[x.get('id') for x in projections.get('projections',[]) if isinstance(x,dict)]
    if projection_ids!=['house-view','temple-view','body-view','tree-vine-view','city-view','plane-view']: errors.append(f'Integrated plurality projection set drifted: {projection_ids}')
    role_ids={x.get('id') for x in census.get('role_types',[]) if isinstance(x,dict)}
    required_roles={'house','dwelling','room','chamber','field','vineyard','road','path','view','court','table','bridge','gate','door','archive','treasury','foundation','pillar','protocol','state','projection','tabernacle','vessel','plane-section','rim','trajectory','spiral-field'}
    if role_ids!=required_roles: errors.append(f'House structural role set drifted: {sorted(role_ids)}')
    if census.get('chamber_status',{}).get('registered_count')!=0: errors.append('Chambers must remain reserved until an explicit Chamber registry is adopted')
    instance_ids=[x.get('id') for x in census.get('instances',[]) if isinstance(x,dict)]
    if len(instance_ids)!=len(set(instance_ids)): errors.append('duplicate House census instance IDs')
    for instance in census.get('instances',[]):
        for role in instance.get('roles',[]):
            if role not in role_ids: errors.append(f'House census instance {instance.get("id")} has unknown role {role}')
        for sid in instance.get('public_surfaces',[]):
            if sid not in surface_ids: errors.append(f'House census instance {instance.get("id")} has unknown public surface {sid}')
    if population.get('structural_census')!='data/house/structural-census.json': errors.append('House population contract census pointer drift')
    pulse_rows=[x for x in pulse.get('records',[]) if isinstance(x,dict)]
    holding_rows=[x for x in holdings.get('holdings',[]) if isinstance(x,dict)]
    if len(holding_rows)!=len(rows): errors.append('House holdings must cover every nested Room')
    if {x.get('room_id') for x in holding_rows}!={x.get('id') for x in rows}: errors.append('House holdings Room IDs drifted')
    assigned=[x for x in holdings.get('file_assignments',[]) if isinstance(x,dict)]
    assigned_paths=[x.get('path') for x in assigned]
    if len(assigned_paths)!=len(set(assigned_paths)): errors.append('A substantive file has more than one primary Room owner')
    if any(x.get('primary_file_count',0)<1 for x in holding_rows): errors.append('Every nested Room must have at least one primary holding')
    collection_ids=[x.get('id') for x in collections.get('collections',[]) if isinstance(x,dict)]
    if len(collection_ids)!=len(set(collection_ids)): errors.append('duplicate House collection IDs')
    bundle_rows=[x for x in data_holdings.get('bundles',[]) if isinstance(x,dict)]
    bundle_ids=[x.get('id') for x in bundle_rows]
    if len(bundle_ids)!=len(set(bundle_ids)): errors.append('duplicate House data bundle IDs')
    data_paths=[]
    for bundle in bundle_rows:
        if bundle.get('primary_room_id') not in {x.get('id') for x in rows}: errors.append(f'House data bundle has unknown primary Room: {bundle.get("id")}')
        data_paths.extend(bundle.get('source_files',[]))
    if len(data_paths)!=len(set(data_paths)): errors.append('A data file is assigned to more than one primary data bundle')
    dossier_rows=[x for x in dossiers.get('dossiers',[]) if isinstance(x,dict)]
    if len(dossier_rows)!=len(rows): errors.append('House Room dossiers must cover every nested Room')
    if {x.get('room_id') for x in dossier_rows}!={x.get('id') for x in rows}: errors.append('House Room dossier IDs drifted')
    hold_count={x.get('room_id'):x.get('primary_file_count',0) for x in holding_rows}
    for d in dossier_rows:
        if d.get('knowledge_holdings',{}).get('primary_file_count')!=hold_count.get(d.get('room_id')): errors.append(f'Room dossier holding count drift: {d.get("room_id")}')
        if not d.get('belongs_here'): errors.append(f'Room dossier missing belongs_here: {d.get("room_id")}')
        if not d.get('stays_out'): errors.append(f'Room dossier missing stays_out: {d.get("room_id")}')
        pairing=d.get('center_pairing',{})
        if not pairing.get('contribution'): errors.append(f'Room dossier missing center contribution: {d.get("room_id")}')
        if not pairing.get('center_nodes'): errors.append(f'Room dossier missing center nodes: {d.get("room_id")}')
        if not pairing.get('hands_to'): errors.append(f'Room dossier missing mature handoff: {d.get("room_id")}')
        local=d.get('local_center',{})
        if not local: errors.append(f'Room dossier missing local_center: {d.get("room_id")}')
        else:
            if local.get('scope_type')!='room' or local.get('scope_id')!=d.get('room_id'): errors.append(f'Room dossier local_center scope drift: {d.get("room_id")}')
            if local.get('parent_center')!='potato-of-life': errors.append(f'Room dossier local_center parent must remain Potato of Life: {d.get("room_id")}')
            if local.get('owner')!=d.get('room_id'): errors.append(f'Room dossier local_center owner drift: {d.get("room_id")}')
            if not local.get('exit_routes'): errors.append(f'Room dossier local_center missing exits: {d.get("room_id")}')
    if len(pulse_rows)!=len(rows): errors.append('House population pulse must cover every nested Room')
    if {x.get('room_id') for x in pulse_rows}!={x.get('id') for x in rows}: errors.append('House population pulse Room IDs drifted')
    federation_ids=[x.get('id') for x in federation.get('forms',[]) if isinstance(x,dict)]
    required_federation=['household','house','city','commons','network','assembly','kingdom-realm','civilization','garden-city']
    if federation_ids!=required_federation: errors.append(f'House federation-scale set drifted: {federation_ids}')
    if len(vocab.get('dwelling_projection',[]))!=10: errors.append('Architectural vocabulary must project exactly ten Dwellings')
    projected={x.get('canonical_room_id') for x in vocab.get('dwelling_projection',[]) if isinstance(x,dict)}
    if projected!=parent_ids: errors.append('Dwelling projection must cover exactly the ten canonical Rooms')
    interface_rows=[x for x in interfaces.get('interfaces',[]) if isinstance(x,dict)]
    interface_ids=[x.get('id') for x in interface_rows]
    if len(interface_ids)!=len(set(interface_ids)): errors.append('duplicate House interface IDs')
    for edge in interface_rows:
        if edge.get('from') not in set(ids) or edge.get('to') not in set(ids):
            errors.append(f'House interface has unknown nested Room endpoint: {edge.get("id")}')
        if not edge.get('preserves'): errors.append(f'House interface {edge.get("id")} must declare preserved invariants')
        if not edge.get('guard'): errors.append(f'House interface {edge.get("id")} must declare a guard')
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
