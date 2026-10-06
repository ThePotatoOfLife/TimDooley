import assert from 'node:assert/strict';
import fs from 'node:fs';

const files = {
  Places:'../world-map/3d-places.js',
  Subdivisions:'../world-map/3d-subdivisions.js',
  ADL:'../world-map/3d-adl-heat.js',
  Mud:'../world-map/3d-mud-below-us.js',
  Spatial:'../world-map/3d-spatial-overlay-ui.js',
  Axis:'../world-map/3d-axis.js',
  AxisDepth:'../world-map/3d-axis-depth.js',
};

for (const [label, rel] of Object.entries(files)) {
  const source = fs.readFileSync(new URL(rel, import.meta.url), 'utf8');
  assert.ok(source.includes('function inspectorRouter()'), `${label} must resolve Inspector dynamically`);
  assert.ok(!source.includes('const inspector = window.__potatoAtlasInspector'), `${label} must not cache Inspector at module boot`);
  assert.ok(source.includes('document.getElementById(\'panel\')') || source.includes('document.querySelector(\'#panel\')'), `${label} must retain a raw panel fallback surface`);
}

for (const [label, rel] of [['Places',files.Places],['Subdivisions',files.Subdivisions]]) {
  const source = fs.readFileSync(new URL(rel, import.meta.url), 'utf8');
  assert.ok(source.includes('if (!inspector?.open'), `${label} must fall back when Inspector is unavailable`);
  assert.ok(source.includes('inspector.setBaseline('), `${label} must promote to typed Inspector history when available`);
  assert.ok(source.includes('inspector.open('), `${label} must open typed Inspector nodes`);
}

for (const [label, rel] of [['ADL',files.ADL],['Mud',files.Mud],['Spatial',files.Spatial],['Axis',files.Axis],['AxisDepth',files.AxisDepth]]) {
  const source = fs.readFileSync(new URL(rel, import.meta.url), 'utf8');
  assert.ok(source.includes('inspectorRouter()?.open'), `${label} must use live Inspector availability`);
}

console.log('WORLD MAP DEGRADED INSPECTOR CONSUMERS REGRESSION PASSED');
