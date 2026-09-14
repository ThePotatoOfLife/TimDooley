from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/'world-map'/'3d-places.js'
LIFECYCLE=ROOT/'world-map'/'3d-panel-lifecycle.js'
errors=[]
if not MODULE.exists(): errors.append('missing 3d-places.js')
else:
    text=MODULE.read_text(encoding='utf-8')
    for token in ['world-cities.geo.json','atlas-places','minimum_zoom','place','__potatoAtlasPlaces','potato-atlas-place-select','potato-atlas-places-ready','data-place-country','openCountry','window.goCountry']:
        if token not in text: errors.append(f'places module missing {token}')
if not LIFECYCLE.exists() or "./3d-places.js" not in LIFECYCLE.read_text(encoding='utf-8'):
    errors.append('places lazy loading not registered')
if errors:
    print('WORLD MAP PLACES VALIDATION FAILED')
    for error in errors: print('-', error)
    sys.exit(1)
print('WORLD MAP PLACES VALIDATION PASSED')
