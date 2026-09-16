import assert from 'node:assert/strict';
import fs from 'node:fs';

const app = fs.readFileSync(new URL('../world-map/3d-app.js', import.meta.url), 'utf8');
const hover = fs.readFileSync(new URL('../world-map/3d-hover.js', import.meta.url), 'utf8');
const country = fs.readFileSync(new URL('../world-map/3d-country-interaction.js', import.meta.url), 'utf8');

for (const token of [
  'window.__potatoAtlasCoreInteractions',
  'countryHub(feature)',
  'semanticHub(feature)',
  'traceHub(feature)',
  'relation(feature)',
]) {
  assert.ok(app.includes(token), `core app must expose semantic action bridge marker: ${token}`);
}

for (const layer of ['countries-fill', 'countries-extrude', 'country-hubs', 'semantic-hubs', 'trace-hubs', 'relations']) {
  assert.ok(!app.includes(`map.on('click','${layer}'`), `${layer} direct click ownership must be retired from 3d-app.js`);
}
assert.ok(!app.includes('function handleCountryPolygonClick'), 'core app must retire its country polygon compatibility handler');
assert.ok(!app.includes('__potatoAtlasOverlayHandled'), 'core app must no longer depend on the compatibility event flag');

const routerBoot = "await import(versionedModule('./3d-interaction-router.js'))";
const countryBoot = "await import(versionedModule('./3d-country-interaction.js'))";
assert.ok(hover.includes(routerBoot), 'core hover boot must initialize Interaction Router immediately after map capture');
assert.ok(hover.includes(countryBoot), 'core hover boot must initialize country interaction immediately after the router');
assert.ok(hover.indexOf(routerBoot) < hover.indexOf(countryBoot), 'Interaction Router must boot before country interaction');
assert.ok(hover.indexOf(countryBoot) < hover.indexOf('async function sharedInteraction()'), 'base country interaction must be live before optional fallback-capital interaction setup');

for (const token of [
  "interaction.register('countries'",
  "interaction.register('core-country-hubs'",
  "interaction.register('core-semantic-hubs'",
  "interaction.register('core-trace-hubs'",
  "interaction.register('core-relations'",
  'window.__potatoAtlasCoreInteractions?.countryHub?.(feature)',
  'window.__potatoAtlasCoreInteractions?.semanticHub?.(feature)',
  'window.__potatoAtlasCoreInteractions?.traceHub?.(feature)',
  'window.__potatoAtlasCoreInteractions?.relation?.(feature)',
]) {
  assert.ok(country.includes(token), `country interaction router must own core semantic action: ${token}`);
}

assert.ok(!country.includes('onClick:() => {}'), 'core interaction registrations must not remain compatibility no-ops');
assert.ok(!country.includes('Legacy core overlay actions remain direct until their dedicated migration'), 'retired compatibility wording must be removed');

console.log('WORLD MAP CORE INTERACTION OWNERSHIP REGRESSION PASSED');
