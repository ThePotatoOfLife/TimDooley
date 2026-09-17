import assert from 'node:assert/strict';
import fs from 'node:fs';

const source = fs.readFileSync(new URL('../world-map/3d-pinned-context.js', import.meta.url), 'utf8');

assert.match(source, /Promise\.all\(/, 'pinned country views should resolve in parallel');
assert.doesNotMatch(source, /setTimeout/, 'pinned context must stay event-driven instead of polling');
assert.match(source, /potato-atlas-active-view-change/, 'pinned context should refresh when Active View publishes data');
assert.match(source, /atlas-pinned-overflow/, 'pinned context should explain hidden overflow instead of silently truncating pins');
assert.match(source, /data-show-all/, 'pinned overflow should let the user temporarily reveal all pinned countries');
assert.match(source, /data-collapse/, 'expanded pinned context should offer a compact collapse action');
assert.match(source, /pinnedContextOverflow/, 'pinned context diagnostics should expose hidden pin count');
assert.match(source, /__potatoAtlasCountryPresentation/, 'pins must consume the shared Country Presentation adapter');
assert.doesNotMatch(source, /function populationObservation/, 'pins must not own a second population resolver');
assert.doesNotMatch(source, /__potatoAtlasDataRuntime\?\.populationObservation/, 'pins must not directly read canonical population runtime');
assert.match(source, /Population ·/, 'pinned country cards must keep population visible even when another map metric is active');
assert.match(source, /populationPrimary/, 'Population as the primary layer must deduplicate the second answer line');

console.log('World Map pinned context contract tests passed');
