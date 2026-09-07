import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8-sig'))

def save(path, obj):
    (ROOT / path).write_text(json.dumps(obj, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

# Repair legacy religious foundation datasets before registering the text layer.
for name in ['data/religious-foundations/enriched-records.json','data/religious-foundations/minor-traditions.json']:
    path = ROOT / name
    raw = path.read_text(encoding='utf-8-sig')
    one = chr(92) + 'n'
    two = chr(92) * 2 + 'n'
    fixed = raw.replace(two, chr(10)).replace(one, chr(10))
    fixed = re.sub(r',([\s]*[}\]])', r'\1', fixed)
    if fixed != raw:
        path.write_text(fixed, encoding='utf-8')
        print('normalized', name)
    with path.open(encoding='utf-8') as f:
        json.load(f)
    print('validated', name)

# Atlas manifest
manifest_path = 'data/atlas-manifest.json'
manifest = load(manifest_path)
manifest['version'] = '1.11.0'
manifest['updated'] = '2026-09-07'
manifest['layers'].setdefault('texts', {
    'label':'Religious Texts',
    'purpose':'Edition-aware catalogue, locally stored public-domain full texts and concordance/search infrastructure.',
    'files':['data/religious-text-library.json','data/religious-text-corpus.json','data/texts/','religious-texts.html','religious-texts.js']
})
belief_files = manifest['layers']['beliefs']['files']
for item in ['data/religious-text-library.json','data/religious-text-corpus.json','data/texts/']:
    if item not in belief_files:
        belief_files.append(item)
save(manifest_path, manifest)

# Backend ownership
coverage_path = 'data/backend-coverage-map.json'
coverage = load(coverage_path)
coverage['version'] = '1.2.0'
coverage['updated'] = '2026-09-07'
existing = {row.get('file') for row in coverage.get('layers', [])}
for row in [
    {'file':'data/religious-text-library.json','owner':'beliefs/sources','consumer':['religious-texts.html','belief.html','node.html','text concordance'],'route':'religious-texts.html','graph_role':'edition-aware text catalogue','status':'canonical'},
    {'file':'data/religious-text-corpus.json','owner':'beliefs/sources','consumer':['religious-texts.html','concordance/search','validators'],'route':'religious-texts.html','graph_role':'full-text availability and edition registry','status':'canonical'},
    {'file':'data/texts/**','owner':'beliefs/sources/full-texts','consumer':['religious-texts.html','concordance/search','future text analyzers'],'route':'religious-texts.html','graph_role':'full-text source corpus','status':'public-domain-source-corpus'},
]:
    if row['file'] not in existing:
        coverage['layers'].append(row)
save(coverage_path, coverage)

# Graph registry
registry_path = 'data/graph-registry.json'
registry = load(registry_path)
registry['version'] = '1.3.0'
registry['updated'] = '2026-09-07'
ids = {row.get('id') for row in registry.get('records', [])}
for row in [
    {'id':'bible-kjv-1611','name':'Bible — King James Version 1611','type':'textual-edition','status':'registry'},
    {'id':'quran-rodwell','name':'The Koran / Qur\'an — Rodwell translation','type':'textual-edition','status':'registry'},
    {'id':'bhagavad-gita-arnold','name':'Bhagavad-Gita — Edwin Arnold translation','type':'textual-edition','status':'registry'},
    {'id':'religious-text-corpus','name':'Religious Text Corpus','type':'textual-corpus','status':'registry'},
]:
    if row['id'] not in ids:
        registry['records'].append(row)
save(registry_path, registry)

print('registered full-text corpus in atlas manifest, backend coverage and graph registry')
