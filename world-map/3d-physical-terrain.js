// Optional physical context for the World Map.
// The control loads with the core, but elevation/hillshade tiles remain dormant
// until the user explicitly enables Terrain.

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

let enabled = new URL(location.href).searchParams.get('terrain') === '1';
let busy = false;

function terrainButton() {
  return document.getElementById('atlasTerrainToggle');
}

function setUrlState(on) {
  const url = new URL(location.href);
  if (on) url.searchParams.set('terrain', '1');
  else url.searchParams.delete('terrain');
  history.replaceState({}, '', url);
}

function setButtonState(message = '') {
  const button = terrainButton();
  if (!button) return;
  button.classList.toggle('active', enabled);
  button.setAttribute('aria-pressed', enabled ? 'true' : 'false');
  button.textContent = enabled ? 'Terrain · on' : 'Terrain';
  button.title = message || (enabled
    ? 'Physical terrain is on · shaded relief and elevation'
    : 'Show physical terrain · shaded relief and elevation');
}

function installControl() {
  if (terrainButton()) return terrainButton();
  const pop = document.querySelector('#viewMenu .atlas-world-menu-pop, #viewMenu .menu-pop');
  if (!pop) return null;
  const button = document.createElement('button');
  button.id = 'atlasTerrainToggle';
  button.type = 'button';
  button.setAttribute('aria-pressed', 'false');
  button.addEventListener('click', () => toggle());
  const separator = pop.querySelector('.menu-sep');
  if (separator) pop.insertBefore(button, separator);
  else pop.prepend(button);
  setButtonState();
  return button;
}

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
      ensureSources();
      ensureHillshade();
      map.setLayoutProperty(HILLSHADE_LAYER, 'visibility', 'visible');
      map.setTerrain({ source: TERRAIN_SOURCE, exaggeration: TERRAIN_EXAGGERATION });
      setBaseOpacity(BASE_RASTER_TERRAIN_OPACITY);
      enabled = true;
      setUrlState(true); // canonical state is terrain=1
      setButtonState();
    } else {
      try { map.setTerrain(null); } catch {}
      if (map.getLayer(HILLSHADE_LAYER)) map.setLayoutProperty(HILLSHADE_LAYER, 'visibility', 'none');
      setBaseOpacity(BASE_RASTER_DEFAULT_OPACITY);
      enabled = false;
      setUrlState(false);
      setButtonState();
    }
  } catch (error) {
    console.warn('Physical terrain unavailable:', error);
    try { map.setTerrain(null); } catch {}
    if (map.getLayer(HILLSHADE_LAYER)) {
      try { map.setLayoutProperty(HILLSHADE_LAYER, 'visibility', 'none'); } catch {}
    }
    setBaseOpacity(BASE_RASTER_DEFAULT_OPACITY);
    enabled = false;
    setUrlState(false);
    setButtonState('Terrain unavailable; the ordinary map remains active.');
  } finally {
    busy = false;
  }
  return enabled;
}

function toggle() {
  return setEnabled(!enabled);
}

installControl();
if (enabled) {
  // Restore URL state only after the map is ready; failures remain nonfatal.
  enabled = false;
  queueMicrotask(() => setEnabled(true));
}

window.__potatoAtlasTerrain = {
  get enabled() { return enabled; },
  enable: () => setEnabled(true),
  disable: () => setEnabled(false),
  toggle,
};
