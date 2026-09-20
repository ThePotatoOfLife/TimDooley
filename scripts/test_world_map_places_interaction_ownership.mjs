import assert from 'node:assert/strict';
import fs from 'node:fs';

const source = fs.readFileSync(new URL('../world-map/3d-places.js', import.meta.url), 'utf8');

assert.ok(source.includes('function interactionRouter()'), 'Places must resolve the shared Interaction Router dynamically');
assert.ok(source.includes('function syncInteractionRegistration()'), 'Places needs one semantic interaction registration');
assert.ok(source.includes("interaction.register('places'"), 'Places must register one shared interaction owner');
assert.ok(source.includes("objectType:'place'"), 'Places must declare its semantic object type');
assert.ok(source.includes('clickPriority:80'), 'Places must stay above subdivisions and spatial overlays');
assert.ok(source.includes('hoverPriority:80'), 'Places hover priority must match its semantic click priority');
assert.ok(source.includes('enabled:() => visible'), 'hidden Places must not remain interactive');
assert.ok(source.includes('function bindFallbackLayerEvents()'), 'direct listeners may exist only as an explicit degraded fallback');
assert.ok(source.includes('function unbindFallbackLayerEvents()'), 'Places fallback listeners must be removable after delayed Router readiness');
assert.ok(source.includes("window.addEventListener('potato-atlas-interaction-ready'"), 'Places must promote from fallback to Router ownership when readiness arrives');
assert.ok(source.includes("map.off('click', layerId, handlers.onClick)"), 'Places promotion must detach degraded click handlers');
assert.ok(source.includes('Degraded/direct-module fallback'), 'fallback ownership must be documented');

const bindStart = source.indexOf('function bindLayerEvents()');
const fallbackStart = source.indexOf('function bindFallbackLayerEvents()');
assert.ok(bindStart >= 0 && fallbackStart >= 0, 'Places interaction functions must exist');
const bindEnd = source.indexOf('\n}', bindStart) + 2;
const bindBody = source.slice(bindStart, bindEnd);
assert.ok(/if \(syncInteractionRegistration\(\)\)\s*\{[^}]*return;[^}]*\}/s.test(bindBody) || bindBody.includes('if (syncInteractionRegistration()) return;'), 'normal Places boot must prefer the router before fallback listeners');
assert.ok(bindBody.includes('bindFallbackLayerEvents();'), 'fallback must be explicit rather than parallel');
assert.ok(!bindBody.includes("map.on('click'"), 'normal bindLayerEvents must not attach its own click owner');

const fallbackEnd = source.indexOf('\n}', fallbackStart) + 2;
const fallbackBody = source.slice(fallbackStart, fallbackEnd);
assert.ok(fallbackBody.includes("map.on('click', layerId"), 'degraded fallback must preserve direct-load click behavior');

console.log('WORLD MAP PLACES INTERACTION OWNERSHIP REGRESSION PASSED');
