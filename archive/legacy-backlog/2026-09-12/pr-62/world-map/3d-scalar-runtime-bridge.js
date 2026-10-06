// Render entity-aware Population/Area Stats from the shared generated scalar plane.
// The ordinary compositor keeps ownership of other scalar families.

const map = window.__potatoAtlasMap;
const layers = window.__potatoAtlasLayers;
const runtime = window.__potatoAtlasDataRuntime;
if (!map || !layers || !runtime?.ready) throw new Error('Scalar bridge requires map, registry and shared data runtime.');

const UNKNOWN = '#303938';

function setBaseFill(expression) {
  for (const layerId of ['countries-fill', 'countries-extrude']) {
    if (!map.getLayer(layerId)) continue;
    const property = layerId === 'countries-fill' ? 'fill-color' : 'fill-extrusion-color';
    map.setPaintProperty(layerId, property, expression);
  }
}

function activeRuntimeScalar() {
  return layers.active().map(id => layers.get(id)).find(entry => entry?.kind === 'scalar' && entry.runtime_scalar) || null;
}

async function applyRuntimeEntityScalar(entry) {
  if (!entry?.runtime_scalar) return false;
  const data = await runtime.ready;
  const metricId = entry.runtime_scalar;
  const rows = data?.scalars?.by_entity || {};
  for (const [code, values] of Object.entries(rows)) {
    const raw = Number(values?.[metricId]?.value);
    const has = Number.isFinite(raw);
    try {
      map.setFeatureState({ source:'countries', id:code }, { atlasEntityScalarHas:has, atlasEntityScalarValue:has ? raw : 0 });
    } catch {}
  }
  const value = ['feature-state', 'atlasEntityScalarValue'];
  let scale;
  if (metricId === 'population') {
    scale = ['step', value, '#263432', 1_000_000, '#36514b', 10_000_000, '#527466', 50_000_000, '#78977d', 100_000_000, '#a7b87f', 500_000_000, '#d0c77e'];
  } else if (metricId === 'area') {
    scale = ['step', value, '#263432', 10_000, '#36514b', 100_000, '#527466', 500_000, '#78977d', 1_000_000, '#a7b87f', 5_000_000, '#d0c77e'];
  } else {
    return false;
  }
  setBaseFill(['case', ['boolean', ['feature-state', 'atlasEntityScalarHas'], false], scale, UNKNOWN]);
  window.dispatchEvent(new CustomEvent('potato-atlas-entity-scalar-render', { detail:{ metricId } }));
  return true;
}

async function sync() {
  const entry = activeRuntimeScalar();
  if (!entry) return false;
  return applyRuntimeEntityScalar(entry);
}

window.addEventListener('potato-atlas-composition-change', event => {
  const active = event?.detail?.active || [];
  const entry = active.map(id => layers.get(id)).find(item => item?.runtime_scalar);
  if (entry) queueMicrotask(() => applyRuntimeEntityScalar(entry));
});
window.addEventListener('potato-atlas-layer-change', () => queueMicrotask(sync));

await sync();
window.__potatoAtlasScalarBridge = { sync, applyRuntimeEntityScalar };
