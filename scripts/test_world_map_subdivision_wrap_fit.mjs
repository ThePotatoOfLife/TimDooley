import assert from 'node:assert/strict';
import fs from 'node:fs';

const source = fs.readFileSync(new URL('../world-map/3d-subdivisions.js', import.meta.url), 'utf8');

for (const token of [
  'geo.antimeridianAwareBounds',
  'map.getCenter?.()?.lng',
  'Number.isFinite(referenceLng)',
]) {
  assert.ok(source.includes(token), `subdivision fit missing wrap-safe marker: ${token}`);
}

for (const token of [
  'function recursiveBounds',
  'function geometryBounds(feature)',
  'recursiveBounds(feature?.geometry?.coordinates',
]) {
  assert.ok(!source.includes(token), `subdivision fit still contains local naïve bounds logic: ${token}`);
}

assert.ok(
  source.includes('const bounds = subdivisionBounds(feature);'),
  'subdivision selection must route fitting through the shared wrap-safe helper',
);

console.log('WORLD MAP SUBDIVISION WRAP FIT REGRESSION PASSED');
