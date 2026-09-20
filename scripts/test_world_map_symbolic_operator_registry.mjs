import assert from 'node:assert/strict';
import fs from 'node:fs';

const symbolic = fs.readFileSync(new URL('../world-map/3d-symbolic-operators.js', import.meta.url), 'utf8');
const registry = fs.readFileSync(new URL('../world-map/3d-layer-registry.js', import.meta.url), 'utf8');

assert.equal(fs.existsSync(new URL('../world-map/3d-fields.js', import.meta.url)), false, 'retired Fields module must stay deleted');
assert.equal(fs.existsSync(new URL('../world-map/3d-networks.js', import.meta.url)), false, 'retired Networks module must stay deleted');

for (const retired of ['axisFieldView', 'empiricalNetworkView']) {
  assert.ok(!symbolic.includes(retired), `symbolic operators must not depend on retired control ${retired}`);
}

for (const marker of [
  "activeRegistrySummary('axis.')",
  "activeRegistrySummary('group.')",
  "activateRegistryLayers(['axis.north','axis.west','axis.east','axis.south'])",
]) {
  assert.ok(symbolic.includes(marker), `symbolic operators missing canonical registry marker: ${marker}`);
}

for (const marker of ['function activate(', 'active() { return [...activeIds]; }', 'get(id) { return byId.get(id) || null; }']) {
  assert.ok(registry.includes(marker), `Layer Registry missing required symbolic-operator API: ${marker}`);
}

console.log('WORLD MAP SYMBOLIC OPERATOR REGISTRY REGRESSION PASSED');
