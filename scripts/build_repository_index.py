#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; OUT=DATA/'repository-index.json'; CONCEPT_REGISTRY=DATA/'potatoism-concept-registry.json'
ID_KEYS=('id','slug','key','term','iso3','country_id'); NAME_KEYS=('name','display_name','proper_name','title','label','term'); DESC_KEYS=('description','definition','summary','purpose','meaning','notes','worldview','core','origin')
SKIP={'repository-index.json','canonical-record-registry.json','source-of-truth-audit.json'}; ROOTS={'spirit','mind','matter'}; SPIRIT={'source','meaning','belief','myths'}; MIND={'psychology','hawkinscale','neurobiology'}; MATTER={'world','region','institution','network','person','object','event','record','ground'}; SCALES={'source','principle','concept','world','region','institution','network','person','object','event','record','ground'}
ROLE_RULES=(('enrichment',lambda s:'-enrichment' in s or '/enrichment' in s),('projection',lambda s:any(x in s for x in ('-nodes','repository-index','country-atlas','lexicon','glossary','comparative-library'))),('relationship',lambda s:s.endswith('relationships.json') or '/relationships' in s),('research',lambda s:'/research/' in s or 'research-' in Path(s).name or '/expansions/' in s or 'expansion-' in Path(s).name),('source',lambda s:'/sources/' in s or Path(s).name.startswith('source-')),('identity-index',lambda s:Path(s).name=='index.json' or Path(s).name.endswith('-index.json')),('schema',lambda s:'blueprint' in Path(s).name),('archive',lambda s:'archive' in Path(s).name))
PREFERRED_CONCEPT_SOURCES=('data/potatoism-dossiers.json','data/potatoism-canonical-corpus.json','data/potatoism-lexicon-expanded.json','data/potatoism-lexicon.json','data/potatoism-cosmology.json')
NEURO_TERMS=('neurobiology','neuroscience','neuroanatom','brain','thalam','pineal','neuron','axon','cortex','cortical','cerebr','dienceph','hypothalam','hippocamp','amygdala','nervous system','spinal cord','cerebrospinal','csf')
PSYCHOLOGY_TERMS=('psychology','psychological','cognition','cognitive','behaviour','behavior','personality','developmental psychology','inner life','mental model')
HAWKINS_TERMS=('hawkins-scale','hawkinscale','hawkins scale')
def scalar(v): return v if isinstance(v,(str,int,float,bool)) else ''
def first(o,keys):
    for k in keys:
        v=scalar(o.get(k))
        if str(v).strip(): return str(v).strip()
    return ''
def classify_role(source,obj):
    explicit=obj.get('record_role')
    if isinstance(explicit,str) and explicit.strip(): return explicit.strip()
    for role,predicate in ROLE_RULES:
        if predicate(source): return role
    return 'canonical-candidate'
def family(source):
    s=source.lower(); n=Path(s).name
    if '/countries/' in s or 'country-' in n or n in {'nations.json','country-static.json'}: return 'countries'
    if 'north-europe-economic-network' in s or 'north-europe-system-atlas' in s: return 'north-europe-economic'
    if 'potatoism' in s or 'potatoverse' in s: return 'potatoism'
    if 'religious-' in s or '/religious-' in s or any(x in s for x in ('/christianity/','/judaism/','/taoism/','/buddhism/')): return 'religion-texts'
    if 'extremism' in s or 'swamp' in s: return 'movements-swamp'
    if 'security-intelligence' in s or 'intelligence-' in s: return 'security-intelligence'
    if 'research' in s or '/expansions/' in s: return 'research'
    if source.endswith('relationships.json') or 'graph' in n: return 'relationships-graph'
    return 'general'
def explicit_value(obj,keys):
    for k in keys:
        v=obj.get(k)
        if isinstance(v,str) and v.strip(): return v.strip().lower()
    return ''
def semantic_subject(source,rid,name,rtype,description):
    return ' '.join(str(x).lower() for x in (source,rid,name,rtype,description) if x)
def has_term(text,terms):
    return any(term in text for term in terms)
def classify_repository(source,obj,rid,name,description,rtype,role,fam):
    root=explicit_value(obj,('repository_root','root_branch','branch')); layer=explicit_value(obj,('repository_layer','root_layer','navigation_layer')); scale=explicit_value(obj,('repository_scale','scale'))
    if root in ROOTS and layer in (SPIRIT|MIND|MATTER) and ((root=='spirit' and layer in SPIRIT) or (root=='mind' and layer in MIND) or (root=='matter' and layer in MATTER)): return root,layer,scale if scale in SCALES else layer,'explicit'
    s=source.lower(); n=Path(s).name; subject=semantic_subject(source,rid,name,rtype,description)
    # Subject classification must outrank source-family classification. A neurobiology
    # record does not stop being neurobiology merely because it lives in Potatoism data.
    if has_term(subject,HAWKINS_TERMS): return 'mind','hawkinscale','concept','semantic-subject'
    if has_term(subject,NEURO_TERMS): return 'mind','neurobiology','record','semantic-subject'
    if has_term(subject,PSYCHOLOGY_TERMS): return 'mind','psychology','record','semantic-subject'
    if fam=='potatoism': return 'spirit','meaning','record' if any(x in n for x in ('observation','research','source','corpus')) else 'concept','source-family'
    if fam=='religion-texts': return 'spirit','myths' if any(x in n for x in ('myth','edda','norse','saga')) else 'belief','record','source-family'
    if role=='relationship' or 'relationships' in s or 'graph' in n:return 'matter','network','network','source-family/type'
    if fam=='countries' or any(x in n for x in ('nation','country','countries','geography','atlas')):return 'matter','region','region','source-family/type'
    if rtype in {'person','people','individual','human'}:return 'matter','person','person','type'
    if rtype in {'event','action','transaction','war','election','geopolitical-timeline','economic-environmental-event','mythic-event'}:return 'matter','event','event','type'
    if rtype in {'organization','institution','company','bank','university','government','authority','system'}:return 'matter','institution','institution','type'
    if rtype in {'network','movement','alliance','market','supply-chain'}:return 'matter','network','network','type'
    if rtype in {'object','artifact','machine','technology','infrastructure','resource'}:return 'matter','object','object','type'
    if role in {'source','research','projection','identity-index','schema','archive','enrichment'}:return 'matter','record','record','record-role'
    if fam=='north-europe-economic':
        if rtype in {'company','port','institution','organization','bank','government'}:return 'matter','institution','institution','source-family/type'
        if rtype in {'network','market','supply-chain'}:return 'matter','network','network','source-family/type'
        return 'matter','record','record','source-family'
    return 'matter','world','world','fallback'
def norm(v):return re.sub(r'[^a-z0-9]+',' ',str(v).casefold()).strip()
def load_concepts():
    if not CONCEPT_REGISTRY.exists():return {}
    data=json.loads(CONCEPT_REGISTRY.read_text(encoding='utf-8')); concepts={}; collisions={}
    for c in data.get('concepts',[]):
        cid=str(c.get('canonical_id','')).strip()
        if not cid:continue
        for value in [cid,c.get('term',''),*c.get('aliases',[])]:
            key=norm(value)
            if not key:continue
            if key in concepts and concepts[key]['canonical_id']!=cid: collisions[key]=True
            else: concepts[key]=c
    for key in collisions: concepts.pop(key,None)
    return concepts
def walk(v,path,source,out):
    if isinstance(v,dict):
        ident=first(v,ID_KEYS); name=first(v,NAME_KEYS)
        if ident and (name or v.get('type') or v.get('kind') or v.get('category')):
            role=classify_role(source,v); rtype=str(v.get('type') or v.get('kind') or v.get('category') or '').strip().lower(); fam=family(source); description=first(v,DESC_KEYS)[:1000]; root,layer,scale,basis=classify_repository(source,v,ident,name or ident,description,rtype,role,fam)
            out.append({'id':ident,'name':name or ident,'description':description,'type':rtype,'layer':str(v.get('layer') or ''),'record_role':role,'owner_family':fam,'repository_root':root,'repository_layer':layer,'repository_scale':scale,'classification_basis':basis,'source':source,'path':path})
        for k,c in v.items():walk(c,path+[k],source,out)
    elif isinstance(v,list):
        for i,c in enumerate(v):walk(c,path+[i],source,out)
def concept_match(r,concepts):
    if r.get('owner_family')!='potatoism':return None
    for value in (r.get('id',''),r.get('name','')):
        c=concepts.get(norm(value))
        if c:return c
    return None
def concept_priority(r):
    try:return PREFERRED_CONCEPT_SOURCES.index(r['source'])
    except ValueError:return 99
def main():
    records=[]; files=[]; errors=[]
    for p in sorted(DATA.rglob('*.json')):
        if p.name in SKIP:continue
        source=p.relative_to(ROOT).as_posix()
        try:data=json.loads(p.read_text(encoding='utf-8'))
        except Exception as e:errors.append({'source':source,'error':f'{type(e).__name__}: {e}'});continue
        before=len(records);walk(data,[],source,records);files.append({'source':source,'records':len(records)-before})
    concepts=load_concepts(); grouped={}; ordinary=[]
    for r in records:
        c=concept_match(r,concepts)
        if c:grouped.setdefault(c['canonical_id'],[]).append(r)
        else:ordinary.append(r)
    consolidated=[]
    for cid,occurrences in grouped.items():
        c=next(v for v in concepts.values() if v['canonical_id']==cid); best=min(occurrences,key=lambda r:(concept_priority(r),r['source'],json.dumps(r['path'],separators=(',',':')))); merged=dict(best)
        merged.update({'id':cid,'name':c.get('term') or best['name'],'description':c.get('definition') or best.get('description',''),'canonical_id':cid,'canonical_concept':True,'source_record_id':best['id'],'occurrence_count':len(occurrences),'occurrences':[{'source':r['source'],'path':r['path'],'id':r['id'],'name':r['name'],'type':r['type']} for r in sorted(occurrences,key=lambda r:(r['source'],json.dumps(r['path'],separators=(',',':'))))]})
        consolidated.append(merged)
    present={r['canonical_id'] for r in consolidated}; registry_by_id={v['canonical_id']:v for v in concepts.values()}
    registry_values=list(registry_by_id.values())
    for cid,c in registry_by_id.items():
        if cid in present:continue
        consolidated.append({'id':cid,'name':c.get('term',cid),'description':c.get('definition',''),'type':c.get('canonical_role','concept'),'layer':'','record_role':'identity-index','owner_family':'potatoism','repository_root':'spirit','repository_layer':'meaning','repository_scale':'concept','classification_basis':'canonical-concept-registry','source':'data/potatoism-concept-registry.json','path':['concepts',next(i for i,x in enumerate(registry_values) if x['canonical_id']==cid)],'canonical_id':cid,'canonical_concept':True,'source_record_id':cid,'occurrence_count':0,'occurrences':[]})
    unique=[];seen=set()
    for r in ordinary+consolidated:
        key=(r['source'],r['id'],json.dumps(r['path'],separators=(',',':')))
        if key not in seen:seen.add(key);unique.append(r)
    unique.sort(key=lambda r:(r['repository_root'],r['repository_layer'],r['name'].casefold(),r['source'],r['id']))
    OUT.write_text(json.dumps({'version':'4.2.0','taxonomy_version':'repository-spine-4.0.0','concept_registry_version':'2.0.0','record_count':len(unique),'raw_record_count':len(records),'consolidated_concept_count':len(consolidated),'file_count':len(files),'json_errors':errors,'files':files,'records':unique},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    counts={r:sum(1 for x in unique if x['repository_root']==r) for r in ('spirit','mind','matter')}
    mind_layers={layer:sum(1 for x in unique if x['repository_root']=='mind' and x['repository_layer']==layer) for layer in ('psychology','hawkinscale','neurobiology')}
    print(f'repository-index: {len(unique)} visible records from {len(records)} raw occurrences, {len(consolidated)} canonical concepts, {len(files)} JSON files, {len(errors)} JSON errors; roots={counts}; mind_layers={mind_layers}')
    for err in errors:
        print(f"JSON ERROR: {err['source']}: {err['error']}")
if __name__=='__main__':main()
