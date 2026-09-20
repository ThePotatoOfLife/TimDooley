import assert from 'node:assert/strict';
import fs from 'node:fs';

const read = name => fs.readFileSync(new URL(`../world-map/${name}`, import.meta.url), 'utf8');
const tooltip = read('3d-tooltip.js');
const axis = read('3d-axis.js');
const fields = read('3d-fields.js');
const networks = read('3d-networks.js');
const subdivisions = read('3d-subdivisions.js');

assert.ok(tooltip.includes('function getOrCreateTooltipService'), 'tooltip module must expose a shared get-or-create owner');
assert.ok(tooltip.includes('getOrCreateTooltipService'), 'shared tooltip accessor must be exported');

for (const [label, source, owner] of [
  ['Axis', axis, 'axis'],
  ['Fields', fields, 'fields'],
  ['Networks', networks, 'networks'],
]) {
  assert.ok(!source.includes('new maplibregl.Popup'), `${label} must not construct a private transient popup`);
  assert.ok(source.includes('getOrCreateTooltipService'), `${label} must acquire the shared tooltip service`);
  assert.ok(source.includes(`tooltip.nextGeneration('${owner}')`), `${label} must own a tooltip generation`);
  assert.ok(source.includes(`tooltip.show('${owner}'`), `${label} must render through the shared tooltip service`);
  assert.ok(source.includes(`tooltip.invalidate('${owner}-leave')`), `${label} must invalidate on leave`);
}

for (const [label, source, owner] of [['Fields', fields, 'project-fields'], ['Networks', networks, 'empirical-networks']]) {
  assert.ok(source.includes(`interaction.register('${owner}'`), `${label} must route hover through the shared Interaction Router`);
  assert.ok(source.includes('onHover:(event,feature)=>'), `${label} must update hover as the routed feature changes`);
  assert.ok(source.includes('activeHoverKey'), `${label} must track semantic hover identity to avoid generation churn`);
  assert.ok(!source.includes("map.on('mousemove',FILL_ID"), `${label} must not regain a direct fill-layer mousemove listener`);
}

assert.ok(subdivisions.includes("tooltip.nextGeneration('subdivision')"), 'Subdivisions must own one shared tooltip generation per semantic region');
assert.ok(subdivisions.includes("tooltip.show('subdivision'"), 'Subdivisions must render hover through the shared Tooltip service');
assert.ok(subdivisions.includes("invalidate?.('subdivision-leave')"), 'Subdivisions must invalidate transient hover on leave');
assert.ok(subdivisions.includes("onHover:(event, feature)"), 'Subdivisions must route hover through the Interaction Router');
assert.ok(subdivisions.includes("map.on('mousemove', HIT_ID, onMove)"), 'Subdivision degraded fallback must retain hover parity');
assert.ok(!subdivisions.includes('new maplibregl.Popup'), 'Subdivisions must not own a private popup');

console.log('WORLD MAP SPECIALIST TOOLTIP OWNERSHIP REGRESSION PASSED');
