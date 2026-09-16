import assert from 'node:assert/strict';
import fs from 'node:fs';

const source = fs.readFileSync(new URL('../world-map/3d-axis.js', import.meta.url), 'utf8');

assert.ok(source.includes('window.__potatoAtlasInteraction'), 'Axis must consume the shared Interaction Router');
assert.ok(source.includes("interaction.register('axis-gate'"), 'Axis gate needs a dedicated semantic interaction owner');
assert.ok(source.includes("layers:[AXIS_GATE]"), 'Axis gate registration must target only the gate point');
assert.ok(source.includes("objectType:'axis-gate'"), 'Axis gate must declare its semantic object type');
assert.ok(source.includes('clickPriority:58'), 'Axis gate must stay below subdivisions but above ordinary country selection');
assert.ok(source.includes('hoverPriority:58'), 'Axis gate hover must use the same semantic priority');

assert.ok(source.includes("interaction.register('axis-fill'"), 'Axis fill needs a distinct low-priority owner');
assert.ok(source.includes("layers:[AXIS_FILL]"), 'Axis fill registration must target only the broad symbolic fill');
assert.ok(source.includes("objectType:'axis-threshold'"), 'Axis fill must declare symbolic threshold semantics');
assert.ok(source.includes('clickPriority:5'), 'Axis fill must stay below ordinary country polygons so symbolic geography cannot swallow physical selection');
assert.ok(source.includes('hoverPriority:5'), 'Axis fill hover must remain below ordinary geographic targets');

assert.ok(source.includes("interaction.register('axis-line'"), 'Axis arc line hover needs shared arbitration');
assert.ok(source.includes("layers:[AXIS_LINE]"), 'Axis line owner must target only the threshold arc');
assert.ok(source.includes('clickPriority:0'), 'Axis line remains non-click semantic decoration');
assert.ok(source.includes('hoverPriority:25'), 'Axis line hover may outrank broad fill without outranking subdivision targets');

assert.ok(source.includes('onClick:() => openGate()'), 'Axis gate/fill router owners must preserve gate opening behavior');
assert.ok(source.includes('onHover:hoverAxis'), 'Axis hover must route shared tooltip behavior through the interaction router');
assert.ok(source.includes('onLeave:leaveAxis'), 'Axis leave must invalidate shared tooltip state through the router');

for (const direct of [
  "map.on('click',AXIS_GATE",
  "map.on('click',AXIS_FILL",
  "map.on('mouseenter',layer",
  "map.on('mouseleave',layer",
]) {
  assert.ok(!source.includes(direct), `Axis must retire direct interaction ownership: ${direct}`);
}

console.log('WORLD MAP AXIS INTERACTION OWNERSHIP REGRESSION PASSED');
