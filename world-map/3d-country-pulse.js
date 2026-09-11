// Country Pulse enhancement for the World Relational Atlas.
//
// Country Pulse turns the active country's canonical record into a compact,
// sourced first-screen summary. It is deliberately non-fatal: sparse records and
// optional demography data produce honest unavailable states rather than guesses.

const panel = document.getElementById('panel');
const INDEX_URL = '../data/countries/index.json';
const DEMOGRAPHY_URL = '../data/world-country-demography.json';

const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
}[char]));
const title = value => String(value || '').replaceAll('_', ' ').replace(/\b\w/g, c => c.toUpperCase());

const INDICATOR_UNITS = {
  'SP.POP.TOTL': 'people',
  'NY.GDP.MKTP.CD': 'current USD',
  'NY.GDP.PCAP.CD': 'current USD / person',
  'NY.GDP.PCAP.PP.CD': 'current international $ / person',
  'NY.GDP.MKTP.KD.ZG': 'percent',
  'FP.CPI.TOTL.ZG': 'percent',
  'SL.UEM.TOTL.ZS': 'percent of labour force',
  'SL.TLF.CACT.ZS': 'percent age 15+',
  'SP.DYN.LE00.IN': 'years',
  'SP.DYN.TFRT.IN': 'births / woman',
  'SP.URB.TOTL.IN.ZS': 'percent of population',
  'SI.POV.NAHC': 'percent',
  'EN.ATM.CO2E.PC': 't CO₂ / person',
  'IT.NET.USER.ZS': 'percent of population',
};

const metricDefinitions = [
  ['population', 'Population'],
  ['gdp', 'GDP'],
  ['gdp_per_capita', 'GDP per capita'],
  ['real_growth', 'Growth'],
  ['inflation', 'Inflation'],
  ['unemployment', 'Unemployment'],
  ['debt_to_gdp', 'Debt / GDP'],
];

let indexPromise;
let demographyPromise;
const recordCache = new Map();
let rendering = false;

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${response.status} ${url}`);
  return response.json();
}

async function indexBy3() {
  if (!indexPromise) indexPromise = fetchJson(INDEX_URL).then(data => Object.fromEntries((data.countries || []).map(row => [row.iso3, row])));
  return indexPromise;
}

async function demography() {
  if (!demographyPromise) demographyPromise = fetchJson(DEMOGRAPHY_URL).catch(() => ({ countries: {} }));
  return demographyPromise;
}

async function getRecord(code) {
  code = String(code || '').toUpperCase();
  if (!code) return null;
  if (recordCache.has(code)) return recordCache.get(code);
  const index = await indexBy3();
  const row = index[code];
  if (!row?.id) return null;
  const record = await fetchJson(`../data/countries/${row.id}.json`).catch(() => null);
  recordCache.set(code, record);
  return record;
}

function periodOf(value, fallback) {
  return value?.year ?? value?.reference_period ?? value?.period ?? fallback ?? null;
}
function sourceOf(value, fallback) {
  return value?.source || fallback || null;
}
function normalizeObservation(value, fallback = {}) {
  if (!value || typeof value !== 'object' || !Number.isFinite(Number(value.value))) return null;
  const indicator = value.indicator || fallback.indicator || null;
  return {
    value: Number(value.value),
    unit: value.unit || fallback.unit || INDICATOR_UNITS[indicator] || '',
    period: periodOf(value, fallback.period),
    source: sourceOf(value, fallback.source),
    sourceUrl: value.source_url || fallback.sourceUrl || null,
    indicator,
  };
}
function scalarMetric(value, unit, period, source, sourceUrl) {
  const number = Number(value);
  if (!Number.isFinite(number)) return null;
  return { value: number, unit, period, source, sourceUrl };
}

function metric(record, id, demoRow = null) {
  const observations = record?.observations || {};
  const aliases = {
    population: ['population'],
    gdp: ['gdp'],
    gdp_per_capita: ['gdp_per_capita'],
    real_growth: ['real_growth', 'real_gdp_growth'],
    inflation: ['inflation'],
    unemployment: ['unemployment'],
    debt_to_gdp: ['debt_to_gdp', 'government_debt_to_gdp'],
    life_expectancy: ['life_expectancy'],
    fertility: ['fertility'],
    urbanization: ['urbanization'],
    labour_force_participation: ['labour_force_participation'],
    internet_penetration: ['internet_penetration'],
    co2_emissions: ['co2_emissions'],
  };
  for (const key of aliases[id] || [id]) {
    const found = normalizeObservation(observations[key]);
    if (found) return found;
  }

  const economy = record?.economy || {};
  const population = record?.population || {};
  if (id === 'population') {
    const demo = normalizeObservation(demoRow?.population);
    if (demo) return demo;
    return scalarMetric(population.value, 'people', population.year, population.source, population.source_url);
  }
  if (id === 'gdp') {
    if (Number.isFinite(Number(economy.gdp_current_usd_trillion))) return scalarMetric(Number(economy.gdp_current_usd_trillion) * 1e12, 'current USD', economy.gdp_year, economy.source, economy.source_url);
    if (Number.isFinite(Number(economy.gdp_current_dkk_billion))) return scalarMetric(Number(economy.gdp_current_dkk_billion), 'DKK billion', economy.gdp_year, economy.source, economy.source_url);
  }
  if (id === 'gdp_per_capita') return scalarMetric(economy.gdp_per_capita_usd, 'current USD / person', economy.gdp_year, economy.source, economy.source_url);
  if (id === 'real_growth') return scalarMetric(economy.gdp_growth_percent ?? economy.real_growth_percent_2025, 'percent', economy.gdp_year || 2025, economy.source, economy.source_url);
  if (id === 'inflation') return scalarMetric(economy.inflation_percent, 'percent', economy.gdp_year || record?.updated, economy.source, economy.source_url);
  if (id === 'unemployment') return scalarMetric(economy.unemployment_percent, 'percent', economy.gdp_year || record?.updated, economy.source, economy.source_url);
  if (id === 'debt_to_gdp') return scalarMetric(record?.public_finance?.debt_to_gdp_percent, 'percent of GDP', record?.public_finance?.year, record?.public_finance?.source, record?.public_finance?.source_url);
  if (id === 'life_expectancy') return scalarMetric(population.life_expectancy, 'years', population.year, population.source, population.source_url);
  if (id === 'fertility') return scalarMetric(population.fertility_rate, 'births / woman', population.year, population.source, population.source_url);
  return null;
}

function compactNumber(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return '—';
  return new Intl.NumberFormat('en', {
    notation: Math.abs(n) >= 1e6 ? 'compact' : 'standard',
    maximumFractionDigits: Math.abs(n) >= 100 ? 1 : 2,
  }).format(n);
}
function displayValue(item) {
  if (!item) return '—';
  if (item.unit === 'current USD') return `$${compactNumber(item.value)}`;
  if (item.unit === 'current USD / person') return `$${new Intl.NumberFormat('en', { maximumFractionDigits: 0 }).format(item.value)}`;
  if (item.unit === 'percent' || String(item.unit).startsWith('percent')) return `${compactNumber(item.value)}%`;
  if (item.unit === 'people') return compactNumber(item.value);
  if (item.unit === 'years') return `${compactNumber(item.value)} yr`;
  return compactNumber(item.value);
}
function metricMeta(item) {
  if (!item) return 'Unavailable in the current sourced record';
  return [item.period, item.unit, item.source].filter(Boolean).join(' · ') || 'Sourced observation';
}

function listValues(value, max = 6) {
  if (!value) return [];
  if (Array.isArray(value)) return value.filter(item => typeof item === 'string' && item.trim()).slice(0, max);
  if (typeof value === 'string') return [value];
  return [];
}
function mergeLists(...values) {
  return [...new Set(values.flatMap(value => listValues(value, 8)))].slice(0, 8);
}
function chips(values) {
  return values.length ? `<div class="pulse-chips">${values.map(value => `<span>${esc(value)}</span>`).join('')}</div>` : '<div class="muted">No structured items in this record yet.</div>';
}

function religionSummary(row) {
  const composition = row?.religion?.composition || {};
  const items = Object.entries(composition)
    .filter(([, value]) => Number.isFinite(Number(value)))
    .sort((a, b) => Number(b[1]) - Number(a[1]))
    .slice(0, 3);
  if (!items.length) return '';
  const labels = {
    christian:'Christian', muslim:'Muslim', hindu:'Hindu', buddhist:'Buddhist',
    jewish:'Jewish', other_religions:'Other religions', unaffiliated:'Unaffiliated'
  };
  return `<div class="pulse-religion"><b>Religion / identity · ${esc(row.religion.year || 2020)}</b>${items.map(([key, value]) => `<div class="pulse-religion-row"><span>${esc(labels[key] || title(key))}</span><strong>${Number(value).toFixed(Number(value) >= 10 ? 0 : 1)}%</strong></div>`).join('')}<div class="muted pulse-note">Descriptive composition only; it does not imply political loyalty, conduct or belief intensity.</div></div>`;
}

function connectionRows(code) {
  const connections = window.__potatoAtlasSelection?.connectionsFor?.(code, 6) || [];
  if (!connections.length) return '<div class="muted">No curated immediate relationships are represented for this country yet.</div>';
  return connections.map(edge => {
    const other = edge.a === code ? edge.b : edge.a;
    const name = window.__potatoAtlasSelection?.countryName?.(other) || other;
    const types = (edge.types || []).slice(0, 3).join(' · ') || edge.layer || 'relationship';
    return `<button class="pulse-connection" data-pulse-country="${esc(other)}"><span>${esc(name)}</span><small>${esc(types)}</small></button>`;
  }).join('');
}

function moreStatistics(record, demoRow) {
  const preferred = [
    ['life_expectancy','Life expectancy'], ['fertility','Fertility'], ['urbanization','Urbanization'],
    ['labour_force_participation','Labour participation'], ['internet_penetration','Internet penetration'],
    ['co2_emissions','CO₂ / person']
  ];
  const rows = preferred.map(([id, label]) => [label, metric(record, id, demoRow)]).filter(([, value]) => value);
  const seen = new Set(rows.map(([label]) => label.toLowerCase()));
  for (const [key, raw] of Object.entries(record?.observations || {})) {
    if (rows.length >= 12) break;
    const value = normalizeObservation(raw);
    const label = title(key);
    if (!value || seen.has(label.toLowerCase())) continue;
    rows.push([label, value]);
    seen.add(label.toLowerCase());
  }
  return rows.length ? rows.map(([label, value]) => `<div class="pulse-stat-row"><span>${esc(label)}</span><b>${esc(displayValue(value))}</b><small>${esc(metricMeta(value))}</small></div>`).join('') : '<div class="muted">No additional normalized observations yet.</div>';
}

function pulseHtml(code, record, demoRow) {
  const name = record?.identity?.name || record?.name || code;
  const headline = metricDefinitions.map(([id, label]) => [label, metric(record, id, demoRow)]);
  const systems = mergeLists(
    record?.energy_and_resources?.strategic_assets,
    record?.energy_and_resources?.observed_system_features,
    record?.trade_and_value_chains?.strategic_value_chains,
    record?.infrastructure?.strategic_assets
  );
  const projects = mergeLists(
    record?.projects,
    record?.programmes,
    record?.research_queue,
    record?.energy_and_resources?.projects
  ).slice(0, 6);
  const institutions = mergeLists(
    record?.political_system?.legislature,
    record?.security_and_external_relations?.major_organizations,
    record?.security_and_external_relations?.alliances
  );
  const coverage = record?.coverage || {};
  const freshness = record?.updated || record?.provenance?.last_refresh || record?.data_freshness?.last_refresh_attempt || 'unknown';

  return `<section class="card atlas-country-pulse" data-pulse-code="${esc(code)}">
    <div class="pulse-heading"><div><span class="eyebrow">Country Pulse</span><b>${esc(name)}</b></div><span class="pill">${esc(code)}</span></div>
    <div class="pulse-metrics">${headline.map(([label, value]) => `<div class="pulse-metric"><span>${esc(label)}</span><strong>${esc(displayValue(value))}</strong><small>${esc(metricMeta(value))}</small></div>`).join('')}</div>
    ${religionSummary(demoRow)}
    <details class="pulse-section" open><summary>Connections</summary><div class="pulse-connections">${connectionRows(code)}</div></details>
    <details class="pulse-section"><summary>Systems & capabilities</summary>${chips(systems)}</details>
    <details class="pulse-section"><summary>Projects / research queue</summary>${chips(projects)}</details>
    <details class="pulse-section"><summary>Institutions & memberships</summary>${chips(institutions)}</details>
    <details class="pulse-section"><summary>More statistics</summary><div class="pulse-stat-list">${moreStatistics(record, demoRow)}</div></details>
    <div class="pulse-quality"><span>Coverage: ${esc(coverage.observations ?? '—')} observations · ${esc(coverage.relationships ?? record?.relationships?.length ?? '—')} relationships</span><span>Updated: ${esc(String(freshness).slice(0, 19))}</span></div>
  </section>`;
}

function isCountryOverview() {
  if (!panel) return false;
  const eyebrow = panel.querySelector('.eyebrow')?.textContent || '';
  return /Canonical country|Territory \/ map polygon/i.test(eyebrow);
}

async function render() {
  if (!panel || rendering || !isCountryOverview()) return;
  const current = window.__potatoAtlasSelection?.current || {};
  const code = String(current.activeCode || current.code || '').toUpperCase();
  if (!code) return;
  const existing = panel.querySelector('.atlas-country-pulse');
  if (existing?.dataset.pulseCode === code) return;
  rendering = true;
  try {
    const [record, demo] = await Promise.all([getRecord(code), demography()]);
    if (!record || !isCountryOverview()) return;
    panel.querySelector('.atlas-country-pulse')?.remove();
    const holder = document.createElement('div');
    holder.innerHTML = pulseHtml(code, record, demo?.countries?.[code]);
    const pulse = holder.firstElementChild;
    const firstGrid = panel.querySelector('.grid');
    if (pulse && firstGrid?.parentNode) firstGrid.parentNode.insertBefore(pulse, firstGrid);
    else if (pulse) panel.appendChild(pulse);
  } finally {
    rendering = false;
  }
}

function ensureStyle() {
  if (document.getElementById('atlasCountryPulseStyle')) return;
  const style = document.createElement('style');
  style.id = 'atlasCountryPulseStyle';
  style.textContent = `
    .atlas-country-pulse{border-color:#526258;background:#111a18}.pulse-heading{display:flex;align-items:flex-start;justify-content:space-between;gap:8px}.pulse-heading b{display:block;font:400 19px Georgia,serif;margin-top:2px}.pulse-metrics{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px;margin-top:9px}.pulse-metric{padding:7px;border:1px solid var(--line);border-radius:8px;background:#0d1514}.pulse-metric span{display:block;color:var(--muted);font-size:9px;text-transform:uppercase;letter-spacing:.06em}.pulse-metric strong{display:block;font-size:14px;margin-top:2px}.pulse-metric small,.pulse-stat-row small{display:block;color:var(--muted);font-size:9px;line-height:1.25;margin-top:2px}.pulse-religion{margin-top:9px;padding-top:8px;border-top:1px solid var(--line)}.pulse-religion-row{display:flex;justify-content:space-between;gap:8px;padding:3px 0}.pulse-note{font-size:9px;margin-top:4px}.pulse-section{border-top:1px solid var(--line);margin-top:8px;padding-top:6px}.pulse-section>summary{cursor:pointer;color:#dfe6dc;font-size:12px;font-weight:650}.pulse-connections{margin-top:5px}.pulse-connection{display:flex;width:100%;justify-content:space-between;gap:8px;align-items:center;text-align:left;margin:4px 0;padding:6px 7px}.pulse-connection small{color:var(--muted);text-align:right}.pulse-chips{display:flex;flex-wrap:wrap;gap:4px;margin-top:6px}.pulse-chips span{border:1px solid var(--line);border-radius:999px;padding:3px 6px;font-size:10px}.pulse-stat-list{margin-top:6px}.pulse-stat-row{padding:5px 0;border-bottom:1px solid var(--line)}.pulse-stat-row:last-child{border:0}.pulse-stat-row span{color:var(--muted);font-size:10px}.pulse-stat-row b{display:block}.pulse-quality{display:flex;justify-content:space-between;gap:7px;flex-wrap:wrap;margin-top:8px;padding-top:7px;border-top:1px solid var(--line);color:var(--muted);font-size:9px}
    @media(max-width:900px){.pulse-metrics{grid-template-columns:1fr 1fr}}
  `;
  document.head.appendChild(style);
}

ensureStyle();
panel?.addEventListener('click', event => {
  const button = event.target.closest('[data-pulse-country]');
  if (button?.dataset.pulseCountry) window.goCountry?.(button.dataset.pulseCountry);
});

if (panel) {
  let scheduled = false;
  const observer = new MutationObserver(() => {
    if (scheduled || rendering) return;
    scheduled = true;
    queueMicrotask(() => { scheduled = false; render(); });
  });
  observer.observe(panel, { childList: true, subtree: true });
}
window.addEventListener('potato-atlas-working-selection-change', render);
window.addEventListener('potato-atlas-selection-change', render);
window.addEventListener('potato-atlas-module-ready', event => {
  if (event?.detail?.label === 'Demography') render();
});

window.__potatoAtlasCountryPulse = {
  render,
  getRecord,
  metric,
  get currentCode() {
    const current = window.__potatoAtlasSelection?.current || {};
    return current.activeCode || current.code || null;
  }
};

render();
