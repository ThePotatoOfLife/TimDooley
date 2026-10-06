import assert from 'node:assert/strict';
import fs from 'node:fs';

const layout = fs.readFileSync(new URL('../world-map/3d-ui-layout.js', import.meta.url), 'utf8');
const bootstrap = fs.readFileSync(new URL('../world-map/3d-bootstrap.js', import.meta.url), 'utf8');
const compositor = fs.readFileSync(new URL('../world-map/3d-compositor.js', import.meta.url), 'utf8');

assert.equal(fs.existsSync(new URL('../world-map/3d-lenses.js', import.meta.url)), false, 'retired Lens adapter must stay deleted');
assert.ok(!bootstrap.includes('3d-lenses.js'), 'bootstrap must not restore the retired Lens adapter');
assert.ok(compositor.includes('window.__potatoAtlasCompositor'), 'Compositor must remain the canonical analytical renderer');
assert.ok(layout.includes('atlasWorldBar') || layout.includes('atlas-registry-ui'), 'UI Layout must remain compatible with the registry-owned toolbar');

console.log('WORLD MAP LENS RETIREMENT REGRESSION PASSED');
