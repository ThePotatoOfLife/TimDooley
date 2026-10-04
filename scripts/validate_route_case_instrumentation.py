#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MATRIX=ROOT/'data/house/route-case-matrix.json'
SYNTH=ROOT/'data/house/project-synthesis.json'
AXIS=ROOT/'axis/index.html'

REQUIRED_CASE_FIELDS=(
    'starting_state','proposed_transition','operator','condition_required',
    'evidence_for_transition','counterevidence_or_falsifier','world_return_measure','status'
)

def load(path:Path):
    return json.loads(path.read_text(encoding='utf-8'))

def main():
    errors=[]
    for path in (MATRIX,SYNTH,AXIS):
        if not path.is_file():
            errors.append(f'missing route-instrumentation artifact: {path.relative_to(ROOT)}')
    if errors:
        print('\n'.join(errors)); raise SystemExit(1)

    matrix=load(MATRIX)
    synth=load(SYNTH)
    cases=matrix.get('cases',[])
    contrasts=matrix.get('mechanism_contrasts',[])

    ids=[x.get('id') for x in contrasts if isinstance(x,dict)]
    expected=['knowledge-fork','residue-fork','growth-fork','descent-fork']
    if ids!=expected:
        errors.append(f'route mechanism contrast order drifted: {ids!r}')

    for c in contrasts:
        if not c.get('starting_material'):
            errors.append(f"{c.get('id')} missing starting material")
        routes=c.get('routes',[])
        if len(routes)<2:
            errors.append(f"{c.get('id')} needs at least two contrasting routes")
        for r in routes:
            for key in ('route','operator','transition_test','failure_signs'):
                if not r.get(key):
                    errors.append(f"{c.get('id')}/{r.get('route','?')} missing {key}")

    if len(cases)<5:
        errors.append('route instrumentation wave must retain at least five cases')
    for c in cases:
        cid=c.get('id','?')
        for key in REQUIRED_CASE_FIELDS:
            if not c.get(key):
                errors.append(f'{cid} missing {key}')
        if c.get('subject_ref') and not c.get('source_ids'):
            errors.append(f'{cid} real-world subject_ref case needs source_ids')
        if not c.get('route_boundary'):
            errors.append(f'{cid} missing route boundary')
        if not c.get('counterevidence_or_falsifier'):
            errors.append(f'{cid} must name counterevidence or falsifier')
        if not c.get('world_return_measure'):
            errors.append(f'{cid} must name a World-level return measure')

    ri=synth.get('route_instrumentation',{})
    if ri.get('authority')!='data/house/route-case-matrix.json':
        errors.append('project synthesis missing route instrumentation authority')
    axis=AXIS.read_text(encoding='utf-8',errors='replace')
    for marker in (
        'route-case-matrix.json',
        'data-route-case',
        'routeCase',
    ):
        if marker not in axis:
            errors.append(f'Axis missing route-case instrumentation marker: {marker}')
    hp=synth.get('homepage_projection',{})
    retired=set(hp.get('runtime_input_contract',{}).get('retired_homepage_runtime_inputs',[]))
    if 'data/house/route-case-matrix.json' not in retired:
        errors.append('homepage contract must retire route-case matrix projection after moving route teaching to Axis')

    if errors:
        print('ROUTE CASE INSTRUMENTATION VALIDATION FAILED')
        for e in errors: print('-',e)
        raise SystemExit(1)
    print('ROUTE CASE INSTRUMENTATION VALIDATION PASSED')

if __name__=='__main__':
    main()
