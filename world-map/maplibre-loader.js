// Atlas MapLibre bootstrap.
//
// MapLibre GL JS 5.x ships a classic browser bundle (dist/maplibre-gl.js)
// with the worker embedded. Version 6 is the line that moved to the ESM-only
// dist/maplibre-gl.mjs layout. Do not ask an ESM conversion service to reinterpret
// v5 at runtime: load the real v5 browser artifact directly, with bounded fallbacks.

const MAPLIBRE_VERSION = '5.24.0';
const PROVIDER_TIMEOUT_MS = 7000;
const providers = [
  `https://cdn.jsdelivr.net/npm/maplibre-gl@${MAPLIBRE_VERSION}/dist/maplibre-gl.js`,
  `https://unpkg.com/maplibre-gl@${MAPLIBRE_VERSION}/dist/maplibre-gl.js`
];

function setBootStatus(message, kind = 'info') {
  const status = document.querySelector('#status');
  if (!status) return;
  status.hidden = !message;
  status.dataset.kind = kind;
  status.textContent = message;
}

function loadClassicScript(url, timeoutMs = PROVIDER_TIMEOUT_MS) {
  return new Promise((resolve, reject) => {
    if (globalThis.maplibregl?.Map) {
      resolve(globalThis.maplibregl);
      return;
    }

    const script = document.createElement('script');
    script.async = true;
    script.src = url;
    script.dataset.atlasMapEngine = url;

    let settled = false;
    const finish = (fn, value) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      script.onload = null;
      script.onerror = null;
      fn(value);
    };

    const timer = setTimeout(() => {
      script.remove();
      finish(reject, new Error(`MapLibre provider timed out: ${url}`));
    }, timeoutMs);

    script.onload = () => {
      if (globalThis.maplibregl?.Map) finish(resolve, globalThis.maplibregl);
      else finish(reject, new Error(`MapLibre provider loaded without exposing maplibregl: ${url}`));
    };
    script.onerror = () => finish(reject, new Error(`MapLibre provider failed: ${url}`));
    document.head.appendChild(script);
  });
}

async function loadRuntime() {
  if (globalThis.maplibregl?.Map) return globalThis.maplibregl;
  setBootStatus('Loading map engine…');
  const errors = [];
  for (const url of providers) {
    try {
      const runtime = await loadClassicScript(url);
      setBootStatus('Map engine ready…');
      return runtime;
    } catch (error) {
      errors.push(error);
      console.warn(error.message);
    }
  }
  throw new AggregateError(errors, 'All MapLibre browser providers failed');
}

let runtime;
try {
  runtime = await loadRuntime();
} catch (error) {
  setBootStatus('Map engine failed to load. Both browser-bundle providers failed.', 'error');
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
// AtlasMap records the first load and replays only late once('load', fn)
// subscriptions, preventing enhancement modules from waiting on an event that
// already happened.
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
        // MapLibre v5 normally returns a Subscription from once(type, listener).
        // Existing atlas callers ignore that handle, so returning a disposable
        // compatibility object is safer than pretending the Map itself is one.
        return { unsubscribe() {} };
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
