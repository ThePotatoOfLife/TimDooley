import assert from 'node:assert/strict';
import { createInspectorRouter } from '../world-map/3d-inspector-router.js';

const calls = [];
const router = createInspectorRouter({ emit:detail => calls.push(['emit', detail]) });
const countCall = (kind, id) => calls.filter(call => call[0] === kind && call[1] === id).length;

const country = {
  type:'country', id:'DNK', owner:'country',
  restore:() => calls.push(['country','DNK']),
};
const subdivision = {
  type:'subdivision', id:'DK-83', owner:'subdivisions', parent:{type:'country', id:'DNK'},
  render:() => calls.push(['subdivision','DK-83']),
};
const place = {
  type:'place', id:'place:haderslev', owner:'places', parent:{type:'subdivision', id:'DK-83'},
  render:() => calls.push(['place','place:haderslev']),
};

assert.equal(router.setBaseline(country), true);
assert.deepEqual(router.state().stack.map(row => `${row.type}:${row.id}`), ['country:DNK']);

const subdivisionBefore = countCall('subdivision','DK-83');
assert.equal(router.open(subdivision), true);
assert.deepEqual(router.state().stack.map(row => `${row.type}:${row.id}`), ['country:DNK','subdivision:DK-83']);
assert.equal(countCall('subdivision','DK-83'), subdivisionBefore + 1, 'opening subdivision must render it');

const placeBefore = countCall('place','place:haderslev');
assert.equal(router.open(place), true);
assert.deepEqual(router.state().stack.map(row => `${row.type}:${row.id}`), ['country:DNK','subdivision:DK-83','place:place:haderslev']);
assert.equal(countCall('place','place:haderslev'), placeBefore + 1, 'opening place must render it');

const refreshBefore = countCall('place','place:haderslev');
assert.equal(router.open(place), true, 'opening the same semantic node should refresh rather than duplicate it');
assert.deepEqual(router.state().stack.map(row => `${row.type}:${row.id}`), ['country:DNK','subdivision:DK-83','place:place:haderslev']);
assert.equal(countCall('place','place:haderslev'), refreshBefore + 1, 'refreshing same place must rerender without duplicating history');

const subdivisionBackBefore = countCall('subdivision','DK-83');
assert.equal(router.back(), true);
assert.deepEqual(router.state().stack.map(row => `${row.type}:${row.id}`), ['country:DNK','subdivision:DK-83']);
assert.equal(countCall('subdivision','DK-83'), subdivisionBackBefore + 1, 'back from place must rerender subdivision');

const countryBefore = countCall('country','DNK');
assert.equal(router.back(), true);
assert.deepEqual(router.state().stack.map(row => `${row.type}:${row.id}`), ['country:DNK']);
assert.equal(countCall('country','DNK'), countryBefore + 1, 'back from subdivision must restore country');

assert.equal(router.back(), false, 'baseline has nowhere further to go');
assert.deepEqual(router.state().stack.map(row => `${row.type}:${row.id}`), ['country:DNK']);

const serial = router.state();
assert.equal(typeof serial.stack[0].restore, 'undefined', 'state snapshots must not leak callbacks');
assert.equal(typeof serial.stack[0].render, 'undefined', 'state snapshots must stay serializable');

router.setBaseline({ type:'country', id:'SWE', owner:'country', restore:() => calls.push(['country','SWE']) });
assert.deepEqual(router.state().stack.map(row => `${row.type}:${row.id}`), ['country:SWE'], 'new country baseline must reset stale child history');

console.log('WORLD MAP INSPECTOR ROUTER REGRESSION PASSED');
