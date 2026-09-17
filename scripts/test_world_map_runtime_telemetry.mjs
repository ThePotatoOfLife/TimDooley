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
const tooltip = {
  state:() => ({ generation:11, owner:'country', visible:true, lastReason:'show', invalidations:4, staleSuppressions:3 }),
};
const contextVisibility = {
  current:{
    scaleBand:'region',
    question:{investigation:'connections',relationMode:'systems'},
    pinnedCountries:['DNK','CAN'],
    budgets:{activeRelations:11,pinnedRelations:2,totalRelations:30},
  },
};
const published = [];
const telemetry = createRuntimeTelemetry(map, {
  interaction,
  styleLifecycle,
  tooltip,
  contextVisibility,
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
assert.equal(state.tooltip.generation, 11, 'runtime telemetry must expose tooltip generation');
assert.equal(state.tooltip.invalidations, 4, 'runtime telemetry must expose tooltip invalidation count');
assert.equal(state.tooltip.staleSuppressions, 3, 'runtime telemetry must expose stale async suppression count');
assert.equal(state.context.scaleBand, 'region', 'runtime telemetry must expose semantic scale context');
assert.equal(state.context.investigation, 'connections', 'runtime telemetry must expose current investigation mode');
assert.equal(state.context.pinCount, 2, 'runtime telemetry must expose retained-country count');
assert.equal(state.context.totalRelations, 30, 'runtime telemetry must expose relation display budget');
assert.equal(state.sampleCount, 1, 'runtime telemetry must publish an initial snapshot');
assert.equal(state.reason, 'init');
assert.equal(published.length, 1);

style = {
  sources:{countries:{type:'geojson'}},
  layers:[{id:'countries-fill', type:'fill'}],
};
contextVisibility.current = {
  scaleBand:'local',
  question:{investigation:'browse',relationMode:'all'},
  pinnedCountries:[],
  budgets:{activeRelations:4,pinnedRelations:1,totalRelations:12},
};
state = telemetry.refresh('context-visibility');
assert.equal(state.sourceCount, 1);
assert.equal(state.layerCount, 1);
assert.equal(state.visibleLayerCount, 1);
assert.equal(state.tooltip.owner, 'country');
assert.equal(state.context.scaleBand, 'local');
assert.equal(state.context.investigation, 'browse');
assert.equal(state.context.pinCount, 0);
assert.equal(state.sampleCount, 2);
assert.equal(state.reason, 'context-visibility');
assert.equal(published.length, 2);

telemetry.destroy();
console.log('WORLD MAP RUNTIME TELEMETRY REGRESSION PASSED');
