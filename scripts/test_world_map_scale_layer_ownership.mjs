import assert from 'node:assert/strict';
import fs from 'node:fs';

const scale = fs.readFileSync(new URL('../world-map/3d-scale.js', import.meta.url), 'utf8');
const subdivisions = fs.readFileSync(new URL('../world-map/3d-subdivisions.js', import.meta.url), 'utf8');
const places = fs.readFileSync(new URL('../world-map/3d-places.js', import.meta.url), 'utf8');

assert.ok(scale.includes('function bandThreshold'), 'Scale runtime must expose named band thresholds');

for (const [source, label] of [[subdivisions,'Subdivisions'], [places,'Places']]) {
  assert.ok(source.includes('const scale = await scaleRuntime()'), `${label} must resolve the shared Scale runtime`);
}

assert.ok(subdivisions.includes("const SUBDIVISION_RENDER_ZOOM = scale.threshold('subdivisions', 'render')"));
assert.ok(subdivisions.includes("const SUBDIVISION_LABEL_ZOOM = scale.threshold('subdivisions', 'label')"));
assert.ok(subdivisions.includes("const SUBDIVISION_NAME_ZOOM = scale.bandThreshold('subnational')"));
assert.ok(subdivisions.includes('minzoom:SUBDIVISION_RENDER_ZOOM'));
assert.ok(subdivisions.includes('minzoom:SUBDIVISION_LABEL_ZOOM'));
assert.ok(subdivisions.includes("['step',['zoom'],['get','code'],SUBDIVISION_NAME_ZOOM,['get','name']]"));

assert.ok(places.includes("const PLACE_DETAIL_RENDER_ZOOM = scale.threshold('places-detail', 'render')"));
assert.ok(places.includes("const PLACE_DETAIL_LABEL_ZOOM = scale.threshold('places-detail', 'label')"));
assert.ok(places.includes('minzoom:PLACE_DETAIL_RENDER_ZOOM'));
assert.ok(places.includes('minzoom:PLACE_DETAIL_LABEL_ZOOM'));

for (const raw of ['minzoom:3.4', 'minzoom:4.25']) assert.ok(!subdivisions.includes(raw), `Subdivisions still duplicates raw threshold ${raw}`);
for (const raw of ['minzoom:4.2', 'minzoom:5.0']) assert.ok(!places.includes(raw), `Places still duplicates raw threshold ${raw}`);

console.log('WORLD MAP SCALE LAYER OWNERSHIP REGRESSION PASSED');
