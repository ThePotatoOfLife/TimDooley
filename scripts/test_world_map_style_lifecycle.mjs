import assert from 'node:assert/strict';
import { createStyleLifecycle } from '../world-map/3d-style-lifecycle.js';

const listeners = new Map();
const map = {
  on(name, handler) { listeners.set(name, handler); },
};
const calls = [];
const events = [];
const lifecycle = createStyleLifecycle(map, {
  queue: callback => callback(),
  emit: detail => events.push(detail),
});

assert.equal(listeners.has('styledata'), true, 'style lifecycle must own exactly one map styledata listener');

lifecycle.register('late', { priority:20, restore:({generation}) => calls.push(`late:${generation}`) });
lifecycle.register('early', { priority:10, restore:({generation}) => calls.push(`early:${generation}`) });
assert.equal(lifecycle.state().registrations.length, 2);

listeners.get('styledata')();
assert.deepEqual(calls, ['early:1','late:1'], 'restorers must run deterministically by priority');
assert.equal(lifecycle.state().generation, 1);
assert.equal(lifecycle.state().restoreRuns, 2);
assert.equal(events.at(-1).generation, 1);

calls.length = 0;
lifecycle.unregister('early');
listeners.get('styledata')();
assert.deepEqual(calls, ['late:2'], 'unregistered restorers must stop running');
assert.equal(lifecycle.state().generation, 2);
assert.equal(lifecycle.state().registrations.length, 1);

console.log('WORLD MAP STYLE LIFECYCLE REGRESSION PASSED');
