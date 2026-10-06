#!/usr/bin/env python3
"""Validate the relationship-first atlas against the current manifest architecture."""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; ERRORS=[]; WARNINGS=[]

REQUIRED_BRANCHES={'tim','son','spirit','transformation','cosmology','body','traditions','north','world','timeline','works','sources'}

def load(p):
    try:
        with p.open(encoding='utf-8') as f:return json.load(f)
    except Exception as e:
        ERRORS.append(f'Invalid JSON: {p.relative_to(ROOT)} — {e}'); return {}

def exists(rel,required=True):
    ok=(ROOT/rel).exists()
    if not ok:(ERRORS if required else WARNINGS).append(f'Missing {"required" if required else "optional"} path: {rel}')
    return ok

def canon_id(x):
    aliases={'democratic-republic-of-congo':'democratic-republic-of-the-congo','republic-of-the-congo':'congo','turkiye':'turkey','state-of-palestine':'palestine'}
    return aliases.get(x,x)

def validate_manifest():
    manifest=load(ROOT/'manifest.json')
    root=manifest.get('root',{})
    if root.get('id')!='potato-of-life':
        ERRORS.append('Manifest root must be potato-of-life')
    branch_ids=[b.get('id') for b in manifest.get('branches',[]) if b.get('id')]
    missing=sorted(REQUIRED_BRANCHES-set(branch_ids))
    if missing:ERRORS.append(f'Manifest missing canonical branches: {missing}')
    dupes=sorted({x for x in branch_ids if branch_ids.count(x)>1})
    if dupes:ERRORS.append(f'Manifest contains duplicate branch IDs: {dupes}')
    by_id={b.get('id'):b for b in manifest.get('branches',[]) if b.get('id')}
    if 'axis' in by_id:
        WARNINGS.append('Legacy AXIS top-level branch remains in current manifest; Axis should be internal to cosmology/North')
    # Potatoism should be reachable through canonical records/terms, not an obsolete AXIS collection.
    reachability=[]
    for bid in ('tim','transformation','cosmology','traditions','sources'):
        b=by_id.get(bid,{})
        reachability.extend(b.get('records',[]))
        reachability.extend(b.get('children',[]))
    joined=' '.join(map(str,reachability)).casefold()
    if not any(token in joined for token in ('potato','potatoism','potato-of-life','potatoverse')):
        ERRORS.append('Potato of Life / Potatoism records are not reachable from current manifest branches')
    for p in manifest.get('pathways',[]):
        for bid in p.get('branches',[]):
            if bid not in by_id:ERRORS.append(f'Pathway {p.get("id","?")} references unknown branch: {bid}')
    for r in manifest.get('relations',[]):
        for side in ('from','to'):
            bid=r.get(side)
            if bid and bid not in by_id:ERRORS.append(f'Manifest relation references unknown {side} branch: {bid}')
    for b in by_id.values():
        for rel in b.get('records',[]):
            if not (ROOT/rel).exists():ERRORS.append(f'Manifest branch {b.get("id")} references missing record: {rel}')
    return manifest

def main():
    backend=load(ROOT/'data/backend.json'); endpoints=backend.get('endpoints',{}); required=set(backend.get('required',[]))
    for k,v in endpoints.items():
        rel=v if isinstance(v,str) else v.get('path','') if isinstance(v,dict) else ''
        if not rel:ERRORS.append(f'Backend endpoint has no path: {k}');continue
        if exists(rel,k in required) and rel.endswith('.json'):load(ROOT/rel)

    manifest=validate_manifest()

    ci=load(ROOT/'data/countries/index.json').get('countries',[])
    layer=load(ROOT/'data/country-layer-manifest.json')
    country_raw={x.get('id') for x in ci if x.get('id')}; country_iso={x.get('iso3') for x in ci if x.get('iso3')}; country_ids={canon_id(x) for x in country_raw}
    if len(ci)!=195:ERRORS.append(f'Canonical country index has {len(ci)} records; expected 195')
    if len(country_iso)!=195:ERRORS.append(f'Country index has {len(country_iso)} ISO identities; expected 195')
    for cid in sorted(country_raw):
        p=ROOT/'data/countries'/f'{cid}.json'
        if not p.exists():ERRORS.append(f'Missing canonical country record: {p.relative_to(ROOT)}')
        else:
            d=load(p)
            if not d:ERRORS.append(f'Empty or invalid canonical country record: {p.relative_to(ROOT)}')
            identity=d.get('identity',{}) if isinstance(d.get('identity',{}),dict) else {}
            record_id=identity.get('id') or d.get('id') or d.get('country_id')
            if record_id not in {cid,None}:ERRORS.append(f'Country identity mismatch: {cid} -> {record_id}')
    if layer.get('canonical_count')!=195:ERRORS.append('Country layer manifest canonical_count is not 195')
    if layer.get('batch_manifests') or layer.get('batch_count') not in (0,None):ERRORS.append('Country layer still declares retired batch overlays')
    if layer.get('enrichment_pattern') is not None:ERRORS.append('Country layer still declares a separate enrichment overlay pattern')
    stale=list(ROOT.glob('data/country-enrichment-batch-*.json'))+list(ROOT.glob('data/country-nodes-batch-*.json'))+list(ROOT.glob('data/countries/*-enrichment.json'))
    if stale:WARNINGS.append(f'Retired country artifacts remain pending archive migration: {len(stale)}')

    graph=load(ROOT/'data/graph-registry.json'); rels=load(ROOT/'data/relationships.json'); nodes=load(ROOT/'data/nodes.json'); children=load(ROOT/'data/tree-child-records.json')
    graph_ids={x.get('id') for x in nodes.get('nodes',[]) if x.get('id')}|{x.get('id') for x in children.get('records',[]) if x.get('id')}|{x.get('id') for x in graph.get('records',[]) if x.get('id')}|country_ids
    for r in rels.get('relationships',[]):
        for side in ('source','target'):
            if r.get(side) and r[side] not in graph_ids:ERRORS.append(f'Relationship {r.get("id","?")} has unknown {side}: {r[side]}')

    belief_files=['data/belief-space.json','data/belief-backend.json','data/belief-registry.json','data/political-lexicon.json','data/religious-lexicon.json']
    for f in belief_files:exists(f)
    s=load(ROOT/'data/belief-space.json'); p=load(ROOT/'data/political-lexicon.json'); r=load(ROOT/'data/religious-lexicon.json')
    if not s.get('political',{}).get('axes') or not s.get('religious',{}).get('axes'):WARNINGS.append('Belief space does not expose both political and religious axis models')
    pe=p.get('entries',[]); re_=r.get('entries',[]); pi=[x[0] for x in pe if isinstance(x,list) and len(x)>=2]; ri=[x[0] for x in re_ if isinstance(x,list) and len(x)>=2]
    if len(pi)!=len(set(pi)):ERRORS.append('Political lexicon contains duplicate IDs')
    if len(ri)!=len(set(ri)):ERRORS.append('Religious lexicon contains duplicate IDs')
    if set(pi)&set(ri):ERRORS.append('Political and religious lexicons contain colliding IDs')

    ref=re.compile(r'''(?:href|src)=["']([^"'#?]+)["']''',re.I)
    for h in ROOT.glob('*.html'):
        for x in ref.findall(h.read_text(encoding='utf-8',errors='replace')):
            if x.startswith(('http:','https:','mailto:','javascript:','data:')) or '${' in x:continue
            t=(ROOT/x).resolve()
            try:t.relative_to(ROOT.resolve())
            except ValueError:continue
            if not t.exists():WARNINGS.append(f'Local HTML reference does not exist: {h.name} → {x}')

    print(f'Manifest root: {manifest.get("root",{}).get("id","?")} · branches: {len(manifest.get("branches",[]))}')
    print(f'Canonical countries: {len(ci)}/195')
    print(f'Country artifacts: {len(stale)} retired overlays pending archive migration')
    print(f'Graph registry records: {len(graph.get("records",[]))}')
    print(f'Relationships checked: {len(rels.get("relationships",[]))}')
    print(f'Political beliefs: {len(pe)} · Religious beliefs: {len(re_)}')
    print(f'Errors: {len(ERRORS)} · Warnings: {len(WARNINGS)}')
    for x in WARNINGS[:100]:print('WARNING:',x)
    for x in ERRORS[:100]:print('ERROR:',x)
    return 1 if ERRORS else 0

if __name__=='__main__':raise SystemExit(main())
