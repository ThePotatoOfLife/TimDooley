#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
WAVE=ROOT/'data/house/foundations-wave-003.json'
PLACEMENT=ROOT/'data/house/foundation-placement-wave-003.json'
CONTRACT=ROOT/'data/house/foundation-axis-placement-contract.json'
TIMELINE=ROOT/'timeline/foundations/index.html'
SYNTH=ROOT/'data/house/project-synthesis.json'
LANDSCAPE=ROOT/'data/house/foundation-landscape-synthesis.json'

def load(p): return json.loads(p.read_text(encoding='utf-8'))

def main():
    errors=[]
    for p in (WAVE,PLACEMENT,CONTRACT,TIMELINE,SYNTH,LANDSCAPE):
        if not p.is_file(): errors.append(f'missing {p.relative_to(ROOT)}')
    if errors:
        print('\n'.join(errors)); raise SystemExit(1)

    wave=load(WAVE); placement=load(PLACEMENT); contract=load(CONTRACT); synth=load(SYNTH); landscape=load(LANDSCAPE)
    ids={x.get('id') for x in wave.get('records',[])}
    pids={x.get('foundation_id') for x in placement.get('records',[])}
    if ids!=pids:
        errors.append('Foundation wave 003 and placement population ids differ')

    allowed_dirs={'root-down','through-door','sprout-up','branch-out','return-down','ring','drain-down','repair-reversal','second-door'}
    allowed_planes={'below-plane','world-plane','heaven-plane','world-plane+heaven-plane'}
    for row in placement.get('records',[]):
        rid=row.get('foundation_id','?')
        if not row.get('primary_room'): errors.append(f'{rid} missing primary_room')
        if not row.get('current_status'): errors.append(f'{rid} missing current_status')
        if not row.get('field_projection'): errors.append(f'{rid} missing field_projection')
        for stage in row.get('field_projection',[]):
            if stage.get('direction') not in allowed_dirs: errors.append(f"{rid} invalid direction {stage.get('direction')}")
            if stage.get('plane') not in allowed_planes: errors.append(f"{rid} invalid plane {stage.get('plane')}")
        if row.get('route_condition')!='unresolved/mixed until episode-level consequence evidence is supplied':
            errors.append(f'{rid} route_condition must preserve evidence boundary')

    inv=contract.get('invariants',[])
    if 'Upper/lower location is orientation, not moral rank.' not in inv:
        errors.append('placement contract lost non-moral altitude invariant')
    if not any('Fear/love' in x for x in inv):
        errors.append('placement contract lost motive-lens boundary')

    if synth.get('foundation_seed_genealogy',{}).get('current_population')!=52:
        errors.append('project synthesis Foundation population must be 52')
    if landscape.get('population')!=52:
        errors.append('Foundation landscape population must be 52')
    archetypes=[x.get('id') for x in landscape.get('trajectory_archetypes',[]) if isinstance(x,dict)]
    expected_archetypes=['crisis-to-law','loss-to-portable-community','need-to-mutual-aid','experiment-to-method','fragmentation-to-standard','manifesto-to-movement','migration-to-community','venture-to-platform','inquiry-to-school']
    if archetypes!=expected_archetypes:
        errors.append('Foundation landscape trajectory archetypes drifted')

    text=TIMELINE.read_text(encoding='utf-8',errors='replace')
    for marker in ('foundation-placement-wave-003.json','stage-path','status-chip'):
        if marker not in text: errors.append(f'Foundation Timeline missing placement marker: {marker}')

    if errors:
        print('FOUNDATION AXIS PLACEMENT VALIDATION FAILED')
        for e in errors: print('-',e)
        raise SystemExit(1)
    print('FOUNDATION AXIS PLACEMENT VALIDATION PASSED')

if __name__=='__main__': main()
