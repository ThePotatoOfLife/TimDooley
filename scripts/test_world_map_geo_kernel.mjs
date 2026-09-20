import assert from 'node:assert/strict';
import {
  normalizeLongitude,
  shortestLongitudeDelta,
  unwrapLongitude,
  minimalLongitudeInterval,
  antimeridianAwareBounds,
  pointInGeometry,
  haversineDistanceKm,
} from '../world-map/3d-geo-kernel.js';

assert.equal(normalizeLongitude(190), -170);
assert.equal(normalizeLongitude(-190), 170);
assert.equal(normalizeLongitude(180), -180);
assert.equal(normalizeLongitude(-180), -180);
assert.equal(normalizeLongitude(540), -180);
assert.throws(() => normalizeLongitude(Number.NaN), /finite/i);

assert.equal(shortestLongitudeDelta(170, -170), 20);
assert.equal(shortestLongitudeDelta(-170, 170), -20);
assert.equal(shortestLongitudeDelta(10, 20), 10);
assert.equal(shortestLongitudeDelta(20, 10), -10);

assert.equal(unwrapLongitude(-170, 170), 190);
assert.equal(unwrapLongitude(170, -170), -190);
assert.equal(unwrapLongitude(175, 179), 175);

const interval = minimalLongitudeInterval([170, -170, 178, -178]);
assert.equal(interval.west, 170);
assert.equal(interval.east, 190);
assert.equal(interval.span, 20);
assert.equal(interval.crossesAntimeridian, true);

const referenced = minimalLongitudeInterval([170, -170], -175);
assert.equal(referenced.west, -190);
assert.equal(referenced.east, -170);
assert.equal(referenced.span, 20);

const bounds = antimeridianAwareBounds([[170, -10], [-170, 15], [178, 5]]);
assert.deepEqual(bounds, {
  west: 170,
  south: -10,
  east: 190,
  north: 15,
  spanLongitude: 20,
  crossesAntimeridian: true,
});

const nestedBounds = antimeridianAwareBounds({
  type: 'Polygon',
  coordinates: [[[179, -2], [-179, -2], [-179, 3], [179, 3], [179, -2]]],
});
assert.equal(nestedBounds.spanLongitude, 2);
assert.equal(nestedBounds.crossesAntimeridian, true);
assert.equal(nestedBounds.south, -2);
assert.equal(nestedBounds.north, 3);

assert.throws(
  () => antimeridianAwareBounds([[Number.NaN, 0], [10, 5]]),
  /finite|coordinate/i,
);
assert.throws(
  () => antimeridianAwareBounds([]),
  /coordinate/i,
);

const polygon = {
  type:'Polygon',
  coordinates:[[[-2,-2],[2,-2],[2,2],[-2,2],[-2,-2]], [[-0.5,-0.5],[0.5,-0.5],[0.5,0.5],[-0.5,0.5],[-0.5,-0.5]]],
};
assert.equal(pointInGeometry([1,1], polygon), true);
assert.equal(pointInGeometry([0,0], polygon), false, 'polygon holes must exclude contained points');
assert.equal(pointInGeometry([3,0], polygon), false);

const wrappedPolygon = {
  type:'Polygon',
  coordinates:[[[179,-2],[-179,-2],[-179,2],[179,2],[179,-2]]],
};
assert.equal(pointInGeometry([179.5,0], wrappedPolygon), true);
assert.equal(pointInGeometry([-179.5,0], wrappedPolygon), true);
assert.equal(pointInGeometry([0,0], wrappedPolygon), false);

const distance = haversineDistanceKm([179, 0], [-179, 0]);
assert.ok(distance > 200 && distance < 225, `expected about 222 km across dateline, got ${distance}`);
assert.ok(haversineDistanceKm([12.5683, 55.6761], [12.5683, 55.6761]) < 1e-9);
assert.throws(() => haversineDistanceKm([0, 91], [0, 0]), /latitude/i);

console.log('WORLD MAP GEO KERNEL REGRESSION PASSED');
