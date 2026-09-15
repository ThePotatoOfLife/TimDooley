// Unified country/place search for the World Relational Atlas.
// Reuses the existing #search input and delegates navigation to subsystem owners.

const input = document.getElementById('search');
const COUNTRY_INDEX_URL = '../data/countries/index.json';
let countriesPromise = null;
let lastResults = [];

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
    lastResults = [];
    return [];
  }
  const limit = Math.max(1, Math.min(30, Number(options.limit) || 12));
  const rows = await countryRows();
  const countries = rows.map(row => countryResult(row, needle)).filter(Boolean);
  const places = placeResults(needle, limit);
  lastResults = [...countries, ...places]
    .sort((a, b) => a.score - b.score || (a.type === 'Country' ? -1 : 1) || a.name.localeCompare(b.name))
    .slice(0, limit);
  return lastResults;
}
async function focus(result) {
  if (!result) return false;
  if (result.type === 'Country') {
    const code = String(result.country || result.id || '').toUpperCase();
    if (!code || !window.goCountry) return false;
    window.goCountry(code);
    return true;
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
  const exact = results.find(result => scoreName(result.name, normalize(query)) === 0 || normalize(result.id) === normalize(query));
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
  input.title = 'Search countries, capitals, cities and towns · press / to focus';
  return list;
}
function renderSuggestions(results) {
  const list = installDatalist();
  if (!list) return;
  list.replaceChildren(...results.slice(0, 10).map(result => {
    const option = document.createElement('option');
    option.value = result.name;
    option.label = `${result.type}${result.country ? ` · ${result.country}` : ''}`;
    return option;
  }));
}

if (input) {
  installDatalist();
  input.addEventListener('input', async event => {
    renderSuggestions(await search(event.target.value, {limit:10}));
  });
  input.addEventListener('keydown', async event => {
    if (event.key !== 'Enter') return;
    const handled = await submit(event.target.value);
    if (!handled) return;
    event.preventDefault();
    event.stopImmediatePropagation();
  }, true);
}

window.__potatoAtlasSearch = {
  search,
  focus,
  submit,
  get results() { return [...lastResults]; },
};

window.dispatchEvent(new CustomEvent('potato-atlas-search-ready'));
