#!/usr/bin/env python3
"""Audit canonical ownership, source-map declarations, indexed routes, and taxonomy.

Important distinction: a consolidated semantic concept can have a canonical index ID
that differs from the literal ID/term stored at its selected source path. The index
records that original value as source_record_id; this audit validates both instead of
mistaking consolidation for a broken route.
"""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; MAP=DATA/'canonical-source-map.json'; INDEX=DATA/'repository-index.json'; REGISTRY=DATA/'canonical-record-registry.json'
NON_SOURCE_KEYS={'policy','rule','purpose','empirical_rule','consolidation_actions','known_stale_references','semantic_identity_registry'}
ROOT_LAYERS={'spirit':{'source','meaning','belief','myths'},'mind':{'psychology','hawkinscale','neurobiology'},'matter':{'world','region','institution','network','person','object','event','record','ground'}}

def load(p): return json.loads(p.read_text(encoding='utf-8'))
def declared_paths(v):
    if isinstance(v,str) and v.startswith(('data/','docs/')): return [v]
    if isinstance(v,list): return sum((declared_paths(x) for x in v),[])
    if isinstance(v,dict): return sum((declared_paths(x) for x in v.values()),[])
    return []
def at_path(root,path):
    cur=root
    for part in path:
        if isinstance(cur,list) and isinstance(part,int) and 0<=part<len(cur): cur=cur[part]
        elif isinstance(cur,dict) and part in cur: cur=cur[part]
        else: return None
    return cur
def candidate_identity(obj):
    return str(obj.get('id') or obj.get('slug') or obj.get('key') or obj.get('term') or obj.get('iso3') or obj.get('country_id') or '')

def main():
    errors=[]; warnings=[]
    if not MAP.exists(): errors.append('missing data/canonical-source-map.json')
    if not INDEX.exists(): errors.append('missing data/repository-index.json')
    if errors: print('\n'.join(errors)); return 1
    sm=load(MAP); idx=load(INDEX); families=sm.get('families',{})
    for family,spec in families.items():
        for key,value in spec.items():
            if key in NON_SOURCE_KEYS: continue
            for raw in declared_paths(value):
                p=ROOT/raw
                if raw.endswith('/'):
                    if not p.is_dir(): warnings.append(f'{family}: declared directory is absent: {raw}')
                elif '*' in raw or '?' in raw:
                    if not list(ROOT.glob(raw)): errors.append(f'{family}: declared pattern has no matches: {raw}')
                elif not p.is_file(): errors.append(f'{family}: declared source does not exist: {raw}')
    by_id={}; checked=0; taxonomy_counts={'spirit':0,'mind':0,'matter':0}
    for row in idx.get('records',[]):
        source=row.get('source'); path=row.get('path'); rid=str(row.get('id',''))
        if not source or not isinstance(path,list): errors.append(f'index: malformed route for {rid or "<unknown>"}'); continue
        root=str(row.get('repository_root','')).lower(); layer=str(row.get('repository_layer','')).lower()
        if root not in ROOT_LAYERS: errors.append(f'index: invalid repository_root for {rid}: {root!r}')
        elif layer not in ROOT_LAYERS[root]: errors.append(f'index: invalid repository_layer for {rid}: {root}/{layer}')
        else: taxonomy_counts[root]+=1
        if not isinstance(row.get('repository_scale'),str) or not row.get('repository_scale'): errors.append(f'index: missing repository_scale for {rid}')
        fp=ROOT/source
        if not fp.is_file(): errors.append(f'index: missing source for {rid}: {source}'); continue
        try: payload=load(fp)
        except Exception as exc: errors.append(f'index: invalid JSON for {source}: {exc}'); continue
        candidate=at_path(payload,path)
        if not isinstance(candidate,dict): errors.append(f'index: unresolved path for {rid}: {source} {path!r}'); continue
        actual=candidate_identity(candidate)
        expected_source_id=str(row.get('source_record_id') or rid)
        if actual!=expected_source_id:
            errors.append(f'index: source id mismatch {rid} -> {source} {path!r} expected {expected_source_id} contains {actual}')
        if actual!=rid:
            if row.get('canonical_concept') and row.get('canonical_id')==rid:
                pass
            else:
                errors.append(f'index: id mismatch {rid} -> {source} {path!r} contains {actual}')
        checked+=1; by_id.setdefault(rid,[]).append(row)
    owners={}
    for family,spec in families.items():
        for key in ('canonical_owner','adjacent_owner'):
            for source in declared_paths(spec.get(key)): owners.setdefault(source,set()).add(family)
    for rid,rows in by_id.items():
        sources={r.get('source') for r in rows if r.get('source') in owners}
        if len(sources)<=1: continue
        fams=set().union(*(owners[s] for s in sources)); msg=f'canonical ID {rid} has owners {sorted(sources)} across families {sorted(fams)}'
        if len(fams)<=1: errors.append('duplicate canonical owner within family: '+msg)
        else: warnings.append('cross-family canonical ID requires namespace review: '+msg)
    if REGISTRY.exists():
        reg=load(REGISTRY); reg_ids={str(r.get('id')) for r in reg.get('records',[])}; idx_ids=set(by_id); missing=idx_ids-reg_ids
        if missing: errors.append(f'registry missing indexed IDs: {len(missing)}')
        if reg_ids!=idx_ids: warnings.append(f'registry/index ID sets differ: registry={len(reg_ids)} index={len(idx_ids)}; registry inventories raw IDs while index consolidates semantic concepts')
    result={'version':'1.5.0','checked_routes':checked,'indexed_ids':len(by_id),'families':len(families),'canonical_sources':len(owners),'taxonomy_counts':taxonomy_counts,'errors':errors,'warnings':warnings,'status':'fail' if errors else 'pass'}
    (DATA/'source-of-truth-audit.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); print(json.dumps(result,indent=2)); return 1 if errors else 0
if __name__=='__main__': raise SystemExit(main())
