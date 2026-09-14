const ATLAS_VERSION = new URL(import.meta.url).searchParams.get('v') || '';
function versionedModule(path) {
  if (!ATLAS_VERSION) return path;
  const url = new URL(path, import.meta.url);
  url.searchParams.set('v', ATLAS_VERSION);
  return url.href;
}
const {buildSearchRecords, rankSearchRecords, subdivisionSearchRows} = await import(versionedModule('./3d-search-core.js'));

const input = document.getElementById('search');
const datalist = document.getElementById('country-list');
const COUNTRY_INDEX = '../data/countries/index.json';
const CITY_URL = '../data/world-cities.geo.json';
const CAPITAL_URL = '../data/world-capitals.geo.json';
const SUBDIVISION_INDEX = '../data/world-subdivisions/index.json';
let records = [];
let loadPromise = null;
let suggestionByDisplay = new Map();

async function fetchJson(url) {
  const response = await fetch(url, {cache:'force-cache'});
  if (!response.ok) throw new Error(`${response.status} ${url}`);
  return response.json();
}

function countryRows(payload) {
  return Array.isArray(payload) ? payload : (payload?.countries || payload?.items || []);
}

function capitalFallbackPlaces(payload) {
  return (payload?.features || []).map(feature => {
    const p = feature?.properties || {};
    const iso3 = String(p.iso3 || '').toUpperCase();
    const name = String(p.name || '').trim();
    return {id:`cap:${iso3}:${name.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')}`,name,iso3,country:p.country || iso3,capital:Boolean(p.primary),aliases:[]};
  }).filter(place => place.id && place.name && place.iso3);
}

async function loadPlacesForSearch() {
  try {
    const payload = await fetchJson(CITY_URL);
    return (payload.features || []).map(feature => feature.properties || {}).filter(p => p.id && p.name && p.iso3);
  } catch {
    return capitalFallbackPlaces(await fetchJson(CAPITAL_URL));
  }
}

async function loadSubdivisionsForSearch() {
  try {
    return subdivisionSearchRows(await fetchJson(SUBDIVISION_INDEX));
  } catch (error) {
    console.warn('Subdivision search manifest unavailable.', error);
    return [];
  }
}

async function ensureRecords() {
  if (loadPromise) return loadPromise;
  loadPromise = (async () => {
    const [countriesPayload, subdivisions, places] = await Promise.all([fetchJson(COUNTRY_INDEX),loadSubdivisionsForSearch(),loadPlacesForSearch()]);
    records = buildSearchRecords({countries:countryRows(countriesPayload),subdivisions,places});
    return records;
  })();
  return loadPromise;
}

function refreshSuggestions(text) {
  if (!datalist) return [];
  const matches = rankSearchRecords(records, text, 12);
  suggestionByDisplay = new Map();
  datalist.innerHTML = '';
  for (const record of matches) {
    suggestionByDisplay.set(record.display, record);
    suggestionByDisplay.set(record.name, record);
    const option = document.createElement('option');
    option.value = record.display;
    option.label = record.display;
    datalist.appendChild(option);
  }
  return matches;
}

async function ensureModule(label, path, globalName) {
  if (window[globalName]) return true;
  await window.__potatoAtlasLoadModule?.(label, path);
  return Boolean(window[globalName]);
}

async function activate(record) {
  if (!record) return false;
  if (record.type === 'country') {
    if (window.goCountry) { await window.goCountry(record.id); return true; }
    return false;
  }
  if (record.type === 'subdivision') {
    await ensureModule('Subdivisions','./3d-subdivisions.js','__potatoAtlasSubdivisions');
    return Boolean(await window.__potatoAtlasSubdivisions?.select?.(record.id));
  }
  if (record.type === 'city') {
    await ensureModule('Places','./3d-places.js','__potatoAtlasPlaces');
    return Boolean(await window.__potatoAtlasPlaces?.select?.(record.id));
  }
  return false;
}

async function query(text, limit=12) {
  await ensureRecords();
  return rankSearchRecords(records,text,limit);
}

async function chosenRecord(value) {
  await ensureRecords();
  return suggestionByDisplay.get(value) || rankSearchRecords(records,value,1)[0] || null;
}

if (input) {
  input.placeholder = 'Find country, state, region or city…';
  input.setAttribute('aria-label','Find country, subdivision or city');
  input.addEventListener('focus', async () => { await ensureRecords(); refreshSuggestions(input.value); });
  input.addEventListener('input', async () => { await ensureRecords(); refreshSuggestions(input.value); });
  input.addEventListener('keydown', async event => {
    if (event.key !== 'Enter') return;
    const record = await chosenRecord(input.value);
    if (!record) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    await activate(record);
    input.value = record.display;
  }, true);
}

window.__potatoAtlasSearch = {ready:Promise.resolve(true),load:ensureRecords,query,activate,refreshSuggestions};
