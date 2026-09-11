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

class AtlasMap extends runtime.Map {
  constructor(options = {}) {
    const deferredRaster = splitDeferredRasterStyle(options.style);
    const bootOptions = deferredRaster
      ? { ...options, style: LOCAL_BOOT_STYLE }
      : options;

    super(bootOptions);
    this.__potatoAtlasFirstLoadComplete = false;
    this.__potatoAtlasDeferredRaster = deferredRaster;
    this.__potatoAtlasBasemapAttached = false;

    super.once('load', () => {
      this.__potatoAtlasFirstLoadComplete = true;
      if (window.__potatoAtlasBootGuard) window.__potatoAtlasBootGuard.stage = 'map-loaded';
      window.dispatchEvent(new CustomEvent('potato-atlas-map-ready', { detail: { map: this } }));
    });
  }

  // The old atlas style included an OpenStreetMap raster source. It is retained
  // as optional context, but never attached merely because the page opened.
  // This prevents a slow/blocked tile service from turning a healthy local map
  // into "it loaded, then started hanging". Progressive UI exposes this method
  // as an explicit Basemap control.
  __potatoAtlasAttachBasemap() {
    const deferredRaster = this.__potatoAtlasDeferredRaster;
    if (!deferredRaster || this.__potatoAtlasBasemapAttached) return this.__potatoAtlasBasemapAttached;
    try {
      for (const [id, source] of Object.entries(deferredRaster.sources)) {
        if (!this.getSource(id)) this.addSource(id, source);
      }
      const before = this.getLayer('countries-fill') ? 'countries-fill' : undefined;
      for (const layer of deferredRaster.layers) {
        if (!this.getLayer(layer.id)) this.addLayer(layer, before);
      }
      this.__potatoAtlasBasemapAttached = true;
      if (window.__potatoAtlasBootGuard) window.__potatoAtlasBootGuard.stage = 'basemap-attached';
      window.dispatchEvent(new CustomEvent('potato-atlas-basemap-change', { detail: { attached: true } }));
      return true;
    } catch (error) {
      console.warn('Optional raster basemap unavailable:', error);
      return false;
    }
  }

  on(type, ...args) {
    // The core HUD used to recompute graph state and rewrite DOM on every zoom,
    // pitch and rotate frame. It already has a moveend listener, so suppress only
    // those redundant animation-frame registrations and leave all other events intact.
    const listener = args.find(arg => typeof arg === 'function');
    if (['zoom', 'pitch', 'rotate'].includes(type) && listener?.name === 'updateHud') {
      return { unsubscribe() {} };
    }
    return super.on(type, ...args);
  }

  once(type, ...args) {
    // MapLibre's load event is one-shot, while loaded() can temporarily become
    // false again as later sources/layers settle. Replay first-load readiness to
    // legacy optional modules instead of letting them wait for an event that has
    // already happened.
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

class AtlasPopup extends runtime.Popup {
  setHTML(html) {
    // Avoid rebuilding identical popup DOM for every mousemove over one country.
    if (html === this.__potatoAtlasLastHtml) return this;
    if (window.__potatoAtlasMap?.isMoving?.()) return this;
    this.__potatoAtlasLastHtml = html;
    return super.setHTML(html);
  }

  setLngLat(lngLat) {
    // Pointer events can keep firing while a WebGL drag is in progress. Popup
    // layout is decorative, so never make it compete with camera rendering.
    if (window.__potatoAtlasMap?.isMoving?.()) return this;
    return super.setLngLat(lngLat);
  }

  addTo(map) {
    if (map?.isMoving?.()) return this;
    return super.addTo(map);
  }
}

export const Map = AtlasMap;
export const Popup = AtlasPopup;
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