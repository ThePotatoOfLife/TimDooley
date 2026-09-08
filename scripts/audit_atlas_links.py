#!/usr/bin/env python3
"""Verify Atlas targets against the records that can actually resolve at runtime."""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def load(path):
    with (ROOT/path).open(encoding='utf-8') as f:return json.load(f)
def ids_from(path, keys=('records','entries','nodes','events','sector_families','scale','people','levels')):
    try:data=load(path)
    except FileNotFoundError:return set()
    out=set()
    def walk(v):
        if isinstance(v,dict):
            if isinstance(v.get('id'),str) and v['id']:out.add(v['id'])
            for x in v.values():walk(x)
        elif isinstance(v,list):
            for x in v:walk(x)
    for key in keys:
        if key in data:walk(data[key])
    return out

def lexicon_ids(path):
    try:data=load(path)
    except FileNotFoundError:return set()
    out=set()
    for x in data.get('entries',[]):
        if isinstance(x,dict):
            if x.get('id'):out.add(str(x['id']))
            if x.get('term'):
                s=re.sub(r'[^a-z0-9]+','-',str(x['term']).lower()).strip('-')
                out.add(s)
        elif isinstance(x,list) and x:
            out.add(str(x[0]))
    return out

all_records=set()
for path in [
 'data/nodes.json','data/tree-child-records.json','data/tree-support-records.json','data/tree-concept-records.json',
 'data/graph-registry.json','data/belief-records.json','data/belief-registry.json','data/potatoism-cosmology.json',
 'data/potatoism-glossary.json','data/potatoism-canonical-corpus.json','data/potatoism-deep-layers.json','data/potatoism-timeline.json',
 'data/tree.json','data/domain-coupling.json','data/global-graph-bridge.json','data/people-registry.json','data/indicator-catalog.json',
 'data/research.json','data/research-carvings-2026-09.json','data/full-text-coverage.json','data/canonical-texts.json',
 'data/religious-comparative-library.json','data/religious-foundations.json','data/religious-foundations/records.json',
 'data/religious-adjacent/records.json','data/religious-adjacent/deep-expansions.json','data/religious-adjacent/deep-expansions-2.json',
 'data/religious-adjacent/deep-expansions-3.json','data/geometry-records.json','data/events.json','data/european-sector-atlas.json',
]:all_records |= ids_from(path)
all_records |= lexicon_ids('data/political-lexicon.json') | lexicon_ids('data/religious-lexicon.json') | lexicon_ids('data/potatoism-lexicon.json')
all_records |= {x.get('id') for x in load('data/nations.json').get('nations',[]) if x.get('id')}
hawkins={f"hawkins-{x.get('level')}" for x in load('data/hawkins-scale.json').get('scale',[]) if x.get('level') is not None}
all_records |= hawkins
rels=load('data/relationships.json').get('relationships',[])
endpoints={r.get(side) for r in rels for side in ('source','target') if r.get(side)}
phantom=sorted(endpoints-all_records)
# Runtime repository routes: nation IDs are intentionally handled by nation.html; everything else in the
# repository leaf resolver goes through node.html, with geometry having its dedicated route.
htmls=list(ROOT.glob('*.html'))
route_refs=set()
for p in htmls:
    text=p.read_text(encoding='utf-8',errors='replace')
    for m in re.finditer(r'(?:node|nation|geometry)\.html\?id=([^"`&\s<>]+)',text):
        route_refs.add(m.group(1))
# Tree references must resolve to a real record, not merely to an endpoint mentioned in relationships.
tree=load('data/tree.json');tree_refs=set()
for level in tree.get('levels',[]):
    if level.get('id'):tree_refs.add(level['id'])
    tree_refs.update(x for x in level.get('children',[]) if x)
tree_missing=sorted(tree_refs-all_records)
errors=[]
if len(load('data/nations.json').get('nations',[]))!=195:errors.append('expected 195 nations')
if phantom:errors.append('phantom relationship endpoints: '+', '.join(phantom))
if tree_missing:errors.append('unresolved tree references: '+', '.join(tree_missing))
for ref in sorted(route_refs):
    # Strip common URL encoding only for diagnostics; static literal refs are checked against IDs.
    raw=ref
    if raw not in all_records and raw not in {str(x).lower() for x in all_records}:
        errors.append('static route references unknown ID: '+raw)
print(f'Canonical record IDs: {len(all_records)}')
print(f'Relationship endpoints: {len(endpoints)}')
print(f'Phantom relationship endpoints: {len(phantom)}')
print(f'Static route references: {len(route_refs)}')
print(f'Tree references: {len(tree_refs)}')
if errors:
    print('\nATLAS LINK AUDIT FAILED')
    for e in errors:print('- '+e)
    raise SystemExit(1)
print('\nATLAS LINK AUDIT PASSED')
