// Generic lazy subdivision renderer for the World Map.
// Partition ownership lives in data/world-subdivisions/index.json so adding a
// country does not require hard-coded renderer logic.

const map = window.__potatoAtlasMap;
if (!map) throw new Error('Atlas subdivisions require the core map.');

const INDEX_URL = '../data/world-subdivisions/index.json';
const SOURCE_PREFIX = 'atlas-subdivisions-';
const LINE_PREFIX = 'atlas-subdivision-line-';
const HIT_PREFIX = 'atlas-subdivision-hit-';
const LABEL_PREFIX = 'atlas-subdivision-label-';

const loaded = new Map();
let indexPromise = null;
let selectedId = new URL(location.href).searchParams.get('subdivision') || null;
// URL selection is one-shot camera intent. Persistent selectedId must never be
// replayed on moveend or fitBounds can feed itself forever.
let pendingDeepLinkId = selectedId;

function fmt(value) {
  if (value == null) return '—';
  return new Intl.NumberFormat('en', { maximumFractionDigits:1 }).format(value);
}
function esc(value) {
  return String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
}
function installInspector() {
  if (document.getElementById('atlasSubdivisionCard')) return;
  const style = document.createElement('style');
  style.id = 'atlasSubdivisionStyle';
  style.textContent = `#atlasSubdivisionCard{position:absolute;left:12px;top:54px;z-index:8;width:min(310px,calc(100% - 24px));padding:10px 11px;background:#0b1010ef;border:1px solid #40504d;border-radius:10px;box-shadow:0 8px 28px #0009;backdrop-filter:blur(9px);font-size:11px}#atlasSubdivisionCard[hidden]{display:none!important}#atlasSubdivisionCard .sub-head{display:flex;align-items:start;justify-content:space-between;gap:8px}#atlasSubdivisionCard b{font-size:14px}#atlasSubdivisionCard small{display:block;color:#9aa6a0;margin-top:4px}#atlasSubdivisionCard .sub-grid{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:8px}#atlasSubdivisionCard .sub-grid div{border:1px solid #2d3939;border-radius:7px;padding:6px}#atlasSubdivisionCard .sub-grid span{display:block;color:#8d9993;font-size:9px;text-transform:uppercase}#atlasSubdivisionCard button{padding:2px 6px;min-height:auto}#atlasSubdivisionCard .sub-infra{margin-top:8px;padding-top:7px;border-top:1px solid #2d3939}#atlasSubdivisionCard .sub-infra-tags{display:flex;gap:5px;flex-wrap:wrap;margin-top:5px}#atlasSubdivisionCard .sub-infra-tags button{border:1px solid #40504d;border-radius:999px;padding:3px 6px;background:#101817;color:#c9d5d0;font-size:10px}`;
  document.head.appendChild(style);
  const card = document.createElement('div');
  card.id = 'atlasSubdivisionCard';
  card.hidden = true;
  document.querySelector('.mapwrap')?.appendChild(card);
}
function renderInspector(feature, descriptor={}) {
  installInspector();
  const card = document.getElementById('atlasSubdivisionCard');
  if (!card || !feature) return;
  const p = feature.properties || {};
  const population = p.population || {};
  const parent = p.parent_name || descriptor.parent_name || p.parent_iso3 || '';
  const type = p.subdivision_type || 'subdivision';
  const areaText = p.area_km2 == null ? '—' : `${fmt(p.area_km2)} km²`;
  card.innerHTML = `<div class="sub-head"><div><b>${esc(p.name || p.id)}</b><small>${esc(type)}${p.code ? ` · ${esc(p.code)}` : ''}${parent ? ` · ${esc(parent)}` : ''}</small></div><button type="button" data-subdivision-close aria-label="Close subdivision inspector">×</button></div><div class="sub-grid"><div><span>Population</span><b>${fmt(population.value)}</b><small>${esc(population.period || '')}</small></div><div><span>Area</span><b>${areaText}</b><small>${esc(p.area_definition || '')}</small></div></div><small>${esc(population.source || p.geometry_source || descriptor.source || '')}</small><div class="sub-infra" data-subdivision-infrastructure hidden></div>`;
  card.hidden = false;
  card.querySelector('[data-subdivision-close]')?.addEventListener('click', () => window.__potatoAtlasSubdivisions?.clear?.());
}
function renderInfrastructureContext(detail) {
  const card = document.getElementById('atlasSubdivisionCard');
  const section = card?.querySelector?.('[data-subdivision-infrastructure]');
  if (!section) return;
  const context = detail?.context || {};
  if (context.kind !== 'subdivision' || context.id !== selectedId) {
    section.hidden = true;
    section.innerHTML = '';
    return;
  }
  const assets = Array.isArray(detail?.assets) ? detail.assets : [];
  const tags = assets.slice(0, 6).map(asset => `<button type="button" data-infrastructure-id="${esc(asset.id)}">${esc(asset.label || asset.id)}</button>`).join('');
  const overflow = assets.length > 6 ? `<small>+${assets.length - 6} more mapped assets</small>` : '';
  section.innerHTML = assets.length
    ? `<small>Mapped physical infrastructure inside this boundary</small><div class="sub-infra-tags">${tags}</div>${overflow}<small>Spatial context only · containment does not imply dependency.</small>`
    : `<small>No point assets from the current infrastructure registry are mapped inside this boundary.</small><small>Missing map coverage is unknown, not zero.</small>`;
  section.hidden = false;
}
function hideInspector() {
  const card = document.getElementById('atlasSubdivisionCard');
  if (card) card.hidden = true;
}
async function subdivisionIndex() {
  if (!indexPromise) {
    indexPromise = fetch(INDEX_URL, {cache:'force-cache'}).then(response => {
      if (!response.ok) throw new Error(`Subdivision index unavailable (${response.status})`);
      return response.json();
    });
  }
  return indexPromise;
}
function descriptorEntries(index) {
  return Object.entries(index?.partitions || {}).filter(([, descriptor]) => descriptor?.path);
}
function partitionForId(index, id) {
  const value = String(id || '');
  return descriptorEntries(index)
    .filter(([, descriptor]) => descriptor?.id_prefix && value.startsWith(String(descriptor.id_prefix)))
    .sort((a,b) => String(b[1].id_prefix).length - String(a[1].id_prefix).length)[0] || null;
}
function viewportOverlaps(bounds) {
  if (!bounds || ![bounds.west,bounds.east,bounds.south,bounds.north].every(Number.isFinite)) return false;
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
async function handSubdivisionToInfrastructure(detail) {
  try {
    if (!window.__potatoAtlasInfrastructure && window.__potatoAtlasLoadModule) {
      await window.__potatoAtlasLoadModule('Infrastructure Context', './3d-infrastructure.js');
    }
    await window.__potatoAtlasInfrastructure?.showForSubdivision?.(detail);
  } catch (error) {
    console.warn('Subdivision infrastructure context unavailable:', error);
  }
}
function selectSubdivision(partition, feature, options = {}) {
  if (!feature) return false;
  const p = feature.properties || {};
  selectedId = p.id || null;
  pendingDeepLinkId = null;
  syncUrl(selectedId);
  const bounds = geometryBounds(feature);
  if (options.fit !== false && bounds) map.fitBounds(bounds, { padding:80, duration:650, maxZoom:7.4 });
  renderInspector(feature, loaded.get(partition)?.descriptor || {});
  const detail = { partition, id:selectedId, properties:p, feature };
  window.dispatchEvent(new CustomEvent('potato-atlas-subdivision-select', { detail }));
  void handSubdivisionToInfrastructure(detail);
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
        'text-field':['step',['zoom'],['coalesce',['get','code'],['get','name']],5.8,['get','name']],
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
  if (!descriptor?.path) throw new Error(`Subdivision partition ${partition} is not available.`);
  const response = await fetch(`../data/world-subdivisions/${descriptor.path}`, {cache:'force-cache'});
  if (!response.ok) throw new Error(`Subdivision partition ${partition} unavailable (${response.status})`);
  const data = await response.json();
  if (data?.type !== 'FeatureCollection' || !Array.isArray(data.features)) throw new Error(`Subdivision partition ${partition} is not GeoJSON.`);
  const state = { descriptor, data };
  loaded.set(partition, state);
  installPartitionLayers(partition, data);
  return state;
}
async function ensureRelevantPartitions() {
  const index = await subdivisionIndex();
  const deepLinkId = pendingDeepLinkId;
  const deepLinkEntry = deepLinkId ? partitionForId(index, deepLinkId) : null;
  for (const [partition, descriptor] of descriptorEntries(index)) {
    const deepLinkTarget = deepLinkEntry?.[0] === partition;
    if (!deepLinkTarget && !viewportOverlaps(descriptor.viewport_bounds)) continue;
    try {
      await loadPartition(partition);
      if (deepLinkTarget && pendingDeepLinkId === deepLinkId) {
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
window.addEventListener('potato-atlas-infrastructure-change', event => renderInfrastructureContext(event?.detail || {}));
await ensureRelevantPartitions();

window.__potatoAtlasSubdivisions = {
  loadPartition,
  async select(id, options={}) {
    const index = await subdivisionIndex();
    const entry = partitionForId(index, id);
    if (!entry) return false;
    const [partition] = entry;
    await loadPartition(partition);
    return selectSubdivision(partition, featureById(partition, id), options);
  },
  clear() {
    const previousId = selectedId;
    selectedId = null;
    pendingDeepLinkId = null;
    syncUrl(null);
    hideInspector();
    window.dispatchEvent(new CustomEvent('potato-atlas-subdivision-clear', { detail:{ id:previousId } }));
    window.__potatoAtlasInfrastructure?.fallBackContext?.();
  },
  get selected() { return selectedId; },
  loadedPartitions() { return [...loaded.keys()]; },
};

window.dispatchEvent(new CustomEvent('potato-atlas-subdivisions-ready', { detail:{ selected:selectedId } }));
