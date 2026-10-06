import assert from 'node:assert/strict';
import fs from 'node:fs';

const root = new URL('../', import.meta.url);
const guard = fs.readFileSync(new URL('world-map/3d-boot-guard.js', root), 'utf8');
const tooltip = fs.readFileSync(new URL('world-map/3d-tooltip.js', root), 'utf8');

for (const token of [
  'potato-atlas-pointer-dragging',
  'POINTER_DRAG_THRESHOLD_PX',
  'suppressUntilMove',
  '.maplibregl-popup:has(.atlas-hover)',
  "window.addEventListener('pointerdown'",
  "window.addEventListener('pointermove'",
  "window.addEventListener('pointerup'",
  "window.addEventListener('pointercancel'",
  'pointerDragSuppressions',
]) {
  assert.ok(!guard.includes(token), `boot guard must retire hover drag workaround marker: ${token}`);
}

for (const token of [
  "for (const eventName of ['dragstart','zoomstart','rotatestart','pitchstart'])",
  "map.on(eventName, () => invalidate(eventName))",
  "potato-atlas-projection-change",
  "potato-atlas-style-generation",
]) {
  assert.ok(tooltip.includes(token), `shared tooltip must retain motion invalidation marker: ${token}`);
}

assert.ok(!guard.includes('atlas-hover'), 'boot guard must no longer own transient tooltip presentation');

console.log('WORLD MAP POINTER DRAG OWNERSHIP REGRESSION PASSED');
