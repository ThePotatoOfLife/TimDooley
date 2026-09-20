#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ATLAS=ROOT/'data/house/foundation-room-atlas.json'
CONTRACT=ROOT/'data/house/foundation-room-contract.json'
SYNTH=ROOT/'data/house/project-synthesis.json'
REPRO=ROOT/'data/house/foundation-first-reproduction-wave-001.json'
HOME=ROOT/'index.html'
TIMELINE=ROOT/'timeline/foundations/index.html'
HOUSE=ROOT/'house/index.html'

def load(p): return json.loads(p.read_text(encoding='utf-8'))

def main():
    errors=[]
    for p in (ATLAS,CONTRACT,SYNTH,REPRO,HOME,TIMELINE,HOUSE):
        if not p.is_file(): errors.append(f'missing {p.relative_to(ROOT)}')
    if errors:
        print('\n'.join(errors)); raise SystemExit(1)

    atlas=load(ATLAS); contract=load(CONTRACT); synth=load(SYNTH); repro=load(REPRO)
    rows=atlas.get('rooms') or []
    if atlas.get('population')!=52 or len(rows)!=52:
        errors.append(f'Foundation Room population must be 52, got atlas={atlas.get("population")} rows={len(rows)}')

    ids=set()
    for row in rows:
        rid=row.get('foundation_id','?')
        if rid in ids: errors.append(f'duplicate Foundation Room {rid}')
        ids.add(rid)
        for face in ('origin_door','house_location','today','genealogy'):
            if not row.get(face): errors.append(f'{rid} missing {face}')
        origin=row.get('origin_door',{})
        if not origin.get('time'): errors.append(f'{rid} missing origin Door time')
        if not origin.get('physical_origin'): errors.append(f'{rid} missing origin physical/distributed place')
        if origin.get('map_ready') and not origin.get('geocode_query'):
            errors.append(f'{rid} map-ready origin missing geocode_query')
        if origin.get('map_geometry') in ('distributed-network','virtual') and origin.get('map_ready'):
            errors.append(f'{rid} distributed/virtual origin cannot be point map-ready')

        house=row.get('house_location',{})
        if not house.get('primary_room'): errors.append(f'{rid} missing primary Room owner')
        if not house.get('circle_anchor',{}).get('id'): errors.append(f'{rid} missing circle anchor')
        if house.get('primary_room')=='house-architecture' and row.get('domain')!='project-canon':
            errors.append(f'{rid} unresolved substantive Room owner fell back to House Architecture')

        today=row.get('today',{})
        if not today.get('as_of'): errors.append(f'{rid} missing Today as_of')
        for m in today.get('typed_reach') or []:
            for key in ('measure','value','unit','as_of','source_title','source_url'):
                if m.get(key) in (None,''): errors.append(f'{rid} current metric missing {key}')
        if 'score' in row.get('magnitude_facets',{}):
            errors.append(f'{rid} must not carry a universal magnitude score')

        first=row.get('first_reproduction',{})
        if not first or not first.get('evidence'):
            errors.append(f'{rid} missing first reproduction evidence/gap state')
        elif not first.get('evidence',{}).get('evidence_type'):
            errors.append(f'{rid} first reproduction missing evidence_type')

        status=row.get('room_status',{})
        for checkpoint in ('origin','reproduction','today','geography'):
            if not status.get(checkpoint,{}).get('state'):
                errors.append(f'{rid} room_status checkpoint missing: {checkpoint}')
        if not isinstance(row.get('door_history'),list) or not row.get('door_history'):
            errors.append(f'{rid} missing Door history')
        if 'completeness_score' in row or 'completion_score' in row:
            errors.append(f'{rid} must not collapse Room status into one completeness score')

        gene=row.get('genealogy',{})
        if not gene.get('technical_owner'): errors.append(f'{rid} genealogy missing technical owner')

    summary=atlas.get('summary',{})
    if summary.get('total_rooms')!=52:
        errors.append('Foundation Room summary total drifted')
    if summary.get('unresolved_owner_count')!=0:
        errors.append('Foundation Room atlas has unresolved Room ownership')
    geometry_counts={}
    for row in rows:
        k=row.get('origin_door',{}).get('map_geometry') or 'unresolved'
        geometry_counts[k]=geometry_counts.get(k,0)+1
    if summary.get('earth_geometry_counts')!=geometry_counts:
        errors.append('Foundation Room earth geometry summary drifted')
    calculated_quant=sum(1 for x in rows if x.get('today',{}).get('typed_reach'))
    if summary.get('current_quantitative_snapshots')!=calculated_quant:
        errors.append('Foundation Room quantified Today count drifted')
    calculated_metrics=sum(len(x.get('today',{}).get('typed_reach') or []) for x in rows)
    if summary.get('current_metric_count')!=calculated_metrics:
        errors.append('Foundation Room current metric count drifted')
    if len(repro.get('records') or [])!=52:
        errors.append('Foundation reproduction ledger must cover all 52 Rooms')
    if {x.get('foundation_id') for x in repro.get('records',[])}!={x.get('foundation_id') for x in rows}:
        errors.append('Foundation Room and reproduction-ledger populations differ')

    if 'typed_current_reach' not in contract.get('magnitude_facets',[]):
        errors.append('Foundation Room contract lost typed reach magnitude')
    if 'Do not rank unlike reach measures.' not in contract.get('anti_drift',[]):
        errors.append('Foundation Room contract lost anti-ranking rule')

    fr=synth.get('foundation_rooms',{})
    if fr.get('authority')!='data/house/foundation-room-atlas.json':
        errors.append('project synthesis missing Foundation Room authority')
    if fr.get('population')!=52:
        errors.append('project synthesis Foundation Room population drifted')

    home=HOME.read_text(encoding='utf-8',errors='replace')
    for marker in ('id="foundation-rooms"',"fetch('data/house/foundation-room-atlas.json')",'Door · Place · House · Today','Foundation Rooms'):
        if marker not in home: errors.append(f'Home missing Foundation Room marker: {marker}')

    timeline=TIMELINE.read_text(encoding='utf-8',errors='replace')
    for marker in ('id="foundation-rooms"',"foundation-room-atlas.json",'foundationRoomCatalog','Map-ready origin','Quantified Today'):
        if marker not in timeline: errors.append(f'Foundation Timeline missing Room marker: {marker}')

    house=HOUSE.read_text(encoding='utf-8',errors='replace')
    if "foundations-wave-003.json" not in house:
        errors.append('House reader is not loading Foundation wave 003')

    if errors:
        print('FOUNDATION ROOM VALIDATION FAILED')
        for e in errors: print('-',e)
        raise SystemExit(1)
    print('FOUNDATION ROOM VALIDATION PASSED')

if __name__=='__main__': main()
