import assert from 'node:assert/strict';
import fs from 'node:fs';
import {
  canonicalWorldCopyLongitude,
  canonicalWorldCopyPoint,
  antimeridianAwareBounds,
} from '../world-map/3d-geo-kernel.js';

const worldBar = fs.readFileSync(new URL('../world-map/3d-world-bar.js', import.meta.url), 'utf8');

// Projection is presentation state: flat maps to Mercator, globe maps to globe,
// and every change is persisted and announced through one shared lifecycle event.
assert.ok(worldBar.includes("projection === 'globe' ? 'globe' : 'mercator'"), 'projection owner must map flat/globe state to MapLibre projection types');
assert.ok(worldBar.includes("url.searchParams.set('projection', projection)"), 'projection state must persist in the URL');
assert.ok(worldBar.includes("potato-atlas-projection-change"), 'projection changes must publish the shared lifecycle event');
assert.ok(worldBar.includes("projection=mode==='globe'?'globe':'flat'"), 'projection API must canonicalize external modes');
assert.ok(worldBar.includes("projection=projection==='globe'?'flat':'globe'"), 'projection toggle must be a two-state transition');

// World copies are presentation copies, never new geographic identities.
for (const visibleLng of [-530, -170, 190, 550]) {
  const identity = canonicalWorldCopyLongitude(visibleLng);
  assert.equal(identity.longitude, -170);
}
assert.deepEqual(canonicalWorldCopyPoint([190,55]), {coordinate:[-170,55],worldCopy:1});
assert.deepEqual(canonicalWorldCopyPoint([-170,55]), {coordinate:[-170,55],worldCopy:0});

// Dateline-local geometry remains local regardless of whether the renderer is flat or globe.
const bounds = antimeridianAwareBounds([[179,-5],[-179,7],[178,1]]);
assert.equal(bounds.crossesAntimeridian, true);
assert.ok(bounds.spanLongitude <= 3, `expected local wrapped bounds, got ${bounds.spanLongitude}°`);

console.log('WORLD MAP PROJECTION CONTRACT REGRESSION PASSED');
