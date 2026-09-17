import assert from 'node:assert/strict';
import fs from 'node:fs';

const root = new URL('../', import.meta.url);
const bridgePath = new URL('world-map/3d-compare-state-bridge.js', root);
const contextPath = new URL('world-map/3d-context-visibility.js', root);

assert.ok(fs.existsSync(bridgePath), 'compare state bridge module must exist');

const bridge = fs.readFileSync(bridgePath, 'utf8');
const context = fs.readFileSync(contextPath, 'utf8');

assert.match(bridge, /__potatoAtlasCompare\?\.isActive\?\.\(\)/, 'bridge should derive live compare state from the canonical Compare API');
assert.match(bridge, /Object\.defineProperty\(selection,\s*['"]current['"]/, 'bridge should expose live compareMode through selection.current');
assert.match(bridge, /potato-atlas-compare-change/, 'bridge should publish a compare-state change event');
assert.match(bridge, /potato-atlas-selection-change/, 'bridge should translate core selection/compare changes into the shared compare event');
assert.match(context, /import ['"]\.\/3d-compare-state-bridge\.js['"]/, 'context visibility should load the compare bridge');
assert.match(context, /potato-atlas-compare-change/, 'context visibility should refresh when Compare state changes');

console.log('World Map compare state bridge tests passed');
