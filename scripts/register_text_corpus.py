import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def repair_profiles_file(name):
    path=ROOT/name
    raw=path.read_text(encoding='utf-8-sig')
    try:
        json.loads(raw)
        print('already valid',name); return
    except json.JSONDecodeError as exc:
        pass
    lines=raw.splitlines()
    start=next((i for i,l in enumerate(lines) if '"profiles":[' in l),None)
    if start is not None:
        # Some legacy exports accidentally closed the profiles array before the
        # final records. Remove only standalone array closers inside that span.
        final=max((i for i,l in enumerate(lines) if l.strip() in (']', '],')), default=-1)
        if final > start:
            lines=lines[:start+1] + [l for l in lines[start+1:final] if l.strip() not in (']', '],')] + lines[final:]
    fixed='\n'.join(lines)+'\n'
    try:
        json.loads(fixed)
    except json.JSONDecodeError as exc:
        print('REPAIR FAILED',name,'line',exc.lineno,'column',exc.colno)
        for i,l in enumerate(fixed.splitlines()[max(0,exc.lineno-3):exc.lineno+1],start=max(0,exc.lineno-2)): print(i+1,repr(l))
        raise
    path.write_text(fixed,encoding='utf-8')
    print('REPAIRED',name)

repair_profiles_file('data/religious-foundations/enriched-records.json')
repair_profiles_file('data/religious-foundations/minor-traditions.json')

for p in ['data/atlas-manifest.json','data/backend-coverage-map.json','data/graph-registry.json']:
    obj=json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
    if p.endswith('atlas-manifest.json'):
        obj['version']='1.11.0'; obj['updated']='2026-09-07'; obj['layers'].setdefault('texts',{'label':'Religious Texts','purpose':'Edition-aware catalogue, locally stored public-domain full texts and concordance/search infrastructure.','files':['data/religious-text-library.json','data/religious-text-corpus.json','data/texts/','religious-texts.html','religious-texts.js']})
        for x in ['data/religious-text-library.json','data/religious-text-corpus.json','data/texts/']:
            if x not in obj['layers']['beliefs']['files']: obj['layers']['beliefs']['files'].append(x)
    elif p.endswith('backend-coverage-map.json'):
        obj['version']='1.2.0'; obj['updated']='2026-09-07'
    else:
        obj['version']='1.3.0'; obj['updated']='2026-09-07'
    (ROOT/p).write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
