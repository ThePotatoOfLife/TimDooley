// Lazy, scale-adaptive Natural Earth physical-water context for the World Map.
// This module is imported only after explicit Water activation. Regional-detail
// sources are created only after Water is on and the user reaches regional zoom.

const map = window.__potatoAtlasMap;
if (!map) throw new Error('Physical Water requires the core map.');

const NE_SHA = 'ca96624a56bd078437bca8184e78163e5039ad19';
const NE_BASE = `https://raw.githubusercontent.com/nvkelso/natural-earth-vector/${NE_SHA}/geojson`;
const DETAIL_ZOOM = 3.4;
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

function sourceUrl(name) { return `${NE_BASE}/${name}`; }
function addGeoJsonSource(id, filename) {
  if (map.getSource(id)) return;
  map.addSource(id, {
    type: 'geojson',
    data: sourceUrl(filename),
    attribution: 'Made with Natural Earth · public domain',
  });
}

function ensureSources() {
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

function waterLayers(sources, layers, detail = false) {
  const beforeFill = map.getLayer('countries-fill') ? 'countries-fill' : undefined;
  const beforeLine = map.getLayer('countries-line') ? 'countries-line' : undefined;
  const minZoom = detail ? DETAIL_ZOOM : 0;

  addLayer({
    id: layers.lakeFill,
    type: 'fill',
    source: sources.lakes,
    minzoom: minZoom,
    layout: { visibility: 'none' },
    paint: { 'fill-color': '#6a9db4', 'fill-opacity': detail ? 0.54 : 0.48 },
  }, beforeFill);
  addLayer({
    id: layers.lakeLine,
    type: 'line',
    source: sources.lakes,
    minzoom: minZoom,
    layout: { visibility: 'none' },
    paint: {
      'line-color': '#9dc6d8',
      'line-opacity': 0.8,
      'line-width': ['interpolate', ['linear'], ['zoom'], 0, 0.35, 5, detail ? 1.05 : 0.9],
    },
  }, beforeLine);
  addLayer({
    id: layers.rivers,
    type: 'line',
    source: sources.rivers,
    minzoom: minZoom,
    layout: { visibility: 'none', 'line-cap': 'round', 'line-join': 'round' },
    paint: {
      'line-color': '#7fb8d0',
      'line-opacity': 0.88,
      'line-width': ['interpolate', ['linear'], ['zoom'], 0, 0.35, 3, 0.7, 6, detail ? 1.35 : 1.15],
    },
  }, beforeLine);
  addLayer({
    id: layers.coastline,
    type: 'line',
    source: sources.coastline,
    minzoom: minZoom,
    layout: { visibility: 'none' },
    paint: {
      'line-color': '#9ec7d7',
      'line-opacity': detail ? 0.72 : 0.62,
      'line-width': ['interpolate', ['linear'], ['zoom'], 0, 0.25, 5, detail ? 0.9 : 0.7],
    },
  }, beforeLine);
}

function ensureLayers() {
  waterLayers(OVERVIEW_SOURCES, OVERVIEW_LAYERS, false);
  installed = true;
}

function ensureDetailLayers() {
  waterLayers(DETAIL_SOURCES, DETAIL_LAYERS, true);
  detailInstalled = true;
}

function setLayerGroupVisibility(layers, visibility) {
  for (const id of Object.values(layers)) {
    if (map.getLayer(id)) map.setLayoutProperty(id, 'visibility', visibility);
  }
}

function syncScaleDetail() {
  if (!enabled) return;
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
  if (installed) setLayerGroupVisibility(OVERVIEW_LAYERS, 'none');
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

// Style reloads can discard custom sources/layers. Reinstall only if Water was
// enabled. The detail tier still remains gated by the current zoom.
map.on('styledata', () => {
  if (!enabled || restoring) return;
  restoring = true;
  queueMicrotask(() => {
    try {
      ensureSources();
      ensureLayers();
      detailInstalled = Boolean(map.getSource(DETAIL_SOURCES.rivers));
      syncScaleDetail();
    } catch (error) {
      console.warn('Physical Water could not restore after style change.', error);
    } finally {
      restoring = false;
    }
  });
});

window.__potatoAtlasPhysicalWater = {
  get enabled() { return enabled; },
  get detailInstalled() { return detailInstalled; },
  enable,
  disable,
  toggle,
};
