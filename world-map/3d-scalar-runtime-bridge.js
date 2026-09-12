// Entity-aware scalar compatibility adapter.
//
// The compositor is the single rendering owner for Population/Area and all other
// scalar fills. This bridge preserves the older public helper surface without
// repainting the map or subscribing to duplicate composition events.

const layers = window.__potatoAtlasLayers;
const runtime = window.__potatoAtlasDataRuntime;
const compositor = window.__potatoAtlasCompositor;
if (!layers || !runtime?.ready || !compositor) throw new Error('Scalar compatibility adapter requires registry, runtime and compositor APIs.');

function activeRuntimeScalar() {
  return layers.active().map(id => layers.get(id)).find(entry => entry?.kind === 'scalar' && entry.runtime_scalar) || null;
}

async function observation(code, metricId = activeRuntimeScalar()?.runtime_scalar) {
  if (!metricId) return null;
  if (runtime.scalarObservation) return runtime.scalarObservation(code, metricId);
  const data = await runtime.ready;
  return data?.scalars?.by_entity?.[String(code || '').toUpperCase()]?.[metricId] || null;
}

async function applyRuntimeEntityScalar(entry = activeRuntimeScalar()) {
  // Compatibility adapter only: scalar painting is owned by 3d-compositor.js.
  if (!entry?.runtime_scalar) return false;
  await compositor.render();
  return true;
}

async function sync() {
  const entry = activeRuntimeScalar();
  return Boolean(entry?.runtime_scalar);
}

window.__potatoAtlasScalarBridge = {
  sync,
  applyRuntimeEntityScalar,
  activeRuntimeScalar,
  observation,
  renderingOwner:'compositor',
};

await sync();
