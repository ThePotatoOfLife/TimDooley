import assert from 'node:assert/strict';
import fs from 'node:fs';
import { createInteractionRouter } from '../world-map/3d-interaction-router.js';

let rendered = [];
const handlers = new Map();
const map = {
  getLayer(id) { return { id }; },
  getZoom() { return 5; },
  queryRenderedFeatures(_point, options = {}) {
    const allowed = new Set(options.layers || []);
    return rendered.filter(feature => allowed.has(feature.layer.id));
  },
  on(type, handler) { handlers.set(type, handler); },
  getCanvas() { return { style:{} }; },
};

const router = createInteractionRouter(map, { bind:false });
const calls = [];
router.register('country', {
  layers:['countries-fill'], objectType:'country', clickPriority:10, hoverPriority:10,
  onClick:(_event, feature) => calls.push(`country:${feature.properties.id}`),
});
router.register('overlay', {
  layers:['overlay-fill'], objectType:'spatial-overlay', clickPriority:40, hoverPriority:40,
  onClick:(_event, feature) => calls.push(`overlay:${feature.properties.id}`),
});
router.register('subdivision', {
  layers:['subdivision-hit'], objectType:'subdivision', clickPriority:60, hoverPriority:60,
  onClick:(_event, feature) => calls.push(`subdivision:${feature.properties.id}`),
});
router.register('place', {
  layers:['place-point'], objectType:'place', clickPriority:80, hoverPriority:80,
  onClick:(_event, feature) => calls.push(`place:${feature.properties.id}`),
});

const feature = (layer, id) => ({ layer:{id:layer}, properties:{id} });
rendered = [
  feature('countries-fill','DNK'),
  feature('overlay-fill','eden'),
  feature('subdivision-hit','DK-1083'),
  feature('place-point','gn:2618425'),
];
let winner = router.resolve({x:10,y:10}, 'click');
assert.equal(winner.owner, 'place');
assert.equal(winner.objectType, 'place');
assert.equal(winner.feature.properties.id, 'gn:2618425');

rendered = rendered.filter(row => row.layer.id !== 'place-point');
winner = router.resolve({x:10,y:10}, 'click');
assert.equal(winner.owner, 'subdivision');
router.unregister('subdivision');
winner = router.resolve({x:10,y:10}, 'click');
assert.equal(winner.owner, 'overlay');

router.register('disabled-place', {
  layers:['disabled-place-point'], objectType:'place', clickPriority:100,
  enabled:() => false,
});
rendered.unshift(feature('disabled-place-point','disabled'));
winner = router.resolve({x:10,y:10}, 'click');
assert.equal(winner.owner, 'overlay', 'disabled registrations must not win');

const originalEvent = {};
router.dispatch('click', { point:{x:4,y:5}, originalEvent });
assert.deepEqual(calls, ['overlay:eden']);
assert.equal(originalEvent.__potatoAtlasOverlayHandled, true, 'router must preserve the legacy claim flag while degraded direct handlers remain possible');

rendered = [{ layer:{id:'countries-fill'}, properties:{iso3:'DNK', name:'Denmark'} }];
router.dispatch('hover', { point:{x:10,y:10} });
assert.equal(router.currentHover()?.objectType, 'country');
assert.equal(router.currentHover()?.feature?.properties?.iso3, 'DNK', 'hover state must expose the semantic country subject');
rendered = [{ layer:{id:'countries-fill'}, properties:{iso3:'DEU', name:'Germany'} }];
router.dispatch('hover', { point:{x:11,y:10} });
assert.equal(router.currentHover()?.feature?.properties?.iso3, 'DEU', 'id-less country polygons must not collapse into one hover identity');
router.clearHover();
assert.equal(router.currentHover(), null, 'clearing hover must clear the ephemeral subject');

const diagnostics = router.diagnostics();
assert.equal(typeof diagnostics.registrationCount, 'number');
assert.equal(typeof diagnostics.enabledCount, 'number');
assert.equal(typeof diagnostics.clickOwnerCount, 'number');
assert.equal(typeof diagnostics.hoverOwnerCount, 'number');
assert.equal(typeof diagnostics.layerCount, 'number');
assert.equal(typeof diagnostics.clickDispatches, 'number');
assert.equal(typeof diagnostics.hoverDispatches, 'number');
assert.equal(diagnostics.clickDispatches, 1, 'diagnostics must count routed click dispatches');
assert.equal(diagnostics.activeHoverOwner, null);

const state = router.state();
assert.ok(state.some(row => row.owner === 'place' && row.clickPriority === 80));
assert.ok(state.some(row => row.owner === 'overlay' && row.objectType === 'spatial-overlay'));

const lifecycle = fs.readFileSync(new URL('../world-map/3d-panel-lifecycle.js', import.meta.url), 'utf8');
const subdivisions = fs.readFileSync(new URL('../world-map/3d-subdivisions.js', import.meta.url), 'utf8');
const places = fs.readFileSync(new URL('../world-map/3d-places.js', import.meta.url), 'utf8');
const bootstrap = fs.readFileSync(new URL('../world-map/3d-bootstrap.js', import.meta.url), 'utf8');
const app = fs.readFileSync(new URL('../world-map/3d-app.js', import.meta.url), 'utf8');
const handoff = fs.readFileSync(new URL('../world-map/3d-core-interaction-handoff.js', import.meta.url), 'utf8');
const hover = fs.readFileSync(new URL('../world-map/3d-hover.js', import.meta.url), 'utf8');
const countrySelection = fs.readFileSync(new URL('../world-map/3d-country-selection.js', import.meta.url), 'utf8');
const spatialOverlays = fs.readFileSync(new URL('../world-map/3d-spatial-overlays.js', import.meta.url), 'utf8');
const gateways = fs.readFileSync(new URL('../world-map/3d-gateways.js', import.meta.url), 'utf8');
const infrastructure = fs.readFileSync(new URL('../world-map/3d-infrastructure.js', import.meta.url), 'utf8');
const impactActions = fs.readFileSync(new URL('../world-map/3d-impact-actions.js', import.meta.url), 'utf8');
const routerSource = fs.readFileSync(new URL('../world-map/3d-interaction-router.js', import.meta.url), 'utf8');

assert.ok(lifecycle.includes("__potatoAtlasLoadModule?.('Interaction Router', './3d-interaction-router.js')"), 'panel lifecycle must retain the shared Interaction Router preload for standalone/degraded boots');
for (const marker of [
  'function interactionRouter()',
  'function bindSubdivisionFallback()',
  'function unbindSubdivisionFallback()',
  "interaction.register('subdivisions'",
  "window.addEventListener('potato-atlas-interaction-ready'",
  "map.off('click', HIT_ID, subdivisionFallbackHandlers.click)",
  'function inspectorRouter()',
  'const inspector = inspectorRouter();',
]) assert.ok(subdivisions.includes(marker), `subdivision degraded-runtime convergence missing marker: ${marker}`);

for (const marker of [
  'function interactionRouter()',
  'function unbindFallbackLayerEvents()',
  "interaction.register('places'",
  "window.addEventListener('potato-atlas-interaction-ready'",
  "map.off('click', layerId, handlers.click)",
  'function inspectorRouter()',
  'const inspector = inspectorRouter();',
]) assert.ok(places.includes(marker), `Places degraded-runtime convergence missing marker: ${marker}`);

assert.ok(routerSource.includes('potato-atlas-interaction-ready'), 'Interaction Router must publish an explicit ready signal for early-boot handoff');
const bootstrapCapture = bootstrap.indexOf("await import(versionedModule('./3d-core-interaction-handoff.js'))");
const bootstrapHover = bootstrap.indexOf("await import(versionedModule('./3d-hover.js'))");
const bootstrapRouter = bootstrap.indexOf("loadAfterPaint('Interaction Router', './3d-interaction-router.js')");
const bootstrapCountry = bootstrap.indexOf("loadAfterPaint('Country selection', './3d-country-selection.js')");
assert.ok(bootstrapCapture >= 0 && bootstrapHover >= 0 && bootstrapCapture < bootstrapHover, 'bootstrap must arm core interaction capture before the renderer boots');
assert.ok(bootstrapRouter >= 0 && bootstrapCountry >= 0 && bootstrapRouter < bootstrapCountry, 'bootstrap must load Interaction Router before canonical country selection');

assert.ok(app.includes("map.on('click','countries-fill',handleCountryPolygonClick)"), 'canonical core renderer must remain in-place for capture and existing runtime contracts');
for (const marker of [
  'function handoffCoreInteractions(interaction)',
  "interaction.register('core-country-fallback'",
  "interaction.register('core-country-hubs'",
  "interaction.register('core-semantic-hubs'",
  "interaction.register('core-trace-hubs'",
  "interaction.register('core-relations'",
  "map.off('click', layerId, listener)",
  'potato-atlas-core-ready',
  'potato-atlas-interaction-ready',
]) assert.ok(handoff.includes(marker), `core interaction handoff missing marker: ${marker}`);

for (const marker of [
  'function interactionRouter()',
  "interaction.unregister('core-country-fallback')",
  "interaction.register('countries'",
  "objectType:'country'",
  'clickPriority:10',
  'function uninstallClickInterception()',
  "window.addEventListener('potato-atlas-interaction-ready', installCountryInteraction)",
  "map.off('click', layer, interceptPolygonClick)",
]) assert.ok(countrySelection.includes(marker), `country selection Router promotion missing marker: ${marker}`);
assert.ok(countrySelection.includes('__potatoAtlasOverlayHandled = true'), 'country selection degraded fallback must still claim handled direct events');
assert.ok(countrySelection.includes('installClickInterception();'), 'country selection degraded fallback must still install the direct click interception path');

for (const marker of [
  'function interactionRouter()',
  'function unbindFallbackInteraction()',
  "window.addEventListener('potato-atlas-interaction-ready', () => syncInteractionRegistration())",
  "interaction.register('spatial-overlays'",
  "map.off('click', id, handlers.onClick)",
]) assert.ok(spatialOverlays.includes(marker), `spatial overlay Router promotion missing marker: ${marker}`);

for (const marker of [
  "interaction.register('country-hover'",
  "interaction.register('legacy-capitals'",
  'Degraded/direct-module fallback',
]) assert.ok(hover.includes(marker), `hover/capital router migration missing marker: ${marker}`);

for (const marker of [
  'function interactionRouter()',
  'function unbindGatewayFallback()',
  'function syncGatewayInteraction(',
  "interaction.register('system-gateways'",
  "window.addEventListener('potato-atlas-interaction-ready'",
  "map.off('click', POINT_LAYER, gatewayFallbackHandlers.click)",
]) assert.ok(gateways.includes(marker), `Gateway late Router promotion missing marker: ${marker}`);

for (const marker of [
  'function interactionRouter()',
  'function unbindInfrastructureFallback()',
  'function syncInfrastructureInteraction(',
  "interaction.register('infrastructure-context'",
  "window.addEventListener('potato-atlas-interaction-ready'",
  "map.off('click', POINT_LAYER, infrastructureFallbackHandlers.click)",
]) assert.ok(infrastructure.includes(marker), `Infrastructure late Router promotion missing marker: ${marker}`);

assert.ok(!impactActions.includes("map.getLayer('atlas-context-gateways-points')) map.on('click'"), 'Impact Actions must not attach a second Gateway click listener');
assert.ok(impactActions.includes("window.addEventListener('potato-atlas-gateway-change'"), 'Impact Actions must respond to semantic Gateway state');

console.log('WORLD MAP INTERACTION ROUTER REGRESSION PASSED');
