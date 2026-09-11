import * as maplibregl from 'https://unpkg.com/maplibre-gl@6.9.0/dist/maplibre-gl.mjs';

// Country-demography facet overlay for the D4 geographic atlas.
//
// This is deliberately separate from the country inspector: the inspector shows
// one country's composition, while this module lets the same sourced observation
// become a world-map percentage layer. It does not infer belief, practice,
// political behavior or moral character from religious identity.

const DEMOGRAPHY_URL = '../data/world-country-demography.json';
const GEO_URL = '../data/world-countries.geo.json';
const SOURCE_ID = 'demography-facet-countries';
const FILL_ID = 'demography-facet-fill';
const LINE_ID = 'demography-facet-line';
const CONTROL_ID = 'religionFacetView';
const LEGEND_ID = 'religionFacetLegend';
const DEFAULT_VIEW = 'off';

const FACETS = {
  christian: { label: 'Christian', color: '#d7b66f' },
  muslim: { label: 'Muslim', color: '#79aa80' },
  hindu: { label: 'Hindu', color: '#d49369' },
  buddhist: { label: 'Buddhist', color: '#c7a86d' },
  jewish: { label: 'Jewish', color: '#75a6d6' },
  other_religions: { label: 'Other religions', color: '#a687bd' },
  unaffiliated: { label: 'Unaffiliated / no religion', color: '#899398' },
};

const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'
}[char]));

let activeFacet = DEFAULT_VIEW;
let historicalSuppressed = false;
let installedMap = null;
let installedData = null;
let popup = null;

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${url} returned HTTP ${response.status}`);
  return response.json();
}

function enrichGeoJSON(geo, data) {
  for (const feature of geo.features || []) {
    const code = String(feature.id || feature.properties?.iso3 || feature.properties?.id || '').toUpperCase();
    const composition = data.countries?.[code]?.religion?.composition || {};
    feature.properties = { ...(feature.properties || {}), iso3: code };
    for (const key of Object.keys(FACETS)) {
      const value = Number(composition[key]);
      feature.properties[`religion_${key}`] = Number.isFinite(value) ? value : -1;
    }
  }
  return geo;
}

function facetProperty(key) {
  return `religion_${key}`;
}

function facetFilter(key) {
  return ['>=', ['get', facetProperty(key)], 0];
}

function opacityExpression(key) {
  return [
    'interpolate', ['linear'], ['get', facetProperty(key)],
    0, .035,
    10, .10,
    25, .20,
    50, .34,
    75, .47,
    100, .60,
  ];
}

function lineOpacityExpression(key) {
  return [
    'interpolate', ['linear'], ['get', facetProperty(key)],
    0, .05,
    25, .20,
    50, .36,
    75, .52,
    100, .70,
  ];
}

function addLayers(map, geo, data) {
  if (map.getSource(SOURCE_ID)) return;
  map.addSource(SOURCE_ID, { type:'geojson', data: enrichGeoJSON(geo, data) });
  const before = map.getLayer('countries-line') ? 'countries-line' : undefined;
  map.addLayer({
    id:FILL_ID,
    type:'fill',
    source:SOURCE_ID,
    layout:{ visibility:'none' },
    filter:['==', ['get','iso3'], '__NONE__'],
    paint:{ 'fill-color':'#899398', 'fill-opacity':0 },
  }, before);
  map.addLayer({
    id:LINE_ID,
    type:'line',
    source:SOURCE_ID,
    layout:{ visibility:'none' },
    filter:['==', ['get','iso3'], '__NONE__'],
    paint:{ 'line-color':'#899398', 'line-opacity':0, 'line-width':['interpolate',['linear'],['zoom'],0,.35,4,.8,7,1.25] },
  }, before);
}

function historicalAllowed() {
  const state = window.__potatoAtlasTime?.getState?.();
  if (!state || state.mode === 'current') return true;
  // Religion snapshot is explicitly a 2020 estimate. Only an exact 2020 As-of
  // view may render it as the active map surface; otherwise leave it as inspector
  // context so a dated observation is not silently projected across time.
  return state.mode === 'as_of' && String(state.time || '').startsWith('2020');
}

function setHistoricalSuppressed() {
  historicalSuppressed = !historicalAllowed();
  const control = document.getElementById(CONTROL_ID);
  if (control) {
    control.disabled = historicalSuppressed;
    control.title = historicalSuppressed
      ? '2020 religion identity layer is hidden outside Current or an exact 2020 As-of view'
      : 'Map a sourced 2020 religious-identity percentage across countries';
  }
  if (historicalSuppressed && installedMap) {
    installedMap.setLayoutProperty(FILL_ID, 'visibility', 'none');
    installedMap.setLayoutProperty(LINE_ID, 'visibility', 'none');
  } else if (installedMap && installedData) {
    applyFacet(installedMap, installedData, activeFacet, { writeUrl:false });
  }
  updateLegend();
}

function updateLegend() {
  let legend = document.getElementById(LEGEND_ID);
  if (!legend) {
    const wrap = document.querySelector('.mapwrap');
    if (!wrap) return;
    legend = document.createElement('div');
    legend.id = LEGEND_ID;
    legend.style.cssText = 'position:absolute;left:12px;bottom:46px;z-index:3;background:#080b0be8;border:1px solid #283333;border-radius:9px;padding:7px 9px;font-size:10px;max-width:310px;pointer-events:none';
    wrap.appendChild(legend);
  }
  const facet = FACETS[activeFacet];
  legend.hidden = !facet || historicalSuppressed;
  if (!facet) return;
  legend.innerHTML = `<div style="display:flex;align-items:center;gap:7px"><i style="display:inline-block;width:11px;height:11px;border-radius:3px;background:${esc(facet.color)}"></i><b>${esc(facet.label)} · 2020 share</b></div><div style="margin-top:4px;color:#aab4aa">Opacity = percent of population · 0 → 100%. Identity estimate, not belief intensity, practice or political behavior.</div>`;
}

function applyFacet(map, data, key, { writeUrl=true } = {}) {
  activeFacet = FACETS[key] ? key : DEFAULT_VIEW;
  const visible = activeFacet !== DEFAULT_VIEW && !historicalSuppressed;
  for (const id of [FILL_ID, LINE_ID]) {
    if (map.getLayer(id)) map.setLayoutProperty(id, 'visibility', visible ? 'visible' : 'none');
  }
  if (visible) {
    const facet = FACETS[activeFacet];
    map.setFilter(FILL_ID, facetFilter(activeFacet));
    map.setFilter(LINE_ID, facetFilter(activeFacet));
    map.setPaintProperty(FILL_ID, 'fill-color', facet.color);
    map.setPaintProperty(FILL_ID, 'fill-opacity', opacityExpression(activeFacet));
    map.setPaintProperty(LINE_ID, 'line-color', facet.color);
    map.setPaintProperty(LINE_ID, 'line-opacity', lineOpacityExpression(activeFacet));
  }
  if (writeUrl) {
    const url = new URL(location.href);
    if (activeFacet === DEFAULT_VIEW) url.searchParams.delete('religion');
    else url.searchParams.set('religion', activeFacet);
    history.replaceState(null, '', url);
  }
  updateLegend();
  window.dispatchEvent(new CustomEvent('potato-atlas-demography-facet-change', {
    detail: { facet: activeFacet, visible, year: data.religion_reference_year || 2020 }
  }));
}

function installControl(map, data) {
  if (document.getElementById(CONTROL_ID)) return;
  const pop = document.querySelector('#layersMenu .menu-pop');
  if (!pop) return;

  const title = document.createElement('div');
  title.className = 'menu-title';
  title.textContent = 'Country facet · religion';

  const select = document.createElement('select');
  select.id = CONTROL_ID;
  select.title = 'Map a sourced 2020 religious-identity percentage across countries';
  select.innerHTML = `<option value="off">Religion · off</option>` + Object.entries(FACETS)
    .map(([key, facet]) => `<option value="${esc(key)}">${esc(facet.label)} · %</option>`)
    .join('');

  const relationType = document.getElementById('relationType');
  if (relationType?.parentElement === pop) {
    pop.insertBefore(title, relationType);
    pop.insertBefore(select, relationType);
  } else {
    pop.appendChild(title);
    pop.appendChild(select);
  }

  const requested = new URL(location.href).searchParams.get('religion');
  select.value = FACETS[requested] ? requested : DEFAULT_VIEW;
  activeFacet = select.value;
  select.addEventListener('change', () => applyFacet(map, data, select.value));
  applyFacet(map, data, activeFacet, { writeUrl:false });
}

function installInteractions(map, data) {
  if (popup) return;
  popup = new maplibregl.Popup({ closeButton:false, closeOnClick:false, offset:8, maxWidth:'300px' });

  map.on('mousemove', FILL_ID, event => {
    if (activeFacet === DEFAULT_VIEW || historicalSuppressed) return;
    const feature = event.features?.[0];
    if (!feature) return;
    const properties = feature.properties || {};
    const code = String(properties.iso3 || '').toUpperCase();
    const value = Number(properties[facetProperty(activeFacet)]);
    const row = data.countries?.[code];
    const facet = FACETS[activeFacet];
    map.getCanvas().style.cursor = 'pointer';
    popup.setLngLat(event.lngLat).setHTML(`<div class="atlas-hover"><b>${esc(row?.name || properties.name || code)}</b><div>${esc(facet.label)}: ${Number.isFinite(value) && value >= 0 ? `${value.toFixed(value >= 10 ? 0 : 1)}%` : '—'}</div><div class="muted">Pew 2020 identity estimate · via Our World in Data</div></div>`).addTo(map);
  });

  map.on('mouseleave', FILL_ID, () => {
    map.getCanvas().style.cursor = '';
    popup.remove();
  });

  map.on('click', FILL_ID, event => {
    if (event?.originalEvent) event.originalEvent.__potatoAtlasOverlayHandled = true;
    const code = event.features?.[0]?.properties?.iso3;
    if (code && window.goCountry) window.goCountry(code);
  });
}

async function boot() {
  const existingData = window.__potatoAtlasDemography;
  const [data, geo] = await Promise.all([
    existingData ? Promise.resolve(existingData) : fetchJson(DEMOGRAPHY_URL),
    fetchJson(GEO_URL),
  ]);
  window.__potatoAtlasDemography = window.__potatoAtlasDemography || data;

  for (let i = 0; i < 120 && !window.__potatoAtlasMap; i += 1) {
    await new Promise(resolve => setTimeout(resolve, 50));
  }
  const map = window.__potatoAtlasMap;
  if (!map) return;
  if (!map.loaded()) await new Promise(resolve => map.once('load', resolve));

  installedMap = map;
  installedData = data;
  addLayers(map, geo, data);
  installControl(map, data);
  installInteractions(map, data);
  setHistoricalSuppressed();

  window.__potatoAtlasDemographyFacets = {
    data,
    facets:FACETS,
    set:key => {
      const select = document.getElementById(CONTROL_ID);
      if (select && (key === 'off' || FACETS[key])) select.value = key;
      applyFacet(map, data, key);
    },
    get active() { return activeFacet; },
  };
}

window.addEventListener('atlas-time-change', setHistoricalSuppressed);
window.addEventListener('potato-atlas-time-change', setHistoricalSuppressed);
boot().catch(error => console.warn('Demography facet layer unavailable:', error));
