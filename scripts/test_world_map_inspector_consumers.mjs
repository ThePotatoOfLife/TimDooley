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
assert.ok(places.includes("type:'place'"));
assert.ok(places.includes("owner:'places'"));
assert.ok(places.includes("type:'subdivision'"));
assert.ok(subdivisions.includes("type:'subdivision'"));
assert.ok(subdivisions.includes("owner:'subdivisions'"));
assert.ok(places.includes("urlState.patch('selection-inspector'"), 'Places must delegate URL mutation to the canonical URL State owner');
assert.ok(subdivisions.includes("urlState.patch('selection-inspector'"), 'Subdivisions must delegate URL mutation to the canonical URL State owner');
assert.ok(!places.includes("history.replaceState("), 'Places must not write browser history directly');
assert.ok(!subdivisions.includes("history.replaceState("), 'Subdivisions must not write browser history directly');

console.log('WORLD MAP INSPECTOR CONSUMER REGRESSION PASSED');
