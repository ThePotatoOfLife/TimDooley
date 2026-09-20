import assert from 'node:assert/strict';
import fs from 'node:fs';

const root = new URL('../', import.meta.url);
const read = path => fs.readFileSync(new URL(path, root), 'utf8');

const presentationPath = new URL('world-map/3d-country-presentation.js', root);
const countryHoverPath = new URL('world-map/3d-country-hover-presentation.js', root);
assert.ok(fs.existsSync(presentationPath), 'shared Country Presentation adapter must exist');
assert.ok(fs.existsSync(countryHoverPath), 'dedicated minimal country-hover presentation must exist');

const presentation = read('world-map/3d-country-presentation.js');
const countryHover = read('world-map/3d-country-hover-presentation.js');
const worldBar = read('world-map/3d-world-bar.js');
const card = read('world-map/3d-country-card.js');
const pins = read('world-map/3d-pinned-context.js');
const pulse = read('world-map/3d-country-pulse.js');
const panel = read('world-map/3d-panel-lifecycle.js');
const bootstrap = read('world-map/3d-bootstrap.js');
const gateways = read('world-map/3d-gateways.js');
const infrastructure = read('world-map/3d-infrastructure.js');
const chains = read('world-map/3d-chain-explorer.js');

for (const token of [
  '__potatoAtlasCountryPresentation',
  'forCountry',
  'currentQuestion',
  'formatPopulation',
  "if (value == null || value === '') return '—';",
  'stat.population',
]) assert.ok(presentation.includes(token), `Country Presentation missing ${token}`);
assert.ok(!presentation.includes("import('./3d-country-hover-presentation.js')"), 'Country Presentation must not secretly own hover loading; bootstrap owns module order and versioning');

assert.ok(bootstrap.includes("loadAfterPaint('Country Presentation', './3d-country-presentation.js')"), 'bootstrap must load Country Presentation');
assert.ok(bootstrap.includes("loadAfterPaint('Country Hover Presentation', './3d-country-hover-presentation.js')"), 'bootstrap must explicitly load the minimal country hover replacement');
assert.ok(bootstrap.indexOf("loadAfterPaint('Active View', './3d-active-view.js')") < bootstrap.indexOf("loadAfterPaint('Country Presentation', './3d-country-presentation.js')"), 'Country Presentation must load after Active View');
assert.ok(bootstrap.indexOf("loadAfterPaint('Country Presentation', './3d-country-presentation.js')") < bootstrap.indexOf("loadAfterPaint('Country Hover Presentation', './3d-country-hover-presentation.js')"), 'minimal hover must load after Country Presentation');
assert.ok(bootstrap.indexOf("loadAfterPaint('Country Hover Presentation', './3d-country-hover-presentation.js')") < bootstrap.indexOf("loadAfterPaint('World Bar', './3d-world-bar.js')"), 'minimal hover must install before ordinary analytical browsing surfaces');

for (const token of ['__potatoAtlasCountryPresentation', "unregister('country-hover')", "register('country-hover-presentation'", 'Population ·']) {
  assert.ok(countryHover.includes(token), `minimal country hover missing ${token}`);
}
for (const forbidden of ['Capital:', 'Area:', 'Currency:', 'Government', 'Memberships']) {
  assert.ok(!countryHover.includes(forbidden), `ordinary country hover must stay minimal: ${forbidden}`);
}

assert.ok(!worldBar.includes('<span>Active</span>'), 'Current Map View must not expose selected-country identity');
assert.ok(worldBar.includes('select a country'), 'relationship context without a subject needs an explicit orientation state');
for (const token of [
  "context.setAttribute('role','status')",
  "context.setAttribute('aria-live','polite')",
  '<span>Physical</span>',
  '<span>Geography</span>',
  '<span>Evidence</span>',
  'potato-atlas-evidence-layer-change',
  'potato-atlas-physical-layer-change',
]) assert.ok(worldBar.includes(token), `Current Map View accessibility summary missing ${token}`);

for (const tab of ['overview','context','connections']) {
  assert.ok(card.includes(`data-country-tab="${tab}"`), `Country Card missing ${tab} tab`);
}
for (const token of ['atlas-country-current-answer','atlas-country-tab-panel','__potatoAtlasCountryPresentation','Population','data-country-context-enrichments']) {
  assert.ok(card.includes(token), `Country Card missing ${token}`);
}
assert.ok(!/>\s*Pinned comparison\s*</i.test(card), 'Country Card must not render a duplicate pinned-comparison section');
for (const [owner, source] of [['System Intelligence', gateways], ['Infrastructure', infrastructure]]) {
  assert.ok(source.includes("querySelector('[data-country-context-enrichments]')"), `${owner} must inject into the Country Card Context tab enrichment host`);
  assert.ok(!source.includes("actions.before(section)"), `${owner} must not append specialist context outside the tab system`);
}
assert.ok(chains.includes("[data-country-panel=\"context\"]"), 'Functional Chains must scope Country Card tag upgrades to the Context tab');

assert.ok(pins.includes('__potatoAtlasCountryPresentation'), 'pins must consume shared Country Presentation');
assert.ok(!pins.includes('function populationObservation'), 'pins must not own a second population resolver');
assert.ok(!pins.includes('__potatoAtlasDataRuntime?.populationObservation'), 'pins must not directly resolve population from runtime');

assert.ok(!panel.includes("'Context Status', './3d-context-status.js'"), 'mixed context-status surface must not load');
assert.ok(!pulse.includes('activeMapViewHtml(view)'), 'deep Country Pulse must not repeat Country Card current-map answer');
assert.ok(!pulse.includes('Current map color'), 'deep Country Pulse must not repeat current scalar answer copy');

console.log('World Map display system contract passed');
