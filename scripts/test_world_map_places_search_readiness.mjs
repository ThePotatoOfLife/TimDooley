import assert from 'node:assert/strict';
import fs from 'node:fs';

const search = fs.readFileSync(new URL('../world-map/3d-search.js', import.meta.url), 'utf8');

assert.ok(search.includes('async function placeResults('), 'Places search leg must be async');
assert.ok(search.includes('await api.ready'), 'unified search must wait for the compact Places index to be ready');
assert.ok(
  search.includes('const [countryRowsLoaded, subdivisionRowsLoaded, places] = await Promise.all([')
    && search.includes('placeResults(needle, limit),'),
  'search must await Places results before ranking, including through the shared Promise.all barrier',
);
assert.ok(!search.includes('const places = placeResults(needle, limit);'), 'search must not sample Places synchronously before readiness');

console.log('WORLD MAP PLACES SEARCH READINESS REGRESSION PASSED');
