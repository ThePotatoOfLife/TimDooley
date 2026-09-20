import assert from 'node:assert/strict';
import fs from 'node:fs';

const root = new URL('../', import.meta.url);
const panel = fs.readFileSync(new URL('world-map/3d-panel-lifecycle.js', root), 'utf8');
const worldBar = fs.readFileSync(new URL('world-map/3d-world-bar.js', root), 'utf8');
const presentationUrl = new URL('world-map/3d-country-presentation.js', root);

assert.ok(
  fs.existsSync(presentationUrl),
  'display overhaul requires one shared country-presentation adapter before retiring the mixed context-status surface',
);
assert.ok(
  !panel.includes("'Context Status', './3d-context-status.js'"),
  'panel lifecycle must stop loading the mixed hover/selection/current-view context-status surface',
);
assert.ok(
  !worldBar.includes('<span>Active</span>'),
  'Current Map View must stay global and must not display selected-country identity',
);
assert.ok(
  worldBar.includes('select a country'),
  'relationship context without an active subject must explicitly orient the user to select a country',
);
assert.ok(worldBar.includes("context.setAttribute('role','status')"), 'successor Current Map View must be a status region');
assert.ok(worldBar.includes("context.setAttribute('aria-live','polite')"), 'successor Current Map View must announce canonical changes politely');
assert.ok(worldBar.includes("context.setAttribute('aria-atomic','true')"), 'successor Current Map View must announce a coherent atomic status');
assert.ok(worldBar.includes("let lastContextMarkup = ''"), 'successor status must track the last rendered announcement');
assert.ok(worldBar.includes("if (markup !== lastContextMarkup)"), 'successor status must not rewrite identical live-region content');

console.log('World Map retired context-status ownership contract passed');
