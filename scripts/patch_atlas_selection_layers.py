#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path, old, new):
    p = ROOT / path
    text = p.read_text(encoding='utf-8')
    if new in text:
        return False
    if old not in text:
        raise SystemExit(f'Expected patch marker missing in {path}: {old[:100]!r}')
    p.write_text(text.replace(old, new, 1), encoding='utf-8')
    return True


def regex_once(path, pattern, replacement):
    p = ROOT / path
    text = p.read_text(encoding='utf-8')
    out, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count == 0:
        if replacement.strip() in text:
            return False
        raise SystemExit(f'Expected regex patch marker missing in {path}: {pattern[:100]!r}')
    p.write_text(out, encoding='utf-8')
    return True

# Core selection semantics: selection is quiet, repeat-click clears it, and
# analytical overlays do not appear until the user asks for them.
replace_once('world-map/3d-app.js',
             'let showInterior = true;\nlet showRelations = true;',
             'let showInterior = false;\nlet showRelations = false;')

old_select = '''async function selectFeature(f,fly=false){
  const code=f.properties.iso3;if(!code)return;
  if(compareMode)return toggleCompareCountry(code);
  if(selected)setState(selected,'selected',false);
  selected=code;selectedFeature=f;setState(code,'selected',true);currentCanonical=await loadCanonical(code);updateSpatial();updateUrl();if(fly)fitCodes([code]);renderCountry();
}'''
new_select = '''function selectionDetail(reason='selection'){
  const r=selected?by3[selected]:null;
  return {reason,code:selected,name:r?.name?.common||selected||null,selected:Boolean(selected),compareMode};
}
function emitSelectionChange(reason='selection'){
  window.dispatchEvent(new CustomEvent('potato-atlas-selection-change',{detail:selectionDetail(reason)}));
}
function deselectCountry({keepView=true,clearCompare=false}={}){
  if(selected)setState(selected,'selected',false);
  selected=null;selectedFeature=null;currentCanonical=null;
  if(clearCompare){clearCompareStates();compareCodes=[];compareMode=false;$('#compare').classList.remove('active')}
  updateSpatial();updateUrl();
  $('#panel').innerHTML='<div class="eyebrow">World mode</div><h1>World Relational Atlas</h1><p class="muted">Select a country to reveal its stable action dock. Detailed country modules stay off-map until requested.</p>';
  if(!keepView)map.easeTo({center:[5,24],zoom:1.5,pitch:0,bearing:0,duration:650});
  emitSelectionChange('cleared');
}
async function selectFeature(f,fly=false,{toggle=false}={}){
  const code=f.properties.iso3;if(!code)return;
  if(compareMode)return toggleCompareCountry(code);
  if(toggle&&selected===code){deselectCountry({keepView:true});return}
  if(selected)setState(selected,'selected',false);
  selected=code;selectedFeature=f;setState(code,'selected',true);currentCanonical=await loadCanonical(code);updateSpatial();updateUrl();if(fly)fitCodes([code]);renderCountry();emitSelectionChange('selected');
}
window.__potatoAtlasSelection={
  get current(){return selectionDetail('read')},
  clear(){deselectCountry({keepView:true})},
  focus(){window.fitCountry?.()},
  inspect(){window.showOverview?.()},
};
window.clearCountrySelection=()=>deselectCountry({keepView:true});'''
replace_once('world-map/3d-app.js', old_select, new_select)

replace_once('world-map/3d-app.js',
             "function resetWorld(clearCompare=true){if(selected)setState(selected,'selected',false);selected=null;selectedFeature=null;currentCanonical=null;if(clearCompare){clearCompareStates();compareCodes=[];compareMode=false;$('#compare').classList.remove('active')}updateSpatial();updateUrl();map.easeTo({center:[5,24],zoom:1.5,pitch:0,bearing:0,duration:650});$('#panel').innerHTML='<div class=\"eyebrow\">World mode</div><h1>World Relational Atlas</h1><p class=\"muted\">Search, compare, recursively trace typed relations, rotate and select a polygon to unfold its canonical data modules.</p>'}",
             "function resetWorld(clearCompare=true){deselectCountry({keepView:false,clearCompare})}")

replace_once('world-map/3d-app.js',
             "map.on('load',async()=>{\n  addLayers();populateControls();",
             "function claimOverlayClick(event){if(event?.originalEvent)event.originalEvent.__potatoAtlasOverlayHandled=true}\nfunction handleCountryPolygonClick(event){\n  const feature=event.features?.[0];if(!feature)return;\n  const originalEvent=event.originalEvent;\n  queueMicrotask(()=>{if(originalEvent?.__potatoAtlasOverlayHandled)return;selectFeature(feature,false,{toggle:true})});\n}\n\nmap.on('load',async()=>{\n  addLayers();populateControls();\n  $('#interior').classList.toggle('active',showInterior);\n  $('#relations').classList.toggle('active',showRelations);")
replace_once('world-map/3d-app.js',
             "  map.on('click','countries-fill',e=>e.features?.[0]&&selectFeature(e.features[0],false));\n  map.on('click','countries-extrude',e=>e.features?.[0]&&selectFeature(e.features[0],false));\n  map.on('click','country-hubs',e=>{const code=e.features?.[0]?.properties?.iso3,f=featureByCode(code);if(f)selectFeature(f,false)});\n  map.on('click','semantic-hubs',e=>{const f=e.features?.[0];if(f)window.openModule(f.properties.id)});\n  map.on('click','trace-hubs',e=>{const code=e.features?.[0]?.properties?.iso3;if(code)window.goCountry(code)});\n  map.on('click','relations',clickRelation);",
             "  map.on('click','countries-fill',handleCountryPolygonClick);\n  map.on('click','countries-extrude',handleCountryPolygonClick);\n  map.on('click','country-hubs',e=>{claimOverlayClick(e);const code=e.features?.[0]?.properties?.iso3,f=featureByCode(code);if(f)selectFeature(f,false)});\n  map.on('click','semantic-hubs',e=>{claimOverlayClick(e);const f=e.features?.[0];if(f)window.openModule(f.properties.id)});\n  map.on('click','trace-hubs',e=>{claimOverlayClick(e);const code=e.features?.[0]?.properties?.iso3;if(code)window.goCountry(code)});\n  map.on('click','relations',e=>{claimOverlayClick(e);clickRelation(e)});")
replace_once('world-map/3d-app.js',
             "$('#interior').onclick=()=>{showInterior=!showInterior;$('#interior').classList.toggle('active',showInterior);updateSpatial()};\n$('#relations').onclick=()=>{showRelations=!showRelations;$('#relations').classList.toggle('active',showRelations);updateSpatial()};",
             "$('#interior').onclick=()=>{showInterior=!showInterior;$('#interior').classList.toggle('active',showInterior);updateSpatial();if(showInterior&&selected&&map.getZoom()<3.2)fitCodes([selected],78);window.dispatchEvent(new CustomEvent('potato-atlas-interior-change',{detail:{visible:showInterior}}))};\n$('#relations').onclick=()=>{showRelations=!showRelations;$('#relations').classList.toggle('active',showRelations);updateSpatial();window.dispatchEvent(new CustomEvent('potato-atlas-relations-change',{detail:{visible:showRelations}}))};")

# Quiet selection: the country panel may be rendered in the background, but it
# no longer forces itself open. The selection dock becomes the stable first action surface.
replace_once('world-map/3d-ui.js',
             "  if (persist) localStorage.setItem('atlas:panel-open', open ? '1' : '0');\n}",
             "  if (persist) localStorage.setItem('atlas:panel-open', open ? '1' : '0');\n  window.dispatchEvent(new CustomEvent('potato-atlas-panel-change',{detail:{open}}));\n}")
replace_once('world-map/3d-ui.js',
             "  const isLanding = /Explore the world/.test(signature);\n  if (!isLanding) setPanel(true, {persist:false});",
             "  const passiveSelection = /Canonical country|Territory \/ map polygon|World Relational Atlas/.test(signature);\n  const isLanding = /Explore the world/.test(signature);\n  if (!isLanding && !passiveSelection) setPanel(true, {persist:false});")

regex_once('world-map/3d-ui.js',
           r"function updateLayerSummary\(\)\{.*?\n\}",
           '''function updateLayerSummary(){
  const capitals=document.getElementById('capitals');
  const field=document.getElementById('axisFieldView')?.value;
  const network=document.getElementById('empiricalNetworkView')?.value;
  const active=[];
  if(capitals&&!capitals.classList.contains('active'))active.push('capitals off');
  if(field&&field!=='all'&&field!=='off')active.push(field==='brics'?'BRICS':field[0].toUpperCase()+field.slice(1));
  if(network&&network!=='off')active.push(network.replaceAll('_',' '));
  summaryText('layersMenu',active.length?`Map · ${active.slice(0,2).join(' + ')}${active.length>2?'…':''}`:'Map',active.length>0);
}''')
regex_once('world-map/3d-ui.js',
           r"function updateTraceSummary\(\)\{.*?\n\}",
           '''function updateTraceSummary(){
  const depth=Number(document.getElementById('traceDepth')?.value||1);
  const entity=document.getElementById('entityTraceToggle')?.classList.contains('active');
  const compare=document.getElementById('compare')?.classList.contains('active');
  const relations=document.getElementById('relations')?.classList.contains('active');
  const relation=document.getElementById('relationType')?.value||'all';
  const parts=[];if(compare)parts.push('compare');if(relations)parts.push('connections');if(relation!=='all')parts.push('filtered');if(depth>1)parts.push(`${depth} hops`);if(entity)parts.push('entities');
  summaryText('traceMenu',parts.length?`Analyze · ${parts.slice(0,3).join(' + ')}${parts.length>3?'…':''}`:'Analyze',parts.length>0);
}''')
replace_once('world-map/3d-ui.js',
             "  if(['relationType','axisFieldView','empiricalNetworkView','traceDepth','height','timeMode','timeDate','timeDate2'].includes(event.target?.id))queueMicrotask(updateMenuSummaries);",
             "  if(['relationType','axisFieldView','empiricalNetworkView','traceDepth','height','timeMode','timeDate','timeDate2'].includes(event.target?.id))queueMicrotask(updateMenuSummaries);")
replace_once('world-map/3d-ui.js',
             "  if(['entityTraceToggle','compare'].includes(event.target?.id))queueMicrotask(updateTraceSummary);",
             "  if(['entityTraceToggle','compare','relations'].includes(event.target?.id))queueMicrotask(updateTraceSummary);")
replace_once('world-map/3d-ui.js',
             "  if(compare&&tracePop){\n    compare.textContent='Compare countries';\n    const title=tracePop.querySelector('.menu-title');\n    if(title)title.after(compare);else tracePop.prepend(compare);\n  }",
             "  if(compare&&tracePop){\n    compare.textContent='Compare countries';\n    const title=tracePop.querySelector('.menu-title');\n    if(title)title.after(compare);else tracePop.prepend(compare);\n  }\n  const relations=document.getElementById('relations');\n  const relationType=document.getElementById('relationType');\n  if(relations&&tracePop){relations.textContent='Country connections';compare?.after(relations)}\n  if(relationType&&tracePop){relations?.after(relationType)}")
replace_once('world-map/3d-ui.js',
             "  const interior=document.getElementById('interior');\n  if(interior?.classList.contains('active'))interior.click();",
             "  const interior=document.getElementById('interior');\n  if(interior){interior.textContent='Module orbit · advanced';interior.title='Optional on-map semantic navigation. The stable selection dock is the primary country interface.'}")

# Capital cities become a first-class build artifact, independent of whether the
# REST Countries runtime snapshot happened to succeed on that deployment.
replace_once('world-map/3d-hover.js',
             "const REST_LOCAL = '../data/rest-countries-runtime.json';",
             "const REST_LOCAL = '../data/rest-countries-runtime.json';\nconst CAPITALS_LOCAL = '../data/world-capitals.geo.json';")
regex_once('world-map/3d-hover.js',
           r"async function loadCapitals\(\) \{.*?\n\}\n\nfunction countryHtml",
           '''async function loadCapitals() {
  const response = await fetchJsonResponse(CAPITALS_LOCAL, { cache: 'force-cache' });
  const payload = await response.json();
  if (payload?.type !== 'FeatureCollection' || !Array.isArray(payload.features)) throw new Error('Local capital snapshot has invalid shape.');
  return payload;
}

function countryHtml''')
replace_once('world-map/3d-hover.js',
             "  for (const id of ['capital-cities', 'capital-city-labels']) {",
             "  for (const id of ['capital-cities', 'capital-city-major-labels', 'capital-city-labels']) {")
replace_once('world-map/3d-hover.js',
             "    if (!map.getLayer('capital-city-labels')) map.addLayer({",
             "    if (!map.getLayer('capital-city-major-labels')) map.addLayer({\n      id: 'capital-city-major-labels', type: 'symbol', source: 'capital-cities', minzoom: 1.1, maxzoom: 3.4,\n      filter: ['<=', ['get', 'scalerank'], 2],\n      layout: {\n        'text-field': ['get', 'name'], 'text-size': 9, 'text-offset': [0, 1.05],\n        'text-anchor': 'top', 'text-allow-overlap': false, 'text-optional': true\n      },\n      paint: { 'text-color': '#f0d98f', 'text-halo-color': '#080b0b', 'text-halo-width': 1.1 }\n    });\n    if (!map.getLayer('capital-city-labels')) map.addLayer({")
replace_once('world-map/3d-hover.js',
             "    map.on('click', 'capital-cities', event => {\n      const code = event.features?.[0]?.properties?.iso3;",
             "    map.on('click', 'capital-cities', event => {\n      if(event?.originalEvent)event.originalEvent.__potatoAtlasOverlayHandled=true;\n      const code = event.features?.[0]?.properties?.iso3;")

# Load the new stable selection/layer controller after the existing progressive UI.
replace_once('world-map/3d-bootstrap.js',
             "  await loadAfterPaint('Progressive UI', './3d-ui.js');",
             "  await loadAfterPaint('Progressive UI', './3d-ui.js');\n  await loadAfterPaint('Selection UI', './3d-selection-ui.js');")

# Publish-time capital snapshot: pinned Natural Earth is primary; the optional
# REST snapshot is only a fallback. If neither yields adequate coverage, fail the
# new deployment and preserve the last known-good Pages release.
replace_once('.github/workflows/pages.yml',
             "          test -s _site/data/world-countries.geo.json\n\n          if ! curl -fsSL --retry 3 --retry-delay 1 \\",
             "          test -s _site/data/world-countries.geo.json\n\n          if ! curl -fsSL --retry 3 --retry-delay 1 \\\n            https://raw.githubusercontent.com/nvkelso/natural-earth-vector/ca96624a56bd078437bca8184e78163e5039ad19/geojson/ne_110m_populated_places_simple.geojson \\\n            -o /tmp/natural-earth-capitals.geojson; then\n            rm -f /tmp/natural-earth-capitals.geojson\n            echo 'Pinned Natural Earth capital snapshot unavailable; REST fallback will be attempted.'\n          fi\n\n          if ! curl -fsSL --retry 3 --retry-delay 1 \\")
replace_once('.github/workflows/pages.yml',
             "          PY\n\n      - name: Build population and religion snapshot",
             "          PY\n\n          python - <<'PY'\n          import json\n          from pathlib import Path\n\n          natural = Path('/tmp/natural-earth-capitals.geojson')\n          rest_path = Path('_site/data/rest-countries-runtime.json')\n          features = []\n          source = None\n\n          if natural.exists():\n              payload = json.loads(natural.read_text(encoding='utf-8'))\n              for feature in payload.get('features', []):\n                  props = feature.get('properties') or {}\n                  if not (props.get('adm0cap') == 1 or props.get('capalt') == 1):\n                      continue\n                  code = props.get('adm0_a3') or props.get('sov_a3')\n                  coords = (feature.get('geometry') or {}).get('coordinates')\n                  if not code or not isinstance(coords, list) or len(coords) != 2:\n                      continue\n                  features.append({\n                      'type': 'Feature',\n                      'properties': {\n                          'iso3': code,\n                          'name': props.get('name') or props.get('nameascii') or code,\n                          'country': props.get('adm0name') or props.get('sov0name') or '',\n                          'scalerank': int(props.get('scalerank') or 9),\n                          'primary': props.get('adm0cap') == 1,\n                          'source': 'Natural Earth 1:110m populated places (pinned)',\n                      },\n                      'geometry': {'type': 'Point', 'coordinates': [float(coords[0]), float(coords[1])]},\n                  })\n              source = 'Natural Earth'\n\n          if len(features) < 150 and rest_path.exists():\n              features = []\n              rows = json.loads(rest_path.read_text(encoding='utf-8'))\n              for row in rows:\n                  name = (row.get('capital') or [None])[0]\n                  latlng = (row.get('capitalInfo') or {}).get('latlng') or []\n                  if not row.get('cca3') or not name or len(latlng) != 2:\n                      continue\n                  features.append({\n                      'type': 'Feature',\n                      'properties': {\n                          'iso3': row['cca3'], 'name': name, 'country': (row.get('name') or {}).get('common',''),\n                          'scalerank': 5, 'primary': True, 'source': 'REST Countries deploy fallback',\n                      },\n                      'geometry': {'type': 'Point', 'coordinates': [float(latlng[1]), float(latlng[0])]},\n                  })\n              source = 'REST Countries fallback'\n\n          assert len(features) >= 150, f'capital coverage too low: {len(features)}'\n          out = {'type': 'FeatureCollection', 'name': 'world-capitals', 'features': features}\n          Path('_site/data/world-capitals.geo.json').write_text(json.dumps(out, separators=(',',':')), encoding='utf-8')\n          print(f'Built local capital snapshot: {len(features)} points from {source}')\n          PY\n\n      - name: Build population and religion snapshot")
replace_once('.github/workflows/pages.yml',
             "          test -s _site/data/world-countries.geo.json",
             "          test -s _site/data/world-countries.geo.json\n          test -s _site/data/world-capitals.geo.json")

# Extend the source validator around the newly explicit selection/layer contracts.
replace_once('scripts/validate_world_map_3d.py',
             "UI = ROOT / \"world-map\" / \"3d-ui.js\"",
             "UI = ROOT / \"world-map\" / \"3d-ui.js\"\nSELECTION_UI = ROOT / \"world-map\" / \"3d-selection-ui.js\"")
replace_once('scripts/validate_world_map_3d.py',
             "for path in (HTML, APP, HOVER, BOOTSTRAP, EVIDENCE, UI, TIME, FIELDS, NETWORKS, RUNTIME, WORLD, COUNTRIES):",
             "for path in (HTML, APP, HOVER, BOOTSTRAP, EVIDENCE, UI, SELECTION_UI, TIME, FIELDS, NETWORKS, RUNTIME, WORLD, COUNTRIES):")
replace_once('scripts/validate_world_map_3d.py',
             "    ui = UI.read_text(encoding=\"utf-8\", errors=\"replace\")",
             "    ui = UI.read_text(encoding=\"utf-8\", errors=\"replace\")\n    selection_ui = SELECTION_UI.read_text(encoding=\"utf-8\", errors=\"replace\")")
replace_once('scripts/validate_world_map_3d.py',
             "fail_if_missing(ui,(\"function setPanel\"",
             "fail_if_missing(selection_ui,(\"atlasSelectionDock\",\"__potatoAtlasLayerRegistry\",\"potato-atlas-selection-change\",\"Module orbit · advanced\",\"Connections\",\"clearCountrySelection\"),\"world-map/3d-selection-ui.js\",errors)\n    fail_if_missing(ui,(\"function setPanel\"")
replace_once('scripts/validate_world_map_3d.py',
             "\"function toggleCompareCountry\",\"function selectFeature\",",
             "\"function toggleCompareCountry\",\"function deselectCountry\",\"function selectFeature\",\"__potatoAtlasSelection\",\"potato-atlas-selection-change\",\"__potatoAtlasOverlayHandled\",")
replace_once('scripts/validate_world_map_3d.py',
             "\"capitalInfo\",\"REST Countries deploy snapshot\",\"installCapitalsWhenUseful\",\"capital-cities\",\"capital-city-labels\"",
             "\"CAPITALS_LOCAL\",\"world-capitals.geo.json\",\"installCapitalsWhenUseful\",\"capital-cities\",\"capital-city-major-labels\",\"capital-city-labels\"")
replace_once('scripts/validate_world_map_3d.py',
             "for text,label in ((app,\"3d-app.js\"),(hover,\"3d-hover.js\"),(bootstrap,\"3d-bootstrap.js\"),(evidence,\"3d-evidence.js\"),(ui,\"3d-ui.js\"),(time_js,\"3d-time.js\"),(fields,\"3d-fields.js\"),(networks,\"3d-networks.js\")):",
             "for text,label in ((app,\"3d-app.js\"),(hover,\"3d-hover.js\"),(bootstrap,\"3d-bootstrap.js\"),(evidence,\"3d-evidence.js\"),(ui,\"3d-ui.js\"),(selection_ui,\"3d-selection-ui.js\"),(time_js,\"3d-time.js\"),(fields,\"3d-fields.js\"),(networks,\"3d-networks.js\")):")

print('Atlas selection/layer patches applied.')
