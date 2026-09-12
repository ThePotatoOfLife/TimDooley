// Compact contextual country card for ordinary World Map exploration.
// Canonical dossiers own country detail; the shared map runtime owns comparable
// empirical scalars, institutional memberships, Axis profiles and functional chains.

const layers = window.__potatoAtlasLayers;
const selection = window.__potatoAtlasSelection;
if (!layers || !selection) throw new Error('Country card requires registry and selection APIs.');
await layers.ready;

const INDEX_URL = '../data/countries/index.json';
const DEMOGRAPHY_URL = '../data/world-country-demography.json';
const RELATION_LABELS = { all:'All context', money:'Money', systems:'Systems', institutions:'Institutions', project:'Project', other:'Other' };
const RUNTIME_GROUPS = ['eu','oecd','g7','g20','schengen','euro-area','usmca','asean','african-union','sadc','pacific-islands-forum','sco','mercosur','gcc','arctic-council','nato','brics','aukus','five-eyes'];
const FIGURE_COUNTRY_CODES = {
  'Canada':'CAN','China':'CHN','Russia':'RUS','India':'IND','United States':'USA','Israel':'ISR',
  'Australia':'AUS','New Zealand':'NZL','Papua New Guinea':'PNG','South Africa':'ZAF'
};

let index = null;
let demography = null;
let renderedCode = null;
let renderVersion = 0;
const records = new Map();

const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
async function fetchJson(url) { const response = await fetch(url, { cache:'no-cache' }); if (!response.ok) throw new Error(`${response.status} ${url}`); return response.json(); }
async function indexData() { if (!index) index = await fetchJson(INDEX_URL); return index; }
async function demographyData() { if (!demography) demography = await fetchJson(DEMOGRAPHY_URL); return demography; }
function runtime() { return window.__potatoAtlasDataRuntime; }
async function populationObservation(code) { return runtime()?.populationObservation?.(code) || null; }
async function areaObservation(code) { return runtime()?.areaObservation?.(code) || null; }

function formatNumber(value, maximumFractionDigits = 1) {
  const number = Number(value);
  if (!Number.isFinite(number)) return '—';
  return new Intl.NumberFormat(undefined, { maximumFractionDigits }).format(number);
}
function formatCompact(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return '—';
  return new Intl.NumberFormat(undefined, { notation:'compact', maximumFractionDigits:1 }).format(number);
}
function formatRuntimeCell(cell) {
  if (!cell || !Number.isFinite(Number(cell.value))) return '—';
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
function observation(record, key) {
  const value = record?.observations?.[key];
  return value && typeof value === 'object' && 'value' in value ? value : null;
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

async function religionShare(code, id) {
  const data = await demographyData();
  const tail = id.split('.').pop();
  const key = tail === 'other' ? 'other_religions' : tail;
  const value = Number(data?.countries?.[code]?.religion?.composition?.[key]);
  return Number.isFinite(value) ? value : null;
}

async function defaultMetrics(code, record) {
  const population = await populationObservation(code);
  const gdp = observation(record, 'gdp');
  const growth = observation(record, 'real_growth') || observation(record, 'real_gdp_growth');
  const inflation = observation(record, 'inflation');
  const unemployment = observation(record, 'unemployment');
  return [
    ['Population', population ? formatCompact(population.value) : '—'],
    ['GDP', gdp ? `${formatNumber(gdp.value, 1)} ${gdp.unit || ''}`.trim() : '—'],
    ['Growth', growth ? `${formatNumber(growth.value, 1)}%` : '—'],
    ['Inflation', inflation ? `${formatNumber(inflation.value, 1)}%` : '—'],
    ['Unemployment', unemployment ? `${formatNumber(unemployment.value, 1)}%` : '—'],
  ];
}

async function membershipLabels(record, code) {
  const dossier = (record?.relationships || [])
    .filter(row => row?.type === 'member-of' && row?.status === 'active')
    .map(row => String(row.target || '').replaceAll('-', ' '))
    .filter(Boolean);
  const empirical = [];
  for (const groupId of RUNTIME_GROUPS) {
    const members = await runtime()?.members?.(groupId) || [];
    if (!members.includes(code)) continue;
    const meta = await runtime()?.groupMeta?.(groupId);
    empirical.push(meta?.label || groupId.replaceAll('-', ' '));
  }
  return [...new Set([...dossier, ...empirical])].slice(0, 10);
}

async function axisContext(code) {
  const profile = await runtime()?.axisProfile?.(code) || { status:'unresolved', orientations:[] };
  const orientations = (profile.orientations || []).filter(item => item?.role !== 'unresolved').slice(0, 3);
  const chains = await runtime()?.chainsForCountry?.(code) || [];
  const figures = await runtime()?.referenceFigures?.() || [];
  const directFigure = figures.find(figure => FIGURE_COUNTRY_CODES[figure.country_or_institution] === code) || null;
  return { profile, orientations, chains, directFigure };
}

function activeComparisonLayer() {
  const active = layers.active().map(id => layers.get(id)).filter(Boolean);
  return active.find(entry => entry.kind === 'scalar' && (entry.family === 'religion' || entry.id === 'stat.population' || entry.id === 'stat.area' || entry.runtime_metric)) || null;
}

async function comparisonValue(code, record, entry) {
  if (entry?.family === 'religion') {
    const value = await religionShare(code, entry.id);
    return { value, display:value == null ? '—' : `${formatNumber(value, 1)}%` };
  }
  if (entry?.id === 'stat.area') {
    const cell = await areaObservation(code);
    const value = Number(cell?.value);
    return { value:Number.isFinite(value) ? value : null, display:Number.isFinite(value) ? `${formatNumber(value)} km²` : '—', cell };
  }
  if (entry?.runtime_metric) {
    const cell = await runtime()?.metric?.(code, entry.runtime_metric);
    const value = Number(cell?.value);
    return { value:Number.isFinite(value) ? value : null, display:formatRuntimeCell(cell), cell };
  }
  const population = await populationObservation(code);
  const value = Number(population?.value);
  return { value:Number.isFinite(value) ? value : null, display:Number.isFinite(value) ? formatCompact(value) : '—', cell:population };
}

async function comparisonRows(codes) {
  const selected = [...new Set((codes || []).map(code => String(code || '').toUpperCase()).filter(code => /^[A-Z]{3}$/.test(code)))];
  if (selected.length < 2) return null;
  const entry = activeComparisonLayer();
  const label = entry?.label || 'Population';
  const metricMeta = entry?.runtime_metric ? await runtime()?.metricMeta?.(entry.runtime_metric) : null;
  const rows = await Promise.all(selected.slice(0, 6).map(async code => {
    const record = await countryRecord(code);
    const metric = await comparisonValue(code, record || {}, entry);
    return { code, name:record?.identity?.name || selection.countryName?.(code) || code, display:metric.display, value:metric.value, active:code === selection.current?.activeCode };
  }));
  rows.sort((a, b) => {
    if (a.active !== b.active) return a.active ? -1 : 1;
    if (a.value == null && b.value != null) return 1;
    if (a.value != null && b.value == null) return -1;
    if (a.value != null && b.value != null && a.value !== b.value) return b.value - a.value;
    return a.name.localeCompare(b.name);
  });
  return { label, metricMeta, rows, remaining:Math.max(0, selected.length - 6) };
}

function connectionRows(code) {
  return (selection.connectionsFor?.(code, 4) || []).map(edge => {
    const partner = edge.a === code ? edge.b : edge.a;
    const types = (edge.types || []).map(type => String(type).replaceAll('-', ' '));
    return { partner, name:selection.countryName?.(partner) || partner, types:types.length ? types.join(' · ') : String(edge.layer || 'relation').replaceAll('-', ' ') };
  });
}

async function contextualRows(code, record) {
  const active = layers.active().map(id => layers.get(id)).filter(Boolean);
  const rows = [];
  const setEntries = active.filter(entry => entry.kind === 'set');
  for (const entry of active) {
    if (entry.family === 'religion') {
      const value = await religionShare(code, entry.id);
      rows.push([entry.label, value == null ? '—' : `${formatNumber(value, 1)}%`]);
    } else if (entry.id === 'stat.population') {
      const pop = await populationObservation(code);
      rows.push([entry.label, pop ? formatCompact(pop.value) : '—']);
    } else if (entry.id === 'stat.area') {
      const area = await areaObservation(code);
      rows.push([entry.label, area?.value != null ? `${formatNumber(area.value)} km²` : '—']);
    } else if (entry.runtime_metric) {
      const cell = await runtime()?.metric?.(code, entry.runtime_metric);
      rows.push([entry.label, formatRuntimeCell(cell)]);
    }
  }
  if (setEntries.length) {
    const matches = await window.__potatoAtlasQuery?.matches?.(code);
    const mode = window.__potatoAtlasQuery?.getMode?.() || 'any';
    rows.unshift([`${mode.toUpperCase()} set query`, matches ? 'matches' : 'outside']);
    rows.splice(1, 0, ['Active sets', setEntries.map(entry => entry.label).join(' · ')]);
  }
  return rows.slice(0, 8);
}

function openInspector() { document.getElementById('atlasApp')?.classList.remove('panel-collapsed'); }
async function showDetails() { selection.inspect?.(); openInspector(); }
async function toggleEntityTrace() {
  openInspector();
  const loaded = window.__potatoEntityTrace ? true : await (window.__potatoAtlasLoadModule ? window.__potatoAtlasLoadModule('Entity Trace', './3d-entity-trace.js') : import('./3d-entity-trace.js').then(() => true).catch(() => false));
  if (!loaded && !window.__potatoEntityTrace) return;
  window.__potatoEntityTrace?.toggle?.();
}
function syncTraceAction() {
  const button = document.querySelector('#atlasCountryCard [data-country-action="entity-trace"]');
  if (!button) return;
  const active = window.__potatoEntityTrace?.isEnabled?.() === true;
  button.classList.toggle('active', active);
  button.textContent = active ? 'Trace connections · on' : 'Trace connections';
}

function install() {
  if (document.getElementById('atlasCountryCard')) return;
  const style = document.createElement('style');
  style.id = 'atlasCountryCardStyle';
  style.textContent = `
    #atlasCountryCard{position:absolute;left:10px;top:10px;z-index:7;width:min(310px,calc(100% - 20px));max-height:calc(100% - 20px);overflow:auto;background:#0a1010ed;border:1px solid #344343;border-radius:13px;padding:11px;box-shadow:0 10px 30px #0009;backdrop-filter:blur(12px)}
    #atlasCountryCard[hidden]{display:none!important}.atlas-country-head{display:flex;align-items:flex-start;gap:9px}.atlas-country-flag{font-size:25px;line-height:1}.atlas-country-title{min-width:0;flex:1}.atlas-country-title b{display:block;font:400 18px/1.05 Georgia,serif}.atlas-country-title small{display:block;color:#9ea9a4;font-size:10px;margin-top:2px}.atlas-country-close{border:0!important;background:transparent!important;color:#9ea9a4!important;padding:1px 4px!important;min-height:0!important}.atlas-country-grid{display:grid;grid-template-columns:1fr 1fr;gap:5px;margin-top:9px}.atlas-country-metric{padding:6px;border:1px solid #273333;border-radius:8px;min-width:0}.atlas-country-metric span{display:block;color:#8f9c96;font-size:9px;text-transform:uppercase;letter-spacing:.05em}.atlas-country-metric b{display:block;font-size:12px;overflow-wrap:anywhere}.atlas-country-row{display:flex;justify-content:space-between;gap:9px;padding:5px 0;border-bottom:1px solid #202b2a;font-size:11px}.atlas-country-row:last-child{border:0}.atlas-country-row span{color:#9aa6a0}.atlas-country-row b{text-align:right;font-weight:600}.atlas-country-section{margin-top:9px}.atlas-country-section>small{display:block;color:#7f8d87;text-transform:uppercase;letter-spacing:.09em;font-size:8px;margin-bottom:2px}.atlas-country-tags{display:flex;flex-wrap:wrap;gap:4px}.atlas-country-tag{border:1px solid #2b3937;border-radius:999px;padding:2px 6px;font-size:9px;color:#bec8c3}.atlas-axis-tag[data-axis="north"]{border-color:#47758a}.atlas-axis-tag[data-axis="west"]{border-color:#315979}.atlas-axis-tag[data-axis="east"]{border-color:#7d493b}.atlas-axis-tag[data-axis="south"]{border-color:#81713a}.atlas-country-compare{width:100%;display:flex;justify-content:space-between;gap:8px;align-items:center;padding:5px 0;border:0;border-bottom:1px solid #202b2a;background:transparent;color:inherit;text-align:left}.atlas-country-compare:last-child{border-bottom:0}.atlas-country-compare:hover,.atlas-country-compare.active{color:#f3dfa4}.atlas-country-compare span{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#b7c2bd;font-size:10px}.atlas-country-compare b{flex:0 0 auto;font-size:10px}.atlas-country-more,.atlas-country-coverage{color:#77847e;font-size:9px;padding-top:3px}.atlas-country-connection{display:grid;grid-template-columns:minmax(74px,.9fr) 1.3fr;gap:8px;padding:5px 0;border-bottom:1px solid #202b2a;font-size:10px}.atlas-country-connection:last-child{border:0}.atlas-country-connection b{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.atlas-country-connection span{color:#909c96;text-align:right;overflow-wrap:anywhere}.atlas-country-actions{display:flex;gap:5px;margin-top:9px;padding-top:8px;border-top:1px solid #273333}.atlas-country-actions button{flex:1;min-height:29px;padding:5px 7px;background:#111918;border:1px solid #2e3a38;color:#bcc8c2;border-radius:7px;font-size:10px}.atlas-country-actions button:hover,.atlas-country-actions button.active{border-color:#708d83;color:#dff1d8;background:#17211f}.atlas-country-source{margin-top:8px;color:#75827c;font-size:8px}@media(max-width:900px){#atlasCountryCard{top:auto;bottom:8px;left:8px;right:8px;width:auto;max-height:38vh}}
  `;
  document.head.appendChild(style);
  const card = document.createElement('section');
  card.id = 'atlasCountryCard'; card.hidden = true; card.setAttribute('aria-live', 'polite');
  document.querySelector('.mapwrap')?.appendChild(card);
  card.addEventListener('click', event => {
    const compare = event.target.closest('[data-compare-code]')?.dataset.compareCode;
    if (compare) { selection.activate?.(compare, { add:false }); return; }
    const action = event.target.closest('[data-country-action]')?.dataset.countryAction;
    if (action === 'details') showDetails();
    if (action === 'entity-trace') toggleEntityTrace();
  });
}

async function render(code = selection.current?.activeCode || selection.current?.code) {
  code = String(code || '').toUpperCase();
  const card = document.getElementById('atlasCountryCard');
  if (!card) return;
  const version = ++renderVersion;
  if (!/^[A-Z]{3}$/.test(code)) { renderedCode = null; card.hidden = true; card.innerHTML = ''; return; }
  renderedCode = code;
  const record = await countryRecord(code);
  if (renderVersion !== version || renderedCode !== code) return;
  const identity = record?.identity || {};
  const political = record?.political_system || {};
  const metrics = await defaultMetrics(code, record || {});
  const [context, comparison, memberships, axis] = await Promise.all([
    contextualRows(code, record || {}),
    comparisonRows(selection.current?.selectedCodes || []),
    membershipLabels(record || {}, code),
    axisContext(code),
  ]);
  if (renderVersion !== version || renderedCode !== code) return;
  const connections = connectionRows(code);
  const relationMode = selection.getRelationMode?.() || 'all';
  const leader = political?.current_leader?.name || '—';
  const leaderOffice = political?.current_leader?.office || political?.head_of_government || '';
  const head = political?.head_of_state || '';
  const refreshed = record?.coverage?.last_enriched || record?.updated || record?.provenance?.retrieved || record?.provenance?.last_refresh || '';
  const coverage = comparison?.metricMeta?.coverage != null ? `${comparison.metricMeta.coverage}/${comparison.metricMeta.country_count} countries` : '';
  const visibleChains = axis.chains.slice(0, 2);
  const remainingChains = Math.max(0, axis.chains.length - visibleChains.length);

  card.innerHTML = `
    <div class="atlas-country-head"><div class="atlas-country-flag" aria-hidden="true">${flagEmoji(identity.iso2 || record?.iso2)}</div><div class="atlas-country-title"><b>${esc(identity.name || record?.country_id || selection.countryName?.(code) || code)}</b><small>${esc(identity.capital || record?.capital || 'Capital unavailable')}${identity.official_name && identity.official_name !== identity.name ? ` · ${esc(identity.official_name)}` : ''}</small></div><button class="atlas-country-close" type="button" aria-label="Close country card">×</button></div>
    ${axis.orientations.length ? `<div class="atlas-country-section"><small>Axis orientation · project interpretation</small><div class="atlas-country-tags">${axis.orientations.map(item => `<span class="atlas-country-tag atlas-axis-tag" data-axis="${esc(item.axis)}" title="${esc(item.note || '')}">${esc(item.axis.charAt(0).toUpperCase()+item.axis.slice(1))} · ${esc(item.role)}</span>`).join('')}</div></div>` : ''}
    <div class="atlas-country-grid">${metrics.map(([label, value]) => `<div class="atlas-country-metric"><span>${esc(label)}</span><b>${esc(value)}</b></div>`).join('')}</div>
    ${comparison ? `<div class="atlas-country-section"><small>Selected comparison · ${esc(comparison.label)}</small>${comparison.rows.map(row => `<button type="button" class="atlas-country-compare${row.active ? ' active' : ''}" data-compare-code="${esc(row.code)}"><span>${esc(row.name)}</span><b>${esc(row.display)}</b></button>`).join('')}${coverage ? `<div class="atlas-country-coverage">Coverage · ${esc(coverage)}</div>` : ''}${comparison.remaining ? `<div class="atlas-country-more">+${comparison.remaining} more selected</div>` : ''}</div>` : ''}
    <div class="atlas-country-section"><small>Government</small><div class="atlas-country-row"><span>${esc(leaderOffice || 'Leader')}</span><b>${esc(leader)}</b></div>${head && head !== leader ? `<div class="atlas-country-row"><span>Head of state</span><b>${esc(head)}</b></div>` : ''}${political.system_type ? `<div class="atlas-country-row"><span>System</span><b>${esc(political.system_type)}</b></div>` : ''}</div>
    ${axis.directFigure ? `<div class="atlas-country-section"><small>Axis reference · project interpretation</small><div class="atlas-country-row"><span>${esc(axis.directFigure.real_office)}</span><b>${esc(axis.directFigure.person)}</b></div><div class="atlas-country-source">${esc(axis.directFigure.axis_role)} · as of ${esc(axis.directFigure.as_of)}</div></div>` : ''}
    ${visibleChains.length ? `<div class="atlas-country-section"><small>Functional chains</small><div class="atlas-country-tags">${visibleChains.map(chain => `<span class="atlas-country-tag" title="${esc(chain.description || '')}">${esc(chain.label)}</span>`).join('')}${remainingChains ? `<span class="atlas-country-tag">+${remainingChains}</span>` : ''}</div></div>` : ''}
    ${context.length ? `<div class="atlas-country-section"><small>Current map question</small>${context.map(([label, value]) => `<div class="atlas-country-row"><span>${esc(label)}</span><b>${esc(value)}</b></div>`).join('')}</div>` : ''}
    ${connections.length ? `<div class="atlas-country-section"><small>Connections${relationMode !== 'all' ? ` · ${esc(RELATION_LABELS[relationMode] || relationMode)}` : ''}</small>${connections.map(row => `<div class="atlas-country-connection"><b>${esc(row.name)}</b><span>${esc(row.types)}</span></div>`).join('')}</div>` : ''}
    ${memberships.length ? `<div class="atlas-country-section"><small>Memberships</small><div class="atlas-country-tags">${memberships.map(label => `<span class="atlas-country-tag">${esc(label)}</span>`).join('')}</div></div>` : ''}
    <div class="atlas-country-actions"><button type="button" data-country-action="details">More country data</button><button type="button" data-country-action="entity-trace">Trace connections</button></div>
    <div class="atlas-country-source">${refreshed ? `Country record · ${esc(refreshed)}` : 'Country record'} · missing values remain unavailable</div>`;
  card.hidden = false;
  card.querySelector('.atlas-country-close')?.addEventListener('click', () => { card.hidden = true; });
  syncTraceAction();
}

install();
window.addEventListener('potato-atlas-working-selection-change', event => render(event?.detail?.activeCode || event?.detail?.code));
window.addEventListener('potato-atlas-layer-change', () => { if (renderedCode) render(renderedCode); });
window.addEventListener('potato-atlas-query-change', () => { if (renderedCode) render(renderedCode); });
window.addEventListener('potato-atlas-relation-mode-change', () => { if (renderedCode) render(renderedCode); });
window.addEventListener('potato-atlas-entity-trace-change', syncTraceAction);
if (selection.current?.selected) render(selection.current.activeCode || selection.current.code);

window.__potatoAtlasCountryCard = { render, comparisonRows, connectionRows, axisContext, close() { const card = document.getElementById('atlasCountryCard'); if (card) card.hidden = true; } };
