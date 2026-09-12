// Normalize upstream geometry identifiers that do not match the Atlas entity keys.
// This runs before 3d-hover.js captures window.fetch, so all later geography loads
// see the same stable identifiers without changing the upstream geometry source.

const nativeFetch = window.fetch.bind(window);
const GEOMETRY_MARKERS = [
  'world-countries.geo.json',
  'johan/world.geo.json',
];
const GEOMETRY_ALIASES = new Map([
  ['CS-KM', 'XKX'],
]);

function isWorldGeometry(url) {
  return GEOMETRY_MARKERS.some(marker => String(url || '').includes(marker));
}

function normalizeGeometry(payload) {
  if (payload?.type !== 'FeatureCollection' || !Array.isArray(payload.features)) return payload;
  for (const feature of payload.features) {
    const alias = GEOMETRY_ALIASES.get(String(feature?.id || ''));
    if (!alias) continue;
    feature.id = alias;
    feature.properties = { ...(feature.properties || {}), iso3: alias };
  }
  return payload;
}

window.fetch = async function atlasGeometryAliasFetch(input, options) {
  const url = typeof input === 'string' ? input : input?.url || String(input);
  const response = await nativeFetch(input, options);
  if (!response.ok || !isWorldGeometry(url)) return response;
  try {
    const payload = normalizeGeometry(await response.clone().json());
    return new Response(JSON.stringify(payload), {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
    });
  } catch (error) {
    console.warn('World geometry alias normalization unavailable; using original response.', error);
    return response;
  }
};

window.__potatoAtlasGeometryAliases = Object.freeze({ 'CS-KM': 'XKX' });
