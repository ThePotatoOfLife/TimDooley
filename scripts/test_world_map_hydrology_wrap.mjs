import assert from 'node:assert/strict';
import fs from 'node:fs';

const source = fs.readFileSync(new URL('../world-map/3d-physical-hydrology.js', import.meta.url), 'utf8');

function extractFunction(name) {
  const marker = `function ${name}(`;
  const start = source.indexOf(marker);
  assert.ok(start >= 0, `missing ${name}`);
  const bodyStart = source.indexOf('{', start);
  let depth = 0;
  for (let i = bodyStart; i < source.length; i += 1) {
    if (source[i] === '{') depth += 1;
    else if (source[i] === '}') {
      depth -= 1;
      if (depth === 0) return source.slice(start, i + 1);
    }
  }
  throw new Error(`unterminated ${name}`);
}

const normalizeLongitude = value => {
  let n = Number(value);
  n = ((n + 180) % 360 + 360) % 360 - 180;
  return n === -180 && Number(value) > 0 ? 180 : n;
};
const splitterSource = extractFunction('canonicalLongitudeEnvelopes');
const canonicalLongitudeEnvelopes = new Function(
  'geoKernel',
  `"use strict"; ${splitterSource}; return canonicalLongitudeEnvelopes;`
)({ normalizeLongitude });

assert.deepEqual(
  canonicalLongitudeEnvelopes(-20, 20, -10, 10),
  ['-20,-10,20,10'],
  'ordinary viewport should remain one envelope'
);
assert.deepEqual(
  canonicalLongitudeEnvelopes(170, 190, -10, 10),
  ['170,-10,180,10', '-180,-10,-170,10'],
  'eastward unwrapped dateline viewport must split at +180/-180'
);
assert.deepEqual(
  canonicalLongitudeEnvelopes(-190, -170, -10, 10),
  ['170,-10,180,10', '-180,-10,-170,10'],
  'westward world copy must canonicalize to the same two envelopes'
);
assert.deepEqual(
  canonicalLongitudeEnvelopes(170, -170, -10, 10),
  ['170,-10,180,10', '-180,-10,-170,10'],
  'canonical west>east dateline viewport must split'
);
assert.deepEqual(
  canonicalLongitudeEnvelopes(-180, 180, -85, 85),
  ['-180,-85,180,85'],
  'world-width viewport should collapse to one canonical envelope'
);
assert.deepEqual(canonicalLongitudeEnvelopes(20, 10, 5, 5), [], 'invalid latitude span must fail closed');

const mergerSource = extractFunction('mergeFeatureCollections');
const mergeFeatureCollections = new Function(
  `"use strict"; ${mergerSource}; return mergeFeatureCollections;`
)();

const merged = mergeFeatureCollections([
  {type:'FeatureCollection',features:[
    {type:'Feature',properties:{HYBAS_ID:1},geometry:{type:'Point',coordinates:[179,0]}},
    {type:'Feature',properties:{HYBAS_ID:2},geometry:{type:'Point',coordinates:[178,1]}},
  ]},
  {type:'FeatureCollection',features:[
    {type:'Feature',properties:{HYBAS_ID:1},geometry:{type:'Point',coordinates:[-179,0]}},
    {type:'Feature',properties:{HYBAS_ID:3},geometry:{type:'Point',coordinates:[-178,1]}},
  ]},
], ['HYBAS_ID']);
assert.deepEqual(merged.features.map(f => f.properties.HYBAS_ID), [1,2,3], 'wrapped halves must deduplicate provider identities');

for (const token of [
  'function viewportEnvelopes()',
  'canonicalLongitudeEnvelopes(bounds.getWest(), bounds.getEast()',
  'hydrologyRequestKey(envelopes',
  'envelopes.map(envelope =>',
]) {
  assert.ok(source.includes(token), `hydrology wrap integration missing: ${token}`);
}
assert.ok(!source.includes('viewport crosses unsupported wrap'), 'dateline viewport must no longer be treated as unsupported');

console.log('WORLD MAP HYDROLOGY WRAP REGRESSION PASSED');
