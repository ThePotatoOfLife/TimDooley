import assert from 'node:assert/strict';
import { createRequestBudget } from '../world-map/3d-request-budget.js';

const budget = createRequestBudget({maxConcurrent:2});
let running = 0;
let maxRunning = 0;
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

const task = value => async () => {
  running += 1;
  maxRunning = Math.max(maxRunning, running);
  await sleep(15);
  running -= 1;
  return value;
};

const values = await Promise.all([
  budget.run('a', task('a')),
  budget.run('b', task('b')),
  budget.run('c', task('c')),
  budget.run('d', task('d')),
]);
assert.deepEqual(values, ['a','b','c','d']);
assert.ok(maxRunning <= 2, 'request budget must enforce max concurrency');

let dedupeRuns = 0;
const same1 = budget.run('same', async () => { dedupeRuns += 1; await sleep(5); return 42; });
const same2 = budget.run('same', async () => { dedupeRuns += 1; return 99; });
assert.equal(await same1, 42);
assert.equal(await same2, 42);
assert.equal(dedupeRuns, 1, 'same in-flight key must de-duplicate');

let cacheRuns = 0;
assert.equal(await budget.run('cached', async () => { cacheRuns += 1; return 'cached-value'; }, {cacheMs:1000}), 'cached-value');
assert.equal(await budget.run('cached', async () => { cacheRuns += 1; return 'wrong'; }, {cacheMs:1000}), 'cached-value');
assert.equal(cacheRuns, 1, 'fresh cache entry must avoid provider work');

const controller = new AbortController();
controller.abort();
await assert.rejects(
  budget.run('aborted', async () => 'nope', {signal:controller.signal}),
  error => error?.name === 'AbortError'
);

const snap = budget.snapshot();
assert.equal(snap.maxConcurrent, 2);
assert.ok(snap.metrics.deduplicated >= 1);
assert.ok(snap.metrics.cacheHits >= 1);
assert.ok(snap.metrics.maxObservedConcurrent <= 2);

console.log('WORLD MAP REQUEST BUDGET REGRESSION PASSED');
