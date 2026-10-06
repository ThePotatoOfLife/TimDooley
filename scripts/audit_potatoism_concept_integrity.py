#!/usr/bin/env python3
"""Audit Potatoism semantic identity, dossiers, aliases, projections and graph endpoints."""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'
REGISTRY=DATA/'potatoism-concept-registry.json'; DOSSIERS=DATA/'potatoism-dossiers.json'; CORPUS=DATA/'potatoism-canonical-corpus.json'; REL=DATA/'potatoism-relationships.json'
PROJECTIONS={DATA/'potatoism-lexicon.json',DATA/'potatoism-lexicon-expanded.json',DATA/'potatoism-cosmology.json',DATA/'potatoism-concept-map.json',DATA/'potatoism-relationships.json',DATA/'potatoism-timeline.json'}
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def norm(v):return re.sub(r'[^a-z0-9]+',' ',str(v).casefold()).strip()
def records(data):
    if isinstance(data,dict):
        for k in ('records','entries','concepts','terms','items'):
            if isinstance(data.get(k),list):yield from(x for x in data[k] if isinstance(x,dict));return
def main():
    errors=[];warnings=[];reg=load(REGISTRY);canonical={};aliases={}
    for c in reg.get('concepts',[]):
        cid=str(c.get('canonical_id','')).strip();term=str(c.get('term','')).strip()
        if not cid or not term:errors.append('registry concept missing canonical_id or term');continue
        if cid in canonical:errors.append(f'duplicate canonical_id: {cid}')
        canonical[cid]=c
        for a in c.get('aliases',[]):
            k=norm(a)
            if not k:continue
            if k in aliases and aliases[k]!=cid:errors.append(f'alias collision: {a!r} -> {aliases[k]} and {cid}')
            else:aliases[k]=cid
    # Exact canonical terms always outrank aliases. An alias matching a canonical term is therefore harmless.
    canonical_terms={norm(c.get('term','')):cid for cid,c in canonical.items() if c.get('term')}
    for k in list(aliases):
        if k in canonical_terms:del aliases[k]
    dossier=list(records(load(DOSSIERS)));dossier_by_id={};dossier_terms={}
    for x in dossier:
        rid=str(x.get('id','')).strip();term=str(x.get('term','')).strip()
        if rid:dossier_by_id.setdefault(rid,[]).append(x)
        if term:dossier_terms.setdefault(norm(term),[]).append(rid or '<missing-id>')
    missing=[]
    for cid in canonical:
        rows=dossier_by_id.get(cid,[])
        if not rows:missing.append(cid)
        elif len(rows)>1:errors.append(f'multiple dossier identities: {cid} ({len(rows)})')
        else:
            words=len(str(rows[0].get('long_form','')).split())
            if words<300:warnings.append(f'shallow dossier: {cid} ({words} words)')
    for term,ids in dossier_terms.items():
        if len(ids)>1:errors.append(f'duplicate dossier term: {term} -> {ids}')
    corpus=list(records(load(CORPUS)));corpus_ids=[str(x.get('id','')).strip() for x in corpus if str(x.get('id','')).strip()]
    if len(corpus_ids)!=len(set(corpus_ids)):warnings.append('canonical corpus contains repeated IDs; retain as source occurrences, never as duplicate concepts')
    for p in PROJECTIONS:
        if not p.exists():continue
        try:data=load(p)
        except Exception as e:errors.append(f'{p.relative_to(ROOT)} invalid JSON: {e}');continue
        # canonical_owner is legitimate projection metadata when it points to the registry.
        if isinstance(data,dict) and 'canonical_owner' in data:
            owner=str(data.get('canonical_owner','')).strip()
            if owner and owner!='data/potatoism-concept-registry.json':errors.append(f'projection has invalid canonical_owner: {p.relative_to(ROOT)} -> {owner}')
    if REL.exists():
        graph=load(REL);nodes={str(x) for x in graph.get('nodes',[])}
        for i,e in enumerate(graph.get('edges',[])):
            if not isinstance(e,dict):errors.append(f'relationship edge {i} is not an object');continue
            for endpoint in ('from','to'):
                value=str(e.get(endpoint,''));
                if not value:errors.append(f'relationship edge {i} missing {endpoint}')
                elif value not in nodes:errors.append(f'relationship edge {i} endpoint {endpoint}={value!r} missing from nodes')
                elif value in canonical:continue
                elif value not in {'potatoism','mountain'}:warnings.append(f'relationship endpoint {value!r} is not a registered canonical concept')
        unknown=nodes-set(canonical)-{'potatoism','mountain'}
        if unknown:warnings.append('relationship nodes without registry identity: '+', '.join(sorted(unknown)))
    if missing:warnings.append(f'missing dense dossiers: {len(missing)}; populate canonical concepts with real substance, never filler')
    print('POTATOISM CONCEPT INTEGRITY: FAIL' if errors else 'POTATOISM CONCEPT INTEGRITY: PASS')
    print(f'canonical concepts: {len(canonical)}; unique dossier identities: {len(dossier_by_id)}; corpus records: {len(set(corpus_ids))}; missing dossiers: {len(missing)}')
    if missing:print('DOSSIER TODOs:\n'+'\n'.join(f' - {x}' for x in missing))
    if warnings:
        print('WARNINGS:');[print(' -',x) for x in warnings]
    for x in errors:print('ERROR:',x)
    return 1 if errors else 0
if __name__=='__main__':raise SystemExit(main())
