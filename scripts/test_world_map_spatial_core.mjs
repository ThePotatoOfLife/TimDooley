import assert from 'node:assert/strict';
import {pointInGeometry, assetsWithinGeometry} from '../world-map/3d-spatial-core.js';

const polygon = {
  type:'Polygon',
  coordinates:[
    [[0,0],[10,0],[10,10],[0,10],[0,0]],
    [[4,4],[6,4],[6,6],[4,6],[4,4]],
  ],
};
assert.equal(pointInGeometry([2,2], polygon), true, 'point inside outer ring should match');
assert.equal(pointInGeometry([5,5], polygon), false, 'point inside a polygon hole should not match');
assert.equal(pointInGeometry([12,2], polygon), false, 'point outside polygon should not match');

const multi = {
  type:'MultiPolygon',
  coordinates:[
    [[[-5,-5],[-1,-5],[-1,-1],[-5,-1],[-5,-5]]],
    [[[20,20],[25,20],[25,25],[20,25],[20,20]]],
  ],
};
assert.equal(pointInGeometry([22,22], multi), true, 'point inside any multipolygon member should match');

const assets = [
  {id:'inside', location:{type:'Point',coordinates:[2,2]}},
  {id:'hole', location:{type:'Point',coordinates:[5,5]}},
  {id:'outside', location:{type:'Point',coordinates:[12,2]}},
  {id:'unknown', geometry_status:'no-geometry'},
];
assert.deepEqual(assetsWithinGeometry(assets, polygon).map(asset => asset.id), ['inside']);
console.log('WORLD MAP SPATIAL CORE PASSED');
