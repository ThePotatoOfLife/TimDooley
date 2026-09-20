import assert from 'node:assert/strict';
import fs from 'node:fs';

const lifecycle = fs.readFileSync(new URL('../world-map/3d-panel-lifecycle.js', import.meta.url), 'utf8');
const physical = fs.readFileSync(new URL('../world-map/3d-physical-layers.js', import.meta.url), 'utf8');

assert.equal(
  lifecycle.match(/new MutationObserver\(/g)?.length || 0,
  1,
  'panel lifecycle must remain the one canonical panel MutationObserver owner',
);
assert.equal(fs.existsSync(new URL('../world-map/3d-ui.js', import.meta.url)), false, 'retired Progressive UI must stay deleted');
assert.equal(fs.existsSync(new URL('../world-map/3d-selection-ui.js', import.meta.url)), false, 'retired Selection UI must stay deleted');
assert.ok(
  physical.includes("setPaintProperty('countries-fill', 'fill-opacity'") ||
  physical.includes("setPaintProperty('countries-fill','fill-opacity'") ||
  physical.includes('fill-opacity'),
  'Physical World must retain the canonical country surface-opacity path',
);

console.log('WORLD MAP UI OWNERSHIP REGRESSION PASSED');
