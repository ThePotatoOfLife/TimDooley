// Legacy Lens compatibility adapter for the World Relational Atlas.
//
// Historical lens/lensOption URLs and __potatoAtlasLenses callers are translated
// into canonical Layer Registry state. This module intentionally owns no country
// paint, feature-state, legend or control surface.

if (!window.__potatoAtlasUrlState) await import('./3d-url-state.js');
const urlState = window.__potatoAtlasUrlState;
urlState.claim('legacy-lens', ['lens','lensOption']);

const layers = window.__potatoAtlasLayers;
const compositor = window.__potatoAtlasCompositor;
if (!layers || !compositor) throw new Error('Legacy Lens adapter requires Layer Registry and Compositor.');
await layers.ready;

const LEGACY_TO_LAYER = Object.freeze({
  'alignment:': 'axis.north',
  'alliances:nato': 'group.nato',
  'alliances:brics': 'group.brics',
  'alliances:aukus': 'group.aukus',
  'alliances:five-eyes': 'group.five-eyes',
  'religion:christian': 'religion.christian',
  'religion:muslim': 'religion.muslim',
  'religion:hindu': 'religion.hindu',
  'religion:buddhist': 'religion.buddhist',
  'religion:jewish': 'religion.jewish',
  'religion:other_religions': 'religion.other',
  'religion:unaffiliated': 'religion.unaffiliated',
  'metric:population': 'stat.population',
  'metric:area': 'stat.area',
});

let state = { id:'neutral', option:'' };

function keyFor(id, option='') {
  return `${String(id || 'neutral')}:${String(option || '')}`;
}
function defaultOption(id) {
  if (id === 'alliances') return 'nato';
  if (id === 'religion') return 'christian';
  if (id === 'metric') return 'population';
  return '';
}
function mappedLayer(id, option='') {
  return LEGACY_TO_LAYER[keyFor(id, option)] || null;
}
function clearLegacyUrl() {
  urlState.patch('legacy-lens', { set:{ lens:null, lensOption:null } });
}
async function setLens(id='neutral', option='') {
  id = String(id || 'neutral');
  option = option || defaultOption(id);
  const layerId = mappedLayer(id, option);

  if (id === 'neutral') {
    layers.reset();
    state = { id:'neutral', option:'' };
  } else if (layerId && layers.get(layerId)?.availability === 'current') {
    layers.activate(layerId);
    state = { id, option };
  } else {
    console.warn(`Legacy Lens ${id}/${option || 'default'} has no canonical current layer; leaving analytical state unchanged.`);
    state = { id, option };
  }

  clearLegacyUrl();
  await compositor.render();
  window.dispatchEvent(new CustomEvent('potato-atlas-lens-change', {
    detail:{ ...state, compatibility:true, canonicalLayer:layerId },
  }));
  return Boolean(id === 'neutral' || layerId);
}
async function restoreLegacyState() {
  const params = new URL(location.href).searchParams;
  const id = params.get('lens');
  if (!id) return false;
  const option = params.get('lensOption') || defaultOption(id);
  return setLens(id, option);
}

window.__potatoAtlasLenses = {
  setLens,
  getState() { return { ...state }; },
  mappedLayer,
  refresh() { return compositor.render(); },
};

await restoreLegacyState();
