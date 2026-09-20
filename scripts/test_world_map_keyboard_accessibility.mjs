import assert from 'node:assert/strict';
import fs from 'node:fs';

const root = new URL('../', import.meta.url);
const read = path => fs.readFileSync(new URL(path, root), 'utf8');

const worldBar = read('world-map/3d-world-bar.js');
const inspector = read('world-map/3d-inspector-visibility.js');
const bootstrap = read('world-map/3d-bootstrap.js');
const accessibility = read('world-map/3d-accessibility-status.js');

for (const token of [
  'function dismissOpenMenu',
  "event?.key !== 'Escape'",
  "stopImmediatePropagation",
  "querySelector(':scope > summary')",
  "bar.addEventListener('keydown', dismissOpenMenu, true)",
]) assert.ok(worldBar.includes(token), `World Bar keyboard dismissal missing ${token}`);

for (const token of [
  'bottom:8px',
  'max-height:calc(100dvh - 60px)',
  'overscroll-behavior:contain',
]) assert.ok(worldBar.includes(token), `small-screen menu bound missing ${token}`);

for (const token of [
  "aria-expanded",
  "aria-controls",
  "aria-hidden",
  "returnFocusOnClose",
  "event?.key !== 'Escape'",
  "stopPropagation",
]) assert.ok(inspector.includes(token), `Inspector focus contract missing ${token}`);

assert.ok(
  bootstrap.includes("loadAfterPaint('Accessibility Status', './3d-accessibility-status.js')"),
  'ordinary bootstrap must load accessible map-state summary',
);
for (const token of [
  "role', 'status'",
  "aria-live', 'polite'",
  "aria-atomic', 'true'",
  'Selected country:',
  'Analytical layers:',
  'Physical layers:',
  'Geography overlays:',
  'Evidence layers:',
  'Relations:',
  'Projection:',
  'Time:',
  'Scale:',
]) assert.ok(accessibility.includes(token), `accessible map-state summary missing ${token}`);
assert.ok(!accessibility.includes('MutationObserver'), 'accessibility summary must remain event-driven');
assert.ok(!accessibility.includes('setInterval('), 'accessibility summary must not poll');

console.log('WORLD MAP KEYBOARD / ACCESSIBILITY CONTRACT PASSED');
