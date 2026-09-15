import assert from 'node:assert/strict';
import fs from 'node:fs';

const lenses = fs.readFileSync(new URL('../world-map/3d-lenses.js', import.meta.url), 'utf8');

assert.ok(lenses.includes("legend.id = 'atlasLensLegend'"), 'Lens legend must remain a distinct semantic surface');
assert.ok(
  lenses.includes("window.__potatoAtlasUILayout?.register?.({ id:'lens-legend', zone:'left-status'"),
  'Lens legend must register with the shared left-status layout stack',
);
assert.ok(
  lenses.includes("window.__potatoAtlasUILayout?.setVisible?.('lens-legend', !legend.hidden)"),
  'Lens visibility changes must be reported through the layout coordinator',
);
assert.ok(
  !lenses.includes("#atlasLensLegend{position:absolute"),
  'Lens legend must not keep an independent absolute-position owner after layout registration',
);

console.log('WORLD MAP LENS LAYOUT OWNERSHIP REGRESSION PASSED');
