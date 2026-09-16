import assert from 'node:assert/strict';
import fs from 'node:fs';

const scale = fs.readFileSync(new URL('../world-map/3d-scale.js', import.meta.url), 'utf8');
const subdivisions = fs.readFileSync(new URL('../world-map/3d-subdivisions.js', import.meta.url), 'utf8');
const places = fs.readFileSync(new URL('../world-map/3d-places.js', import.meta.url), 'utf8');

assert.ok(scale.includes('function bandThreshold'), 'Scale runtime must expose named band thresholds');

for (const [source, label] of [[subdivisions,'Subdivisions'], [places,'Places']]) {
  assert.ok(source.includes('const scale = await scaleRuntime()'), `${label} must resolve the shared Scale runtime`);
}

assert.ok(subdivisions.includes("scale.threshold('subdivisions', 'render')"), 'Subdivisions render threshold must come from Scale Contract');
assert.ok(subdivisions.includes("scale.threshold('subdivisions', 'label')"), 'Subdivisions label threshold must come from Scale Contract');
assert.ok(subdivisions.includes("scale.bandThreshold('subnational')"), 'Subdivision name promotion must use the named subnational band');
assert.match(subdivisions, /minzoom:\s*renderZoom/, 'Subdivision geometry/hit layers must consume the contract-derived render threshold');
assert.match(subdivisions, /minzoom:\s*labelZoom/, 'Subdivision labels must consume the contract-derived label threshold');
assert.match(subdivisions, /\['step',\['zoom'\],\['get','code'\],nameZoom,\['get','name'\]\]/, 'Subdivision name promotion must consume the contract-derived named-band threshold');

assert.ok(places.includes("scale.threshold('places-detail', 'render')"), 'Places detail render threshold must come from Scale Contract');
assert.ok(places.includes("scale.threshold('places-detail', 'label')"), 'Places detail label threshold must come from Scale Contract');
assert.match(places, /minzoom:\s*PLACE_DETAIL_RENDER_ZOOM/, 'Places detail geometry must consume the contract-derived render threshold');
assert.match(places, /minzoom:\s*PLACE_DETAIL_LABEL_ZOOM/, 'Places detail labels must consume the contract-derived label threshold');

for (const raw of ['minzoom:3.4', 'minzoom:4.25']) assert.ok(!subdivisions.includes(raw), `Subdivisions still duplicates raw threshold ${raw}`);
for (const raw of ['minzoom:4.2', 'minzoom:5.0']) assert.ok(!places.includes(raw), `Places still duplicates raw threshold ${raw}`);

console.log('WORLD MAP SCALE LAYER OWNERSHIP REGRESSION PASSED');
