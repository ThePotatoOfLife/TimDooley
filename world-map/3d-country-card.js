// Selected-country workspace for ordinary World Map exploration.
// Selection owns the persistent subject, Country Presentation normalizes shared
// summary data, and the Inspector remains the deep-dive surface.

const layers = window.__potatoAtlasLayers;
const selection = window.__potatoAtlasSelection;
const presentation = window.__potatoAtlasCountryPresentation;
if (!layers || !selection || !presentation) throw new Error('Country card requires registry, selection and Country Presentation APIs.');
await layers.ready;

const INDEX_URL = '../data/countries/index.json';
const RELATION_LABELS = { all:'All context', money:'Money', systems:'Systems', institutions:'Institutions', project:'Project', other:'Other' };
let index = null;
let renderedCode = null;
let renderVersion = 0;
let renderScheduled = false;
let pendingRenderCode = null;
let activeTab = 'overview';
const records = new Map();

const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
async function fetchJson(url) { const response = await fetch(url, { cache:'no-cache' }); if (!response.ok) throw new Error(`${response.status} ${url}`); return response.json(); }
async function indexData() { if (!index) index = await fetchJson(INDEX_URL); return index; }
function runtime() { return window.__potatoAtlasDataRuntime; }
async function populationObservation(code) { return runtime()?.populationObservation?.(code) || null; }
async function areaObservation(code) { return runtime()?.areaObservation?.(code) || null; }
function observation(record, key) {
  const value = record?.observations?.[key];
  return value && typeof value === 'object' && 'value' in value ? value : null;
}
function formatNumber(value, maximumFractionDigits = 1) {
  if (value == null || value === '') return '—';
  const number = Number(value);
  if (!Number.isFinite(number)) return '—';
  return new Intl.NumberFormat(undefined, { maximumFractionDigits }).format(number);
}
function formatObservation(cell) {
  if (!cell || cell.value == null || !Number.isFinite(Number(cell.value))) return '—';
  const value = Number(cell.value);
  const unit = String(cell.unit || '');
  if (unit.includes('USD') || unit.includes('international $')) return new Intl.NumberFormat(undefined, { style:'currency', currency:'USD', maximumFractionDigits:0 }).format(value);
  if (unit.includes('percent')) return `${formatNumber(value, 1)}%`;
  return `${formatNumber(value, 1)}${unit ? ` ${unit}` : ''}`;
}
function flagEmoji(iso2) {
  const code = String(iso2 || '').toUpperCase();
  if (!/^[A-Z]{2}$/.test(code)) return '🌐';
  return [...code].map(char => String.fromCodePoint(127397 + char.charCodeAt(0))).join('');
}
async function countryRecord(code) {
  if (records.has(code)) return records.get(code);
  const data = await indexData();
  const row = (data?.countries || []).find(item => item.iso3 === code);
  if (!row?.id) return null;
  try {
    const record = await fetchJson(`../data/countries/${row.id}.json`);
    records.set(code, record);
    return record;
  } catch { return null; }
}

async function defaultMetrics(code, record, shared) {
  const population = await populationObservation(code);
  const area = await areaObservation(code);
  const gdp = observation(record, 'gdp');
  const gdpPerCapita = observation(record, 'gdp_per_capita');
  const growth = observation(record, 'real_growth') || observation(record, 'real_gdp_growth');
  const inflation = observation(record, 'inflation');
  const unemployment = observation(record, 'unemployment');
  return [
    ['Population', shared?.population?.display || presentation.formatPopulation(population?.value)],
    ['GDP', formatObservation(gdp)],
    ['GDP per capita', formatObservation(gdpPerCapita)],
    ['Growth', formatObservation(growth)],
    ['Inflation', formatObservation(inflation)],
    ['Unemployment', formatObservation(unemployment)],
    ['Area', shared?.identity?.area?.display || presentation.formatArea(area?.value)],
  ];
}

async function axisContext(code) {
  const profile = await runtime()?.axisProfile?.(code) || { status:'unresolved', orientations:[] };
  const orientations = (profile.orientations || []).filter(item => item?.role !== 'unresolved').slice(0, 4);
  const chains = await runtime()?.chainsForCountry?.(code) || [];
  return { profile, orientations, chains };
}

function connectionRows(code) {
  return (selection.connectionsFor?.(code, 6) || []).map(edge => {
    const partner = edge.a === code ? edge.b : edge.a;
    const types = (edge.types || []).map(type => String(type).replaceAll('-', ' '));
    return { partner, name:selection.countryName?.(partner) || partner, types:types.length ? types.join(' · ') : String(edge.layer || 'relation').replaceAll('-', ' ') };
  });
}

async function contextualRows(code, shared = null) {
  const result = [];
  const memberships = shared?.memberships?.memberships || [];
  if (memberships.length) {
    result.push([`${String(shared.memberships.mode || 'any').toUpperCase()} set query`, shared.memberships.matches ? 'Matches' : 'Outside']);
    result.push(['Active sets', memberships.map(item => `${item.label}: ${item.member ? 'yes' : 'no'}`).join(' · ')]);
  }
  const axisLayers = layers.active().filter(id => String(id).startsWith('axis.'));
  if (axisLayers.length) {
    const axis = await axisContext(code);
    if (axis.orientations.length) result.push(['Axis orientation', axis.orientations.map(item => `${item.axis}: ${item.role}`).join(' · ')]);
    if (axis.chains.length) result.push(['Functional chains', axis.chains.slice(0, 3).map(item => item.label).join(' · ')]);
  }
  return result;
}

// Retained public helper for compatibility with older callers. Pinned comparison
// presentation now belongs to 3d-pinned-context.js, not the selected-country card.
async function comparisonRows(codes) {
  const unique = [...new Set((codes || []).map(code => String(code || '').toUpperCase()).filter(code => /^[A-Z]{3}$/.test(code)))];
  return Promise.all(unique.slice(0, 6).map(code => presentation.forCountry(code)));
}

function currentAnswerHtml(shared) {
  const answer = shared?.answer;
  if (!answer || answer.kind === 'none' || answer.status === 'neutral') return '';
  // Population is already a permanent orientation field. When it is the active
  // scalar, source/period are attached there instead of rendering the same value twice.
  if (answer.populationPrimary) return '';
  if (answer.kind === 'scalar') {
    const meta = [answer.period, answer.source].filter(Boolean).join(' · ');
    return `<section class="atlas-country-current-answer" data-answer-kind="scalar"><small>Current map</small><span>${esc(answer.label)}</span><strong>${esc(answer.display || 'Unknown')}</strong>${meta ? `<em>${esc(meta)}</em>` : ''}</section>`;
  }
  const memberships = answer.memberships?.memberships || [];
  return `<section class="atlas-country-current-answer" data-answer-kind="set"><small>Current map</small><span>${esc(answer.label || 'Set query')}</span><strong>${esc(answer.display || 'Outside')}</strong>${memberships.length ? `<em>${esc(memberships.map(item => `${item.label}: ${item.member ? 'yes' : 'no'}`).join(' · '))}</em>` : ''}</section>`;
}

function governmentRows(record) {
  const political = record?.political_system || {};
  const rows = [];
  if (political.system_type) rows.push(['System', political.system_type]);
  const leader = political.current_leader?.name;
  const office = political.current_leader?.office || political.head_of_government || 'Leader';
  if (leader) rows.push([office, leader]);
  if (political.head_of_state && political.head_of_state !== leader) rows.push(['Head of state', political.head_of_state]);
  return rows.slice(0, 3);
}

function activateTab(tab) {
  const card = document.getElementById('atlasCountryCard');
  if (!card || !['overview','context','connections'].includes(tab)) return;
  activeTab = tab;
  card.querySelectorAll('[data-country-tab]').forEach(button => {
    const selected = button.dataset.countryTab === tab;
    button.classList.toggle('active', selected);
    button.setAttribute('aria-selected', selected ? 'true' : 'false');
  });
  card.querySelectorAll('.atlas-country-tab-panel').forEach(panel => { panel.hidden = panel.dataset.countryPanel !== tab; });
}

function openInspector() { document.getElementById('atlasApp')?.classList.remove('panel-collapsed'); }
async function showDetails() { selection.inspect?.(); openInspector(); }
async function showStatistics() {
  const code = selection.current?.activeCode || selection.current?.code;
  if (!code) return;
  await showDetails();
  if (!window.__potatoAtlasCountryPulse) {
    if (window.__potatoAtlasLoadModule) await window.__potatoAtlasLoadModule('Country Pulse', './3d-country-pulse.js');
    else await import('./3d-country-pulse.js').catch(() => false);
  }
  await window.__potatoAtlasCountryPulse?.render?.();
  document.querySelector('.atlas-country-pulse details:last-of-type')?.setAttribute('open', '');
}
async function toggleEntityTrace() {
  openInspector();
  const loaded = window.__potatoEntityTrace ? true : await (window.__potatoAtlasLoadModule ? window.__potatoAtlasLoadModule('Entity Trace', './3d-entity-trace.js') : import('./3d-entity-trace.js').then(() => true).catch(() => false));
  if (!loaded && !window.__potatoEntityTrace) return;
  window.__potatoEntityTrace?.toggle?.();
}
async function showPath() {
  const code = selection.current?.activeCode || selection.current?.code;
  if (!code) return;
  if (!window.__potatoAtlasPath) {
    if (window.__potatoAtlasLoadModule) await window.__potatoAtlasLoadModule('Path finder', './3d-pathfinder.js');
    else await import('./3d-pathfinder.js').catch(() => false);
  }
  window.__potatoAtlasPath?.showFor?.(code);
}
async function showImpact() {
  const code = selection.current?.activeCode || selection.current?.code;
  if (!code) return;
  if (!window.__potatoAtlasImpactTrace && window.__potatoAtlasLoadModule) await window.__potatoAtlasLoadModule('Impact Trace', './3d-impact-trace.js');
  await window.__potatoAtlasImpactTrace?.showEntity?.(code);
}
function syncTraceAction() {
  const button = document.querySelector('#atlasCountryCard [data-country-action="entity-trace"]');
  if (!button) return;
  const active = window.__potatoEntityTrace?.isEnabled?.() === true;
  button.classList.toggle('active', active);
  button.textContent = active ? 'Trace · on' : 'Trace';
}

function install() {
  if (document.getElementById('atlasCountryCard')) return;
  const style = document.createElement('style');
  style.id = 'atlasCountryCardStyle';
  style.textContent = `
    #atlasCountryCard{position:absolute;left:10px;top:10px;z-index:7;width:min(330px,calc(100% - 20px));max-height:calc(100% - 20px);overflow:auto;background:#0a1010ed;border:1px solid #344343;border-radius:13px;padding:11px;box-shadow:0 10px 30px #0009;backdrop-filter:blur(12px)}
    #atlasCountryCard[hidden]{display:none!important}.atlas-country-head{display:flex;align-items:flex-start;gap:9px}.atlas-country-flag{font-size:25px;line-height:1}.atlas-country-title{min-width:0;flex:1}.atlas-country-title b{display:block;font:400 18px/1.05 Georgia,serif}.atlas-country-title small{display:block;color:#9ea9a4;font-size:10px;margin-top:2px;line-height:1.35}.atlas-country-title .population-primary{color:#f0dfaa}.atlas-country-close{border:0!important;background:transparent!important;color:#9ea9a4!important;padding:1px 4px!important;min-height:0!important}.atlas-country-pin{margin-left:auto;min-height:25px;padding:3px 7px;border:1px solid #394844;border-radius:7px;background:#111918;color:#c4cec9;font-size:9px}.atlas-country-pin[aria-pressed="true"]{border-color:#d1b76f;color:#f3dfa4}.atlas-country-current-answer{margin-top:9px;padding:8px 9px;border:1px solid #4a5d58;border-radius:9px;background:#111a18}.atlas-country-current-answer small,.atlas-country-current-answer span,.atlas-country-current-answer strong,.atlas-country-current-answer em{display:block}.atlas-country-current-answer small{color:#9bac9f;font-size:8px;text-transform:uppercase;letter-spacing:.09em}.atlas-country-current-answer span{margin-top:2px;color:#aeb9b3;font-size:9px}.atlas-country-current-answer strong{margin-top:1px;color:#f0dfaa;font-size:16px}.atlas-country-current-answer em{margin-top:2px;color:#87948e;font-size:9px;font-style:normal}.atlas-country-tabs{display:grid;grid-template-columns:repeat(3,1fr);gap:4px;margin-top:9px}.atlas-country-tabs button{min-height:29px;padding:5px;border:1px solid #2d3937;border-radius:7px;background:#0f1615;color:#9eaaa4;font-size:9px}.atlas-country-tabs button.active{border-color:#617a73;background:#17201e;color:#e3ebe6}.atlas-country-tab-panel{margin-top:8px}.atlas-country-tab-panel[hidden]{display:none!important}.atlas-country-grid{display:grid;grid-template-columns:1fr 1fr;gap:5px}.atlas-country-metric{padding:6px;border:1px solid #273333;border-radius:8px;min-width:0}.atlas-country-metric span{display:block;color:#8f9c96;font-size:8px;text-transform:uppercase;letter-spacing:.05em}.atlas-country-metric b{display:block;margin-top:1px;font-size:11px;overflow-wrap:anywhere}.atlas-country-row{display:flex;justify-content:space-between;gap:9px;padding:5px 0;border-bottom:1px solid #202b2a;font-size:10px}.atlas-country-row:last-child{border:0}.atlas-country-row span{color:#9aa6a0}.atlas-country-row b{text-align:right;font-weight:600}.atlas-country-section{margin-top:8px}.atlas-country-section>small{display:block;color:#7f8d87;text-transform:uppercase;letter-spacing:.09em;font-size:8px;margin-bottom:3px}.atlas-country-tags{display:flex;flex-wrap:wrap;gap:4px}.atlas-country-tag{border:1px solid #2b3937;border-radius:999px;padding:2px 6px;font-size:9px;color:#bec8c3}.atlas-country-connection{display:grid;grid-template-columns:minmax(78px,.9fr) 1.3fr;gap:8px;padding:6px 0;border-bottom:1px solid #202b2a;font-size:10px}.atlas-country-connection:last-child{border:0}.atlas-country-connection button{border:0;background:transparent;color:#d9e2dc;text-align:left;padding:0;font-weight:600}.atlas-country-connection span{color:#909c96;text-align:right;overflow-wrap:anywhere}.atlas-country-empty{padding:8px 0;color:#7f8b85;font-size:10px}.atlas-country-actions{display:flex;flex-wrap:wrap;gap:5px;margin-top:9px;padding-top:8px;border-top:1px solid #273333}.atlas-country-actions button{flex:1 1 29%;min-height:29px;padding:5px 6px;background:#111918;border:1px solid #2e3a38;color:#bcc8c2;border-radius:7px;font-size:9px}.atlas-country-actions button:hover,.atlas-country-actions button.active{border-color:#708d83;color:#dff1d8;background:#17211f}.atlas-country-source{margin-top:7px;color:#75827c;font-size:8px}@media(max-width:900px){#atlasCountryCard{top:auto;bottom:8px;left:8px;right:8px;width:auto;max-height:44vh}}
  `;
  document.head.appendChild(style);
  const card = document.createElement('section');
  card.id = 'atlasCountryCard'; card.hidden = true; card.setAttribute('aria-live', 'polite');
  document.querySelector('.mapwrap')?.appendChild(card);
  card.addEventListener('click', event => {
    const tab = event.target.closest('[data-country-tab]')?.dataset.countryTab;
    if (tab) { activateTab(tab); return; }
    const partner = event.target.closest('[data-connection-country]')?.dataset.connectionCountry;
    if (partner) { selection.activate?.(partner); return; }
    const pin = event.target.closest('[data-atlas-pin]');
    if (pin) { selection.togglePinnedCountry?.(pin.dataset.atlasPin); return; }
    if (event.target.closest('[data-atlas-statistics]')) { showStatistics(); return; }
    const action = event.target.closest('[data-country-action]')?.dataset.countryAction;
    if (action === 'details') showDetails();
    if (action === 'entity-trace') toggleEntityTrace();
    if (action === 'path') showPath();
    if (action === 'impact') showImpact();
  });
}

async function render(code = selection.current?.activeCode || selection.current?.code) {
  code = String(code || '').toUpperCase();
  const card = document.getElementById('atlasCountryCard');
  if (!card) return;
  const version = ++renderVersion;
  if (!/^[A-Z]{3}$/.test(code)) { renderedCode = null; card.hidden = true; card.innerHTML = ''; return; }
  renderedCode = code;
  const [record, shared] = await Promise.all([countryRecord(code), presentation.forCountry(code)]);
  if (renderVersion !== version || renderedCode !== code || !shared) return;
  const [metrics, context] = await Promise.all([
    defaultMetrics(code, record || {}, shared),
    contextualRows(code, shared),
  ]);
  if (renderVersion !== version || renderedCode !== code) return;

  const identity = record?.identity || {};
  const government = governmentRows(record || {});
  const connections = connectionRows(code);
  const relationMode = shared.relation?.mode || selection.getRelationMode?.() || 'all';
  const pinned = selection.isPinned?.(code) === true;
  const populationMeta = shared.answer?.populationPrimary ? [shared.population?.period, shared.population?.source].filter(Boolean).join(' · ') : '';
  const refreshed = record?.coverage?.last_enriched || record?.updated || record?.provenance?.retrieved || record?.provenance?.last_refresh || '';
  const name = shared.identity?.name || identity.name || selection.countryName?.(code) || code;
  const capital = shared.identity?.capital || identity.capital || record?.capital || 'Capital unavailable';

  card.innerHTML = `
    <div class="atlas-country-head">
      <div class="atlas-country-flag" aria-hidden="true">${flagEmoji(identity.iso2 || record?.iso2)}</div>
      <div class="atlas-country-title"><b>${esc(name)}</b><small>${esc(code)} · ${esc(capital)}<br><span class="${shared.answer?.populationPrimary ? 'population-primary' : ''}">Population · ${esc(shared.population?.display || '—')}${populationMeta ? ` · ${esc(populationMeta)}` : ''}</span></small></div>
      <button class="atlas-country-pin" type="button" data-atlas-pin="${esc(code)}" aria-pressed="${pinned ? 'true' : 'false'}">${pinned ? 'Pinned' : 'Pin'}</button>
      <button class="atlas-country-close" type="button" aria-label="Close country card">×</button>
    </div>
    ${currentAnswerHtml(shared)}
    <div class="atlas-country-tabs" role="tablist" aria-label="Country information">
      <button type="button" data-country-tab="overview" role="tab">Overview</button>
      <button type="button" data-country-tab="context" role="tab">Context</button>
      <button type="button" data-country-tab="connections" role="tab">Connections</button>
    </div>
    <section class="atlas-country-tab-panel" data-country-panel="overview" role="tabpanel">
      <div class="atlas-country-grid">${metrics.map(([label,value]) => `<div class="atlas-country-metric"><span>${esc(label)}</span><b>${esc(value)}</b></div>`).join('')}</div>
      ${government.length ? `<div class="atlas-country-section"><small>Government / system identity</small>${government.map(([label,value]) => `<div class="atlas-country-row"><span>${esc(label)}</span><b>${esc(value)}</b></div>`).join('')}</div>` : ''}
    </section>
    <section class="atlas-country-tab-panel" data-country-panel="context" role="tabpanel">
      ${context.length ? `<div class="atlas-country-section"><small>Active map context</small>${context.map(([label,value]) => `<div class="atlas-country-row"><span>${esc(label)}</span><b>${esc(value)}</b></div>`).join('')}</div>` : '<div class="atlas-country-empty">No country-specific supporting context is active.</div>'}
      <div data-country-context-enrichments></div>
    </section>
    <section class="atlas-country-tab-panel" data-country-panel="connections" role="tabpanel">
      <div class="atlas-country-section"><small>${esc(RELATION_LABELS[relationMode] || relationMode)} · ${connections.length} represented</small>${connections.length ? connections.map(row => `<div class="atlas-country-connection"><button type="button" data-connection-country="${esc(row.partner)}">${esc(row.name)}</button><span>${esc(row.types)}</span></div>`).join('') : '<div class="atlas-country-empty">No represented relationships match this filter.</div>'}</div>
    </section>
    <div class="atlas-country-actions"><button type="button" data-atlas-statistics>Statistics</button><button type="button" data-country-action="details">More data</button><button type="button" data-country-action="entity-trace">Trace</button><button type="button" data-country-action="path">Path</button><button type="button" data-country-action="impact">Impact</button></div>
    <div class="atlas-country-source">${refreshed ? `Country record · ${esc(refreshed)}` : 'Country record'} · missing values remain unavailable</div>`;
  card.hidden = false;
  card.querySelector('.atlas-country-close')?.addEventListener('click', () => { card.hidden = true; });
  activateTab(activeTab);
  syncTraceAction();
  if (window.__potatoAtlasDiagnostics) window.__potatoAtlasDiagnostics.countryCardRenders = (window.__potatoAtlasDiagnostics.countryCardRenders || 0) + 1;
  window.dispatchEvent(new CustomEvent('potato-atlas-country-card-rendered', { detail:{ code, version, pinned, answer:shared.answer } }));
}

function scheduleRender(code = selection.current?.activeCode || selection.current?.code || '') {
  pendingRenderCode = String(code || '').toUpperCase();
  const diagnostics = window.__potatoAtlasDiagnostics;
  if (renderScheduled) {
    if (diagnostics) diagnostics.countryCardRenderCoalesced = (diagnostics.countryCardRenderCoalesced || 0) + 1;
    return;
  }
  renderScheduled = true;
  if (diagnostics) diagnostics.countryCardRenderSchedules = (diagnostics.countryCardRenderSchedules || 0) + 1;
  requestAnimationFrame(() => {
    renderScheduled = false;
    const nextCode = pendingRenderCode;
    pendingRenderCode = null;
    void render(nextCode);
  });
}

install();
window.addEventListener('potato-atlas-working-selection-change', event => scheduleRender(event?.detail?.activeCode || event?.detail?.code || ''));
window.addEventListener('potato-atlas-pin-change', () => { if (renderedCode) scheduleRender(renderedCode); });
window.addEventListener('potato-atlas-active-view-change', event => {
  const code = event?.detail?.code;
  if (!code || code === renderedCode || code === pendingRenderCode) scheduleRender(code || renderedCode || '');
});
window.addEventListener('potato-atlas-query-change', () => { if (renderedCode) scheduleRender(renderedCode); });
window.addEventListener('potato-atlas-relation-mode-change', () => { if (renderedCode) scheduleRender(renderedCode); });
window.addEventListener('potato-atlas-entity-trace-change', syncTraceAction);
if (selection.current?.selected) scheduleRender(selection.current.activeCode || selection.current.code);

window.__potatoAtlasCountryCard = {
  render,
  scheduleRender,
  comparisonRows,
  connectionRows,
  contextualRows,
  axisContext,
  activateTab,
  close() { const card = document.getElementById('atlasCountryCard'); if (card) card.hidden = true; },
};
