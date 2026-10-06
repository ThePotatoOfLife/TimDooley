import assert from 'node:assert/strict';
import fs from 'node:fs';

const read = name => fs.readFileSync(new URL(`../world-map/${name}`, import.meta.url), 'utf8');
const tooltip = read('3d-tooltip.js');
const axis = read('3d-axis.js');
const subdivisions = read('3d-subdivisions.js');

assert.ok(tooltip.includes('function getOrCreateTooltipService'), 'tooltip module must expose a shared get-or-create owner');
assert.ok(tooltip.includes('getOrCreateTooltipService'), 'shared tooltip accessor must be exported');

for (const [label, source, owner] of [
  ['Axis', axis, 'axis'],
]) {
  assert.ok(!source.includes('new maplibregl.Popup'), `${label} must not construct a private transient popup`);
  assert.ok(source.includes('getOrCreateTooltipService'), `${label} must acquire the shared tooltip service`);
  assert.ok(source.includes(`tooltip.nextGeneration('${owner}')`), `${label} must own a tooltip generation`);
  assert.ok(source.includes(`tooltip.show('${owner}'`), `${label} must render through the shared tooltip service`);
  assert.ok(source.includes(`tooltip.invalidate('${owner}-leave')`), `${label} must invalidate on leave`);
}

assert.equal(fs.existsSync(new URL('../world-map/3d-fields.js', import.meta.url)), false, 'retired Fields module must stay deleted');
assert.equal(fs.existsSync(new URL('../world-map/3d-networks.js', import.meta.url)), false, 'retired Networks module must stay deleted');

assert.ok(subdivisions.includes("tooltip.nextGeneration('subdivision')"), 'Subdivisions must own one shared tooltip generation per semantic region');
assert.ok(subdivisions.includes("tooltip.show('subdivision'"), 'Subdivisions must render hover through the shared Tooltip service');
assert.ok(subdivisions.includes("invalidate?.('subdivision-leave')"), 'Subdivisions must invalidate transient hover on leave');
assert.ok(subdivisions.includes("onHover:(event, feature)"), 'Subdivisions must route hover through the Interaction Router');
assert.ok(subdivisions.includes("map.on('mousemove', HIT_ID, onMove)"), 'Subdivision degraded fallback must retain hover parity');
assert.ok(!subdivisions.includes('new maplibregl.Popup'), 'Subdivisions must not own a private popup');

console.log('WORLD MAP SPECIALIST TOOLTIP OWNERSHIP REGRESSION PASSED');
