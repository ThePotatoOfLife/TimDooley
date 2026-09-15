import assert from 'node:assert/strict';
import fs from 'node:fs';

const source = fs.readFileSync(new URL('../world-map/3d-infrastructure.js', import.meta.url), 'utf8');

assert.ok(source.includes('const interaction = window.__potatoAtlasInteraction'), 'Infrastructure must consume the shared Interaction Router');
assert.ok(source.includes("interaction.register('infrastructure'"), 'Infrastructure must register one semantic click owner');
assert.ok(source.includes("objectType:'infrastructure'"), 'Infrastructure must declare its semantic object type');
assert.ok(source.includes('clickPriority:70'), 'Infrastructure must sit below Places and above subdivisions');
assert.ok(source.includes('hoverPriority:70'), 'Infrastructure pointer semantics must use the same priority');
assert.ok(source.includes('async function handleInfrastructureClick'), 'Infrastructure click behavior must stay isolated from registration');
assert.ok(source.includes('await showPopup(asset'), 'Infrastructure must preserve its persistent rich popup behavior');
assert.ok(!source.includes("map.on('click', POINT_LAYER"), 'normal Infrastructure boot must not install a competing direct click owner');
assert.ok(source.includes('Degraded/direct-module fallback'), 'Infrastructure must document any direct listener as fallback-only');

console.log('WORLD MAP INFRASTRUCTURE INTERACTION OWNERSHIP REGRESSION PASSED');
