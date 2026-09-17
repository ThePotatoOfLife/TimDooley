import assert from 'node:assert/strict';
import fs from 'node:fs';

const source = fs.readFileSync(new URL('../world-map/3d-pinned-context.js', import.meta.url), 'utf8');

assert.match(source, /Promise\.all\(/, 'pinned country views should resolve in parallel');
assert.doesNotMatch(source, /setTimeout/, 'pinned context must stay event-driven instead of polling');
assert.match(source, /potato-atlas-active-view-change/, 'pinned context should refresh when Active View publishes data');
assert.match(source, /atlas-pinned-overflow/, 'pinned context should explain hidden overflow instead of silently truncating pins');
assert.match(source, /pinnedContextOverflow/, 'pinned context diagnostics should expose hidden pin count');

console.log('World Map pinned context contract tests passed');
