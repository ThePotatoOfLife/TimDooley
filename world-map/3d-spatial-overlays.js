// Spatial overlays are independent from analytical country layers.
// They intentionally preserve overlap between sacred, textual, historical,
// ideological, current/disputed and conflict-context geography.

const map = window.__potatoAtlasMap;
if (!map) throw new Error('Spatial overlays require the core atlas map.');
const interaction = window.__potatoAtlasInteraction;

const MANIFEST_URL = '../data/world-map-spatial-overlays.json';
const ACTIVE_PARAM = 'overlays';
const Z_ORDER = [
  'historical_reconstruction',
  'project_interpretive',
  'textual_reconstruction',
  'political_ideology',
  'current_observed',
  'current_disputed',
  'humanitarian_observed',
  'event_observed',
];

const STYLE = {
  historical_reconstruction: { fill:'#9f8b6d', fillOpacity:.16, line:'#c5ad82', width:1.6, dash:[3,2] },
  project_interpretive: { fill:'#d6b56d', fillOpacity:.13, line:'#e0bd78', width:2.0, dash:[2,2] },
  textual_reconstruction: { fill:'#967bb9', fillOpacity:.13, line:'#b49bd1', width:1.9, dash:[1,2] },
  political_ideology: { fill:'#c27878', fillOpacity:.12, line:'#d79898', width:2.0, dash:[5,2] },
  current_observed: { fill:'#73a7d8', fillOpacity:.10, line:'#9bc5ea', width:1.8, dash:null },
  current_disputed: { fill:'#d38b62', fillOpacity:.10, line:'#e7a77f', width:2.0, dash:[3,2] },
  humanitarian_observed: { fill:'#88ad89', fillOpacity:.12, line:'#a8cca9', width:1.8, dash:[2,1] },
  event_observed: { fill:'#d06c6c', fillOpacity:.08, line:'#e39a9a', width:1.8, dash:null },
};

let manifest = null;
const byId = new Map();
const activeIds = new Set();
const ownerCache = new Map();
const rendered = new Map();
let loadError = null;

function safeId(value) {
  return String(value).replace(/[^a-zA-Z0-9_-]+/g, '-');
}
function sourceUrl(owner) {
  if (/^(https?:)?\/\//.test(owner)) return owner;
  return owner.startsWith('data/') ? `../${owner}` : owner;
}
function entry(id) { return byId.get(id) || null; }
function available(id) { return entry(id)?.availability === 'current'; }
function layerIdsFor(id) { return rendered.get(id)?.layerIds || []; }
function emit(reason='change', extra={}) {
  window.dispatchEvent(new CustomEvent('potato-atlas-spatial-overlay-change', {
    detail: {
      reason,
      active:[...activeIds],
      entries:[...activeIds].map(entry).filter(Boolean),
      ...extra,
    },
  }));
}
function persist() {
  const url = new URL(location.href);
  const ids = [...activeIds].filter(available).sort();
  if (ids.length) url.searchParams.set(ACTIVE_PARAM, ids.join(','));
  else url.searchParams.delete(ACTIVE_PARAM);
  history.replaceState({}, '', url);
}
function normalizeManifest(data) {
  byId.clear();
  manifest = data;
  for (const row of data?.entries || []) byId.set(row.id, Object.freeze({ ...row }));
}
async function loadOwner(owner) {
  if (ownerCache.has(owner)) return ownerCache.get(owner);
  const promise = (async () => {
    const response = await fetch(sourceUrl(owner), { cache:'no-cache' });
    if (!response.ok) throw new Error(`${response.status} ${owner}`);
    const data = await response.json();
    if (data?.type !== 'FeatureCollection') throw new Error(`${owner} is not a FeatureCollection`);
    return data;
  })();
  ownerCache.set(owner, promise);
  return promise;
}
function featureCollectionFor(row, owner) {
  const wanted = new Set(row.feature_ids || []);
  return {
    type:'FeatureCollection',
    features:(owner.features || []).filter(feature => wanted.has(feature?.properties?.feature_id)),
  };
}
function geometryKinds(fc) {
  const kinds = new Set();
  for (const feature of fc.features || []) {
    const type = feature?.geometry?.type || '';
    if (type.includes('Polygon')) kinds.add('polygon');
    else if (type.includes('LineString')) kinds.add('line');
    else if (type.includes('Point')) kinds.add('point');
  }
  return kinds;
}
function beforeLayerId() {
  // Compatibility fallback only; Render Stack owns final semantic ordering.
  return map.getLayer('country-labels') ? 'country-labels' : undefined;
}
function addMapLayer(definition, beforeId) {
  if (beforeId && map.getLayer(beforeId)) map.addLayer(definition, beforeId);
  else map.addLayer(definition);
}
function registerRenderedLayers(row, layerIds) {
  const stack = window.__potatoAtlasRenderStack;
  layerIds.forEach((layerId, index) => stack?.register?.(layerId, {
    slot:'geography-context',
    priority:100 + index,
    owner:`spatial-overlays:${row.id}`,
  }));
}
function handleSpatialFeatureClick(event) {
  emit('feature-click', { point:event.point, lngLat:event.lngLat, features:featuresAt(event.point) });
}
function bindFallbackInteraction(layerIds) {
  for (const id of layerIds) {
    map.on('mouseenter', id, () => { map.getCanvas().style.cursor = 'pointer'; });
    map.on('mouseleave', id, () => { map.getCanvas().style.cursor = ''; });
    map.on('click', id, event => {
      if (event?.originalEvent) event.originalEvent.__potatoAtlasOverlayHandled = true;
      handleSpatialFeatureClick(event);
    });
  }
}
function syncInteractionRegistration() {
  if (!interaction?.register) return false;
  const layers = [...rendered.values()].flatMap(state => state.layerIds || []).filter(layerId => map.getLayer(layerId));
  if (!layers.length) {
    interaction.unregister?.('spatial-overlays');
    return false;
  }
  interaction.register('spatial-overlays', {
    layers,
    objectType:'spatial-overlay',
    clickPriority:40,
    hoverPriority:40,
    cursor:'pointer',
    onClick:event => emit('feature-click', { point:event.point, lngLat:event.lngLat, features:featuresAt(event.point) }),
  });
  return true;
}
function installRenderedLayers(row, fc) {
  const token = safeId(row.id);
  const sourceId = `atlas-spatial-${token}`;
  const layerIds = [];
  const style = STYLE[row.epistemic_type] || STYLE.project_interpretive;
  if (!map.getSource(sourceId)) map.addSource(sourceId, { type:'geojson', data:fc });
  const kinds = geometryKinds(fc);
  const beforeId = beforeLayerId();

  if (kinds.has('polygon')) {
    const fillId = `${sourceId}-fill`;
    const lineId = `${sourceId}-line`;
    addMapLayer({
      id:fillId, type:'fill', source:sourceId,
      paint:{'fill-color':style.fill,'fill-opacity':style.fillOpacity},
      metadata:{atlasSpatialOverlay:row.id, epistemic_type:row.epistemic_type},
    }, beforeId);
    const linePaint = {'line-color':style.line,'line-width':style.width,'line-opacity':.92};
    if (style.dash) linePaint['line-dasharray'] = style.dash;
    addMapLayer({
      id:lineId, type:'line', source:sourceId, paint:linePaint,
      metadata:{atlasSpatialOverlay:row.id, epistemic_type:row.epistemic_type},
    }, beforeId);
    layerIds.push(fillId,lineId);
  }
  if (kinds.has('line')) {
    const lineId = `${sourceId}-route`;
    const linePaint = {'line-color':style.line,'line-width':Math.max(style.width,2.2),'line-opacity':.92};
    if (style.dash) linePaint['line-dasharray'] = style.dash;
    addMapLayer({
      id:lineId, type:'line', source:sourceId, paint:linePaint,
      metadata:{atlasSpatialOverlay:row.id, epistemic_type:row.epistemic_type},
    }, beforeId);
    layerIds.push(lineId);
  }
  if (kinds.has('point')) {
    const pointId = `${sourceId}-point`;
    addMapLayer({
      id:pointId, type:'circle', source:sourceId,
      paint:{'circle-radius':6,'circle-color':style.line,'circle-stroke-color':'#0b1010','circle-stroke-width':1.3,'circle-opacity':.9},
      metadata:{atlasSpatialOverlay:row.id, epistemic_type:row.epistemic_type},
    }, beforeId);
    layerIds.push(pointId);
  }

  registerRenderedLayers(row, layerIds);
  rendered.set(row.id, { sourceId, layerIds });
  if (!syncInteractionRegistration()) bindFallbackInteraction(layerIds);
}
async function ensureRendered(id) {
  const row = entry(id);
  if (!row || row.availability !== 'current') return false;
  if (rendered.has(id)) {
    registerRenderedLayers(row, layerIdsFor(id));
    syncInteractionRegistration();
    return true;
  }
  const owner = await loadOwner(row.geometry_owner);
  const fc = featureCollectionFor(row, owner);
  if (!fc.features.length) throw new Error(`Spatial overlay ${id} has no matching geometry features.`);
  installRenderedLayers(row, fc);
  return true;
}
function setVisibility(id, visible) {
  for (const layerId of layerIdsFor(id)) {
    if (map.getLayer(layerId)) map.setLayoutProperty(layerId, 'visibility', visible ? 'visible' : 'none');
  }
}
async function activate(id, { silent=false }={}) {
  const row = entry(id);
  if (!row || row.availability !== 'current') return false;
  await ensureRendered(id);
  activeIds.add(id);
  setVisibility(id, true);
  if (!silent) { persist(); emit('activate'); }
  return true;
}
function deactivate(id, { silent=false }={}) {
  const changed = activeIds.delete(id);
  if (rendered.has(id)) setVisibility(id, false);
  if (changed && !silent) { persist(); emit('deactivate'); }
  return changed;
}
async function toggle(id) {
  if (activeIds.has(id)) return deactivate(id);
  return activate(id);
}
function reset({ silent=false }={}) {
  for (const id of [...activeIds]) deactivate(id, { silent:true });
  if (!silent) { persist(); emit('reset'); }
}
function entries(family=null, { availableOnly=false }={}) {
  let rows = [...byId.values()];
  if (family) rows = rows.filter(row => row.family === family);
  if (availableOnly) rows = rows.filter(row => row.availability === 'current');
  return rows;
}
function featuresAt(point) {
  const layerIds = [...activeIds].flatMap(layerIdsFor).filter(layerId => map.getLayer(layerId));
  if (!layerIds.length || !point) return [];
  const rows = map.queryRenderedFeatures(point, { layers:layerIds }) || [];
  const seen = new Set();
  return rows.map(feature => {
    const overlayId = feature?.properties?.overlay_id;
    const featureId = feature?.properties?.feature_id;
    const key = `${overlayId}|${featureId}`;
    if (!overlayId || seen.has(key)) return null;
    seen.add(key);
    const row = entry(overlayId);
    let sourceIds = feature?.properties?.source_ids;
    try { if (typeof sourceIds === 'string' && sourceIds.startsWith('[')) sourceIds = JSON.parse(sourceIds); } catch {}
    return {
      overlay_id:overlayId,
      overlay:row,
      feature_id:featureId,
      label:feature?.properties?.label || row?.label || overlayId,
      epistemic_type:feature?.properties?.epistemic_type || row?.epistemic_type,
      confidence:feature?.properties?.confidence || row?.confidence,
      status_note:feature?.properties?.status_note || row?.status_note,
      geometry_version:feature?.properties?.geometry_version || null,
      measurement_policy:feature?.properties?.measurement_policy || null,
      source_ids:Array.isArray(sourceIds) ? sourceIds : row?.source_ids || [],
    };
  }).filter(Boolean).sort((a,b) => Z_ORDER.indexOf(b.epistemic_type) - Z_ORDER.indexOf(a.epistemic_type));
}
function boundsForFeature(feature) {
  let minX=180,minY=90,maxX=-180,maxY=-90,ok=false;
  const walk = value => {
    if (!Array.isArray(value)) return;
    if (typeof value[0] === 'number' && typeof value[1] === 'number') {
      ok=true; minX=Math.min(minX,value[0]); minY=Math.min(minY,value[1]); maxX=Math.max(maxX,value[0]); maxY=Math.max(maxY,value[1]); return;
    }
    value.forEach(walk);
  };
  walk(feature?.geometry?.coordinates);
  return ok ? [[minX,minY],[maxX,maxY]] : null;
}
async function fit(id) {
  const row = entry(id);
  if (!row) return false;
  const owner = await loadOwner(row.geometry_owner);
  const fc = featureCollectionFor(row, owner);
  let minX=180,minY=90,maxX=-180,maxY=-90,ok=false;
  for (const feature of fc.features) {
    const bounds=boundsForFeature(feature); if(!bounds) continue;
    ok=true; minX=Math.min(minX,bounds[0][0]); minY=Math.min(minY,bounds[0][1]); maxX=Math.max(maxX,bounds[1][0]); maxY=Math.max(maxY,bounds[1][1]);
  }
  if (ok) map.fitBounds([[minX,minY],[maxX,maxY]], { padding:70, maxZoom:7, duration:650 });
  return ok;
}
async function restoreFromUrl() {
  const requested = (new URL(location.href).searchParams.get(ACTIVE_PARAM) || '').split(',').map(value => value.trim()).filter(Boolean);
  for (const id of requested) await activate(id, { silent:true });
  persist();
}

async function load() {
  try {
    const response = await fetch(MANIFEST_URL, { cache:'no-cache' });
    if (!response.ok) throw new Error(`${response.status} ${MANIFEST_URL}`);
    normalizeManifest(await response.json());
    await restoreFromUrl();
    emit('ready');
    return manifest;
  } catch (error) {
    loadError = error;
    console.warn('Spatial overlay registry unavailable:', error);
    window.dispatchEvent(new CustomEvent('potato-atlas-spatial-overlay-error', { detail:{ message:error?.message || String(error) } }));
    return null;
  }
}

const ready = load();
window.__potatoAtlasSpatialOverlays = {
  ready,
  get manifest(){ return manifest; },
  get error(){ return loadError; },
  get:entry,
  entries,
  active(){ return [...activeIds]; },
  isActive(id){ return activeIds.has(id); },
  activate,
  deactivate,
  toggle,
  reset,
  fit,
  featuresAt,
};

export { ready };
