import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

for name in ['data/religious-foundations/enriched-records.json','data/religious-foundations/minor-traditions.json']:
    path = ROOT / name
    raw = path.read_text(encoding='utf-8-sig')
    # These two legacy files contain literal escaped line separators between
    # adjacent records. Repair the exact record boundary before strict parsing.
    fixed, substitutions = re.subn(r'},\\+n(\s*{)', '},\n\\1', raw)
    fixed, substitutions2 = re.subn(r'},\\\\+n(\s*{)', '},\n\\1', fixed)
    fixed = re.sub(r',([\s]*[}\]])', r'\1', fixed)
    print(name, 'record-boundary repairs:', substitutions + substitutions2)
    if fixed != raw:
        path.write_text(fixed, encoding='utf-8')
    with path.open(encoding='utf-8') as f:
        json.load(f)
    print('validated', name)

# Atlas manifest
manifest_path = 'data/atlas-manifest.json'
manifest = load(manifest_path) if False else json.loads((ROOT / manifest_path).read_text(encoding='utf-8-sig'))
manifest['version'] = '1.11.0'; manifest['updated'] = '2026-09-07'
manifest['layers'].setdefault('texts', {'label':'Religious Texts','purpose':'Edition-aware catalogue, locally stored public-domain full texts and concordance/search infrastructure.','files':['data/religious-text-library.json','data/religious-text-corpus.json','data/texts/','religious-texts.html','religious-texts.js']})
for item in ['data/religious-text-library.json','data/religious-text-corpus.json','data/texts/']:
    if item not in manifest['layers']['beliefs']['files']: manifest['layers']['beliefs']['files'].append(item)
(ROOT / manifest_path).write_text(json.dumps(manifest, ensure_ascii=False, separators=(',',':')), encoding='utf-8')

coverage_path='data/backend-coverage-map.json'; coverage=json.loads((ROOT/coverage_path).read_text(encoding='utf-8-sig')); coverage['version']='1.2.0'; coverage['updated']='2026-09-07'; existing={r.get('file') for r in coverage.get('layers',[])}
for row in [
 {'file':'data/religious-text-library.json','owner':'beliefs/sources','consumer':['religious-texts.html','belief.html','node.html','text concordance'],'route':'religious-texts.html','graph_role':'edition-aware text catalogue','status':'canonical'},
 {'file':'data/religious-text-corpus.json','owner':'beliefs/sources','consumer':['religious-texts.html','concordance/search','validators'],'route':'religious-texts.html','graph_role':'full-text availability and edition registry','status':'canonical'},
 {'file':'data/texts/**','owner':'beliefs/sources/full-texts','consumer':['religious-texts.html','concordance/search','future text analyzers'],'route':'religious-texts.html','graph_role':'full-text source corpus','status':'public-domain-source-corpus'}]:
    if row['file'] not in existing: coverage['layers'].append(row)
(ROOT/coverage_path).write_text(json.dumps(coverage,ensure_ascii=False,separators=(',',':')),encoding='utf-8')

registry_path='data/graph-registry.json'; registry=json.loads((ROOT/registry_path).read_text(encoding='utf-8-sig')); registry['version']='1.3.0'; registry['updated']='2026-09-07'; ids={r.get('id') for r in registry.get('records',[])}
for row in [
 {'id':'bible-kjv-1611','name':'Bible — King James Version 1611','type':'textual-edition','status':'registry'},
 {'id':'quran-rodwell','name':"The Koran / Qur'an — Rodwell translation",'type':'textual-edition','status':'registry'},
 {'id':'bhagavad-gita-arnold','name':'Bhagavad-Gita — Edwin Arnold translation','type':'textual-edition','status':'registry'},
 {'id':'religious-text-corpus','name':'Religious Text Corpus','type':'textual-corpus','status':'registry'}]:
    if row['id'] not in ids: registry['records'].append(row)
(ROOT/registry_path).write_text(json.dumps(registry,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
print('registered full-text corpus')
