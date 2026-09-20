import assert from 'node:assert/strict';
import fs from 'node:fs';

globalThis.window = globalThis;
globalThis.location = { href:'https://example.test/world-map/?country=USA' };
globalThis.innerWidth = 390;
const listeners = new Map();
globalThis.addEventListener = (type, handler) => {
  const rows = listeners.get(type) || [];
  rows.push(handler);
  listeners.set(type, rows);
};
globalThis.dispatchEvent = event => {
  for (const handler of listeners.get(event.type) || []) handler(event);
  return true;
};
globalThis.CustomEvent = class CustomEvent {
  constructor(type, init={}) { this.type=type; this.detail=init.detail; }
};
globalThis.document = {
  documentElement:{ clientWidth:390 },
  getElementById(){ return null; },
  querySelector(){ return null; },
};

const sources = new Map();
const layers = new Map();
const filters = new Map();
const zoomRanges = new Map();
const layouts = [];
const mapHandlers = new Map();
const map = {
  on(type, ...args) { mapHandlers.set([type,...args.slice(0,-1)].join(':'), args.at(-1)); },
  off(){},
  loaded(){ return true; },
  once(type, cb){ cb(); },
  getZoom(){ return 4.1; },
  getCenter(){ return {lng:-97,lat:38}; },
  getBounds(){ return {getWest:()=>-125,getEast:()=>-66,getSouth:()=>24,getNorth:()=>50}; },
  getPitch(){ return 0; },
  getBearing(){ return 0; },
  getSource(id){ return sources.get(id) || null; },
  addSource(id, spec){ sources.set(id,{...spec,setData(data){ this.data=data; }}); },
  getLayer(id){ return layers.get(id) || null; },
  addLayer(spec){ layers.set(spec.id,spec); },
  setLayerZoomRange(id,min,max){ zoomRanges.set(id,{min,max}); },
  setLayoutProperty(id,prop,value){ layouts.push({id,prop,value}); },
  setFilter(id,value){ filters.set(id,value); },
  getCanvas(){ return {style:{}}; },
  cameraForBounds(){ return {center:{lng:-97,lat:38},zoom:4}; },
  easeTo(){},
  fitBounds(){},
};
window.__potatoAtlasMap = map;
window.__potatoAtlasUrlState = { claim(){}, patch(){} };
window.__potatoAtlasStyleLifecycle = { register(){} };
window.__potatoAtlasMotion = { easeTo(){ return true; }, fitBounds(){ return true; } };
window.__potatoAtlasProjection = { get:()=> 'globe' };
window.__potatoAtlasGeo = {
  unwrapLongitude(v){ return Number(v); },
  haversineDistanceKm(){ return 0; },
  antimeridianAwareBounds(){ return {west:-101,east:-99,south:39,north:41}; },
  pointInGeometry(){ return true; },
};
window.__potatoAtlasScale = { ready:Promise.resolve({
  threshold(domain,phase){
    assert.equal(domain,'subdivisions');
    if(phase==='render') return 3.4;
    if(phase==='label') return 4.25;
    if(phase==='interact') return 4.1;
    return 3.0;
  },
  bandThreshold(name){
    if(name==='macro-region') return 2.5;
    if(name==='subnational') return 5.8;
    if(name==='local') return 7.0;
    return 4;
  },
  capabilityActive(){ return true; },
}) };

const feature = {
  type:'Feature',
  geometry:{type:'Polygon',coordinates:[[[-101,39],[-99,39],[-99,41],[-101,41],[-101,39]]]},
  properties:{
    id:'US-TS',
    code:'TS',
    name:'Test State',
    local_name:'Test Local',
    country_iso3:'USA',
    country_name:'United States',
    subdivision_type:'State',
  },
};
globalThis.fetch = async url => {
  const text=String(url);
  if(text.includes('world-subdivisions/index.json')) return {ok:true,json:async()=>({
    runtime_budget:{partition_max_bytes:1500000,rendered_max_bytes:3000000,rendered_max_partitions:4,cache_max_bytes:6000000,cache_max_partitions:8},
    partitions:{USA:{path:'USA.geo.json',id_prefix:'US-',viewport_bounds:{west:-125,east:-66,south:24,north:50},bytes:1000}},
  })};
  if(text.includes('USA.geo.json')) return {ok:true,json:async()=>({type:'FeatureCollection',features:[feature]})};
  throw new Error('unexpected fetch '+text);
};

await import(new URL('../world-map/3d-subdivisions.js?combined-scenario=1', import.meta.url));
const api = window.__potatoAtlasSubdivisions;
assert.ok(api);

const status = api.status();
assert.equal(status.labelPresentation.narrow,true);
assert.equal(status.labelPresentation.globe,true);
assert.equal(status.labelPresentation.labelZoom,5.55);
assert.equal(status.labelPresentation.nameZoom,7.1);
assert.equal(status.labelPresentation.localNameZoom,8.3);
assert.equal(zoomRanges.get('atlas-subdivision-label').min,5.55,'ambient labels must be delayed in narrow globe mode');
assert.equal(layers.get('atlas-subdivision-selected-label').minzoom,3.4,'selected region label must remain available from render scale');

assert.equal(await api.select('US-TS',{fit:false}),true);
assert.equal(api.selected,'US-TS');
assert.deepEqual(filters.get('atlas-subdivision-selected-label'),['==',['get','id'],'US-TS']);

for (const handler of listeners.get('potato-atlas-projection-change') || []) handler(new CustomEvent('potato-atlas-projection-change'));
for (const handler of listeners.get('resize') || []) handler(new CustomEvent('resize'));
assert.equal(api.selected,'US-TS','projection/viewport presentation changes must not clear regional selection');

const placesSource = fs.readFileSync(new URL('../world-map/3d-places.js', import.meta.url),'utf8');
const subdivisionsSource = fs.readFileSync(new URL('../world-map/3d-subdivisions.js', import.meta.url),'utf8');
const showStart = placesSource.indexOf('async function showSubdivision(');
const showEnd = placesSource.indexOf('\nfunction status()', showStart);
assert.ok(showStart >= 0 && showEnd > showStart);
const showBody = placesSource.slice(showStart,showEnd);
assert.ok(showBody.includes('await loadCountry(result.code)'), 'region→Places must reuse bounded country partition loading');
assert.ok(showBody.includes('setVisible(true)'), 'region→Places must reveal canonical Places layers');
assert.ok(showBody.includes('potato-atlas-places-subdivision-show'), 'region→Places must emit a semantic handoff event');
assert.ok(!showBody.includes('clear('), 'region→Places handoff must not clear the active subdivision');
assert.ok(subdivisionsSource.includes("showSubdivision?.(feature, {limit:50})"), 'subdivision inspector must hand off to canonical Places owner');

console.log('WORLD MAP COMBINED REGION SCENARIO REGRESSION PASSED');
