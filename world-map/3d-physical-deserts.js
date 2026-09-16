// Lazy ecological deserts/xeric context for the World Map.
// Source: The Nature Conservancy terrestrial ecoregions snapshot (2009),
// filtered to the WWF major habitat type “Deserts and Xeric Shrublands”.

const map = window.__potatoAtlasMap;
if (!map) throw new Error('Deserts / xeric requires the core map.');
if (!window.__potatoAtlasStyleLifecycle) {
  const { createStyleLifecycle } = await import('./3d-style-lifecycle.js');
  window.__potatoAtlasStyleLifecycle = createStyleLifecycle(map);
}
const styleLifecycle = window.__potatoAtlasStyleLifecycle;

const SOURCE_ID = 'atlas-physical-deserts-xeric';
const FILL_ID = 'atlas-physical-deserts-xeric-fill';
const LINE_ID = 'atlas-physical-deserts-xeric-line';
const SERVICE = 'https://services.arcgis.com/As5CFN3ThbQpy8Ph/arcgis/rest/services/TerrestrialEcoRegions/FeatureServer/0/query';
const WHERE = "WWF_MHTNAM='Deserts and Xeric Shrublands'";
const QUERY_URL = `${SERVICE}?where=${encodeURIComponent(WHERE)}&outFields=ECO_NAME,WWF_MHTNAM,WWF_REALM2&returnGeometry=true&outSR=4326&f=geojson`;
const BASE_FILL_OPACITY = 0.26;
const BASE_LINE_OPACITY = 0.62;

let enabled = false;
let restoring = false;
let opacity = 0.26;

function registerLayers() {
  const stack = window.__potatoAtlasRenderStack;
  stack?.register?.(FILL_ID, { slot:'physical-surface', priority:40, owner:'physical.aridity' });
  stack?.register?.(LINE_ID, { slot:'physical-line', priority:40, owner:'physical.aridity' });
}
function clampOpacity(value) { return Math.max(0, Math.min(1, Number(value))); }
function multiplier() { return opacity / 0.26; }
function applyOpacity() {
  const scale = multiplier();
  if (map.getLayer(FILL_ID)) map.setPaintProperty(FILL_ID, 'fill-opacity', Math.min(1, BASE_FILL_OPACITY * scale));
  if (map.getLayer(LINE_ID)) map.setPaintProperty(LINE_ID, 'line-opacity', Math.min(1, BASE_LINE_OPACITY * scale));
}
function setOpacity(value) {
  opacity = clampOpacity(value);
  applyOpacity();
  return true;
}
function getOpacity() { return opacity; }

function ensureSource() {
  if (map.getSource(SOURCE_ID)) return;
  map.addSource(SOURCE_ID, {
    type: 'geojson',
    data: QUERY_URL,
    attribution: 'The Nature Conservancy · terrestrial ecoregions snapshot (2009)',
  });
}

function ensureLayers() {
  const beforeFill = map.getLayer('countries-fill') ? 'countries-fill' : undefined;
  const beforeLine = map.getLayer('countries-line') ? 'countries-line' : undefined;
  if (!map.getLayer(FILL_ID)) {
    map.addLayer({
      id: FILL_ID,
      type: 'fill',
      source: SOURCE_ID,
      maxzoom: 9,
      layout: { visibility: 'none' },
      paint: { 'fill-color': '#d3a85f', 'fill-opacity': BASE_FILL_OPACITY },
    }, beforeFill);
  }
  if (!map.getLayer(LINE_ID)) {
    map.addLayer({
      id: LINE_ID,
      type: 'line',
      source: SOURCE_ID,
      maxzoom: 9,
      layout: { visibility: 'none' },
      paint: {
        'line-color': '#e4bc78',
        'line-opacity': BASE_LINE_OPACITY,
        'line-width': ['interpolate', ['linear'], ['zoom'], 0, 0.35, 6, 0.9],
      },
    }, beforeLine);
  }
  registerLayers();
  applyOpacity();
}

function setVisibility(visibility) {
  for (const id of [FILL_ID, LINE_ID]) if (map.getLayer(id)) map.setLayoutProperty(id, 'visibility', visibility);
}

async function enable() {
  if (enabled && map.getLayer(FILL_ID)) return true;
  try {
    ensureSource();
    ensureLayers();
    setVisibility('visible');
    enabled = true;
    return true;
  } catch (error) {
    console.warn('Ecological deserts/xeric layer unavailable; ordinary map remains active.', error);
    enabled = false;
    return false;
  }
}

async function disable() {
  setVisibility('none');
  enabled = false;
  return true;
}

async function toggle() { return enabled ? disable() : enable(); }

styleLifecycle.register('physical-deserts', {
  priority:30,
  restore:() => {
    if (!enabled || restoring) return;
    restoring = true;
    queueMicrotask(() => {
      try {
        ensureSource();
        ensureLayers();
        applyOpacity();
        setVisibility('visible');
      } catch (error) {
        console.warn('Ecological deserts/xeric layer could not restore after style change.', error);
      } finally {
        restoring = false;
      }
    });
  },
});

window.__potatoAtlasDeserts = {
  get enabled() { return enabled; },
  enable,
  disable,
  toggle,
  setOpacity,
  getOpacity,
};
