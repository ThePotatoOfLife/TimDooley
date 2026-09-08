#!/usr/bin/env python3
"""Fail closed when Potatoism creates duplicate semantic identities or shallow filler.

Occurrences in source files are legitimate. Duplicate canonical concepts are not.
Every registered concept must have exactly one dossier identity; projections may point
to it but may not silently become another definition owner.
"""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'
REGISTRY=DATA/'potatoism-concept-registry.json'; DOSSIERS=DATA/'potatoism-dossiers.json'; CORPUS=DATA/'potatoism-canonical-corpus.json'
PROJECTIONS={DATA/'potatoism-lexicon.json',DATA/'potatoism-lexicon-expanded.json',DATA/'potatoism-cosmology.json',DATA/'potatoism-concept-map.json',DATA/'potatoism-relationships.json',DATA/'potatoism-timeline.json'}
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def norm(v):return re.sub(r'[^a-z0-9]+',' ',str(v).casefold()).strip()
def records(data):
    if isinstance(data,dict):
        for k in ('records','entries','concepts','terms','items'):
            if isinstance(data.get(k),list):
                yield from (x for x in data[k] if isinstance(x,dict));return
def main():
    errors=[]; warnings=[]; reg=load(REGISTRY); canonical={}; aliases={}
    for c in reg.get('concepts',[]):
        cid=str(c.get('canonical_id','')).strip(); term=str(c.get('term','')).strip()
        if not cid or not term:errors.append('registry concept missing canonical_id or term');continue
        if cid in canonical:errors.append(f'duplicate canonical_id: {cid}')
        canonical[cid]=c
        for a in [term,*c.get('aliases',[])]:
            k=norm(a)
            if not k:continue
            if k in aliases and aliases[k]!=cid:errors.append(f'alias collision: {a!r} -> {aliases[k]} and {cid}')
            else:aliases[k]=cid
    dossier=list(records(load(DOSSIERS))); dossier_by_id={}; dossier_terms={}
    for x in dossier:
        rid=str(x.get('id','')).strip(); term=str(x.get('term','')).strip()
        if rid:dossier_by_id.setdefault(rid,[]).append(x)
        if term:dossier_terms.setdefault(norm(term),[]).append(rid or '<missing-id>')
    for cid in canonical:
        rows=dossier_by_id.get(cid,[])
        if not rows:errors.append(f'missing canonical dossier: {cid}')
        elif len(rows)>1:errors.append(f'multiple dossier identities: {cid} ({len(rows)})')
        else:
            x=rows[0]; prose=str(x.get('long_form','')).strip()
            if len(prose.split())<300:errors.append(f'shallow dossier: {cid} ({len(prose.split())} words)')
    for term,ids in dossier_terms.items():
        if len(ids)>1:errors.append(f'duplicate dossier term: {term} -> {ids}')
    corpus=list(records(load(CORPUS))); corpus_ids=[str(x.get('id','')).strip() for x in corpus if str(x.get('id','')).strip()]
    if len(corpus_ids)!=len(set(corpus_ids)):warnings.append('canonical corpus contains repeated IDs; these are source-canon occurrences and must not be presented as separate concepts')
    # Projection definitions are allowed as historical/source occurrences, but explicit
    # owner declarations are forbidden. Repeated term labels are warnings, not failures.
    projection_term_hits={}
    for p in PROJECTIONS:
        if not p.exists():continue
        try:data=load(p)
        except Exception as e:errors.append(f'{p.relative_to(ROOT)} invalid JSON: {e}');continue
        if 'canonical_owner' in json.dumps(data,ensure_ascii=False):errors.append(f'projection declares canonical_owner: {p.relative_to(ROOT)}')
        for x in records(data):
            t=norm(x.get('term') or x.get('name') or '')
            if t in aliases:projection_term_hits.setdefault(aliases[t],set()).add(p.relative_to(ROOT).as_posix())
    if projection_term_hits:warnings.append(f'canonical concepts occur in {sum(len(v) for v in projection_term_hits.values())} projection-file relationships; these are retained as provenance, not identities')
    print('POTATOISM CONCEPT INTEGRITY: FAIL' if errors else 'POTATOISM CONCEPT INTEGRITY: PASS')
    print(f'canonical concepts: {len(canonical)}; unique dossier identities: {len(dossier_by_id)}; corpus records: {len(set(corpus_ids))}')
    if warnings:
        print('WARNINGS:')
        for x in warnings:print(' -',x)
    for x in errors:print('ERROR:',x)
    return 1 if errors else 0
if __name__=='__main__':raise SystemExit(main())
