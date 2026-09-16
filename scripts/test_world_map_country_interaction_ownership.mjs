import assert from 'node:assert/strict';
import fs from 'node:fs';

const source = fs.readFileSync(new URL('../world-map/3d-country-interaction.js', import.meta.url), 'utf8');

assert.ok(source.includes('const interaction = window.__potatoAtlasInteraction'), 'country interaction must consume the shared Interaction Router');
assert.ok(source.includes("interaction.register('countries'"), 'country polygons need one shared interaction owner');
assert.ok(source.includes("objectType:'country'"), 'country polygons must declare their semantic object type');
assert.ok(source.includes('clickPriority:10'), 'country polygons must remain the lowest-priority selectable map target');
assert.ok(source.includes('hoverPriority:10'), 'country hover priority must match base-country semantics');
assert.ok(source.includes("layers:['countries-fill','countries-extrude']"), 'both flat and extruded country surfaces must share one owner');

for (const [owner, layer, priority] of [
  ['core-country-hubs', 'country-hubs', 65],
  ['core-semantic-hubs', 'semantic-hubs', 65],
  ['core-trace-hubs', 'trace-hubs', 55],
  ['core-relations', 'relations', 50],
]) {
  assert.ok(source.includes(`interaction.register('${owner}'`), `${owner} must block base-country clicks during legacy action migration`);
  assert.ok(source.includes(`layers:['${layer}']`), `${owner} must arbitrate ${layer}`);
  assert.ok(source.includes(`clickPriority:${priority}`), `${owner} must preserve semantic priority ${priority}`);
}

assert.ok(source.includes('window.__potatoAtlasSelection?.current'), 'country bridge must inspect canonical selection state');
assert.ok(source.includes('window.__potatoAtlasSelection?.clear?.()'), 're-clicking a selected country must keep toggle-off semantics');
assert.ok(source.includes('await window.goCountry?.(code)'), 'new country selection must use the canonical public selection action');
assert.ok(source.includes('map.jumpTo(camera)'), 'router migration must preserve click camera position after public selection action');
assert.ok(source.includes('Legacy core overlay actions remain direct until their dedicated migration'), 'temporary compatibility blockers must be explicit');
assert.ok(!source.includes("map.on('click'"), 'country bridge must not create another direct click owner');

console.log('WORLD MAP COUNTRY INTERACTION OWNERSHIP REGRESSION PASSED');
