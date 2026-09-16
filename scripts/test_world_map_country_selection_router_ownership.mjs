import assert from 'node:assert/strict';
import fs from 'node:fs';

const interaction = fs.readFileSync(new URL('../world-map/3d-country-interaction.js', import.meta.url), 'utf8');
const selection = fs.readFileSync(new URL('../world-map/3d-country-selection.js', import.meta.url), 'utf8');

assert.ok(interaction.includes('async function selectCountry(feature, event = {})'), 'router country action must receive the originating event');
assert.ok(interaction.includes("document.getElementById('compare')?.classList.contains('active')"), 'router country action must preserve compare-mode delegation');
assert.ok(interaction.includes('event?.originalEvent?.shiftKey'), 'router country action must preserve shift-to-pin semantics');
assert.ok(interaction.includes('selection?.activate'), 'router country action must use the working-selection activation API when available');
assert.ok(interaction.includes('selection?.togglePinnedCountry?.(code)'), 'router country action must preserve shift pin toggling');
assert.ok(interaction.includes('onClick:(event, feature) => { void selectCountry(feature, event); }'), 'country router registration must pass the click event to semantic selection');
assert.ok(interaction.includes('map.jumpTo(camera)'), 'ordinary router-owned country activation must preserve browse camera state');

for (const token of [
  'function interceptPolygonClick',
  'function installClickInterception',
  "map.on('click', layer, interceptPolygonClick)",
  'installClickInterception();',
]) {
  assert.ok(!selection.includes(token), `working-selection controller must retire direct polygon click ownership: ${token}`);
}

console.log('WORLD MAP COUNTRY SELECTION ROUTER OWNERSHIP REGRESSION PASSED');
