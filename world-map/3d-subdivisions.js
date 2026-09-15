// Generic lazy subdivision renderer for the World Map.
// Uses same-origin country partitions and the canonical right inspector (#panel).

const map = window.__potatoAtlasMap;
if (!map) throw new Error('Atlas subdivisions require the core map.');

const INDEX_URL = '../data/world-subdivisions/index.json';
const USA_PARTITION_FALLBACK = 'USA.geo.json';
const SOURCE_PREFIX = 'atlas-subdivisions-';
const LINE_PREFIX = 'atlas-subdivision-line-';
const HIT_PREFIX = 'atlas-subdivision-hit-';
const LABEL_PREFIX = 'atlas-subdivision-label-';
const USA_BOUNDS_FALLBACK = { west:-179.5, east:-65, south:17, north:72.5 };

const loaded = new Map();
let indexPromise = null;
let selectedId = new URL(location.href).searchParams.get('subdivision') || null;
// Camera intent from a deep link is one-shot. Persistent selection must not be
// replayed on every moveend or fitBounds can recurse forever.
let pendingDeepLinkId = selectedId;
let panelSnapshot = null;

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
function renderInspector(feature) {
  const panel = document.getElementById('panel');
  if (!panel || !feature) return;
  if (panel.querySelector(':scope > .eyebrow')?.textContent?.trim() !== 'Subdivision') panelSnapshot = panel.innerHTML;
  const p = feature.properties || {};
  const population = p.population || {};
  const code = countryCode(p);
  panel.innerHTML = `
    <div class="eyebrow">Subdivision</div>
    <h1>${esc(p.name || p.id || 'Subdivision')}</h1>
    <p class="muted">${esc(p.subdivision_type || 'Subdivision')} · ${esc(p.code || p.id || '')} · ${esc(p.country_name || p.parent_name || code)}</p>
    <div class="stat-grid">
      <div><span>Population</span><b>${fmt(population.value)}</b><small>${esc(population.period || '—')}</small></div>
      <div><span>Area</span><b>${fmt(p.area_km2)} km²</b><small>land + water</small></div>
    </div>
    ${population.source ? `<p class="muted">Source: ${esc(population.source)}</p>` : ''}
    <div class="panel-actions">
      <button type="button" data-subdivision-open-country>Open country</button>
      <button type="button" data-subdivision-close>Close subdivision</button>
    </div>`;
  panel.querySelector('[data-subdivision-open-country]')?.addEventListener('click', () => {
    if (code && window.goCountry) window.goCountry(code);
  });
  panel.querySelector('[data-subdivision-close]')?.addEventListener('click', () => window.__potatoAtlasSubdivisions?.clear?.());
  window.__potatoAtlasPanelLifecycle?.publish?.();
}
function restoreInspector() {
  const panel = document.getElementById('panel');
  if (!panel) return;
  const eyebrow = panel.querySelector(':scope > .eyebrow')?.textContent?.trim();
  if (eyebrow === 'Subdivision' && panelSnapshot != null) {
    panel.innerHTML = panelSnapshot;
    panelSnapshot = null;
    window.__potatoAtlasPanelLifecycle?.publish?.();
  }
}
async function subdivisionIndex() {
  if (!indexPromise) {
    indexPromise = fetch(INDEX_URL).then(response => {
      if (!response.ok) throw new Error(`Subdivision index unavailable (${response.status})`);
      return response.json();
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
function viewportOverlaps(bounds) {
  if (!bounds) return false;
  const view = map.getBounds();
  const west = view.getWest(), east = view.getEast(), south = view.getSouth(), north = view.getNorth();
  return west <= bounds.east && east >= bounds.west && south <= bounds.north && north >= bounds.south;
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
function recursiveBounds(node, box) {
  if (!Array.isArray(node)) return box;
  if (node.length >= 2 && typeof node[0] === 'number' && typeof node[1] === 'number') {
    const [lon, lat] = node;
    box[0] = Math.min(box[0], lon); box[1] = Math.min(box[1], lat);
    box[2] = Math.max(box[2], lon); box[3] = Math.max(box[3], lat);
    return box;
  }
  for (const child of node) recursiveBounds(child, box);
  return box;
}
function geometryBounds(feature) {
  const box = recursiveBounds(feature?.geometry?.coordinates, [Infinity, Infinity, -Infinity, -Infinity]);
  return box.every(Number.isFinite) ? [[box[0],box[1]],[box[2],box[3]]] : null;
}
function featureById(partition, id) {
  return loaded.get(partition)?.data?.features?.find(feature => feature?.properties?.id === id) || null;
}
function sourceId(partition) { return `${SOURCE_PREFIX}${partition}`; }
function lineId(partition) { return `${LINE_PREFIX}${partition}`; }
function hitId(partition) { return `${HIT_PREFIX}${partition}`; }
function labelId(partition) { return `${LABEL_PREFIX}${partition}`; }
function syncUrl(id) {
  const url = new URL(location.href);
  if (id) url.searchParams.set('subdivision', id);
  else url.searchParams.delete('subdivision');
  history.replaceState({}, '', url);
}
function selectSubdivision(partition, feature, options = {}) {
  if (!feature) return false;
  const p = feature.properties || {};
  selectedId = p.id || null;
  pendingDeepLinkId = null;
  syncUrl(selectedId);
  const bounds = geometryBounds(feature);
  if (options.fit !== false && bounds) map.fitBounds(bounds, { padding:80, duration:650, maxZoom:7.4 });
  renderInspector(feature);
  window.dispatchEvent(new CustomEvent('potato-atlas-subdivision-select', { detail:{ partition, id:selectedId, properties:p, feature } }));
  return true;
}
function bindLayerEvents(partition) {
  const hit = hitId(partition);
  map.on('mouseenter', hit, () => { map.getCanvas().style.cursor = 'pointer'; });
  map.on('mouseleave', hit, () => { map.getCanvas().style.cursor = ''; });
  map.on('click', hit, event => {
    const feature = event.features?.[0];
    if (!feature) return;
    if (event.originalEvent) {
      event.originalEvent.__potatoAtlasSubdivisionHandled = true;
      event.originalEvent.__potatoAtlasOverlayHandled = true;
    }
    selectSubdivision(partition, feature, {fit:true});
  });
}
function installPartitionLayers(partition, data) {
  const source = sourceId(partition);
  if (!map.getSource(source)) map.addSource(source, { type:'geojson', data, promoteId:'id' });
  const before = map.getLayer('countries-line') ? 'countries-line' : (map.getLayer('countries-outline') ? 'countries-outline' : undefined);
  if (!map.getLayer(hitId(partition))) {
    map.addLayer({id:hitId(partition),type:'fill',source,minzoom:3.4,paint:{'fill-color':'#ffffff','fill-opacity':0.001}}, before);
  }
  if (!map.getLayer(lineId(partition))) {
    map.addLayer({
      id:lineId(partition),type:'line',source,minzoom:3.4,
      paint:{
        'line-color':'#9aa9a2',
        'line-opacity':['interpolate',['linear'],['zoom'],3.4,0.28,5,0.55,7,0.78],
        'line-width':['interpolate',['linear'],['zoom'],3.4,0.45,5,0.85,7,1.4]
      }
    }, before);
  }
  if (!map.getLayer(labelId(partition))) {
    map.addLayer({
      id:labelId(partition),type:'symbol',source,minzoom:4.25,
      layout:{
        'text-field':['step',['zoom'],['get','code'],5.8,['get','name']],
        'text-size':['interpolate',['linear'],['zoom'],4.25,9,6.5,12],
        'text-max-width':8,'text-allow-overlap':false,'text-ignore-placement':false
      },
      paint:{'text-color':'#d4ddd7','text-halo-color':'#0a0f0f','text-halo-width':1.1,'text-opacity':0.86}
    });
  }
  bindLayerEvents(partition);
}
async function loadPartition(partition) {
  if (loaded.has(partition)) return loaded.get(partition);
  const index = await subdivisionIndex();
  const descriptor = index?.partitions?.[partition];
  const fallbackPath = partition === 'USA' ? USA_PARTITION_FALLBACK : null;
  const partitionPath = descriptor?.path || fallbackPath;
  if (!partitionPath) throw new Error(`Subdivision partition ${partition} is not available.`);
  const response = await fetch(`../data/world-subdivisions/${partitionPath}`);
  if (!response.ok) throw new Error(`Subdivision partition ${partition} unavailable (${response.status})`);
  const data = await response.json();
  if (data?.type !== 'FeatureCollection' || !Array.isArray(data.features)) throw new Error(`Subdivision partition ${partition} is not GeoJSON.`);
  const state = { descriptor: descriptor || { path:partitionPath }, data };
  loaded.set(partition, state);
  installPartitionLayers(partition, data);
  return state;
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
  const deepLinkPartition = partitionForId(index, deepLinkId);
  for (const [partition, descriptor] of partitionEntries(index)) {
    const wantsDeepLink = partition === deepLinkPartition;
    const wantsViewport = viewportOverlaps(descriptorBounds(partition, descriptor));
    if (!wantsDeepLink && !wantsViewport) continue;
    try {
      await loadPartition(partition);
      if (wantsDeepLink && pendingDeepLinkId === deepLinkId) {
        pendingDeepLinkId = null;
        const feature = featureById(partition, deepLinkId);
        if (feature) selectSubdivision(partition, feature, {fit:true});
      }
    } catch (error) {
      console.warn(`Subdivision layer unavailable: ${partition}`, error);
    }
  }
}

map.on('moveend', ensureRelevantPartitions);
await ensureRelevantPartitions();

window.__potatoAtlasSubdivisions = {
  loadPartition,
  async select(id, options={}) {
    const index = await subdivisionIndex();
    const partition = partitionForId(index, id);
    if (!partition) return false;
    await loadPartition(partition);
    return selectSubdivision(partition, featureById(partition, id), options);
  },
  clear() {
    selectedId = null;
    pendingDeepLinkId = null;
    syncUrl(null);
    restoreInspector();
    window.dispatchEvent(new CustomEvent('potato-atlas-subdivision-clear'));
    return true;
  },
  get selected() { return selectedId; },
  loadedPartitions() { return [...loaded.keys()]; },
};

window.dispatchEvent(new CustomEvent('potato-atlas-subdivisions-ready', { detail:{ selected:selectedId } }));
