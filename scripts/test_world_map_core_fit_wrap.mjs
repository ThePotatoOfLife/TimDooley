import assert from 'node:assert/strict';
import fs from 'node:fs';

const app = fs.readFileSync(new URL('../world-map/3d-app.js', import.meta.url), 'utf8');
const hover = fs.readFileSync(new URL('../world-map/3d-hover.js', import.meta.url), 'utf8');

const geoBoot = "await import(versionedModule('./3d-geo-kernel.js'))";
const appBoot = "await import(versionedModule('./3d-app.js'))";
assert.ok(hover.includes(geoBoot), 'core boot must preload the shared geospatial kernel');
assert.ok(hover.includes(appBoot), 'core boot must still load 3d-app.js through the deployment-versioned module path');
assert.ok(hover.indexOf(geoBoot) < hover.indexOf(appBoot), 'geo kernel must be ready before core app deep-link fitting');

assert.ok(app.includes('window.__potatoAtlasGeo'), 'core app must consume the shared geo kernel');
assert.ok(app.includes('geoKernel.antimeridianAwareBounds'), 'core fitting must use antimeridian-aware bounds');
assert.ok(app.includes('map.getCenter()?.lng'), 'core fitting should anchor wrapped bounds near the current world copy');

assert.ok(!app.includes('let minX=180,minY=90,maxX=-180,maxY=-90'), 'naïve single-country longitude min/max must be retired');
assert.ok(!app.includes('minX=Math.min(minX,b[0][0])'), 'naïve multi-country longitude min/max must be retired');

console.log('WORLD MAP CORE FIT WRAP REGRESSION PASSED');
