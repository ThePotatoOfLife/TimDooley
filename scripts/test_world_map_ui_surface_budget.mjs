import assert from 'node:assert/strict';
import { selectVisibleSurfaceIds, surfaceNaturallyVisible } from '../world-map/3d-ui-layout-policy.js';

const rows = [
  {id:'operator', priority:50, visible:true},
  {id:'current-view', priority:10, visible:true},
  {id:'time', priority:20, visible:true},
  {id:'lens', priority:40, visible:false},
  {id:'world-context', priority:30, visible:true},
];

assert.deepEqual(
  selectVisibleSurfaceIds(rows, 3),
  ['current-view','time','world-context'],
  'status budget should preserve the highest-priority visible surfaces',
);
assert.deepEqual(
  selectVisibleSurfaceIds(rows, 4),
  ['current-view','time','world-context','operator'],
);
assert.deepEqual(selectVisibleSurfaceIds(rows, 0), []);
assert.deepEqual(selectVisibleSurfaceIds(rows, Infinity), ['current-view','time','world-context','operator']);

assert.equal(
  surfaceNaturallyVisible({ visible:false, element:{ hidden:false } }),
  true,
  'live element visibility must win over stale registration-time visibility',
);
assert.equal(surfaceNaturallyVisible({ visible:true, element:{ hidden:true } }), false);
assert.equal(surfaceNaturallyVisible({ visible:true }), true, 'registration visibility is only the fallback when no element exists');

console.log('World Map UI surface budget tests passed');
