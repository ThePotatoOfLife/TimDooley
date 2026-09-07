#!/usr/bin/env python3
"""Validate the relationship-first atlas before deployment."""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; ERRORS=[]; WARNINGS=[]
def load(p):
    try:
        with p.open(encoding='utf-8') as f:return json.load(f)
    except Exception as e: ERRORS.append(f'Invalid JSON: {p.relative_to(ROOT)} — {e}'); return {}
def exists(rel,required=True):
    ok=(ROOT/rel).exists()
    if not ok:(ERRORS if required else WARNINGS).append(f'Missing {"required" if required else "optional"} path: {rel}')
    return ok
def canon_id(x):
    aliases={'democratic-republic-of-congo':'democratic-republic-of-the-congo','republic-of-the-congo':'congo','turkiye':'turkey','state-of-palestine':'palestine'}
    return aliases.get(x,x)
def beliefs():
    s=load(ROOT/'data/belief-space.json'); b=load(ROOT/'data/belief-backend.json'); p=load(ROOT/'data/political-lexicon.json'); r=load(ROOT/'data/religious-lexicon.json')
    for x in ['belief.html','political-compass.html','data/belief-space.json','data/belief-backend.json','data/belief-registry.json','data/political-lexicon.json','data/religious-lexicon.json']:exists(x)
    if not s.get('political',{}).get('axes') or not s.get('religious',{}).get('axes'):ERRORS.append('Belief space must define both political and religious three-axis models')
    pe=p.get('entries',[]); re_=r.get('entries',[]); pi=[x[0] for x in pe if isinstance(x,list) and len(x)>=2]; ri=[x[0] for x in re_ if isinstance(x,list) and len(x)>=2]
    if len(pi)!=len(set(pi)):ERRORS.append('Political lexicon contains duplicate IDs')
    if len(ri)!=len(set(ri)):ERRORS.append('Religious lexicon contains duplicate IDs')
    if set(pi)&set(ri):ERRORS.append('Political and religious lexicons contain colliding IDs')
    for x in pe:
        if not isinstance(x,list) or len(x)<5:ERRORS.append('Political lexicon entry has invalid shape');continue
        if not all(isinstance(v,(int,float)) for v in x[2:4]) or not all(-10<=float(v)<=10 for v in x[2:4]):ERRORS.append(f'Political coordinates invalid: {x[0]}')
    if b.get('individualRecord')!='belief.html?id=<slug>':ERRORS.append('Belief backend individualRecord route is incorrect')
    return len(pe),len(re_)
def main():
    backend=load(ROOT/'data/backend.json'); endpoints=backend.get('endpoints',{}); required=set(backend.get('required',[]))
    for k,v in endpoints.items():
        rel=v if isinstance(v,str) else v.get('path','') if isinstance(v,dict) else ''
        if not rel:ERRORS.append(f'Backend endpoint has no path: {k}');continue
        if exists(rel,k in required) and rel.endswith('.json'):load(ROOT/rel)
    nations=load(ROOT/'data/nations.json').get('nations',[]); ci=load(ROOT/'data/countries/index.json').get('countries',[]); repair=load(ROOT/'data/countries/democratic-republic-of-the-congo.json'); repair_id=repair.get('id')
    nation_ids={canon_id(x.get('id')) for x in nations if x.get('id')}; country_ids={canon_id(x.get('id')) for x in ci if x.get('id')}
    if len(nations)!=195:ERRORS.append(f'Canonical nation directory has {len(nations)} records; expected 195')
    if len(country_ids)!=195:ERRORS.append(f'Country layer has {len(country_ids)} canonical IDs; expected 195')
    if nation_ids!=country_ids:ERRORS.append(f'Canonical nation directory and country layer IDs differ: nations-only={sorted(nation_ids-country_ids)} country-only={sorted(country_ids-nation_ids)}')
    for cid in country_ids:
        p=ROOT/'data/countries'/f'{cid}.json'
        if cid==canon_id(repair_id):
            p=ROOT/'data/countries'/'democratic-republic-of-the-congo.json'
        if not p.exists():ERRORS.append(f'Missing canonical country record: {p.relative_to(ROOT)}')
    base=load(ROOT/'data/country-enrichment-index.json'); base_ids=set(base.get('enriched_ids',[])); base_nodes=load(ROOT/'data/country-nodes.json').get('nodes',[])
    batches=sorted(ROOT.glob('data/country-enrichment-batch-*.json')); node_batches=sorted(ROOT.glob('data/country-nodes-batch-*.json')); all_ids=set(base_ids); all_nodes=list(base_nodes); seen=[]
    for bp in batches:
        b=load(bp); ids=set(b.get('added_ids',[])); seen.extend(ids)
        if b.get('added_count')!=len(ids):ERRORS.append(f'{bp.name}: added_count mismatch')
        if ids&base_ids:ERRORS.append(f'{bp.name}: duplicates base overlays: {sorted(ids&base_ids)}')
        if ids-country_ids:ERRORS.append(f'{bp.name}: unknown country IDs: {sorted(ids-country_ids)}')
        all_ids|=ids
    if len(seen)!=len(set(seen)):ERRORS.append('Country enrichment batches contain duplicate country IDs')
    for np in node_batches:all_nodes.extend(load(np).get('nodes',[]))
    node_ids={x.get('country_id') for x in all_nodes if x.get('country_id')}
    if node_ids!=all_ids:ERRORS.append('Combined country graph nodes and enrichment layers are out of sync')
    for cid in sorted(all_ids):
        p=ROOT/'data/countries'/f'{cid}-enrichment.json'
        if not p.exists():ERRORS.append(f'Missing enrichment overlay: {p.name}')
        else:load(p)
    graph=load(ROOT/'data/graph-registry.json'); rels=load(ROOT/'data/relationships.json'); nodes=load(ROOT/'data/nodes.json'); children=load(ROOT/'data/tree-child-records.json')
    graph_ids={x.get('id') for x in nodes.get('nodes',[]) if x.get('id')}|{x.get('id') for x in children.get('records',[]) if x.get('id')}|{x.get('id') for x in graph.get('records',[]) if x.get('id')}|{x.get('id') for x in all_nodes if x.get('id')}|country_ids
    for r in rels.get('relationships',[]):
        for side in ('source','target'):
            if r.get(side) and r[side] not in graph_ids:ERRORS.append(f'Relationship {r.get("id","?")} has unknown {side}: {r[side]}')
    ref=re.compile(r'''(?:href|src)=["']([^"'#?]+)["']''',re.I)
    for h in ROOT.glob('*.html'):
        for x in ref.findall(h.read_text(encoding='utf-8',errors='replace')):
            if x.startswith(('http:','https:','mailto:','javascript:','data:')) or '${' in x:continue
            t=(ROOT/x).resolve()
            try:t.relative_to(ROOT.resolve())
            except ValueError:continue
            if not t.exists():WARNINGS.append(f'Local HTML reference does not exist: {h.name} → {x}')
    pc,rc=beliefs(); print(f'Canonical nations: {len(nations)}/195');print(f'Enrichment overlays: {len(all_ids)} ({len(base_ids)} base + {len(seen)} batch records)');print(f'Country graph nodes: {len(all_nodes)}');print(f'Enrichment batches discovered: {len(batches)}');print(f'Graph registry records: {len(graph.get("records",[]))}');print(f'Relationships checked: {len(rels.get("relationships",[]))}');print(f'Political beliefs: {pc} · Religious beliefs: {rc}');print(f'Errors: {len(ERRORS)} · Warnings: {len(WARNINGS)}')
    for x in WARNINGS[:100]:print('WARNING:',x)
    for x in ERRORS[:100]:print('ERROR:',x)
    return 1 if ERRORS else 0
if __name__=='__main__':raise SystemExit(main())
