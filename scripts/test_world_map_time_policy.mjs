import assert from 'node:assert/strict';
import { normalizeTimeState, describeTimeWindow } from '../world-map/3d-time-policy.js';

assert.deepEqual(normalizeTimeState({mode:'current', time:'2026-01-01', time2:'2026-02-01'}), {
  mode:'current', time:'', time2:'', valid:true, normalized:true, issue:null,
});

assert.deepEqual(normalizeTimeState({mode:'as_of', time:'2026-09-17'}), {
  mode:'as_of', time:'2026-09-17', time2:'', valid:true, normalized:false, issue:null,
});

const reversed = normalizeTimeState({mode:'changed_between', time:'2026-09-17', time2:'2026-01-01'});
assert.equal(reversed.time, '2026-01-01');
assert.equal(reversed.time2, '2026-09-17');
assert.equal(reversed.valid, true);
assert.equal(reversed.normalized, true);
assert.equal(reversed.issue, 'reordered-range');

const invalid = normalizeTimeState({mode:'as_of', time:'2026-02-31'});
assert.equal(invalid.valid, false);
assert.equal(invalid.issue, 'invalid-date');

const incomplete = normalizeTimeState({mode:'changed_between', time:'2026-01-01', time2:''});
assert.equal(incomplete.valid, false);
assert.equal(incomplete.issue, 'missing-range-end');

const window = describeTimeWindow({mode:'changed_between', time:'2026-01-01', time2:'2026-01-31'});
assert.equal(window.kind, 'range');
assert.equal(window.days, 30);
assert.equal(window.label, '2026-01-01 → 2026-01-31');

console.log('World Map time policy tests passed');
