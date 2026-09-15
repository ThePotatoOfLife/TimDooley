import assert from 'node:assert/strict';
import fs from 'node:fs';

const source = fs.readFileSync(new URL('../world-map/3d-axis.js', import.meta.url), 'utf8');

assert.ok(source.includes("import('./3d-tooltip.js')"), 'Axis must be able to initialize the shared Tooltip Service on direct loads');
assert.ok(source.includes('window.__potatoAtlasTooltip'), 'Axis must reuse the shared transient tooltip owner');
assert.ok(source.includes("tooltip.nextGeneration('axis')"), 'Axis hover must claim a fresh generation');
assert.ok(source.includes("tooltip.show('axis'"), 'Axis hover must render through the shared service');
assert.ok(source.includes("tooltip.invalidate('axis-leave')"), 'Axis leave must invalidate stale hover generations');
assert.ok(!source.includes('new maplibregl.Popup'), 'Axis must not construct a private transient popup');
assert.ok(source.includes("map.on('click',AXIS_GATE,openGate)"), 'persistent Axis gate click behavior must remain separate from transient tooltip migration');
assert.ok(source.includes("map.on('click',AXIS_FILL,openGate)"), 'Axis fill click behavior must remain intact');

console.log('WORLD MAP AXIS TOOLTIP OWNERSHIP REGRESSION PASSED');
