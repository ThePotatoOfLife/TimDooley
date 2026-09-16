import assert from 'node:assert/strict';
import fs from 'node:fs';

const places = fs.readFileSync(new URL('../world-map/3d-places.js', import.meta.url), 'utf8');
const subdivisions = fs.readFileSync(new URL('../world-map/3d-subdivisions.js', import.meta.url), 'utf8');

for (const [label, source] of [['Places', places], ['Subdivisions', subdivisions]]) {
  assert.ok(source.includes('const inspector = window.__potatoAtlasInspector'), `${label} must consume the shared Inspector Router`);
  assert.ok(source.includes('inspector.setBaseline('), `${label} must establish a live country baseline`);
  assert.ok(source.includes('inspector.open('), `${label} must open a typed inspector node`);
  assert.ok(source.includes('inspector.back()'), `${label} close/back must restore semantic parent state`);
  assert.ok(!source.includes('panelSnapshot'), `${label} must not preserve raw panel.innerHTML snapshots`);
}

assert.ok(places.includes("type:'place'"), 'Places must register a typed place inspector node');
assert.ok(places.includes("owner:'places'"), 'Places inspector node must declare its owner');
assert.ok(places.includes("type:'subdivision'"), 'Places must preserve subdivision parent context when present');
assert.ok(subdivisions.includes("type:'subdivision'"), 'Subdivisions must register a typed subdivision inspector node');
assert.ok(subdivisions.includes("owner:'subdivisions'"), 'Subdivision inspector node must declare its owner');
assert.ok(places.includes("url.searchParams.delete('place')"), 'Places close/back must clear its URL state');
assert.ok(subdivisions.includes("url.searchParams.delete('subdivision')"), 'Subdivision close/back must clear its URL state');

console.log('WORLD MAP INSPECTOR CONSUMER REGRESSION PASSED');
