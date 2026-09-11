import * as maplibregl from 'https://unpkg.com/maplibre-gl@6.9.0/dist/maplibre-gl.mjs';

// The bootstrap gives every deployment a SHA query parameter. Carry it through
// the hover -> app dynamic import so a fresh HTML document cannot accidentally
// reuse an older cached 3d-app.js module from a previous deployment.
const ATLAS_VERSION = new URL(import.meta.url).searchParams.get('v') || '';
function versionedModule(path) {
  if (!ATLAS_VERSION) return path;
  const url = new URL(path, import.meta.url);
  url.searchParams.set('v', ATLAS_VERSION);
  return url.href;
}

// Resilient atlas boot order:
//   same-origin Pages snapshot -> primary provider -> alternate provider -> local synthesis.
// Third-party data enriches the atlas; it must not be a single point of failure.
const nativeFetch = window.fetch.bind(window);
const GEO_LOCAL = '../data/world-countries.geo.json';
const GEO_PRIMARY = 'https://cdn.jsdelivr.net/gh/johan/world.geo.json@master/countries.geo.json';
const GEO_FALLBACK = 'https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json';
const REST_LOCAL = '../data/rest-countries-runtime.json';
const CAPITALS_LOCAL = '../data/world-capitals.geo.json';
const REST_PREFIX = 'https://restcountries.com/v3.1/all';
const COUNTRY_FACTS_URL = '../data/world-country-facts.json';

async function fetchJsonResponse(url, options) {
  const response = await nativeFetch(url, options);
  if (!response.ok) throw new Error(`${response.status} ${url}`);
  return response;
}

function representativePoint(feature) {
  let minX = 180, minY = 90, maxX = -180, maxY = -90, seen = false;
  const walk = value => {
    if (!Array.isArray(value)) return;
    if (typeof value[0] === 'number' && typeof value[1] === 'number') {
      seen = true;
      minX = Math.min(minX, value[0]); maxX = Math.max(maxX, value[0]);
      minY = Math.min(minY, value[1]); maxY = Math.max(maxY, value[1]);
      return;
    }
    value.forEach(walk);
  };
  walk(feature?.geometry?.coordinates);
  return seen ? [(minY + maxY) / 2, (minX + maxX) / 2] : null;
}

async function bestGeometryResponse() {
  try { return await fetchJsonResponse(GEO_LOCAL); }
  catch (localError) { console.warn('Local world geometry snapshot unavailable.', localError); }
  try { return await fetchJsonResponse(GEO_PRIMARY); }
  catch (primaryError) { console.warn('Primary world geometry unavailable.', primaryError); }
  return fetchJsonResponse(GEO_FALLBACK);
}

async function fallbackRestCountries() {
  const [indexResponse, geoResponse] = await Promise.all([
    fetchJsonResponse('../data/countries/index.json'),
    bestGeometryResponse()
  ]);
  const [indexPayload, geo] = await Promise.all([indexResponse.json(), geoResponse.json()]);
  const rows = Array.isArray(indexPayload) ? indexPayload : (indexPayload.countries || indexPayload.items || []);
  const names = new Map((geo.features || []).map(feature => [feature.id, feature]));
  return rows.map(row => {
    const code = row.iso3 || row.cca3 || row.code;
    const feature = names.get(code);
    const name = row.name || feature?.properties?.name || code;
    return {
      name: { common: name, official: name },
      cca3: code,
      population: null,
      area: null,
      latlng: representativePoint(feature) || [],
      capital: [],
      capitalInfo: {},
      region: '',
      subregion: '',
      borders: [],
      atlas_fallback: true
    };
  }).filter(row => row.cca3);
}

window.fetch = async function atlasResilientFetch(input, options) {
  const url = typeof input === 'string' ? input : input?.url || String(input);
  if (url === GEO_PRIMARY) return bestGeometryResponse();
  if (url.startsWith(REST_PREFIX)) {
    try { return await fetchJsonResponse(REST_LOCAL, options); }
    catch (localError) { console.warn('Local country runtime snapshot unavailable.', localError); }
    try {
      const response = await nativeFetch(input, options);
      if (response.ok) return response;
      throw new Error(`REST Countries returned ${response.status}`);
    } catch (primaryError) {
      console.warn('REST Countries unavailable; using local minimal country runtime.', primaryError);
      const data = await fallbackRestCountries();
      return new Response(JSON.stringify(data), {
        status: 200,
        headers: { 'Content-Type': 'application/json', 'X-Atlas-Fallback': 'local-country-runtime' }
      });
    }
  }
  return nativeFetch(input, options);
};

const originalAddControl = maplibregl.Map.prototype.addControl;
maplibregl.Map.prototype.addControl = function (...args) {
  window.__potatoAtlasMap = this;
  return originalAddControl.apply(this, args);
};

try {
  await import(versionedModule('./3d-app.js'));
} finally {
  maplibregl.Map.prototype.addControl = originalAddControl;
}

const map = window.__potatoAtlasMap;
if (!map) throw new Error('World atlas map instance was not captured.');

try {
  const response = await fetchJsonResponse(COUNTRY_FACTS_URL);
  window.__potatoAtlasCountryFacts = await response.json();
} catch (error) {
  window.__potatoAtlasCountryFacts = { countries: {} };
  console.warn('Local country facts snapshot unavailable; hover will use renderer fallbacks.', error);
}

const number = value => value == null || Number.isNaN(Number(value))
  ? '—'
  : new Intl.NumberFormat('en', { maximumFractionDigits: 0 }).format(Number(value));

const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[char]));

const popup = new maplibregl.Popup({ closeButton: false, closeOnClick: false, offset: 12, maxWidth: '300px' });
let capitalFeatures = [];
const capitalByCode = new Map();

async function loadCapitals() {
  const response = await fetchJsonResponse(CAPITALS_LOCAL, { cache: 'force-cache' });
  const payload = await response.json();
  if (payload?.type !== 'FeatureCollection' || !Array.isArray(payload.features)) throw new Error('Local capital snapshot has invalid shape.');
  return payload;
}

function indexCapitals(features) {
  capitalFeatures = Array.isArray(features) ? features : [];
  capitalByCode.clear();
  for (const feature of capitalFeatures) {
    const code = String(feature?.properties?.iso3 || '').toUpperCase();
    const coords = feature?.geometry?.coordinates;
    if (!code || !Array.isArray(coords) || coords.length < 2) continue;
    const current = capitalByCode.get(code);
    const primary = feature?.properties?.primary === true;
    if (!current || (primary && current.properties?.primary !== true)) capitalByCode.set(code, feature);
  }
}

function capitalFor(code) {
  return capitalByCode.get(String(code || '').toUpperCase()) || null;
}

function focusCapital(code, options = {}) {
  const feature = capitalFor(code);
  const coords = feature?.geometry?.coordinates;
  if (!feature || !Array.isArray(coords) || coords.length < 2) return false;
  const zoom = Math.max(4.2, Math.min(8, Number(options.zoom) || 5.6));
  map.easeTo({ center: [Number(coords[0]), Number(coords[1])], zoom, pitch: Math.min(map.getPitch(), 45), duration: 750 });
  return true;
}

function countryHtml(properties) {
  const code = String(properties.iso3 || properties.cca3 || properties.ISO_A3 || properties.id || '').toUpperCase();
  const demography = code ? window.__potatoAtlasDemography?.countries?.[code] : null;
  const facts = code ? window.__potatoAtlasCountryFacts?.countries?.[code] : null;
  const population = demography?.population?.value ?? properties.population;
  const populationYear = demography?.population?.year;
  const name = facts?.name || demography?.name || properties.name || properties.NAME || properties.ADMIN || code || 'Country';
  const capital = facts?.capital || properties.capital || '—';
  const area = facts?.area_km2 ?? properties.area;
  const region = [facts?.region || facts?.continent || properties.region, facts?.subregion || properties.subregion].filter(Boolean).join(' · ') || '—';
  const currency = facts?.currency;
  const yearText = populationYear ? ` <span class="muted">(${escapeHtml(populationYear)})</span>` : '';
  const currencyText = currency ? `<div>Currency: ${escapeHtml(currency)}</div>` : '';
  return `<div class="atlas-hover"><b>${escapeHtml(name)}</b><div>Population: ${number(population)}${yearText}</div><div>Capital: ${escapeHtml(capital)}</div><div>Area: ${number(area)} km²</div><div>${escapeHtml(region)}</div>${currencyText}</div>`;
}

function capitalHtml(properties) {
  return `<div class="atlas-hover atlas-hover-capital"><b>${escapeHtml(properties.name)}</b><div class="muted">Capital city · ${escapeHtml(properties.iso3 || '')}</div></div>`;
}

function showPopup(event, html) {
  popup.setLngLat(event.lngLat).setHTML(html).addTo(map);
}

function bindCountryHover(layerId) {
  map.on('mousemove', layerId, event => {
    const feature = event.features?.[0];
    if (!feature) return;
    map.getCanvas().style.cursor = 'pointer';
    showPopup(event, countryHtml(feature.properties || {}));
  });
  map.on('mouseleave', layerId, () => {
    map.getCanvas().style.cursor = '';
    popup.remove();
  });
}

let capitalsStarted = false;
let capitalsVisible = true;
function setCapitalsVisible(visible) {
  capitalsVisible = Boolean(visible);
  for (const id of ['capital-cities', 'capital-city-major-labels', 'capital-city-labels']) {
    if (map.getLayer(id)) map.setLayoutProperty(id, 'visibility', capitalsVisible ? 'visible' : 'none');
  }
  window.dispatchEvent(new CustomEvent('potato-atlas-capitals-change', { detail: { visible: capitalsVisible } }));
  return capitalsVisible;
}

async function installCapitalsWhenUseful() {
  if (capitalsStarted) return;
  capitalsStarted = true;
  try {
    const capitals = await loadCapitals();
    if (capitals.features.length < 150) throw new Error(`capital coverage unexpectedly low: ${capitals.features.length}`);
    indexCapitals(capitals.features);
    if (!map.getSource('capital-cities')) map.addSource('capital-cities', { type: 'geojson', data: capitals });
    if (!map.getLayer('capital-cities')) map.addLayer({
      id: 'capital-cities', type: 'circle', source: 'capital-cities', minzoom: 0,
      filter: ['==', ['get', 'primary'], true],
      paint: {
        'circle-radius': ['interpolate', ['linear'], ['zoom'], 1, 1.8, 3, 2.9, 7, 5.8],
        'circle-color': '#e7c56f', 'circle-stroke-color': '#171a18',
        'circle-stroke-width': 1.1, 'circle-opacity': 0.92
      }
    });
    if (!map.getLayer('capital-city-major-labels')) map.addLayer({
      id: 'capital-city-major-labels', type: 'symbol', source: 'capital-cities', minzoom: 1.1, maxzoom: 3.4,
      filter: ['all', ['==', ['get', 'primary'], true], ['<=', ['get', 'scalerank'], 3]],
      layout: {
        'text-field': ['get', 'name'], 'text-size': 9, 'text-offset': [0, 1.05],
        'text-anchor': 'top', 'text-allow-overlap': false, 'text-optional': true
      },
      paint: { 'text-color': '#f0d98f', 'text-halo-color': '#080b0b', 'text-halo-width': 1.1 }
    });
    if (!map.getLayer('capital-city-labels')) map.addLayer({
      id: 'capital-city-labels', type: 'symbol', source: 'capital-cities', minzoom: 3.1,
      filter: ['==', ['get', 'primary'], true],
      layout: {
        'text-field': ['get', 'name'], 'text-size': ['interpolate', ['linear'], ['zoom'], 3.1, 9, 7, 11],
        'text-offset': [0, 1.15], 'text-anchor': 'top', 'text-allow-overlap': false,
        'text-optional': true
      },
      paint: { 'text-color': '#f3df9e', 'text-halo-color': '#080b0b', 'text-halo-width': 1.15 }
    });

    map.on('mousemove', 'capital-cities', event => {
      const feature = event.features?.[0];
      if (!feature) return;
      map.getCanvas().style.cursor = 'pointer';
      showPopup(event, capitalHtml(feature.properties || {}));
    });
    map.on('mouseleave', 'capital-cities', () => {
      map.getCanvas().style.cursor = '';
      popup.remove();
    });
    map.on('click', 'capital-cities', event => {
      if(event?.originalEvent)event.originalEvent.__potatoAtlasOverlayHandled=true;
      const code = event.features?.[0]?.properties?.iso3;
      if (code && window.goCountry) window.goCountry(code);
    });

    setCapitalsVisible(true);
    window.__potatoAtlasCapitals = {
      setVisible: setCapitalsVisible,
      focus: focusCapital,
      forCountry: capitalFor,
      get visible() { return capitalsVisible; },
      get count() { return capitalFeatures.length; }
    };
    window.dispatchEvent(new CustomEvent('potato-atlas-capitals-ready', {
      detail: { count: capitals.features.length, visible: capitalsVisible }
    }));
  } catch (error) {
    capitalsStarted = false;
    console.warn('Capital city layer unavailable:', error);
  }
}

function install() {
  bindCountryHover('countries-fill');
  bindCountryHover('countries-extrude');
  // Capitals are useful orientation at world scale, so install the already-local
  // snapshot immediately. Labels remain progressive and do not appear until the
  // map is zoomed in enough to keep the overview readable.
  installCapitalsWhenUseful();
}

if (map.loaded()) install();
else map.once('load', install());