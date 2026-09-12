(()=>{
'use strict';

const nativeFetch=window.fetch.bind(window);
const DOSSIER_PATH='../../knowledge/traditions/biblical-syncretism-dossiers.json';
const FRAGMENT_PATH='../../knowledge/traditions/biblical-passage-fragments-dossiers.json';
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const arr=value=>Array.isArray(value)?value:(value==null?[]:[value]);
let mergedRows=new Map();

async function json(url){const response=await nativeFetch(url);if(!response.ok)throw new Error(`${url}: ${response.status}`);return response.json()}
const dossierPromise=json(DOSSIER_PATH).catch(error=>{console.warn('Bible dossier extension unavailable',error);return null});
const dossierFragmentPromise=json(FRAGMENT_PATH).catch(error=>{console.warn('Bible dossier fragments unavailable',error);return null});

function enrichRow(row){
 const copy={...row};
 if(copy.relation_argument&&typeof copy.relation_argument==='object'){
  const argument=copy.relation_argument;
  copy.relation_arguments=[...arr(copy.relation_arguments),argument.why_dense,argument.why_it_matters,...arr(argument.correspondences),argument.maximum_claim?`Maximum defensible claim: ${argument.maximum_claim}`:''].filter(Boolean);
 }
 if(copy.mismatch&&!arr(copy.weaknesses).includes(copy.mismatch))copy.weaknesses=[...arr(copy.weaknesses),copy.mismatch];
 if(copy.discovery_history?.source_direction&&!copy.source_direction)copy.source_direction=copy.discovery_history.source_direction;
 return copy;
}

function mergeField(base,dossiers){
 if(!dossiers)return base;
 const rows=arr(base.relations).map(row=>({...row})),byId=new Map(rows.map(row=>[row.id,row]));
 arr(dossiers.enrichments).forEach(enrichment=>{const target=byId.get(enrichment.relation_id);if(!target)return;Object.entries(enrichment).forEach(([key,value])=>{if(key!=='relation_id')target[key]=value})});
 arr(dossiers.new_relations).forEach(row=>{if(byId.has(row.id))return;const copy={...row};rows.push(copy);byId.set(copy.id,copy)});
 const enriched=rows.map(enrichRow);mergedRows=new Map(enriched.map(row=>[row.id,row]));
 return {...base,dossier_contract:dossiers.dossier_contract,relations:enriched};
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
  const [response,dossiers]=await Promise.all([nativeFetch(input,init),dossierPromise]);
  if(!response.ok||!dossiers)return response;
  const base=await response.json();
  return new Response(JSON.stringify(mergeField(base,dossiers)),{status:response.status,statusText:response.statusText,headers:{'Content-Type':'application/json'}});
 }
 if(url.endsWith('biblical-passage-fragments.json')){
  const [response,extension]=await Promise.all([nativeFetch(input,init),dossierFragmentPromise]);
  if(!response.ok||!extension)return response;
  const base=await response.json();
  return new Response(JSON.stringify(mergeFragments(base,extension)),{status:response.status,statusText:response.statusText,headers:{'Content-Type':'application/json'}});
 }
 return nativeFetch(input,init);
};

function list(items){const values=arr(items).filter(Boolean);return values.length?`<ol>${values.map(item=>`<li>${esc(item)}</li>`).join('')}</ol>`:''}
function paragraph(label,value){return value?`<p><strong>${esc(label)}:</strong> ${esc(value)}</p>`:''}

function decorate(){
 const article=document.querySelector('#active-relation .relation[data-relation-id]');
 if(!article||article.dataset.dossierDecorated==='1')return;
 const row=mergedRows.get(article.dataset.relationId);
 if(!row||row.dossier_level!=='A')return;
 article.dataset.dossierDecorated='1';
 const scene=row.scene_context||{},argument=row.relation_argument||{},scripture=row.scripture_context||{},discovery=row.discovery_history||{};
 const parallel=article.querySelector('.parallel');
 if(scene.summary&&parallel){
  const section=document.createElement('section');section.className='dossier-scene';
  section.innerHTML=`<div class="dossier-kicker">Circumstance · ${esc(scene.source_status||'context')}</div><h3>What was happening</h3><p>${esc(scene.summary)}</p>${scene.lead_up?`<p class="dossier-leadup"><strong>Lead-up:</strong> ${esc(scene.lead_up)}</p>`:''}`;
  parallel.before(section);
 }
 const why=article.querySelector('.why p');
 if(why&&argument.why_dense)why.textContent=[argument.why_dense,argument.why_it_matters].filter(Boolean).join(' ');
 const boundary=article.querySelector('.boundary-callout');
 if(argument.maximum_claim){
  const max=document.createElement('div');max.className='maximum-claim';max.innerHTML=`<strong>Maximum defensible claim:</strong> ${esc(argument.maximum_claim)}`;
  (boundary||article.querySelector('.relation-details'))?.before(max);
 }
 const details=article.querySelector('.relation-details');
 if(!details)return;
 const circumstances=document.createElement('details');
 circumstances.innerHTML=`<summary>Circumstances &amp; sequence</summary><div class="detail-body dossier-detail">${paragraph('Setting',scene.setting)}${paragraph('Activity',scene.activity)}${paragraph('Trigger',scene.conversation_trigger)}${scene.participants?.length?paragraph('Participants',scene.participants.join(' · ')):''}${scene.surrounding_topics?.length?paragraph('Surrounding topics',scene.surrounding_topics.join(' · ')):''}${paragraph('Before',scene.before)}${paragraph('After',scene.after)}${argument.project_sequence?.length?`<h4>Project sequence</h4>${list(argument.project_sequence)}`:''}<p class="source-status">Scene source status: <strong>${esc(scene.source_status||'unknown')}</strong></p></div>`;
 const bible=document.createElement('details');
 bible.innerHTML=`<summary>Bible in context</summary><div class="detail-body dossier-detail">${paragraph('Literary context',scripture.literary_context)}${paragraph('Canonical context',scripture.canonical_context)}${paragraph('Historical context',scripture.historical_context)}${paragraph('Reception history',scripture.reception_history)}${paragraph('Text / translation caveat',scripture.translation_or_textual_caveats)}${argument.biblical_sequence?.length?`<h4>Biblical sequence</h4>${list(argument.biblical_sequence)}`:''}</div>`;
 const history=document.createElement('details');
 history.innerHTML=`<summary>Discovery history</summary><div class="detail-body dossier-detail">${paragraph('Project anchor',discovery.project_anchor_date)}${paragraph('Scripture at the time',String(discovery.scripture_explicit_at_time??''))}${paragraph('First comparison',discovery.first_comparison_date)}${paragraph('Formal archive date',discovery.first_formal_archive_date)}${paragraph('Source direction',discovery.source_direction)}${row.wording_status?paragraph('Project wording status',row.wording_status):''}</div>`;
 details.prepend(history);details.prepend(bible);details.prepend(circumstances);
}

const observer=new MutationObserver(()=>decorate());
function start(){const active=document.getElementById('active-relation');if(!active)return;observer.observe(active,{childList:true,subtree:true});dossierPromise.then(d=>{if(!d)return;arr(d.new_relations).forEach(row=>mergedRows.set(row.id,enrichRow(row)));decorate()})}
document.readyState==='loading'?document.addEventListener('DOMContentLoaded',start):start();
})();
