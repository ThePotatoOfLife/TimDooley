// Browse-first country controller for the World Relational Atlas.
//
// Ordinary clicks inspect one active country at a time. Retained multi-country
// state is deliberate: pins feed Compare/Path and other multi-country tools.
// Automatic relationship context follows the active country instead of browse
// history, so users can simply click around the map without deselecting first.
// Legacy URL compatibility: older builds wrote searchParams.set('selected', …).
// This controller reads selected= during restore, but writes pins= going forward.

const map = window.__potatoAtlasMap;
const baseSelection = window.__potatoAtlasSelection;
const baseGoCountry = window.goCountry;
const baseClearCountry = window.clearCountrySelection;

if (!map || typeof baseGoCountry !== 'function' || !baseSelection) {
  throw new Error('Country selection controller requires the core atlas selection API.');
}

const WORLD_URL = '../data/world-relational-map.json';
const INDEX_URL = '../data/countries/index.json';
const ENTITY_URL = '../data/world-map-entities.json';
const REST_LOCAL = '../data/rest-countries-runtime.json';
const REST_REMOTE = 'https://restcountries.com/v3.1/all?fields=name,cca3,population,area,latlng,capital,region,subregion,borders';

const AUTO_EDGES_ACTIVE = 8;
const AUTO_EDGES_OTHER = 4; // retained for public/runtime compatibility
const AUTO_EDGES_TOTAL = 28;
const RELATION_MODES = new Set(['all', 'money', 'systems', 'institutions', 'project', 'other']);
const TYPE_PRIORITY = new Map([
  ['trade', 100], ['economic', 98], ['fiscal', 96], ['funding', 95], ['investment', 94],
  ['energy', 92], ['infrastructure', 90], ['security', 86], ['alliance', 84],
  ['constitutional', 82], ['ownership', 80], ['technology', 76], ['research', 74],
  ['culture', 64], ['geographic', 56]
]);

const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot',"'":'&#39;'
}[char]));

let pinnedCodes = [];
let activeCode = null;
let world = { curated_edges: [] };
let by3 = {};
let names = {};
let entityNames = {};
let syncingCore = false;
let ready = false;
let relationMode = RELATION_MODES.has(new URL(location.href).searchParams.get('relation'))
  ? new URL(location.href).searchParams.get('relation')
  : 'all';

function emptyFC() { return { type: 'FeatureCollection', features: [] }; }
function codeList(value) {
  return [...new Set(String(value || '').split(',').map(v => v.trim().toUpperCase()).filter(v => /^[A-Z]{3}$/.test(v)))];
}
function edgeKey(edge) {
  return [edge.a, edge.b].sort().join('|') + '|' + (edge.types || []).slice().sort().join(',') + '|' + (edge.layer || '');
}
function entityKnown(code) { return Boolean(names[code] || entityNames[code] || by3[code]); }
function countryName(code) { return names[code] || entityNames[code] || by3[code]?.name?.common || code; }
function allKnownCodes() {
  return [...new Set([...Object.keys(names), ...Object.keys(entityNames), ...Object.keys(by3), ...pinnedCodes, activeCode].filter(Boolean))];
}
function setFeatureState(code, key, value) {
  if (!code) return;
  try { map.setFeatureState({ source: 'countries', id: code }, { [key]: value }); }
  catch { /* source may still be settling during restored state */ }
}
function snapshot(reason = 'read') {
  return {
    source: 'working-selection', reason, code: activeCode, activeCode,
    name: activeCode ? countryName(activeCode) : null,
    selected: Boolean(activeCode),
    // Compatibility: older consumers use selectedCodes for retained multi-country state.
    selectedCodes: [...pinnedCodes],
    pinned: pinnedCodes.length > 0,
    pinnedCodes: [...pinnedCodes],
    isPinned: activeCode ? pinnedCodes.includes(activeCode) : false,
    relationMode, compareMode: false,
  };
}

function updateUrl() {
  const url = new URL(location.href);
  url.searchParams.delete('selected');
  if (pinnedCodes.length) url.searchParams.set('pins', pinnedCodes.join(',')); else url.searchParams.delete('pins');
  if (activeCode) url.searchParams.set('country', activeCode); else url.searchParams.delete('country');
  if (relationMode !== 'all') url.searchParams.set('relation', relationMode); else url.searchParams.delete('relation');
  if (!document.getElementById('compare')?.classList.contains('active')) url.searchParams.delete('compare');
  history.replaceState({}, '', url);
}

function applySelectionStates() {
  for (const code of allKnownCodes()) {
    setFeatureState(code, 'selected', pinnedCodes.includes(code));
    setFeatureState(code, 'active', code === activeCode);
  }
  if (map.getLayer('countries-line')) {
    map.setPaintProperty('countries-line', 'line-color', ['case', ['boolean', ['feature-state', 'active'], false], '#fff0ad', ['boolean', ['feature-state', 'selected'], false], '#e0bd78', ['boolean', ['feature-state', 'compare'], false], '#b9dcff', '#1c2626']);
    map.setPaintProperty('countries-line', 'line-width', ['case', ['boolean', ['feature-state', 'active'], false], 3.6, ['boolean', ['feature-state', 'selected'], false], 2.2, ['boolean', ['feature-state', 'compare'], false], 2.5, .7]);
  }
}

function installRelationPaint() {
  if (!map.getLayer('relations')) return;
  map.setPaintProperty('relations', 'line-color', ['case', ['==', ['get', 'mode'], 'auto'], '#78908f', ['step', ['get', 'depth'], '#73a7d8', 2, '#8ba5bd', 3, '#687f94']]);
  map.setPaintProperty('relations', 'line-width', ['case', ['==', ['get', 'mode'], 'auto'], 1.15, ['interpolate', ['linear'], ['zoom'], 2, 1.2, 6, 3]]);
  map.setPaintProperty('relations', 'line-opacity', ['case', ['==', ['get', 'mode'], 'auto'], .46, ['step', ['get', 'depth'], .82, 2, .62, 3, .44]]);
}

function relationBucket(edge) {
  const types = edge.types || [];
  if (types.some(type => ['trade','economic','fiscal','funding','investment','ownership'].includes(type))) return 'money';
  if (types.some(type => ['energy','infrastructure'].includes(type))) return 'systems';
  if (types.some(type => ['security','alliance','constitutional'].includes(type))) return 'institutions';
  if (String(edge.layer || '').includes('project')) return 'project';
  return 'other';
}
function edgeMatchesRelationMode(edge, mode = relationMode) { return mode === 'all' || relationBucket(edge) === mode; }
function displayScore(edge) {
  const typeScore = Math.max(0, ...(edge.types || []).map(type => TYPE_PRIORITY.get(type) || 50));
  const layer = String(edge.layer || '').toLowerCase();
  const evidenceBonus = layer.includes('empirical') || layer.includes('observ') ? 20 : layer.includes('mixed') ? 6 : 0;
  const quantifiedBonus = Number.isFinite(Number(edge.value)) ? 10 : 0;
  return typeScore + evidenceBonus + quantifiedBonus;
}
function rankedEdges(root, budget) {
  const candidates = (world.curated_edges || []).filter(edge => (edge.a === root || edge.b === root) && edgeMatchesRelationMode(edge)).map(edge => ({ edge, bucket: relationBucket(edge), score: displayScore(edge), key: edgeKey(edge) })).sort((a, b) => b.score - a.score || a.key.localeCompare(b.key));
  const chosen = [], used = new Set();
  const buckets = relationMode === 'all' ? ['money', 'systems', 'institutions', 'project', 'other'] : [relationMode];
  for (const bucket of buckets) {
    const hit = candidates.find(item => item.bucket === bucket && !used.has(item.key));
    if (hit && chosen.length < budget) { chosen.push(hit.edge); used.add(hit.key); }
  }
  for (const item of candidates) {
    if (chosen.length >= budget) break;
    if (used.has(item.key)) continue;
    chosen.push(item.edge); used.add(item.key);
  }
  return chosen;
}
function connectionsFor(code, budget = AUTO_EDGES_ACTIVE) { return rankedEdges(String(code || '').toUpperCase(), Math.max(1, Number(budget) || AUTO_EDGES_ACTIVE)); }

function automaticRelationData(codes = activeCode ? [activeCode] : []) {
  const roots = [...new Set((codes || []).filter(Boolean))];
  if (!roots.length) return emptyFC();
  const chosen = [], seen = new Set();
  for (const root of roots) {
    const budget = root === activeCode ? AUTO_EDGES_ACTIVE : AUTO_EDGES_OTHER;
    for (const edge of rankedEdges(root, budget)) {
      if (chosen.length >= AUTO_EDGES_TOTAL) break;
      const key = edgeKey(edge);
      if (seen.has(key)) continue;
      seen.add(key); chosen.push({ edge, root });
    }
    if (chosen.length >= AUTO_EDGES_TOTAL) break;
  }
  const features = [];
  for (const { edge, root } of chosen) {
    const a = by3[edge.a]?.latlng, b = by3[edge.b]?.latlng;
    if (!Array.isArray(a) || a.length !== 2 || !Array.isArray(b) || b.length !== 2) continue;
    features.push({ type:'Feature', properties:{a:edge.a,b:edge.b,root,mode:'auto',relationMode,depth:1,types:(edge.types||[]).join(' · '),layer:edge.layer||'',raw:JSON.stringify(edge)}, geometry:{type:'LineString',coordinates:[[a[1],a[0]],[b[1],b[0]]]}});
  }
  return { type:'FeatureCollection', features };
}
function explicitTraceVisible() { return document.getElementById('relations')?.classList.contains('active') === true; }
function applyAutomaticRelations() {
  if (!ready || explicitTraceVisible()) return;
  const source = map.getSource('relations');
  if (source?.setData) source.setData(automaticRelationData());
}
function setRelationMode(mode) {
  const next = RELATION_MODES.has(mode) ? mode : 'all';
  if (next === relationMode) return;
  relationMode = next; updateUrl(); applyAutomaticRelations();
  window.dispatchEvent(new CustomEvent('potato-atlas-relation-mode-change', { detail:{mode:relationMode,pinnedCodes:[...pinnedCodes],selectedCodes:[...pinnedCodes],activeCode} }));
}

function renderSelectionStrip() {
  const strip = document.getElementById('atlasWorkingSelection');
  if (!strip) return;
  strip.hidden = !pinnedCodes.length;
  const list = strip.querySelector('.selection-list');
  list.innerHTML = pinnedCodes.map(code => `<span class="selection-chip${code === activeCode ? ' active' : ''}" data-country-code="${esc(code)}"><button type="button" data-activate="${esc(code)}" title="Inspect ${esc(countryName(code))}">${esc(countryName(code))}</button><button type="button" class="selection-remove" data-remove="${esc(code)}" aria-label="Unpin ${esc(countryName(code))}">×</button></span>`).join('');
  strip.querySelector('.selection-count').textContent = `${pinnedCodes.length} pinned`;
}
function emit(reason) {
  const detail = snapshot(reason);
  window.dispatchEvent(new CustomEvent('potato-atlas-selection-change', { detail }));
  window.dispatchEvent(new CustomEvent('potato-atlas-working-selection-change', { detail }));
}
function emitPins(reason) {
  const detail = { ...snapshot(reason), pinnedCodes:[...pinnedCodes], selectedCodes:[...pinnedCodes] };
  window.dispatchEvent(new CustomEvent('potato-atlas-pin-change', { detail }));
}

async function activateCountry(code, { fly = false } = {}) {
  code = String(code || '').toUpperCase();
  if (!entityKnown(code)) return false;
  activeCode = code;
  syncingCore = true;
  try { await baseGoCountry(code); } finally { syncingCore = false; }
  applySelectionStates(); renderSelectionStrip(); updateUrl(); applyAutomaticRelations();
  if (fly && window.fitCountry) window.fitCountry();
  emit('activated');
  return true;
}
function pinCountry(code) {
  code = String(code || '').toUpperCase();
  if (!entityKnown(code) || pinnedCodes.includes(code)) return false;
  pinnedCodes.push(code);
  applySelectionStates(); renderSelectionStrip(); updateUrl(); emitPins('pinned');
  return true;
}
function unpinCountry(code) {
  code = String(code || '').toUpperCase();
  if (!pinnedCodes.includes(code)) return false;
  pinnedCodes = pinnedCodes.filter(value => value !== code);
  setFeatureState(code, 'selected', false);
  applySelectionStates(); renderSelectionStrip(); updateUrl(); emitPins('unpinned');
  return true;
}
function togglePinnedCountry(code) {
  code = String(code || '').toUpperCase();
  if (pinnedCodes.includes(code)) return unpinCountry(code);
  return pinCountry(code);
}
// Compatibility alias for older callers: "toggle selection" now means toggle retained pin.
function toggleCountrySelection(code) { return togglePinnedCountry(code); }
function clearPins() {
  for (const code of pinnedCodes) setFeatureState(code, 'selected', false);
  pinnedCodes = [];
  applySelectionStates(); renderSelectionStrip(); updateUrl(); emitPins('pins-cleared');
}
function clearActive() {
  if (!activeCode) return;
  setFeatureState(activeCode, 'active', false);
  activeCode = null; syncingCore = true;
  try {
    if (typeof baseClearCountry === 'function') baseClearCountry(); else baseSelection.clear?.();
  } finally { syncingCore = false; }
  applySelectionStates(); updateUrl(); map.getSource('relations')?.setData?.(emptyFC()); emit('cleared');
}
function clearAll({ keepView = true } = {}) {
  for (const code of pinnedCodes) setFeatureState(code, 'selected', false);
  if (activeCode) setFeatureState(activeCode, 'active', false);
  pinnedCodes = []; activeCode = null; syncingCore = true;
  try {
    if (typeof baseClearCountry === 'function') baseClearCountry(); else baseSelection.clear?.();
  } finally { syncingCore = false; }
  renderSelectionStrip(); updateUrl(); map.getSource('relations')?.setData?.(emptyFC());
  if (!keepView) document.getElementById('world')?.click();
  emitPins('pins-cleared'); emit('cleared');
}

function installStrip() {
  document.getElementById('atlasSelectionDock')?.style.setProperty('display', 'none', 'important');
  if (document.getElementById('atlasWorkingSelection')) return;
  const style = document.createElement('style');
  style.id = 'atlasWorkingSelectionStyle';
  style.textContent = `#atlasWorkingSelection{position:absolute;z-index:6;left:50%;bottom:10px;transform:translateX(-50%);display:flex;align-items:center;gap:7px;max-width:calc(100% - 28px);padding:6px 8px;border:1px solid #384745;border-radius:13px;background:#0b1212ed;box-shadow:0 8px 24px #0007}#atlasWorkingSelection[hidden]{display:none!important}.selection-list{display:flex;gap:5px;min-width:0;overflow-x:auto}.selection-chip{display:inline-flex;align-items:center;border:1px solid #31413e;border-radius:999px;background:#111b1a;flex:0 0 auto}.selection-chip.active{border-color:#e0bd78}.selection-chip button{border:0;background:transparent;padding:5px 7px}.selection-chip.active button:first-child{color:#f3dfa4}.selection-remove{color:#9fa9a4!important;padding-left:2px!important}.selection-count{font-size:10px;color:var(--muted);white-space:nowrap}.selection-clear-all{padding:5px 8px;border-radius:999px;white-space:nowrap}@media(max-width:900px){#atlasWorkingSelection{left:8px;right:8px;transform:none;max-width:none;justify-content:flex-start}.selection-count{display:none}.selection-list{flex:1}}`;
  document.head.appendChild(style);
  const strip = document.createElement('div');
  strip.id = 'atlasWorkingSelection'; strip.hidden = true;
  strip.innerHTML = '<span class="selection-count">0 pinned</span><div class="selection-list"></div><button type="button" class="selection-clear-all">Clear pins</button>';
  document.querySelector('.mapwrap')?.appendChild(strip);
  strip.addEventListener('click', event => {
    const remove = event.target.closest('[data-remove]'); if (remove) { unpinCountry(remove.dataset.remove); return; }
    const activate = event.target.closest('[data-activate]'); if (activate) { activateCountry(activate.dataset.activate); return; }
    if (event.target.closest('.selection-clear-all')) clearPins();
  });
}
function interceptPolygonClick(event) {
  if (document.getElementById('compare')?.classList.contains('active')) return;
  const code = event.features?.[0]?.properties?.iso3;
  if (!code || !entityKnown(code)) return;
  if (event.originalEvent) event.originalEvent.__potatoAtlasOverlayHandled = true;
  if (event.originalEvent?.shiftKey) {
    activateCountry(code).then(() => togglePinnedCountry(code));
    return;
  }
  activateCountry(code);
}
function installClickInterception() {
  for (const layer of ['countries-fill', 'countries-extrude']) if (map.getLayer(layer)) map.on('click', layer, interceptPolygonClick);
}
function adoptExternalSelection(event) {
  if (syncingCore) return;
  const detail = event?.detail || {};
  if (detail.source === 'working-selection' || detail.compareMode) return;
  if (detail.reason === 'cleared' || !detail.selected) { if (activeCode) clearActive(); return; }
  const code = String(detail.code || '').toUpperCase();
  if (!code || !entityKnown(code)) return;
  activeCode = code; applySelectionStates(); renderSelectionStrip(); updateUrl(); applyAutomaticRelations(); emit('external-selection');
}

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${response.status} ${url}`);
  return response.json();
}
async function loadRestRuntime() {
  try { return await fetchJson(REST_LOCAL); }
  catch (localError) {
    try { return await fetchJson(REST_REMOTE); }
    catch (remoteError) {
      console.warn('Country browsing has no coordinate runtime; automatic relation lines will be limited.', localError, remoteError);
      return [];
    }
  }
}
async function loadData() {
  const [worldResult, indexResult, entityResult, rest] = await Promise.all([
    fetchJson(WORLD_URL), fetchJson(INDEX_URL), fetchJson(ENTITY_URL).catch(() => ({entities:{}})), loadRestRuntime()
  ]);
  world = worldResult;
  names = Object.fromEntries((indexResult.countries || []).map(row => [row.iso3, row.name]));
  entityNames = Object.fromEntries(Object.entries(entityResult.entities || {}).filter(([, row]) => row?.render_status === 'current').map(([code, row]) => [code, row.name || code]));
  by3 = Object.fromEntries((rest || []).filter(row => row.cca3).map(row => [row.cca3, row]));
}

async function restoreState() {
  const url = new URL(location.href);
  const pins = codeList(url.searchParams.get('pins'));
  const legacySelected = codeList(url.searchParams.get('selected'));
  const legacyCompare = codeList(url.searchParams.get('compare'));
  const legacyCountry = String(url.searchParams.get('country') || baseSelection.current?.code || '').toUpperCase();
  pinnedCodes = (pins.length ? pins : legacySelected.length ? legacySelected : legacyCompare).filter(entityKnown);
  activeCode = entityKnown(legacyCountry) ? legacyCountry : pinnedCodes.at(-1) || null;
  if (legacyCompare.length && typeof window.leaveCompare === 'function') {
    syncingCore = true; try { window.leaveCompare(); } finally { syncingCore = false; }
  }
  if (activeCode && baseSelection.current?.code !== activeCode) {
    syncingCore = true; try { await baseGoCountry(activeCode); } finally { syncingCore = false; }
  }
  applySelectionStates(); renderSelectionStrip(); updateUrl(); applyAutomaticRelations();
  if (pinnedCodes.length) emitPins('restored');
  if (activeCode) emit('restored');
}

await loadData();
installStrip(); installClickInterception(); applySelectionStates(); installRelationPaint(); ready = true;

window.goCountry = async code => {
  if (document.getElementById('compare')?.classList.contains('active')) return baseGoCountry(code);
  return activateCountry(code);
};
window.__potatoAtlasSelection = {
  get current() { return snapshot('read'); },
  toggle:toggleCountrySelection, activate:activateCountry,
  pin:pinCountry, unpin:unpinCountry, togglePinnedCountry,
  isPinned(code) { return pinnedCodes.includes(String(code || '').toUpperCase()); },
  clear:clearActive, clearActive, clearPins, clearAll,
  focus() { if (activeCode) window.fitCountry?.(); }, inspect() { window.showOverview?.(); },
  automaticRelationData, connectionsFor, countryName, relationBucket, edgeMatchesRelationMode, setRelationMode, getRelationMode() { return relationMode; },
};
window.clearCountrySelection = clearActive;
window.clearAllSelectedCountries = clearPins;
window.addEventListener('potato-atlas-selection-change', adoptExternalSelection);
window.addEventListener('potato-atlas-relations-change', event => { if (!event?.detail?.visible) queueMicrotask(applyAutomaticRelations); });
window.addEventListener('potato-atlas-lens-change', applySelectionStates);
map.on('zoomend', applyAutomaticRelations);

await restoreState();
window.dispatchEvent(new CustomEvent('potato-atlas-working-selection-ready', { detail:{pinnedCodes:[...pinnedCodes],selectedCodes:[...pinnedCodes],activeCode,relationMode} }));