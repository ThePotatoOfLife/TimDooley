// Lazy, scale-adaptive physical-water context for the World Map.
// The ocean color uses a seam-safe generated globe mesh below canonical land.
// Natural Earth remains the pinned source for coastline, lakes and river detail.

const map = window.__potatoAtlasMap;
if (!map) throw new Error('Physical Water requires the core map.');
if (!window.__potatoAtlasScale) await import('./3d-scale.js');
const scale = await window.__potatoAtlasScale?.ready;
if (!scale?.threshold) throw new Error('Physical Water requires the shared Scale runtime.');
if (!window.__potatoAtlasStyleLifecycle) {
  const { createStyleLifecycle } = await import('./3d-style-lifecycle.js');
  window.__potatoAtlasStyleLifecycle = createStyleLifecycle(map);
}
const styleLifecycle = window.__potatoAtlasStyleLifecycle;

const NE_SHA = 'ca96624a56bd078437bca8184e78163e5039ad19';
const NE_BASE = `https://raw.githubusercontent.com/nvkelso/natural-earth-vector/${NE_SHA}/geojson`;
const DETAIL_ZOOM = scale.threshold('physical-water-detail', 'load');
const DEFAULT_OPACITY = 0.72;
const OCEAN_SOURCE = 'atlas-physical-water-ocean-grid';
const BASE_LAYERS = {
  oceanBase: 'atlas-physical-water-ocean-grid',
  landMask: 'atlas-physical-water-land-mask',
};
const OVERVIEW_SOURCES = {
  rivers: 'atlas-physical-water-rivers-110m',
  lakes: 'atlas-physical-water-lakes-110m',
  coastline: 'atlas-physical-water-coastline-110m',
};
const DETAIL_SOURCES = {
  rivers: 'atlas-physical-water-rivers-50m',
  lakes: 'atlas-physical-water-lakes-50m',
  coastline: 'atlas-physical-water-coastline-50m',
};
const OVERVIEW_LAYERS = {
  lakeFill: 'atlas-physical-water-lake-fill-110m',
  lakeLine: 'atlas-physical-water-lake-line-110m',
  rivers: 'atlas-physical-water-river-line-110m',
  coastline: 'atlas-physical-water-coastline-line-110m',
};
const DETAIL_LAYERS = {
  lakeFill: 'atlas-physical-water-lake-fill-50m',
  lakeLine: 'atlas-physical-water-lake-line-50m',
  rivers: 'atlas-physical-water-river-line-50m',
  coastline: 'atlas-physical-water-coastline-line-50m',
};

let enabled = false;
let installed = false;
let detailInstalled = false;
let restoring = false;
let opacity = DEFAULT_OPACITY;

function registerBase() {
  const stack = window.__potatoAtlasRenderStack;
  stack?.register?.(BASE_LAYERS.oceanBase, { slot:'physical-surface', priority:8, owner:'physical.water.base' });
  stack?.register?.(BASE_LAYERS.landMask, { slot:'physical-surface', priority:9, owner:'physical.water.base' });
}
function registerGroup(layers) {
  const stack = window.__potatoAtlasRenderStack;
  stack?.register?.(layers.lakeFill, { slot:'physical-water', priority:20, owner:'physical.water.base' });
  stack?.register?.(layers.lakeLine, { slot:'physical-line', priority:20, owner:'physical.water.base' });
  stack?.register?.(layers.rivers, { slot:'physical-line', priority:24, owner:'physical.water.base' });
  stack?.register?.(layers.coastline, { slot:'physical-line', priority:29, owner:'physical.water.base' });
}
function clampOpacity(value) { return Math.max(0, Math.min(1, Number(value))); }
function opacityScale() { return DEFAULT_OPACITY ? opacity / DEFAULT_OPACITY : 1; }
function sourceUrl(name) { return `${NE_BASE}/${name}`; }
function addGeoJsonSource(id, filename) {
  if (map.getSource(id)) return;
  map.addSource(id, {
    type: 'geojson',
    data: sourceUrl(filename),
    attribution: 'Made with Natural Earth · public domain',
  });
}

function buildOceanMesh() {
  // Never create a polygon that crosses the antimeridian or touches a pole.
  // Small independent cells avoid globe triangulation folding a world-spanning
  // ring over the North Pole while remaining visually continuous at map scale.
  const longitudes = [-179.999, -120, -60, 0, 60, 120, 179.999];
  const latitudes = [-89.999, -60, -30, 0, 30, 60, 89.999];
  const features = [];
  for (let y = 0; y < latitudes.length - 1; y += 1) {
    for (let x = 0; x < longitudes.length - 1; x += 1) {
      const west = longitudes[x];
      const east = longitudes[x + 1];
      const south = latitudes[y];
      const north = latitudes[y + 1];
      features.push({
        type:'Feature',
        properties:{ cell:`${x}-${y}` },
        geometry:{
          type:'Polygon',
          coordinates:[[[west,south],[east,south],[east,north],[west,north],[west,south]]],
        },
      });
    }
  }
  return { type:'FeatureCollection', features };
}

function ensureOceanSource() {
  if (map.getSource(OCEAN_SOURCE)) return;
  map.addSource(OCEAN_SOURCE, {
    type:'geojson',
    data:buildOceanMesh(),
    buffer: 0,
  });
}
function ensureSources() {
  ensureOceanSource();
  addGeoJsonSource(OVERVIEW_SOURCES.rivers, 'ne_110m_rivers_lake_centerlines.geojson');
  addGeoJsonSource(OVERVIEW_SOURCES.lakes, 'ne_110m_lakes.geojson');
  addGeoJsonSource(OVERVIEW_SOURCES.coastline, 'ne_110m_coastline.geojson');
}
function ensureDetailSources() {
  addGeoJsonSource(DETAIL_SOURCES.rivers, 'ne_50m_rivers_lake_centerlines.geojson');
  addGeoJsonSource(DETAIL_SOURCES.lakes, 'ne_50m_lakes.geojson');
  addGeoJsonSource(DETAIL_SOURCES.coastline, 'ne_50m_coastline.geojson');
}
function addLayer(definition, before) {
  if (map.getLayer(definition.id)) return;
  map.addLayer(definition, before && map.getLayer(before) ? before : undefined);
}

function ensureBaseLayers() {
  const beforeCountry = map.getLayer('countries-fill') ? 'countries-fill' : undefined;
  addLayer({
    id:BASE_LAYERS.oceanBase,
    type:'fill',
    source:OCEAN_SOURCE,
    layout:{visibility:'none'},
    paint:{'fill-color':'#426f86','fill-opacity':0.36},
  }, beforeCountry);
  if (map.getSource('countries')) {
    addLayer({
      id:BASE_LAYERS.landMask,
      type:'fill',
      source:'countries',
      layout:{visibility:'none'},
      paint:{'fill-color':'#080b0b','fill-opacity':1},
    }, beforeCountry);
  }
  registerBase();
}

function waterLayers(sources, layers, detail = false) {
  const beforeLine = map.getLayer('countries-line') ? 'countries-line' : undefined;
  // Scale ownership lives in syncScaleDetail(). Do not also put DETAIL_ZOOM on
  // MapLibre's native minzoom: zoomend switching plus native minzoom can leave a
  // transient frame where neither overview nor detail water is drawable.
  const minZoom = 0;
  addLayer({id:layers.lakeFill,type:'fill',source:sources.lakes,minzoom:minZoom,layout:{visibility:'none'},paint:{'fill-color':'#6a9db4','fill-opacity':detail ? 0.64 : 0.58}}, beforeLine);
  addLayer({id:layers.lakeLine,type:'line',source:sources.lakes,minzoom:minZoom,layout:{visibility:'none'},paint:{'line-color':'#a7d3e4','line-opacity':0.86,'line-width':['interpolate',['linear'],['zoom'],0,0.35,5,detail?1.05:0.9]}}, beforeLine);
  addLayer({id:layers.rivers,type:'line',source:sources.rivers,minzoom:minZoom,layout:{visibility:'none','line-cap':'round','line-join':'round'},paint:{'line-color':'#7fb8d0','line-opacity':0.88,'line-width':['interpolate',['linear'],['zoom'],0,0.35,3,0.7,6,detail?1.35:1.15]}}, beforeLine);
  addLayer({id:layers.coastline,type:'line',source:sources.coastline,minzoom:minZoom,layout:{visibility:'none'},paint:{'line-color':'#b2d8e6','line-opacity':detail?0.8:0.72,'line-width':['interpolate',['linear'],['zoom'],0,0.3,5,detail?1.0:0.78]}}, beforeLine);
  registerGroup(layers);
}

function applyBaseOpacity() {
  const scale = opacityScale();
  const oceanBase = (map.getZoom() >= DETAIL_ZOOM ? 0.42 : 0.36) * scale;
  if (map.getLayer(BASE_LAYERS.oceanBase)) map.setPaintProperty(BASE_LAYERS.oceanBase, 'fill-opacity', Math.min(1, oceanBase));
  if (map.getLayer(BASE_LAYERS.landMask)) map.setPaintProperty(BASE_LAYERS.landMask, 'fill-opacity', 1);
}
function applyGroupOpacity(layers, detail = false) {
  const scale = opacityScale();
  const values = {
    lakeFill:(detail ? 0.64 : 0.58) * scale,
    lakeLine:0.86 * scale,
    rivers:0.88 * scale,
    coastline:(detail ? 0.8 : 0.72) * scale,
  };
  if (map.getLayer(layers.lakeFill)) map.setPaintProperty(layers.lakeFill, 'fill-opacity', Math.min(1, values.lakeFill));
  for (const key of ['lakeLine','rivers','coastline']) {
    if (map.getLayer(layers[key])) map.setPaintProperty(layers[key], 'line-opacity', Math.min(1, values[key]));
  }
}
function applyOpacity() {
  if (installed) {
    applyBaseOpacity();
    applyGroupOpacity(OVERVIEW_LAYERS, false);
  }
  if (detailInstalled) applyGroupOpacity(DETAIL_LAYERS, true);
}
function setOpacity(value) {
  opacity = clampOpacity(value);
  applyOpacity();
  return true;
}
function getOpacity() { return opacity; }

function ensureLayers() {
  ensureBaseLayers();
  waterLayers(OVERVIEW_SOURCES, OVERVIEW_LAYERS, false);
  installed = true;
  applyOpacity();
}
function ensureDetailLayers() {
  waterLayers(DETAIL_SOURCES, DETAIL_LAYERS, true);
  detailInstalled = true;
  applyGroupOpacity(DETAIL_LAYERS, true);
}
function setLayerGroupVisibility(layers, visibility) {
  for (const id of Object.values(layers)) if (map.getLayer(id)) map.setLayoutProperty(id, 'visibility', visibility);
}
function syncScaleDetail() {
  if (!enabled) return;
  setLayerGroupVisibility(BASE_LAYERS, 'visible');
  const detail = map.getZoom() >= DETAIL_ZOOM;
  if (detail) {
    ensureDetailSources();
    ensureDetailLayers();
    setLayerGroupVisibility(OVERVIEW_LAYERS, 'none');
    setLayerGroupVisibility(DETAIL_LAYERS, 'visible');
  } else {
    setLayerGroupVisibility(OVERVIEW_LAYERS, 'visible');
    if (detailInstalled) setLayerGroupVisibility(DETAIL_LAYERS, 'none');
  }
  applyOpacity();
}

async function enable() {
  if (enabled) return true;
  try {
    ensureSources();
    ensureLayers();
    enabled = true;
    syncScaleDetail();
    return true;
  } catch (error) {
    console.warn('Physical Water unavailable; ordinary map remains active.', error);
    enabled = false;
    return false;
  }
}
async function disable() {
  if (installed) {
    setLayerGroupVisibility(BASE_LAYERS, 'none');
    setLayerGroupVisibility(OVERVIEW_LAYERS, 'none');
  }
  if (detailInstalled) setLayerGroupVisibility(DETAIL_LAYERS, 'none');
  enabled = false;
  return true;
}
async function toggle() { return enabled ? disable() : enable(); }

map.on('zoomend', () => {
  if (!enabled) return;
  try { syncScaleDetail(); }
  catch (error) { console.warn('Physical Water detail unavailable at this zoom.', error); }
});
styleLifecycle.register('physical-water', {
  priority:40,
  restore:() => {
    if (!enabled || restoring) return;
    restoring = true;
    queueMicrotask(() => {
      try {
        ensureSources();
        ensureLayers();
        detailInstalled = Boolean(map.getSource(DETAIL_SOURCES.coastline));
        syncScaleDetail();
        applyOpacity();
      } catch (error) {
        console.warn('Physical Water could not restore after style change.', error);
      } finally {
        restoring = false;
      }
    });
  },
});

window.__potatoAtlasPhysicalWater = {
  get enabled() { return enabled; },
  get detailInstalled() { return detailInstalled; },
  enable,
  disable,
  toggle,
  setOpacity,
  getOpacity,
};
