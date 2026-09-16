import assert from 'node:assert/strict';
import fs from 'node:fs';

const layout = fs.readFileSync(new URL('../world-map/3d-ui-layout.js', import.meta.url), 'utf8');
const worldBar = fs.readFileSync(new URL('../world-map/3d-world-bar.js', import.meta.url), 'utf8');
const app = fs.readFileSync(new URL('../world-map/3d-app.js', import.meta.url), 'utf8');

assert.ok(layout.includes('function cameraPadding'), 'UI Layout must expose map-safe camera padding');
assert.ok(layout.includes("'right-inspector'"), 'camera padding must remain coupled to the registered inspector zone');
assert.ok(layout.includes('panel-collapsed'), 'camera padding must respect collapsed inspector state');
assert.ok(layout.includes('window.__potatoAtlasUILayout = {'), 'UI Layout public API must remain explicit');
assert.ok(layout.includes('cameraPadding'), 'UI Layout public API must publish cameraPadding');
assert.ok(layout.includes('--panel-w:clamp(300px,24vw,360px)'), 'desktop inspector width must be responsive and bounded');

assert.ok(worldBar.includes('max-height:min(420px,calc(100dvh - 76px))'), 'desktop World Bar menus must not consume most of a tall map');
assert.ok(worldBar.includes('scrollbar-gutter:stable'), 'scrolling menus must reserve stable scrollbar space');
assert.ok(worldBar.includes('overscroll-behavior:contain'), 'menu scroll must not leak into map zoom/pan');

assert.ok(app.includes('window.__potatoAtlasUILayout?.cameraPadding?.(padding)'), 'country/trace/compare fit path must consume shared UI-safe padding');
assert.ok(app.includes('padding:uiPadding || padding'), 'fitBounds must prefer UI-safe asymmetric padding');

console.log('WORLD MAP VIEWPORT OCCLUSION REGRESSION PASSED');
