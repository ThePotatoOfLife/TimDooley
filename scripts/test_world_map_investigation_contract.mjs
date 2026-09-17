import assert from 'node:assert/strict';
import fs from 'node:fs';

const root = new URL('../', import.meta.url);
const investigation = fs.readFileSync(new URL('world-map/3d-investigation-surface.js', root), 'utf8');
const evidence = fs.readFileSync(new URL('world-map/3d-evidence.js', root), 'utf8');
const context = fs.readFileSync(new URL('world-map/3d-context-visibility.js', root), 'utf8');

assert.match(investigation, /function active\(\)/, 'investigation surface must expose active id');
assert.match(investigation, /get current\(\)/, 'investigation surface should expose a stable current snapshot for consumers');
assert.match(investigation, /isActive/, 'investigation surface should expose active-state query');
assert.match(investigation, /function closeActive\(/, 'investigation surface should expose one shared close-active operation');
assert.match(investigation, /event\.key === 'Escape'/, 'Escape should close the active investigation surface centrally');

assert.match(evidence, /register\('evidence'/, 'Evidence must register with the shared investigation surface');
assert.match(evidence, /\.open\('evidence'\)/, 'opening Eye must claim the shared investigation surface');
assert.match(evidence, /\.close\('evidence'\)/, 'closing Eye must release the shared investigation surface');

assert.match(context, /api\.active\(\)/, 'context visibility must consume the actual investigation API');
assert.doesNotMatch(context, /__potatoAtlasInvestigationSurface\?\.current\?\.type/, 'context visibility must not depend on a nonexistent current.type shape');

console.log('World Map investigation contract tests passed');
