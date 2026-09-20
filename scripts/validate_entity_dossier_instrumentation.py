#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCHEMA=ROOT/'data/house/entity-dossier-schema.json'
DATA=ROOT/'data/house/entity-dossiers-wave-001.json'
HOUSE=ROOT/'house/index.html'
AUDIT=ROOT/'knowledge/research/element-materialization-audit-2026-09-18.json'

REQUIRED_INSTRUMENTS=(
    'scale_profile',
    'reproduction_and_correction',
    'visibility_and_access',
    'longitudinal_indicators',
)

def load(path:Path):
    return json.loads(path.read_text(encoding='utf-8'))

def main():
    errors=[]
    for path in (SCHEMA,DATA,HOUSE,AUDIT):
        if not path.is_file():
            errors.append(f'missing entity instrumentation artifact: {path.relative_to(ROOT)}')
    if errors:
        print('\n'.join(errors)); raise SystemExit(1)

    schema=load(SCHEMA)
    data=load(DATA)
    required=schema.get('required_sections',[])
    for key in REQUIRED_INSTRUMENTS:
        if key not in required:
            errors.append(f'entity schema missing required instrument: {key}')

    dossiers=data.get('dossiers',[])
    if len(dossiers)<4:
        errors.append('entity instrumentation wave must retain at least four real dossiers')

    for d in dossiers:
        did=d.get('id','?')
        source_ids={s.get('id') for s in d.get('sources',[]) if isinstance(s,dict)}
        for key in REQUIRED_INSTRUMENTS:
            if key not in d:
                errors.append(f'{did} missing {key}')
        scale=d.get('scale_profile',{})
        if not scale.get('operating_scale') or not scale.get('scope_boundary'):
            errors.append(f'{did} scale_profile must define operating scale and scope boundary')
        if not scale.get('key_dependencies'):
            errors.append(f'{did} scale_profile needs key dependencies')

        rc=d.get('reproduction_and_correction',{})
        for key in ('reproduction_mechanisms','correction_channels','observed_change'):
            if not rc.get(key):
                errors.append(f'{did} reproduction_and_correction missing {key}')

        va=d.get('visibility_and_access',{})
        for key in ('public_observability','restricted_or_confidential','structural_missingness','status_guard'):
            if not va.get(key):
                errors.append(f'{did} visibility_and_access missing {key}')

        longitudinal=d.get('longitudinal_indicators',[])
        if not longitudinal:
            errors.append(f'{did} needs at least one longitudinal indicator')
        for m in longitudinal:
            mid=m.get('id','?')
            observations=m.get('observations',[])
            if not observations:
                errors.append(f'{did}/{mid} missing observations')
            for obs in observations:
                sid=obs.get('source')
                if not sid or sid not in source_ids:
                    errors.append(f'{did}/{mid} observation references unknown source {sid!r}')
            if not m.get('limit'):
                errors.append(f'{did}/{mid} missing interpretation limit')
            reading=(m.get('reading') or '').lower()
            if any(term in reading for term in ('caused by','proves that','therefore caused')):
                errors.append(f'{did}/{mid} uses causal language in descriptive longitudinal reading')

    text=HOUSE.read_text(encoding='utf-8',errors='replace')
    for marker in ('Observed change over time','Reproduction & correction','Visibility & access','Scope boundary'):
        if marker not in text:
            errors.append(f'House entity-case UI missing instrumentation marker: {marker}')

    if errors:
        print('Entity dossier instrumentation validation failed:')
        for e in errors: print('-',e)
        raise SystemExit(1)
    print('Entity dossier instrumentation validation passed.')

if __name__=='__main__':
    main()
