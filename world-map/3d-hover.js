import * as maplibregl from 'https://unpkg.com/maplibre-gl@6.9.0/dist/maplibre-gl.mjs';

// The 3D atlas used to fail hard when either jsDelivr or REST Countries had a
// transient/CORS/network problem. Keep external services as enrichments, not
// single points of failure. The wrapper below retries geometry from raw GitHub
// and can synthesize a minimal REST-Countries-compatible runtime from the
// repository's own country index + world polygons.
const nativeFetch = window.fetch.bind(window);
const GEO_PRIMARY = 'https://cdn.jsdelivr.net/gh/johan/world.geo.json@master/countries.geo.json';
const GEO_FALLBACK = 'https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json';
const REST_PREFIX = 'https://restcountries.com/v3.1/all';

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

async function fallbackRestCountries() {
  const [indexResponse, geoResponse] = await Promise.all([
    fetchJsonResponse('../data/countries/index.json'),
    (async () => {
      try { return await fetchJsonResponse(GEO_PRIMARY); }
      catch { return fetchJsonResponse(GEO_FALLBACK); }
    })()
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
  if (url === GEO_PRIMARY) {
    try {
      const response = await nativeFetch(input, options);
      if (response.ok) return response;
      throw new Error(`Primary world geometry returned ${response.status}`);
    } catch (primaryError) {
      console.warn('Primary world geometry failed; retrying raw GitHub.', primaryError);
      return fetchJsonResponse(GEO_FALLBACK, options);
    }
  }
  if (url.startsWith(REST_PREFIX)) {
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

// Capture the atlas Map instance without coupling the core renderer to this optional layer.
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

const number = value => value == null || Number.isNaN(Number(value))
  ? '—'
  : new Intl.NumberFormat('en', { maximumFractionDigits: 0 }).format(Number(value));

const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[char]));

const popup = new maplibregl.Popup({
  closeButton: false,
  closeOnClick: false,
  offset: 12,
  maxWidth: '280px'
});

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
  const name = properties.name || properties.NAME || properties.ADMIN || properties.iso3 || 'Country';
  const capital = properties.capital || '—';
  const region = [properties.region, properties.subregion].filter(Boolean).join(' · ') || '—';
  return `<div class="atlas-hover"><b>${escapeHtml(name)}</b><div>Population: ${number(properties.population)}</div><div>Capital: ${escapeHtml(capital)}</div><div>Area: ${number(properties.area)} km²</div><div>${escapeHtml(region)}</div></div>`;
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
      id: 'capital-cities',
      type: 'circle',
      source: 'capital-cities',
      minzoom: 1.2,
      paint: {
        'circle-radius': ['interpolate', ['linear'], ['zoom'], 1.2, 3.4, 4, 5.2, 7, 7],
        'circle-color': '#f3d36f',
        'circle-stroke-color': '#171a18',
        'circle-stroke-width': 1.5,
        'circle-opacity': 0.95
      }
    });
    map.addLayer({
      id: 'capital-city-labels',
      type: 'symbol',
      source: 'capital-cities',
      minzoom: 4.8,
      layout: {
        'text-field': ['get', 'name'],
        'text-size': 10,
        'text-offset': [0, 1.25],
        'text-anchor': 'top',
        'text-allow-overlap': false
      },
      paint: {
        'text-color': '#f7e8a4',
        'text-halo-color': '#080b0b',
        'text-halo-width': 1.2
      }
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