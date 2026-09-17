import assert from 'node:assert/strict';
import fs from 'node:fs';

const root = new URL('../', import.meta.url);
const status = fs.readFileSync(new URL('world-map/3d-context-status.js', root), 'utf8');
const panel = fs.readFileSync(new URL('world-map/3d-panel-lifecycle.js', root), 'utf8');

for (const token of [
  'atlasContextStatus',
  'potato-atlas-context-visibility-change',
  'potato-atlas-working-selection-change',
  'potato-atlas-interaction-state',
  'atlas-time-change',
  "zone:'left-status'",
  'Current view',
  'Preview',
  'Selected',
  'Population',
  'currentHover',
  '__potatoAtlasActiveView',
]) assert.ok(status.includes(token), `context status missing ${token}`);

assert.ok(status.includes('pinnedCountries.length'), 'status should expose retained-country count');
assert.ok(status.includes('context.question?.investigation'), 'status should expose investigation mode');
assert.ok(status.includes('context.scaleBand'), 'status should expose semantic scale band');
assert.ok(status.includes('context.time'), 'status should expose time context');
assert.ok(status.includes('populationObservation'), 'country subject summary must resolve population from the shared data runtime');
assert.ok(status.includes("hover?.objectType === 'country'"), 'hovered country must outrank selected country only as an ephemeral presentation subject');
assert.ok(status.includes('renderGeneration'), 'async hover/selection summaries need stale-render suppression');
assert.ok(panel.includes('./3d-context-status.js'), 'panel lifecycle should load context status');

console.log('World Map context status contract tests passed');
