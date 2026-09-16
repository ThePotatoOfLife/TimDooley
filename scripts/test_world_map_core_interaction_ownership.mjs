import assert from 'node:assert/strict';
import fs from 'node:fs';

const app = fs.readFileSync(new URL('../world-map/3d-app.js', import.meta.url), 'utf8');
const bootstrap = fs.readFileSync(new URL('../world-map/3d-bootstrap.js', import.meta.url), 'utf8');
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

const lifecycleBoot = "await loadAfterPaint('Panel lifecycle', './3d-panel-lifecycle.js')";
const routerReady = 'await waitForInteractionRouter()';
const countryBoot = "await loadAfterPaint('Country interaction', './3d-country-interaction.js')";
const interactiveEvent = "window.dispatchEvent(new CustomEvent('potato-atlas-interactive'))";
for (const token of [lifecycleBoot, routerReady, countryBoot, interactiveEvent]) {
  assert.ok(bootstrap.includes(token), `bootstrap must preserve core interaction readiness marker: ${token}`);
}
assert.ok(bootstrap.indexOf(lifecycleBoot) < bootstrap.indexOf(routerReady), 'panel lifecycle must start the control plane before router readiness is awaited');
assert.ok(bootstrap.indexOf(routerReady) < bootstrap.indexOf(countryBoot), 'router must be ready before country interaction registers');
assert.ok(bootstrap.indexOf(countryBoot) < bootstrap.indexOf(interactiveEvent), 'country interaction must be registered before the atlas becomes interactive');

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
