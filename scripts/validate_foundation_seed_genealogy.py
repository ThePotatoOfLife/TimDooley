#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GEN=ROOT/'data/house/foundation-door-seed-genealogy.json'
F1=ROOT/'data/house/foundations-wave-001.json'
F2=ROOT/'data/house/foundations-wave-002.json'
SYNTH=ROOT/'data/house/project-synthesis.json'
PAGE=ROOT/'timeline/foundations/index.html'

def load(p): return json.loads(p.read_text(encoding='utf-8'))

def main():
    errors=[]
    for p in (GEN,F1,F2,SYNTH,PAGE):
        if not p.is_file(): errors.append(f'missing {p.relative_to(ROOT)}')
    if errors:
        print('\n'.join(errors)); raise SystemExit(1)
    gen=load(GEN); f1=load(F1); f2=load(F2); synth=load(SYNTH)
    source_ids={x.get('id') for x in [*(f1.get('records') or []),*(f2.get('records') or [])]}
    rows=gen.get('records') or []
    if len(rows)!=len(source_ids):
        errors.append(f'genealogy population {len(rows)} != Foundation population {len(source_ids)}')
    ids={x.get('foundation_id') for x in rows}
    if ids!=source_ids:
        errors.append('Foundation Seed genealogy ids drift from Foundation registries')

    allowed_place_precision={'building','site','building+city','site+city','district+city','neighborhood+city','city','city+region','city+distributed','city-to-city','locality','region','country','country+virtual','distributed','distributed+state','distributed+site region','distributed-network','institution+city','multi-city','multi-city/imperial','multi-region','region+city','region+cities','route+cities','site+city','state','state+virtual','virtual','multi-city/imperial','multi-region','city+jurisdiction','country/distributed','institution+city','city+transnational','region+traditional-site','distributed+state','city-area'}
    for row in rows:
        rid=row.get('foundation_id','?')
        for key in ('seed_of_death','door_crossing','seed_of_life','foundation_rise','fall_return_refoundation'):
            if not row.get(key): errors.append(f'{rid} missing {key}')
        places=row.get('emergence_places') or []
        if not places: errors.append(f'{rid} has no emergence places')
        for p in places:
            if not p.get('clock') or not p.get('place') or not p.get('precision') or not p.get('status'):
                errors.append(f'{rid} has incomplete place record')
        if not row.get('evidence_boundary'):
            errors.append(f'{rid} missing evidence boundary')
        if not row.get('foundation_rise',{}).get('reproduction_basis'):
            errors.append(f'{rid} missing reproduction basis')

    fs=synth.get('foundation_seed_genealogy',{})
    if fs.get('authority')!='data/house/foundation-door-seed-genealogy.json':
        errors.append('project synthesis missing Foundation Seed genealogy authority')
    if fs.get('current_population')!=len(rows):
        errors.append('project synthesis Foundation Seed population drifted')

    text=PAGE.read_text(encoding='utf-8',errors='replace')
    for marker in ('Seeds through the Door','foundationSeedGrid',"foundation-door-seed-genealogy.json",'Seed of Death','Seed of Life','Door crossing'):
        if marker not in text: errors.append(f'Foundation Timeline missing marker: {marker}')

    if errors:
        print('FOUNDATION SEED GENEALOGY VALIDATION FAILED')
        for e in errors: print('-',e)
        raise SystemExit(1)
    print('FOUNDATION SEED GENEALOGY VALIDATION PASSED')

if __name__=='__main__': main()
