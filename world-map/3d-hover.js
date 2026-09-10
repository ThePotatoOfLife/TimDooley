import * as maplibregl from 'https://unpkg.com/maplibre-gl@6.9.0/dist/maplibre-gl.mjs';

// Capture the atlas Map instance without coupling the core renderer to this optional layer.
const originalAddControl = maplibregl.Map.prototype.addControl;
maplibregl.Map.prototype.addControl = function (...args) {
  window.__potatoAtlasMap = this;
  return originalAddControl.apply(this, args);
};

await import('./3d-app.js');
maplibregl.Map.prototype.addControl = originalAddControl;

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
  const response = await fetch(url, { headers: { Accept: 'application/sparql-results+json' } });
  if (!response.ok) throw new Error(`Wikidata capitals: ${response.status}`);
  const data = await response.json();

  // Some entities can appear more than once because of multiple ranked population statements.
  // Keep one node per country/capital, preferring the largest available numeric population.
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
    // Capitals are an enhancement layer. Failure of the external observable-data feed
    // must never break the canonical atlas itself.
    console.warn('Capital city layer unavailable:', error);
  }
}

if (map.loaded()) install();
else map.once('load', install);
