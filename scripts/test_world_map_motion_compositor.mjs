import assert from 'node:assert/strict';
import fs from 'node:fs';

const root = new URL('../', import.meta.url);
const loader = fs.readFileSync(new URL('world-map/maplibre-loader.js', root), 'utf8');
const page = fs.readFileSync(new URL('world-map/index.html', root), 'utf8');

for (const token of [
  "const motionClass = 'potato-atlas-map-moving'",
  "super.on('movestart'",
  "super.on('moveend'",
  "super.on('remove'",
]) assert.ok(loader.includes(token), `MapLibre motion compositor missing ${token}`);

assert.ok(
  page.includes('html.potato-atlas-map-moving .mapwrap *{backdrop-filter:none!important;box-shadow:none!important;transition:none!important}'),
  'map shell must disable expensive decorative compositing while the camera is moving',
);

console.log('WORLD MAP MOTION COMPOSITOR REGRESSION PASSED');
