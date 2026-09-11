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
  christian: '#d7b66f',
  muslim: '#79aa80',
  hindu: '#d49369',
  buddhist: '#c7a86d',
  jewish: '#75a6d6',
  other_religions: '#a687bd',
  unaffiliated: '#899398',
};
const ALIGNMENT_COLORS = {
  north: '#58b6c7',
  west: '#d0a352',
  east: '#c96f58',
  south: '#6fa77a',
  overlap: '#a57bc3',
  unclassified: UNKNOWN,
};

let world;
let demography;
let state = { id: 'neutral', option: '' };
let applying = false;
let pendingApply = false;

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
  // South currently has no settled ISO-coded membership. Keep it visible in the
  // legend without guessing country assignments from broad region prose.
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
  return [
    'case',
    ['boolean', ['feature-state', 'lensHas'], false],
    ['interpolate', ['linear'], ['feature-state', 'lensValue'], 0, '#1e2928', 20, '#3c5551', 50, base, 80, '#e3d8a2', 100, '#fff0bf'],
    UNKNOWN
  ];
}

function metricExpression(option) {
  if (option === 'area') {
    return ['case', ['>', ['get', 'area'], 0], ['step', ['get', 'area'], '#263432', 10000, '#36514b', 100000, '#527466', 500000, '#78977d', 1000000, '#a7b87f', 5000000, '#d0c77e'], UNKNOWN];
  }
  return ['case', ['>', ['get', 'population'], 0], ['step', ['get', 'population'], '#263432', 1000000, '#36514b', 10000000, '#527466', 50000000, '#78977d', 100000000, '#a7b87f', 500000000, '#d0c77e'], UNKNOWN];
}

function legendRows(items) {
  return items.map(([label, color]) => `<span class="atlas-lens-key"><i style="background:${esc(color)}"></i>${esc(label)}</span>`).join('');
}
function showLegend(title, note, rows = '') {
  const legend = document.getElementById('atlasLensLegend');
  if (!legend) return;
  legend.hidden = state.id === 'neutral';
  legend.innerHTML = `<b>${esc(title)}</b>${rows ? `<div class="atlas-lens-keys">${rows}</div>` : ''}<small>${esc(note)}</small>`;
}
function sameLens(a, b) {
  return a?.id === b?.id && a?.option === b?.option;
}

async function applyLens() {
  if (applying) { pendingApply = true; return; }
  applying = true;
  const requested = { ...state };
  try {
    if (requested.id !== 'religion') clearReligionState();
    if (requested.id === 'neutral') {
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
      const rows = option === 'dominant' ? legendRows(Object.entries(RELIGION_COLORS).map(([key, color]) => [RELIGION_LABELS[key] || key, color])) : legendRows([['Low share', '#1e2928'], ['Higher share', RELIGION_COLORS[option] || '#82a8a3'], ['Very high share', '#fff0bf']]);
      showLegend(`Religion · ${RELIGION_LABELS[option] || option}`, 'Descriptive religious-identity composition; it does not imply political loyalty, conduct or belief intensity.', rows);
      return;
    }
    if (requested.id === 'metric') {
      if (!sameLens(state, requested)) return;
      const option = requested.option || 'population';
      setFill(metricExpression(option));
      showLegend(`Metric · ${option === 'area' ? 'Area' : 'Population'}`, `Country fill encodes ${option === 'area' ? 'area (km²)' : 'population'} from the current geographic runtime. Missing values are neutral.`, legendRows([
        ['Lower', '#263432'], ['Mid', '#527466'], ['Higher', '#a7b87f'], ['Highest tier', '#d0c77e']
      ]));
    }
  } catch (error) {
    console.warn('Atlas Lens unavailable:', error);
    if (sameLens(state, requested)) {
      state = { id: 'neutral', option: '' };
      syncControls();
      persist();
      setFill(NEUTRAL);
      showLegend('Lens unavailable', 'The requested optional Lens data could not be loaded; neutral geography remains usable.');
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
  if (id === 'metric') return [['population','Population'],['area','Area']];
  return [];
}
function defaultOption(id) {
  return id === 'alliances' ? 'nato' : id === 'religion' ? 'dominant' : id === 'metric' ? 'population' : '';
}
function syncControls() {
  const family = document.getElementById('atlasLensFamily');
  const option = document.getElementById('atlasLensOption');
  if (!family || !option) return;
  family.value = state.id;
  const choices = optionConfig(state.id);
  option.innerHTML = choices.map(([value, label]) => `<option value="${esc(value)}">${esc(label)}</option>`).join('');
  option.hidden = !choices.length;
  if (choices.length) option.value = choices.some(([value]) => value === state.option) ? state.option : defaultOption(state.id);
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

  const legend = document.createElement('div');
  legend.id = 'atlasLensLegend';
  legend.hidden = true;
  document.querySelector('.mapwrap')?.appendChild(legend);

  const style = document.createElement('style');
  style.id = 'atlasLensStyle';
  style.textContent = `
    #atlasLensControl{margin:7px 0;padding:7px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}#atlasLensControl select{display:block;width:100%;margin:4px 0}.atlas-lens-hint{font-size:9px;line-height:1.35;margin-top:4px}#atlasLensLegend{position:absolute;z-index:4;left:10px;bottom:46px;max-width:340px;padding:7px 9px;border:1px solid #344442;border-radius:9px;background:#0b1212e8;box-shadow:0 5px 18px #0006;font-size:10px}#atlasLensLegend[hidden]{display:none!important}#atlasLensLegend>b{display:block;margin-bottom:4px;color:#edf2e9}.atlas-lens-keys{display:flex;flex-wrap:wrap;gap:4px 8px;margin:4px 0}.atlas-lens-key{display:inline-flex;align-items:center;gap:4px;color:#cbd4cd}.atlas-lens-key i{width:9px;height:9px;border-radius:2px;border:1px solid #ffffff35}#atlasLensLegend small{display:block;color:var(--muted);line-height:1.35}@media(max-width:900px){#atlasLensLegend{left:8px;bottom:64px;max-width:calc(100% - 16px)}}
  `;
  document.head.appendChild(style);
}

function restoreState() {
  const url = new URL(location.href);
  const id = url.searchParams.get('lens') || 'neutral';
  const option = url.searchParams.get('lensOption') || defaultOption(id);
  return setLens(id, option);
}

ensureUi();
window.__potatoAtlasLenses = {
  setLens,
  getState() { return { ...state }; },
  refresh: applyLens,
};

await restoreState();
