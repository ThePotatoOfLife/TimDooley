import assert from 'node:assert/strict';
globalThis.window=globalThis;
globalThis.CustomEvent=class CustomEvent{constructor(type,init={}){this.type=type;this.detail=init.detail;}};
globalThis.dispatchEvent=()=>true;
globalThis.structuredClone=globalThis.structuredClone || (value=>JSON.parse(JSON.stringify(value)));
const index={
  purpose:'fixture',datasets:{DNK:{path:'DNK.json',source:'Statistics Denmark',source_ref:'fixture-source',period:'2026',status:'official'}}
};
const stats={records:[{subdivision_id:'DK-1083',population:1234567,population_meta:{period:'2026-Q1',source:'Statistics Denmark',source_ref:'fixture-pop'},area_km2:12000,area_km2_meta:{period:'2026',source:'Agency area table',source_ref:'fixture-area'}}]};
globalThis.fetch=async url=>{
  const text=String(url);
  if(text.endsWith('statistics/index.json')) return {ok:true,json:async()=>index};
  if(text.endsWith('statistics/DNK.json')) return {ok:true,json:async()=>stats};
  throw new Error('unexpected fetch '+text);
};
await import(new URL('../world-map/3d-subdivision-statistics.js?fixture=1',import.meta.url));
const geometrySource='DAWA/Dataforsyningen';
const original={type:'Feature',properties:{id:'DK-1083',name:'Region Syddanmark',population:null,population_status:'unknown-not-zero',geometry_source:geometrySource},geometry:{type:'Polygon',coordinates:[]}};
const collection={type:'FeatureCollection',features:[original]};
const enriched=await window.__potatoAtlasSubdivisionStatistics.enrichCollection('DNK',collection);
const p=enriched.features[0].properties;
assert.equal(p.geometry_source,geometrySource,'statistics join must not alter geometry provenance');
assert.equal(original.properties.population,null,'statistics join must not mutate canonical input feature');
assert.equal(p.population.value,1234567);
assert.equal(p.population.source,'Statistics Denmark');
assert.equal(p.area_km2,12000);
assert.equal(p.area_definition,'sourced ADM1 statistics enrichment; not calculated from display geometry');
assert.equal(p.statistics_provenance.population.source_ref,'fixture-pop');
assert.equal(p.statistics_provenance.area_km2.source_ref,'fixture-area');
console.log('WORLD MAP SUBDIVISION STATISTICS REGRESSION PASSED');
