// Unified country/subdivision/place search for the World Relational Atlas.
// Reuses the existing #search input and delegates navigation to subsystem owners.

const input = document.getElementById('search');
const COUNTRY_INDEX_URL = '../data/countries/index.json';
const SUBDIVISION_INDEX_URL = '../data/world-subdivisions/index.json';
const TYPE_RANK = Object.freeze({ Country:0, State:1, Region:1, District:1, Subdivision:1, Capital:2, City:3, Town:4 });
let countriesPromise = null;
let subdivisionsPromise = null;
let lastResults = [];
let suggestionGeneration = 0;

function normalize(value) {
  return String(value || '').trim().toLowerCase();
}
function scoreName(name, query) {
  const value = normalize(name);
  if (!value || !query) return 99;
  if (value === query) return 0;
  if (value.startsWith(query)) return 1;
  if (value.includes(query)) return 2;
  return 99;
}
function typeRank(type) {
  return TYPE_RANK[type] ?? 9;
}
function compareResults(a, b) {
  return a.score - b.score
    || typeRank(a.type) - typeRank(b.type)
    || String(a.name || '').localeCompare(String(b.name || ''))
    || String(a.id || '').localeCompare(String(b.id || ''));
}
function countryRows() {
  if (!countriesPromise) {
    countriesPromise = fetch(COUNTRY_INDEX_URL, {cache:'force-cache'})
      .then(response => {
        if (!response.ok) throw new Error(`Country index unavailable (${response.status})`);
        return response.json();
      })
      .then(payload => Array.isArray(payload) ? payload : (payload.countries || payload.items || []))
      .catch(error => {
        console.warn('Unified search country index unavailable:', error);
        return [];
      });
  }
  return countriesPromise;
}
function subdivisionRows() {
  if (!subdivisionsPromise) {
    subdivisionsPromise = fetch(SUBDIVISION_INDEX_URL, {cache:'force-cache'})
      .then(response => {
        if (!response.ok) throw new Error(`Subdivision index unavailable (${response.status})`);
        return response.json();
      })
      .then(payload => Object.values(payload?.partitions || {})
        .flatMap(descriptor => Array.isArray(descriptor?.search_records) ? descriptor.search_records : []))
      .catch(error => {
        console.warn('Unified search subdivision index unavailable:', error);
        return [];
      });
  }
  return subdivisionsPromise;
}
function countryResult(row, query) {
  const iso3 = String(row.iso3 || row.cca3 || row.code || '').toUpperCase();
  const iso2 = String(row.iso2 || '').toUpperCase();
  const name = row.name || row.label || iso3;
  const aliases = Array.isArray(row.aliases) ? row.aliases : [];
  const best = Math.min(
    scoreName(name, query),
    scoreName(iso3, query),
    scoreName(iso2, query),
    ...aliases.map(alias => scoreName(alias, query))
  );
  return best < 99 ? { type:'Country', id:iso3, name, country:iso3, score:best, row } : null;
}
function subdivisionType(row = {}) {
  const type = normalize(row.subdivision_type);
  if (type === 'state') return 'State';
  if (type === 'region') return 'Region';
  if (type === 'federal district' || type === 'district') return 'District';
  return 'Subdivision';
}
function subdivisionResult(row, query) {
  const id = String(row.id || '');
  const name = row.name || id;
  const code = String(row.code || '');
  const aliases = Array.isArray(row.aliases) ? row.aliases : [];
  const best = Math.min(
    scoreName(name, query),
    scoreName(code, query),
    scoreName(id, query),
    ...aliases.map(alias => scoreName(alias, query))
  );
  if (best >= 99) return null;
  return {
    type:subdivisionType(row),
    kind:'Subdivision',
    id,
    name,
    country:String(row.parent_iso3 || '').toUpperCase(),
    parentName:row.parent_name || '',
    score:best,
    row,
  };
}
function placeResults(query, limit) {
  const api = window.__potatoAtlasPlaces;
  if (!api?.search) return [];
  return api.search(query, {limit}).map(result => ({
    type:['Capital','City','Town'].includes(result.type) ? result.type : 'City',
    id:result.id,
    name:result.name,
    country:result.country,
    score:scoreName(result.name, query),
    feature:result.feature,
  }));
}
async function search(query, options = {}) {
  const needle = normalize(query);
  if (!needle) {
    if (options.store !== false) lastResults = [];
    return [];
  }
  const limit = Math.max(1, Math.min(30, Number(options.limit) || 12));
  const [countryRowsLoaded, subdivisionRowsLoaded] = await Promise.all([countryRows(), subdivisionRows()]);
  const countries = countryRowsLoaded.map(row => countryResult(row, needle)).filter(Boolean);
  const subdivisions = subdivisionRowsLoaded.map(row => subdivisionResult(row, needle)).filter(Boolean);
  const places = placeResults(needle, limit);
  const results = [...countries, ...subdivisions, ...places]
    .sort(compareResults)
    .slice(0, limit);
  if (options.store !== false) lastResults = results;
  return results;
}
async function focus(result) {
  if (!result) return false;
  if (result.type === 'Country') {
    const code = String(result.country || result.id || '').toUpperCase();
    if (!code || !window.goCountry) return false;
    window.goCountry(code);
    return true;
  }
  if (result.kind === 'Subdivision' || ['State','Region','District','Subdivision'].includes(result.type)) {
    return Boolean(await window.__potatoAtlasSubdivisions?.select?.(result.id, {fit:true}));
  }
  if (['Capital','City','Town'].includes(result.type)) {
    return Boolean(await window.__potatoAtlasPlaces?.focus?.(result.id, {
      country:result.country,
      feature:result.feature,
      fit:true,
    }));
  }
  return false;
}
async function submit(query) {
  const results = await search(query, {limit:12});
  if (!results.length) return false;
  const needle = normalize(query);
  const exact = results.find(result => scoreName(result.name, needle) === 0 || normalize(result.id) === needle || normalize(result.row?.code) === needle);
  return focus(exact || results[0]);
}

function installDatalist() {
  if (!input) return null;
  let list = document.getElementById('atlasUnifiedSearchOptions');
  if (!list) {
    list = document.createElement('datalist');
    list.id = 'atlasUnifiedSearchOptions';
    document.body.appendChild(list);
  }
  input.setAttribute('list', list.id);
  input.title = 'Search countries, states, regions, capitals, cities and towns · press / to focus';
  return list;
}
function renderSuggestions(results) {
  const list = installDatalist();
  if (!list) return;
  list.replaceChildren(...results.slice(0, 10).map(result => {
    const option = document.createElement('option');
    option.value = result.name;
    const context = result.parentName || result.country;
    option.label = `${result.type}${context ? ` · ${context}` : ''}`;
    return option;
  }));
}

if (input) {
  installDatalist();
  input.addEventListener('input', async event => {
    const generation = ++suggestionGeneration;
    const results = await search(event.target.value, {limit:10, store:false});
    if (generation !== suggestionGeneration) {
      if (window.__potatoAtlasDiagnostics) {
        window.__potatoAtlasDiagnostics.staleSearchSuppressions = (window.__potatoAtlasDiagnostics.staleSearchSuppressions || 0) + 1;
      }
      return;
    }
    lastResults = results;
    renderSuggestions(results);
  });
  input.addEventListener('keydown', event => {
    if (event.key !== 'Enter') return;
    event.preventDefault();
    event.stopImmediatePropagation();
    void submit(event.target.value);
  }, true);
}

window.__potatoAtlasSearch = {
  search,
  focus,
  submit,
  get results() { return [...lastResults]; },
};

window.dispatchEvent(new CustomEvent('potato-atlas-search-ready'));
