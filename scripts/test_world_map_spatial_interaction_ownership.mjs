import assert from 'node:assert/strict';
import fs from 'node:fs';

const source = fs.readFileSync(new URL('../world-map/3d-spatial-overlays.js', import.meta.url), 'utf8');

assert.ok(source.includes('const interaction = window.__potatoAtlasInteraction'), 'spatial overlays must consume the shared Interaction Router');
assert.ok(source.includes('function syncInteractionRegistration()'), 'spatial overlays need one dynamic interaction registration owner');
assert.ok(source.includes("interaction.register('spatial-overlays'"), 'spatial overlays must register one semantic interaction owner');
assert.ok(source.includes("objectType:'spatial-overlay'"), 'spatial interaction must declare its semantic object type');
assert.ok(source.includes('clickPriority:40'), 'spatial overlays must retain their first-wave priority below subdivisions/places');
assert.ok(source.includes("features:featuresAt(event.point)"), 'one winning spatial owner must still enumerate all overlapping active overlay claims');
assert.ok(!source.includes("map.on('click', layerId"), 'rendered spatial layers must not each attach parallel click listeners after migration');

// Interaction registration must refresh as new dynamic overlay layers are rendered,
// otherwise the router would only know the first set of layer IDs.
const installIndex = source.indexOf('rendered.set(row.id, { sourceId, layerIds });');
const syncIndex = source.indexOf('syncInteractionRegistration();', installIndex);
assert.ok(installIndex >= 0 && syncIndex > installIndex, 'dynamic rendered-layer registration must refresh the shared router');

console.log('WORLD MAP SPATIAL INTERACTION OWNERSHIP REGRESSION PASSED');
