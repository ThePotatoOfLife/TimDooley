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
assert.equal(countCall('subdivision','DK-83'), subdivisionBefore + 1);
const placeBefore = countCall('place','place:haderslev');
assert.equal(router.open(place), true);
assert.deepEqual(router.state().stack.map(row => `${row.type}:${row.id}`), ['country:DNK','subdivision:DK-83','place:place:haderslev']);
assert.equal(countCall('place','place:haderslev'), placeBefore + 1);
const refreshBefore = countCall('place','place:haderslev');
assert.equal(router.open(place), true);
assert.deepEqual(router.state().stack.map(row => `${row.type}:${row.id}`), ['country:DNK','subdivision:DK-83','place:place:haderslev']);
assert.equal(countCall('place','place:haderslev'), refreshBefore + 1);
const subdivisionBackBefore = countCall('subdivision','DK-83');
assert.equal(router.back(), true);
assert.deepEqual(router.state().stack.map(row => `${row.type}:${row.id}`), ['country:DNK','subdivision:DK-83']);
assert.equal(countCall('subdivision','DK-83'), subdivisionBackBefore + 1);
router.open(place);
router.open({type:'subdivision', id:'DK-84', owner:'subdivisions', parent:{type:'country', id:'DNK'}, render:() => calls.push(['subdivision','DK-84'])});
assert.deepEqual(router.state().stack.map(row => `${row.type}:${row.id}`), ['country:DNK','subdivision:DK-84']);
const countryBefore = countCall('country','DNK');
assert.equal(router.back(), true);
assert.deepEqual(router.state().stack.map(row => `${row.type}:${row.id}`), ['country:DNK']);
assert.equal(countCall('country','DNK'), countryBefore + 1);
assert.equal(router.back(), false);
const serial = router.state();
assert.equal(typeof serial.stack[0].restore, 'undefined');
assert.equal(typeof serial.stack[0].render, 'undefined');
router.setBaseline({ type:'country', id:'SWE', owner:'country', restore:() => calls.push(['country','SWE']) });
assert.deepEqual(router.state().stack.map(row => `${row.type}:${row.id}`), ['country:SWE']);

// Keyboard/focus contract: opening a child inspector focuses its heading;
// backing out restores the control that invoked the child.
const trigger = { isConnected:true, focused:false, focus(){ this.focused=true; } };
const heading = {
  isConnected:true, focused:false, attrs:new Map(),
  focus(){ this.focused=true; },
  hasAttribute(name){ return this.attrs.has(name); },
  setAttribute(name,value){ this.attrs.set(name,value); },
};
const panel = { querySelector(){ return heading; } };
global.document = {
  activeElement:trigger,
  body:{},
  documentElement:{},
  getElementById(id){ return id === 'panel' ? panel : null; },
};
const focusRouter = createInspectorRouter({emit:()=>{}});
focusRouter.setBaseline({type:'country',id:'DNK',owner:'country',restore:()=>{}});
focusRouter.open({type:'subdivision',id:'DK-83',owner:'subdivisions',parent:{type:'country',id:'DNK'},render:()=>{}});
await Promise.resolve();
assert.equal(heading.focused,true,'opening a child inspector should focus the rendered heading');
focusRouter.back();
await Promise.resolve();
assert.equal(trigger.focused,true,'Inspector Back should restore the invoking control');

console.log('WORLD MAP INSPECTOR ROUTER REGRESSION PASSED');
