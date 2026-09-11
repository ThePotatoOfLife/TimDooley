// Registry-driven country Metric Explorer for the World Relational Atlas.
//
// The metric snapshot is a presentation runtime, not a canonical database. This
// module delegates the Metric Lens sub-choice to one sourced registry while the
// existing Lens framework remains the top-level semantic owner of country fill.

const map = window.__potatoAtlasMap;
if (!map) throw new Error('Atlas metrics require the core map.');

const METRICS_URL = '../data/world-country-metrics.json';
const UNKNOWN = '#303938';
const SCALE_COLORS = ['#263432', '#36514b', '#527466', '#78977d', '#a7b87f', '#d0c77e'];
const DIVERGING_COLORS = ['#8e5b58', '#725f5a', '#4d6661', '#6e8c73', '#a7b87f'];
const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
}[char]));

let payload = { metrics: {}, countries: {} };
let available = false;
let currentMetric = null;
let historicalSuppressed = false;
let requestToken = 0;

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${response.status} ${url}`);
  return response.json();
}

function metricIds() { return Object.keys(payload.metrics || {}); }
function definition(id = currentMetric) { return id ? payload.metrics?.[id] || null : null; }
function forCountry(iso3) { return payload.countries?.[String(iso3 || '').toUpperCase()] || {}; }
function observation(iso3, metricId = currentMetric) { return forCountry(iso3)?.[metricId] || null; }

function currentLensIsMetric() {
  return window.__potatoAtlasLenses?.getState?.().id === 'metric';
}

function clearMetricStates() {
  for (const code of Object.keys(payload.countries || {})) {
    try {
      map.removeFeatureState({ source: 'countries', id: code }, 'metricValue');
      map.removeFeatureState({ source: 'countries', id: code }, 'metricHas');
    } catch { /* polygon source may not contain every canonical code */ }
  }
}

function applyFeatureStates(metricId) {
  clearMetricStates();
  for (const [code, row] of Object.entries(payload.countries || {})) {
    const value = Number(row?.[metricId]?.value);
    try {
      map.setFeatureState({ source: 'countries', id: code }, {
        metricValue: Number.isFinite(value) ? value : 0,
        metricHas: Number.isFinite(value),
      });
    } catch { /* ignore canonical states not represented by current polygon source */ }
  }
}

function safeDomain(def) {
  const domain = def?.display_domain || def?.observed_domain;
  if (!Array.isArray(domain) || domain.length !== 2) return [0, 1];
  const low = Number(domain[0]), high = Number(domain[1]);
  if (!Number.isFinite(low) || !Number.isFinite(high) || low === high) return [low || 0, (low || 0) + 1];
  return low < high ? [low, high] : [high, low];
}

function transformValueExpression(transform) {
  if (transform === 'log1p') return ['ln', ['+', 1, ['max', ['feature-state', 'metricValue'], 0]]];
  return ['feature-state', 'metricValue'];
}

function transformedDomain(def) {
  const [rawLow, rawHigh] = safeDomain(def);
  if (def?.transform === 'log1p') return [Math.log1p(Math.max(0, rawLow)), Math.log1p(Math.max(0, rawHigh))];
  return [rawLow, rawHigh];
}

function sequentialExpression(def) {
  const value = transformValueExpression(def?.transform);
  const [low, high] = transformedDomain(def);
  const span = high - low || 1;
  const stops = SCALE_COLORS.flatMap((color, index) => [low + span * (index / (SCALE_COLORS.length - 1)), color]);
  return ['case', ['boolean', ['feature-state', 'metricHas'], false], ['interpolate', ['linear'], value, ...stops], UNKNOWN];
}

function divergingExpression(def) {
  const [low, high] = safeDomain(def);
  const extent = Math.max(Math.abs(low), Math.abs(high), 1);
  return [
    'case',
    ['boolean', ['feature-state', 'metricHas'], false],
    ['interpolate', ['linear'], ['feature-state', 'metricValue'],
      -extent, DIVERGING_COLORS[0],
      -extent * 0.25, DIVERGING_COLORS[1],
      0, DIVERGING_COLORS[2],
      extent * 0.25, DIVERGING_COLORS[3],
      extent, DIVERGING_COLORS[4]
    ],
    UNKNOWN
  ];
}

function expression(metricId = currentMetric) {
  const def = definition(metricId);
  if (!def) return UNKNOWN;
  if (def.transform === 'diverging-zero') return divergingExpression(def);
  return sequentialExpression(def);
}

function setFill(fillExpression) {
  for (const layer of ['countries-fill', 'countries-extrude']) {
    if (!map.getLayer(layer)) continue;
    const property = layer === 'countries-fill' ? 'fill-color' : 'fill-extrusion-color';
    map.setPaintProperty(layer, property, fillExpression);
  }
}

function compact(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return '—';
  return new Intl.NumberFormat('en', {
    notation: Math.abs(number) >= 1e6 ? 'compact' : 'standard',
    maximumFractionDigits: Math.abs(number) >= 100 ? 1 : 2,
  }).format(number);
}

function formatObservation(obs, def) {
  if (!obs) return '—';
  const unit = obs.unit || def?.unit || '';
  if (unit === 'current USD') return `$${compact(obs.value)}`;
  if (unit === 'current USD / person') return `$${new Intl.NumberFormat('en', { maximumFractionDigits: 0 }).format(Number(obs.value))}`;
  if (unit.includes('percent')) return `${compact(obs.value)}%`;
  return `${compact(obs.value)}${unit ? ` ${unit}` : ''}`;
}

function rankFor(code, metricId = currentMetric) {
  const current = Number(observation(code, metricId)?.value);
  if (!Number.isFinite(current)) return null;
  const values = Object.entries(payload.countries || {})
    .map(([iso3, row]) => [iso3, Number(row?.[metricId]?.value)])
    .filter(([, value]) => Number.isFinite(value))
    .sort((a, b) => b[1] - a[1]);
  const index = values.findIndex(([iso3]) => iso3 === code);
  return index < 0 ? null : { rank: index + 1, coverage: values.length };
}

function renderLegend() {
  if (!currentLensIsMetric()) return;
  const legend = document.getElementById('atlasLensLegend');
  if (!legend) return;
  legend.hidden = false;
  if (!available || !definition()) {
    legend.innerHTML = '<b>Metric unavailable</b><small>The harmonized metric snapshot is unavailable; neutral geography remains usable.</small>';
    return;
  }
  const def = definition();
  if (historicalSuppressed) {
    legend.innerHTML = `<b>${esc(def.label)}</b><small>Historical metric view unavailable. Current/latest observations are not projected backward onto the selected historical date.</small>`;
    return;
  }
  const [low, high] = safeDomain(def);
  const clipped = def.display_domain_method ? ` · ${def.display_domain_method}` : '';
  legend.innerHTML = `<b>Metric · ${esc(def.label)}</b><div class="atlas-metric-legend-scale"><span>${esc(compact(low))}</span><i></i><span>${esc(compact(high))}</span></div><small>${esc(def.unit || '')} · ${esc(def.coverage || 0)} countries with data${esc(clipped)}</small>`;
}

function applyMetricFill() {
  if (!currentLensIsMetric()) return;
  if (!available || !currentMetric || historicalSuppressed) {
    setFill(UNKNOWN);
    renderLegend();
    return;
  }
  applyFeatureStates(currentMetric);
  setFill(expression(currentMetric));
  renderLegend();
}

function persist() {
  const url = new URL(location.href);
  if (currentMetric) url.searchParams.set('metric', currentMetric);
  else url.searchParams.delete('metric');
  history.replaceState({}, '', url);
}

function ensureMetricSelector() {
  const lensControl = document.getElementById('atlasLensControl');
  if (!lensControl || document.getElementById('atlasMetricSelector')) return;
  const selector = document.createElement('select');
  selector.id = 'atlasMetricSelector';
  selector.setAttribute('aria-label', 'Country metric');
  selector.title = 'Choose the sourced country metric used by the Metric Lens';
  selector.hidden = true;
  lensControl.querySelector('#atlasLensOption')?.after(selector);
  selector.addEventListener('change', event => setMetric(event.target.value));
  const style = document.createElement('style');
  style.id = 'atlasMetricStyle';
  style.textContent = `.atlas-metric-legend-scale{display:grid;grid-template-columns:auto minmax(80px,1fr) auto;gap:6px;align-items:center;margin:4px 0}.atlas-metric-legend-scale i{height:7px;border-radius:999px;background:linear-gradient(90deg,${SCALE_COLORS.join(',')})}.atlas-active-metric{border-color:#465b55}.atlas-active-metric-row{display:flex;justify-content:space-between;gap:8px;align-items:flex-start}.atlas-active-metric-row small{display:block;color:var(--muted);font-size:9px;margin-top:2px}`;
  document.head.appendChild(style);
}

function syncSelector() {
  ensureMetricSelector();
  const selector = document.getElementById('atlasMetricSelector');
  const legacyOption = document.getElementById('atlasLensOption');
  if (!selector) return;
  const isMetric = currentLensIsMetric();
  selector.hidden = !isMetric || !available;
  if (legacyOption && isMetric) legacyOption.hidden = true;
  if (!isMetric) return;
  selector.innerHTML = metricIds().map(id => `<option value="${esc(id)}">${esc(payload.metrics[id].label || id)}</option>`).join('');
  if (currentMetric && metricIds().includes(currentMetric)) selector.value = currentMetric;
}

function activeCode() {
  const selection = window.__potatoAtlasSelection?.current || {};
  return String(selection.activeCode || selection.code || '').toUpperCase();
}

function augmentPulse() {
  const pulse = document.querySelector('.atlas-country-pulse');
  const code = activeCode();
  if (!pulse || !code || !currentMetric || !available) return;
  const existing = pulse.querySelector('.atlas-active-metric');
  if (existing?.dataset.metricId === currentMetric && existing?.dataset.code === code) return;
  existing?.remove();
  const obs = observation(code);
  const def = definition();
  const rank = rankFor(code);
  const block = document.createElement('div');
  block.className = 'card atlas-active-metric';
  block.dataset.metricId = currentMetric;
  block.dataset.code = code;
  block.innerHTML = `<b>Selected metric · ${esc(def?.label || currentMetric)}</b><div class="atlas-active-metric-row"><div><strong>${esc(formatObservation(obs, def))}</strong><small>${obs ? esc([obs.period, obs.source].filter(Boolean).join(' · ')) : 'No comparable observation in this runtime.'}</small></div>${rank ? `<span class="pill">rank ${rank.rank} / ${rank.coverage}</span>` : ''}</div>`;
  const metrics = pulse.querySelector('.pulse-metrics');
  if (metrics?.parentNode) metrics.parentNode.insertBefore(block, metrics.nextSibling);
  else pulse.appendChild(block);
}

async function setMetric(id, { activateLens = true } = {}) {
  if (!available) return false;
  id = String(id || '');
  if (!payload.metrics?.[id]) id = metricIds()[0] || null;
  if (!id) return false;
  currentMetric = id;
  persist();
  syncSelector();
  if (activateLens && !currentLensIsMetric()) {
    await window.__potatoAtlasLenses?.setLens?.('metric', 'population');
  }
  const token = ++requestToken;
  if (token === requestToken) applyMetricFill();
  augmentPulse();
  window.dispatchEvent(new CustomEvent('potato-atlas-metric-change', { detail: { metric: currentMetric, definition: definition() } }));
  return true;
}

function timeState(event) {
  const state = event?.detail || window.__potatoAtlasTime?.getState?.() || { mode: 'current' };
  historicalSuppressed = Boolean(state.mode && state.mode !== 'current');
  applyMetricFill();
}

async function boot() {
  ensureMetricSelector();
  try {
    payload = await fetchJson(METRICS_URL);
    available = Boolean(payload?.metrics && payload?.countries);
  } catch (error) {
    console.warn('Atlas metric runtime unavailable; foundation map remains usable.', error);
    payload = { metrics: {}, countries: {} };
    available = false;
  }
  const requested = new URL(location.href).searchParams.get('metric');
  currentMetric = payload.metrics?.[requested] ? requested : (payload.metrics?.population ? 'population' : metricIds()[0] || null);
  syncSelector();
  if (currentMetric) applyFeatureStates(currentMetric);
  if (currentLensIsMetric()) applyMetricFill();
  augmentPulse();
  window.dispatchEvent(new CustomEvent('potato-atlas-metrics-ready', { detail: { available, metric: currentMetric } }));
}

window.addEventListener('potato-atlas-lens-change', () => { syncSelector(); applyMetricFill(); augmentPulse(); });
window.addEventListener('potato-atlas-working-selection-change', augmentPulse);
window.addEventListener('potato-atlas-selection-change', augmentPulse);
window.addEventListener('atlas-time-change', timeState);
window.addEventListener('potato-atlas-module-ready', event => {
  if (event?.detail?.label === 'Country Pulse') augmentPulse();
});

window.__potatoAtlasMetrics = {
  setMetric,
  getMetric() { return currentMetric; },
  forCountry,
  observation,
  expression,
  rankFor,
  get registry() { return payload.metrics || {}; },
  get available() { return available; },
  get historicalSuppressed() { return historicalSuppressed; },
};

await boot();
