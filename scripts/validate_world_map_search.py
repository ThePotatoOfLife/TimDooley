from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
search=ROOT/'world-map'/'3d-search.js'
html=ROOT/'world-map'/'index.html'
boot=ROOT/'world-map'/'3d-bootstrap.js'
errors=[]
if not search.exists(): errors.append('missing unified search controller')
else:
    text=search.read_text(encoding='utf-8')
    for token in ['3d-search-core.js','__potatoAtlasSearch','__potatoAtlasSubdivisions','__potatoAtlasPlaces','stopImmediatePropagation','world-cities.geo.json','world-subdivisions']:
        if token not in text: errors.append(f'search controller missing {token}')
if not html.exists() or 'Find country, state or city' not in html.read_text(encoding='utf-8'):
    errors.append('search copy not upgraded')
if not boot.exists() or "./3d-search.js" not in boot.read_text(encoding='utf-8'):
    errors.append('search bootstrap not wired')
if errors:
    print('WORLD MAP SEARCH VALIDATION FAILED')
    for error in errors: print('-', error)
    sys.exit(1)
print('WORLD MAP SEARCH VALIDATION PASSED')
