import * as maplibregl from 'https://unpkg.com/maplibre-gl@6.9.0/dist/maplibre-gl.mjs';

// Resilient atlas boot order:
//   same-origin Pages snapshot -> primary provider -> alternate provider -> local synthesis.
// Third-party data enriches the atlas; it must not be a single point of failure.
const nativeFetch = window.fetch.bind(window);
const GEO_LOCAL = '../data/world-countries.geo.json';
const GEO_PRIMARY = 'https://cdn.jsdelivr.net/gh/johan/world.geo.json@master/countries.geo.json';
const GEO_FALLBACK = 'https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json';
const REST_LOCAL = '../data/rest-countries-runtime.json';
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
  await import('./3d-app.js');
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

function pointFromWkt(wkt) {
  const match = String(wkt || '').match(/Point\(([-\d.]+)\s+([-\d.]+)\)/i);
  return match ? [Number(match[1]), Number(match[2])] : null;
}

async function loadCapitals() {
  const query = `
SELECT ?iso3 ?capital ?capitalLabel ?coord ?population WHERE {
  ?country wdt:P298 ?iso3 ;
           wdt:P36 ?capital .
  ?capital wdt:P625 ?coord .
  OPTIONAL { ?capital wdt:P1082 ?population . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}`;
  const url = 'https://query.wikidata.org/sparql?format=json&query=' + encodeURIComponent(query);
  const response = await nativeFetch(url, { headers: { Accept: 'application/sparql-results+json' } });
  if (!response.ok) throw new Error(`Wikidata capitals: ${response.status}`);
  const data = await response.json();

  const byKey = new Map();
  for (const row of data.results?.bindings || []) {
    const iso3 = row.iso3?.value;
    const name = row.capitalLabel?.value;
    const coordinates = pointFromWkt(row.coord?.value);
    if (!iso3 || !name || !coordinates) continue;
    const population = row.population?.value != null ? Number(row.population.value) : null;
    const key = `${iso3}|${row.capital?.value || name}`;
    const previous = byKey.get(key);
    if (!previous || (population != null && (previous.population == null || population > previous.population))) {
      byKey.set(key, { iso3, name, population, coordinates });
    }
  }

  return {
    type: 'FeatureCollection',
    features: [...byKey.values()].map(city => ({
      type: 'Feature',
      properties: { iso3: city.iso3, name: city.name, population: city.population },
      geometry: { type: 'Point', coordinates: city.coordinates }
    }))
  };
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
  return `<div class="atlas-hover atlas-hover-capital"><b>${escapeHtml(properties.name)}</b><div>Population: ${number(properties.population)}</div></div>`;
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

async function install() {
  bindCountryHover('countries-fill');
  bindCountryHover('countries-extrude');

  try {
    const capitals = await loadCapitals();
    map.addSource('capital-cities', { type: 'geojson', data: capitals });
    map.addLayer({
      id: 'capital-cities', type: 'circle', source: 'capital-cities', minzoom: 1.2,
      paint: {
        'circle-radius': ['interpolate', ['linear'], ['zoom'], 1.2, 3.4, 4, 5.2, 7, 7],
        'circle-color': '#f3d36f', 'circle-stroke-color': '#171a18',
        'circle-stroke-width': 1.5, 'circle-opacity': 0.95
      }
    });
    map.addLayer({
      id: 'capital-city-labels', type: 'symbol', source: 'capital-cities', minzoom: 4.8,
      layout: {
        'text-field': ['get', 'name'], 'text-size': 10, 'text-offset': [0, 1.25],
        'text-anchor': 'top', 'text-allow-overlap': false
      },
      paint: { 'text-color': '#f7e8a4', 'text-halo-color': '#080b0b', 'text-halo-width': 1.2 }
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
  } catch (error) {
    console.warn('Capital city layer unavailable:', error);
  }
}

if (map.loaded()) install();
else map.once('load', install);
