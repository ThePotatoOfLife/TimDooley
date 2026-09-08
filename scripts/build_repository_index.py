#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
OUT = DATA / 'repository-index.json'
ID_KEYS = ('id','slug','key','term','iso3','country_id')
NAME_KEYS = ('name','display_name','proper_name','title','label','term')
DESC_KEYS = ('description','definition','summary','purpose','meaning','notes','worldview','core','origin')
SKIP = {'repository-index.json', 'canonical-record-registry.json'}

# Runtime navigation must distinguish canonical records from overlays and projections.
# These are conservative source-path classifications; they do not delete or merge data.
ROLE_RULES = (
    ('enrichment', lambda s: '-enrichment' in s or '/enrichment' in s),
    ('projection', lambda s: any(x in s for x in ('-nodes', 'repository-index', 'country-atlas', 'lexicon', 'glossary', 'comparative-library'))),
    ('relationship', lambda s: s.endswith('relationships.json') or '/relationships' in s),
    ('research', lambda s: '/research/' in s or 'research-' in Path(s).name or '/expansions/' in s or 'expansion-' in Path(s).name),
    ('source', lambda s: '/sources/' in s or Path(s).name.startswith('source-')),
    ('identity-index', lambda s: Path(s).name == 'index.json' or Path(s).name.endswith('-index.json')),
    ('schema', lambda s: 'blueprint' in Path(s).name),
    ('archive', lambda s: 'archive' in Path(s).name),
)

def scalar(v):
    return v if isinstance(v,(str,int,float,bool)) else ''

def first(o, keys):
    for k in keys:
        v = scalar(o.get(k))
        if str(v).strip(): return str(v).strip()
    return ''

def classify(source: str, obj: dict) -> str:
    explicit = obj.get('record_role')
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip()
    for role, predicate in ROLE_RULES:
        if predicate(source):
            return role
    return 'canonical-candidate'

def family(source: str) -> str:
    s = source.lower()
    if '/countries/' in s or 'country-' in Path(s).name or Path(s).name in {'nations.json','country-static.json'}:
        return 'countries'
    if 'north-europe-economic-network' in s or 'north-europe-system-atlas' in s:
        return 'north-europe-economic'
    if 'potatoism' in s or 'potatoverse' in s:
        return 'potatoism'
    if 'religious-' in s or '/religious-' in s or '/christianity/' in s or '/judaism/' in s or '/taoism/' in s or '/buddhism/' in s:
        return 'religion-texts'
    if 'extremism' in s or 'swamp' in s:
        return 'movements-swamp'
    if 'security-intelligence' in s or 'intelligence-' in s:
        return 'security-intelligence'
    if 'research' in s or '/expansions/' in s:
        return 'research'
    if source.endswith('relationships.json') or 'graph' in Path(s).name:
        return 'relationships-graph'
    return 'general'

def walk(v, path, source, out):
    if isinstance(v, dict):
        ident = first(v, ID_KEYS)
        name = first(v, NAME_KEYS)
        if ident and (name or v.get('type') or v.get('kind') or v.get('category')):
            role = classify(source, v)
            out.append({'id':ident,'name':name or ident,'description':first(v,DESC_KEYS)[:1000],
                        'type':str(v.get('type') or v.get('kind') or v.get('category') or ''),
                        'layer':str(v.get('layer') or ''),'record_role':role,
                        'owner_family':family(source),'source':source,'path':path})
        for k,c in v.items(): walk(c,path+[k],source,out)
    elif isinstance(v,list):
        for i,c in enumerate(v): walk(c,path+[i],source,out)

def main():
    records=[]; files=[]; errors=[]
    for p in sorted(DATA.rglob('*.json')):
        if p.name in SKIP: continue
        source=p.relative_to(ROOT).as_posix()
        try: data=json.loads(p.read_text(encoding='utf-8'))
        except Exception as e:
            errors.append({'source':source,'error':f'{type(e).__name__}: {e}'})
            continue
        before=len(records); walk(data,[],source,records)
        files.append({'source':source,'records':len(records)-before})
    seen=set(); unique=[]
    for r in records:
        key=(r['source'],r['id'],json.dumps(r['path'],separators=(',',':')))
        if key not in seen: seen.add(key); unique.append(r)
    unique.sort(key=lambda r:(r['name'].casefold(),r['record_role'],r['source'],r['id']))
    OUT.write_text(json.dumps({'version':'2.0.0','record_count':len(unique),'file_count':len(files),'json_errors':errors,'files':files,'records':unique},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'repository-index: {len(unique)} records, {len(files)} JSON files, {len(errors)} JSON errors')
    return 0

if __name__ == '__main__': raise SystemExit(main())
