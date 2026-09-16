import assert from 'node:assert/strict';
import fs from 'node:fs';

const app = fs.readFileSync(new URL('../world-map/3d-app.js', import.meta.url), 'utf8');
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

for (const layer of ['country-hubs', 'semantic-hubs', 'trace-hubs', 'relations']) {
  assert.ok(!app.includes(`map.on('click','${layer}'`), `${layer} direct click ownership must be retired from 3d-app.js`);
}

for (const token of [
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
