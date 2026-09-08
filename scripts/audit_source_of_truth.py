#!/usr/bin/env python3
"""Audit canonical ownership, source-map references, and repository-index routes."""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
MAP = DATA / 'canonical-source-map.json'
INDEX = DATA / 'repository-index.json'
REGISTRY = DATA / 'canonical-record-registry.json'

ROLE_ALIASES = {
    'canonical': {'canonical-candidate','canonical'},
    'identity': {'identity-index','identity'},
    'enrichment': {'enrichment'},
    'projection': {'projection'},
    'relationship': {'relationship'},
    'research': {'research'},
    'source': {'source'},
    'schema': {'schema'},
    'archive': {'archive'},
}

def load(path):
    return json.loads(path.read_text(encoding='utf-8'))

def exists(path):
    return (ROOT / path).is_file()

def source_paths(value):
    out=[]
    if isinstance(value,str) and value.startswith(('data/','docs/')): out.append(value)
    elif isinstance(value,list):
        for x in value: out.extend(source_paths(x))
    elif isinstance(value,dict):
        for x in value.values(): out.extend(source_paths(x))
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
    if errors:
        print('\n'.join(errors)); return 1
    source_map=load(MAP); index=load(INDEX)
    families=source_map.get('families',{})
    # Every declared source path must exist. Wildcards are validated only when they are explicit globs.
    for family, spec in families.items():
        for key, value in spec.items():
            for raw in source_paths(value):
                if '*' in raw or '?' in raw:
                    matches=list(ROOT.glob(raw))
                    if not matches: errors.append(f'{family}: declared pattern has no matches: {raw}')
                elif not exists(raw):
                    errors.append(f'{family}: declared source does not exist: {raw}')
    # Every index route must resolve to the exact JSON path it advertises.
    records=index.get('records',[])
    checked=0
    for row in records:
        source=row.get('source'); path=row.get('path'); rid=str(row.get('id',''))
        if not source or not isinstance(path,list):
            errors.append(f'index: malformed route for {rid or "<unknown>"}')
            continue
        fp=ROOT/source
        if not fp.is_file():
            errors.append(f'index: missing source for {rid}: {source}')
            continue
        try: payload=load(fp)
        except Exception as exc:
            errors.append(f'index: invalid JSON for {source}: {exc}')
            continue
        candidate=at_path(payload,path)
        if not isinstance(candidate,dict):
            errors.append(f'index: unresolved path for {rid}: {source} {path!r}')
            continue
        actual=str(candidate.get('id') or candidate.get('slug') or candidate.get('key') or candidate.get('term') or candidate.get('iso3') or candidate.get('country_id') or '')
        if actual != rid:
            errors.append(f'index: id mismatch {rid} -> {source} {path!r} contains {actual}')
        checked += 1
    # Duplicate IDs are informational unless multiple occurrences claim a canonical role.
    by_id={}
    for row in records:
        by_id.setdefault(str(row.get('id','')),[]).append(row)
    competing=[]
    for rid, rows in by_id.items():
        canon=[r for r in rows if r.get('record_role') in ROLE_ALIASES['canonical']]
        if len(canon)>1:
            competing.append((rid,canon))
    if competing:
        errors.extend([f'duplicate canonical owner candidate: {rid} -> '+', '.join(r['source'] for r in rows) for rid,rows in competing])
    # Registry is generated and must agree on the set of indexed IDs when present.
    if REGISTRY.exists():
        reg=load(REGISTRY)
        reg_ids={str(r.get('id')) for r in reg.get('records',[])}
        idx_ids=set(by_id)
        if reg_ids and reg_ids != idx_ids:
            warnings.append(f'registry/index ID sets differ: registry={len(reg_ids)} index={len(idx_ids)}')
    result={
        'version':'1.0.0','checked_routes':checked,'indexed_ids':len(by_id),
        'families':len(families),'errors':errors,'warnings':warnings,
        'status':'fail' if errors else 'pass'
    }
    out=DATA/'source-of-truth-audit.json'
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
    return 1 if errors else 0

if __name__=='__main__': raise SystemExit(main())
