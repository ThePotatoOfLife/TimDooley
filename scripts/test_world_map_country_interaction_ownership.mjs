import assert from 'node:assert/strict';
import fs from 'node:fs';

const source = fs.readFileSync(new URL('../world-map/3d-country-interaction.js', import.meta.url), 'utf8');

assert.ok(source.includes('const interaction = window.__potatoAtlasInteraction'), 'country interaction must consume the shared Interaction Router');
assert.ok(source.includes("interaction.register('countries'"), 'country polygons need one shared interaction owner');
assert.ok(source.includes("objectType:'country'"), 'country polygons must declare their semantic object type');
assert.ok(source.includes('clickPriority:10'), 'country polygons must remain the lowest-priority selectable geographic target');
assert.ok(source.includes('hoverPriority:10'), 'country hover priority must match base-country semantics');
assert.ok(source.includes("layers:['countries-fill','countries-extrude']"), 'both flat and extruded country surfaces must share one owner');

for (const [owner, layer, priority, action] of [
  ['core-country-hubs', 'country-hubs', 65, 'countryHub'],
  ['core-semantic-hubs', 'semantic-hubs', 65, 'semanticHub'],
  ['core-trace-hubs', 'trace-hubs', 55, 'traceHub'],
  ['core-relations', 'relations', 50, 'relation'],
]) {
  assert.ok(source.includes(`interaction.register('${owner}'`), `${owner} must own its semantic map target`);
  assert.ok(source.includes(`layers:['${layer}']`), `${owner} must arbitrate ${layer}`);
  assert.ok(source.includes(`clickPriority:${priority}`), `${owner} must preserve semantic priority ${priority}`);
  assert.ok(source.includes(`window.__potatoAtlasCoreInteractions?.${action}?.(feature)`), `${owner} must invoke its canonical core semantic action`);
}

assert.ok(source.includes('const selection = window.__potatoAtlasSelection'), 'country bridge must resolve the current working-selection API at click time');
assert.ok(source.includes("typeof selection?.activate === 'function'"), 'working-selection activation must be preferred once its controller is loaded');
assert.ok(source.includes('selection?.togglePinnedCountry?.(code)'), 'shift-click pin semantics must be preserved through the router');
assert.ok(source.includes("document.getElementById('compare')?.classList.contains('active')"), 'compare-mode clicks must continue delegating to the public country action');
assert.ok(source.includes('await window.goCountry?.(code)'), 'core-boot and compare fallbacks must retain the canonical public country action');
assert.ok(source.includes('map.jumpTo(camera)'), 'router migration must preserve browse camera position after working-selection activation');
assert.ok(!source.includes('Legacy core overlay actions remain direct until their dedicated migration'), 'retired temporary compatibility wording must stay removed');
assert.ok(!source.includes('onClick:() => {}'), 'core map targets must not regress to compatibility no-ops');
assert.ok(!source.includes("map.on('click'"), 'country bridge must not create another direct click owner');

console.log('WORLD MAP COUNTRY INTERACTION OWNERSHIP REGRESSION PASSED');
