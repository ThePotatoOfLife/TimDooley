import assert from 'node:assert/strict';
import fs from 'node:fs';

const guardUrl = new URL('../world-map/3d-boot-guard.js', import.meta.url);
const source = fs.readFileSync(guardUrl, 'utf8');

for (const token of [
  'potato-atlas-pointer-dragging',
  'POINTER_DRAG_THRESHOLD_PX',
  "window.addEventListener('pointerdown'",
  "window.addEventListener('pointermove'",
  "window.addEventListener('pointerup'",
  "window.addEventListener('pointercancel'",
  ".maplibregl-popup:has(.atlas-hover)",
  'suppressUntilMove',
]) {
  assert.ok(source.includes(token), `3d-boot-guard.js missing pointer-drag artifact guard marker: ${token}`);
}

assert.ok(
  source.includes("document.documentElement.classList.toggle(POINTER_DRAG_CLASS"),
  'drag suppression must be represented by one document-level class toggle',
);
assert.ok(
  source.includes("document.querySelector('#map')"),
  'pointer drag suppression must only arm from the map surface',
);

console.log('WORLD MAP POINTER DRAG ARTIFACT REGRESSION PASSED');
