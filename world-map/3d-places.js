// Scale-aware Places runtime for the World Relational Atlas.
// Owns place data, rendering, selection, bounded country detail and place inspection.

if (!window.__potatoAtlasUrlState) await import('./3d-url-state.js');
const urlState = window.__potatoAtlasUrlState;
urlState.claim('selection-inspector', ['place']);

const map = window.__potatoAtlasMap;
const styleLifecycle = window.__potatoAtlasStyleLifecycle;
if (!map) throw new Error('Atlas Places require the core map.');
function interactionRouter() { return window.__potatoAtlasInteraction; }
function inspectorRouter() { return window.__potatoAtlasInspector; }
if (!window.__potatoAtlasMotion) await import('./3d-motion.js');
const motion = window.__potatoAtlasMotion;
if (!window.__potatoAtlasGeo) await import('./3d-geo-kernel.js');
const geo = window.__potatoAtlasGeo;
if (!geo?.pointInGeometry) throw new Error('Places requires the shared geospatial containment kernel.');

const DATA_ROOT = '../data/world-places/';
const INDEX_URL = `${DATA_ROOT}index.json`;
const MAJOR_SOURCE = 'atlas-places-major';
const DETAIL_SOURCE = 'atlas-places-detail';
const MAJOR_POINTS = 'atlas-places-major-points';
const MAJOR_LABELS = 'atlas-places-major-labels';
const DETAIL_POINTS = 'atlas-places-detail-points';
const DETAIL_LABELS = 'atlas-places-detail-labels';
const LEGACY_CAPITAL_LAYERS = Object.freeze(['capital-cities', 'capital-city-major-labels', 'capital-city-labels']);
const EMPTY_COLLECTION = Object.freeze({ type:'FeatureCollection', features:[] });
const DEFAULT_RUNTIME_BUDGET = Object.freeze({
  partition_max_bytes: 2_097_152,
  rendered_max_partitions: 2,
  cache_max_partitions: 6,
  cache_max_bytes: 8_388_608,
  global_major_max_bytes: 5_242_880,
  global_major_max_features: 5_000,
});

let indexPayload = null;
let majorData = EMPTY_COLLECTION;
let selectedId = new URL(location.href).searchParams.get('place') || null;
let visible = true;
let lastError = null;
let runtimeBudget = { ...DEFAULT_RUNTIME_BUDGET };
let usageClock = 0;
let cacheBytes = 0;
let cacheHits = 0;
let cacheMisses = 0;
let cacheEvictions = 0;
const fallbackLayerBindings = new Map();

const featureById = new Map();
const majorFeatureIds = new Set();
const majorFeatureById = new Map();
const partitionCache = new Map();
const inflightCountries = new Map();
const renderedPartitions = new Map();

function esc(value) {
  return String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
}
function number(value) {
  if (value == null || !Number.isFinite(Number(value))) return '—';
  return new Intl.NumberFormat('en', { maximumFractionDigits:0 }).format(Number(value));
}
function placeKind(properties = {}) {
  if (properties.is_national_capital || properties.capital_status === 'national') return 'Capital';
  const population = Number(properties.population);
  return Number.isFinite(population) && population > 0 && population < 50_000 ? 'Town' : 'City';
}
function collection(features = []) {
  return { type:'FeatureCollection', features };
}
function sourceData(sourceId, data) {
  const source = map.getSource(sourceId);
  if (source?.setData) source.setData(data);
}
function boundedBudget(source = {}) {
  const next = {};
  for (const [key, fallback] of Object.entries(DEFAULT_RUNTIME_BUDGET)) {
    const value = Number(source?.[key]);
    next[key] = Number.isFinite(value) && value > 0 ? Math.min(value, fallback) : fallback;
  }
  return next;
}
function indexFeatures(features = []) {
  for (const feature of features) {
    const id = feature?.properties?.id;
    if (id) featureById.set(String(id), feature);
  }
}
function indexMajorFeatures(features = []) {
  for (const feature of features) {
    const id = String(feature?.properties?.id || '');
    if (!id) continue;
    majorFeatureIds.add(id);
    majorFeatureById.set(id, feature);
    featureById.set(id, feature);
  }
}
function compactSearchRecords() {
  return Array.isArray(indexPayload?.search_records) ? indexPayload.search_records : [];
}
function compactRecord(id) {
  const key = String(id || '');
  return compactSearchRecords().find(row => String(row?.id || '') === key) || null;
}
function selectedPartitionCode() {
  if (!selectedId) return null;
  const feature = featureById.get(String(selectedId));
  const fromFeature = String(feature?.properties?.country_iso3 || '').toUpperCase();
  if (fromFeature) return fromFeature;
  const record = compactRecord(selectedId);
  return String(record?.partition || record?.country_iso3 || '').toUpperCase() || null;
}
function touchPartition(state) {
  if (!state) return 0;
  state.lastUsed = ++usageClock;
  return state.lastUsed;
}
function removePartitionFeatures(state) {
  for (const feature of state?.data?.features || []) {
    const id = String(feature?.properties?.id || '');
    if (!id) continue;
    if (majorFeatureIds.has(id)) {
      const majorFeature = majorFeatureById.get(id);
      if (majorFeature) featureById.set(id, majorFeature);
      continue;
    }
    if (featureById.get(id) === feature) featureById.delete(id);
  }
}
function renderedByteCount() {
  let total = 0;
  for (const code of renderedPartitions.keys()) total += Number(partitionCache.get(code)?.bytes || 0);
  return total;
}
function syncDetailSource() {
  const seen = new Set();
  const features = [];
  for (const code of renderedPartitions.keys()) {
    const state = partitionCache.get(code);
    for (const feature of state?.data?.features || []) {
      const id = String(feature?.properties?.id || '');
      if (!id || seen.has(id)) continue;
      seen.add(id);
      features.push(feature);
    }
  }
  sourceData(DETAIL_SOURCE, collection(features));
}
function trimRenderedPartitions(protectCode = null) {
  const selectedCode = selectedPartitionCode();
  const protectedCodes = new Set([protectCode, selectedCode].filter(Boolean));
  let changed = false;
  while (renderedPartitions.size > runtimeBudget.rendered_max_partitions) {
    const candidates = [...renderedPartitions.entries()]
      .filter(([code]) => !protectedCodes.has(code))
      .sort((a, b) => a[1] - b[1] || a[0].localeCompare(b[0]));
    const victim = candidates[0]?.[0];
    if (!victim) break;
    renderedPartitions.delete(victim);
    changed = true;
  }
  if (changed) syncDetailSource();
}
function activateRenderedPartition(code, protectCode = code) {
  const normalized = String(code || '').toUpperCase();
  const state = partitionCache.get(normalized);
  if (!state) return false;
  const stamp = touchPartition(state);
  renderedPartitions.delete(normalized);
  renderedPartitions.set(normalized, stamp);
  trimRenderedPartitions(protectCode);
  syncDetailSource();
  return true;
}
function evictCache(extraProtected = []) {
  const protectedCodes = new Set([
    selectedPartitionCode(),
    ...renderedPartitions.keys(),
    ...(extraProtected instanceof Set ? extraProtected : extraProtected || []),
  ].filter(Boolean));
  while (
    partitionCache.size > runtimeBudget.cache_max_partitions
    || cacheBytes > runtimeBudget.cache_max_bytes
  ) {
    const candidates = [...partitionCache.entries()]
      .filter(([code]) => !protectedCodes.has(code))
      .sort((a, b) => (a[1]?.lastUsed || 0) - (b[1]?.lastUsed || 0) || a[0].localeCompare(b[0]));
    const [code, state] = candidates[0] || [];
    if (!code || !state) break;
    partitionCache.delete(code);
    renderedPartitions.delete(code);
    cacheBytes = Math.max(0, cacheBytes - Number(state.bytes || 0));
    cacheEvictions += 1;
    removePartitionFeatures(state);
  }
}
function nationalCapitalForCountry(code) {
  const iso3 = String(code || '').toUpperCase();
  return (majorData.features || []).find(feature => {
    const p = feature?.properties || {};
    return String(p.country_iso3 || '').toUpperCase() === iso3
      && (p.is_national_capital === true || p.capital_status === 'national');
  }) || null;
}
function hideLegacyCapitalLayers() {
  for (const layerId of LEGACY_CAPITAL_LAYERS) {
    if (map.getLayer(layerId)) map.setLayoutProperty(layerId, 'visibility', 'none');
  }
}
function convergeLegacyCapitals() {
  if (!(majorData.features?.length > 0)) return false;
  hideLegacyCapitalLayers();
  window.__potatoAtlasCapitals = {
    setVisible(next) { return setVisible(next); },
    focus(code, options = {}) {
      const feature = nationalCapitalForCountry(code);
      if (!feature) return false;
      return focus(feature.properties?.id, { ...options, feature, fit:options.fit !== false });
    },
    forCountry(code) { return nationalCapitalForCountry(code); },
    get visible() { return visible; },
    get count() {
      return (majorData.features || []).filter(feature => {
        const p = feature?.properties || {};
        return p.is_national_capital === true || p.capital_status === 'national';
      }).length;
    },
  };
  window.dispatchEvent(new CustomEvent('potato-atlas-capitals-change', {
    detail:{ visible, owner:'places', count:window.__potatoAtlasCapitals.count }
  }));
  return true;
}
function syncUrl(id) {
  urlState.patch('selection-inspector', { set:{ place:id || null } });
}
function countryBaseline(code) {
  const id = String(code || '').toUpperCase();
  return {
    type:'country', id, owner:'country',
    restore:() => { if (id && window.goCountry) window.goCountry(id); },
  };
}
function placeParent(code) {
  const current = inspectorRouter()?.current?.();
  if (current?.type === 'subdivision') return { type:'subdivision', id:current.id };
  if (current?.type === 'place' && current.parent?.type === 'subdivision') return { ...current.parent };
  return { type:'country', id:String(code || '').toUpperCase() };
}
function renderInspector(feature) {
  const panel = document.getElementById('panel');
  if (!panel || !feature) return;
  const p = feature.properties || {};
  const [lon, lat] = feature.geometry?.coordinates || [];
  const populationPeriod = p.population_period || '—';
  const country = p.country_name || p.country_iso3 || '—';
  const admin = [p.admin1_name, p.admin1_code].filter(Boolean).join(' · ');
  panel.innerHTML = `
    <div class="eyebrow">Place</div>
    <h1>${esc(p.name || p.id || 'Place')}</h1>
    <p class="muted">${esc(placeKind(p))} · ${esc(country)}</p>
    <div class="stat-grid">
      <div><span>Population</span><b>${number(p.population)}</b><small>${esc(populationPeriod)}</small></div>
      <div><span>Coordinates</span><b>${Number.isFinite(Number(lat)) ? Number(lat).toFixed(3) : '—'}, ${Number.isFinite(Number(lon)) ? Number(lon).toFixed(3) : '—'}</b></div>
    </div>
    ${admin ? `<p><b>Administrative region</b><br>${esc(admin)}</p>` : ''}
    <p class="muted">Source: ${esc(p.source || 'GeoNames')}<br>Dataset refreshed: ${esc(p.dataset_refresh_date || '—')}</p>
    <div class="panel-actions">
      <button type="button" data-place-open-country>Open country</button>
      <button type="button" data-place-close>Close place</button>
    </div>`;
  panel.querySelector('[data-place-open-country]')?.addEventListener('click', () => {
    const code = String(p.country_iso3 || '').toUpperCase();
    if (!code) return;
    clear({ restore:false });
    const inspector = inspectorRouter();
    if (inspector?.reset) inspector.reset(countryBaseline(code));
    else if (window.goCountry) window.goCountry(code);
  });
  panel.querySelector('[data-place-close]')?.addEventListener('click', () => clear());
  window.__potatoAtlasPanelLifecycle?.publish?.();
}
function openInspector(feature) {
  if (!feature) return false;
  const p = feature.properties || {};
  const code = String(p.country_iso3 || '').toUpperCase();
  const inspector = inspectorRouter();
  if (!inspector?.open || !code) {
    renderInspector(feature);
    return true;
  }
  const parent = placeParent(code);
  inspector.setBaseline(countryBaseline(code));
  inspector.open({
    type:'place',
    id:String(p.id || selectedId || ''),
    owner:'places',
    parent,
    render:() => renderInspector(feature),
  });
  return true;
}
function registerLayer(layerId, priority) {
  window.__potatoAtlasRenderStack?.register?.(layerId, {
    slot:'context-network', priority, owner:'places'
  });
}
async function scaleRuntime() {
  const scale = await window.__potatoAtlasScale?.ready;
  if (!scale?.threshold || !scale?.bandThreshold) throw new Error('World Map Scale runtime unavailable to Places.');
  return scale;
}
async function installLayers() {
  const scale = await scaleRuntime();
  const PLACE_DETAIL_RENDER_ZOOM = scale.threshold('places-detail', 'render');
  const PLACE_DETAIL_LABEL_ZOOM = scale.threshold('places-detail', 'label');
  if (!map.getSource(MAJOR_SOURCE)) map.addSource(MAJOR_SOURCE, { type:'geojson', data:majorData });
  if (!map.getSource(DETAIL_SOURCE)) map.addSource(DETAIL_SOURCE, { type:'geojson', data:EMPTY_COLLECTION });

  if (!map.getLayer(MAJOR_POINTS)) {
    map.addLayer({
      id:MAJOR_POINTS, type:'circle', source:MAJOR_SOURCE,
      paint:{
        'circle-radius':['interpolate',['linear'],['zoom'],1,2.1,4,3.7,8,6.0],
        'circle-color':['case',['boolean',['get','is_national_capital'],false],'#e7c56f','#d7ded9'],
        'circle-stroke-color':'#111716', 'circle-stroke-width':1,
        'circle-opacity':0.92
      }
    });
  }
  if (!map.getLayer(MAJOR_LABELS)) {
    map.addLayer({
      id:MAJOR_LABELS, type:'symbol', source:MAJOR_SOURCE, minzoom:1.2,
      layout:{
        'text-field':['get','name'],
        'text-size':['interpolate',['linear'],['zoom'],1.2,8,5,10.5,8,12],
        'symbol-sort-key':['+',
          ['case',['boolean',['get','is_national_capital'],false],0,1000000000],
          ['-',1000000000,['coalesce',['to-number',['get','population']],0]]
        ],
        'text-variable-anchor':['top','bottom','left','right'],
        'text-radial-offset':1.05,
        'text-padding':['interpolate',['linear'],['zoom'],1.2,5,6,2],
        'text-optional':true,
        'text-allow-overlap':false
      },
      paint:{
        'text-color':['case',['boolean',['get','is_national_capital'],false],'#f0d98f','#d7ded9'],
        'text-halo-color':'#080b0b', 'text-halo-width':1.1,
        'text-opacity':0.9
      }
    });
  }
  if (!map.getLayer(DETAIL_POINTS)) {
    map.addLayer({
      id:DETAIL_POINTS, type:'circle', source:DETAIL_SOURCE, minzoom:PLACE_DETAIL_RENDER_ZOOM,
      paint:{
        'circle-radius':['interpolate',['linear'],['zoom'],PLACE_DETAIL_RENDER_ZOOM,2,8,4.4,11,6],
        'circle-color':'#cdd8d2','circle-stroke-color':'#111716','circle-stroke-width':0.9,'circle-opacity':0.88
      }
    });
  }
  if (!map.getLayer(DETAIL_LABELS)) {
    map.addLayer({
      id:DETAIL_LABELS, type:'symbol', source:DETAIL_SOURCE, minzoom:PLACE_DETAIL_LABEL_ZOOM,
      layout:{
        'text-field':['get','name'],
        'text-size':['interpolate',['linear'],['zoom'],PLACE_DETAIL_LABEL_ZOOM,8.5,9,11],
        'text-variable-anchor':['top','bottom','left','right'],
        'text-radial-offset':1.0,
        'text-padding':3,
        'text-optional':true,
        'text-allow-overlap':false
      },
      paint:{'text-color':'#d3ddd7','text-halo-color':'#080b0b','text-halo-width':1.0}
    });
  }
  registerLayer(MAJOR_POINTS, 30);
  registerLayer(MAJOR_LABELS, 31);
  registerLayer(DETAIL_POINTS, 32);
  registerLayer(DETAIL_LABELS, 33);
  setVisible(visible, {silent:true});
  bindLayerEvents();
}

function syncInteractionRegistration() {
  const interaction = interactionRouter();
  if (!interaction?.register) return false;
  unbindFallbackLayerEvents();
  interaction.register('places', {
    layers:[MAJOR_POINTS, DETAIL_POINTS],
    objectType:'place',
    clickPriority:80,
    hoverPriority:80,
    cursor:'pointer',
    enabled:() => visible,
    onClick:(event, feature) => {
      const id = feature?.properties?.id;
      if (id) focus(id, {feature, fit:false});
    },
  });
  return true;
}
function bindFallbackLayerEvents() {
  // Degraded/direct-module fallback when the shared Interaction Router is unavailable.
  for (const layerId of [MAJOR_POINTS, DETAIL_POINTS]) {
    if (fallbackLayerBindings.has(layerId)) continue;
    const onEnter = () => { map.getCanvas().style.cursor = 'pointer'; };
    const onLeave = () => { map.getCanvas().style.cursor = ''; };
    const onClick = event => {
      const feature = event.features?.[0];
      if (!feature) return;
      if (event.originalEvent) event.originalEvent.__potatoAtlasOverlayHandled = true;
      const id = feature.properties?.id;
      if (id) focus(id, {feature, fit:false});
    };
    map.on('mouseenter', layerId, onEnter);
    map.on('mouseleave', layerId, onLeave);
    map.on('click', layerId, onClick);
    fallbackLayerBindings.set(layerId, { onEnter, onLeave, onClick });
  }
}
function unbindFallbackLayerEvents() {
  for (const [layerId, handlers] of fallbackLayerBindings.entries()) {
    try { map.off('mouseenter', layerId, handlers.onEnter); } catch {}
    try { map.off('mouseleave', layerId, handlers.onLeave); } catch {}
    try { map.off('click', layerId, handlers.onClick); } catch {}
  }
  fallbackLayerBindings.clear();
}
let eventsBound = false;
function bindLayerEvents() {
  if (syncInteractionRegistration()) { eventsBound = true; return; }
  if (eventsBound) return;
  eventsBound = true;
  bindFallbackLayerEvents();
}

window.addEventListener('potato-atlas-interaction-ready', () => {
  if (eventsBound) syncInteractionRegistration();
});

async function loadIndex() {
  if (indexPayload) return indexPayload;
  const response = await fetch(INDEX_URL, {cache:'force-cache'});
  if (!response.ok) throw new Error(`Places index unavailable (${response.status})`);
  indexPayload = await response.json();
  runtimeBudget = boundedBudget(indexPayload?.runtime_budget);
  return indexPayload;
}
async function loadMajor() {
  const index = await loadIndex();
  const descriptor = index?.global_major || {};
  const path = descriptor.path || 'global-major.geo.json';
  if (Number(descriptor.bytes || 0) > runtimeBudget.global_major_max_bytes) {
    throw new Error('Global Places snapshot exceeds runtime byte budget.');
  }
  if (Number(descriptor.count || 0) > runtimeBudget.global_major_max_features) {
    throw new Error('Global Places snapshot exceeds runtime feature budget.');
  }
  const response = await fetch(`${DATA_ROOT}${path}`, {cache:'force-cache'});
  if (!response.ok) throw new Error(`Global Places snapshot unavailable (${response.status})`);
  const data = await response.json();
  if (data?.type !== 'FeatureCollection' || !Array.isArray(data.features)) throw new Error('Global Places snapshot is not GeoJSON.');
  if (data.features.length > runtimeBudget.global_major_max_features) throw new Error('Global Places snapshot exceeds runtime feature budget.');
  majorData = data;
  indexMajorFeatures(data.features);
  sourceData(MAJOR_SOURCE, data);
  convergeLegacyCapitals();
  return data;
}
async function loadCountry(iso3) {
  const code = String(iso3 || '').toUpperCase();
  if (!code) return null;

  const cached = partitionCache.get(code);
  if (cached) {
    cacheHits += 1;
    touchPartition(cached);
    activateRenderedPartition(code, code);
    return cached;
  }
  if (inflightCountries.has(code)) return inflightCountries.get(code);

  cacheMisses += 1;
  const promise = (async () => {
    const index = await loadIndex();
    const descriptor = index?.countries?.[code];
    if (!descriptor?.path) return { code, descriptor:null, data:EMPTY_COLLECTION, bytes:0, lastUsed:++usageClock };
    const declaredBytes = Number(descriptor.bytes || 0);
    if (declaredBytes > runtimeBudget.partition_max_bytes) {
      throw new Error(`Places partition ${code} exceeds runtime byte budget.`);
    }
    const response = await fetch(`${DATA_ROOT}${descriptor.path}`, {cache:'force-cache'});
    if (!response.ok) throw new Error(`Places partition ${code} unavailable (${response.status})`);
    const data = await response.json();
    if (data?.type !== 'FeatureCollection' || !Array.isArray(data.features)) throw new Error(`Places partition ${code} is not GeoJSON.`);
    const bytes = declaredBytes || JSON.stringify(data).length;
    if (bytes > runtimeBudget.partition_max_bytes) {
      throw new Error(`Places partition ${code} exceeds runtime byte budget.`);
    }
    const state = { code, descriptor, data, bytes, lastUsed:++usageClock };
    partitionCache.set(code, state);
    cacheBytes += bytes;
    indexFeatures(data.features);
    activateRenderedPartition(code, code);
    evictCache(new Set([code]));
    return state;
  })();

  inflightCountries.set(code, promise);
  try {
    return await promise;
  } finally {
    inflightCountries.delete(code);
  }
}
function findFeature(id) {
  return featureById.get(String(id || '')) || null;
}
async function focus(id, options = {}) {
  let feature = options.feature || findFeature(id);
  const record = compactRecord(id);
  const country = String(
    options.country
    || feature?.properties?.country_iso3
    || record?.partition
    || record?.country_iso3
    || ''
  ).toUpperCase();
  if (!feature && country) {
    await loadCountry(country);
    feature = findFeature(id);
  }
  if (!feature) return false;
  const p = feature.properties || {};
  const coords = feature.geometry?.coordinates;
  selectedId = String(p.id || id);
  const selectedCode = String(p.country_iso3 || country || '').toUpperCase();
  if (selectedCode && partitionCache.has(selectedCode)) {
    activateRenderedPartition(selectedCode, selectedCode);
    evictCache(new Set([selectedCode]));
  }
  syncUrl(selectedId);
  openInspector(feature);
  if (options.fit !== false && Array.isArray(coords) && coords.length >= 2) {
    motion.easeTo(map, {
      center:[Number(coords[0]), Number(coords[1])],
      zoom:Math.max(Number(options.zoom) || 6.2, map.getZoom()),
      pitch:Math.min(map.getPitch(), 45), duration:650
    });
  }
  window.dispatchEvent(new CustomEvent('potato-atlas-place-select', {detail:{id:selectedId, properties:p, feature}}));
  return true;
}
function clear(options = {}) {
  const previous = current();
  const code = String(previous?.properties?.country_iso3 || new URL(location.href).searchParams.get('country') || '').toUpperCase();
  selectedId = null;
  syncUrl(null);
  if (options.restore !== false) {
    const inspector = inspectorRouter();
    if (inspector?.current?.()?.type === 'place') inspector.back();
    else if (code && window.goCountry) window.goCountry(code);
  }
  evictCache();
  window.dispatchEvent(new CustomEvent('potato-atlas-place-clear'));
  return true;
}
function setVisible(next, options = {}) {
  visible = Boolean(next);
  const visibility = visible ? 'visible' : 'none';
  for (const id of [MAJOR_POINTS, MAJOR_LABELS, DETAIL_POINTS, DETAIL_LABELS]) {
    if (map.getLayer(id)) map.setLayoutProperty(id, 'visibility', visibility);
  }
  if (majorData.features?.length) hideLegacyCapitalLayers();
  if (!options.silent) {
    window.dispatchEvent(new CustomEvent('potato-atlas-places-change', {detail:{visible}}));
    if (majorData.features?.length) {
      window.dispatchEvent(new CustomEvent('potato-atlas-capitals-change', {detail:{visible, owner:'places'}}));
    }
  }
  return visible;
}
function current() {
  return selectedId ? findFeature(selectedId) : null;
}
function search(query, options = {}) {
  const needle = String(query || '').trim().toLowerCase();
  if (!needle) return [];
  const limit = Math.max(1, Math.min(50, Number(options.limit) || 12));
  const normalized = value => String(value || '').toLowerCase();
  const records = compactSearchRecords();
  return records
    .map(record => {
      const names = [record?.name, ...(Array.isArray(record?.aliases) ? record.aliases : [])].map(normalized);
      const best = Math.min(...names.map(name => name === needle ? 0 : name.startsWith(needle) ? 1 : name.includes(needle) ? 2 : 9));
      return {record, best};
    })
    .filter(row => row.best < 9)
    .sort((a, b) => a.best - b.best
      || Number(a.record?.population_rank || Number.MAX_SAFE_INTEGER) - Number(b.record?.population_rank || Number.MAX_SAFE_INTEGER)
      || String(a.record?.name || '').localeCompare(String(b.record?.name || ''))
      || String(a.record?.id || '').localeCompare(String(b.record?.id || '')))
    .slice(0, limit)
    .map(({record}) => {
      const feature = findFeature(record.id);
      return {
        id:record.id,
        name:record.name,
        country:String(record.country_iso3 || record.partition || '').toUpperCase(),
        type:['Capital','City','Town'].includes(record.type) ? record.type : (feature ? placeKind(feature.properties || {}) : 'City'),
        population_rank:record.population_rank,
        partition:record.partition,
        feature:feature || undefined,
      };
    });
}
async function inSubdivision(subdivisionFeature, options = {}) {
  const geometry = subdivisionFeature?.geometry;
  const properties = subdivisionFeature?.properties || {};
  const code = String(properties.parent_iso3 || properties.country_iso3 || '').toUpperCase();
  if (!geometry || !code) return { available:false, code, places:[], reason:'missing-subdivision-context' };
  let state;
  try {
    state = await loadCountry(code);
  } catch (error) {
    return { available:false, code, places:[], reason:error?.message || 'country-place-partition-unavailable' };
  }
  if (!state?.descriptor?.path || !Array.isArray(state?.data?.features)) {
    return { available:false, code, places:[], reason:'country-place-partition-not-built' };
  }
  const limit = Math.max(1, Math.min(50, Number(options.limit) || 12));
  const places = state.data.features
    .filter(feature => {
      const coords = feature?.geometry?.coordinates;
      return Array.isArray(coords) && coords.length >= 2 && geo.pointInGeometry(coords, geometry);
    })
    .sort((a,b) => {
      const pa = Number(a?.properties?.population);
      const pb = Number(b?.properties?.population);
      const va = Number.isFinite(pa) ? pa : -1;
      const vb = Number.isFinite(pb) ? pb : -1;
      return vb - va
        || String(a?.properties?.name || '').localeCompare(String(b?.properties?.name || ''));
    })
    .slice(0, limit);
  return {
    available:true,
    code,
    total:state.data.features.filter(feature => {
      const coords = feature?.geometry?.coordinates;
      return Array.isArray(coords) && coords.length >= 2 && geo.pointInGeometry(coords, geometry);
    }).length,
    places,
    source:indexPayload?.source || 'GeoNames',
    datasetRefreshDate:indexPayload?.dataset_refresh_date || null,
  };
}

function status() {
  const renderedCodes = [...renderedPartitions.keys()];
  const cachedCodes = [...partitionCache.keys()];
  return {
    visible,
    selected:selectedId,
    majorCount:majorData.features?.length || 0,
    loadedCountries:cachedCodes,
    renderedPartitions:renderedCodes,
    renderedBytes:renderedByteCount(),
    cachedPartitions:cachedCodes,
    cachedBytes:cacheBytes,
    cacheHits,
    cacheMisses,
    cacheEvictions,
    runtimeBudget:{...runtimeBudget},
    indexReady:Boolean(indexPayload),
    error:lastError ? String(lastError.message || lastError) : null,
  };
}

window.addEventListener('potato-atlas-capitals-ready', () => convergeLegacyCapitals());


async function restoreAfterStyleGeneration() {
  try {
    await installLayers();
    if (majorData?.features?.length) sourceData(MAJOR_SOURCE, majorData);
    const rendered = [...renderedPartitions.keys()];
    if (rendered.length) {
      const merged = {
        type:'FeatureCollection',
        features:rendered.flatMap(code => partitionCache.get(code)?.data?.features || []),
      };
      sourceData(DETAIL_SOURCE, merged);
    }
    setVisible(visible, {silent:true});
    syncInteractionRegistration();
  } catch (error) {
    console.warn('Places style-generation restore unavailable:', error);
  }
}

async function initialize() {
  if (map.loaded()) await installLayers();
  else await new Promise(resolve => map.once('load', async () => { await installLayers(); resolve(); }));
  try {
    await loadMajor();
    const url = new URL(location.href);
    const requested = url.searchParams.get('place');
    const country = url.searchParams.get('country');
    if (requested && !findFeature(requested) && country) await loadCountry(country);
    if (requested) await focus(requested, {country, fit:true});
  } catch (error) {
    lastError = error;
    console.warn('Places data unavailable; country map remains usable.', error);
  }
  const state = status();
  window.dispatchEvent(new CustomEvent('potato-atlas-places-ready', {detail:state}));
  return state;
}

styleLifecycle?.register?.('places', { priority:50, restore:() => { queueMicrotask(restoreAfterStyleGeneration); } });

const ready = initialize();
window.__potatoAtlasPlaces = {
  ready,
  setVisible,
  focus,
  current,
  search,
  inSubdivision,
  clear,
  status,
  loadCountry,
  get visible() { return visible; },
};
