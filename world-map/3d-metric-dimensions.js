// Optional 3D metric extension for the World Relational Atlas.
//
// Reuses the existing Height selector for distinct descriptive views: curated
// relation coverage, sourced D4 observables, and D3/D6 data-readiness surfaces.
// Raw magnitude and data coverage are never treated as spiritual Axis height.

const map = window.__potatoAtlasMap;
const heightSelect = document.getElementById('height');
const relationTypeSelect = document.getElementById('relationType');
const viewMenu = document.getElementById('viewMenu');

if (!map || !heightSelect) throw new Error('3D metric dimensions require the core atlas map and Height selector.');

const WORLD_GRAPH_URL = '../data/world-relational-map.json';
const OBSERVABLES_URL = '../data/world-country-observables.json';
const WORLD_BANK_URL = 'https://api.worldbank.org/v2/country/all/indicator';
const RELATIONSHIP_HEIGHT_SCALE_METERS = 180000;
const COVERAGE_HEIGHT_SCALE_METERS = 90000;
const D4_MIN_HEIGHT = 45000;
const D4_MAX_HEIGHT = 1050000;

const ALL_D4_METRICS = {
  population:'SP.POP.TOTL',
  gdp:'NY.GDP.MKTP.CD',
  gdp_per_capita:'NY.GDP.PCAP.CD',
  real_growth:'NY.GDP.MKTP.KD.ZG',
  unemployment:'SL.UEM.TOTL.ZS',
  life_expectancy:'SP.DYN.LE00.IN',
  urbanization:'SP.URB.TOTL.IN.ZS',
  internet_penetration:'IT.NET.USER.ZS',
  trade_openness:'NE.TRD.GNFS.ZS',
  net_migration:'SM.POP.NETM',
  energy_dependence:'EG.IMP.CONS.ZS',
  fdi_inflow:'BX.KLT.DINV.WD.GD.ZS',
};
const INDICATOR_TO_METRIC = Object.fromEntries(Object.entries(ALL_D4_METRICS).map(([id,indicator]) => [indicator,id]));

const D4_SURFACES = {
  gdp: {label:'D4 · GDP', indicator:ALL_D4_METRICS.gdp, unit:'current USD', scale:'log', role:'economic production scale'},
  gdp_per_capita: {label:'D4 · GDP / person', indicator:ALL_D4_METRICS.gdp_per_capita, unit:'current USD/person', scale:'log', role:'production per person'},
  trade_openness: {label:'D4 · Trade / GDP', indicator:ALL_D4_METRICS.trade_openness, unit:'percent of GDP', scale:'linear', domain:[0,250], role:'cross-border trade intensity'},
  life_expectancy: {label:'D4 · Life expectancy', indicator:ALL_D4_METRICS.life_expectancy, unit:'years', scale:'linear', domain:[45,90], role:'broad human outcome'},
  urbanization: {label:'D4 · Urban population', indicator:ALL_D4_METRICS.urbanization, unit:'percent of population', scale:'linear', domain:[0,100], role:'settlement structure'},
  internet_penetration: {label:'D4 · Internet use', indicator:ALL_D4_METRICS.internet_penetration, unit:'percent of population', scale:'linear', domain:[0,100], role:'digital connectivity'},
};

let worldGraph = null;
let observables = null;
let relationshipOption = null;
let note = null;
const d4Options = new Map();
const axisCoverageOptions = new Map();

function currentTimeState() {
  return window.__potatoAtlasTime?.getState?.() || { mode: 'current' };
}

function activeRelationType() {
  const value = relationTypeSelect?.value || 'all';
  return value || 'all';
}

function edgeMatches(edge, relationType) {
  if (relationType === 'all') return true;
  return Array.isArray(edge?.types) && edge.types.includes(relationType);
}

function relationshipCounts(relationType = activeRelationType()) {
  const counts = new Map();
  for (const edge of worldGraph?.curated_edges || []) {
    if (!edgeMatches(edge, relationType)) continue;
    for (const code of [edge?.a, edge?.b]) {
      if (!/^[A-Z]{3}$/.test(String(code || ''))) continue;
      counts.set(code, (counts.get(code) || 0) + 1);
    }
  }
  return counts;
}

function matchExpression(values, fallback = 0) {
  const match = ['match', ['get', 'iso3']];
  for (const [code, value] of [...values.entries()].sort(([a], [b]) => a.localeCompare(b))) match.push(code, value);
  match.push(fallback);
  return match;
}

function setRelationshipHeight() {
  if (!worldGraph || !map.getLayer('countries-extrude')) return;
  const expression = matchExpression(relationshipCounts());
  map.setPaintProperty('countries-extrude', 'fill-extrusion-height', ['*', RELATIONSHIP_HEIGHT_SCALE_METERS, ['sqrt', ['max', expression, 0]]]);
}

function ensureOptions() {
  relationshipOption = [...heightSelect.options].find(option => option.value === 'relationships') || null;
  if (!relationshipOption) {
    relationshipOption = document.createElement('option');
    relationshipOption.value = 'relationships';
    relationshipOption.textContent = 'Height · represented relationships';
    heightSelect.appendChild(relationshipOption);
  }

  const axisCoverage = [
    ['d3-coverage','Height · D3 · evidence coverage'],
    ['d6-change','Height · D6 · change coverage'],
  ];
  for (const [mode,label] of axisCoverage) {
    let option = [...heightSelect.options].find(item => item.value === `axis:${mode}`) || null;
    if (!option) {
      option = document.createElement('option');
      option.value = `axis:${mode}`;
      option.textContent = label;
      heightSelect.appendChild(option);
    }
    axisCoverageOptions.set(mode, option);
  }

  for (const [metricId, spec] of Object.entries(D4_SURFACES)) {
    const value = `d4:${metricId}`;
    let option = [...heightSelect.options].find(item => item.value === value) || null;
    if (!option) {
      option = document.createElement('option');
      option.value = value;
      option.textContent = `Height · ${spec.label}`;
      heightSelect.appendChild(option);
    }
    d4Options.set(metricId, option);
  }
}

function ensureNote() {
  if (note) return note;
  note = document.createElement('div');
  note.id = 'metricHeightNote';
  note.className = 'boundary';
  note.hidden = true;
  note.style.marginTop = '7px';
  note.style.fontSize = '10px';
  heightSelect.insertAdjacentElement('afterend', note);
  return note;
}

function numeric(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function surfaceRows(metricId) {
  const rows = [];
  for (const [code,row] of Object.entries(observables?.countries || {})) {
    const item = row?.metrics?.[metricId];
    const value = numeric(item?.value);
    if (value == null) continue;
    rows.push({code, value, year:item?.year});
  }
  return rows;
}

function coverageCounts(kind) {
  const counts = new Map();
  for (const [code,row] of Object.entries(observables?.countries || {})) {
    const metrics = row?.metrics || {};
    let count = 0;
    for (const metricId of Object.keys(ALL_D4_METRICS)) {
      const item = metrics[metricId];
      if (kind === 'd3-coverage' && numeric(item?.value) != null) count += 1;
      if (kind === 'd6-change' && numeric(item?.value) != null && numeric(item?.previous?.value) != null) count += 1;
    }
    if (count > 0) counts.set(code, count);
  }
  return counts;
}

function setCoverageHeight(kind) {
  if (!observables || !map.getLayer('countries-extrude')) return;
  const counts = coverageCounts(kind);
  map.setPaintProperty('countries-extrude', 'fill-extrusion-height', ['*', COVERAGE_HEIGHT_SCALE_METERS, matchExpression(counts, 0)]);
}

function quantile(values, q) {
  if (!values.length) return 0;
  const sorted = [...values].sort((a,b) => a-b);
  const index = Math.max(0, Math.min(sorted.length - 1, Math.round((sorted.length - 1) * q)));
  return sorted[index];
}

function transform(value, spec) {
  if (spec.scale === 'log') return Math.log10(Math.max(value, 1));
  if (spec.scale === 'sqrt') return Math.sqrt(Math.max(value, 0));
  return value;
}

function surfaceHeights(metricId) {
  const spec = D4_SURFACES[metricId];
  const rows = surfaceRows(metricId);
  const transformed = rows.map(row => transform(row.value, spec));
  let low;
  let high;
  if (Array.isArray(spec.domain)) {
    low = transform(spec.domain[0], spec);
    high = transform(spec.domain[1], spec);
  } else {
    low = quantile(transformed, .05);
    high = quantile(transformed, .95);
  }
  if (!Number.isFinite(low) || !Number.isFinite(high) || high <= low) {
    low = Math.min(...transformed, 0);
    high = Math.max(...transformed, 1);
  }
  const heights = new Map();
  for (const row of rows) {
    const x = transform(row.value, spec);
    const normalized = Math.max(0, Math.min(1, (x - low) / Math.max(high - low, Number.EPSILON)));
    heights.set(row.code, Math.round(D4_MIN_HEIGHT + Math.pow(normalized, .82) * (D4_MAX_HEIGHT - D4_MIN_HEIGHT)));
  }
  return {heights, rows};
}

function setD4Height(metricId) {
  if (!observables || !D4_SURFACES[metricId] || !map.getLayer('countries-extrude')) return;
  map.setPaintProperty('countries-extrude', 'fill-extrusion-height', matchExpression(surfaceHeights(metricId).heights, 0));
}

function yearSummary(rows) {
  const years = rows.map(row => Number(row.year)).filter(Number.isFinite).sort((a,b) => a-b);
  if (!years.length) return 'mixed/unknown years';
  return years[0] === years.at(-1) ? String(years[0]) : `${years[0]}–${years.at(-1)}`;
}

function activeD4Metric() {
  return heightSelect.value.startsWith('d4:') ? heightSelect.value.slice(3) : null;
}

function activeAxisCoverage() {
  return heightSelect.value.startsWith('axis:') ? heightSelect.value.slice(5) : null;
}

function updateNote() {
  const node = ensureNote();
  const value = heightSelect.value;
  const activeRelationship = value === 'relationships';
  const metricId = activeD4Metric();
  const axisMode = activeAxisCoverage();
  node.hidden = !activeRelationship && !metricId && !axisMode;
  if (node.hidden) return;

  if (activeRelationship) {
    const type = activeRelationType();
    const counts = relationshipCounts(type);
    const representedCountries = [...counts.values()].filter(count => count > 0).length;
    const representedEdges = (worldGraph?.curated_edges || []).filter(edge => edgeMatches(edge, type)).length;
    const filterText = type === 'all' ? 'all represented types' : `type: ${type}`;
    node.textContent = `Represented graph links · ${representedEdges} curated edges across ${representedCountries} countries · ${filterText}. Height uses √(edge count) scaling. This is repository graph coverage/connectivity, not a country rank.`;
    return;
  }

  if (axisMode) {
    const counts = coverageCounts(axisMode);
    const values = [...counts.values()];
    const full = values.filter(count => count === Object.keys(ALL_D4_METRICS).length).length;
    const maximum = values.length ? Math.max(...values) : 0;
    if (axisMode === 'd3-coverage') {
      node.textContent = `D3 evidence-coverage surface · height = number of populated D4 source series (0–12). ${counts.size} countries have at least one series; ${full} currently have all 12. This maps Atlas evidence density/provenance readiness, not historical depth, truth, quality of a country, or spiritual position.`;
    } else {
      node.textContent = `D6 change-coverage surface · height = number of D4 metrics with both a current and prior comparable observation (0–12; current maximum ${maximum}). It shows where change can already be derived. It is dataset readiness for recurrence analysis, not a score of national dynamism or Axis ascent.`;
    }
    return;
  }

  const spec = D4_SURFACES[metricId];
  const rows = surfaceRows(metricId);
  node.textContent = `${spec.label} · ${rows.length} countries · observation years ${yearSummary(rows)} · ${spec.unit}. Extrusion is a normalized display of ${spec.role}; it does not change the underlying value and does not represent Axis height, moral worth, political rank or project membership. Source: World Bank WDI.`;
}

function applyMode() {
  const historical = currentTimeState().mode !== 'current';
  if (relationshipOption) relationshipOption.disabled = historical;
  for (const option of d4Options.values()) option.disabled = historical || !observables;
  for (const option of axisCoverageOptions.values()) option.disabled = historical || !observables;

  if (historical && (heightSelect.value === 'relationships' || activeD4Metric() || activeAxisCoverage())) {
    heightSelect.value = 'flat';
    heightSelect.dispatchEvent(new Event('change', { bubbles: true }));
    return;
  }

  if (heightSelect.value === 'relationships') setRelationshipHeight();
  const metricId = activeD4Metric();
  if (metricId) setD4Height(metricId);
  const axisMode = activeAxisCoverage();
  if (axisMode) setCoverageHeight(axisMode);
  updateNote();
}

async function loadWorldGraph() {
  const response = await fetch(WORLD_GRAPH_URL);
  if (!response.ok) throw new Error(`${WORLD_GRAPH_URL} returned HTTP ${response.status}`);
  const payload = await response.json();
  if (!Array.isArray(payload?.curated_edges)) throw new Error('World relational graph has no curated_edges array.');
  return payload;
}

async function loadD4Snapshot() {
  try {
    const response = await fetch(OBSERVABLES_URL);
    if (response.ok) {
      const payload = await response.json();
      if (payload?.countries && typeof payload.countries === 'object') return payload;
    }
  } catch {}

  const indicators = Object.values(ALL_D4_METRICS).map(encodeURIComponent).join(';');
  const query = new URLSearchParams({format:'json', source:'2', per_page:'10000', mrnev:'2'});
  try {
    const response = await fetch(`${WORLD_BANK_URL}/${indicators}?${query}`);
    if (!response.ok) return null;
    const payload = await response.json();
    const rows = Array.isArray(payload) && Array.isArray(payload[1]) ? payload[1] : [];
    const grouped = {};
    for (const row of rows) {
      const code = String(row?.countryiso3code || '').toUpperCase();
      const metricId = INDICATOR_TO_METRIC[String(row?.indicator?.id || '')];
      if (!/^[A-Z]{3}$/.test(code) || !metricId || row?.value == null || row?.date == null) continue;
      grouped[code] ||= {};
      grouped[code][metricId] ||= [];
      grouped[code][metricId].push({value:row.value, year:Number(row.date) || row.date});
    }
    const countries = {};
    for (const [code,metrics] of Object.entries(grouped)) {
      countries[code] = {metrics:{}};
      for (const [metricId,values] of Object.entries(metrics)) {
        values.sort((a,b) => String(b.year).localeCompare(String(a.year)));
        countries[code].metrics[metricId] = {
          value:values[0].value,
          year:values[0].year,
          indicator:ALL_D4_METRICS[metricId],
          source:'World Bank World Development Indicators',
          previous:values[1] || null,
        };
      }
    }
    return {record_type:'world-country-observables-runtime-fallback', source:{id:'world-bank-wdi'}, countries};
  } catch {
    return null;
  }
}

ensureOptions();
ensureNote();
[worldGraph, observables] = await Promise.all([loadWorldGraph(), loadD4Snapshot()]);

// The core renderer owns flat, population and area. These listeners only supply
// extra descriptive modes after the core handler has made the extrusion visible.
heightSelect.addEventListener('change', applyMode);
relationTypeSelect?.addEventListener('change', () => {
  if (heightSelect.value === 'relationships') setRelationshipHeight();
  updateNote();
});
window.addEventListener('atlas-time-change', applyMode);
window.addEventListener('potato-atlas-time-change', applyMode);

viewMenu?.dispatchEvent(new Event('change', { bubbles: true }));
applyMode();

window.__potatoAtlasMetricDimensions = {
  relationshipCounts,
  coverageCounts,
  surfaces:D4_SURFACES,
  observables,
  refresh:applyMode,
  get mode() { return heightSelect.value; },
};
