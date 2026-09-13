(()=>{
'use strict';

const upstreamFetch=window.fetch.bind(window);
const WAVES=[19,20,22,23,24,25];
const arr=value=>Array.isArray(value)?value:(value==null?[]:[value]);
const dossierPath=wave=>`../../knowledge/traditions/biblical-syncretism-dossiers-wave${wave}.json`;
const fragmentPath=wave=>`../../knowledge/traditions/biblical-passage-fragments-wave${wave}.json`;
const load=url=>upstreamFetch(url)
 .then(response=>response.ok?response.json():null)
 .catch(error=>{console.warn(`Bible mining extension unavailable: ${url}`,error);return null});

const dossierPromise=Promise.all(WAVES.map(wave=>load(dossierPath(wave))));
const fragmentPromise=Promise.all(WAVES.map(wave=>load(fragmentPath(wave))));

function mergeLayer(base,layer){
 if(!layer)return base;
 const rows=[...arr(base.relations)];
 const byId=new Map(rows.map(row=>[row.id,row]));
 arr(layer.enrichments).forEach(enrichment=>{
  const target=byId.get(enrichment.relation_id);
  if(!target)return;
  Object.entries(enrichment).forEach(([key,value])=>{
   if(key!=='relation_id')target[key]=value;
  });
 });
 arr(layer.new_relations).forEach(row=>{
  if(byId.has(row.id))return;
  const copy={...row};
  rows.push(copy);
  byId.set(copy.id,copy);
 });
 return {...base,relations:rows};
}

function mergeFragments(base,layers){
 const fragments=[...arr(base.fragments)];
 const seen=new Set(fragments.map(item=>item.id));
 layers.filter(Boolean).forEach(layer=>{
  arr(layer.fragments).forEach(item=>{
   if(seen.has(item.id))return;
   fragments.push(item);
   seen.add(item.id);
  });
 });
 return {...base,fragments};
}

window.fetch=async function(input,init){
 const url=typeof input==='string'?input:input?.url||'';
 if(url.endsWith('biblical-syncretism-field.json')){
  const [response,layers]=await Promise.all([upstreamFetch(input,init),dossierPromise]);
  if(!response.ok)return response;
  let base=await response.json();
  layers.filter(Boolean).forEach(layer=>{base=mergeLayer(base,layer)});
  return new Response(JSON.stringify(base),{
   status:response.status,
   statusText:response.statusText,
   headers:{'Content-Type':'application/json'}
  });
 }
 if(url.endsWith('biblical-passage-fragments.json')){
  const [response,layers]=await Promise.all([upstreamFetch(input,init),fragmentPromise]);
  if(!response.ok)return response;
  const base=await response.json();
  return new Response(JSON.stringify(mergeFragments(base,layers)),{
   status:response.status,
   statusText:response.statusText,
   headers:{'Content-Type':'application/json'}
  });
 }
 return upstreamFetch(input,init);
};
})();
