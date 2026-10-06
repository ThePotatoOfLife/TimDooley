(()=>{
'use strict';
const upstreamFetch=window.fetch.bind(window);
const DOSSIER_PATH='../../knowledge/traditions/biblical-syncretism-dossiers.json';
const PROMOTION_PATH='../../knowledge/traditions/biblical-syncretism-dossiers-promotions.json';
const FRAGMENT_PATH='../../knowledge/traditions/biblical-passage-fragments-dossiers.json';
const arr=value=>Array.isArray(value)?value:(value==null?[]:[value]);
const load=url=>upstreamFetch(url).then(r=>r.ok?r.json():null).catch(error=>{console.warn('Bible dossier extension unavailable',url,error);return null});
const dossierPromise=load(DOSSIER_PATH);
const promotionPromise=load(PROMOTION_PATH);
const dossierFragmentPromise=load(FRAGMENT_PATH);
function enrichRow(row){
 const copy={...row};
 if(copy.relation_argument&&typeof copy.relation_argument==='object'){
  const argument=copy.relation_argument;
  copy.relation_arguments=[...arr(copy.relation_arguments),argument.why_dense,argument.why_it_matters,...arr(argument.correspondences),argument.maximum_claim?('Maximum defensible claim: '+argument.maximum_claim):''].filter(Boolean);
 }
 if(copy.mismatch&&!arr(copy.weaknesses).includes(copy.mismatch))copy.weaknesses=[...arr(copy.weaknesses),copy.mismatch];
 if(copy.discovery_history?.source_direction&&!copy.source_direction)copy.source_direction=copy.discovery_history.source_direction;
 return copy;
}
function applyLayer(rows,byId,layer){
 if(!layer)return;
 arr(layer.enrichments).forEach(enrichment=>{const target=byId.get(enrichment.relation_id);if(!target)return;Object.entries(enrichment).forEach(([key,value])=>{if(key!=='relation_id')target[key]=value})});
 arr(layer.new_relations).forEach(row=>{if(byId.has(row.id))return;const copy={...row};rows.push(copy);byId.set(copy.id,copy)});
}
function mergeField(base,...layers){
 const rows=arr(base.relations).map(row=>({...row})),byId=new Map(rows.map(row=>[row.id,row]));
 layers.forEach(layer=>applyLayer(rows,byId,layer));
 const dossierContract=layers.find(layer=>layer?.dossier_contract)?.dossier_contract;
 return {...base,...(dossierContract?{dossier_contract:dossierContract}:{}),relations:rows.map(enrichRow)};
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
  const [response,dossiers,promotions]=await Promise.all([upstreamFetch(input,init),dossierPromise,promotionPromise]);
  if(!response.ok)return response;
  const base=await response.json();
  return new Response(JSON.stringify(mergeField(base,dossiers,promotions)),{status:response.status,statusText:response.statusText,headers:{'Content-Type':'application/json'}});
 }
 if(url.endsWith('biblical-passage-fragments.json')){
  const [response,extension]=await Promise.all([upstreamFetch(input,init),dossierFragmentPromise]);
  if(!response.ok||!extension)return response;
  const base=await response.json();
  return new Response(JSON.stringify(mergeFragments(base,extension)),{status:response.status,statusText:response.statusText,headers:{'Content-Type':'application/json'}});
 }
 return upstreamFetch(input,init);
};
})();
