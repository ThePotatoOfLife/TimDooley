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
SKIP = {'repository-index.json', 'canonical-record-registry.json', 'source-of-truth-audit.json'}

ROOTS = {'spirit','mind','matter'}
SPIRIT = {'source','meaning','belief','myths'}
MIND = {'psychology','hawkinscale','neurobiology'}
MATTER = {'world','region','institution','network','person','object','event','record','ground'}
SCALES = {'source','principle','concept','world','region','institution','network','person','object','event','record','ground'}

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

def scalar(v): return v if isinstance(v,(str,int,float,bool)) else ''

def first(o, keys):
    for k in keys:
        v = scalar(o.get(k))
        if str(v).strip(): return str(v).strip()
    return ''

def classify_role(source: str, obj: dict) -> str:
    explicit = obj.get('record_role')
    if isinstance(explicit, str) and explicit.strip(): return explicit.strip()
    for role, predicate in ROLE_RULES:
        if predicate(source): return role
    return 'canonical-candidate'

def family(source: str) -> str:
    s = source.lower(); name = Path(s).name
    if '/countries/' in s or 'country-' in name or name in {'nations.json','country-static.json'}: return 'countries'
    if 'north-europe-economic-network' in s or 'north-europe-system-atlas' in s: return 'north-europe-economic'
    if 'potatoism' in s or 'potatoverse' in s: return 'potatoism'
    if 'religious-' in s or '/religious-' in s or any(x in s for x in ('/christianity/','/judaism/','/taoism/','/buddhism/')): return 'religion-texts'
    if 'extremism' in s or 'swamp' in s: return 'movements-swamp'
    if 'security-intelligence' in s or 'intelligence-' in s: return 'security-intelligence'
    if 'research' in s or '/expansions/' in s: return 'research'
    if source.endswith('relationships.json') or 'graph' in name: return 'relationships-graph'
    return 'general'

def explicit_value(obj: dict, keys: tuple[str,...]) -> str:
    for k in keys:
        v = obj.get(k)
        if isinstance(v,str) and v.strip(): return v.strip().lower()
    return ''

def classify_repository(source: str, obj: dict, rid: str, rtype: str, role: str, fam: str) -> tuple[str,str,str]:
    # Explicit record metadata always wins. This lets future source owners declare placement
    # without changing this builder.
    root = explicit_value(obj, ('repository_root','root_branch','branch'))
    layer = explicit_value(obj, ('repository_layer','root_layer','navigation_layer'))
    scale = explicit_value(obj, ('repository_scale','scale'))
    if root in ROOTS and layer in (SPIRIT | MIND | MATTER):
        if (root == 'spirit' and layer in SPIRIT) or (root == 'mind' and layer in MIND) or (root == 'matter' and layer in MATTER):
            return root, layer, scale if scale in SCALES else layer

    s = source.lower(); n = Path(s).name
    # Source-family placement is the stable fallback. Description keyword matching is
    # deliberately not used: prose should never silently move a record between branches.
    if fam == 'potatoism':
        if any(x in n for x in ('observation','research','source','corpus')): return 'spirit','meaning','record'
        return 'spirit','meaning','concept'
    if fam == 'religion-texts':
        if any(x in n for x in ('myth','edda','norse','saga')): return 'spirit','myths','record'
        return 'spirit','belief','record'
    if any(x in s for x in ('hawkins-scale','hawkinscale')) or 'hawkins' in n: return 'mind','hawkinscale','concept'
    if any(x in s for x in ('neurobiology','neuro-','brain','pineal','thalam')): return 'mind','neurobiology','record'
    if any(x in s for x in ('psychology','psychological')): return 'mind','psychology','record'

    # Strong data-shape/source rules for Matter.
    if role in {'relationship'} or 'relationships' in s or 'graph' in n: return 'matter','network','network'
    if fam == 'countries' or any(x in n for x in ('nation','country','countries','geography','atlas')): return 'matter','region','region'
    if rtype in {'person','people','individual','human'}: return 'matter','person','person'
    if rtype in {'event','action','transaction','war','election'}: return 'matter','event','event'
    if rtype in {'organization','institution','company','bank','university','government','authority','system'}: return 'matter','institution','institution'
    if rtype in {'network','movement','alliance','market','supply-chain'}: return 'matter','network','network'
    if rtype in {'object','artifact','machine','technology','infrastructure','resource'}: return 'matter','object','object'
    if role in {'source','research','projection','identity-index','schema','archive','enrichment'}: return 'matter','record','record'
    if fam == 'north-europe-economic':
        # Economic network files contain companies, ports, institutions and relationships;
        # the record's declared type is more reliable than the filename.
        if rtype in {'company','port','institution','organization','bank','government'}: return 'matter','institution','institution'
        if rtype in {'network','market','supply-chain'}: return 'matter','network','network'
        return 'matter','record','record'
    return 'matter','world','world'

def walk(v, path, source, out):
    if isinstance(v, dict):
        ident = first(v, ID_KEYS); name = first(v, NAME_KEYS)
        if ident and (name or v.get('type') or v.get('kind') or v.get('category')):
            role = classify_role(source, v); rtype = str(v.get('type') or v.get('kind') or v.get('category') or '').strip().lower()
            fam = family(source); root, layer, scale = classify_repository(source, v, ident, rtype, role, fam)
            out.append({'id':ident,'name':name or ident,'description':first(v,DESC_KEYS)[:1000],
                        'type':rtype,'layer':str(v.get('layer') or ''),'record_role':role,
                        'owner_family':fam,'repository_root':root,'repository_layer':layer,
                        'repository_scale':scale,'classification_basis':'explicit' if explicit_value(v,('repository_root','root_branch','branch')) else 'source-family/type',
                        'source':source,'path':path})
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
            errors.append({'source':source,'error':f'{type(e).__name__}: {e}'}); continue
        before=len(records); walk(data,[],source,records); files.append({'source':source,'records':len(records)-before})
    seen=set(); unique=[]
    for r in records:
        key=(r['source'],r['id'],json.dumps(r['path'],separators=(',',':')))
        if key not in seen: seen.add(key); unique.append(r)
    unique.sort(key=lambda r:(r['repository_root'],r['repository_layer'],r['name'].casefold(),r['source'],r['id']))
    OUT.write_text(json.dumps({'version':'3.0.0','taxonomy_version':'repository-spine-2.3.0','record_count':len(unique),'file_count':len(files),'json_errors':errors,'files':files,'records':unique},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    counts={r:sum(1 for x in unique if x['repository_root']==r) for r in ('spirit','mind','matter')}
    print(f'repository-index: {len(unique)} records, {len(files)} JSON files, {len(errors)} JSON errors; roots={counts}')
    return 0
if __name__=='__main__': raise SystemExit(main())