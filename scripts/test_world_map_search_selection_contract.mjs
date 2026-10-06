import assert from 'node:assert/strict';
import fs from 'node:fs';

const source = fs.readFileSync(new URL('../world-map/3d-search.js', import.meta.url), 'utf8');

assert.ok(source.includes('await window.goCountry(code)'), 'country search focus must await the canonical async country navigation');
assert.ok(source.includes('return Boolean(await window.goCountry(code))'), 'country search should report the actual selection result');
assert.ok(source.includes('suggestionGeneration'), 'search suggestions should suppress stale async results');
assert.ok(source.includes('__potatoAtlasSubdivisions?.select'), 'subdivision search must delegate to the subdivision owner');
assert.ok(source.includes('__potatoAtlasPlaces?.focus'), 'place search must delegate to the places owner');

console.log('World Map search selection contract tests passed');
