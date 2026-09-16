// Shared Interaction Router bridge for core country selection and core semantic map actions.
// Base country stays at priority 10 while higher semantic targets arbitrate above it.

const map = window.__potatoAtlasMap;
const interaction = window.__potatoAtlasInteraction;
if (!map || !interaction?.register) throw new Error('Country interaction requires map and Interaction Router.');

function featureCode(feature) {
  return String(
    feature?.properties?.iso3
    || feature?.properties?.cca3
    || feature?.properties?.ISO_A3
    || feature?.id
    || ''
  ).toUpperCase();
}

function cameraSnapshot() {
  const center = map.getCenter?.();
  return {
    center: center && Number.isFinite(Number(center.lng)) && Number.isFinite(Number(center.lat))
      ? [Number(center.lng), Number(center.lat)]
      : center,
    zoom:Number(map.getZoom?.()),
    bearing:Number(map.getBearing?.()),
    pitch:Number(map.getPitch?.()),
  };
}

async function selectCountry(feature) {
  const code = featureCode(feature);
  if (!code) return false;
  const current = window.__potatoAtlasSelection?.current;
  if (current?.selected && current.code === code && !current.compareMode) {
    window.__potatoAtlasSelection?.clear?.();
    return true;
  }
  const camera = cameraSnapshot();
  await window.goCountry?.(code);
  map.jumpTo(camera);
  return true;
}

interaction.register('countries', {
  layers:['countries-fill','countries-extrude'],
  objectType:'country',
  clickPriority:10,
  hoverPriority:10,
  cursor:'pointer',
  onClick:(_event, feature) => { void selectCountry(feature); },
});

interaction.register('core-country-hubs', {
  layers:['country-hubs'],
  objectType:'country-hub',
  clickPriority:65,
  hoverPriority:65,
  cursor:'pointer',
  onClick:(_event, feature) => { window.__potatoAtlasCoreInteractions?.countryHub?.(feature); },
});
interaction.register('core-semantic-hubs', {
  layers:['semantic-hubs'],
  objectType:'semantic-hub',
  clickPriority:65,
  hoverPriority:65,
  cursor:'pointer',
  onClick:(_event, feature) => { window.__potatoAtlasCoreInteractions?.semanticHub?.(feature); },
});
interaction.register('core-trace-hubs', {
  layers:['trace-hubs'],
  objectType:'trace-hub',
  clickPriority:55,
  hoverPriority:55,
  cursor:'pointer',
  onClick:(_event, feature) => { window.__potatoAtlasCoreInteractions?.traceHub?.(feature); },
});
interaction.register('core-relations', {
  layers:['relations'],
  objectType:'country-relation',
  clickPriority:50,
  hoverPriority:50,
  cursor:'pointer',
  onClick:(_event, feature) => { window.__potatoAtlasCoreInteractions?.relation?.(feature); },
});

window.__potatoAtlasCountryInteraction = Object.freeze({
  selectCountry,
  featureCode,
});
