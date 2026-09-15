// Lazy ESA WorldCover 2021 visual land-cover context.
// The official WMS is an RGB cartographic service. This module renders it as
// visual context and deliberately does not claim analytical class lookup.

const map = window.__potatoAtlasMap;
if (!map) throw new Error('Land cover requires the core map.');

const SOURCE_ID = 'atlas-land-cover-worldcover-2021';
const LAYER_ID = 'atlas-land-cover-worldcover-2021-raster';
const LEGEND_ID = 'atlasLandCoverLegend';
const WMS_BASE = 'https://titiler.terrascope.be/wms';
const WMS_LAYER = 'esa-worldcover-map-10m-2021-v2_map';
const WMS_TILE = `${WMS_BASE}?service=WMS&request=GetMap&version=1.1.1&layers=${WMS_LAYER}&styles=&format=image/png&transparent=true&srs=EPSG:3857&bbox={bbox-epsg-3857}&width=256&height=256`;

const CLASSES = [
  ['#006400', 'Tree cover'],
  ['#ffbb22', 'Shrubland'],
  ['#ffff4c', 'Grassland'],
  ['#f096ff', 'Cropland'],
  ['#fa0000', 'Built-up'],
  ['#b4b4b4', 'Bare / sparse vegetation'],
  ['#f0f0f0', 'Snow and ice'],
  ['#0064c8', 'Permanent water bodies'],
  ['#0096a0', 'Herbaceous wetland'],
  ['#00cf75', 'Mangroves'],
  ['#fae6a0', 'Moss and lichen'],
];

let enabled = false;
let restoring = false;
let opacity = 0.58;

function registerLayer() {
  window.__potatoAtlasRenderStack?.register?.(LAYER_ID, {
    slot:'physical-surface',
    priority:20,
    owner:'physical.land-cover',
  });
}
function clampOpacity(value) { return Math.max(0, Math.min(1, Number(value))); }
function applyOpacity() {
  if (map.getLayer(LAYER_ID)) map.setPaintProperty(LAYER_ID, 'raster-opacity', opacity);
}
function setOpacity(value) {
  opacity = clampOpacity(value);
  applyOpacity();
  return true;
}
function getOpacity() { return opacity; }

function ensureStyle() {
  if (document.getElementById('atlasLandCoverStyle')) return;
  const style = document.createElement('style');
  style.id = 'atlasLandCoverStyle';
  style.textContent = `
    #${LEGEND_ID}{background:#080b0be8;border:1px solid #344343;border-radius:10px;padding:7px 9px;color:#dce5e5;font:11px/1.25 system-ui;max-width:280px;backdrop-filter:blur(8px)}
    #${LEGEND_ID} summary{cursor:pointer;font-weight:750;color:#e5f4f4;list-style:none}
    #${LEGEND_ID} summary::-webkit-details-marker{display:none}
    #${LEGEND_ID} .atlas-lc-note{margin:5px 0;color:#9caeae;font-size:9px;line-height:1.3}
    #${LEGEND_ID} .atlas-lc-grid{display:grid;grid-template-columns:1fr 1fr;gap:3px 8px;margin-top:6px}
    #${LEGEND_ID} .atlas-lc-item{display:flex;gap:5px;align-items:center;min-width:0;font-size:9px}
    #${LEGEND_ID} .atlas-lc-swatch{width:9px;height:9px;border-radius:2px;flex:0 0 9px;border:1px solid rgba(255,255,255,.18)}
    @media(max-width:900px){#${LEGEND_ID} .atlas-lc-grid{grid-template-columns:1fr}#${LEGEND_ID}{max-height:25vh;overflow:auto}}
  `;
  document.head.appendChild(style);
}

function ensureLegend() {
  let legend = document.getElementById(LEGEND_ID);
  if (!legend) {
    ensureStyle();
    legend = document.createElement('details');
    legend.id = LEGEND_ID;
    legend.hidden = true;
    legend.innerHTML = `
      <summary>Land cover · ESA 2021</summary>
      <div class="atlas-lc-note">WorldCover 2021 v200 · 10 m source · visual WMS context</div>
      <div class="atlas-lc-grid">${CLASSES.map(([color,label]) => `<div class="atlas-lc-item"><span class="atlas-lc-swatch" style="background:${color}"></span><span>${label}</span></div>`).join('')}</div>
      <div class="atlas-lc-note">Bare / sparse vegetation is a land-cover class, not a synonym for desert or climatic aridity.</div>`;
    document.querySelector('.mapwrap')?.appendChild(legend);
  }
  const layout = window.__potatoAtlasUILayout;
  if (layout) {
    const known = layout.getState?.().some(row => row.id === 'land-cover-legend');
    if (!known) layout.register({ id:'land-cover-legend', zone:'left-status', element:legend, priority:12 });
  }
  return legend;
}

function ensureSource() {
  if (map.getSource(SOURCE_ID)) return;
  map.addSource(SOURCE_ID, {
    type: 'raster',
    tiles: [WMS_TILE],
    tileSize: 256,
    minzoom: 0,
    maxzoom: 14,
    attribution: '© ESA WorldCover project 2021 / Contains modified Copernicus Sentinel data (2021) processed by ESA WorldCover consortium',
  });
}

function ensureLayer() {
  if (!map.getLayer(LAYER_ID)) {
    const before = map.getLayer('countries-fill') ? 'countries-fill' : undefined;
    map.addLayer({
      id: LAYER_ID,
      type: 'raster',
      source: SOURCE_ID,
      layout: { visibility: 'none' },
      paint: {
        'raster-opacity': opacity,
        'raster-fade-duration': 120,
      },
    }, before);
  }
  registerLayer();
}

function setLegendVisible(visible) {
  const legend = ensureLegend();
  legend.hidden = !visible;
  window.__potatoAtlasUILayout?.setVisible?.('land-cover-legend', visible);
}

async function enable() {
  if (enabled && map.getLayer(LAYER_ID)) return true;
  try {
    ensureSource();
    ensureLayer();
    applyOpacity();
    map.setLayoutProperty(LAYER_ID, 'visibility', 'visible');
    enabled = true;
    setLegendVisible(true);
    return true;
  } catch (error) {
    console.warn('ESA WorldCover land-cover layer unavailable; ordinary map remains active.', error);
    enabled = false;
    setLegendVisible(false);
    return false;
  }
}

async function disable() {
  if (map.getLayer(LAYER_ID)) map.setLayoutProperty(LAYER_ID, 'visibility', 'none');
  enabled = false;
  setLegendVisible(false);
  return true;
}

async function toggle() { return enabled ? disable() : enable(); }

map.on('styledata', () => {
  if (!enabled || restoring) return;
  restoring = true;
  queueMicrotask(() => {
    try {
      ensureSource();
      ensureLayer();
      applyOpacity();
      map.setLayoutProperty(LAYER_ID, 'visibility', 'visible');
      setLegendVisible(true);
    } catch (error) {
      console.warn('ESA WorldCover layer could not restore after style change.', error);
    } finally {
      restoring = false;
    }
  });
});

window.__potatoAtlasLandCover = {
  get enabled() { return enabled; },
  enable,
  disable,
  toggle,
  setOpacity,
  getOpacity,
};
