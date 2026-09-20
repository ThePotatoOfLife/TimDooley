import assert from 'node:assert/strict';
import fs from 'node:fs';

const adl = fs.readFileSync(new URL('../world-map/3d-adl-heat.js', import.meta.url), 'utf8');

for (const token of [
  "scale.threshold('adl-heat-points', 'render')",
  "scale.threshold('adl-heat-points', 'interact')",
  'minzoom:pointRenderZoom',
  'minzoom:pointInteractZoom',
  "scale.capabilityActive('adl-heat-points', 'interact'",
]) {
  assert.ok(adl.includes(token), `ADL point scale ownership missing: ${token}`);
}

assert.ok(!adl.includes('source:POINT_SOURCE,minzoom:4.2'), 'ADL point layers must not own raw 4.2 minzoom');
assert.ok(!adl.includes("enabled:()=>enabled,"), 'ADL incident interaction must not ignore canonical scale capability');

console.log('WORLD MAP ADL SCALE OWNERSHIP REGRESSION PASSED');
