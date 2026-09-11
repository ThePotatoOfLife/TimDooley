// Color Lens framework for the World Relational Atlas.
//
// Exactly one Lens owns country fill color at a time. Selection remains an
// outline/state concern, so choosing a metric or demographic view never erases
// which countries are selected. Project Axis interpretation stays separate from
// empirical alliances and descriptive religious composition.

const map = window.__potatoAtlasMap;
if (!map) throw new Error('Atlas Lenses require the core map.');

const WORLD_URL = '../data/world-relational-map.json';
const DEMOGRAPHY_URL = '../data/world-country-demography.json';
const NEUTRAL = '#566262';
const UNKNOWN = '#303938';
const METRIC_PALETTE = ['#263432', '#36514b', '#527466', '#78977d', '#a7b87f', '#d0c77e'];

const RELIGION_LABELS = {
  dominant: 'Dominant category',
  christian: 'Christian share',
  muslim: 'Muslim share',
  hindu: 'Hindu share',
  buddhist: 'Buddhist share',
  jewish: 'Jewish share',
  other_religions: 'Other religions share',
  unaffiliated: 'Unaffiliated share',
};
const RELIGION_COLORS = {
  christian: '#d7b66f', muslim: '#79aa80', hindu: '#d49369', buddhist: '#c7a86d',
  jewish: '#75a6d6', other_religions: '#a687bd', unaffiliated: '#899398',
};
const ALIGNMENT_COLORS = {
  north: '#58b6c7', west: '#d0a352', east: '#c96f58', south: '#6fa77a', overlap: '#a57bc3', unclassified: UNKNOWN,
};
const METRIC_OPTIONS = [
  ['population','Population'], ['area','Area'], ['gdp','GDP'], ['gdp_per_capita','GDP / person'],
  ['gdp_per_capita_ppp','GDP / person · PPP'], ['real_growth','Real GDP growth'], ['inflation','Inflation'],
  ['unemployment','Unemployment'], ['labour_force_participation','Labour participation'],
  ['life_expectancy','Life expectancy'], ['fertility','Fertility'], ['urbanization','Urban population'],
  ['poverty','Poverty rate'], ['internet_penetration','Internet use'], ['co2_emissions','CO₂ / person'],
];
const QUICK_METRICS = new Set(['population','gdp','gdp_per_capita','real_growth','inflation','unemployment','life_expectancy','internet_penetration']);

let world;
let demography;
let state = { id: 'neutral', option: '' };
let applying = false;
let pendingApply = false;
let metricLoading = null;
let metricSummary = null;

const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
}[char]));

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${response.status} ${url}`);
  return response.json();
}
async function worldData() {
  if (!world) world = await fetchJson(WORLD_URL);
  return world;
}
async function demographyData() {
  if (!demography) demography = await fetchJson(DEMOGRAPHY_URL);
  return demography;
}

function setFill(expression) {
  for (const layer of ['countries-fill', 'countries-extrude']) {
    if (!map.getLayer(layer)) continue;
    const property = layer === 'countries-fill' ? 'fill-color' : 'fill-extrusion-color';
    map.setPaintProperty(layer, property, expression);
  }
}
function matchExpression(mapping, fallback = UNKNOWN) {
  const parts = ['match', ['get', 'iso3']];
  for (const [code, color] of Object.entries(mapping).sort(([a], [b]) => a.localeCompare(b))) parts.push(code, color);
  parts.push(fallback);
  return parts;
}
function clearReligionState() {
  const rows = demography?.countries || {};
  for (const code of Object.keys(rows)) {
    try {
      map.removeFeatureState({ source: 'countries', id: code }, 'lensValue');
      map.removeFeatureState({ source: 'countries', id: code }, 'lensHas');
      map.removeFeatureState({ source: 'countries', id: code }, 'lensCategory');
    } catch { /* feature may not exist in the polygon source */ }
  }
}

function alignmentMap(data) {
  const memberships = new Map();
  const add = (code, family) => {
    if (!/^[A-Z]{3}$/.test(String(code || ''))) return;
    if (!memberships.has(code)) memberships.set(code, new Set());
    memberships.get(code).add(family);
  };
  const axis = data.project_axis || {};
  const north = axis.north || {};
  for (const [group, codes] of Object.entries(north)) {
    if (!Array.isArray(codes)) continue;
    if (['external','excluded_current_version','future_reconnection'].includes(group)) continue;
    codes.forEach(code => add(code, 'north'));
  }
  for (const codes of Object.values(axis.west || {})) if (Array.isArray(codes)) codes.forEach(code => add(code, 'west'));
  for (const codes of Object.values(axis.east || {})) if (Array.isArray(codes)) codes.forEach(code => add(code, 'east'));
  const mapping = {};
  for (const [code, families] of memberships) {
    const values = [...families];
    mapping[code] = ALIGNMENT_COLORS[values.length > 1 ? 'overlap' : values[0]] || UNKNOWN;
  }
  return mapping;
}

function allianceMap(data, option) {
  const registry = data.empirical_memberships || {};
  const key = option === 'five-eyes' ? 'Five_Eyes' : option.toUpperCase();
  const group = registry[key] || {};
  const mapping = {};
  for (const code of group.members || []) mapping[code] = '#5b9fd0';
  for (const code of group.partners || []) if (!mapping[code]) mapping[code] = '#8d7bc1';
  return { mapping, group, key };
}

function setReligionFeatureStates(data, option) {
  const rows = data.countries || {};
  for (const [code, row] of Object.entries(rows)) {
    const composition = row?.religion?.composition || {};
    try {
      if (option === 'dominant') {
        const entries = Object.entries(composition).filter(([, value]) => Number.isFinite(Number(value)));
        const category = entries.sort((a, b) => Number(b[1]) - Number(a[1]))[0]?.[0] || null;
        map.setFeatureState({ source: 'countries', id: code }, { lensCategory: category || 'unknown', lensHas: Boolean(category) });
      } else {
        const value = Number(composition[option]);
        map.setFeatureState({ source: 'countries', id: code }, { lensValue: Number.isFinite(value) ? value : 0, lensHas: Number.isFinite(value) });
      }
    } catch { /* ignore territories not represented in the polygon source */ }
  }
}

function religionExpression(option) {
  if (option === 'dominant') {
    const expression = ['match', ['coalesce', ['feature-state', 'lensCategory'], 'unknown']];
    for (const [key, color] of Object.entries(RELIGION_COLORS)) expression.push(key, color);
    expression.push(UNKNOWN);
    return expression;
  }
  const base = RELIGION_COLORS[option] || '#82a8a3';
  return ['case', ['boolean', ['feature-state', 'lensHas'], false],
    ['interpolate', ['linear'], ['feature-state', 'lensValue'], 0, '#1e2928', 20, '#3c5551', 50, base, 80, '#e3d8a2', 100, '#fff0bf'], UNKNOWN];
}

function nativeMetricExpression(option) {
  if (option === 'area') {
    return ['case', ['>', ['get', 'area'], 0], ['step', ['get', 'area'], '#263432', 10000, '#36514b', 100000, '#527466', 500000, '#78977d', 1000000, '#a7b87f', 5000000, '#d0c77e'], UNKNOWN];
  }
  return ['case', ['>', ['get', 'population'], 0], ['step', ['get', 'population'], '#263432', 1000000, '#36514b', 10000000, '#527466', 50000000, '#78977d', 100000000, '#a7b87f', 500000000, '#d0c77e'], UNKNOWN];
}

function metricStateExpression(summary) {
  if (summary?.scale === 'diverging-zero' && Number.isFinite(summary.maxAbs) && summary.maxAbs > 0) {
    return ['case', ['boolean', ['feature-state', 'metricHas'], false],
      ['interpolate', ['linear'], ['feature-state', 'metricValue'], -summary.maxAbs, '#b56b63', 0, '#c9c3a2', summary.maxAbs, '#6ea385'], UNKNOWN];
  }
  const values = [summary?.min, summary?.q25, summary?.median, summary?.q75, summary?.max]
    .filter(Number.isFinite).sort((a, b) => a - b).filter((value, index, rows) => !index || value !== rows[index - 1]);
  if (values.length < 2) return ['case', ['boolean', ['feature-state', 'metricHas'], false], '#78977d', UNKNOWN];
  const scale = ['interpolate', ['linear'], ['feature-state', 'metricValue']];
  values.forEach((value, index) => {
    const paletteIndex = Math.round(index * (METRIC_PALETTE.length - 1) / (values.length - 1));
    scale.push(value, METRIC_PALETTE[paletteIndex]);
  });
  return ['case', ['boolean', ['feature-state', 'metricHas'], false], scale, UNKNOWN];
}

function legendRows(items) {
  return items.map(([label, color]) => `<span class="atlas-lens-key"><i style="background:${esc(color)}"></i>${esc(label)}</span>`).join('');
}
function showLegend(title, note, rows = '', extra = '', loading = false) {
  const legend = document.getElementById('atlasLensLegend');
  if (!legend) return;
  legend.hidden = state.id === 'neutral';
  legend.classList.toggle('metric-loading', loading);
  legend.innerHTML = `<b>${esc(title)}</b>${extra || ''}${rows ? `<div class="atlas-lens-keys">${rows}</div>` : ''}<small>${esc(note)}</small>`;
}
function sameLens(a, b) { return a?.id === b?.id && a?.option === b?.option; }
function metricLabel(id) { return METRIC_OPTIONS.find(([value]) => value === id)?.[1] || id; }

function activeMetricExtra(option) {
  const metrics = window.__potatoAtlasMetrics;
  const current = window.__potatoAtlasSelection?.current || {};
  const code = current.activeCode || current.code;
  if (!metrics || !code || ['population','area'].includes(option)) return '';
  const item = metrics.forCountry(code, option);
  const name = current.name || code;
  if (!item) return `<div class="atlas-lens-country-value"><span>${esc(name)}</span><b>No comparable value</b></div>`;
  const meta = [item.period, item.source].filter(Boolean).join(' · ');
  return `<div class="atlas-lens-country-value"><span>${esc(name)}</span><b>${esc(metrics.formatValue(item.value, option))}</b>${meta ? `<small>${esc(meta)}</small>` : ''}</div>`;
}

function showMetricLegend(option, summary, { loading = false, completed = 0, total = 0 } = {}) {
  if (loading) {
    showLegend(`Metric · ${metricLabel(option)}`, `Loading sourced country records${total ? ` · ${completed}/${total}` : '…'}`, '', '', true);
    return;
  }
  if (['population','area'].includes(option)) {
    showLegend(`Metric · ${metricLabel(option)}`, 'Current geographic runtime · missing values remain neutral.', legendRows([
      ['Lower', METRIC_PALETTE[0]], ['Mid', METRIC_PALETTE[2]], ['Higher', METRIC_PALETTE[4]], ['Highest tier', METRIC_PALETTE[5]]
    ]));
    return;
  }
  const coverage = Number.isFinite(summary?.coverage) ? `${summary.coverage}/${summary.total || 195} countries` : 'available countries';
  const rows = summary?.scale === 'diverging-zero'
    ? legendRows([['Negative', '#b56b63'], ['Near zero', '#c9c3a2'], ['Positive', '#6ea385']])
    : legendRows([['Lower', METRIC_PALETTE[0]], ['Mid', METRIC_PALETTE[2]], ['Higher', METRIC_PALETTE[4]], ['Highest', METRIC_PALETTE[5]]]);
  showLegend(`Metric · ${metricLabel(option)}`, `${coverage} · latest comparable sourced values; periods vary. Missing ≠ zero.`, rows, activeMetricExtra(option));
}

async function applyMetric(option, requested) {
  if (['population','area'].includes(option)) {
    metricSummary = { id: option, native: true };
    setFill(nativeMetricExpression(option));
    showMetricLegend(option, metricSummary);
    return;
  }
  const metrics = window.__potatoAtlasMetrics;
  if (!metrics) throw new Error('Metrics runtime is unavailable.');
  metricLoading = option;
  showMetricLegend(option, null, { loading: true });
  const summary = await metrics.prepare(option);
  if (!sameLens(state, requested)) return;
  metricLoading = null;
  metricSummary = summary;
  setFill(metricStateExpression(summary));
  showMetricLegend(option, summary);
}

async function applyLens() {
  if (applying) { pendingApply = true; return; }
  applying = true;
  const requested = { ...state };
  try {
    if (requested.id !== 'religion') clearReligionState();
    if (requested.id === 'neutral') {
      metricLoading = null; metricSummary = null;
      if (!sameLens(state, requested)) return;
      setFill(NEUTRAL);
      showLegend('Neutral', 'Country fill carries no analytical category.');
      return;
    }
    if (requested.id === 'alignment') {
      const data = await worldData();
      if (!sameLens(state, requested)) return;
      setFill(matchExpression(alignmentMap(data), UNKNOWN));
      showLegend('Alignment / Axis', 'Project interpretation — not sovereignty, consent or empirical alliance membership.', legendRows([
        ['North', ALIGNMENT_COLORS.north], ['West', ALIGNMENT_COLORS.west], ['East', ALIGNMENT_COLORS.east], ['South', ALIGNMENT_COLORS.south], ['Overlap', ALIGNMENT_COLORS.overlap]
      ]));
      return;
    }
    if (requested.id === 'alliances') {
      const data = await worldData();
      if (!sameLens(state, requested)) return;
      const { mapping, group, key } = allianceMap(data, requested.option || 'nato');
      setFill(matchExpression(mapping, UNKNOWN));
      showLegend(`Alliances · ${key.replaceAll('_', ' ')}`, `Empirical membership view${group.updated ? ` · updated ${group.updated}` : ''}. Non-members recede.`, legendRows([
        ['Member', '#5b9fd0'], ['Partner', '#8d7bc1'], ['Other / unknown', UNKNOWN]
      ]));
      return;
    }
    if (requested.id === 'religion') {
      const data = await demographyData();
      if (!sameLens(state, requested)) return;
      const option = requested.option || 'dominant';
      setReligionFeatureStates(data, option);
      setFill(religionExpression(option));
      const rows = option === 'dominant'
        ? legendRows(Object.entries(RELIGION_COLORS).map(([key, color]) => [RELIGION_LABELS[key] || key, color]))
        : legendRows([['Low share', '#1e2928'], ['Higher share', RELIGION_COLORS[option] || '#82a8a3'], ['Very high share', '#fff0bf']]);
      showLegend(`Religion · ${RELIGION_LABELS[option] || option}`, 'Descriptive religious-identity composition; it does not imply political loyalty, conduct or belief intensity.', rows);
      return;
    }
    if (requested.id === 'metric') {
      const option = requested.option || 'population';
      await applyMetric(option, requested);
    }
  } catch (error) {
    console.warn('Atlas Lens unavailable:', error);
    if (sameLens(state, requested)) {
      state = { id: 'neutral', option: '' };
      syncControls();
      persist();
      setFill(NEUTRAL);
      showLegend('Lens unavailable', 'Optional Lens data could not be loaded; neutral geography remains usable.');
    }
  } finally {
    applying = false;
    if (pendingApply || !sameLens(state, requested)) {
      pendingApply = false;
      queueMicrotask(applyLens);
    }
  }
}

function persist() {
  const url = new URL(location.href);
  if (state.id === 'neutral') {
    url.searchParams.delete('lens');
    url.searchParams.delete('lensOption');
  } else {
    url.searchParams.set('lens', state.id);
    if (state.option) url.searchParams.set('lensOption', state.option); else url.searchParams.delete('lensOption');
  }
  history.replaceState({}, '', url);
}

function optionConfig(id) {
  if (id === 'alliances') return [['nato','NATO'],['brics','BRICS'],['aukus','AUKUS'],['five-eyes','Five Eyes']];
  if (id === 'religion') return Object.entries(RELIGION_LABELS).map(([value, label]) => [value, label]);
  if (id === 'metric') return METRIC_OPTIONS;
  return [];
}
function defaultOption(id) {
  return id === 'alliances' ? 'nato' : id === 'religion' ? 'dominant' : id === 'metric' ? 'population' : '';
}
function syncControls() {
  const family = document.getElementById('atlasLensFamily');
  const option = document.getElementById('atlasLensOption');
  if (family && option) {
    family.value = state.id;
    const choices = optionConfig(state.id);
    option.innerHTML = choices.map(([value, label]) => `<option value="${esc(value)}">${esc(label)}</option>`).join('');
    option.hidden = !choices.length;
    if (choices.length) option.value = choices.some(([value]) => value === state.option) ? state.option : defaultOption(state.id);
  }
  const quick = document.getElementById('atlasLensQuickSelect');
  if (quick) {
    if (state.id === 'metric' && QUICK_METRICS.has(state.option)) quick.value = state.option;
    else if (state.id === 'neutral') quick.value = 'neutral';
    else quick.value = 'other';
  }
}

async function setLens(id, option = '') {
  const allowed = new Set(['neutral','alignment','alliances','religion','metric']);
  id = allowed.has(id) ? id : 'neutral';
  const choices = optionConfig(id).map(([value]) => value);
  option = choices.length ? (choices.includes(option) ? option : defaultOption(id)) : '';
  state = { id, option };
  syncControls();
  persist();
  await applyLens();
  window.dispatchEvent(new CustomEvent('potato-atlas-lens-change', { detail: { ...state } }));
}

function ensureUi() {
  if (document.getElementById('atlasLensControl')) return;
  const host = document.querySelector('#layersMenu .menu-pop');
  if (!host) return;

  const block = document.createElement('div');
  block.id = 'atlasLensControl';
  block.innerHTML = `<div class="menu-title">Color Lens</div><select id="atlasLensFamily" aria-label="Country color Lens"><option value="neutral">Neutral</option><option value="alignment">Alignment / Axis</option><option value="alliances">Alliances</option><option value="religion">Religion</option><option value="metric">Metric</option></select><select id="atlasLensOption" aria-label="Lens option" hidden></select><div class="muted atlas-lens-hint">One Lens owns country fill color at a time. Selection stays in outlines.</div>`;
  const registry = host.querySelector('.atlas-layer-registry');
  if (registry) host.insertBefore(block, registry); else host.appendChild(block);
  block.querySelector('#atlasLensFamily').addEventListener('change', event => setLens(event.target.value, defaultOption(event.target.value)));
  block.querySelector('#atlasLensOption').addEventListener('change', event => setLens(state.id, event.target.value));

  const quick = document.createElement('div');
  quick.id = 'atlasLensQuick';
  quick.title = 'Quick Lens';
  quick.innerHTML = `<span>Lens</span><select id="atlasLensQuickSelect" aria-label="Quick Lens"><option value="neutral">Neutral</option>${METRIC_OPTIONS.filter(([id]) => QUICK_METRICS.has(id)).map(([id, label]) => `<option value="${esc(id)}">${esc(label)}</option>`).join('')}<option value="other" disabled>Other lens active</option></select>`;
  document.querySelector('.mapwrap')?.appendChild(quick);
  quick.querySelector('select').addEventListener('change', event => {
    if (event.target.value === 'neutral') setLens('neutral');
    else setLens('metric', event.target.value);
  });

  const legend = document.createElement('div');
  legend.id = 'atlasLensLegend';
  legend.hidden = true;
  document.querySelector('.mapwrap')?.appendChild(legend);

  const style = document.createElement('style');
  style.id = 'atlasLensStyle';
  style.textContent = `
    #atlasLensControl{margin:7px 0;padding:7px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}#atlasLensControl select{display:block;width:100%;margin:4px 0}.atlas-lens-hint{font-size:9px;line-height:1.35;margin-top:4px}
    #atlasLensQuick{position:absolute;z-index:5;left:10px;top:10px;display:flex;align-items:center;gap:6px;padding:5px 7px;border:1px solid #40514e;border-radius:10px;background:#0b1212e8;box-shadow:0 5px 18px #0005;font-size:10px;color:#c9d3cc}#atlasLensQuick span{font-weight:700;color:#eef2ea}#atlasLensQuick select{max-width:165px;padding:4px 24px 4px 6px}
    #atlasLensLegend{position:absolute;z-index:4;left:10px;top:50px;max-width:360px;padding:8px 10px;border:1px solid #344442;border-radius:10px;background:#0b1212e8;box-shadow:0 5px 18px #0006;font-size:10px}#atlasLensLegend[hidden]{display:none!important}#atlasLensLegend.metric-loading{opacity:.86}#atlasLensLegend>b{display:block;margin-bottom:4px;color:#edf2e9}.atlas-lens-keys{display:flex;flex-wrap:wrap;gap:4px 8px;margin:5px 0}.atlas-lens-key{display:inline-flex;align-items:center;gap:4px;color:#cbd4cd}.atlas-lens-key i{width:9px;height:9px;border-radius:2px;border:1px solid #ffffff35}#atlasLensLegend>small{display:block;color:var(--muted);line-height:1.35}.atlas-lens-country-value{display:grid;grid-template-columns:1fr auto;gap:2px 10px;margin:5px 0;padding:6px 7px;border-radius:7px;background:#101b1a}.atlas-lens-country-value span{color:#cbd4cd}.atlas-lens-country-value b{color:#f2dda2}.atlas-lens-country-value small{grid-column:1/-1;color:var(--muted)}
    @media(max-width:900px){#atlasLensQuick{left:8px;top:8px}#atlasLensLegend{left:8px;top:48px;max-width:calc(100% - 16px)}}
  `;
  document.head.appendChild(style);
}

function restoreState() {
  const url = new URL(location.href);
  const id = url.searchParams.get('lens') || 'neutral';
  const option = url.searchParams.get('lensOption') || defaultOption(id);
  return setLens(id, option);
}

window.addEventListener('potato-atlas-metric-progress', event => {
  if (state.id !== 'metric' || !metricLoading) return;
  showMetricLegend(state.option, null, { loading: true, completed: event.detail?.completed || 0, total: event.detail?.total || 0 });
});
window.addEventListener('potato-atlas-working-selection-change', () => {
  if (state.id === 'metric' && metricSummary && !metricLoading) showMetricLegend(state.option, metricSummary);
});

ensureUi();
window.__potatoAtlasLenses = {
  setLens,
  getState() { return { ...state }; },
  refresh: applyLens,
};

await restoreState();
