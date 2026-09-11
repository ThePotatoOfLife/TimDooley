// Same-origin MapLibre GL JS 6 bootstrap for the 3D atlas.
//
// The application was authored against MapLibre 6.x. Pages vendors the ESM
// bundle, worker and shared worker dependency into ./vendor at deploy time.
// Keeping the engine on the same origin removes CDN availability from browser
// boot while preserving the API/runtime version the atlas code expects.

import * as runtime from './vendor/maplibre-gl.mjs?v=6.9.0';

// A number of optional atlas modules were written when they all started in
// parallel. They use `loaded()` followed by `once("load")`. MapLibre's load
// event is one-shot, while loaded() can temporarily become false again when a
// later source/layer is settling. Replay that first-load readiness signal for
// late enhancement modules so they cannot wait forever on an event that already
// happened.
class AtlasMap extends runtime.Map {
  constructor(options = {}) {
    super(options);
    this.__potatoAtlasFirstLoadComplete = false;
    super.once('load', () => {
      this.__potatoAtlasFirstLoadComplete = true;
      if (window.__potatoAtlasBootGuard) window.__potatoAtlasBootGuard.stage = 'map-loaded';
      window.dispatchEvent(new CustomEvent('potato-atlas-map-ready', { detail: { map: this } }));
    });
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
