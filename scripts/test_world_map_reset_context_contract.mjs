import assert from 'node:assert/strict';
import fs from 'node:fs';

const root = new URL('../', import.meta.url);
const state = fs.readFileSync(new URL('world-map/3d-map-state.js', root), 'utf8');
const pinned = fs.readFileSync(new URL('world-map/3d-pinned-context.js', root), 'utf8');

assert.ok(state.includes("runStep('investigation'"), 'map reset should explicitly close temporary investigations');
assert.ok(state.includes('__potatoAtlasInvestigationSurface?.closeActive'), 'map reset should use the shared investigation coordinator');
assert.ok(state.includes("runStep('pinned-context'"), 'map reset should reset transient pinned-context presentation state');
assert.ok(state.includes('__potatoAtlasPinnedContext?.collapse'), 'map reset should collapse expanded pinned context');
assert.ok(pinned.includes('collapse'), 'pinned context API should expose collapse');
assert.ok(pinned.includes('expanded = false'), 'pinned context collapse should restore bounded presentation');

console.log('World Map reset context contract tests passed');
