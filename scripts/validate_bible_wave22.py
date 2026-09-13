#!/usr/bin/env python3
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOSSIERS = ROOT / 'knowledge' / 'traditions' / 'biblical-syncretism-dossiers-wave22.json'
FRAGMENTS = ROOT / 'knowledge' / 'traditions' / 'biblical-passage-fragments-wave22.json'
LOADER = ROOT / 'app' / 'bible-mining-wave19-loader.js'
BUILDER = ROOT / 'scripts' / 'build_bible_study.py'

REQUIRED = {
 'father-teaches-walk-hosea11',
 'eagle-carry-deut32',
 'living-way-hebrews10',
 'access-spirit-father-house-ephesians2',
 'sprout-builder-throne-zechariah6',
 'distributed-body-growth-ephesians4',
 'greatness-serves-matthew20-john13',
 'entrustment-responsibility-luke12',
 'kenosis-reversal-philippians2',
 'throne-participation-revelation3',
 'office-test-psalm82',
 'father-carries-deut1',
 'moses-burden-numbers11',
 'shared-spirit-burden-numbers11',
 'burden-mutual-own-galatians6',
 'living-stones-house-1peter2',
 'field-building-1cor3',
 'son-over-house-hebrews3',
 'source-mediation-1cor8',
 'kingdom-to-father-1cor15',
 'father-release-return-luke15',
 'shepherd-carry-feed-isaiah40-john21',
 'least-ones-judgment-matthew25',
 'discipline-fruit-hebrews12',
}

def main() -> int:
    errors=[]
    for p in (DOSSIERS,FRAGMENTS,LOADER,BUILDER):
        if not p.exists(): errors.append(f'missing {p.relative_to(ROOT)}')
    rows=[]; fragments=[]
    if DOSSIERS.exists():
        rows=json.loads(DOSSIERS.read_text(encoding='utf-8')).get('new_relations',[])
        ids={r.get('id') for r in rows}
        missing=sorted(REQUIRED-ids)
        if missing: errors.append('missing relation ids: '+', '.join(missing))
        if len(rows)<24: errors.append(f'expected >=24 relations, found {len(rows)}')
        if len(ids)!=len(rows): errors.append('duplicate relation ids')
        for r in rows:
            rid=r.get('id','<unknown>')
            if not r.get('project_anchor'): errors.append(f'{rid}: missing project_anchor')
            if not r.get('biblical_refs'): errors.append(f'{rid}: missing biblical_refs')
            if not (r.get('mismatch') or r.get('counter_text')): errors.append(f'{rid}: missing mismatch boundary')
            direction=r.get('source_direction') or (r.get('discovery_history') or {}).get('source_direction')
            if not direction: errors.append(f'{rid}: missing source direction')
            if r.get('dossier_level')=='A' and not (r.get('relation_argument') or {}).get('maximum_claim'):
                errors.append(f'{rid}: Level-A missing maximum_claim')
    if FRAGMENTS.exists():
        fragments=json.loads(FRAGMENTS.read_text(encoding='utf-8')).get('fragments',[])
        if len(fragments)<24: errors.append(f'expected >=24 fragments, found {len(fragments)}')
        matches={str(m) for f in fragments for m in f.get('matches',[])}
        for r in rows:
            for ref in r.get('biblical_refs',[]):
                if ref not in matches: errors.append(f"{r.get('id')}: no fragment for {ref}")
    loader=LOADER.read_text(encoding='utf-8') if LOADER.exists() else ''
    builder=BUILDER.read_text(encoding='utf-8') if BUILDER.exists() else ''
    for marker in ('biblical-syncretism-dossiers-wave22.json','biblical-passage-fragments-wave22.json'):
        if marker not in loader: errors.append('loader missing '+marker)
        if marker not in builder: errors.append('builder missing '+marker)
    if errors:
        print('BIBLE WAVE22 VALIDATION FAILED')
        for e in errors: print(' -',e)
        return 1
    print(f'BIBLE WAVE22 VALIDATION PASSED ({len(rows)} relations, {len(fragments)} fragments)')
    return 0

if __name__=='__main__': sys.exit(main())
