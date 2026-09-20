import * as maplibregl from 'https://unpkg.com/maplibre-gl@6.9.0/dist/maplibre-gl.mjs';

const ATLAS_VERSION = new URL(import.meta.url).searchParams.get('v') || '';
function versionedModule(path) {
  if (!ATLAS_VERSION) return path;
  const url = new URL(path, import.meta.url);
  url.searchParams.set('v', ATLAS_VERSION);
  return url.href;
}

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

function ringArea(ring) {
  if (!Array.isArray(ring) || ring.length < 3) return 0;
  let area = 0;
  for (let i = 0; i < ring.length; i += 1) {
    const a = ring[i], b = ring[(i + 1) % ring.length];
    area += Number(a?.[0] || 0) * Number(b?.[1] || 0) - Number(b?.[0] || 0) * Number(a?.[1] || 0);
  }
  return Math.abs(area / 2);
}
function polygonCentroid(ring) {
  let area2 = 0, cx = 0, cy = 0;
  for (let i = 0; i < ring.length; i += 1) {
    const a = ring[i], b = ring[(i + 1) % ring.length];
    const cross = Number(a?.[0] || 0) * Number(b?.[1] || 0) - Number(b?.[0] || 0) * Number(a?.[1] || 0);
    area2 += cross; cx += (Number(a?.[0] || 0) + Number(b?.[0] || 0)) * cross; cy += (Number(a?.[1] || 0) + Number(b?.[1] || 0)) * cross;
  }
  if (Math.abs(area2) < 1e-9) return null;
  return [cx / (3 * area2), cy / (3 * area2)];
}
function pointInRing(point, ring) {
  if (!point || !Array.isArray(ring)) return false;
  const [x, y] = point;
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const xi = Number(ring[i]?.[0]), yi = Number(ring[i]?.[1]), xj = Number(ring[j]?.[0]), yj = Number(ring[j]?.[1]);
    const intersects = ((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / ((yj - yi) || 1e-12) + xi);
    if (intersects) inside = !inside;
  }
  return inside;
}
function representativePoint(feature) {
  const geometry = feature?.geometry;
  const polygons = geometry?.type === 'Polygon' ? [geometry.coordinates] : geometry?.type === 'MultiPolygon' ? geometry.coordinates : [];
  const candidates = polygons.map(poly => poly?.[0]).filter(ring => Array.isArray(ring) && ring.length >= 3).map(ring => ({ring, area:ringArea(ring)}));
  if (!candidates.length) return null;
  const ring = candidates.sort((a, b) => b.area - a.area)[0].ring;
  const centroid = polygonCentroid(ring);
  const point = centroid && pointInRing(centroid, ring) ? centroid : ring[Math.floor(ring.length / 2)];
  return Array.isArray(point) && point.length >= 2 ? [Number(point[1]), Number(point[0])] : null;
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
      return new Response(JSON.stringify(data), { status: 200, headers: { 'Content-Type': 'application/json', 'X-Atlas-Fallback': 'local-country-runtime' } });
    }
  }
  return nativeFetch(input, options);
};

const originalAddControl = maplibregl.Map.prototype.addControl;
maplibregl.Map.prototype.addControl = function (...args) {
  window.__potatoAtlasMap = this;
  return originalAddControl.apply(this, args);
};

await import(versionedModule('./3d-geo-kernel.js'));
try { await import(versionedModule('./3d-app.js')); }
finally { maplibregl.Map.prototype.addControl = originalAddControl; }

const map = window.__potatoAtlasMap;
if (!map) throw new Error('World atlas map instance was not captured.');
const { getOrCreateTooltipService } = await import(versionedModule('./3d-tooltip.js'));
const tooltip = getOrCreateTooltipService(map, { PopupClass:maplibregl.Popup, eventTarget:window });

try {
  const response = await fetchJsonResponse(COUNTRY_FACTS_URL);
  window.__potatoAtlasCountryFacts = await response.json();
} catch (error) {
  window.__potatoAtlasCountryFacts = { countries: {} };
  console.warn('Local country facts snapshot unavailable; hover will use renderer fallbacks.', error);
}

const number = value => value == null || Number.isNaN(Number(value)) ? '—' : new Intl.NumberFormat('en', { maximumFractionDigits: 0 }).format(Number(value));
const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
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
function capitalFor(code) { return capitalByCode.get(String(code || '').toUpperCase()) || null; }
function focusCapital(code, options = {}) {
  const feature = capitalFor(code);
  const coords = feature?.geometry?.coordinates;
  if (!feature || !Array.isArray(coords) || coords.length < 2) return false;
  const zoom = Math.max(4.2, Math.min(8, Number(options.zoom) || 5.6));
  map.easeTo({ center: [Number(coords[0]), Number(coords[1])], zoom, pitch: Math.min(map.getPitch(), 45), duration: 750 });
  return true;
}
async function scalarObservation(code, metricId) {
  const runtime = window.__potatoAtlasDataRuntime;
  if (!runtime?.ready) return null;
  if (metricId === 'population' && runtime.populationObservation) return runtime.populationObservation(code);
  if (metricId === 'area' && runtime.areaObservation) return runtime.areaObservation(code);
  const data = await runtime.ready;
  return data?.scalars?.by_entity?.[String(code || '').toUpperCase()]?.[metricId] || null;
}
async function populationObservation(code) { return scalarObservation(code, 'population'); }
async function areaObservation(code) { return scalarObservation(code, 'area'); }
async function countryHtml(properties) {
  const code = String(properties.iso3 || properties.cca3 || properties.ISO_A3 || properties.id || '').toUpperCase();
  const demography = code ? window.__potatoAtlasDemography?.countries?.[code] : null;
  const facts = code ? window.__potatoAtlasCountryFacts?.countries?.[code] : null;
  const [populationCell, areaCell] = await Promise.all([populationObservation(code), areaObservation(code)]);
  const population = populationCell?.value ?? demography?.population?.value ?? properties.population;
  const populationYear = populationCell?.period ?? demography?.population?.year;
  const name = facts?.name || demography?.name || properties.name || properties.NAME || properties.ADMIN || code || 'Country';
  const capital = facts?.capital || properties.capital || '—';
  const area = areaCell?.value ?? facts?.area_km2 ?? properties.area;
  const areaDefinition = areaCell?.definition ? ` <span class="muted">(${escapeHtml(areaCell.definition)})</span>` : '';
  const region = [facts?.region || facts?.continent || properties.region, facts?.subregion || properties.subregion].filter(Boolean).join(' · ') || '—';
  const currency = facts?.currency;
  const yearText = populationYear ? ` <span class="muted">(${escapeHtml(populationYear)})</span>` : '';
  const currencyText = currency ? `<div>Currency: ${escapeHtml(currency)}</div>` : '';
  return `<div class="atlas-hover"><b>${escapeHtml(name)}</b><div>Population: ${number(population)}${yearText}</div><div>Capital: ${escapeHtml(capital)}</div><div>Area: ${number(area)} km²${areaDefinition}</div><div>${escapeHtml(region)}</div>${currencyText}</div>`;
}
function capitalHtml(properties) { return `<div class="atlas-hover atlas-hover-capital"><b>${escapeHtml(properties.name)}</b><div class="muted">Capital city · ${escapeHtml(properties.iso3 || '')}</div></div>`; }

let countryHoverKey = '';
let countryHoverEvent = null;
let countryHoverHtml = null;
let countryHoverGeneration = null;
const directCountryHover = new Map();
async function handleCountryHover(event, feature) {
  if (!feature) return;
  const properties = feature.properties || {};
  const key = String(
    properties.iso3 || properties.cca3 || properties.ISO_A3 || properties.id ||
    properties.name || properties.NAME || properties.ADMIN || ''
  ).toUpperCase();
  countryHoverEvent = event;
  if (key === countryHoverKey) {
    if (countryHoverHtml && countryHoverGeneration != null) tooltip.show('country', countryHoverEvent.lngLat, countryHoverHtml, countryHoverGeneration);
    return;
  }
  countryHoverKey = key;
  countryHoverHtml = null;
  countryHoverGeneration = tooltip.nextGeneration('country');
  const html = await countryHtml(properties);
  if (key !== countryHoverKey || !countryHoverEvent) return;
  countryHoverHtml = html;
  tooltip.show('country', countryHoverEvent.lngLat, html, countryHoverGeneration);
}
function clearCountryHover() {
  countryHoverKey = '';
  countryHoverEvent = null;
  countryHoverHtml = null;
  countryHoverGeneration = null;
  tooltip.invalidate('country-leave');
}
function bindCountryHover(layerId) {
  const move = event => {
    const feature = event.features?.[0];
    if (!feature) return;
    map.getCanvas().style.cursor = 'pointer';
    void handleCountryHover(event, feature);
  };
  const leave = () => {
    map.getCanvas().style.cursor = '';
    clearCountryHover();
  };
  directCountryHover.set(layerId, { move, leave });
  map.on('mousemove', layerId, move);
  map.on('mouseleave', layerId, leave);
}
function unbindCountryHover() {
  for (const [layerId, handlers] of directCountryHover) {
    map.off('mousemove', layerId, handlers.move);
    map.off('mouseleave', layerId, handlers.leave);
  }
  directCountryHover.clear();
}
function installCountryHoverInteraction(interaction = window.__potatoAtlasInteraction) {
  if (!interaction?.register) return false;
  unbindCountryHover();
  interaction.register('country-hover', {
    layers:['countries-fill', 'countries-extrude'],
    objectType:'country',
    clickPriority:0,
    hoverPriority:20,
    claimOverlay:false,
    onHover:(event, feature) => { void handleCountryHover(event, feature); },
    onLeave:() => clearCountryHover(),
  });
  return true;
}

let capitalsStarted = false;
let capitalsVisible = true;
let directCapitalHandlers = null;
function setCapitalsVisible(visible) {
  capitalsVisible = Boolean(visible);
  for (const id of ['capital-cities', 'capital-city-major-labels', 'capital-city-labels']) if (map.getLayer(id)) map.setLayoutProperty(id, 'visibility', capitalsVisible ? 'visible' : 'none');
  window.dispatchEvent(new CustomEvent('potato-atlas-capitals-change', { detail: { visible: capitalsVisible } }));
  return capitalsVisible;
}
function handleCapitalHover(event, feature) {
  if (!feature) return;
  const generation = tooltip.nextGeneration('capital');
  tooltip.show('capital', event.lngLat, capitalHtml(feature.properties || {}), generation);
}
function clearCapitalHover() { tooltip.invalidate('capital-leave'); }
function handleCapitalClick(_event, feature) {
  const code = feature?.properties?.iso3;
  if (code && window.goCountry) window.goCountry(code);
}
function bindLegacyCapitalDirect() {
  // Degraded/direct-module fallback: only used when the shared router is absent.
  if (directCapitalHandlers || !map.getLayer('capital-cities')) return;
  const move = event => {
    const feature = event.features?.[0];
    if (!feature) return;
    map.getCanvas().style.cursor = 'pointer';
    handleCapitalHover(event, feature);
  };
  const leave = () => {
    map.getCanvas().style.cursor = '';
    clearCapitalHover();
  };
  const click = event => {
    if (event?.originalEvent) event.originalEvent.__potatoAtlasOverlayHandled = true;
    handleCapitalClick(event, event.features?.[0]);
  };
  directCapitalHandlers = { move, leave, click };
  map.on('mousemove', 'capital-cities', move);
  map.on('mouseleave', 'capital-cities', leave);
  map.on('click', 'capital-cities', click);
}
function unbindLegacyCapitalDirect() {
  if (!directCapitalHandlers) return;
  map.off('mousemove', 'capital-cities', directCapitalHandlers.move);
  map.off('mouseleave', 'capital-cities', directCapitalHandlers.leave);
  map.off('click', 'capital-cities', directCapitalHandlers.click);
  directCapitalHandlers = null;
}
function installLegacyCapitalInteraction(interaction = window.__potatoAtlasInteraction) {
  if (!interaction?.register || !map.getLayer('capital-cities')) return false;
  unbindLegacyCapitalDirect();
  interaction.register('legacy-capitals', {
    layers:['capital-cities'],
    objectType:'place',
    clickPriority:75,
    hoverPriority:75,
    onClick:(event, feature) => handleCapitalClick(event, feature),
    onHover:(event, feature) => handleCapitalHover(event, feature),
    onLeave:() => clearCapitalHover(),
  });
  return true;
}
async function installCapitalsWhenUseful() {
  if (capitalsStarted) return;
  capitalsStarted = true;
  try {
    const capitals = await loadCapitals();
    if (capitals.features.length < 150) throw new Error(`capital coverage unexpectedly low: ${capitals.features.length}`);
    indexCapitals(capitals.features);
    if (!map.getSource('capital-cities')) map.addSource('capital-cities', { type: 'geojson', data: capitals });
    if (!map.getLayer('capital-cities')) map.addLayer({ id: 'capital-cities', type: 'circle', source: 'capital-cities', minzoom: 0, filter: ['==', ['get', 'primary'], true], paint: { 'circle-radius': ['interpolate', ['linear'], ['zoom'], 1, 1.8, 3, 2.9, 7, 5.8], 'circle-color': '#e7c56f', 'circle-stroke-color': '#171a18', 'circle-stroke-width': 1.1, 'circle-opacity': 0.92 } });
    if (!map.getLayer('capital-city-major-labels')) map.addLayer({ id: 'capital-city-major-labels', type: 'symbol', source: 'capital-cities', minzoom: 1.1, maxzoom: 3.4, filter: ['all', ['==', ['get', 'primary'], true], ['<=', ['get', 'scalerank'], 3]], layout: { 'text-field': ['get', 'name'], 'text-size': 9, 'text-offset': [0, 1.05], 'text-anchor': 'top', 'text-allow-overlap': false, 'text-optional': true }, paint: { 'text-color': '#f0d98f', 'text-halo-color': '#080b0b', 'text-halo-width': 1.1 } });
    if (!map.getLayer('capital-city-labels')) map.addLayer({ id: 'capital-city-labels', type: 'symbol', source: 'capital-cities', minzoom: 3.1, filter: ['==', ['get', 'primary'], true], layout: { 'text-field': ['get', 'name'], 'text-size': ['interpolate', ['linear'], ['zoom'], 3.1, 9, 7, 11], 'text-offset': [0, 1.15], 'text-anchor': 'top', 'text-allow-overlap': false, 'text-optional': true }, paint: { 'text-color': '#f3df9e', 'text-halo-color': '#080b0b', 'text-halo-width': 1.15 } });
    if (!installLegacyCapitalInteraction()) bindLegacyCapitalDirect();
    setCapitalsVisible(true);
    window.__potatoAtlasCapitals = { setVisible: setCapitalsVisible, focus: focusCapital, forCountry: capitalFor, get visible() { return capitalsVisible; }, get count() { return capitalFeatures.length; } };
    window.dispatchEvent(new CustomEvent('potato-atlas-capitals-ready', { detail: { count: capitals.features.length, visible: capitalsVisible } }));
  } catch (error) { capitalsStarted = false; console.warn('Capital city layer unavailable:', error); }
}
function placesCanOwnCapitals(detail = {}) {
  const status = window.__potatoAtlasPlaces?.status?.() || detail || {};
  return Number(status.majorCount || 0) > 0 && !status.error;
}
window.addEventListener('potato-atlas-places-ready', event => {
  if (placesCanOwnCapitals(event?.detail || {})) return;
  void installCapitalsWhenUseful();
});
window.addEventListener('potato-atlas-interaction-ready', event => {
  const interaction = event?.detail?.interaction || window.__potatoAtlasInteraction;
  installCountryHoverInteraction(interaction);
  installLegacyCapitalInteraction(interaction);
});
function install() {
  if (installCountryHoverInteraction()) return;
  // Degraded/direct-module fallback while the core renderer is available before
  // the Interaction Router is loaded by the bootstrap.
  bindCountryHover('countries-fill');
  bindCountryHover('countries-extrude');
}
if (map.loaded()) install(); else map.once('load', install);