// Lazy regional physical hydrology for the World Map.
// HydroBASINS/HydroRIVERS requests are viewport-bounded and are not issued
// below regional zoom. This layer is physical drainage context only.

const map = window.__potatoAtlasMap;
if (!map) throw new Error('Hydrology requires the core map.');
if (!window.__potatoAtlasStyleLifecycle) {
  const { createStyleLifecycle } = await import('./3d-style-lifecycle.js');
  window.__potatoAtlasStyleLifecycle = createStyleLifecycle(map);
}
const styleLifecycle = window.__potatoAtlasStyleLifecycle;

const PHYSICAL_ID = 'physical.water.hydrology';
const MIN_ZOOM = 4;
const DEFAULT_OPACITY = 0.72;
const BASIN_SERVICE = 'https://services3.arcgis.com/AdYB7LvDmN7hzWUb/arcgis/rest/services/Hydrobasins/FeatureServer/2/query';
const RIVER_SERVICE = 'https://maps.fsc.org/server/rest/services/hosted/Optimized_Hyrdo/FeatureServer/0/query';
const COMMON_QUERY = '&geometryType=esriGeometryEnvelope&spatialRel=esriSpatialRelIntersects&inSR=4326&outSR=4326&returnGeometry=true&f=geojson&resultRecordCount=2000';

const BASIN_SOURCE = 'atlas-hydrology-basins';
const RIVER_SOURCE = 'atlas-hydrology-rivers';
const BASIN_FILL = 'atlas-hydrology-basin-fill';
const BASIN_LINE = 'atlas-hydrology-basin-line';
const RIVER_LINE = 'atlas-hydrology-river-line';
const STATUS_ID = 'atlasHydrologyStatus';
const BASE_BASIN_FILL_OPACITY = 0.055;
const BASE_BASIN_LINE_OPACITY = 0.52;
const BASE_RIVER_OPACITY = 0.9;

const EMPTY = () => ({ type:'FeatureCollection', features:[] });
let enabled = false;
let controller = null;
let requestSerial = 0;
let activeRequestKey = null;
let completedRequestKey = null;
let refreshScheduled = false;
let restoring = false;
let lastBasins = EMPTY();
let lastRivers = EMPTY();
let opacity = DEFAULT_OPACITY;

function diagnostics() {
  if (!window.__potatoAtlasDiagnostics) return null;
  const d = window.__potatoAtlasDiagnostics;
  if (!Number.isFinite(d.hydrologyRequests)) d.hydrologyRequests = 0;
  if (!Number.isFinite(d.hydrologyDeduplicatedRefreshes)) d.hydrologyDeduplicatedRefreshes = 0;
  if (!Number.isFinite(d.hydrologyAbortedRequests)) d.hydrologyAbortedRequests = 0;
  return d;
}
function registerLayers() {
  const stack = window.__potatoAtlasRenderStack;
  stack?.register?.(BASIN_FILL, { slot:'physical-surface', priority:50, owner:PHYSICAL_ID });
  stack?.register?.(BASIN_LINE, { slot:'physical-line', priority:50, owner:PHYSICAL_ID });
  stack?.register?.(RIVER_LINE, { slot:'physical-line', priority:60, owner:PHYSICAL_ID });
}
function clampOpacity(value) { return Math.max(0, Math.min(1, Number(value))); }
function opacityScale() { return DEFAULT_OPACITY ? opacity / DEFAULT_OPACITY : 1; }
function applyOpacity() {
  const scale = opacityScale();
  if (map.getLayer(BASIN_FILL)) map.setPaintProperty(BASIN_FILL, 'fill-opacity', Math.min(1, BASE_BASIN_FILL_OPACITY * scale));
  if (map.getLayer(BASIN_LINE)) map.setPaintProperty(BASIN_LINE, 'line-opacity', Math.min(1, BASE_BASIN_LINE_OPACITY * scale));
  if (map.getLayer(RIVER_LINE)) map.setPaintProperty(RIVER_LINE, 'line-opacity', Math.min(1, BASE_RIVER_OPACITY * scale));
}
function setOpacity(value) {
  opacity = clampOpacity(value);
  applyOpacity();
  return true;
}
function getOpacity() { return opacity; }
function reportStatus(phase, message) {
  window.dispatchEvent(new CustomEvent('potato-atlas-physical-layer-status', {
    detail:{ id:PHYSICAL_ID, phase, message }
  }));
}

function ensureStatus() {
  let status = document.getElementById(STATUS_ID);
  if (!status) {
    status = document.createElement('div');
    status.id = STATUS_ID;
    status.hidden = true;
    status.style.cssText = 'background:#080b0be8;border:1px solid #344343;border-radius:999px;padding:5px 9px;color:#b9dce8;font:700 9px/1.2 system-ui;letter-spacing:.04em;backdrop-filter:blur(8px)';
    document.querySelector('.mapwrap')?.appendChild(status);
  }
  const layout = window.__potatoAtlasUILayout;
  if (layout && !layout.getState?.().some(row => row.id === 'hydrology-status')) {
    layout.register({ id:'hydrology-status', zone:'left-status', element:status, priority:14 });
  }
  return status;
}

function setStatus(text, visible = enabled) {
  const status = ensureStatus();
  status.textContent = text;
  status.hidden = !visible;
  window.__potatoAtlasUILayout?.setVisible?.('hydrology-status', visible);
}

function ensureSources() {
  if (!map.getSource(BASIN_SOURCE)) map.addSource(BASIN_SOURCE, { type:'geojson', data:lastBasins, attribution:'HydroSHEDS · HydroBASINS · Lehner & Grill (2013)' });
  if (!map.getSource(RIVER_SOURCE)) map.addSource(RIVER_SOURCE, { type:'geojson', data:lastRivers, attribution:'HydroSHEDS · HydroRIVERS · Lehner & Grill (2013)' });
}

function ensureLayers() {
  const beforeFill = map.getLayer('countries-fill') ? 'countries-fill' : undefined;
  const beforeLine = map.getLayer('countries-line') ? 'countries-line' : undefined;
  if (!map.getLayer(BASIN_FILL)) map.addLayer({id:BASIN_FILL,type:'fill',source:BASIN_SOURCE,layout:{visibility:'none'},paint:{'fill-color':'#4b8392','fill-opacity':BASE_BASIN_FILL_OPACITY}}, beforeFill);
  if (!map.getLayer(BASIN_LINE)) map.addLayer({id:BASIN_LINE,type:'line',source:BASIN_SOURCE,layout:{visibility:'none'},paint:{'line-color':'#69a5b3','line-opacity':BASE_BASIN_LINE_OPACITY,'line-width':['interpolate',['linear'],['zoom'],4,0.55,8,1.15]}}, beforeLine);
  if (!map.getLayer(RIVER_LINE)) map.addLayer({id:RIVER_LINE,type:'line',source:RIVER_SOURCE,layout:{visibility:'none','line-cap':'round','line-join':'round'},paint:{'line-color':'#67b8da','line-opacity':BASE_RIVER_OPACITY,'line-width':['interpolate',['linear'],['zoom'],4,0.55,6,0.9,9,1.35]}}, beforeLine);
  registerLayers();
  applyOpacity();
}

function setVisibility(visibility) {
  for (const id of [BASIN_FILL, BASIN_LINE, RIVER_LINE]) if (map.getLayer(id)) map.setLayoutProperty(id, 'visibility', visibility);
}
function clearData() {
  lastBasins = EMPTY();
  lastRivers = EMPTY();
  completedRequestKey = null;
  map.getSource(BASIN_SOURCE)?.setData(lastBasins);
  map.getSource(RIVER_SOURCE)?.setData(lastRivers);
}
function riverThreshold() {
  const zoom = map.getZoom();
  if (zoom < 5.2) return 5000;
  if (zoom < 6.7) return 1500;
  if (zoom < 8.2) return 500;
  return 150;
}
function viewportEnvelope() {
  const bounds = map.getBounds();
  const west = Math.max(-180, bounds.getWest());
  const east = Math.min(180, bounds.getEast());
  const south = Math.max(-85, bounds.getSouth());
  const north = Math.min(85, bounds.getNorth());
  if (!(east > west && north > south)) return null;
  return `${west},${south},${east},${north}`;
}
function hydrologyRequestKey(envelope, threshold, zoom) {
  const rounded = String(envelope || '').split(',').map(value => Number(value).toFixed(2)).join(',');
  const regime = zoom < 5.2 ? 'regional' : zoom < 6.7 ? 'subregional' : zoom < 8.2 ? 'local' : 'detailed';
  return `${regime}|${threshold}|${rounded}`;
}
function shouldSkipHydrologyRequest(requestKey) {
  return Boolean(requestKey && (requestKey === activeRequestKey || requestKey === completedRequestKey));
}
function queryUrl(service, where, fields, envelope) {
  return `${service}?where=${encodeURIComponent(where)}&outFields=${encodeURIComponent(fields)}&geometry=${encodeURIComponent(envelope)}${COMMON_QUERY}`;
}
async function fetchGeoJSON(url, signal) {
  const response = await fetch(url, { signal, cache:'no-store' });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const data = await response.json();
  if (data?.error) throw new Error(data.error.message || 'ArcGIS query failed');
  if (data?.type !== 'FeatureCollection' || !Array.isArray(data.features)) throw new Error('Unexpected GeoJSON response');
  return data;
}

async function refreshViewport() {
  if (!enabled) return;
  const zoom = map.getZoom();
  if (zoom < MIN_ZOOM) {
    if (controller && activeRequestKey) diagnostics() && (diagnostics().hydrologyAbortedRequests += 1);
    controller?.abort();
    controller = null;
    activeRequestKey = null;
    clearData();
    setStatus('Hydrology · zoom in to regional scale');
    reportStatus('zoom-needed', 'Zoom in to regional scale');
    return;
  }
  const envelope = viewportEnvelope();
  if (!envelope) {
    setStatus('Hydrology · viewport crosses unsupported wrap');
    reportStatus('error', 'Viewport crosses unsupported wrap');
    return;
  }

  const threshold = riverThreshold();
  const requestKey = hydrologyRequestKey(envelope, threshold, zoom);
  if (shouldSkipHydrologyRequest(requestKey)) {
    const d = diagnostics();
    if (d) d.hydrologyDeduplicatedRefreshes += 1;
    return;
  }
  if (controller && activeRequestKey) {
    const d = diagnostics();
    if (d) d.hydrologyAbortedRequests += 1;
    controller.abort();
  }
  controller = new AbortController();
  activeRequestKey = requestKey;
  const d = diagnostics();
  if (d) d.hydrologyRequests += 1;
  const serial = ++requestSerial;
  const loadingMessage = `Loading regional drainage ≥ ${threshold.toLocaleString()} km² catchments`;
  setStatus(`Hydrology · ${loadingMessage.toLowerCase()}`);
  reportStatus('loading', loadingMessage);

  const basinUrl = queryUrl(BASIN_SERVICE, '1=1', '*', envelope);
  const riverUrl = queryUrl(RIVER_SERVICE, `catch_skm>=${threshold}`, 'hyriv_id,main_riv,length_km,catch_skm,dis_av_cms,ord_stra', envelope);
  const [basins, rivers] = await Promise.allSettled([
    fetchGeoJSON(basinUrl, controller.signal),
    fetchGeoJSON(riverUrl, controller.signal),
  ]);
  if (serial !== requestSerial || !enabled) return;

  let failures = 0;
  if (basins.status === 'fulfilled') {
    lastBasins = basins.value;
    map.getSource(BASIN_SOURCE)?.setData(lastBasins);
  } else if (basins.reason?.name !== 'AbortError') {
    failures += 1;
    console.warn('HydroBASINS regional query unavailable:', basins.reason);
  }
  if (rivers.status === 'fulfilled') {
    lastRivers = rivers.value;
    map.getSource(RIVER_SOURCE)?.setData(lastRivers);
  } else if (rivers.reason?.name !== 'AbortError') {
    failures += 1;
    console.warn('HydroRIVERS regional query unavailable:', rivers.reason);
  }

  if (serial === requestSerial) {
    activeRequestKey = null;
    controller = null;
    if (failures < 2 || lastBasins.features.length || lastRivers.features.length) completedRequestKey = requestKey;
  }

  setVisibility('visible');
  applyOpacity();
  const basinCount = lastBasins.features.length;
  const riverCount = lastRivers.features.length;
  if (failures >= 2 && !basinCount && !riverCount) {
    setStatus('Hydrology · regional provider unavailable');
    reportStatus('error', 'Regional providers unavailable');
    return;
  }
  if (failures) {
    const message = `${basinCount} basins · ${riverCount} major river segments`;
    setStatus(`Hydrology · partial regional data · ${message}`);
    reportStatus('partial', message);
  } else {
    const message = `${basinCount} basins · ${riverCount} major river segments`;
    setStatus(`Hydrology · ${message}`);
    reportStatus('active', message);
  }
}

function scheduleRefresh() {
  if (!enabled || refreshScheduled) return;
  refreshScheduled = true;
  queueMicrotask(() => {
    refreshScheduled = false;
    refreshViewport().catch(error => {
      activeRequestKey = null;
      controller = null;
      if (error?.name === 'AbortError') return;
      console.warn('Regional hydrology unavailable:', error);
      setStatus('Hydrology · regional provider unavailable');
      reportStatus('error', error?.message || 'Regional provider unavailable');
    });
  });
}

async function enable() {
  ensureSources();
  ensureLayers();
  enabled = true;
  setVisibility('visible');
  applyOpacity();
  if (map.getZoom() < MIN_ZOOM) {
    setStatus('Hydrology · zoom in to regional scale');
    reportStatus('zoom-needed', 'Zoom in to regional scale');
  } else {
    setStatus('Hydrology · loading regional drainage');
    reportStatus('loading', 'Loading regional drainage');
  }
  scheduleRefresh();
  return true;
}
async function disable() {
  if (controller && activeRequestKey) {
    const d = diagnostics();
    if (d) d.hydrologyAbortedRequests += 1;
  }
  controller?.abort();
  controller = null;
  activeRequestKey = null;
  requestSerial += 1;
  setVisibility('none');
  enabled = false;
  setStatus('', false);
  return true;
}
async function toggle() { return enabled ? disable() : enable(); }

map.on('moveend', scheduleRefresh);
map.on('zoomend', scheduleRefresh);
styleLifecycle.register('physical-hydrology', {
  priority:50,
  restore:() => {
    if (!enabled || restoring) return;
    restoring = true;
    queueMicrotask(() => {
      try {
        ensureSources();
        ensureLayers();
        setVisibility('visible');
        applyOpacity();
        map.getSource(BASIN_SOURCE)?.setData(lastBasins);
        map.getSource(RIVER_SOURCE)?.setData(lastRivers);
        scheduleRefresh();
      } finally {
        restoring = false;
      }
    });
  },
});

window.__potatoAtlasHydrology = {
  get enabled() { return enabled; },
  refresh:refreshViewport,
  enable,
  disable,
  toggle,
  setOpacity,
  getOpacity,
};
