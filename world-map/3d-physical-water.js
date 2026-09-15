// Lazy Natural Earth physical-water context for the World Map.
// This module is imported only after explicit Water activation.

const map = window.__potatoAtlasMap;
if (!map) throw new Error('Physical Water requires the core map.');

const NE_SHA = 'ca96624a56bd078437bca8184e78163e5039ad19';
const NE_BASE = `https://raw.githubusercontent.com/nvkelso/natural-earth-vector/${NE_SHA}/geojson`;
const SOURCES = {
  rivers: 'atlas-physical-water-rivers',
  lakes: 'atlas-physical-water-lakes',
  coastline: 'atlas-physical-water-coastline',
};
const LAYERS = {
  lakeFill: 'atlas-physical-water-lake-fill',
  lakeLine: 'atlas-physical-water-lake-line',
  rivers: 'atlas-physical-water-river-line',
  coastline: 'atlas-physical-water-coastline-line',
};

let enabled = false;
let installed = false;

function sourceUrl(name) {
  return `${NE_BASE}/${name}`;
}

function ensureSources() {
  if (!map.getSource(SOURCES.rivers)) {
    map.addSource(SOURCES.rivers, {
      type: 'geojson',
      data: sourceUrl('ne_110m_rivers_lake_centerlines.geojson'),
      attribution: 'Made with Natural Earth · public domain',
    });
  }
  if (!map.getSource(SOURCES.lakes)) {
    map.addSource(SOURCES.lakes, {
      type: 'geojson',
      data: sourceUrl('ne_110m_lakes.geojson'),
      attribution: 'Made with Natural Earth · public domain',
    });
  }
  if (!map.getSource(SOURCES.coastline)) {
    map.addSource(SOURCES.coastline, {
      type: 'geojson',
      data: sourceUrl('ne_110m_coastline.geojson'),
      attribution: 'Made with Natural Earth · public domain',
    });
  }
}

function addLayer(definition, before) {
  if (map.getLayer(definition.id)) return;
  try {
    map.addLayer(definition, before && map.getLayer(before) ? before : undefined);
  } catch (error) {
    console.warn(`Physical Water layer install failed: ${definition.id}`, error);
    throw error;
  }
}

function ensureLayers() {
  const beforeFill = map.getLayer('countries-fill') ? 'countries-fill' : undefined;
  const beforeLine = map.getLayer('countries-line') ? 'countries-line' : undefined;

  addLayer({
    id: LAYERS.lakeFill,
    type: 'fill',
    source: SOURCES.lakes,
    layout: { visibility: 'none' },
    paint: {
      'fill-color': '#6a9db4',
      'fill-opacity': 0.48,
    },
  }, beforeFill);

  addLayer({
    id: LAYERS.lakeLine,
    type: 'line',
    source: SOURCES.lakes,
    layout: { visibility: 'none' },
    paint: {
      'line-color': '#9dc6d8',
      'line-opacity': 0.8,
      'line-width': ['interpolate', ['linear'], ['zoom'], 0, 0.35, 5, 0.9],
    },
  }, beforeLine);

  addLayer({
    id: LAYERS.rivers,
    type: 'line',
    source: SOURCES.rivers,
    layout: {
      visibility: 'none',
      'line-cap': 'round',
      'line-join': 'round',
    },
    paint: {
      'line-color': '#7fb8d0',
      'line-opacity': 0.88,
      'line-width': ['interpolate', ['linear'], ['zoom'], 0, 0.35, 3, 0.7, 6, 1.15],
    },
  }, beforeLine);

  addLayer({
    id: LAYERS.coastline,
    type: 'line',
    source: SOURCES.coastline,
    layout: { visibility: 'none' },
    paint: {
      'line-color': '#9ec7d7',
      'line-opacity': 0.62,
      'line-width': ['interpolate', ['linear'], ['zoom'], 0, 0.25, 5, 0.7],
    },
  }, beforeLine);

  installed = true;
}

function setVisibility(visibility) {
  for (const id of Object.values(LAYERS)) {
    if (!map.getLayer(id)) continue;
    map.setLayoutProperty(id, 'visibility', visibility);
  }
}

async function enable() {
  if (enabled) return true;
  try {
    ensureSources();
    ensureLayers();
    setVisibility('visible');
    enabled = true;
    return true;
  } catch (error) {
    console.warn('Physical Water unavailable; ordinary map remains active.', error);
    enabled = false;
    return false;
  }
}

async function disable() {
  if (!installed) {
    enabled = false;
    return true;
  }
  setVisibility('none');
  enabled = false;
  return true;
}

async function toggle() {
  return enabled ? disable() : enable();
}

// Style reloads can discard custom sources/layers. Reinstall only if the user
// had Water enabled; this does not create polling or startup network activity.
map.on('styledata', () => {
  if (!enabled) return;
  try {
    ensureSources();
    ensureLayers();
    setVisibility('visible');
  } catch (error) {
    console.warn('Physical Water could not restore after style change.', error);
  }
});

window.__potatoAtlasPhysicalWater = {
  get enabled() { return enabled; },
  enable,
  disable,
  toggle,
};
