import assert from 'node:assert/strict';
import fs from 'node:fs';

const source = fs.readFileSync(new URL('../world-map/3d-fields.js', import.meta.url), 'utf8');

assert.ok(source.includes("import('./3d-tooltip.js')"), 'Fields must initialize the shared Tooltip Service on direct loads');
assert.ok(source.includes('window.__potatoAtlasTooltip'), 'Fields must reuse the shared transient tooltip owner');
assert.ok(source.includes("tooltip.nextGeneration('fields')"), 'Fields hover must claim a fresh tooltip generation');
assert.ok(source.includes("tooltip.show('fields'"), 'Fields hover must render through the shared service');
assert.ok(source.includes("tooltip.invalidate('fields-leave')"), 'Fields leave must invalidate stale tooltip state');
assert.ok(source.includes('if(historicalSuppressed)return;'), 'historical suppression must remain intact');
assert.ok(!source.includes('new maplibregl.Popup'), 'Fields must not construct a private transient popup');

console.log('WORLD MAP FIELDS TOOLTIP OWNERSHIP REGRESSION PASSED');
