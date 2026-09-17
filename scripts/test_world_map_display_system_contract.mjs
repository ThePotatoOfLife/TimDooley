import assert from 'node:assert/strict';
import fs from 'node:fs';

const root = new URL('../', import.meta.url);
const read = path => fs.readFileSync(new URL(path, root), 'utf8');

const presentationPath = new URL('world-map/3d-country-presentation.js', root);
assert.ok(fs.existsSync(presentationPath), 'shared Country Presentation adapter must exist');

const presentation = read('world-map/3d-country-presentation.js');
const hover = read('world-map/3d-hover.js');
const worldBar = read('world-map/3d-world-bar.js');
const card = read('world-map/3d-country-card.js');
const pins = read('world-map/3d-pinned-context.js');
const pulse = read('world-map/3d-country-pulse.js');
const panel = read('world-map/3d-panel-lifecycle.js');
const bootstrap = read('world-map/3d-bootstrap.js');

for (const token of [
  '__potatoAtlasCountryPresentation',
  'forCountry',
  'currentQuestion',
  'formatPopulation',
  "if (value == null || value === '') return '—';",
  'stat.population',
]) assert.ok(presentation.includes(token), `Country Presentation missing ${token}`);

assert.ok(bootstrap.includes("loadAfterPaint('Country Presentation', './3d-country-presentation.js')"), 'bootstrap must load Country Presentation');
assert.ok(bootstrap.indexOf("loadAfterPaint('Active View', './3d-active-view.js')") < bootstrap.indexOf("loadAfterPaint('Country Presentation', './3d-country-presentation.js')"), 'Country Presentation must load after Active View');
assert.ok(bootstrap.indexOf("loadAfterPaint('Country Presentation', './3d-country-presentation.js')") < bootstrap.indexOf("loadAfterPaint('World Bar', './3d-world-bar.js')"), 'Country Presentation must load before World Bar');

assert.ok(hover.includes('__potatoAtlasCountryPresentation'), 'hover must consume shared Country Presentation');
for (const forbidden of ['Capital:', 'Area:', 'Currency:']) {
  assert.ok(!hover.includes(forbidden), `ordinary country hover must stay minimal: ${forbidden}`);
}

assert.ok(!worldBar.includes('<span>Active</span>'), 'Current Map View must not expose selected-country identity');
assert.ok(worldBar.includes('select a country'), 'relationship context without a subject needs an explicit orientation state');

for (const tab of ['overview','context','connections']) {
  assert.ok(card.includes(`data-country-tab="${tab}"`), `Country Card missing ${tab} tab`);
}
for (const token of ['atlas-country-current-answer','atlas-country-tab-panel','__potatoAtlasCountryPresentation','Population']) {
  assert.ok(card.includes(token), `Country Card missing ${token}`);
}
assert.ok(!card.includes('Pinned comparison'), 'Country Card must not duplicate pinned comparison rail');

assert.ok(pins.includes('__potatoAtlasCountryPresentation'), 'pins must consume shared Country Presentation');
assert.ok(!pins.includes('function populationObservation'), 'pins must not own a second population resolver');
assert.ok(!pins.includes('__potatoAtlasDataRuntime?.populationObservation'), 'pins must not directly resolve population from runtime');

assert.ok(!panel.includes("'Context Status', './3d-context-status.js'"), 'mixed context-status surface must not load');
assert.ok(!pulse.includes('activeMapViewHtml(view)'), 'deep Country Pulse must not repeat Country Card current-map answer');
assert.ok(!pulse.includes('Current map color'), 'deep Country Pulse must not repeat current scalar answer copy');

console.log('World Map display system contract passed');
