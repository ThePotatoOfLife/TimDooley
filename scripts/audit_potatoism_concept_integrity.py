#!/usr/bin/env python3
"""Audit Potatoism identity ownership.

Many files may contain occurrences for provenance, but only one canonical identity
and one dense dossier may exist for each concept. Missing dossiers are reported as
TODOs while identity collisions fail the build.
"""
from __future__ import annotations
import json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'
REGISTRY=DATA/'potatoism-concept-registry.json'; DOSSIERS=DATA/'potatoism-dossiers.json'; CORPUS=DATA/'potatoism-canonical-corpus.json'
PROJECTIONS={DATA/'potatoism-lexicon.json',DATA/'potatoism-lexicon-expanded.json',DATA/'potatoism-cosmology.json',DATA/'potatoism-concept-map.json',DATA/'potatoism-relationships.json',DATA/'potatoism-timeline.json'}
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def norm(v): return re.sub(r'[^a-z0-9]+',' ',str(v).casefold()).strip()
def records(data):
    if isinstance(data,dict):
        for k in ('records','entries','concepts','terms','items'):
            if isinstance(data.get(k),list):
                yield from (x for x in data[k] if isinstance(x,dict)); return
def main():
    errors=[]; todos=[]; reg=load(REGISTRY); canonical={}; owners={}
    for c in reg.get('concepts',[]):
        cid=str(c.get('canonical_id','')).strip(); term=str(c.get('term','')).strip()
        if not cid or not term: errors.append('registry concept missing canonical_id or term'); continue
        if cid in canonical: errors.append(f'duplicate canonical_id: {cid}')
        canonical[cid]=c
        # Only true identity aliases belong here. Contextual/symbolic relationships belong in relations.
        for a in [term,*c.get('aliases',[])]:
            key=norm(a)
            if not key: continue
            if key in owners and owners[key]!=cid: errors.append(f'alias collision: {a!r} -> {owners[key]} and {cid}')
            else: owners[key]=cid
    dossier_ids=[str(x.get('id','')).strip() for x in records(load(DOSSIERS)) if str(x.get('id','')).strip()]
    if len(dossier_ids)!=len(set(dossier_ids)): errors.append('potatoism-dossiers.json contains duplicate canonical IDs')
    corpus_ids=[str(x.get('id','')).strip() for x in records(load(CORPUS)) if str(x.get('id','')).strip()]
    if len(corpus_ids)!=len(set(corpus_ids)): errors.append('potatoism-canonical-corpus.json contains duplicate IDs')
    for cid in canonical:
        if cid not in dossier_ids: todos.append(f'missing dense dossier: {cid}')
    for p in PROJECTIONS:
        if not p.exists(): continue
        try: data=load(p)
        except Exception as e: errors.append(f'{p.relative_to(ROOT)} invalid JSON: {e}'); continue
        if '"canonical_owner"' in json.dumps(data,ensure_ascii=False): errors.append(f'projection declares canonical_owner: {p.relative_to(ROOT)}')
    print('POTATOISM CONCEPT INTEGRITY: FAIL' if errors else 'POTATOISM CONCEPT INTEGRITY: PASS')
    print(f'canonical concepts: {len(canonical)}; dense dossiers: {len(set(dossier_ids))}; corpus records: {len(set(corpus_ids))}')
    if todos:
        print('DOSSIER TODOs:')
        for x in todos: print(' -',x)
    for x in errors: print('ERROR:',x)
    return 1 if errors else 0
if __name__=='__main__': raise SystemExit(main())
