(()=>{
'use strict';

const upstreamFetch=window.fetch.bind(window);
const DOSSIER_PATH='../../knowledge/traditions/biblical-syncretism-dossiers-wave19.json';
const FRAGMENT_PATH='../../knowledge/traditions/biblical-passage-fragments-wave19.json';
const WAVE22_PATHS=[
 '../../knowledge/traditions/biblical-operator-comparisons-wave22-a.json',
 '../../knowledge/traditions/biblical-operator-comparisons-wave22-b1.json',
 '../../knowledge/traditions/biblical-operator-comparisons-wave22-b2.json',
 '../../knowledge/traditions/biblical-operator-comparisons-wave22-b3.json',
 '../../knowledge/traditions/biblical-operator-comparisons-wave22-c2.json',
 '../../knowledge/traditions/biblical-operator-comparisons-wave22-c3.json',
 '../../knowledge/traditions/biblical-operator-comparisons-wave22-c5.json',
];
const WAVE22_FRAGMENT_PATH='../../knowledge/traditions/biblical-passage-fragments-wave22.json';
const arr=value=>Array.isArray(value)?value:(value==null?[]:[value]);
const fetchJson=path=>upstreamFetch(path).then(r=>r.ok?r.json():null).catch(error=>{console.warn('Bible comparison layer unavailable',path,error);return null});
const dossierPromise=fetchJson(DOSSIER_PATH);
const fragmentPromise=fetchJson(FRAGMENT_PATH);
const wave22Promise=Promise.all(WAVE22_PATHS.map(fetchJson));
const wave22FragmentPromise=fetchJson(WAVE22_FRAGMENT_PATH);

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
  const [response,layer,wave22]=await Promise.all([upstreamFetch(input,init),dossierPromise,wave22Promise]);
  if(!response.ok)return response;
  let base=await response.json();
  base=mergeLayer(base,layer);
  wave22.forEach(extra=>{base=mergeLayer(base,extra)});
  return new Response(JSON.stringify(base),{status:response.status,statusText:response.statusText,headers:{'Content-Type':'application/json'}});
 }
 if(url.endsWith('biblical-passage-fragments.json')){
  const [response,extension,wave22Extension]=await Promise.all([upstreamFetch(input,init),fragmentPromise,wave22FragmentPromise]);
  if(!response.ok)return response;
  let base=await response.json();
  base=mergeFragments(base,extension);
  base=mergeFragments(base,wave22Extension);
  return new Response(JSON.stringify(base),{status:response.status,statusText:response.statusText,headers:{'Content-Type':'application/json'}});
 }
 return upstreamFetch(input,init);
};
})();
