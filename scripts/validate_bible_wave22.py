#!/usr/bin/env python3
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TRAD=ROOT/'knowledge'/'traditions'
LOADER=ROOT/'app'/'bible-mining-wave19-loader.js'
BUILDER=ROOT/'scripts'/'build_bible_study.py'
FRAGMENTS=TRAD/'biblical-passage-fragments-wave22.json'
REQUIRED={
'father-teaches-walk-hosea11','eagle-carry-deut32','living-way-hebrews10',
'access-spirit-father-house-ephesians2','sprout-builder-throne-zechariah6',
'distributed-body-growth-ephesians4','greatness-serves-matthew20-john13',
'entrustment-responsibility-luke12','many-members-one-body-1cor12',
'living-stones-house-1peter2','equip-others-build-body-eph4'}

def main()->int:
    errors=[]
    packs=sorted(TRAD.glob('biblical-operator-comparisons-wave22-*.json'))
    rows=[]
    for path in packs:
        rows.extend(json.loads(path.read_text(encoding='utf-8')).get('new_relations',[]))
    ids=[row.get('id') for row in rows]
    if len(packs)<7: errors.append(f'expected >=7 wave22 packs, found {len(packs)}')
    if len(rows)<11: errors.append(f'expected >=11 wave22 relations, found {len(rows)}')
    if len(ids)!=len(set(ids)): errors.append('duplicate wave22 relation ids')
    missing=sorted(REQUIRED-set(ids))
    if missing: errors.append('missing relations: '+', '.join(missing))
    for row in rows:
        rid=row.get('id','<unknown>')
        for key in ('project_anchor','biblical_refs','source_direction','mismatch'):
            if not row.get(key): errors.append(f'{rid}: missing {key}')
        if row.get('dossier_level')=='A' and not (row.get('relation_argument') or {}).get('maximum_claim'):
            errors.append(f'{rid}: Level-A relation missing maximum_claim')
    if not FRAGMENTS.exists():
        errors.append('missing biblical-passage-fragments-wave22.json')
        matches=set()
    else:
        data=json.loads(FRAGMENTS.read_text(encoding='utf-8'))
        matches={str(m) for fragment in data.get('fragments',[]) for m in fragment.get('matches',[])}
    for row in rows:
        for ref in row.get('biblical_refs',[]):
            if ref not in matches: errors.append(f'{row.get("id")}: no passage fragment for {ref}')
    loader=LOADER.read_text(encoding='utf-8') if LOADER.exists() else ''
    builder=BUILDER.read_text(encoding='utf-8') if BUILDER.exists() else ''
    if 'biblical-operator-comparisons-wave22-' not in loader: errors.append('dynamic Bible loader does not route wave22 packs')
    if 'biblical-operator-comparisons-wave22-' not in builder: errors.append('static Bible builder does not route wave22 packs')
    if 'biblical-passage-fragments-wave22.json' not in loader: errors.append('dynamic Bible loader does not route wave22 fragments')
    if 'biblical-passage-fragments-wave22.json' not in builder: errors.append('static Bible builder does not route wave22 fragments')
    if errors:
        print('BIBLE WAVE22 VALIDATION FAILED')
        for error in errors: print(' -',error)
        return 1
    print(f'BIBLE WAVE22 VALIDATION PASSED ({len(rows)} relations in {len(packs)} packs)')
    return 0

if __name__=='__main__': sys.exit(main())
