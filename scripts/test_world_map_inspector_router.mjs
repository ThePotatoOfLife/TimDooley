import assert from 'node:assert/strict';
import { createInspectorRouter } from '../world-map/3d-inspector-router.js';

const calls = [];
const router = createInspectorRouter({ emit:detail => calls.push(['emit', detail]) });

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

assert.equal(router.open(subdivision), true);
assert.deepEqual(router.state().stack.map(row => `${row.type}:${row.id}`), ['country:DNK','subdivision:DK-83']);
assert.deepEqual(calls.at(-1), ['subdivision','DK-83']);

assert.equal(router.open(place), true);
assert.deepEqual(router.state().stack.map(row => `${row.type}:${row.id}`), ['country:DNK','subdivision:DK-83','place:place:haderslev']);
assert.deepEqual(calls.at(-1), ['place','place:haderslev']);

assert.equal(router.open(place), true, 'opening the same semantic node should refresh rather than duplicate it');
assert.deepEqual(router.state().stack.map(row => `${row.type}:${row.id}`), ['country:DNK','subdivision:DK-83','place:place:haderslev']);

assert.equal(router.back(), true);
assert.deepEqual(router.state().stack.map(row => `${row.type}:${row.id}`), ['country:DNK','subdivision:DK-83']);
assert.deepEqual(calls.at(-1), ['subdivision','DK-83']);

assert.equal(router.back(), true);
assert.deepEqual(router.state().stack.map(row => `${row.type}:${row.id}`), ['country:DNK']);
assert.deepEqual(calls.at(-1), ['country','DNK']);

assert.equal(router.back(), false, 'baseline has nowhere further to go');
assert.deepEqual(router.state().stack.map(row => `${row.type}:${row.id}`), ['country:DNK']);

const serial = router.state();
assert.equal(typeof serial.stack[0].restore, 'undefined', 'state snapshots must not leak callbacks');
assert.equal(typeof serial.stack[0].render, 'undefined', 'state snapshots must stay serializable');

router.setBaseline({ type:'country', id:'SWE', owner:'country', restore:() => calls.push(['country','SWE']) });
assert.deepEqual(router.state().stack.map(row => `${row.type}:${row.id}`), ['country:SWE'], 'new country baseline must reset stale child history');

console.log('WORLD MAP INSPECTOR ROUTER REGRESSION PASSED');
