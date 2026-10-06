#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from bible_excavation import DIMENSIONS, STATUSES

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'knowledge'/'indexes'/'bible-comparator-excavation.json'

def main()->int:
    errors=[]
    if not REPORT.exists():
        errors.append('missing knowledge/indexes/bible-comparator-excavation.json')
    else:
        data=json.loads(REPORT.read_text(encoding='utf-8'))
        if data.get('dimensions')!=DIMENSIONS:errors.append('dimension registry mismatch')
        if data.get('relation_count')!=len(data.get('relations',[])):errors.append('relation_count mismatch')
        seen=set()
        for relation in data.get('relations',[]):
            rid=relation.get('relation_id')
            if not rid:errors.append('relation without relation_id');continue
            if rid in seen:errors.append(f'duplicate relation {rid}')
            seen.add(rid)
            dims=relation.get('dimensions',{})
            if set(dims)!=set(DIMENSIONS):errors.append(f'{rid}: dimension set mismatch')
            for name,item in dims.items():
                status=item.get('status')
                if status not in STATUSES:errors.append(f'{rid}/{name}: invalid status {status!r}')
                if status in {'partial','missing','blocked_external'} and not item.get('next_action'):
                    errors.append(f'{rid}/{name}: incomplete status missing next_action')
            level=relation.get('level')
            if level not in range(6):errors.append(f'{rid}: invalid level {level!r}')
        for item in data.get('mine_next',[]):
            if item.get('relation_id') not in seen:errors.append(f"mine_next references unknown relation {item.get('relation_id')}")
    if errors:
        print('BIBLE COMPARATOR EXCAVATION VALIDATION FAILED')
        for error in errors:print(' -',error)
        return 1
    print('BIBLE COMPARATOR EXCAVATION VALIDATION PASSED')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
