import * as maplibregl from 'https://unpkg.com/maplibre-gl@6.9.0/dist/maplibre-gl.mjs';

// Compatibility wrapper around the preserved core renderer. The renderer boots
// before the Interaction Router so geography remains available early. We capture
// only the legacy layer-click listeners that need arbitration, then detach those
// exact functions and re-register their behavior with the shared router.
const CAPTURED_CLICK_LAYERS = new Set([
  'countries-fill',
  'countries-extrude',
  'country-hubs',
  'semantic-hubs',
  'trace-hubs',
  'relations',
]);
const capturedClicks = new Map();
const originalOn = maplibregl.Map.prototype.on;
maplibregl.Map.prototype.on = function (type, layerId, listener, ...rest) {
  if (type === 'click' && typeof layerId === 'string' && CAPTURED_CLICK_LAYERS.has(layerId) && typeof listener === 'function') {
    capturedClicks.set(layerId, { map:this, listener });
  }
  return originalOn.call(this, type, layerId, listener, ...rest);
};

const coreUrl = new URL('./3d-app-core.js', import.meta.url);
const version = new URL(import.meta.url).searchParams.get('v');
if (version) coreUrl.searchParams.set('v', version);
try { await import(coreUrl.href); }
finally { maplibregl.Map.prototype.on = originalOn; }

const map = window.__potatoAtlasMap || [...capturedClicks.values()][0]?.map;
let handedOff = false;

function routedEvent(event, feature) {
  const routed = Object.create(event || null);
  Object.defineProperty(routed, 'features', { value:[feature], configurable:true });
  return routed;
}
function invokeCaptured(layerId, event, feature) {
  const listener = capturedClicks.get(layerId)?.listener;
  if (listener) listener(routedEvent(event, feature));
}
function detachCapturedClicks() {
  for (const [layerId, captured] of capturedClicks) {
    const { listener } = captured;
    captured.map.off('click', layerId, listener);
  }
}

function handoffCoreInteractions(interaction) {
  if (handedOff || !interaction?.register || !map) return false;
  detachCapturedClicks();

  interaction.register('core-country-fallback', {
    layers:['countries-fill', 'countries-extrude'],
    objectType:'country',
    clickPriority:5,
    hoverPriority:5,
    claimOverlay:false,
    onClick:(event, feature, winner) => invokeCaptured(winner.layerId, event, feature),
  });
  interaction.register('core-country-hubs', {
    layers:['country-hubs'],
    objectType:'country',
    clickPriority:15,
    hoverPriority:15,
    onClick:(event, feature) => invokeCaptured('country-hubs', event, feature),
  });
  interaction.register('core-semantic-hubs', {
    layers:['semantic-hubs'],
    objectType:'semantic-hub',
    clickPriority:30,
    hoverPriority:30,
    onClick:(event, feature) => invokeCaptured('semantic-hubs', event, feature),
  });
  interaction.register('core-trace-hubs', {
    layers:['trace-hubs'],
    objectType:'country',
    clickPriority:30,
    hoverPriority:30,
    onClick:(event, feature) => invokeCaptured('trace-hubs', event, feature),
  });
  interaction.register('core-relations', {
    layers:['relations'],
    objectType:'relation',
    clickPriority:25,
    hoverPriority:25,
    onClick:(event, feature) => invokeCaptured('relations', event, feature),
  });
  handedOff = true;
  window.__potatoAtlasCoreInteractionHandoff = { handedOff:true, captured:[...capturedClicks.keys()] };
  return true;
}

window.addEventListener('potato-atlas-interaction-ready', event => {
  handoffCoreInteractions(event?.detail?.interaction || window.__potatoAtlasInteraction);
});
if (window.__potatoAtlasInteraction) handoffCoreInteractions(window.__potatoAtlasInteraction);

export { handoffCoreInteractions };
