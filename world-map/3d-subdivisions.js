// Generic first-wave subdivision renderer for the World Map.
//
// The module is lazy-loaded by camera scale. It reads the same-origin partition
// index, then loads country partitions only when they are relevant. The first
// implemented partition is USA: 50 states + District of Columbia.
// Deep-link contract: ?subdivision=US-CA (or another supported subdivision id).

const map = window.__potatoAtlasMap;
if (!map) throw new Error('Atlas subdivisions require the core map.');

const INDEX_URL = '../data/world-subdivisions/index.json';
const USA_PARTITION_FALLBACK = 'USA.geo.json';
const SOURCE_PREFIX = 'atlas-subdivisions-';
const LINE_PREFIX = 'atlas-subdivision-line-';
const HIT_PREFIX = 'atlas-subdivision-hit-';
const LABEL_PREFIX = 'atlas-subdivision-label-';
const USA_BOUNDS = { west:-179.5, east:-65, south:17, north:72.5 };

const loaded = new Map();
let indexPromise = null;
let selectedId = new URL(location.href).searchParams.get('subdivision') || null;
// A URL deep link needs one initial camera fit after its partition loads. Keep
// that one-shot intent separate from selectedId: selectedId persists after a
// click, while replaying it on every moveend would create a fitBounds loop.
let pendingDeepLinkId = selectedId;

function fmt(value) {
  if (value == null) return '—';
  return new Intl.NumberFormat('en', { maximumFractionDigits:1 }).format(value);
}
function esc(value) {
  return String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot',"'":'&#39;'}[char]));
}
function installInspector() {
  if (document.getElementById('atlasSubdivisionCard')) return;
  const style = document.createElement('style');
  style.id = 'atlasSubdivisionStyle';
  style.textContent = `#atlasSubdivisionCard{position:absolute;left:12px;top:54px;z-index:8;width:min(290px,calc(100% - 24px));padding:10px 11px;background:#0b1010ef;border:1px solid #40504d;border-radius:10px;box-shadow:0 8px 28px #0009;backdrop-filter:blur(9px);font-size:11px}#atlasSubdivisionCard[hidden]{display:none!important}#atlasSubdivisionCard .sub-head{display:flex;align-items:start;justify-content:space-between;gap:8px}#atlasSubdivisionCard b{font-size:14px}#atlasSubdivisionCard small{display:block;color:#9aa6a0;margin-top:4px}#atlasSubdivisionCard .sub-grid{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:8px}#atlasSubdivisionCard .sub-grid div{border:1px solid #2d3939;border-radius:7px;padding:6px}#atlasSubdivisionCard .sub-grid span{display:block;color:#8d9993;font-size:9px;text-transform:uppercase}#atlasSubdivisionCard button{padding:2px 6px;min-height:auto}`;
  document.head.appendChild(style);
  const card = document.createElement('div');
  card.id = 'atlasSubdivisionCard';
  card.hidden = true;
  card.innerHTML = '<div class="sub-head"><div><b>Subdivision</b></div><button type="button" data-subdivision-close aria-label="Close subdivision inspector">×</button></div>';
  document.querySelector('.mapwrap')?.appendChild(card);
  card.querySelector('[data-subdivision-close]')?.addEventListener('click', () => window.__potatoAtlasSubdivisions?.clear?.());
}
function renderInspector(feature) {
  installInspector();
  const card = document.getElementById('atlasSubdivisionCard');
  if (!card || !feature) return;
  const p = feature.properties || {};
  const population = p.population || {};
  card.innerHTML = `<div class="sub-head"><div><b>${esc(p.name || p.id)}</b><small>${esc(p.subdivision_type || 'subdivision')} · ${esc(p.code || '')} · United States</small></div><button type="button" data-subdivision-close aria-label="Close subdivision inspector">×</button></div><div class="sub-grid"><div><span>Population</span><b>${fmt(population.value)}</b><small>${esc(population.period || '')}</small></div><div><span>Area</span><b>${fmt(p.area_km2)} km²</b><small>land + water</small></div></div><small>${esc(population.source || '')}</small>`;
  card.hidden = false;
  card.querySelector('[data-subdivision-close]')?.addEventListener('click', () => window.__potatoAtlasSubdivisions?.clear?.());
}
function hideInspector() {
  const card = document.getElementById('atlasSubdivisionCard');
  if (card) card.hidden = true;
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
function viewportOverlaps(bounds) {
  const view = map.getBounds();
  const west = view.getWest(), east = view.getEast(), south = view.getSouth(), north = view.getNorth();
  const horizontal = west <= bounds.east && east >= bounds.west;
  const vertical = south <= bounds.north && north >= bounds.south;
  return horizontal && vertical;
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
        'text-max-width':8,
        'text-allow-overlap':false,
        'text-ignore-placement':false
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
  const deepLinkId = pendingDeepLinkId;
  if (deepLinkId?.startsWith('US-') || viewportOverlaps(USA_BOUNDS)) {
    try {
      await loadPartition('USA');
      if (deepLinkId?.startsWith('US-')) {
        // Consume the one-shot intent before moving the camera so the moveend
        // generated by fitBounds cannot replay the same selection.
        pendingDeepLinkId = null;
        const feature = featureById('USA', deepLinkId);
        if (feature) selectSubdivision('USA', feature, {fit:true});
      }
    } catch (error) {
      console.warn('U.S. subdivision layer unavailable:', error);
    }
  }
}

map.on('moveend', ensureRelevantPartitions);
await ensureRelevantPartitions();

window.__potatoAtlasSubdivisions = {
  loadPartition,
  select(id, options={}) {
    const partition = String(id || '').startsWith('US-') ? 'USA' : null;
    if (!partition) return false;
    return loadPartition(partition).then(() => selectSubdivision(partition, featureById(partition, id), options));
  },
  clear() { selectedId = null; pendingDeepLinkId = null; syncUrl(null); hideInspector(); },
  get selected() { return selectedId; },
  loadedPartitions() { return [...loaded.keys()]; },
};

window.dispatchEvent(new CustomEvent('potato-atlas-subdivisions-ready', { detail:{ selected:selectedId } }));
