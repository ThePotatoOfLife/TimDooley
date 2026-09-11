// D4 observable-country vector for the 3D World Relational Atlas.
//
// The inspector prefers a same-origin build snapshot when available, then falls
// back to one small batched World Bank WDI request for the selected country.
// Values stay dated and typed; raw magnitude never becomes Axis height.

const SNAPSHOT_URL = '../data/world-country-observables.json';
const panel = document.getElementById('panel');
const cache = new Map();
let snapshotPromise = null;
let renderToken = 0;

const METRICS = {
  population: {label:'Population', indicator:'SP.POP.TOTL', unit:'persons', format:'population'},
  gdp: {label:'GDP', indicator:'NY.GDP.MKTP.CD', unit:'current USD', format:'usd-large'},
  gdp_per_capita: {label:'GDP / person', indicator:'NY.GDP.PCAP.CD', unit:'current USD/person', format:'usd'},
  real_growth: {label:'Real GDP growth', indicator:'NY.GDP.MKTP.KD.ZG', unit:'percent/year', format:'percent'},
  unemployment: {label:'Unemployment', indicator:'SL.UEM.TOTL.ZS', unit:'percent of labour force', format:'percent'},
  life_expectancy: {label:'Life expectancy', indicator:'SP.DYN.LE00.IN', unit:'years', format:'years'},
  urbanization: {label:'Urban population', indicator:'SP.URB.TOTL.IN.ZS', unit:'percent of population', format:'percent'},
  internet_penetration: {label:'Internet use', indicator:'IT.NET.USER.ZS', unit:'percent of population', format:'percent'},
};
const INDICATOR_TO_METRIC = Object.fromEntries(Object.entries(METRICS).map(([metricId,spec]) => [spec.indicator,metricId]));

const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'
}[char]));

function currentCode() {
  const code = String(window.__potatoAtlasSelection?.current?.code || '').toUpperCase();
  return /^[A-Z]{3}$/.test(code) ? code : null;
}

function isCountryOverview(target = panel) {
  const eyebrow = target?.querySelector('.eyebrow')?.textContent || '';
  return /Canonical country|Territory \/ map polygon/i.test(eyebrow);
}

function number(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function compact(value, maximumFractionDigits = 1) {
  const n = number(value);
  if (n == null) return '—';
  return new Intl.NumberFormat('en', {notation:'compact', maximumFractionDigits}).format(n);
}

function fixed(value, digits = 1) {
  const n = number(value);
  if (n == null) return '—';
  return new Intl.NumberFormat('en', {maximumFractionDigits:digits, minimumFractionDigits:0}).format(n);
}

function formatValue(metricId, value) {
  const spec = METRICS[metricId];
  const n = number(value);
  if (n == null) return '—';
  if (spec?.format === 'population') return compact(n, 2);
  if (spec?.format === 'usd-large') {
    if (Math.abs(n) >= 1e12) return `$${fixed(n / 1e12, 2)}T`;
    if (Math.abs(n) >= 1e9) return `$${fixed(n / 1e9, 1)}B`;
    if (Math.abs(n) >= 1e6) return `$${fixed(n / 1e6, 1)}M`;
    return `$${fixed(n, 0)}`;
  }
  if (spec?.format === 'usd') return `$${new Intl.NumberFormat('en', {maximumFractionDigits:0}).format(n)}`;
  if (spec?.format === 'percent') return `${fixed(n, 1)}%`;
  if (spec?.format === 'years') return `${fixed(n, 1)} y`;
  return fixed(n, 1);
}

async function loadSnapshot() {
  if (snapshotPromise) return snapshotPromise;
  snapshotPromise = fetch(SNAPSHOT_URL)
    .then(response => response.ok ? response.json() : null)
    .catch(() => null);
  return snapshotPromise;
}

function normalizeSnapshotMetric(metricId, item) {
  if (!item || number(item.value) == null) return null;
  return {
    value:item.value,
    year:item.year,
    unit:item.unit || METRICS[metricId]?.unit,
    indicator:item.indicator || METRICS[metricId]?.indicator,
    source:item.source || 'World Bank World Development Indicators',
    source_id:item.source_id || 'world-bank-wdi',
    previous:item.previous && number(item.previous.value) != null ? item.previous : null,
    status:item.status || 'sourced',
  };
}

async function fetchWorldBankCountry(code) {
  const indicatorPath = Object.values(METRICS).map(spec => encodeURIComponent(spec.indicator)).join(';');
  const query = new URLSearchParams({format:'json', source:'2', per_page:'100', mrnev:'2'});
  const url = `https://api.worldbank.org/v2/country/${encodeURIComponent(code)}/indicator/${indicatorPath}?${query}`;
  try {
    const response = await fetch(url);
    if (!response.ok) return {};
    const payload = await response.json();
    const rows = Array.isArray(payload) && Array.isArray(payload[1]) ? payload[1] : [];
    const grouped = Object.fromEntries(Object.keys(METRICS).map(metricId => [metricId,[]]));
    for (const row of rows) {
      const indicator = String(row?.indicator?.id || '');
      const metricId = INDICATOR_TO_METRIC[indicator];
      if (!metricId || row?.value == null || row?.date == null) continue;
      grouped[metricId].push({value:row.value, year:Number(row.date) || row.date});
    }
    const metrics = {};
    for (const [metricId,values] of Object.entries(grouped)) {
      values.sort((a,b) => String(b.year).localeCompare(String(a.year)));
      if (!values.length) continue;
      metrics[metricId] = {
        value:values[0].value,
        year:values[0].year,
        unit:METRICS[metricId].unit,
        indicator:METRICS[metricId].indicator,
        source:'World Bank World Development Indicators',
        source_id:'world-bank-wdi',
        status:'sourced',
        previous:values[1] || null,
      };
    }
    return metrics;
  } catch {
    return {};
  }
}

async function observablesFor(code) {
  if (cache.has(code)) return cache.get(code);
  const promise = (async () => {
    const snapshot = await loadSnapshot();
    const row = snapshot?.countries?.[code];
    if (row?.metrics) {
      const metrics = {};
      for (const metricId of Object.keys(METRICS)) {
        const normalized = normalizeSnapshotMetric(metricId, row.metrics[metricId]);
        if (normalized) metrics[metricId] = normalized;
      }
      if (Object.keys(metrics).length) return {code, metrics, mode:'snapshot', generated_at:snapshot.generated_at, source:snapshot.source};
    }

    const metrics = await fetchWorldBankCountry(code);
    return {
      code,
      metrics,
      mode:'live-selected-country',
      source:{id:'world-bank-wdi', name:'World Bank World Development Indicators', url:'https://data.worldbank.org/indicator'},
    };
  })();
  cache.set(code, promise);
  return promise;
}

function priorHtml(metricId, metric) {
  const previous = metric?.previous;
  if (!previous || number(previous.value) == null) return '';
  return `<small class="d4-prior">prior ${esc(previous.year ?? '—')} · ${esc(formatValue(metricId, previous.value))}</small>`;
}

function metricHtml(metricId, metric) {
  const spec = METRICS[metricId];
  if (!metric) return '';
  return `<div class="d4-observable" data-d4-metric="${esc(metricId)}" title="${esc(metric.indicator || spec.indicator)} · ${esc(metric.unit || spec.unit)}">
    <span>${esc(spec.label)}</span>
    <b>${esc(formatValue(metricId, metric.value))}</b>
    <small>${esc(metric.year ?? '—')} · ${esc(metric.unit || spec.unit)}</small>
    ${priorHtml(metricId, metric)}
  </div>`;
}

function ensureStyle() {
  if (document.getElementById('atlasD4ObservablesStyle')) return;
  const style = document.createElement('style');
  style.id = 'atlasD4ObservablesStyle';
  style.textContent = `
    .atlas-d4-observables{border-color:#41544d}
    .atlas-d4-heading{display:flex;justify-content:space-between;gap:8px;align-items:flex-start}
    .atlas-d4-heading small{color:var(--muted);font-size:9px;text-align:right;max-width:150px}
    .d4-observable-grid{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:9px}
    .d4-observable{border:1px solid var(--line);border-radius:8px;padding:7px 8px;min-width:0;background:#101918}
    .d4-observable>span{display:block;color:var(--muted);font-size:9px;text-transform:uppercase;letter-spacing:.07em}
    .d4-observable>b{display:block;font-size:15px;margin:2px 0;overflow-wrap:anywhere}
    .d4-observable>small{display:block;color:#bac4bc;font-size:9px;line-height:1.25}
    .d4-observable .d4-prior{color:#839188;margin-top:2px}
    .d4-observable-empty{font-size:11px;color:var(--muted);padding:7px 0}
    .d4-observable-note{font-size:10px;margin-top:8px;line-height:1.35}
    @media(max-width:900px){.d4-observable-grid{grid-template-columns:1fr}}
  `;
  document.head.appendChild(style);
}

function insertCard(code, data) {
  if (!panel || !isCountryOverview(panel) || currentCode() !== code) return;
  panel.querySelectorAll('.atlas-d4-observables').forEach(node => node.remove());
  const metrics = data?.metrics || {};
  const available = Object.keys(METRICS).filter(metricId => metrics[metricId]);
  const card = document.createElement('div');
  card.className = 'card atlas-d4-observables';
  card.dataset.d4Code = code;
  card.innerHTML = `<div class="atlas-d4-heading"><div><b>D4 · observable country vector</b><div class="muted" style="font-size:10px">scale · production · prosperity · motion · labour · life · settlement · connectivity</div></div><small>${data.mode === 'snapshot' ? 'same-origin runtime snapshot' : 'one selected-country WDI request'}</small></div>
    <div class="d4-observable-grid">${available.length ? available.map(metricId => metricHtml(metricId, metrics[metricId])).join('') : '<div class="d4-observable-empty">No comparable D4 observations returned for this country.</div>'}</div>
    <div class="muted d4-observable-note">World Bank WDI · each metric keeps its own observation year, so years may differ. Prior points are retained only as dated observations to seed later D6 change analysis. Current USD is not PPP. Missing is not zero. None of these values determines Axis height or moral rank.</div>`;

  const anchor = panel.querySelector('.atlas-country-profile') || panel.querySelector('.grid');
  if (anchor?.parentNode) anchor.parentNode.insertBefore(card, anchor.nextSibling);
  else panel.appendChild(card);
  window.dispatchEvent(new CustomEvent('potato-atlas-d4-observables-rendered', {detail:{code, metrics, mode:data.mode}}));
}

async function render() {
  if (!panel || !isCountryOverview(panel)) return;
  const code = currentCode();
  if (!code) return;
  const token = ++renderToken;
  const existing = panel.querySelector(`.atlas-d4-observables[data-d4-code="${CSS.escape(code)}"]`);
  if (existing) return;

  const loading = document.createElement('div');
  loading.className = 'card atlas-d4-observables';
  loading.dataset.d4Code = code;
  loading.innerHTML = '<b>D4 · observable country vector</b><p class="muted" style="margin-bottom:0">Loading sourced country observations…</p>';
  const anchor = panel.querySelector('.atlas-country-profile') || panel.querySelector('.grid');
  if (anchor?.parentNode) anchor.parentNode.insertBefore(loading, anchor.nextSibling);
  else panel.appendChild(loading);

  const data = await observablesFor(code);
  if (token !== renderToken || currentCode() !== code || !isCountryOverview(panel)) return;
  insertCard(code, data);
}

ensureStyle();
window.addEventListener('potato-atlas-selection-change', () => { renderToken += 1; queueMicrotask(render); });
window.addEventListener('potato-atlas-panel-change', () => queueMicrotask(render));

if (panel) {
  let scheduled = false;
  const observer = new MutationObserver(() => {
    if (scheduled) return;
    scheduled = true;
    queueMicrotask(() => {
      scheduled = false;
      render();
    });
  });
  observer.observe(panel, {childList:true, subtree:true});
}

window.__potatoAtlasD4Observables = {
  metrics:METRICS,
  forCountry:observablesFor,
  render,
  clearCache:code => code ? cache.delete(String(code).toUpperCase()) : cache.clear(),
};

render();
