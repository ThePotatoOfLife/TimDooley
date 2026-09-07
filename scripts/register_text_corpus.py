import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def repair(name):
    p=ROOT/name
    raw=p.read_text(encoding='utf-8-sig')
    fixed=raw.replace(chr(92)+"'", "'")
    if fixed!=raw: p.write_text(fixed,encoding='utf-8')
    with p.open(encoding='utf-8') as f: json.load(f)
    print('VALID JSON',name)

repair('data/religious-foundations/enriched-records.json')
repair('data/religious-foundations/minor-traditions.json')

for p in ['data/atlas-manifest.json','data/backend-coverage-map.json','data/graph-registry.json']:
    path=ROOT/p; obj=json.loads(path.read_text(encoding='utf-8-sig'))
    if p.endswith('atlas-manifest.json'):
        obj['version']='1.11.0'; obj['updated']='2026-09-07'; obj['layers'].setdefault('texts',{'label':'Religious Texts','purpose':'Edition-aware catalogue, locally stored public-domain full texts and concordance/search infrastructure.','files':['data/religious-text-library.json','data/religious-text-corpus.json','data/texts/','religious-texts.html','religious-texts.js']})
        for x in ['data/religious-text-library.json','data/religious-text-corpus.json','data/texts/']:
            if x not in obj['layers']['beliefs']['files']: obj['layers']['beliefs']['files'].append(x)
    elif p.endswith('backend-coverage-map.json'): obj['version']='1.2.0'; obj['updated']='2026-09-07'
    else: obj['version']='1.3.0'; obj['updated']='2026-09-07'
    path.write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
