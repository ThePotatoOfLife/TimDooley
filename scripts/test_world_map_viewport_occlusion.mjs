import assert from 'node:assert/strict';
import fs from 'node:fs';

const layout = fs.readFileSync(new URL('../world-map/3d-ui-layout.js', import.meta.url), 'utf8');

assert.ok(layout.includes('function cameraPadding'), 'UI Layout must expose map-safe camera padding');
assert.ok(layout.includes("'right-inspector'"), 'camera padding must remain coupled to the registered inspector zone');
assert.ok(layout.includes('panel-collapsed'), 'camera padding must respect collapsed inspector state');
assert.ok(layout.includes('window.__potatoAtlasUILayout = {'), 'UI Layout public API must remain explicit');
assert.ok(layout.includes('cameraPadding'), 'UI Layout public API must publish cameraPadding');
assert.ok(layout.includes('--panel-w:clamp(300px,24vw,360px)'), 'desktop inspector width must be responsive and bounded');

assert.ok(layout.includes('max-height:min(420px,calc(100dvh - 76px))'), 'World Bar menus must not consume most of a tall map');
assert.ok(layout.includes('scrollbar-gutter:stable'), 'scrolling menus must reserve stable scrollbar space');
assert.ok(layout.includes('overscroll-behavior:contain'), 'menu scroll must not leak into map zoom/pan');

assert.ok(layout.includes('function syncMapPadding'), 'UI Layout must actively synchronize safe camera insets');
assert.ok(layout.includes('window.__potatoAtlasMap?.setPadding'), 'MapLibre camera must consume shared viewport-safe padding');
assert.ok(layout.includes('cameraPadding(0)'), 'persistent map padding must be derived from the shared camera-padding policy');

console.log('WORLD MAP VIEWPORT OCCLUSION REGRESSION PASSED');
