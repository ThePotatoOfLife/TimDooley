(()=>{
'use strict';

const upstreamFetch=window.fetch.bind(window);
const DOSSIER_PATH='../../knowledge/traditions/biblical-syncretism-dossiers-wave20.json';
const FRAGMENT_PATH='../../knowledge/traditions/biblical-passage-fragments-wave20.json';
const arr=value=>Array.isArray(value)?value:(value==null?[]:[value]);
const dossierPromise=upstreamFetch(DOSSIER_PATH).then(r=>r.ok?r.json():null).catch(error=>{console.warn('Bible mining wave 20 unavailable',error);return null});
const fragmentPromise=upstreamFetch(FRAGMENT_PATH).then(r=>r.ok?r.json():null).catch(error=>{console.warn('Bible mining wave 20 fragments unavailable',error);return null});

function mergeLayer(base,layer){
 if(!layer)return base;
 const rows=[...arr(base.relations)],byId=new Map(rows.map(row=>[row.id,row]));
 arr(layer.enrichments).forEach(enrichment=>{
  const target=byId.get(enrichment.relation_id);
  if(!target)return;
  Object.entries(enrichment).forEach(([key,value])=>{if(key!=='relation_id')target[key]=value});
 });
 arr(layer.new_relations).forEach(row=>{
  if(byId.has(row.id))return;
  const copy={...row};
  rows.push(copy);
  byId.set(copy.id,copy);
 });
 return {...base,relations:rows};
}

function mergeFragments(base,extension){
 if(!extension)return base;
 const fragments=[...arr(base.fragments)],seen=new Set(fragments.map(item=>item.id));
 arr(extension.fragments).forEach(item=>{if(!seen.has(item.id)){fragments.push(item);seen.add(item.id)}});
 return {...base,fragments};
}

window.fetch=async function(input,init){
 const url=typeof input==='string'?input:input?.url||'';
 if(url.endsWith('biblical-syncretism-field.json')){
  const [response,layer]=await Promise.all([upstreamFetch(input,init),dossierPromise]);
  if(!response.ok||!layer)return response;
  const base=await response.json();
  return new Response(JSON.stringify(mergeLayer(base,layer)),{status:response.status,statusText:response.statusText,headers:{'Content-Type':'application/json'}});
 }
 if(url.endsWith('biblical-passage-fragments.json')){
  const [response,extension]=await Promise.all([upstreamFetch(input,init),fragmentPromise]);
  if(!response.ok||!extension)return response;
  const base=await response.json();
  return new Response(JSON.stringify(mergeFragments(base,extension)),{status:response.status,statusText:response.statusText,headers:{'Content-Type':'application/json'}});
 }
 return upstreamFetch(input,init);
};
})();
