import assert from 'node:assert/strict';
import fs from 'node:fs';

const guard = fs.readFileSync(new URL('../world-map/3d-boot-guard.js', import.meta.url), 'utf8');
const tooltip = fs.readFileSync(new URL('../world-map/3d-tooltip.js', import.meta.url), 'utf8');
const transientOwners = [
  '../world-map/3d-hover.js',
  '../world-map/3d-axis.js',
  '../world-map/3d-fields.js',
  '../world-map/3d-networks.js',
].map(path => fs.readFileSync(new URL(path, import.meta.url), 'utf8'));

for (const token of [
  'potato-atlas-pointer-dragging',
  'POINTER_DRAG_THRESHOLD_PX',
  '.maplibregl-popup:has(.atlas-hover)',
  'suppressUntilMove',
  "window.addEventListener('pointerdown'",
  "window.addEventListener('pointermove'",
  "window.addEventListener('pointerup'",
  "window.addEventListener('pointercancel'",
]) {
  assert.ok(!guard.includes(token), `retired pointer-drag workaround returned: ${token}`);
}

assert.ok(tooltip.includes("for (const eventName of ['dragstart','zoomstart','rotatestart','pitchstart'])"), 'shared Tooltip Service must own map-motion invalidation');
assert.ok(tooltip.includes("map.on(eventName, () => invalidate(eventName))"), 'map motion must invalidate transient tooltip state directly');

for (const [index, source] of transientOwners.entries()) {
  assert.ok(source.includes('window.__potatoAtlasTooltip'), `transient owner ${index} must consume shared Tooltip Service`);
  assert.ok(!source.includes('new maplibregl.Popup({closeButton:false'), `transient owner ${index} must not construct a private hover popup`);
}

console.log('WORLD MAP POINTER DRAG WORKAROUND RETIREMENT REGRESSION PASSED');
