#!/usr/bin/env python3
"""Audit canonical ownership, source-map declarations, and indexed routes."""
from __future__ import annotations
import fnmatch, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
MAP = DATA / 'canonical-source-map.json'
INDEX = DATA / 'repository-index.json'
REGISTRY = DATA / 'canonical-record-registry.json'
ROLE_KEYS = {'canonical_owner':'canonical','identity_owner':'identity','schema_owner':'schema','graph_schema_owner':'schema','bridge_owner':'projection','system_view':'projection','country_view':'projection','graph_view':'projection','research_question_owner':'research','research_seed_owner':'research','foundation_context':'projection'}
LIST_ROLE_KEYS = {'derived_views':'projection','related_views':'projection','enrichment_layers':'enrichment','adjacent_enrichment':'enrichment','additional_research':'research','expansion_layers':'research','source_layers':'source','source_registry_layers':'source','research_or_extrapolation':'research','documentation_layers':'documentation','legacy_or_fallback':'projection','legacy_or_classification_view':'projection','derived_or_scoped_layers':'relationship'}
NON_SOURCE_KEYS = {'policy','rule','purpose','empirical_rule','consolidation_actions','known_stale_references'}

def load(path): return json.loads(path.read_text(encoding='utf-8'))

def declared_paths(value):
    out=[]
    if isinstance(value,str) and value.startswith(('data/','docs/')): out.append(value)
    elif isinstance(value,list):
        for x in value: out.extend(declared_paths(x))
    elif isinstance(value,dict):
        for x in value.values(): out.extend(declared_paths(x))
    return out

def at_path(root,path):
    cur=root
    for part in path:
        if isinstance(cur,list) and isinstance(part,int) and 0 <= part < len(cur): cur=cur[part]
        elif isinstance(cur,dict) and part in cur: cur=cur[part]
        else: return None
    return cur

def main():
    errors=[]; warnings=[]
    if not MAP.exists(): errors.append('missing data/canonical-source-map.json')
    if not INDEX.exists(): errors.append('missing data/repository-index.json')
    if errors: print('\n'.join(errors)); return 1
    source_map=load(MAP); index=load(INDEX); families=source_map.get('families',{})
    for family,spec in families.items():
        for key,value in spec.items():
            if key in NON_SOURCE_KEYS: continue
            for raw in declared_paths(value):
                p=ROOT/raw
                if raw.endswith('/'):
                    if not p.is_dir(): warnings.append(f'{family}: declared directory is absent from Git: {raw}')
                elif '*' in raw or '?' in raw:
                    if not list(ROOT.glob(raw)): errors.append(f'{family}: declared pattern has no matches: {raw}')
                elif not p.is_file(): errors.append(f'{family}: declared source does not exist: {raw}')
    records=index.get('records',[]); checked=0; by_id={}
    for row in records:
        source=row.get('source'); path=row.get('path'); rid=str(row.get('id',''))
        if not source or not isinstance(path,list): errors.append(f'index: malformed route for {rid or "<unknown>"}'); continue
        fp=ROOT/source
        if not fp.is_file(): errors.append(f'index: missing source for {rid}: {source}'); continue
        try: payload=load(fp)
        except Exception as exc: errors.append(f'index: invalid JSON for {source}: {exc}'); continue
        candidate=at_path(payload,path)
        if not isinstance(candidate,dict): errors.append(f'index: unresolved path for {rid}: {source} {path!r}'); continue
        actual=str(candidate.get('id') or candidate.get('slug') or candidate.get('key') or candidate.get('term') or candidate.get('iso3') or candidate.get('country_id') or '')
        if actual != rid: errors.append(f'index: id mismatch {rid} -> {source} {path!r} contains {actual}')
        checked += 1; by_id.setdefault(rid,[]).append(row)
    owner_sources={}
    for family,spec in families.items():
        for key in ('canonical_owner','adjacent_owner'):
            for source in declared_paths(spec.get(key)): owner_sources.setdefault(source,set()).add(family)
    hard=[]; cross_family=[]
    for rid,rows in by_id.items():
        owners=[r for r in rows if r.get('source') in owner_sources]; sources={r.get('source') for r in owners}
        if len(sources) <= 1: continue
        fams=set()
        for src in sources: fams.update(owner_sources.get(src,set()))
        if len(fams) <= 1: hard.append((rid,sources))
        else: cross_family.append((rid,sources,fams))
    for rid,sources in hard: errors.append(f'duplicate canonical owner within family: {rid} -> '+', '.join(sorted(sources)))
    for rid,sources,fams in cross_family: warnings.append(f'cross-family canonical ID requires namespace review: {rid} -> families={sorted(fams)} sources={sorted(sources)}')
    if REGISTRY.exists():
        reg=load(REGISTRY); reg_ids={str(r.get('id')) for r in reg.get('records',[])}; idx_ids=set(by_id); missing=idx_ids-reg_ids
        if missing: errors.append(f'registry missing indexed IDs: {len(missing)}')
        if reg_ids != idx_ids: warnings.append(f'registry/index ID sets differ: registry={len(reg_ids)} index={len(idx_ids)}; registry is expected to inventory at least the index')
    result={'version':'1.2.0','checked_routes':checked,'indexed_ids':len(by_id),'families':len(families),'canonical_sources':len(owner_sources),'errors':errors,'warnings':warnings,'status':'fail' if errors else 'pass'}
    out=DATA/'source-of-truth-audit.json'; out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2)); return 1 if errors else 0

if __name__=='__main__': raise SystemExit(main())
