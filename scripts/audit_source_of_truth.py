#!/usr/bin/env python3
"""Audit canonical ownership, source-map references, and repository-index routes."""
from __future__ import annotations
import fnmatch, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
MAP = DATA / 'canonical-source-map.json'
INDEX = DATA / 'repository-index.json'
REGISTRY = DATA / 'canonical-record-registry.json'

# Only explicit canonical owners are authoritative. Everything else is an
# overlay, projection, research/source layer, or an unclassified candidate.
ROLE_KEYS = {
    'canonical_owner': 'canonical', 'identity_owner': 'identity',
    'schema_owner': 'schema', 'graph_schema_owner': 'schema',
    'bridge_owner': 'projection', 'system_view': 'projection',
    'country_view': 'projection', 'graph_view': 'projection',
    'research_question_owner': 'research', 'research_seed_owner': 'research',
}
LIST_ROLE_KEYS = {
    'derived_views':'projection','related_views':'projection','enrichment_layers':'enrichment',
    'adjacent_enrichment':'enrichment','additional_research':'research','expansion_layers':'research',
    'source_layers':'source','source_registry_layers':'source','research_or_extrapolation':'research',
    'documentation_layers':'documentation','subdirectories':'directory',
}

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

def role_for(source, source_map):
    for _, spec in source_map.get('families',{}).items():
        for key, value in spec.items():
            role=ROLE_KEYS.get(key) or LIST_ROLE_KEYS.get(key)
            if not role: continue
            for pattern in declared_paths(value):
                if '*' in pattern or '?' in pattern:
                    if fnmatch.fnmatch(source, pattern): return role
                elif source == pattern: return role
    # Conservative path defaults for known generated/technical layers.
    name=Path(source).name; s=source.lower()
    if name in {'repository-index.json','canonical-record-registry.json'}: return 'projection'
    if name.endswith('-enrichment.json') or '/enrichment/' in s: return 'enrichment'
    if '/blueprints/' in s or name.endswith('blueprint.json'): return 'schema'
    if name == 'graph-registry.json': return 'schema'
    if name.endswith('relationships.json'): return 'relationship'
    if '/research/' in s or '/expansions/' in s or 'research-' in name or 'expansion-' in name: return 'research'
    if '/sources/' in s or name.startswith('source-'): return 'source'
    if name == 'index.json' or name.endswith('-index.json'): return 'identity'
    return 'unclassified'

def main():
    errors=[]; warnings=[]
    if not MAP.exists(): errors.append('missing data/canonical-source-map.json')
    if not INDEX.exists(): errors.append('missing data/repository-index.json')
    if errors:
        print('\n'.join(errors)); return 1
    source_map=load(MAP); index=load(INDEX)
    families=source_map.get('families',{})
    # Validate declared files and directories separately.
    for family, spec in families.items():
        for key, value in spec.items():
            for raw in declared_paths(value):
                p=ROOT/raw
                if raw.endswith('/'):
                    if not p.is_dir(): errors.append(f'{family}: declared directory does not exist: {raw}')
                elif '*' in raw or '?' in raw:
                    if not list(ROOT.glob(raw)): errors.append(f'{family}: declared pattern has no matches: {raw}')
                elif not p.is_file(): errors.append(f'{family}: declared source does not exist: {raw}')
    records=index.get('records',[]); checked=0
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
        checked += 1
    # Canonical conflicts are tested only against the source map's explicit
    # canonical_owner declarations. Repeated IDs in graph schemas, indexes,
    # research and overlays are not ownership conflicts.
    canonical_sources=set()
    for spec in families.values():
        canonical_sources.update(declared_paths(spec.get('canonical_owner')))
        canonical_sources.update(declared_paths(spec.get('adjacent_owner')))
    by_id={}
    for row in records:
        rid=str(row.get('id','')); src=row.get('source','')
        if rid: by_id.setdefault(rid,[]).append(row)
    competing=[]
    for rid, rows in by_id.items():
        owners=[r for r in rows if r.get('source') in canonical_sources]
        if len({r.get('source') for r in owners})>1: competing.append((rid,owners))
    for rid, rows in competing:
        errors.append(f'duplicate canonical owner: {rid} -> '+', '.join(sorted({r['source'] for r in rows})))
    if REGISTRY.exists():
        reg=load(REGISTRY)
        reg_ids={str(r.get('id')) for r in reg.get('records',[])}
        idx_ids=set(by_id)
        if not idx_ids.issubset(reg_ids): errors.append(f'registry missing indexed IDs: {len(idx_ids-reg_ids)}')
        if reg_ids != idx_ids: warnings.append(f'registry/index ID sets differ because registry inventories deeper record-like objects: registry={len(reg_ids)} index={len(idx_ids)}')
    result={'version':'1.1.0','checked_routes':checked,'indexed_ids':len(by_id),'families':len(families),'canonical_sources':len(canonical_sources),'errors':errors,'warnings':warnings,'status':'fail' if errors else 'pass'}
    out=DATA/'source-of-truth-audit.json'; out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2)); return 1 if errors else 0

if __name__=='__main__': raise SystemExit(main())
