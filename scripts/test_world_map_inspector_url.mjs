import assert from 'node:assert/strict';
import { encodeInspectorPath, decodeInspectorPath, deriveInspectorPathFromUrl, createInspectorUrlBridge } from '../world-map/3d-inspector-url.js';

const stack = [
  {type:'country', id:'DNK', owner:'country'},
  {type:'subdivision', id:'DK-83', owner:'subdivisions', parent:{type:'country', id:'DNK'}},
  {type:'place', id:'place:haderslev', owner:'places', parent:{type:'subdivision', id:'DK-83'}},
];
const encoded = encodeInspectorPath(stack);
assert.equal(encoded, 'country:DNK/subdivision:DK-83/place:place%3Ahaderslev');
assert.deepEqual(decodeInspectorPath(encoded).map(node => ({type:node.type,id:node.id,parent:node.parent})), [
  {type:'country', id:'DNK', parent:null},
  {type:'subdivision', id:'DK-83', parent:{type:'country', id:'DNK'}},
  {type:'place', id:'place:haderslev', parent:{type:'subdivision', id:'DK-83'}},
]);
assert.deepEqual(decodeInspectorPath('country:DNK/place:gn%3A123').at(-1).parent, {type:'country',id:'DNK'});
assert.deepEqual(decodeInspectorPath('place:gn%3A123'), [{type:'place',id:'gn:123',parent:null}]);
assert.deepEqual(decodeInspectorPath('country:DNK/bogus:x'), []);
assert.equal(
  encodeInspectorPath([
    {type:'country', id:'USA', owner:'country'},
    {type:'subdivision', id:'US-CA', owner:'subdivisions', parent:{type:'country',id:'USA'}},
    {type:'evidence', id:'adl-heat:US-CA', owner:'adl-heat', parent:{type:'subdivision',id:'US-CA'}},
  ]),
  'country:USA/subdivision:US-CA/evidence:adl-heat%3AUS-CA'
);
assert.equal(
  encodeInspectorPath([
    {type:'country', id:'USA', owner:'country'},
    {type:'evidence-record', id:'adl:record:1', owner:'adl-heat', parent:{type:'country',id:'USA'}},
  ]),
  'country:USA/evidence-record:adl%3Arecord%3A1'
);
assert.deepEqual(
  decodeInspectorPath('country:USA/subdivision:US-CA/evidence:adl-heat%3AUS-CA').at(-1).parent,
  {type:'subdivision', id:'US-CA'}
);
assert.equal(
  encodeInspectorPath([
    {type:'country', id:'USA', owner:'country'},
    {type:'project-case', id:'mud:1', owner:'mud-below-us', parent:{type:'country',id:'USA'}},
  ]),
  'country:USA/project-case:mud%3A1'
);
assert.equal(
  encodeInspectorPath([
    {type:'spatial-overlay', id:'father.mesopotamia-core', owner:'spatial-overlay-ui'},
  ]),
  'spatial-overlay:father.mesopotamia-core'
);
assert.equal(
  encodeInspectorPath([
    {type:'axis', id:'north-axis', owner:'axis'},
    {type:'axis-depth', id:'D7', owner:'axis-depth', parent:{type:'axis',id:'north-axis'}},
  ]),
  'axis:north-axis/axis-depth:D7'
);

const legacy = new URL('https://example.test/world-map/?country=DNK&subdivision=DK-83&place=place%3Ahaderslev');
assert.equal(deriveInspectorPathFromUrl(legacy), encoded);

let href = 'https://example.test/world-map/?inspect=country%3ADNK%2Fsubdivision%3ADK-83%2Fplace%3Aplace%253Ahaderslev';
const listeners = new Map();
const eventTarget = { addEventListener(type, handler) { listeners.set(type, handler); }, removeEventListener(type) { listeners.delete(type); } };
const replaced = [];
const bridge = createInspectorUrlBridge({ getHref:() => href, replace:url => { href = String(url); replaced.push(href); }, eventTarget });
let hydrated = new URL(href);
assert.equal(hydrated.searchParams.get('country'), 'DNK');
assert.equal(hydrated.searchParams.get('subdivision'), 'DK-83');
assert.equal(hydrated.searchParams.get('place'), 'place:haderslev');
assert.equal(hydrated.searchParams.get('inspect'), encoded);
assert.equal(bridge.state().path, encoded);
listeners.get('potato-atlas-inspector-change')?.({ detail:{stack:stack.slice(0,2), current:stack[1]} });
hydrated = new URL(href);
assert.equal(hydrated.searchParams.get('inspect'), 'country:DNK/subdivision:DK-83');
assert.equal(hydrated.searchParams.has('place'), false);
listeners.get('potato-atlas-inspector-change')?.({ detail:{stack:[stack[0]], current:stack[0]} });
hydrated = new URL(href);
assert.equal(hydrated.searchParams.get('inspect'), 'country:DNK');
assert.equal(hydrated.searchParams.has('subdivision'), false);
assert.equal(hydrated.searchParams.has('place'), false);
assert.ok(replaced.length >= 3);
bridge.destroy();
assert.equal(listeners.has('potato-atlas-inspector-change'), false);
console.log('WORLD MAP INSPECTOR URL REGRESSION PASSED');
