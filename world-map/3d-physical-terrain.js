// Optional physical terrain behavior for the World Map.
// Loaded only by the Physical World runtime after explicit Terrain activation.
// One capped DEM source is shared by 3D terrain and hillshade to avoid duplicate
// elevation tile requests and keep the optional physical layer lightweight.

const map = window.__potatoAtlasMap;
if (!map) throw new Error('Physical Terrain requires the core map.');

const PHYSICAL_ID = 'physical.terrain';
const TERRAIN_SOURCE = 'atlas-terrain-dem';
const HILLSHADE_LAYER = 'atlas-hillshade';
const TERRAIN_TILEJSON = 'https://tiles.mapterhorn.com/tilejson.json';
const TERRAIN_MAX_SOURCE_ZOOM = 12;
const BASE_RASTER_LAYER = 'osm';
const BASE_RASTER_DEFAULT_OPACITY = 0.25;
const BASE_RASTER_TERRAIN_OPACITY = 0.50;
const TERRAIN_EXAGGERATION = 1.03;
const HILLSHADE_EXAGGERATION = 0.28;

let enabled = false;
let busy = false;

function reportStatus(phase, message) {
  window.dispatchEvent(new CustomEvent('potato-atlas-physical-layer-status', {
    detail:{ id:PHYSICAL_ID, provider:'Mapterhorn', phase, message, retryable:true }
  }));
}

function registerHillshade() {
  window.__potatoAtlasRenderStack?.register?.(HILLSHADE_LAYER, {
    slot:'physical-surface',
    priority:10,
    owner:'physical.terrain',
  });
}

function ensureSources() {
  if (map.getSource(TERRAIN_SOURCE)) return;
  map.addSource(TERRAIN_SOURCE, {
    type: 'raster-dem',
    url: TERRAIN_TILEJSON,
    tileSize: 512,
    maxzoom: TERRAIN_MAX_SOURCE_ZOOM,
    encoding: 'terrarium',
    attribution: 'Terrain © Mapterhorn',
  });
}

function ensureHillshade() {
  if (!map.getLayer(HILLSHADE_LAYER)) {
    const before = map.getLayer('countries-fill') ? 'countries-fill' : undefined;
    map.addLayer({
      id: HILLSHADE_LAYER,
      type: 'hillshade',
      source: TERRAIN_SOURCE,
      layout: { visibility: 'none' },
      paint: { 'hillshade-exaggeration': HILLSHADE_EXAGGERATION },
    }, before);
  }
  registerHillshade();
}

function setBaseOpacity(value) {
  if (!map.getLayer(BASE_RASTER_LAYER)) return;
  try { map.setPaintProperty(BASE_RASTER_LAYER, 'raster-opacity', value); } catch {}
}

async function setEnabled(next) {
  if (busy || enabled === next) return enabled;
  busy = true;
  if (next) reportStatus('loading', 'Loading terrain DEM');
  try {
    if (next) {
      // Network-backed DEM data is created only here, after explicit activation.
      // Terrain and hillshade intentionally share one source and one tile cache.
      ensureSources();
      ensureHillshade();
      map.setLayoutProperty(HILLSHADE_LAYER, 'visibility', 'visible');
      map.setTerrain({ source:TERRAIN_SOURCE, exaggeration:TERRAIN_EXAGGERATION });
      setBaseOpacity(BASE_RASTER_TERRAIN_OPACITY);
      enabled = true;
      reportStatus('active', 'Terrain DEM active');
    } else {
      try { map.setTerrain(null); } catch {}
      if (map.getLayer(HILLSHADE_LAYER)) map.setLayoutProperty(HILLSHADE_LAYER, 'visibility', 'none');
      setBaseOpacity(BASE_RASTER_DEFAULT_OPACITY);
      enabled = false;
      reportStatus('idle', 'Terrain off');
    }
  } catch (error) {
    console.warn('Physical terrain unavailable:', error);
    try { map.setTerrain(null); } catch {}
    if (map.getLayer(HILLSHADE_LAYER)) {
      try { map.setLayoutProperty(HILLSHADE_LAYER, 'visibility', 'none'); } catch {}
    }
    setBaseOpacity(BASE_RASTER_DEFAULT_OPACITY);
    enabled = false;
    reportStatus('error', error?.message || 'Terrain provider unavailable');
  } finally {
    busy = false;
  }
  return enabled;
}

function toggle() {
  return setEnabled(!enabled);
}

window.__potatoAtlasTerrain = {
  get enabled() { return enabled; },
  get maxSourceZoom() { return TERRAIN_MAX_SOURCE_ZOOM; },
  enable: () => setEnabled(true),
  disable: () => setEnabled(false),
  toggle,
};
