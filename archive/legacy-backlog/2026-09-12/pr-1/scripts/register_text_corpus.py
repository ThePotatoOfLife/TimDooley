import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def repair(name):
    p=ROOT/name
    raw=p.read_text(encoding='utf-8-sig')
    fixed=raw.replace('\\\\n','\n').replace('\\n','\n')
    if fixed != raw:
        p.write_text(fixed,encoding='utf-8')
        raw=fixed
    try:
        json.loads(raw)
        print('VALID JSON',name)
        return
    except json.JSONDecodeError:
        pass
    lines=raw.splitlines()
    records=[]
    for line in lines:
        s=line.strip()
        if not s.startswith('{'): continue
        if s.endswith(','): s=s[:-1]
        try: records.append(json.loads(s))
        except json.JSONDecodeError: continue
    if not records:
        raise RuntimeError(f'could not recover records from {name}')
    version='2.0.0'; updated='2026-09-07'; purpose='Deep comparative records for the religious atlas.'; source_method=''
    for line in lines[:12]:
        if '"version"' in line: version=line.split('"version":',1)[1].split(',',1)[0].strip().strip('"')
        if '"updated"' in line: updated=line.split('"updated":',1)[1].split(',',1)[0].strip().strip('"')
        if '"purpose"' in line: purpose=line.split('"purpose":',1)[1].rsplit('"',1)[0].strip().lstrip('"')
        if '"source_method"' in line: source_method=line.split('"source_method":',1)[1].rsplit('"',1)[0].strip().lstrip('"')
    out={'version':version,'updated':updated,'purpose':purpose}
    if 'minor-traditions' in name: out['traditions']=records
    else: out['source_method']=source_method; out['profiles']=records
    p.write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    json.loads(p.read_text(encoding='utf-8'))
    print('REPAIRED',name,'records=',len(records))

repair('data/religious-foundations/enriched-records.json')
repair('data/religious-foundations/minor-traditions.json')

for p in ['data/atlas-manifest.json','data/backend-coverage-map.json','data/graph-registry.json']:
    path=ROOT/p; obj=json.loads(path.read_text(encoding='utf-8-sig'))
    if p.endswith('atlas-manifest.json'):
        obj['version']='1.11.0'; obj['updated']='2026-09-07'
        obj['layers'].setdefault('texts',{'label':'Religious Texts','purpose':'Edition-aware catalogue, locally stored public-domain full texts and concordance/search infrastructure.','files':['data/religious-text-library.json','data/religious-text-corpus.json','data/texts/','religious-texts.html','religious-texts.js']})
    elif p.endswith('backend-coverage-map.json'):
        obj['version']='1.2.0'; obj['updated']='2026-09-07'
    else:
        obj['version']='1.3.0'; obj['updated']='2026-09-07'
    path.write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
