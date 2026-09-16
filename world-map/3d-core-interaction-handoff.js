import * as maplibregl from 'https://unpkg.com/maplibre-gl@6.9.0/dist/maplibre-gl.mjs';

// The core renderer intentionally boots before the optional control plane. Capture
// only its legacy layer-click registrations while it starts, then detach those
// exact listener functions and preserve their behavior behind Interaction Router
// owners as soon as the router is ready.
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
let captureActive = true;
let handedOff = false;

function capturingOn(type, layerId, listener, ...rest) {
  if (captureActive && type === 'click' && typeof layerId === 'string' && CAPTURED_CLICK_LAYERS.has(layerId) && typeof listener === 'function') {
    capturedClicks.set(layerId, { map:this, listener });
  }
  return originalOn.call(this, type, layerId, listener, ...rest);
}
maplibregl.Map.prototype.on = capturingOn;

function stopCapture() {
  captureActive = false;
  if (maplibregl.Map.prototype.on === capturingOn) maplibregl.Map.prototype.on = originalOn;
}

function routedEvent(event, feature) {
  const routed = Object.create(event || null);
  Object.defineProperty(routed, 'features', { value:[feature], configurable:true });
  return routed;
}

function invokeCaptured(layerId, event, feature) {
  const captured = capturedClicks.get(layerId);
  captured?.listener?.call(captured.map, routedEvent(event, feature));
}

function detachCapturedClicks() {
  for (const [layerId, captured] of capturedClicks) {
    const map = captured.map;
    const listener = captured.listener;
    map.off('click', layerId, listener);
  }
}

function handoffCoreInteractions(interaction) {
  if (handedOff || !interaction?.register) return false;
  const map = window.__potatoAtlasMap || [...capturedClicks.values()][0]?.map;
  if (!map) return false;
  stopCapture();
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
  window.__potatoAtlasCoreInteractionHandoff = Object.freeze({
    handedOff:true,
    captured:[...capturedClicks.keys()],
  });
  return true;
}

window.addEventListener('potato-atlas-core-ready', stopCapture, { once:true });
window.addEventListener('potato-atlas-interaction-ready', event => {
  handoffCoreInteractions(event?.detail?.interaction || window.__potatoAtlasInteraction);
});
if (window.__potatoAtlasInteraction) handoffCoreInteractions(window.__potatoAtlasInteraction);

export { handoffCoreInteractions };
