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
const PALESTINE_REPAIR_URL = '../data/world-map-spatial/palestine-base-repair.geojson';
let palestineRepairPromise = null;

function isWorldGeometry(url) {
  return GEOMETRY_MARKERS.some(marker => String(url || '').includes(marker));
}

async function loadPalestineRepair() {
  if (!palestineRepairPromise) {
    palestineRepairPromise = nativeFetch(PALESTINE_REPAIR_URL, { cache:'no-cache' })
      .then(response => {
        if (!response.ok) throw new Error(`${response.status} ${PALESTINE_REPAIR_URL}`);
        return response.json();
      })
      .catch(error => {
        console.warn('Palestine base-map repair unavailable; keeping upstream PSE geometry.', error);
        return null;
      });
  }
  return palestineRepairPromise;
}

function polygonParts(geometry) {
  if (!geometry) return [];
  if (geometry.type === 'Polygon') return [geometry.coordinates];
  if (geometry.type === 'MultiPolygon') return geometry.coordinates || [];
  return [];
}

async function mergePalestineGeometry(payload) {
  const feature = payload?.features?.find(item => String(item?.id || item?.properties?.iso3 || '') === 'PSE');
  if (!feature) return payload;
  const repair = await loadPalestineRepair();
  const GazaStrip = repair?.features?.find(item => (item?.properties || {}).component === 'Gaza Strip');
  if (!GazaStrip?.geometry) return payload;

  const parts = [...polygonParts(feature.geometry), ...polygonParts(GazaStrip.geometry)];
  if (parts.length < 2) return payload;
  feature.geometry = { type:'MultiPolygon', coordinates:parts };
  feature.properties = {
    ...(feature.properties || {}),
    iso3:'PSE',
    canonical_entity:'PSE',
    components:'West Bank + Gaza Strip',
    geometry_repair:'repository-owned Gaza repair',
  };
  return payload;
}

function normalizeAliases(payload) {
  if (payload?.type !== 'FeatureCollection' || !Array.isArray(payload.features)) return payload;
  for (const feature of payload.features) {
    const alias = GEOMETRY_ALIASES.get(String(feature?.id || ''));
    if (!alias) continue;
    feature.id = alias;
    feature.properties = { ...(feature.properties || {}), iso3: alias };
  }
  return payload;
}

async function normalizeGeometry(payload) {
  normalizeAliases(payload);
  await mergePalestineGeometry(payload);
  return payload;
}

window.fetch = async function atlasGeometryAliasFetch(input, options) {
  const url = typeof input === 'string' ? input : input?.url || String(input);
  const response = await nativeFetch(input, options);
  if (!response.ok || !isWorldGeometry(url)) return response;
  try {
    const payload = await normalizeGeometry(await response.clone().json());
    return new Response(JSON.stringify(payload), {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
    });
  } catch (error) {
    console.warn('World geometry normalization unavailable; using original response.', error);
    return response;
  }
};

window.__potatoAtlasGeometryAliases = Object.freeze({
  'CS-KM': 'XKX',
  Palestine: Object.freeze({ canonical_entity:'PSE', component:'Gaza Strip', repair:PALESTINE_REPAIR_URL }),
});
