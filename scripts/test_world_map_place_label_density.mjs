import assert from 'node:assert/strict';
import fs from 'node:fs';

const source = fs.readFileSync(new URL('../world-map/3d-places.js', import.meta.url), 'utf8');

assert.ok(source.includes("'symbol-sort-key'"), 'major place labels must have deterministic collision priority');
assert.ok(source.includes("['boolean',['get','is_national_capital'],false]"), 'national-capital status must participate in label priority');
assert.ok(source.includes("['coalesce',['to-number',['get','population']],0]"), 'population must break ties between place labels');
assert.ok(source.includes("'text-variable-anchor':['top','bottom','left','right']"), 'major labels must be able to move around their point to avoid collisions');
assert.ok(source.includes("'text-padding':['interpolate',['linear'],['zoom'],1.2,5,6,2]"), 'major labels must reserve more collision space at regional/world scale');
assert.ok(source.includes("'text-variable-anchor':['top','bottom','left','right']"), 'detail labels must use collision-friendly anchors too');
assert.ok(source.includes("'text-padding':3"), 'detail labels must keep explicit collision spacing');
assert.ok(source.includes("'text-allow-overlap':false"), 'place labels must remain collision-aware');

console.log('WORLD MAP PLACE LABEL DENSITY REGRESSION PASSED');
