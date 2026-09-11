// Atlas MapLibre bootstrap.
//
// Two deliberate compatibility choices live here:
// 1. Keep the atlas on the last v5 release while the v6 migration settles.
// 2. Never let the initial MapLibre `load` depend on a third-party raster tile server.
//    The atlas countries are its real map; a decorative OSM raster must not gate boot.

const MAPLIBRE_TIMEOUT_MS = 10000;
const MAPLIBRE_VERSION = '5.24.0';
const providers = [
  `https://cdn.jsdelivr.net/npm/maplibre-gl@${MAPLIBRE_VERSION}/dist/maplibre-gl.mjs`,
  `https://esm.sh/maplibre-gl@${MAPLIBRE_VERSION}?bundle`
];

function deadline(ms) {
  return new Promise((_, reject) => {
    setTimeout(() => reject(new Error(`MapLibre providers timed out after ${ms} ms`)), ms);
  });
}

let runtime;
try {
  runtime = await Promise.race([
    Promise.any(providers.map(url => import(url))),
    deadline(MAPLIBRE_TIMEOUT_MS)
  ]);
} catch (error) {
  const status = document.querySelector('#status');
  if (status) {
    status.hidden = false;
    status.dataset.kind = 'error';
    status.textContent = 'Map engine failed to load. Reload or check network filtering.';
  }
  console.error('Atlas MapLibre bootstrap failed.', error);
  throw error;
}

function isRemoteOsmBootstrapStyle(style) {
  if (!style || typeof style !== 'object') return false;
  const osm = style.sources?.osm;
  if (!osm || osm.type !== 'raster') return false;
  return (osm.tiles || []).some(url => String(url).includes('tile.openstreetmap.org'));
}

function localBootstrapStyle() {
  return {
    version: 8,
    sources: {},
    layers: [
      {
        id: 'atlas-background',
        type: 'background',
        paint: { 'background-color': '#080b0b' }
      }
    ]
  };
}

// The application historically used Map.loaded() + once('load') as though `load`
// were a replayable readiness signal. MapLibre's load event is one-shot, while
// loaded() can become false again whenever a later source/layer is still settling.
// That combination can wait forever after the first load already happened.
//
// AtlasMap records the first load and replays only *late* once('load', fn)
// subscriptions. Existing modules can therefore keep their current boot logic
// without deadlocking after another module adds a GeoJSON source.
class AtlasMap extends runtime.Map {
  constructor(options = {}) {
    const sanitized = isRemoteOsmBootstrapStyle(options.style)
      ? { ...options, style: localBootstrapStyle() }
      : options;
    super(sanitized);
    this.__potatoAtlasFirstLoadComplete = false;
    super.once('load', () => {
      this.__potatoAtlasFirstLoadComplete = true;
      window.dispatchEvent(new CustomEvent('potato-atlas-map-ready', { detail: { map: this } }));
    });
  }

  once(type, ...args) {
    if (type === 'load' && this.__potatoAtlasFirstLoadComplete) {
      const listener = args.find(arg => typeof arg === 'function');
      if (listener) {
        queueMicrotask(() => listener.call(this, { type: 'load', target: this }));
        return this;
      }
    }
    return super.once(type, ...args);
  }
}

export const Map = AtlasMap;
export const Popup = runtime.Popup;
export const NavigationControl = runtime.NavigationControl;
export const Marker = runtime.Marker;
export const LngLat = runtime.LngLat;
export const LngLatBounds = runtime.LngLatBounds;
export const MercatorCoordinate = runtime.MercatorCoordinate;
export const AttributionControl = runtime.AttributionControl;
export const ScaleControl = runtime.ScaleControl;
export const FullscreenControl = runtime.FullscreenControl;
export const GeolocateControl = runtime.GeolocateControl;
export const LogoControl = runtime.LogoControl;
export const version = runtime.version;
