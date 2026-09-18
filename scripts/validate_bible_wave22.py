#!/usr/bin/env python3
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TRAD=ROOT/'knowledge'/'traditions'
MANIFEST=TRAD/'bible-layer-manifest.json'
BUILDER=ROOT/'scripts'/'build_bible_study.py'
FRAGMENTS=TRAD/'biblical-passage-fragments-wave22.json'
REQUIRED={
'father-teaches-walk-hosea11','eagle-carry-deut32','living-way-hebrews10',
'access-spirit-father-house-ephesians2','sprout-builder-throne-zechariah6',
'distributed-body-growth-ephesians4','greatness-serves-matthew20-john13',
'entrustment-responsibility-luke12','many-members-one-body-1cor12',
'living-stones-house-1peter2','equip-others-build-body-eph4',
'patient-gardener-luke13','house-does-not-contain-source-1kings8',
'presence-beyond-temple-acts17','ordinary-carrier-burning-bush-exodus3',
'adoption-spirit-father-romans8','shepherd-carry-feed-isaiah40',
'least-ones-judgment-matthew25','formation-fruit-hebrews12',
'new-wine-new-container-mark2','partial-view-exodus33',
'mirror-partial-knowledge-1cor13'}

def main()->int:
    errors=[]
    packs=sorted(TRAD.glob('biblical-operator-comparisons-wave22-*.json'))
    rows=[]
    for path in packs:
        rows.extend(json.loads(path.read_text(encoding='utf-8')).get('new_relations',[]))
    ids=[row.get('id') for row in rows]
    if len(packs)<18: errors.append(f'expected >=18 wave22 packs, found {len(packs)}')
    if len(rows)<22: errors.append(f'expected >=22 wave22 relations, found {len(rows)}')
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
    builder=BUILDER.read_text(encoding='utf-8') if BUILDER.exists() else ''
    if not MANIFEST.exists():
        errors.append('missing canonical Bible layer manifest')
    else:
        manifest=json.loads(MANIFEST.read_text(encoding='utf-8'))
        active_paths={
            item.get('path') for item in manifest.get('layers',[])
            if item.get('status') in {'canonical','additive'}
        }
        for path in packs:
            expected='knowledge/traditions/'+path.name
            if expected not in active_paths: errors.append(f'Bible manifest missing {path.name}')
        if 'knowledge/traditions/biblical-passage-fragments-wave22.json' not in active_paths:
            errors.append('Bible manifest does not route wave22 fragments')
    if 'assemble_relations' not in builder or 'load_manifest' not in builder:
        errors.append('static Bible builder must consume the manifest-defined corpus')
    if errors:
        print('BIBLE WAVE22 VALIDATION FAILED')
        for error in errors: print(' -',error)
        return 1
    print(f'BIBLE WAVE22 VALIDATION PASSED ({len(rows)} relations in {len(packs)} packs)')
    return 0

if __name__=='__main__': sys.exit(main())
