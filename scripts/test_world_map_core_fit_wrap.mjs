import assert from 'node:assert/strict';
import fs from 'node:fs';

const app = fs.readFileSync(new URL('../world-map/3d-app.js', import.meta.url), 'utf8');
const hover = fs.readFileSync(new URL('../world-map/3d-hover.js', import.meta.url), 'utf8');

const geoBoot = "await import(versionedModule('./3d-geo-kernel.js'))";
const appBoot = "await import(versionedModule('./3d-app.js'))";
assert.ok(hover.includes(geoBoot), 'core boot must preload the shared geospatial kernel');
assert.ok(
  hover.indexOf(geoBoot) < hover.indexOf(appBoot),
  'geospatial kernel must be ready before 3d-app.js initializes deep-link/country fitting'
);

assert.ok(app.includes('window.__potatoAtlasGeo'), 'core app must consume the shared geospatial kernel');
assert.ok(app.includes('geo.antimeridianAwareBounds'), 'core country/compare fitting must use antimeridian-aware bounds');
assert.ok(app.includes('map.getCenter()?.lng'), 'wrapped fit should stay near the current rendered world copy');
assert.ok(!app.includes('let minX=180,minY=90,maxX=-180,maxY=-90'), 'core fitting must retire naïve longitude min/max bounds');
assert.ok(!app.includes('minX=Math.min(minX,b[0][0])'), 'multi-country fitting must not merge longitudes with naïve min/max');

console.log('WORLD MAP CORE FIT WRAP REGRESSION PASSED');
