import assert from 'node:assert/strict';
import fs from 'node:fs';

const lenses = fs.readFileSync(new URL('../world-map/3d-lenses.js', import.meta.url), 'utf8');
const layout = fs.readFileSync(new URL('../world-map/3d-ui-layout.js', import.meta.url), 'utf8');

assert.ok(lenses.includes("legend.id = 'atlasLensLegend'"), 'Lens legend must remain a distinct semantic surface');
assert.ok(
  layout.includes("document.getElementById('atlasLensLegend')"),
  'UI layout coordinator must discover the Lens legend',
);
assert.ok(
  layout.includes("id:'lens-legend', zone:'left-status'"),
  'UI layout coordinator must place the Lens legend in the shared left-status stack',
);
assert.ok(
  layout.includes("window.addEventListener('potato-atlas-module-ready', scheduleRefresh)"),
  'layout must re-adopt surfaces when optional modules such as Lenses arrive',
);
assert.ok(
  layout.includes('#atlasUILeftStatus>*{position:static!important'),
  'hosted status surfaces must have independent absolute positioning neutralized',
);

console.log('WORLD MAP LENS LAYOUT OWNERSHIP REGRESSION PASSED');
