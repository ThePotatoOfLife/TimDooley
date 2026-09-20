import assert from 'node:assert/strict';
import fs from 'node:fs';

const root = new URL('../', import.meta.url);
const app = fs.readFileSync(new URL('world-map/3d-app.js', root), 'utf8');
const selection = fs.readFileSync(new URL('world-map/3d-country-selection.js', root), 'utf8');
const pathfinder = fs.readFileSync(new URL('world-map/3d-pathfinder.js', root), 'utf8');
const geoKernel = fs.readFileSync(new URL('world-map/3d-geo-kernel.js', root), 'utf8');

assert.ok(app.includes("geometry_meaning:'relationship_chord'"), 'explicit Trace relation lines must declare schematic relationship geometry');
assert.ok(app.includes('geoKernel.shortestWrappedLine'), 'explicit Trace relations must use shortest wrapped longitude geometry');
assert.ok(selection.includes("geometry_meaning:'relationship_chord'"), 'automatic relation lines must declare schematic relationship geometry');
assert.ok(selection.includes('geoKernel.shortestWrappedLine'), 'automatic relation lines must use shortest wrapped longitude geometry');
assert.ok(geoKernel.includes('function shortestWrappedLine('), 'geospatial kernel must own wrapped relation-line geometry');
assert.ok(app.includes("geometry_meaning:'symbolic_route'"), 'semantic interior links must declare symbolic route geometry');
assert.ok(
  pathfinder.includes('Map lines are schematic relationship chords, not surveyed transport, cable, pipeline, border, or physical route geometry.'),
  'Path must explain that graph lines are not surveyed physical routes',
);

console.log('WORLD MAP ROUTE GEOMETRY SEMANTICS REGRESSION PASSED');
