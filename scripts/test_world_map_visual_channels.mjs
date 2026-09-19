import assert from 'node:assert/strict';
import fs from 'node:fs';

const root = new URL('../', import.meta.url);
const contract = JSON.parse(fs.readFileSync(new URL('data/world-map-visual-channel-contract.json', root), 'utf8'));
const compositor = fs.readFileSync(new URL('world-map/3d-compositor.js', root), 'utf8');
const registry = JSON.parse(fs.readFileSync(new URL('data/world-map-layer-registry.json', root), 'utf8'));

assert.equal(contract.compatibility['pattern+height'].status, 'incompatible-current-renderer');
assert.equal(contract.compatibility['pattern+height'].policy, 'prefer-pattern-flatten-height');
assert.ok(compositor.includes('async function enforceVisualCompatibility(entries)'));
assert.ok(compositor.includes("height.value = 'flat'"));
assert.ok(compositor.includes('height.disabled = incompatible'));
assert.ok(compositor.includes('potato-atlas-visual-channel-resolution'));

for (const row of registry.entries.filter(row => row.availability === 'current')) {
  if (row.kind === 'scalar') assert.equal(row.visual_channel, 'fill', `${row.id} scalar must own fill`);
  if (row.kind === 'set') assert.equal(row.visual_channel, 'pattern', `${row.id} set must own pattern`);
}

console.log('WORLD MAP VISUAL CHANNEL CONTRACT PASSED');
