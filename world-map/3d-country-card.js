// Compact contextual country card for ordinary World Map exploration.
// It reads canonical country dossiers and active registry state; it does not
// become a second country database. Deeper investigation stays contextual:
// actions only appear after a country is selected.

const layers = window.__potatoAtlasLayers;
const selection = window.__potatoAtlasSelection;
if (!layers || !selection) throw new Error('Country card requires registry and selection APIs.');
await layers.ready;

const INDEX_URL = '../data/countries/index.json';
const DEMOGRAPHY_URL = '../data/world-country-demography.json';

let index = null;
let demography = null;
let renderedCode = null;
const records = new Map();

const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
}[char]));

async function fetchJson(url) {
  const response = await fetch(url, { cache: 'no-cache' });
  if (!response.ok) throw new Error(`${response.status} ${url}`);
  return response.json();
}
async function indexData() { if (!index) index = await fetchJson(INDEX_URL); return index; }
async function demographyData() { if (!demography) demography = await fetchJson(DEMOGRAPHY_URL); return demography; }

function formatNumber(value, maximumFractionDigits = 1) {
  const number = Number(value);
  if (!Number.isFinite(number)) return '—';
  return new Intl.NumberFormat(undefined, { maximumFractionDigits }).format(number);
}
function formatCompact(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return '—';
  return new Intl.NumberFormat(undefined, { notation: 'compact', maximumFractionDigits: 1 }).format(number);
}
function observation(record, field) {
  const item = record?.observations?.[field];
  return item && item.value !== undefined && item.value !== null ? item.value : null;
}
function observationYear(record, field) { return record?.observations?.[field]?.year || ''; }
function sourceMeta(record, field) {
  const item = record?.observations?.[field];
  if (!item) return null;
  return { source:item.source || null, year:item.year || null, confidence:item.confidence || null };
}
function countryFromCode(code, idx) {
  const key = String(code || '').trim().toLowerCase();
  return idx.countries?.find(item => item.id === key || String(item.iso2 || '').toLowerCase() === key || String(item.iso3 || '').toLowerCase() === key) || null;
}
async function recordFor(country) {
  if (!country?.id) return null;
  if (records.has(country.id)) return records.get(country.id);
  try {
    const record = await fetchJson(`../data/countries/${country.id}.json`);
    records.set(country.id, record);
    return record;
  } catch {
    records.set(country.id, null);
    return null;
  }
}
function demographicFor(country, demo) {
  if (!country) return null;
  return demo?.countries?.[String(country.iso3 || '').toUpperCase()] || demo?.countries?.[country.id] || null;
}
function groupName(layerId) {
  return layers.getLayer?.(layerId)?.name || layerId;
}
function membershipsFor(countryId) {
  const resolver = layers.resolver;
  const active = layers.getActiveLayers?.() || [];
  if (!resolver || !countryId) return [];
  const memberships = [];
  for (const layer of active) {
    if (layer.kind !== 'group' || !layer.source_key) continue;
    const members = resolver.membersForGroup?.(layer.source_key) || [];
    if (members.includes(countryId)) memberships.push(groupName(layer.id));
  }
  return memberships;
}
function activeStats() {
  return (layers.getActiveLayers?.() || []).filter(layer => layer.kind === 'stat');
}
function statRows(countryId) {
  const resolver = layers.resolver;
  if (!resolver) return [];
  return activeStats().map(layer => {
    const result = resolver.scalarForCountry?.(layer.source_key, countryId) || { value:null, metadata:{} };
    return { layer, result };
  }).filter(item => item.result.value !== null && item.result.value !== undefined);
}
function signal(title, value, meta = null) {
  const foot = meta ? [meta.year, meta.source, meta.confidence].filter(Boolean).join(' · ') : '';
  return `<div class="country-card-signal"><span>${esc(title)}</span><strong>${esc(value)}</strong>${foot ? `<small>${esc(foot)}</small>` : ''}</div>`;
}
function openInspector() {
  window.__potatoAtlasPanel?.open?.();
  window.__potatoAtlasSelection?.inspect?.();
}
async function ensureTrace() {
  if (window.__potatoEntityTrace) return window.__potatoEntityTrace;
  const loader = window.__potatoAtlasLoadModule;
  if (typeof loader !== 'function') throw new Error('Atlas module loader unavailable.');
  await loader('./3d-entity-trace.js');
  if (!window.__potatoEntityTrace) throw new Error('Entity Trace failed to initialize.');
  return window.__potatoEntityTrace;
}
async function toggleTrace(button) {
  try {
    window.__potatoAtlasPanel?.open?.();
    const trace = await ensureTrace();
    trace.toggle?.();
    button?.classList.toggle('active', Boolean(trace.isEnabled?.()));
  } catch (error) {
    console.warn('[country-card] trace unavailable', error);
  }
}
function wireActions(root) {
  root?.querySelector('[data-country-action="inspect"]')?.addEventListener('click', openInspector);
  root?.querySelector('[data-country-action="trace"]')?.addEventListener('click', event => toggleTrace(event.currentTarget));
}
function actionRows() {
  return `<div class="country-card-actions"><button type="button" data-country-action="inspect">More country data</button><button type="button" data-country-action="trace" class="${window.__potatoEntityTrace?.isEnabled?.() ? 'active' : ''}">Trace connections</button></div>`;
}
async function render() {
  const root = document.getElementById('countryCard');
  if (!root) return;
  const code = selection.primary;
  if (!code) {
    renderedCode = null;
    root.innerHTML = '<div class="country-card-empty">Select a country to inspect it.</div>';
    return;
  }
  const [idx, demo] = await Promise.all([indexData(), demographyData().catch(() => null)]);
  if (selection.primary !== code) return;
  const country = countryFromCode(code, idx);
  if (!country) {
    root.innerHTML = `<div class="country-card-empty">No canonical country record for ${esc(code)}.</div>`;
    return;
  }
  const record = await recordFor(country);
  if (selection.primary !== code) return;
  const demographic = demographicFor(country, demo);
  const population = observation(record, 'population') ?? demographic?.population ?? null;
  const gdp = observation(record, 'gdp');
  const area = record?.identity?.area_km2 ?? country.area_km2 ?? null;
  const memberships = membershipsFor(country.id);
  const stats = statRows(country.id);
  const populationMeta = sourceMeta(record, 'population');
  const gdpMeta = sourceMeta(record, 'gdp');
  const populationYear = observationYear(record, 'population');

  root.innerHTML = `<div class="country-card-head"><div><span>${esc(country.iso3 || '')}</span><h3>${esc(country.name || country.id)}</h3></div><button type="button" data-country-clear aria-label="Deselect ${esc(country.name || country.id)}">×</button></div><div class="country-card-grid">${population !== null ? signal('Population', formatCompact(population), populationMeta || (populationYear ? { year:populationYear } : null)) : ''}${area !== null ? signal('Area', `${formatNumber(area)} km²`) : ''}${gdp !== null ? signal('GDP', formatCompact(gdp), gdpMeta) : ''}${stats.map(({ layer, result }) => signal(layer.name, formatCompact(result.value), result.metadata)).join('')}</div>${memberships.length ? `<div class="country-card-memberships"><span>Active memberships</span><div>${memberships.map(name => `<b>${esc(name)}</b>`).join('')}</div></div>` : ''}${demographic?.religions ? `<div class="country-card-memberships"><span>Religion composition</span><div>${Object.entries(demographic.religions).sort((a,b)=>Number(b[1])-Number(a[1])).slice(0,5).map(([name,value]) => `<b>${esc(name)} ${esc(formatNumber(value,1))}%</b>`).join('')}</div></div>` : ''}${actionRows()}`;
  root.querySelector('[data-country-clear]')?.addEventListener('click', () => selection.toggle(code));
  wireActions(root);
  renderedCode = code;
}

window.addEventListener('potato-atlas-working-selection-change', render);
window.addEventListener('potato-atlas-layer-registry-change', render);
window.addEventListener('potato-atlas-entity-trace-change', render);
render();
