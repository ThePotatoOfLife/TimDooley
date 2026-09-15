import assert from 'node:assert/strict';
import fs from 'node:fs';

const ui = fs.readFileSync(new URL('../world-map/3d-ui.js', import.meta.url), 'utf8');
const lifecycle = fs.readFileSync(new URL('../world-map/3d-panel-lifecycle.js', import.meta.url), 'utf8');
const physical = fs.readFileSync(new URL('../world-map/3d-physical-layers.js', import.meta.url), 'utf8');

assert.equal(
  lifecycle.match(/new MutationObserver\(/g)?.length || 0,
  1,
  'panel lifecycle must remain the one canonical panel MutationObserver owner',
);
assert.equal(
  ui.match(/new MutationObserver\(/g)?.length || 0,
  0,
  'Progressive UI must consume potato-atlas-panel-rendered instead of observing #panel again',
);
assert.ok(
  ui.includes("window.addEventListener('potato-atlas-panel-rendered'"),
  'Progressive UI must consume the canonical panel-render event',
);
assert.ok(
  !ui.includes("setPaintProperty('countries-fill','fill-opacity'") &&
  !ui.includes('setPaintProperty("countries-fill","fill-opacity"'),
  'Progressive UI must not compete with Physical World for countries-fill opacity',
);
assert.ok(
  physical.includes("setPaintProperty('countries-fill', 'fill-opacity'") ||
  physical.includes("setPaintProperty('countries-fill','fill-opacity'") ||
  physical.includes('fill-opacity'),
  'Physical World must retain the canonical country surface-opacity path',
);

console.log('WORLD MAP UI OWNERSHIP REGRESSION PASSED');
