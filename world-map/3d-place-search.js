// Unified geographic search for the World Relational Atlas.
//
// This controller deliberately reuses the existing header search box. Countries
// stay owned by the canonical selection controller; subdivisions stay owned by
// the subdivision module; city search reuses the pinned Natural Earth snapshot
// already rendered by 3d-hover.js.

const input = document.getElementById('search');
const countryList = document.getElementById('country-list');
const map = window.__potatoAtlasMap;
const CITY_URL = '../data/world-capitals.geo.json';
const PLACE_SOURCE = 'atlas-place-selection';
const PLACE_MARKER = 'atlas-place-selection-marker';
const PLACE_LABEL = 'atlas-place-selection-label';

if (!input) throw new Error('Place search requires the existing atlas search input.');
if (!map) throw new Error('Place search requires the core atlas map.');

input.placeholder = 'Find place…';
input.setAttribute('aria-label', 'Find place');
input.title = 'Find a country, state, or city';

const normalize = value => String(value || '').trim().toLocaleLowerCase('en').normalize('NFKD').replace(/[\u0300-\u036f]/g, '');
const slug = value => normalize(value).replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

function emptyFeatureCollection() { return { type:'FeatureCollection', features:[] }; }

function countryCandidates() {
  return [...(countryList?.options || [])].map(option => {
    const value = String(option.value || '').trim();
    const match = value.match(/^(.*?)\s*\(([A-Z]{3})\)\s*$/);
    if (!match) return null;
    return { type:'country', name:match[1].trim(), code:match[2], value };
  }).filter(Boolean);
}

function countryMatch(query, exactOnly = false) {
  const needle = normalize(query);
  if (!needle) return null;
  const candidates = countryCandidates();
  const exact = candidates.find(item =>
    normalize(item.code) === needle || normalize(item.name) === needle || normalize(item.value) === needle
  );
  if (exact || exactOnly) return exact || null;
  return candidates.find(item => normalize(item.name).startsWith(needle))
    || candidates.find(item => normalize(item.name).includes(needle))
    || null;
}

function syncPlace(id) {
  const url = new URL(location.href);
  if (id) url.searchParams.set('place', id);
  else url.searchParams.delete('place');
  if (id) url.searchParams.delete('subdivision');
  history.replaceState({}, '', url);
}

function ensurePlaceMarker() {
  if (!map.getSource(PLACE_SOURCE)) map.addSource(PLACE_SOURCE, { type:'geojson', data:emptyFeatureCollection() });
  if (!map.getLayer(PLACE_MARKER)) map.addLayer({
    id:PLACE_MARKER,
    type:'circle',
    source:PLACE_SOURCE,
    paint:{
      'circle-radius':['interpolate',['linear'],['zoom'],2,5,7,8],
      'circle-color':'#fff0ad',
      'circle-stroke-color':'#151918',
      'circle-stroke-width':2,
      'circle-opacity':0.96
    }
  });
  if (!map.getLayer(PLACE_LABEL)) map.addLayer({
    id:PLACE_LABEL,
    type:'symbol',
    source:PLACE_SOURCE,
    layout:{'text-field':['get','name'],'text-size':11,'text-offset':[0,1.25],'text-anchor':'top','text-optional':true},
    paint:{'text-color':'#fff0ad','text-halo-color':'#080b0b','text-halo-width':1.2}
  });
}

function clearPlace({ sync = true } = {}) {
  map.getSource(PLACE_SOURCE)?.setData?.(emptyFeatureCollection());
  if (sync) syncPlace(null);
}

async function activateCountry(candidate) {
  if (!candidate) return false;
  clearPlace();
  const selection = window.__potatoAtlasSelection;
  if (selection?.activate) return Boolean(await selection.activate(candidate.code, { fly:true }));
  if (typeof window.goCountry === 'function') return Boolean(await window.goCountry(candidate.code));
  return false;
}

let subdivisionPromise = null;
async function subdivisions() {
  if (window.__potatoAtlasSubdivisions) return window.__potatoAtlasSubdivisions;
  if (!subdivisionPromise) {
    subdivisionPromise = Promise.resolve(
      window.__potatoAtlasLoadModule?.('Subdivisions', './3d-subdivisions.js')
    ).then(() => window.__potatoAtlasSubdivisions || null).catch(error => {
      console.warn('Subdivision search unavailable:', error);
      return null;
    });
  }
  return subdivisionPromise;
}

function addSubdivisionSuggestions(matches = []) {
  if (!countryList) return;
  for (const match of matches) {
    const value = `${match.name} (${match.id})`;
    if ([...countryList.options].some(option => option.value === value)) continue;
    const option = document.createElement('option');
    option.value = value;
    option.label = `${match.subdivision_type || 'subdivision'} · ${match.code || match.id}`;
    option.dataset.placeKind = 'subdivision';
    countryList.appendChild(option);
  }
}

async function warmSubdivisions() {
  const api = await subdivisions();
  if (!api?.search) return [];
  const all = await api.search('');
  addSubdivisionSuggestions(all);
  return all;
}

function subdivisionExact(matches, query) {
  const needle = normalize(query);
  return matches.find(match =>
    normalize(match.id) === needle
    || normalize(match.code) === needle
    || normalize(match.name) === needle
    || normalize(`${match.name} (${match.id})`) === needle
  ) || null;
}

let cityPromise = null;
function cityRow(feature) {
  const p = feature?.properties || {};
  const coordinates = feature?.geometry?.coordinates || [];
  if (!p.name || !p.iso3 || coordinates.length < 2) return null;
  const id = `CITY-${String(p.iso3).toUpperCase()}-${slug(p.name)}`;
  return {
    id,
    type:'city',
    name:p.name,
    country:p.country || p.iso3,
    iso3:String(p.iso3).toUpperCase(),
    scalerank:Number(p.scalerank ?? 99),
    primary:p.primary === true,
    source:p.source || 'Natural Earth populated places (pinned)',
    coordinates:[Number(coordinates[0]), Number(coordinates[1])],
    feature
  };
}

async function cityRows() {
  if (!cityPromise) {
    cityPromise = fetch(CITY_URL, { cache:'force-cache' }).then(async response => {
      if (!response.ok) throw new Error(`Pinned city snapshot unavailable (${response.status})`);
      const payload = await response.json();
      if (payload?.type !== 'FeatureCollection' || !Array.isArray(payload.features)) throw new Error('Pinned city snapshot is not GeoJSON.');
      return payload.features.map(cityRow).filter(Boolean);
    }).catch(error => {
      cityPromise = null;
      console.warn('Pinned city search unavailable:', error);
      return [];
    });
  }
  return cityPromise;
}

function cityScore(city, needle) {
  const id = normalize(city.id), name = normalize(city.name), country = normalize(city.country);
  const display = normalize(`${city.name} — ${city.country}`);
  if (needle === id) return 0;
  if (needle === name) return 1;
  if (needle === display) return 2;
  if (name.startsWith(needle)) return 3;
  if (`${name} ${country}`.includes(needle)) return 4;
  return 99;
}

async function searchCities(query) {
  const rows = await cityRows();
  const needle = normalize(query);
  if (!needle) return [...rows].sort((a,b) => Number(b.primary) - Number(a.primary) || a.scalerank - b.scalerank || a.name.localeCompare(b.name));
  return rows.map(city => ({city, score:cityScore(city, needle)}))
    .filter(item => item.score < 99)
    .sort((a,b) => a.score - b.score || Number(b.city.primary) - Number(a.city.primary) || a.city.scalerank - b.city.scalerank || a.city.name.localeCompare(b.city.name))
    .map(item => item.city);
}

function addCitySuggestions(matches = []) {
  if (!countryList) return;
  for (const city of matches) {
    const value = `${city.name} — ${city.country}`;
    if ([...countryList.options].some(option => option.value === value)) continue;
    const option = document.createElement('option');
    option.value = value;
    option.label = city.primary ? `capital · ${city.iso3}` : `city · ${city.iso3}`;
    option.dataset.placeKind = 'city';
    option.dataset.placeId = city.id;
    countryList.appendChild(option);
  }
}

async function warmCities() {
  const all = await searchCities('');
  addCitySuggestions(all);
  return all;
}

function cityExact(matches, query) {
  const needle = normalize(query);
  return matches.find(city =>
    normalize(city.id) === needle
    || normalize(city.name) === needle
    || normalize(`${city.name} — ${city.country}`) === needle
  ) || null;
}

async function focusCity(city, options = {}) {
  if (!city?.id || !Array.isArray(city.coordinates)) return false;
  const selection = window.__potatoAtlasSelection;
  if (selection?.activate && city.iso3) await selection.activate(city.iso3, { fly:false });
  ensurePlaceMarker();
  map.getSource(PLACE_SOURCE)?.setData?.({
    type:'FeatureCollection',
    features:[{ type:'Feature', properties:{ id:city.id, name:city.name, country:city.country, iso3:city.iso3, primary:city.primary }, geometry:{type:'Point', coordinates:city.coordinates} }]
  });
  syncPlace(city.id);
  if (options.fit !== false) {
    const targetZoom = Math.max(5.6, Math.min(8, Number(options.zoom) || 6.4));
    map.easeTo({ center:city.coordinates, zoom:targetZoom, pitch:Math.min(map.getPitch(), 45), duration:700 });
  }
  input.value = `${city.name} — ${city.country}`;
  input.setCustomValidity('');
  window.dispatchEvent(new CustomEvent('potato-atlas-place-select', { detail:{...city} }));
  return true;
}

async function restoreRequestedPlace() {
  const requested = new URL(location.href).searchParams.get('place');
  if (!requested) return false;
  const rows = await cityRows();
  const city = rows.find(row => row.id === requested) || null;
  return city ? focusCity(city, { fit:true }) : false;
}

async function submit(query) {
  const raw = String(query || '').trim();
  if (!raw) return false;

  // Preserve the long-established country interpretation for exact country names
  // and ISO3 codes. Plain "Georgia" remains the country; GA / US-GA identifies
  // the U.S. state.
  const exactCountry = countryMatch(raw, true);
  if (exactCountry) return activateCountry(exactCountry);

  const [api, cities] = await Promise.all([subdivisions(), searchCities(raw)]);
  const subdivisionMatches = api?.search ? await api.search(raw) : [];
  addSubdivisionSuggestions(subdivisionMatches);
  addCitySuggestions(cities);

  const exactSubdivision = subdivisionExact(subdivisionMatches, raw);
  if (exactSubdivision) {
    clearPlace();
    if (await api.select(exactSubdivision.id, { fit:true })) return true;
  }

  const exactCity = cityExact(cities, raw);
  if (exactCity && await focusCity(exactCity)) return true;

  const country = countryMatch(raw, false);
  if (country) return activateCountry(country);

  const subdivision = subdivisionMatches[0] || null;
  if (subdivision) {
    clearPlace();
    if (await api.select(subdivision.id, { fit:true })) return true;
  }

  const city = cities[0] || null;
  if (city && await focusCity(city)) return true;
  return false;
}

async function warmPlaces() {
  const [subdivisionRows, cityRowsResult] = await Promise.all([warmSubdivisions(), warmCities()]);
  return { subdivisions:subdivisionRows, cities:cityRowsResult };
}

// Capture Enter before the original country-only handler. We own the complete
// route only after the country datalist is populated; before that, the core
// handler remains the safe fallback during very early startup.
input.addEventListener('keydown', event => {
  if (event.key !== 'Enter' || countryCandidates().length === 0) return;
  event.preventDefault();
  event.stopImmediatePropagation();
  submit(input.value).then(handled => {
    if (!handled) input.setCustomValidity('No matching country, supported subdivision, or indexed city.');
    else input.setCustomValidity('');
  }).catch(error => {
    input.setCustomValidity('Place search is temporarily unavailable.');
    console.warn('Place search failed:', error);
  });
}, true);

input.addEventListener('input', () => {
  input.setCustomValidity('');
  if (input.value.trim().length >= 2) warmPlaces();
}, { passive:true });
input.addEventListener('focus', () => warmPlaces(), { once:true, passive:true });

window.__potatoAtlasPlaceSearch = {
  submit,
  warm:warmPlaces,
  countries:countryCandidates,
  cities:searchCities,
  focusCity,
  clearPlace,
};

restoreRequestedPlace();
window.dispatchEvent(new CustomEvent('potato-atlas-place-search-ready'));
