// Optional physical terrain behavior for the World Map.
// Loaded only by the Physical World runtime after explicit Terrain activation.

const map = window.__potatoAtlasMap;
if (!map) throw new Error('Physical Terrain requires the core map.');

const TERRAIN_SOURCE = 'atlas-terrain-dem';
const HILLSHADE_SOURCE = 'atlas-hillshade-dem';
const HILLSHADE_LAYER = 'atlas-hillshade';
const TERRAIN_TILEJSON = 'https://tiles.mapterhorn.com/tilejson.json';
const BASE_RASTER_LAYER = 'osm';
const BASE_RASTER_DEFAULT_OPACITY = 0.25;
const BASE_RASTER_TERRAIN_OPACITY = 0.55;
const TERRAIN_EXAGGERATION = 1.05;

let enabled = false;
let busy = false;

function ensureSources() {
  if (!map.getSource(TERRAIN_SOURCE)) {
    map.addSource(TERRAIN_SOURCE, {
      type: 'raster-dem',
      url: TERRAIN_TILEJSON,
      tileSize: 512,
      encoding: 'terrarium',
      attribution: 'Terrain © Mapterhorn',
    });
  }
  if (!map.getSource(HILLSHADE_SOURCE)) {
    map.addSource(HILLSHADE_SOURCE, {
      type: 'raster-dem',
      url: TERRAIN_TILEJSON,
      tileSize: 512,
      encoding: 'terrarium',
      attribution: 'Terrain © Mapterhorn',
    });
  }
}

function ensureHillshade() {
  if (map.getLayer(HILLSHADE_LAYER)) return;
  const before = map.getLayer('countries-fill') ? 'countries-fill' : undefined;
  map.addLayer({
    id: HILLSHADE_LAYER,
    type: 'hillshade',
    source: HILLSHADE_SOURCE,
    layout: { visibility: 'none' },
    paint: { 'hillshade-exaggeration': 0.35 },
  }, before);
}

function setBaseOpacity(value) {
  if (!map.getLayer(BASE_RASTER_LAYER)) return;
  try { map.setPaintProperty(BASE_RASTER_LAYER, 'raster-opacity', value); } catch {}
}

async function setEnabled(next) {
  if (busy || enabled === next) return enabled;
  busy = true;
  try {
    if (next) {
      // Network-backed DEM sources are created only here, after explicit activation.
      ensureSources();
      ensureHillshade();
      map.setLayoutProperty(HILLSHADE_LAYER, 'visibility', 'visible');
      map.setTerrain({ source:TERRAIN_SOURCE, exaggeration:TERRAIN_EXAGGERATION });
      setBaseOpacity(BASE_RASTER_TERRAIN_OPACITY);
      enabled = true;
    } else {
      try { map.setTerrain(null); } catch {}
      if (map.getLayer(HILLSHADE_LAYER)) map.setLayoutProperty(HILLSHADE_LAYER, 'visibility', 'none');
      setBaseOpacity(BASE_RASTER_DEFAULT_OPACITY);
      enabled = false;
    }
  } catch (error) {
    console.warn('Physical terrain unavailable:', error);
    try { map.setTerrain(null); } catch {}
    if (map.getLayer(HILLSHADE_LAYER)) {
      try { map.setLayoutProperty(HILLSHADE_LAYER, 'visibility', 'none'); } catch {}
    }
    setBaseOpacity(BASE_RASTER_DEFAULT_OPACITY);
    enabled = false;
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
  enable: () => setEnabled(true),
  disable: () => setEnabled(false),
  toggle,
};
