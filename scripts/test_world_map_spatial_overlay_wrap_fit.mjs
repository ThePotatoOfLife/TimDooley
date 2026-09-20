import assert from 'node:assert/strict';
import fs from 'node:fs';

const source = fs.readFileSync(new URL('../world-map/3d-spatial-overlays.js', import.meta.url), 'utf8');

for (const token of [
  'window.__potatoAtlasGeo',
  'geoKernel.antimeridianAwareBounds',
  'map.getCenter()?.lng',
]) {
  assert.ok(source.includes(token), `spatial overlay fit missing wrap-safe marker: ${token}`);
}

for (const token of [
  'function boundsForFeature',
  'let minX=180,minY=90,maxX=-180,maxY=-90,ok=false',
  'minX=Math.min(minX,bounds[0][0])',
]) {
  assert.ok(!source.includes(token), `spatial overlay fit still contains naïve bounds logic: ${token}`);
}

assert.ok(
  source.includes("const geometries = (fc.features || []).map(feature => feature?.geometry).filter(Boolean);"),
  'spatial overlay fit must aggregate selected geometries before computing wrapped bounds',
);

console.log('WORLD MAP SPATIAL OVERLAY WRAP FIT REGRESSION PASSED');
