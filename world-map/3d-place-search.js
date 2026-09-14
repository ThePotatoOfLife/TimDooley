// Unified geographic search for the World Relational Atlas.
//
// This controller deliberately reuses the existing header search box. Countries
// stay owned by the canonical selection controller; subdivisions stay owned by
// the subdivision module. Later populated-place data plugs into this same seam.

const input = document.getElementById('search');
const countryList = document.getElementById('country-list');

if (!input) throw new Error('Place search requires the existing atlas search input.');

input.placeholder = 'Find place…';
input.setAttribute('aria-label', 'Find place');
input.title = 'Find a country, state, or city';

const normalize = value => String(value || '').trim().toLocaleLowerCase('en').normalize('NFKD').replace(/[\u0300-\u036f]/g, '');

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

async function activateCountry(candidate) {
  if (!candidate) return false;
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

async function submit(query) {
  const raw = String(query || '').trim();
  if (!raw) return false;

  // Preserve the long-established country interpretation for exact country names
  // and ISO3 codes. This also keeps ambiguous "Georgia" resolving to the country;
  // the U.S. state remains explicit as GA / US-GA / Georgia (US-GA).
  const exactCountry = countryMatch(raw, true);
  if (exactCountry) return activateCountry(exactCountry);

  const api = await subdivisions();
  if (api?.search) {
    const matches = await api.search(raw);
    addSubdivisionSuggestions(matches);
    const exactSubdivision = subdivisionExact(matches, raw);
    const subdivision = exactSubdivision || matches[0] || null;
    if (subdivision && await api.select(subdivision.id, { fit:true })) return true;
  }

  const country = countryMatch(raw, false);
  if (country) return activateCountry(country);
  return false;
}

// Capture Enter before the original country-only handler. We own the complete
// route only after the country datalist is populated; before that, the core
// handler remains the safe fallback during very early startup.
input.addEventListener('keydown', event => {
  if (event.key !== 'Enter' || countryCandidates().length === 0) return;
  event.preventDefault();
  event.stopImmediatePropagation();
  submit(input.value).then(handled => {
    if (!handled) input.setCustomValidity('No matching country or supported subdivision.');
    else input.setCustomValidity('');
  }).catch(error => {
    input.setCustomValidity('Place search is temporarily unavailable.');
    console.warn('Place search failed:', error);
  });
}, true);

input.addEventListener('input', () => {
  input.setCustomValidity('');
  if (input.value.trim().length >= 2) warmSubdivisions();
}, { passive:true });
input.addEventListener('focus', () => warmSubdivisions(), { once:true, passive:true });

window.__potatoAtlasPlaceSearch = {
  submit,
  warm:warmSubdivisions,
  countries:countryCandidates,
};

window.dispatchEvent(new CustomEvent('potato-atlas-place-search-ready'));
