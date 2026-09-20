// Generic lazy subdivision renderer for the World Map.
// Uses same-origin country partitions, one bounded shared rendering surface,
// and the canonical right inspector (#panel).

if (!window.__potatoAtlasUrlState) await import('./3d-url-state.js');
const urlState = window.__potatoAtlasUrlState;
urlState.claim('selection-inspector', ['subdivision']);

const map = window.__potatoAtlasMap;
if (!map) throw new Error('Atlas subdivisions require the core map.');
if (!window.__potatoAtlasMotion) await import('./3d-motion.js');
const motion = window.__potatoAtlasMotion;
if (!window.__potatoAtlasGeo) await import('./3d-geo-kernel.js');
const geo = window.__potatoAtlasGeo;
if (!geo) throw new Error('Atlas subdivisions require the shared geospatial kernel.');
function interactionRouter() { return window.__potatoAtlasInteraction; }
const inspector = window.__potatoAtlasInspector;

const INDEX_URL = '../data/world-subdivisions/index.json';
const USA_PARTITION_FALLBACK = 'USA.geo.json';
const SOURCE_ID = 'atlas-subdivisions-active';
const LINE_ID = 'atlas-subdivision-line';
const HIT_ID = 'atlas-subdivision-hit';
const LABEL_ID = 'atlas-subdivision-label';
const SELECTED_LABEL_ID = 'atlas-subdivision-selected-label';
const NARROW_SCREEN_MAX = 720;
const NARROW_LABEL_DELAY = 0.85;
const USA_BOUNDS_FALLBACK = { west:-179.5, east:-65, south:17, north:72.5 };
const DEFAULT_RUNTIME_BUDGET = Object.freeze({
  partition_max_bytes:1500000,
  rendered_max_bytes:3000000,
  rendered_max_partitions:4,
  cache_max_bytes:6000000,
  cache_max_partitions:8,
});

const cache = new Map();
let indexPromise = null;
let selectedId = new URL(location.href).searchParams.get('subdivision') || null;
// Camera intent from a deep link is one-shot. Persistent selection must not be
// replayed on every moveend or fitBounds can recurse forever.
let pendingDeepLinkId = selectedId;
let eventsBound = false;
let fallbackSharedHandlers = null;
let useClock = 0;
let activePartitions = [];
const forcedPartitions = new Set();
const forcedPartitionOwners = new Map();
const evidenceProviders = new Map();
const sourceRefreshObservers = new Map();
let sharedScale = null;

function retentionOwner(owner = 'anonymous') {
  const token = String(owner || '').trim();
  return token || 'anonymous';
}
function retainForcedPartition(partition, owner = 'anonymous') {
  const key = String(partition || '').toUpperCase();
  if (!key) return false;
  const token = retentionOwner(owner);
  const owners = forcedPartitionOwners.get(key) || new Set();
  owners.add(token);
  forcedPartitionOwners.set(key, owners);
  forcedPartitions.add(key);
  return true;
}
function releaseForcedPartition(partition, owner = 'anonymous') {
  const key = String(partition || '').toUpperCase();
  const owners = forcedPartitionOwners.get(key);
  if (!owners) return false;
  const removed = owners.delete(retentionOwner(owner));
  if (!owners.size) {
    forcedPartitionOwners.delete(key);
    forcedPartitions.delete(key);
  }
  return removed;
}
function retentionOwners() {
  return Object.fromEntries(
    [...forcedPartitionOwners.entries()]
      .sort(([a],[b]) => a.localeCompare(b))
      .map(([partition, owners]) => [partition, [...owners].sort()])
  );
}

let activeBytes = 0;
let labelZoomBase = null;
let nameZoomBase = null;
let runtimeBudget = { ...DEFAULT_RUNTIME_BUDGET };
let cacheHits = 0;
let cacheMisses = 0;
let cacheEvictions = 0;

function fmt(value) {
  if (value == null || !Number.isFinite(Number(value))) return '—';
  return new Intl.NumberFormat('en', { maximumFractionDigits:1 }).format(Number(value));
}
function esc(value) {
  return String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
}
function countryCode(properties = {}) {
  return String(properties.country_iso3 || properties.parent_iso3 || properties.iso3 || 'USA').toUpperCase();
}
function countryBaseline(code) {
  const id = String(code || '').toUpperCase();
  return {
    type:'country', id, owner:'country',
    restore:() => { if (id && window.goCountry) window.goCountry(id); },
  };
}
function activeEvidenceRows(id) {
  const rows = [];
  for (const [providerId, provider] of evidenceProviders.entries()) {
    let row = null;
    try { row = provider?.summary?.(id) || null; } catch (error) { console.warn(`Subdivision evidence provider failed: ${providerId}`, error); }
    if (!row || row.active === false) continue;
    rows.push({ providerId, provider, row });
  }
  return rows;
}
function subdivisionEvidenceHtml(id) {
  return activeEvidenceRows(id).map(({providerId,row}) => `
    <div class="card subdivision-evidence-card">
      <div class="eyebrow">${esc(row.eyebrow || 'Active evidence')}</div>
      <p>${row.primary != null ? `<b>${fmt(row.primary)}</b>` : ''} ${esc(row.summary || '')}</p>
      ${row.boundary ? `<p class="muted">${esc(row.boundary)}</p>` : ''}
      <button type="button" data-subdivision-evidence-provider="${esc(providerId)}">${esc(row.actionLabel || 'Open evidence')}</button>
    </div>`).join('');
}
function subdivisionContextActions(properties = {}) {
  const code = countryCode(properties);
  if (code !== 'USA') return '';
  return `
    <div class="card subdivision-context-actions">
      <div class="eyebrow">Optional state context</div>
      <p class="muted">Load source-attributed evidence or project case context for this state. These counts do not characterize residents.</p>
      <div class="actions">
        <button type="button" data-subdivision-context="adl-heat">Show ADL evidence</button>
        <button type="button" data-subdivision-context="mud-below-us">Show Mud / Below project cases</button>
      </div>
    </div>`;
}
async function activateSubdivisionContext(kind, feature) {
  const id = String(feature?.properties?.id || '');
  if (!id) return false;
  if (kind === 'adl-heat') {
    await window.__potatoAtlasLoadModule?.('ADL H.E.A.T.', './3d-adl-heat.js');
    await window.__potatoAtlasAdlHeat?.setEnabled?.(true);
  } else if (kind === 'mud-below-us') {
    await window.__potatoAtlasLoadModule?.('Mud / Below U.S.', './3d-mud-below-us.js');
    await window.__potatoAtlasMudBelow?.setEnabled?.(true);
  } else return false;
  renderInspector(feature);
  return true;
}

function populationDensity(properties = {}) {
  const population = Number(properties?.population?.value);
  const area = Number(properties?.area_km2);
  if (!Number.isFinite(population) || population <= 0 || !Number.isFinite(area) || area <= 0) return null;
  return population / area;
}
function placePopulationLabel(feature) {
  const value = Number(feature?.properties?.population);
  return Number.isFinite(value) && value > 0 ? fmt(value) : 'population unknown';
}
async function hydrateSubdivisionPlaces(feature) {
  const host = document.querySelector('[data-subdivision-places]');
  if (!host || !feature) return false;
  const id = String(feature?.properties?.id || '');
  const api = window.__potatoAtlasPlaces;
  if (!api?.inSubdivision) {
    host.innerHTML = '<p class="muted">City detail is not loaded yet.</p>';
    return false;
  }
  const result = await api.inSubdivision(feature, {limit:12});
  if (selectedId !== id || !host.isConnected) return false;
  if (!result?.available) {
    host.innerHTML = '<p class="muted">City detail is not available for this country snapshot yet.</p>';
    return false;
  }
  const rows = result.places || [];
  host.innerHTML = rows.length ? `
    <p class="muted"><b>${fmt(result.total)} mapped places</b> fall inside this subdivision · showing ${fmt(rows.length)} by population · source: ${esc(result.source || 'Places')}${result.datasetRefreshDate ? ` · refreshed ${esc(result.datasetRefreshDate)}` : ''}</p>
    <div class="card">${rows.map(place => {
      const p = place.properties || {};
      return `<button type="button" class="relation-button" data-subdivision-place="${esc(p.id || '')}">
        <span><b>${esc(p.name || p.id || 'Place')}</b><small>${esc(placePopulationLabel(place))}</small></span>
        <span>Open</span>
      </button>`;
    }).join('')}</div>`
    : '<p class="muted">No mapped places in the current place snapshot fall inside this subdivision.</p>';
  host.querySelectorAll?.('[data-subdivision-place]')?.forEach(button => {
    button.addEventListener('click', async () => {
      const placeId = button.dataset.subdivisionPlace;
      if (!placeId) return;
      await window.__potatoAtlasPlaces?.focus?.(placeId, { country:result.code, fit:true });
    });
  });
  return true;
}
function renderInspector(feature) {
  const panel = document.getElementById('panel');
  if (!panel || !feature) return;
  const p = feature.properties || {};
  const population = p.population || {};
  const density = populationDensity(p);
  const code = countryCode(p);
  panel.innerHTML = `
    <div class="eyebrow">Subdivision</div>
    <h1>${esc(p.name || p.id || 'Subdivision')}</h1>
    <p class="muted">${esc(p.subdivision_type || 'Subdivision')} · ${esc(p.code || p.id || '')} · ${esc(p.country_name || p.parent_name || code)}</p>
    <div class="stat-grid">
      <div><span>Population</span><b>${fmt(population.value)}</b><small>${esc(population.period || '—')}</small></div>
      <div><span>Area</span><b>${fmt(p.area_km2)} km²</b><small>land + water</small></div>
      <div><span>Density</span><b>${density == null ? '—' : `${fmt(density)} / km²`}</b><small>population ÷ area</small></div>
      <div><span>Region type</span><b>${esc(p.subdivision_type || 'Subdivision')}</b><small>${esc(p.code || p.id || '')}</small></div>
    </div>
    ${population.source ? `<p class="muted">Population source: ${esc(population.source)}</p>` : ''}
    ${p.geometry_source ? `<p class="muted">Boundary source: ${esc(p.geometry_source)}</p>` : ''}
    <h2>Cities and places</h2>
    <div data-subdivision-places><p class="muted">Loading mapped places inside this region…</p></div>
    <h2>Evidence & project context</h2>
    ${subdivisionEvidenceHtml(p.id) || subdivisionContextActions(p)}
    <div class="panel-actions">
      <button type="button" data-subdivision-open-country>Open country</button>
      <button type="button" data-subdivision-close>Close subdivision</button>
    </div>`;
  panel.querySelectorAll?.('[data-subdivision-evidence-provider]')?.forEach(button => {
    button.addEventListener('click', () => {
      const provider = evidenceProviders.get(button.dataset.subdivisionEvidenceProvider);
      provider?.open?.(p.id);
    });
  });
  panel.querySelectorAll?.('[data-subdivision-context]')?.forEach(button => {
    button.addEventListener('click', async () => {
      button.disabled = true;
      try { await activateSubdivisionContext(button.dataset.subdivisionContext, feature); }
      catch (error) { console.warn('Subdivision context layer unavailable:', error); }
      finally { button.disabled = false; }
    });
  });
  panel.querySelector('[data-subdivision-open-country]')?.addEventListener('click', () => {
    window.__potatoAtlasSubdivisions?.clear?.({ restore:false });
    if (inspector?.reset) inspector.reset(countryBaseline(code));
    else if (code && window.goCountry) window.goCountry(code);
  });
  panel.querySelector('[data-subdivision-close]')?.addEventListener('click', () => window.__potatoAtlasSubdivisions?.clear?.());
  window.__potatoAtlasPanelLifecycle?.publish?.();
  hydrateSubdivisionPlaces(feature).catch(error => {
    const host = document.querySelector('[data-subdivision-places]');
    if (host && selectedId === String(p.id || '')) host.innerHTML = '<p class="muted">City detail could not be loaded for this subdivision.</p>';
    console.warn('Subdivision places unavailable:', error);
  });
}
function openInspector(feature) {
  if (!feature) return false;
  const p = feature.properties || {};
  const code = countryCode(p);
  if (!inspector?.open || !code) {
    renderInspector(feature);
    return true;
  }
  inspector.setBaseline(countryBaseline(code));
  inspector.open({
    type:'subdivision',
    id:String(p.id || selectedId || ''),
    owner:'subdivisions',
    parent:{ type:'country', id:code },
    render:() => renderInspector(feature),
  });
  return true;
}
function normalizeBudget(index) {
  const supplied = index?.runtime_budget || {};
  runtimeBudget = {
    partition_max_bytes:Number(supplied.partition_max_bytes) || DEFAULT_RUNTIME_BUDGET.partition_max_bytes,
    rendered_max_bytes:Number(supplied.rendered_max_bytes) || DEFAULT_RUNTIME_BUDGET.rendered_max_bytes,
    rendered_max_partitions:Number(supplied.rendered_max_partitions) || DEFAULT_RUNTIME_BUDGET.rendered_max_partitions,
    cache_max_bytes:Number(supplied.cache_max_bytes) || DEFAULT_RUNTIME_BUDGET.cache_max_bytes,
    cache_max_partitions:Number(supplied.cache_max_partitions) || DEFAULT_RUNTIME_BUDGET.cache_max_partitions,
  };
  return runtimeBudget;
}
async function subdivisionIndex() {
  if (!indexPromise) {
    indexPromise = fetch(INDEX_URL).then(response => {
      if (!response.ok) throw new Error(`Subdivision index unavailable (${response.status})`);
      return response.json();
    }).then(index => {
      normalizeBudget(index);
      return index;
    });
  }
  return indexPromise;
}
function partitionEntries(index) {
  return Object.entries(index?.partitions || {});
}
function descriptorBounds(partition, descriptor = {}) {
  if (descriptor.viewport_bounds) return descriptor.viewport_bounds;
  return partition === 'USA' ? USA_BOUNDS_FALLBACK : null;
}
function unwrappedInterval(west, east, reference) {
  const left = geo.unwrapLongitude(west, reference);
  let right = geo.unwrapLongitude(east, left);
  if (right < left) right += 360;
  return [left, right];
}
function viewportOverlaps(bounds) {
  if (!bounds) return false;
  const view = map.getBounds();
  const mapCenter = map.getCenter?.();
  const reference = Number.isFinite(Number(mapCenter?.lng)) ? Number(mapCenter.lng) : Number(view.getWest());
  const [west, east] = unwrappedInterval(view.getWest(), view.getEast(), reference);
  const [boundsWest, boundsEast] = unwrappedInterval(bounds.west, bounds.east, reference);
  const south = view.getSouth(), north = view.getNorth();
  return west <= boundsEast && east >= boundsWest && south <= bounds.north && north >= bounds.south;
}
function partitionForId(index, id) {
  const value = String(id || '');
  if (!value) return null;
  for (const [partition, descriptor] of partitionEntries(index)) {
    const prefix = String(descriptor?.id_prefix || '');
    if (prefix && value.startsWith(prefix)) return partition;
  }
  return value.startsWith('US-') ? 'USA' : null;
}
function descriptorCenter(bounds) {
  if (!bounds) return null;
  const west = Number(bounds.west);
  const east = geo.unwrapLongitude(bounds.east, west);
  return [(west + east) / 2, (Number(bounds.south) + Number(bounds.north)) / 2];
}
function distanceToMapCenterKm(bounds) {
  const center = descriptorCenter(bounds);
  const mapCenter = map.getCenter?.();
  if (!center || !mapCenter || !Number.isFinite(Number(mapCenter.lng)) || !Number.isFinite(Number(mapCenter.lat))) {
    return Number.POSITIVE_INFINITY;
  }
  return geo.haversineDistanceKm(center, [Number(mapCenter.lng), Number(mapCenter.lat)]);
}
function subdivisionBounds(feature) {
  if (!feature?.geometry) return null;
  const referenceLng = Number(map.getCenter?.()?.lng);
  try {
    const bounds = geo.antimeridianAwareBounds(
      feature.geometry,
      Number.isFinite(referenceLng) ? referenceLng : null,
    );
    return [[bounds.west,bounds.south],[bounds.east,bounds.north]];
  } catch {
    return null;
  }
}
function touch(state) {
  state.lastUsed = ++useClock;
  return state;
}
function cacheBytes() {
  return [...cache.values()].reduce((sum, state) => sum + state.bytes, 0);
}
function notifySourceRefresh(reason='update') {
  const detail = {
    reason,
    sourceId:SOURCE_ID,
    renderedPartitions:[...activePartitions],
  };
  for (const [observerId, callback] of sourceRefreshObservers.entries()) {
    try { callback(detail); }
    catch (error) { console.warn(`Subdivision source refresh observer failed: ${observerId}`, error); }
  }
  window.dispatchEvent(new CustomEvent('potato-atlas-subdivisions-source-change', { detail }));
}
function syncDiagnostics() {
  const diagnostics = window.__potatoAtlasDiagnostics;
  if (!diagnostics) return;
  diagnostics.subdivisions = {
    ...(diagnostics.subdivisions || {}),
    cacheHits,
    cacheMisses,
    cacheEvictions,
    cacheBytes:cacheBytes(),
    cachedPartitions:cache.size,
    renderedBytes:activeBytes,
    renderedPartitions:activePartitions.length,
  };
}
function featureById(partition, id) {
  return cache.get(partition)?.data?.features?.find(feature => feature?.properties?.id === id) || null;
}
function enforceCacheBudget(index, extraProtected = []) {
  const protectedIds = new Set(activePartitions);
  const selectedPartition = partitionForId(index, selectedId);
  const pendingPartition = partitionForId(index, pendingDeepLinkId);
  if (selectedPartition) protectedIds.add(selectedPartition);
  if (pendingPartition) protectedIds.add(pendingPartition);
  for (const partition of forcedPartitions) protectedIds.add(partition);
  for (const partition of extraProtected) if (partition) protectedIds.add(partition);

  let bytes = cacheBytes();
  const evictable = [...cache.entries()]
    .filter(([partition]) => !protectedIds.has(partition))
    .sort((a, b) => a[1].lastUsed - b[1].lastUsed || a[0].localeCompare(b[0]));

  while ((cache.size > runtimeBudget.cache_max_partitions || bytes > runtimeBudget.cache_max_bytes) && evictable.length) {
    const [partition, state] = evictable.shift();
    if (!cache.has(partition)) continue;
    cache.delete(partition);
    bytes -= state.bytes;
    cacheEvictions += 1;
  }
  syncDiagnostics();
}
function syncUrl(id) {
  urlState.patch('selection-inspector', { set:{ subdivision:id || null } });
}
function selectSubdivision(partition, feature, options = {}) {
  if (!feature) return false;
  const p = feature.properties || {};
  selectedId = p.id || null;
  pendingDeepLinkId = null;
  syncUrl(selectedId);
  syncSelectedLabel(selectedId);
  const bounds = subdivisionBounds(feature);
  if (options.fit !== false && bounds) motion.fitBounds(map, bounds, { padding:80, duration:650, maxZoom:7.4 });
  openInspector(feature);
  window.dispatchEvent(new CustomEvent('potato-atlas-subdivision-select', { detail:{ partition, id:selectedId, properties:p, feature } }));
  return true;
}
async function handleSharedLayerClick(event) {
  const id = event.features?.[0]?.properties?.id;
  if (!id) return;
  try {
    const index = await subdivisionIndex();
    const partition = partitionForId(index, id);
    if (!partition) return;
    await loadPartition(partition);
    const feature = featureById(partition, id);
    if (feature) selectSubdivision(partition, feature, {fit:true});
  } catch (error) {
    console.warn(`Subdivision selection unavailable: ${id}`, error);
  }
}
function unbindSharedLayerFallback() {
  if (!fallbackSharedHandlers) return;
  try { map.off('mouseenter', HIT_ID, fallbackSharedHandlers.onEnter); } catch {}
  try { map.off('mouseleave', HIT_ID, fallbackSharedHandlers.onLeave); } catch {}
  try { map.off('click', HIT_ID, fallbackSharedHandlers.onClick); } catch {}
  fallbackSharedHandlers = null;
}
function syncSharedLayerInteraction() {
  const interaction = interactionRouter();
  if (!interaction?.register) return false;
  unbindSharedLayerFallback();
  interaction.register('subdivisions', {
    layers:[HIT_ID],
    objectType:'subdivision',
    clickPriority:60,
    hoverPriority:60,
    enabled:()=>!sharedScale || sharedScale.capabilityActive('subdivisions', 'interact', map.getZoom()),
    onClick:(event, feature) => handleSharedLayerClick({ ...event, features:[feature] }),
  });
  return true;
}
function bindSharedLayerEvents() {
  if (syncSharedLayerInteraction()) { eventsBound = true; return; }
  if (eventsBound) return;
  // Degraded/direct-module fallback for tests and partial boots. Promote live
  // to Interaction Router ownership when the shared Router announces readiness.
  const onEnter = () => { map.getCanvas().style.cursor = 'pointer'; };
  const onLeave = () => { map.getCanvas().style.cursor = ''; };
  const onClick = event => {
    if (event?.originalEvent) event.originalEvent.__potatoAtlasOverlayHandled = true;
    return handleSharedLayerClick(event);
  };
  map.on('mouseenter', HIT_ID, onEnter);
  map.on('mouseleave', HIT_ID, onLeave);
  map.on('click', HIT_ID, onClick);
  fallbackSharedHandlers = { onEnter, onLeave, onClick };
  eventsBound = true;
}
window.addEventListener?.('potato-atlas-interaction-ready', () => syncSharedLayerInteraction());

function viewportWidth() {
  return Number(window.innerWidth || document.documentElement?.clientWidth || 1024);
}
function labelPresentation() {
  const narrow = viewportWidth() <= NARROW_SCREEN_MAX;
  return {
    narrow,
    labelZoom:Number(labelZoomBase || 0) + (narrow ? NARROW_LABEL_DELAY : 0),
    nameZoom:Number(nameZoomBase || 0) + (narrow ? NARROW_LABEL_DELAY : 0),
  };
}
function syncSelectedLabel(id = selectedId) {
  if (!map.getLayer(SELECTED_LABEL_ID) || typeof map.setFilter !== 'function') return false;
  map.setFilter(SELECTED_LABEL_ID, ['==', ['get','id'], id || '__none__']);
  return true;
}
function syncLabelPresentation() {
  if (!map.getLayer(LABEL_ID) || labelZoomBase == null || nameZoomBase == null) return false;
  const policy = labelPresentation();
  map.setLayerZoomRange?.(LABEL_ID, policy.labelZoom, 24);
  map.setLayoutProperty?.(LABEL_ID, 'text-field', ['step',['zoom'],['get','code'],policy.nameZoom,['get','name']]);
  return true;
}
async function scaleRuntime() {
  const scale = await window.__potatoAtlasScale?.ready;
  if (!scale?.threshold || !scale?.bandThreshold || !scale?.capabilityActive) throw new Error('World Map Scale runtime unavailable to subdivisions.');
  sharedScale = scale;
  return scale;
}
async function installSharedLayers() {
  const scale = await scaleRuntime();
  const renderZoom = scale.threshold('subdivisions', 'render');
  const labelZoom = scale.threshold('subdivisions', 'label');
  labelZoomBase = labelZoom;
  let contextLineZoom = renderZoom;
  try { contextLineZoom = Math.min(renderZoom, scale.bandThreshold('macro-region')); } catch {}
  const nameZoom = scale.bandThreshold('subnational');
  nameZoomBase = nameZoom;
  if (!map.getSource(SOURCE_ID)) {
    map.addSource(SOURCE_ID, { type:'geojson', data:{type:'FeatureCollection',features:[]}, promoteId:'id' });
  }
  const before = map.getLayer('countries-line') ? 'countries-line' : (map.getLayer('countries-outline') ? 'countries-outline' : undefined);
  if (!map.getLayer(HIT_ID)) {
    map.addLayer({id:HIT_ID,type:'fill',source:SOURCE_ID,minzoom:renderZoom,paint:{'fill-color':'#ffffff','fill-opacity':0.001}}, before);
  }
  if (!map.getLayer(LINE_ID)) {
    map.addLayer({
      id:LINE_ID,type:'line',source:SOURCE_ID,minzoom:contextLineZoom,
      paint:{
        'line-color':'#9aa9a2',
        'line-opacity':['interpolate',['linear'],['zoom'],renderZoom,0.28,5,0.55,7,0.78],
        'line-width':['interpolate',['linear'],['zoom'],renderZoom,0.45,5,0.85,7,1.4]
      }
    }, before);
  }
  if (!map.getLayer(LABEL_ID)) {
    map.addLayer({
      id:LABEL_ID,type:'symbol',source:SOURCE_ID,minzoom:labelZoom,
      layout:{
        'text-field':['step',['zoom'],['get','code'],nameZoom,['get','name']],
        'text-size':['interpolate',['linear'],['zoom'],labelZoom,9,6.5,12],
        'text-max-width':8,'text-allow-overlap':false,'text-ignore-placement':false
      },
      paint:{'text-color':'#d4ddd7','text-halo-color':'#0a0f0f','text-halo-width':1.1,'text-opacity':0.86}
    }, before);
  }
  if (!map.getLayer(SELECTED_LABEL_ID)) {
    map.addLayer({
      id:SELECTED_LABEL_ID,type:'symbol',source:SOURCE_ID,minzoom:renderZoom,
      filter:['==',['get','id'],'__none__'],
      layout:{
        'text-field':['coalesce',['get','name'],['get','code']],
        'text-size':['interpolate',['linear'],['zoom'],renderZoom,10,7,13],
        'text-max-width':10,'text-allow-overlap':true,'text-ignore-placement':true
      },
      paint:{'text-color':'#fff0ad','text-halo-color':'#080b0b','text-halo-width':1.5,'text-opacity':1}
    }, before);
  }
  syncLabelPresentation();
  syncSelectedLabel();
  bindSharedLayerEvents();
}
map.on('sourcedata', event => {
  if (event?.sourceId === SOURCE_ID && event?.isSourceLoaded) notifySourceRefresh('sourcedata');
});
async function loadPartition(partition) {
  if (cache.has(partition)) {
    cacheHits += 1;
    const state = touch(cache.get(partition));
    syncDiagnostics();
    return state;
  }
  cacheMisses += 1;
  const index = await subdivisionIndex();
  const descriptor = index?.partitions?.[partition];
  const fallbackPath = partition === 'USA' ? USA_PARTITION_FALLBACK : null;
  const partitionPath = descriptor?.path || fallbackPath;
  if (!partitionPath) {
    syncDiagnostics();
    throw new Error(`Subdivision partition ${partition} is not available.`);
  }
  const response = await fetch(`../data/world-subdivisions/${partitionPath}`);
  if (!response.ok) {
    syncDiagnostics();
    throw new Error(`Subdivision partition ${partition} unavailable (${response.status})`);
  }
  const data = await response.json();
  if (data?.type !== 'FeatureCollection' || !Array.isArray(data.features)) {
    syncDiagnostics();
    throw new Error(`Subdivision partition ${partition} is not GeoJSON.`);
  }
  const state = touch({
    descriptor: descriptor || { path:partitionPath },
    data,
    bytes:Number(descriptor?.bytes) || 0,
    lastUsed:0,
  });
  cache.set(partition, state);
  await installSharedLayers();
  enforceCacheBudget(index, [partition]);
  return state;
}
function relevantCandidates(index) {
  const pendingPartition = partitionForId(index, pendingDeepLinkId);
  const selectedPartition = partitionForId(index, selectedId);
  return partitionEntries(index)
    .map(([partition, descriptor]) => {
      const bounds = descriptorBounds(partition, descriptor);
      let priority = 3;
      if (forcedPartitions.has(partition)) priority = 0;
      else if (partition === pendingPartition) priority = 1;
      else if (partition === selectedPartition) priority = 2;
      if (priority === 3 && !viewportOverlaps(bounds)) return null;
      return { partition, descriptor, priority, distance:distanceToMapCenterKm(bounds) };
    })
    .filter(Boolean)
    .sort((a, b) => a.priority - b.priority || a.distance - b.distance || a.partition.localeCompare(b.partition));
}
async function reconcileActive(index) {
  await installSharedLayers();
  normalizeBudget(index);
  const selected = [];
  let bytes = 0;
  for (const candidate of relevantCandidates(index)) {
    let state;
    try {
      state = await loadPartition(candidate.partition);
    } catch (error) {
      console.warn(`Subdivision layer unavailable: ${candidate.partition}`, error);
      continue;
    }
    const nextCount = selected.length + 1;
    const nextBytes = bytes + state.bytes;
    if (nextCount > runtimeBudget.rendered_max_partitions || nextBytes > runtimeBudget.rendered_max_bytes) continue;
    selected.push({ partition:candidate.partition, state });
    bytes = nextBytes;
  }
  const merged = {
    type:'FeatureCollection',
    features:selected.flatMap(entry => entry.state.data.features || []),
  };
  const source = map.getSource(SOURCE_ID);
  if (source?.setData) source.setData(merged);
  else if (source) source.data = merged;
  activePartitions = selected.map(entry => entry.partition);
  activeBytes = bytes;
  notifySourceRefresh('setData');
  enforceCacheBudget(index);
  syncDiagnostics();
  return activePartitions;
}
async function ensureRelevantPartitions() {
  let index;
  try {
    index = await subdivisionIndex();
  } catch (error) {
    console.warn('Subdivision index unavailable:', error);
    return;
  }
  const deepLinkId = pendingDeepLinkId;
  await reconcileActive(index);
  if (!deepLinkId || pendingDeepLinkId !== deepLinkId) return;
  const deepLinkPartition = partitionForId(index, deepLinkId);
  if (!deepLinkPartition) return;
  try {
    await loadPartition(deepLinkPartition);
    if (pendingDeepLinkId === deepLinkId) {
      // Consume camera intent before fitBounds so the resulting moveend cannot replay it.
      pendingDeepLinkId = null;
      const feature = featureById(deepLinkPartition, deepLinkId);
      if (feature) selectSubdivision(deepLinkPartition, feature, {fit:true});
    }
  } catch (error) {
    console.warn(`Subdivision layer unavailable: ${deepLinkPartition}`, error);
  }
}

await installSharedLayers();
map.on('moveend', ensureRelevantPartitions);
window.addEventListener?.('resize', syncLabelPresentation);
await ensureRelevantPartitions();

window.__potatoAtlasSubdivisions = {
  loadPartition,
  async select(id, options={}) {
    const index = await subdivisionIndex();
    const partition = partitionForId(index, id);
    if (!partition) return false;
    await loadPartition(partition);
    const result = selectSubdivision(partition, featureById(partition, id), options);
    if (result) await reconcileActive(index);
    return result;
  },
  clear(options={}) {
    const code = String(new URL(location.href).searchParams.get('country') || '').toUpperCase();
    selectedId = null;
    pendingDeepLinkId = null;
    syncUrl(null);
    syncSelectedLabel(null);
    if (options.restore !== false) {
      if (inspector?.current?.()?.type === 'subdivision') inspector.back();
      else if (code && window.goCountry) window.goCountry(code);
    }
    subdivisionIndex().then(reconcileActive).catch(error => console.warn('Subdivision reconcile unavailable:', error));
    window.dispatchEvent(new CustomEvent('potato-atlas-subdivision-clear'));
    return true;
  },
  get selected() { return selectedId; },
  loadedPartitions() { return [...cache.keys()]; },
  async retainPartition(partition, owner='anonymous') {
    const key = String(partition || '').toUpperCase();
    const index = await subdivisionIndex();
    if (!index?.partitions?.[key]) return false;
    retainForcedPartition(key, owner);
    try {
      await loadPartition(key);
      await reconcileActive(index);
      return true;
    } catch (error) {
      releaseForcedPartition(key, owner);
      throw error;
    }
  },
  async releasePartition(partition, owner='anonymous') {
    const key = String(partition || '').toUpperCase();
    releaseForcedPartition(key, owner);
    const index = await subdivisionIndex();
    await reconcileActive(index);
    return true;
  },
  async refresh() {
    const index = await subdivisionIndex();
    return reconcileActive(index);
  },
  registerSourceRefreshObserver(id, callback) {
    const key = String(id || '').trim();
    if (!key || typeof callback !== 'function') return false;
    sourceRefreshObservers.set(key, callback);
    return true;
  },
  unregisterSourceRefreshObserver(id) {
    return sourceRefreshObservers.delete(String(id || '').trim());
  },
  sourceRefreshObservers() { return [...sourceRefreshObservers.keys()].sort(); },
  registerEvidenceProvider(id, provider) {
    const key = String(id || '').trim();
    if (!key || !provider?.summary) return false;
    evidenceProviders.set(key, provider);
    return true;
  },
  unregisterEvidenceProvider(id) {
    return evidenceProviders.delete(String(id || '').trim());
  },
  evidenceProviders() { return [...evidenceProviders.keys()].sort(); },
  evidenceSummaries(id) {
    return activeEvidenceRows(id).map(({providerId,row}) => ({
      providerId,
      eyebrow:String(row.eyebrow || 'Active evidence'),
      primary:row.primary ?? null,
      summary:String(row.summary || ''),
      boundary:String(row.boundary || ''),
      actionLabel:String(row.actionLabel || 'Open evidence'),
    }));
  },
  status() {
    return {
      selected:selectedId,
      renderedPartitions:[...activePartitions],
      renderedBytes:activeBytes,
      cachedPartitions:[...cache.keys()],
      forcedPartitions:[...forcedPartitions],
      retentionOwners:retentionOwners(),
      cacheBytes:cacheBytes(),
      cacheHits,
      cacheMisses,
      cacheEvictions,
      budget:{...runtimeBudget},
    };
  },
};

syncDiagnostics();
window.dispatchEvent(new CustomEvent('potato-atlas-subdivisions-ready', { detail:{ selected:selectedId } }));
