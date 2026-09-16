import assert from 'node:assert/strict';
import { createRuntimeTelemetry } from '../world-map/3d-runtime-telemetry.js';

let style = {
  sources:{
    countries:{type:'geojson'},
    basemap:{type:'vector'},
  },
  layers:[
    {id:'countries-fill', type:'fill'},
    {id:'country-labels', type:'symbol'},
    {id:'hidden-debug', type:'line', layout:{visibility:'none'}},
  ],
};
const map = { getStyle:() => style };
const interaction = {
  diagnostics:() => ({ registrationCount:5, enabledCount:5, clickOwnerCount:4, hoverOwnerCount:5, layerCount:8, clickDispatches:2, hoverDispatches:7, activeHoverOwner:'places' }),
};
const styleLifecycle = {
  state:() => ({ generation:3, restoreRuns:9, styleEvents:4, registrations:[{owner:'water'},{owner:'render-stack'}] }),
};
const published = [];
const telemetry = createRuntimeTelemetry(map, {
  interaction,
  styleLifecycle,
  bind:false,
  publish:snapshot => published.push(snapshot),
});

let state = telemetry.state();
assert.equal(state.sourceCount, 2);
assert.equal(state.layerCount, 3);
assert.equal(state.visibleLayerCount, 2);
assert.deepEqual(state.layerTypes, {fill:1, line:1, symbol:1});
assert.deepEqual(state.sourceTypes, {geojson:1, vector:1});
assert.equal(state.interaction.registrationCount, 5);
assert.equal(state.style.generation, 3);
assert.equal(state.style.restoreRuns, 9);
assert.equal(state.sampleCount, 1, 'runtime telemetry must publish an initial snapshot');
assert.equal(state.reason, 'init');
assert.equal(published.length, 1);

style = {
  sources:{countries:{type:'geojson'}},
  layers:[{id:'countries-fill', type:'fill'}],
};
state = telemetry.refresh('module-ready');
assert.equal(state.sourceCount, 1);
assert.equal(state.layerCount, 1);
assert.equal(state.visibleLayerCount, 1);
assert.equal(state.sampleCount, 2);
assert.equal(state.reason, 'module-ready');
assert.equal(published.length, 2);

telemetry.destroy();
console.log('WORLD MAP RUNTIME TELEMETRY REGRESSION PASSED');
