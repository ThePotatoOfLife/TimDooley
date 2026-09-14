// Neutral comparable country metrics for the World Relational Atlas.
// Same-origin runtime only: the browser never queries World Bank directly.

const SNAPSHOT_URL = '../data/world-country-metrics.json';
const panel = document.getElementById('panel');
const HEADLINE = ['gdp','gdp_per_capita','real_growth','inflation','unemployment','life_expectancy'];
let snapshotPromise = null;
let snapshot = null;

const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

function currentCode() {
  const current = window.__potatoAtlasSelection?.current || {};
  const code = String(current.activeCode || current.code || '').toUpperCase();
  return /^[A-Z]{3}$/.test(code) ? code : null;
}

async function loadSnapshot() {
  if (snapshotPromise) return snapshotPromise;
  snapshotPromise = fetch(SNAPSHOT_URL, {cache:'force-cache'})
    .then(async response => {
      if (!response.ok) return null;
      const payload = await response.json();
      if (payload?.record_type !== 'world-country-metrics-runtime') return null;
      snapshot = payload;
      return payload;
    })
    .catch(error => {
      console.warn('Country metrics snapshot unavailable:', error);
      return null;
    });
  return snapshotPromise;
}

function compactNumber(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return '—';
  const abs = Math.abs(n);
  if (abs >= 1e12) return `${(n/1e12).toFixed(2)}T`;
  if (abs >= 1e9) return `${(n/1e9).toFixed(2)}B`;
  if (abs >= 1e6) return `${(n/1e6).toFixed(1)}M`;
  if (abs >= 1e3) return `${(n/1e3).toFixed(1)}k`;
  return new Intl.NumberFormat('en',{maximumFractionDigits:2}).format(n);
}

function displayValue(metricId, observation) {
  const value = Number(observation?.value);
  if (!Number.isFinite(value)) return '—';
  if (metricId === 'gdp') return `$${compactNumber(value)}`;
  if (metricId === 'gdp_per_capita') return `$${new Intl.NumberFormat('en',{maximumFractionDigits:0}).format(value)}`;
  if (['real_growth','inflation','unemployment','labor_force_participation','urbanization','internet_penetration','electricity_access','trade_openness','fdi_inflow'].includes(metricId)) return `${new Intl.NumberFormat('en',{maximumFractionDigits:1}).format(value)}%`;
  if (metricId === 'life_expectancy') return `${new Intl.NumberFormat('en',{maximumFractionDigits:1}).format(value)} yr`;
  if (metricId === 'co2_per_capita') return `${new Intl.NumberFormat('en',{maximumFractionDigits:2}).format(value)} t/person`;
  if (metricId === 'population') return compactNumber(value);
  return compactNumber(value);
}

function metricTile(metricId, observation, registry) {
  const spec = registry?.[metricId] || {};
  return `<div class="atlas-country-metric" title="${esc(observation?.unit || spec.unit || '')}"><span>${esc(spec.label || metricId)}</span><b>${esc(displayValue(metricId, observation))}</b><small>${esc(observation?.year || '')}</small></div>`;
}

function ensureStyle() {
  if (document.getElementById('atlasCountryMetricsStyle')) return;
  const style = document.createElement('style');
  style.id = 'atlasCountryMetricsStyle';
  style.textContent = `
    .atlas-country-metrics{border-color:#3a4744}
    .atlas-country-metrics-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px;margin-top:8px}
    .atlas-country-metric{border:1px solid #2c3937;border-radius:7px;padding:7px;min-width:0}
    .atlas-country-metric span{display:block;color:var(--muted);font-size:9px;text-transform:uppercase;letter-spacing:.05em}
    .atlas-country-metric b{display:block;margin-top:2px;font-size:13px;overflow-wrap:anywhere}
    .atlas-country-metric small{display:block;color:var(--muted);margin-top:2px;font-size:9px}
    .atlas-country-metrics details{margin-top:8px}.atlas-country-metrics summary{cursor:pointer;color:var(--muted);font-size:10px}
    @media(max-width:900px){.atlas-country-metrics-grid{grid-template-columns:1fr 1fr}}
  `;
  document.head.appendChild(style);
}

function countryRow(data, code) { return data?.countries?.[code] || null; }

async function render() {
  if (!panel) return;
  const code = currentCode();
  if (!code) return;
  const data = await loadSnapshot();
  const row = countryRow(data, code);
  if (!data || !row || !Object.keys(row.metrics || {}).length) return;
  ensureStyle();

  const metrics = row.metrics || {};
  const registry = data.metrics || {};
  const headlineIds = HEADLINE.filter(id => metrics[id]);
  const moreIds = (data.metric_order || Object.keys(metrics)).filter(id => metrics[id] && !headlineIds.includes(id));
  let card = panel.querySelector('.atlas-country-metrics');
  if (!card) {
    card = document.createElement('div');
    card.className = 'card atlas-country-metrics';
    const profile = panel.querySelector('.atlas-country-profile');
    if (profile?.parentNode) profile.parentNode.insertBefore(card, profile.nextSibling);
    else panel.appendChild(card);
  }
  card.dataset.countryMetricsCode = code;
  const more = moreIds.length ? `<details><summary>More indicators (${moreIds.length})</summary><div class="atlas-country-metrics-grid">${moreIds.map(id => metricTile(id,metrics[id],registry)).join('')}</div></details>` : '';
  card.innerHTML = `<b>Comparable indicators</b><div class="muted">Latest sourced observation per metric; reference years can differ.</div><div class="atlas-country-metrics-grid">${headlineIds.map(id => metricTile(id,metrics[id],registry)).join('')}</div>${more}<div class="muted" style="margin-top:8px">${esc(data.source?.name || 'Sourced observations')} · missing is unknown, never zero · indicators do not determine Axis height or a country score.</div>`;
}

window.addEventListener('potato-atlas-panel-rendered', () => queueMicrotask(render));
window.addEventListener('potato-atlas-selection-change', event => { if (event?.detail?.selected !== false) queueMicrotask(render); });
window.addEventListener('potato-atlas-working-selection-change', event => { if (event?.detail?.selected !== false) queueMicrotask(render); });

window.__potatoAtlasCountryMetrics = {
  ready: loadSnapshot(),
  load: loadSnapshot,
  render,
  async country(code) { const data = await loadSnapshot(); return countryRow(data,String(code || '').toUpperCase()); },
  async metric(code,id) { const row = await this.country(code); return row?.metrics?.[id] || null; },
  get snapshot() { return snapshot; },
};

queueMicrotask(render);
