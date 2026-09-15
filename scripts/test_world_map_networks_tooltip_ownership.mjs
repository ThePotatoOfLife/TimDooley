import assert from 'node:assert/strict';
import fs from 'node:fs';

const source = fs.readFileSync(new URL('../world-map/3d-networks.js', import.meta.url), 'utf8');

assert.ok(source.includes("import('./3d-tooltip.js')"), 'Networks must initialize the shared Tooltip Service on direct loads');
assert.ok(source.includes('window.__potatoAtlasTooltip'), 'Networks must reuse the shared transient tooltip owner');
assert.ok(source.includes("tooltip.nextGeneration('networks')"), 'Networks hover must claim a fresh tooltip generation');
assert.ok(source.includes("tooltip.show('networks'"), 'Networks hover must render through the shared service');
assert.ok(source.includes("tooltip.invalidate('networks-leave')"), 'Networks leave must invalidate stale tooltip state');
assert.ok(source.includes('if(historicalSuppressed)return;'), 'historical network suppression must remain intact');
assert.ok(!source.includes('new maplibregl.Popup'), 'Networks must not construct a private transient popup');

console.log('WORLD MAP NETWORKS TOOLTIP OWNERSHIP REGRESSION PASSED');
