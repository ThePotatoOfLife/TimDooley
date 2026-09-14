(()=>{
'use strict';
const ACTIVE=new Set(['canonical','additive']);
const clone=value=>JSON.parse(JSON.stringify(value));
const isObject=value=>value&&typeof value==='object'&&!Array.isArray(value);
function mergeValue(oldValue,newValue){
  if(isObject(oldValue)&&isObject(newValue)){
    const result=clone(oldValue);
    for(const [key,value] of Object.entries(newValue))result[key]=Object.prototype.hasOwnProperty.call(result,key)?mergeValue(result[key],value):clone(value);
    return result;
  }
  return clone(newValue);
}
const layers=(manifest,kind)=>[...(manifest.layers||[])].filter(x=>x.kind===kind&&ACTIVE.has(x.status)).sort((a,b)=>(a.precedence||0)-(b.precedence||0)||String(a.id).localeCompare(String(b.id)));
function mergeRelations(manifest,getData){
  const rows=[],byId=new Map();
  for(const meta of layers(manifest,'relations')){
    const data=getData(meta.path)||{};
    for(const row of data.relations||[]){if(!row.id)throw new Error(`relation without id in ${meta.id}`);if(byId.has(row.id))throw new Error(`duplicate relation id ${row.id}`);const item=clone(row);rows.push(item);byId.set(item.id,item)}
    for(const enrichment of data.enrichments||[]){const target=byId.get(enrichment.relation_id);if(!target)throw new Error(`missing enrichment target ${enrichment.relation_id}`);for(const [key,value] of Object.entries(enrichment)){if(key!=='relation_id')target[key]=Object.prototype.hasOwnProperty.call(target,key)?mergeValue(target[key],value):clone(value)}}
    for(const row of data.new_relations||[]){if(!row.id)throw new Error(`new relation without id in ${meta.id}`);if(byId.has(row.id))throw new Error(`duplicate relation id ${row.id}`);const item=clone(row);rows.push(item);byId.set(item.id,item)}
  }
  return rows;
}
function mergeFragments(manifest,getData){const rows=[],seen=new Set();for(const meta of layers(manifest,'fragments')){for(const fragment of (getData(meta.path)||{}).fragments||[]){if(!fragment.id)throw new Error(`fragment without id in ${meta.id}`);if(seen.has(fragment.id))continue;seen.add(fragment.id);rows.push(clone(fragment))}}return rows}
function mergeScenes(manifest,getData){const rows=[],seen=new Set();for(const meta of layers(manifest,'scenes')){for(const scene of (getData(meta.path)||{}).scenes||[]){if(!scene.id)throw new Error(`scene without id in ${meta.id}`);if(seen.has(scene.id))throw new Error(`duplicate scene id ${scene.id}`);seen.add(scene.id);rows.push(clone(scene))}}return rows}
async function load(base='../../'){
  const json=async path=>{const r=await fetch(base+path);if(!r.ok)throw new Error(`${path}: ${r.status}`);return r.json()};
  const manifest=await json('knowledge/traditions/bible-layer-manifest.json');
  const active=manifest.layers.filter(x=>ACTIVE.has(x.status)&&['relations','fragments','scenes'].includes(x.kind));
  const pairs=await Promise.all(active.map(async meta=>[meta.path,await json(meta.path)]));
  const data=new Map(pairs),getData=path=>data.get(path);
  return {manifest,relations:mergeRelations(manifest,getData),fragments:mergeFragments(manifest,getData),scenes:mergeScenes(manifest,getData)};
}
window.BibleCorpus={layers,mergeValue,mergeRelations,mergeFragments,mergeScenes,load};
})();
