(()=>{
'use strict';
const ACTIVE=new Set(['canonical','additive']);
const clone=value=>JSON.parse(JSON.stringify(value));
const isObject=value=>value&&typeof value==='object'&&!Array.isArray(value);
const nativeFetch=window.fetch.bind(window);
const REDIRECTS_PATH='knowledge/traditions/bible-relation-redirects.json';
function mergeValue(oldValue,newValue){
  if(isObject(oldValue)&&isObject(newValue)){
    const result=clone(oldValue);
    for(const [key,value] of Object.entries(newValue))result[key]=Object.prototype.hasOwnProperty.call(result,key)?mergeValue(result[key],value):clone(value);
    return result;
  }
  return clone(newValue);
}
const layers=(manifest,kind)=>[...(manifest.layers||[])].filter(x=>x.kind===kind&&ACTIVE.has(x.status)).sort((a,b)=>(a.precedence||0)-(b.precedence||0)||String(a.id).localeCompare(String(b.id)));
function mergeRelations(manifest,getData,redirects={}){
  const rows=[],byId=new Map(),redirected=new Set(Object.keys(redirects||{}));
  for(const meta of layers(manifest,'relations')){
    const data=getData(meta.path)||{};
    for(const row of data.relations||[]){if(!row.id)throw new Error(`relation without id in ${meta.id}`);if(redirected.has(row.id))continue;if(byId.has(row.id))throw new Error(`duplicate relation id ${row.id}`);const item=clone(row);rows.push(item);byId.set(item.id,item)}
    for(const enrichment of data.enrichments||[]){const target=byId.get(enrichment.relation_id);if(!target)throw new Error(`missing enrichment target ${enrichment.relation_id}`);for(const [key,value] of Object.entries(enrichment)){if(key!=='relation_id')target[key]=Object.prototype.hasOwnProperty.call(target,key)?mergeValue(target[key],value):clone(value)}}
    for(const row of data.new_relations||[]){if(!row.id)throw new Error(`new relation without id in ${meta.id}`);if(redirected.has(row.id))continue;if(byId.has(row.id))throw new Error(`duplicate relation id ${row.id}`);const item=clone(row);rows.push(item);byId.set(item.id,item)}
  }
  for(const [source,target] of Object.entries(redirects||{})){if(!byId.has(target))throw new Error(`redirect target missing for ${source}: ${target}`)}
  return rows;
}
function mergeFragments(manifest,getData){const rows=[],seen=new Set();for(const meta of layers(manifest,'fragments')){for(const fragment of (getData(meta.path)||{}).fragments||[]){if(!fragment.id)throw new Error(`fragment without id in ${meta.id}`);if(seen.has(fragment.id))continue;seen.add(fragment.id);rows.push(clone(fragment))}}return rows}
function mergeScenes(manifest,getData){const rows=[],seen=new Set();for(const meta of layers(manifest,'scenes')){for(const scene of (getData(meta.path)||{}).scenes||[]){if(!scene.id)throw new Error(`scene without id in ${meta.id}`);if(seen.has(scene.id))throw new Error(`duplicate scene id ${scene.id}`);seen.add(scene.id);rows.push(clone(scene))}}return rows}
function resolveRelationId(id,redirects={}){let current=String(id||''),seen=new Set();while(current&&redirects[current]&&!seen.has(current)){seen.add(current);current=redirects[current]}return current}
async function load(base='../../'){
  const json=async path=>{const r=await nativeFetch(base+path);if(!r.ok)throw new Error(`${path}: ${r.status}`);return r.json()};
  const manifest=await json('knowledge/traditions/bible-layer-manifest.json');
  let redirectData={redirects:{}};try{redirectData=await json(REDIRECTS_PATH)}catch(error){console.warn('Bible relation redirects unavailable',error)}
  const redirects=redirectData.redirects||{};
  const active=manifest.layers.filter(x=>ACTIVE.has(x.status)&&['relations','fragments','scenes'].includes(x.kind));
  const pairs=await Promise.all(active.map(async meta=>[meta.path,await json(meta.path)]));
  const data=new Map(pairs),getData=path=>data.get(path);
  return {manifest,redirects,relations:mergeRelations(manifest,getData,redirects),fragments:mergeFragments(manifest,getData),scenes:mergeScenes(manifest,getData)};
}
function readerRelation(row){
  const item=clone(row);
  if(item.project_concept&&!item.project_anchor)item.project_anchor=item.project_concept;
  if(item.relation_type&&!item.relation_class)item.relation_class=item.relation_type;
  if(item.reader_reading){item.relation_arguments=[item.reader_reading,...(Array.isArray(item.relation_arguments)?item.relation_arguments:[])];}
  if(item.counterpoint&&!item.counter_text)item.counter_text=item.counterpoint;
  if(item.source_refs&&!item.owners)item.owners=item.source_refs;
  if(item.evidence_class==='P0-public-occurrence'&&!item.discovery_mode)item.discovery_mode='public-occurrence';
  return item;
}
window.BibleCorpus={layers,mergeValue,mergeRelations,mergeFragments,mergeScenes,resolveRelationId,load,readerRelation};

const corpusPromise=load('../../').catch(error=>{console.warn('Bible manifest corpus bridge unavailable',error);return null});
window.BibleCorpus.ready=corpusPromise;
window.fetch=async function bibleCorpusBridge(input,init){
  const url=typeof input==='string'?input:String(input&&input.url||input||'');
  if(url.endsWith('knowledge/traditions/biblical-syncretism-field.json')){
    const corpus=await corpusPromise;
    if(corpus)return new Response(JSON.stringify({id:'bible-reader-manifest-corpus',relations:corpus.relations.map(readerRelation)}),{status:200,headers:{'Content-Type':'application/json'}});
  }
  if(url.endsWith('knowledge/traditions/biblical-passage-fragments.json')){
    const corpus=await corpusPromise;
    if(corpus)return new Response(JSON.stringify({id:'bible-reader-manifest-fragments',fragments:corpus.fragments}),{status:200,headers:{'Content-Type':'application/json'}});
  }
  return nativeFetch(input,init);
};
})();
