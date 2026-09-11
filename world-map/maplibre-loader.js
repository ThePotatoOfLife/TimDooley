// Same-origin MapLibre GL JS 6 bootstrap for the 3D atlas.
//
// The application was authored against MapLibre 6.x. Pages vendors the ESM
// bundle, worker and shared worker dependency into ./vendor at deploy time.
// Keeping the engine on the same origin removes CDN availability from browser
// boot while preserving the API/runtime version the atlas code expects.

import * as runtime from './vendor/maplibre-gl.mjs?v=6.9.0';

const LOCAL_BOOT_STYLE = {
  version: 8,
  sources: {},
  layers: [{
    id: 'atlas-boot-background',
    type: 'background',
    paint: { 'background-color': '#080b0b' }
  }]
};

function splitDeferredRasterStyle(style) {
  if (!style || typeof style !== 'object' || Array.isArray(style)) return null;
  const sources = style.sources || {};
  const layers = Array.isArray(style.layers) ? style.layers : [];
  const rasterSourceIds = Object.entries(sources)
    .filter(([, source]) => source?.type === 'raster')
    .map(([id]) => id);
  if (!rasterSourceIds.length) return null;

  const rasterLayers = layers.filter(layer => rasterSourceIds.includes(layer?.source));
  if (!rasterLayers.length) return null;

  return {
    sources: Object.fromEntries(rasterSourceIds.map(id => [id, sources[id]])),
    layers: rasterLayers
  };
}

// A number of optional atlas modules were written when they all started in
// parallel. They use `loaded()` followed by `once("load")`. MapLibre's load
// event is one-shot, while loaded() can temporarily become false again when a
// later source/layer is settling. Replay that first-load readiness signal for
// late enhancement modules so they cannot wait forever on an event that already
// happened.
class AtlasMap extends runtime.Map {
  constructor(options = {}) {
    const deferredRaster = splitDeferredRasterStyle(options.style);
    const bootOptions = deferredRaster
      ? { ...options, style: LOCAL_BOOT_STYLE }
      : options;

    super(bootOptions);
    this.__potatoAtlasFirstLoadComplete = false;
    this.__potatoAtlasDeferredRaster = deferredRaster;

    super.once('load', () => {
      this.__potatoAtlasFirstLoadComplete = true;
      if (window.__potatoAtlasBootGuard) window.__potatoAtlasBootGuard.stage = 'map-loaded';
      window.dispatchEvent(new CustomEvent('potato-atlas-map-ready', { detail: { map: this } }));
    });

    // The geographic country layer is the availability boundary. Only after
    // the bootstrap has proved that layer exists do we attach external raster
    // context such as OSM. A tile outage therefore cannot block first paint.
    if (deferredRaster) {
      window.addEventListener('potato-atlas-core-ready', () => {
        try {
          for (const [id, source] of Object.entries(deferredRaster.sources)) {
            if (!this.getSource(id)) this.addSource(id, source);
          }
          const before = this.getLayer('countries-fill') ? 'countries-fill' : undefined;
          for (const layer of deferredRaster.layers) {
            if (!this.getLayer(layer.id)) this.addLayer(layer, before);
          }
          if (window.__potatoAtlasBootGuard) window.__potatoAtlasBootGuard.stage = 'basemap-attached';
        } catch (error) {
          console.warn('Optional raster basemap unavailable:', error);
        }
      }, { once: true });
    }
  }

  once(type, ...args) {
    if (type === 'load' && this.__potatoAtlasFirstLoadComplete) {
      const listener = args.find(arg => typeof arg === 'function');
      if (listener) {
        queueMicrotask(() => listener.call(this, { type: 'load', target: this }));
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
export const setWorkerUrl = runtime.setWorkerUrl;
export const getWorkerUrl = runtime.getWorkerUrl;
export const version = runtime.version;