import assert from 'node:assert/strict';
import fs from 'node:fs';

const read = name => fs.readFileSync(new URL(`../world-map/${name}`, import.meta.url), 'utf8');
const layout = read('3d-ui-layout.js');
const ui = read('3d-ui.js');
const worldBar = read('3d-world-bar.js');
const axisDepth = read('3d-axis-depth.js');
const selection = read('3d-country-selection.js');
const lenses = read('3d-lenses.js');
const pathfinder = read('3d-pathfinder.js');
const chain = read('3d-chain-explorer.js');
const impact = read('3d-impact-trace.js');
const landCover = read('3d-physical-land-cover.js');
const hydrology = read('3d-physical-hydrology.js');
const app = read('3d-app.js');

// Visual-only full-canvas effects may remain direct children only when they cannot
// intercept input. The Axis tint is the one intentional current example.
assert.ok(axisDepth.includes("pointer-events:none"), 'Axis tint must remain input-transparent');
assert.ok(axisDepth.includes("tint.id = TINT_ID"), 'Axis tint remains an explicit visual-only surface');

// Legacy compatibility surfaces must be suppressed when their canonical successor
// is live rather than stacking in the same map region.
assert.ok(selection.includes("document.getElementById('atlasSelectionDock')?.style.setProperty('display', 'none', 'important')"), 'working selection must suppress legacy selection dock');
assert.ok(worldBar.includes('body.atlas-registry-ui .hud{display:none!important}'), 'registry toolbar must suppress legacy bottom-left HUD');
assert.ok(worldBar.includes('body.atlas-registry-ui .camera'), 'registry toolbar must suppress legacy camera helper');
assert.ok(ui.includes("id:'axis-compact', zone:'canvas-control'"), 'Axis compact control must register as a canvas control');

// Persistent informational surfaces belong to the shared status stack.
for (const marker of ['world-context','time-state','lens-legend','axis-field-legend','axis-operator-hud']) {
  assert.ok(layout.includes(marker), `layout inventory missing persistent surface ${marker}`);
}
assert.ok(layout.includes('#atlasUILeftStatus>*{position:static!important'), 'shared status host must neutralize child absolute positioning');

// Temporary investigation panels may float bottom-right, but only through the
// shared arbitration surface so Path / Chain / Impact cannot stack there.
for (const [source, id] of [[pathfinder,'path'],[chain,'chain'],[impact,'impact']]) {
  assert.ok(source.includes(`register?.('${id}'`), `${id} must register with investigation surface`);
  assert.ok(source.includes(`open?.('${id}'`), `${id} must claim the temporary investigation slot before showing`);
}

// Physical legends/status chips may originate in mapwrap for compatibility, but
// must immediately hand placement to the UI layout coordinator.
assert.ok(landCover.includes("zone:'left-status'"), 'land-cover legend must use shared status placement');
assert.ok(hydrology.includes("zone:'left-status'"), 'hydrology status must use shared status placement');

// The core loading/error pill is allowed to remain centered because it is lifecycle
// bounded: empty text hides it after successful startup.
assert.ok(app.includes('status.hidden = !message'), 'core status pill must hide when its message clears');
assert.ok(app.includes("setStatus('');"), 'core status pill must clear after successful core load');

console.log('WORLD MAP FLOATER INVENTORY PASSED');
