import assert from 'node:assert/strict';

globalThis.window = globalThis;
globalThis.location = { href:'https://example.test/world-map/' };
globalThis.document = {
  documentElement:{ clientWidth:1200 },
  getElementById(){ return null; },
  querySelector(){ return null; },
};
globalThis.CustomEvent = class CustomEvent { constructor(type, init={}) { this.type=type; this.detail=init.detail; } };
globalThis.dispatchEvent = () => true;
globalThis.addEventListener = () => {};

const moves = [];
const handlers = new Map();
const sources = new Map();
const layers = new Map();
const map = {
  on(type, ...args) { handlers.set([type,...args.slice(0,-1)].join(':'), args.at(-1)); },
  off(){},
  getZoom(){ return 1.2; },
  getCenter(){ return {lng:20,lat:45}; },
  getBounds(){ return {getWest:()=>-20,getEast:()=>30,getSouth:()=>30,getNorth:()=>65}; },
  cameraForBounds(bounds) {
    assert.deepEqual(bounds, [[19,41],[190,82]], 'Russia viewport bounds should unwrap across the antimeridian');
    return { center:{lng:104.5,lat:61.5}, zoom:2.1 };
  },
  easeTo(options){ moves.push(options); },
  fitBounds(){ throw new Error('focusPartition should use shared easeTo policy when cameraForBounds exists'); },
  getSource(id){ return sources.get(id) || null; },
  addSource(id, spec){ sources.set(id,{...spec,setData(data){ this.data=data; }}); },
  getLayer(id){ return layers.get(id) || null; },
  addLayer(spec){ layers.set(spec.id,spec); },
  setLayerZoomRange(){},
  setLayoutProperty(){},
  setFilter(){},
  getCanvas(){ return {style:{}}; },
};
window.__potatoAtlasMap = map;
window.__potatoAtlasUrlState = { claim(){}, patch(){} };
window.__potatoAtlasStyleLifecycle = { register(){} };
window.__potatoAtlasMotion = {
  easeTo(target, options){ target.easeTo(options); return true; },
  fitBounds(){ return true; },
};
window.__potatoAtlasGeo = {
  unwrapLongitude(value, reference) {
    let out=Number(value);
    while(out-reference>180) out-=360;
    while(out-reference<-180) out+=360;
    return out;
  },
  haversineDistanceKm(){ return 0; },
  antimeridianAwareBounds(){ return {west:0,east:1,south:0,north:1}; },
};
window.__potatoAtlasScale = { ready:Promise.resolve({
  threshold(domain, phase){ assert.equal(domain,'subdivisions'); return phase==='render' ? 3.4 : 4.25; },
  bandThreshold(){ return 5.8; },
  capabilityActive(){ return true; },
}) };

globalThis.fetch = async url => {
  const text=String(url);
  if(text.includes('world-subdivisions/index.json')) return {ok:true,json:async()=>({
    runtime_budget:{},
    partitions:{RUS:{path:'RUS.geo.json',id_prefix:'RU-',viewport_bounds:{west:19,east:-170,south:41,north:82},bytes:1000}},
  })};
  if(text.includes('RUS.geo.json')) return {ok:true,json:async()=>({type:'FeatureCollection',features:[]})};
  throw new Error('unexpected fetch '+text);
};

await import(new URL('../world-map/3d-subdivisions.js?partition-focus=1', import.meta.url));
assert.equal(await window.__potatoAtlasSubdivisions.retainPartition('RUS','test'), true);
assert.equal(await window.__potatoAtlasSubdivisions.focusPartition('RUS'), true);
assert.equal(moves.length,1);
assert.equal(moves[0].zoom,3.58,'partition focus must floor camera at visible subdivision scale');
assert.deepEqual(moves[0].center,{lng:104.5,lat:61.5});

console.log('WORLD MAP REGION DOORWAY FOCUS REGRESSION PASSED');
