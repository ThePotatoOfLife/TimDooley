from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
search=ROOT/'world-map'/'3d-search.js'
lifecycle=ROOT/'world-map'/'3d-panel-lifecycle.js'
errors=[]
if not search.exists(): errors.append('missing unified search controller')
else:
    text=search.read_text(encoding='utf-8')
    for token in ['3d-search-core.js','__potatoAtlasSearch','__potatoAtlasSubdivisions','__potatoAtlasPlaces','stopImmediatePropagation','world-cities.geo.json','world-subdivisions','Find country, state or city']:
        if token not in text: errors.append(f'search controller missing {token}')
    if 'ready:ensureRecords()' in text: errors.append('search data loads eagerly instead of on first use')
if not lifecycle.exists() or "./3d-search.js" not in lifecycle.read_text(encoding='utf-8'):
    errors.append('search controller is not wired after core paint')
if errors:
    print('WORLD MAP SEARCH VALIDATION FAILED')
    for error in errors: print('-', error)
    sys.exit(1)
print('WORLD MAP SEARCH VALIDATION PASSED')
