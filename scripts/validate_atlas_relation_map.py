#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TYPES=ROOT/'data/atlas-relation-types.json'
MAP=ROOT/'data/atlas-relation-map.json'


def main()->int:
    types_doc=json.loads(TYPES.read_text(encoding='utf-8'))
    map_doc=json.loads(MAP.read_text(encoding='utf-8'))
    valid={str(row.get('id')) for row in types_doc.get('types',[]) if isinstance(row,dict) and row.get('id')}
    rows=map_doc.get('mappings',[])
    if not isinstance(rows,list):raise SystemExit('ATLAS RELATION MAP FAILED: mappings must be a list')
    raw=[]
    for row in rows:
        if not isinstance(row,dict):raise SystemExit('ATLAS RELATION MAP FAILED: row must be object')
        label=str(row.get('raw','')).strip();raw.append(label)
        canonical=str(row.get('canonical','')).strip()
        if not label:raise SystemExit('ATLAS RELATION MAP FAILED: empty raw label')
        if canonical not in valid:raise SystemExit(f'ATLAS RELATION MAP FAILED: unknown type {label}->{canonical}')
        if not str(row.get('reason','')).strip():raise SystemExit(f'ATLAS RELATION MAP FAILED: missing reason {label}')
    if len(raw)!=len(set(raw)):raise SystemExit('ATLAS RELATION MAP FAILED: duplicate raw mapping')
    print(f'ATLAS RELATION MAP PASSED: {len(rows)} deliberate mappings')
    return 0

if __name__=='__main__':raise SystemExit(main())
