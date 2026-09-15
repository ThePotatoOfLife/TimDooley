import assert from 'node:assert/strict';
import fs from 'node:fs';

const source = fs.readFileSync(new URL('../world-map/3d-gateways.js', import.meta.url), 'utf8');

assert.ok(source.includes('const interaction = window.__potatoAtlasInteraction'), 'Gateways must consume the shared Interaction Router');
assert.ok(source.includes("interaction.register('gateways'"), 'Gateways must register one semantic interaction owner');
assert.ok(source.includes("objectType:'gateway'"), 'Gateways must declare a gateway object type');
assert.ok(source.includes('clickPriority:75'), 'Gateways must sit below Places and above Infrastructure');
assert.ok(source.includes('hoverPriority:75'), 'Gateway pointer semantics must use the same priority');
assert.ok(source.includes('async function handleGatewayClick'), 'Gateway click behavior must be isolated from registration');
assert.ok(source.includes("emitGateway(p.id, gateway)"), 'Gateway change semantics must remain intact');
assert.ok(source.includes("popup.on('close'"), 'Gateway close must still clear active gateway state');
assert.ok(source.includes('Degraded/direct-module fallback'), 'Gateway direct listeners must be fallback-only');

console.log('WORLD MAP GATEWAY INTERACTION OWNERSHIP REGRESSION PASSED');
