import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as geo from '../world-map/3d-geo-kernel.js';

const source = fs.readFileSync(new URL('../world-map/3d-subdivisions.js', import.meta.url), 'utf8');
const lifecycle = fs.readFileSync(new URL('../world-map/3d-panel-lifecycle.js', import.meta.url), 'utf8');

function extractFunction(name) {
  const marker = `function ${name}(`;
  const start = source.indexOf(marker);
  assert.ok(start >= 0, `missing ${name} in world-map/3d-subdivisions.js`);
  const bodyStart = source.indexOf('{', start);
  let depth = 0;
  let quote = null;
  let escaped = false;
  for (let i = bodyStart; i < source.length; i += 1) {
    const char = source[i];
    if (quote) {
      if (escaped) { escaped = false; continue; }
      if (char === '\\') { escaped = true; continue; }
      if (char === quote) quote = null;
      continue;
    }
    if (char === '"' || char === "'" || char === '`') { quote = char; continue; }
    if (char === '{') depth += 1;
    if (char === '}') {
      depth -= 1;
      if (depth === 0) return source.slice(start, i + 1);
    }
  }
  throw new Error(`unterminated ${name}`);
}

const map = {
  getCenter() { return { lng:179, lat:0 }; },
  getBounds() {
    return {
      getWest() { return 178; },
      getEast() { return 181; },
      getSouth() { return -5; },
      getNorth() { return 5; },
    };
  },
};

const distanceToMapCenterKm = new Function(
  'map', 'geo',
  `"use strict"; ${extractFunction('descriptorCenter')} ${extractFunction('distanceToMapCenterKm')} return distanceToMapCenterKm;`,
)(map, geo);

const viewportOverlaps = new Function(
  'map', 'geo',
  `"use strict"; ${extractFunction('unwrappedInterval')} ${extractFunction('viewportOverlaps')} return viewportOverlaps;`,
)(map, geo);

const datelinePartition = { west:-180, east:-178, south:-2, north:2 };
const distance = distanceToMapCenterKm(datelinePartition);
assert.ok(distance > 200 && distance < 225, `expected wrapped distance near 222 km, got ${distance}`);
assert.equal(
  viewportOverlaps(datelinePartition),
  true,
  'viewport crossing +180 must overlap the equivalent -180 partition interval',
);

const farPartition = { west:-80, east:-70, south:-2, north:2 };
assert.ok(distanceToMapCenterKm(farPartition) > 9000);
assert.equal(viewportOverlaps(farPartition), false);

const geoLoad = lifecycle.indexOf("__potatoAtlasLoadModule?.('Geo Kernel', './3d-geo-kernel.js')");
const subdivisionLoad = lifecycle.indexOf("__potatoAtlasLoadModule?.('Subdivisions', './3d-subdivisions.js')");
assert.ok(geoLoad >= 0, 'panel lifecycle must load the shared Geo Kernel');
assert.ok(subdivisionLoad >= 0, 'panel lifecycle must retain lazy Subdivisions loading');
assert.ok(geoLoad < subdivisionLoad, 'Geo Kernel must load before Subdivisions can be promoted');

console.log('WORLD MAP SUBDIVISION WRAP MATH REGRESSION PASSED');
