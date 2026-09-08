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
SKIP = {'repository-index.json'}

def scalar(v):
    return v if isinstance(v,(str,int,float,bool)) else ''

def first(o, keys):
    for k in keys:
        v = scalar(o.get(k))
        if str(v).strip(): return str(v).strip()
    return ''

def walk(v, path, source, out):
    if isinstance(v, dict):
        ident = first(v, ID_KEYS)
        name = first(v, NAME_KEYS)
        if ident and (name or v.get('type') or v.get('kind') or v.get('category')):
            out.append({'id':ident,'name':name or ident,'description':first(v,DESC_KEYS)[:1000],
                        'type':str(v.get('type') or v.get('kind') or v.get('category') or ''),
                        'layer':str(v.get('layer') or ''),'source':source,'path':path})
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
    unique.sort(key=lambda r:(r['name'].casefold(),r['source'],r['id']))
    OUT.write_text(json.dumps({'version':'1.0.0','record_count':len(unique),'file_count':len(files),'json_errors':errors,'files':files,'records':unique},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'repository-index: {len(unique)} records, {len(files)} JSON files, {len(errors)} JSON errors')
    # A bad optional data file must never make the entire static site disappear.
    return 0

if __name__ == '__main__': raise SystemExit(main())
