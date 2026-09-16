import assert from 'node:assert/strict';
import fs from 'node:fs';

const read = path => fs.readFileSync(new URL(`../${path}`, import.meta.url), 'utf8');
const count = (text, token) => text.split(token).length - 1;

const overlayMarker = '__potatoAtlasOverlayHandled';
const deadSubdivisionMarker = '__potatoAtlasSubdivisionHandled';

const runtimePaths = [
  'world-map/3d-app.js',
  'world-map/3d-core-interaction-handoff.js',
  'world-map/3d-interaction-router.js',
  'world-map/3d-country-selection.js',
  'world-map/3d-hover.js',
  'world-map/3d-places.js',
  'world-map/3d-subdivisions.js',
  'world-map/3d-spatial-overlays.js',
];
const runtime = Object.fromEntries(runtimePaths.map(path => [path, read(path)]));

// The compatibility marker has one canonical reader/writer pair in the early
// core renderer. Those handlers are still valid before the router exists.
const app = runtime['world-map/3d-app.js'];
assert.ok(
  app.includes('if(originalEvent?.__potatoAtlasOverlayHandled)return'),
  'core polygon fallback must retain the one compatibility read',
);
assert.equal(count(app, overlayMarker), 2, '3d-app should retain exactly its legacy early-core read/write pair');

// Once the router owns dispatch, captured core listeners must not receive the
// real DOM originalEvent. That keeps legacy handlers behaviorally useful without
// letting them re-claim a click that the router has already arbitrated.
const handoff = runtime['world-map/3d-core-interaction-handoff.js'];
assert.ok(
  handoff.includes("Object.defineProperty(routed, 'originalEvent', { value:null, configurable:true });"),
  'core interaction handoff must shadow originalEvent before invoking captured legacy handlers',
);
assert.ok(!handoff.includes(overlayMarker), 'handoff must isolate the legacy marker without becoming another marker owner');

// Shared router owns the normal-path claim; direct modules may write the marker
// only inside their degraded fallback handlers.
assert.equal(count(runtime['world-map/3d-interaction-router.js'], overlayMarker), 1, 'router should own one normal-path compatibility claim');
assert.equal(count(runtime['world-map/3d-country-selection.js'], overlayMarker), 1, 'country selection should keep one degraded fallback claim');
assert.equal(count(runtime['world-map/3d-hover.js'], overlayMarker), 1, 'legacy capitals should keep one degraded fallback claim');
assert.equal(count(runtime['world-map/3d-places.js'], overlayMarker), 1, 'Places should keep one degraded fallback claim');
assert.equal(count(runtime['world-map/3d-subdivisions.js'], overlayMarker), 1, 'subdivisions should keep one degraded fallback claim');
assert.equal(count(runtime['world-map/3d-spatial-overlays.js'], overlayMarker), 1, 'spatial overlays should keep one degraded fallback claim');

const subdivisions = runtime['world-map/3d-subdivisions.js'];
const subdivisionFallback = subdivisions.indexOf('// Degraded/direct-module fallback');
const subdivisionMarker = subdivisions.indexOf(overlayMarker);
assert.ok(subdivisionFallback >= 0 && subdivisionMarker > subdivisionFallback, 'subdivision marker must live only inside the direct fallback branch');
assert.ok(!subdivisions.slice(0, subdivisionFallback).includes(overlayMarker), 'routed subdivision handling must not write the compatibility marker');

const places = runtime['world-map/3d-places.js'];
assert.ok(places.indexOf(overlayMarker) > places.indexOf('function bindFallbackLayerEvents()'), 'Places marker must remain inside fallback binding only');
const hover = runtime['world-map/3d-hover.js'];
assert.ok(hover.indexOf(overlayMarker) > hover.indexOf('function bindLegacyCapitalDirect()'), 'capital marker must remain inside direct fallback only');
const spatial = runtime['world-map/3d-spatial-overlays.js'];
assert.ok(spatial.indexOf(overlayMarker) > spatial.indexOf('function bindFallbackInteraction(layerIds)'), 'spatial overlay marker must remain inside fallback binding only');

for (const [path, source] of Object.entries(runtime)) {
  assert.ok(!source.includes(deadSubdivisionMarker), `${path} must not retain dead subdivision-specific handled state`);
}

// Marker ownership is centralized here. Broad feature validators must not keep
// the compatibility flag alive as an unrelated required token.
for (const path of [
  'scripts/validate_world_map_3d.py',
  'scripts/validate_world_map_interaction_router.py',
  'scripts/validate_world_map_subdivisions.py',
  'scripts/validate_world_places.py',
]) {
  assert.ok(!read(path).includes(overlayMarker), `${path} must not require the compatibility marker`);
}

console.log('WORLD MAP INTERACTION COMPATIBILITY REGRESSION PASSED');
