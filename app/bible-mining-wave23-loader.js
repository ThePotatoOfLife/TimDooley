(()=>{
'use strict';

const upstreamFetch=window.fetch.bind(window);
const DOSSIER_PATHS=[
 '../../knowledge/traditions/biblical-syncretism-dossiers-wave23.json',
 '../../knowledge/traditions/biblical-syncretism-dossiers-wave24.json',
 '../../knowledge/traditions/biblical-syncretism-dossiers-wave25.json'
];
const FRAGMENT_PATHS=[
 '../../knowledge/traditions/biblical-passage-fragments-wave23.json',
 '../../knowledge/traditions/biblical-passage-fragments-wave24.json',
 '../../knowledge/traditions/biblical-passage-fragments-wave25.json'
];
const arr=value=>Array.isArray(value)?value:(value==null?[]:[value]);
const load=url=>upstreamFetch(url).then(r=>r.ok?r.json():null).catch(error=>{console.warn(`Bible mining extension unavailable: ${url}`,error);return null});
const dossierPromise=Promise.all(DOSSIER_PATHS.map(load));
const fragmentPromise=Promise.all(FRAGMENT_PATHS.map(load));

function mergeLayer(base,layer){
 if(!layer)return base;
 const rows=[...arr(base.relations)],byId=new Map(rows.map(row=>[row.id,row]));
 arr(layer.enrichments).forEach(enrichment=>{
  const target=byId.get(enrichment.relation_id);if(!target)return;
  Object.entries(enrichment).forEach(([key,value])=>{if(key!=='relation_id')target[key]=value});
 });
 arr(layer.new_relations).forEach(row=>{
  if(byId.has(row.id))return;
  const copy={...row};rows.push(copy);byId.set(copy.id,copy);
 });
 return {...base,relations:rows};
}
function mergeFragments(base,layers){
 const fragments=[...arr(base.fragments)],seen=new Set(fragments.map(item=>item.id));
 layers.filter(Boolean).forEach(layer=>arr(layer.fragments).forEach(item=>{
  if(!seen.has(item.id)){fragments.push(item);seen.add(item.id)}
 }));
 return {...base,fragments};
}

window.fetch=async function(input,init){
 const url=typeof input==='string'?input:input?.url||'';
 if(url.endsWith('biblical-syncretism-field.json')){
  const [response,layers]=await Promise.all([upstreamFetch(input,init),dossierPromise]);
  if(!response.ok)return response;
  let base=await response.json();
  layers.filter(Boolean).forEach(layer=>{base=mergeLayer(base,layer)});
  return new Response(JSON.stringify(base),{status:response.status,statusText:response.statusText,headers:{'Content-Type':'application/json'}});
 }
 if(url.endsWith('biblical-passage-fragments.json')){
  const [response,layers]=await Promise.all([upstreamFetch(input,init),fragmentPromise]);
  if(!response.ok)return response;
  const base=await response.json();
  return new Response(JSON.stringify(mergeFragments(base,layers)),{status:response.status,statusText:response.statusText,headers:{'Content-Type':'application/json'}});
 }
 return upstreamFetch(input,init);
};
})();
