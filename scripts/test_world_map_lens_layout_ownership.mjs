import assert from 'node:assert/strict';
import fs from 'node:fs';

const lenses = fs.readFileSync(new URL('../world-map/3d-lenses.js', import.meta.url), 'utf8');
const layout = fs.readFileSync(new URL('../world-map/3d-ui-layout.js', import.meta.url), 'utf8');

for (const marker of ['LEGACY_TO_LAYER','layers.activate(layerId)','compositor.render()','compatibility:true']) {
  assert.ok(lenses.includes(marker), `legacy Lens adapter missing canonical translation marker: ${marker}`);
}
for (const forbidden of ['setPaintProperty(', 'setFeatureState(', "atlasLensLegend", "atlasLensControl"]) {
  assert.ok(!lenses.includes(forbidden), `legacy Lens adapter must not own live paint/control surface: ${forbidden}`);
}
assert.ok(!layout.includes('atlasLensLegend'), 'UI layout must not reserve a stale Lens legend surface');
assert.ok(!layout.includes('lens-legend'), 'UI layout must not retain the retired Lens legend registration');

console.log('WORLD MAP LENS ADAPTER OWNERSHIP REGRESSION PASSED');
