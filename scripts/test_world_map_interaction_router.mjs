import assert from 'node:assert/strict';
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

// Deliberately put the country first and the place last: semantic priority, not
// renderer return order, must choose the interaction target.
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
assert.equal(originalEvent.__potatoAtlasOverlayHandled, true, 'router must preserve the legacy claim flag while unmigrated country handlers remain');

const state = router.state();
assert.ok(state.some(row => row.owner === 'place' && row.clickPriority === 80));
assert.ok(state.some(row => row.owner === 'overlay' && row.objectType === 'spatial-overlay'));

console.log('WORLD MAP INTERACTION ROUTER REGRESSION PASSED');
