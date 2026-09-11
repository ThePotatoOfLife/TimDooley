// MapLibre boot shim for the World Relational Atlas.
// Every atlas module still imports the historical unpkg URL; 3d.html redirects that
// specifier here with an import map. We then race independent providers and fail in
// finite time instead of leaving the page suspended on a static module import.
const MAPLIBRE_TIMEOUT_MS = 10000;
const providers = [
  'https://cdn.jsdelivr.net/npm/maplibre-gl@6.9.0/dist/maplibre-gl.mjs',
  'https://esm.sh/maplibre-gl@6.9.0?bundle'
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

// Export the MapLibre API surface used by the atlas and common controls so existing
// `import * as maplibregl` callers continue to work through this shim.
export const Map = runtime.Map;
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
