import assert from 'node:assert/strict';
import { selectVisibleSurfaceIds } from '../world-map/3d-ui-layout-policy.js';

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

console.log('World Map UI surface budget tests passed');
