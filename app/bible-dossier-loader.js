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
function sequenceSentence(items){const values=arr(items).filter(Boolean);return values.length?values.join(' → '):''}
function join(items,separator=' · '){return arr(items).filter(Boolean).join(separator)}
function quoteList(row){
 const quotes=[...arr(row.exact_wording),...arr(row.public_wording),...arr(row.recovered_wording)].filter(Boolean);
 return [...new Set(quotes)];
}
function evidencePanel(title,body,className=''){
 if(!body)return'';
 return `<section class="evidence-panel ${className}"><h4>${esc(title)}</h4>${body}</section>`;
}
function openEvidence(row,scene,argument,scripture,discovery){
 const quotes=quoteList(row);
 const modernBody=[
  scene.setting?paragraph('Setting',scene.setting):'',
  scene.activity?paragraph('Activity',scene.activity):'',
  scene.conversation_trigger?paragraph('Trigger',scene.conversation_trigger):'',
  scene.participants?.length?paragraph('Participants',join(scene.participants)):'',
  scene.surrounding_topics?.length?paragraph('Surrounding topics',join(scene.surrounding_topics)):'',
  scene.lead_up?paragraph('Lead-up',scene.lead_up):'',
  scene.before?paragraph('Before',scene.before):'',
  scene.after?paragraph('After',scene.after):'',
  scene.source_status?paragraph('Scene source status',scene.source_status):''
 ].filter(Boolean).join('');
 const bibleBody=[
  scripture.literary_context?paragraph('Literary context',scripture.literary_context):'',
  scripture.canonical_context?paragraph('Canonical context',scripture.canonical_context):'',
  scripture.historical_context?paragraph('Historical context',scripture.historical_context):'',
  scripture.reception_history?paragraph('Reception history',scripture.reception_history):'',
  scripture.translation_or_textual_caveats?paragraph('Text / translation caveat',scripture.translation_or_textual_caveats):''
 ].filter(Boolean).join('');
 const provenanceBody=[
  paragraph('Project anchor',discovery.project_anchor_date||row.date),
  discovery.scripture_explicit_at_time!==undefined?paragraph('Scripture explicit at the time',String(discovery.scripture_explicit_at_time)):'',
  paragraph('First comparison',discovery.first_comparison_date),
  paragraph('Formal archive date',discovery.first_formal_archive_date),
  paragraph('Source direction',discovery.source_direction||row.source_direction),
  paragraph('Project wording status',row.wording_status),
  `<p class="timestamp-caveat">The timestamp establishes when the modern-side material is attested. It does not by itself establish that the biblical event literally repeated.</p>`
 ].filter(Boolean).join('');
 const quoteBody=quotes.length?quotes.map(item=>`<blockquote class="evidence-quote">${esc(item)}</blockquote>`).join(''):'';
 const sequenceBody=(argument.project_sequence?.length||argument.biblical_sequence?.length)?`<div class="sequence-grid">${argument.project_sequence?.length?`<div><h5>Modern sequence</h5>${list(argument.project_sequence)}</div>`:''}${argument.biblical_sequence?.length?`<div><h5>Biblical sequence</h5>${list(argument.biblical_sequence)}</div>`:''}</div>`:'';
 return `<section class="dossier-open-evidence"><div class="open-evidence-heading"><span class="dossier-kicker">Evidence in the open</span><h3>More of the dossier, without another click</h3><p>The comparator keeps the core context visible by default. Collapsible sections below are reserved for supporting provenance and secondary detail.</p></div><div class="evidence-grid">${evidencePanel('Exact / recovered wording',quoteBody,'wording-panel')}${evidencePanel('Modern circumstances',modernBody,'modern-context-panel')}${evidencePanel('Biblical context',bibleBody,'biblical-context-panel')}${evidencePanel('Chronology &amp; provenance',provenanceBody,'provenance-panel')}</div>${sequenceBody}</section>`;
}

function decorate(){
 const article=document.querySelector('#active-relation .relation[data-relation-id]');
 if(!article||article.dataset.dossierDecorated==='1')return;
 const row=mergedRows.get(article.dataset.relationId);
 if(!row||row.dossier_level!=='A')return;
 article.dataset.dossierDecorated='1';
 const scene=row.scene_context||{},argument=row.relation_argument||{},scripture=row.scripture_context||{},discovery=row.discovery_history||{};
 const parallel=article.querySelector('.parallel');
 if(parallel){
  const paired=document.createElement('section');paired.className='paired-narrative';
  const timSequence=sequenceSentence(argument.project_sequence),bibleSequence=sequenceSentence(argument.biblical_sequence);
  paired.innerHTML=`<div class="paired-intro"><div class="dossier-kicker">Paired event reading · modern source status ${esc(scene.source_status||'unknown')}</div><h3>Two scenes, one structural comparison</h3><p>Read the biblical episode and the dated Tim/Son episode as separate narratives first. The comparison comes from the order of roles, pressures, actions and consequences—not from pretending the two settings are literally identical.</p></div><div class="paired-scenes"><article class="paired-scene modern-scene"><span class="scene-label">Tim / Son scene</span><h4>${esc(row.date||'Modern project chronology')}</h4><p>${esc(scene.summary||row.what_happened||row.project_anchor)}</p>${scene.lead_up?`<p><strong>Lead-up:</strong> ${esc(scene.lead_up)}</p>`:''}${scene.after?`<p><strong>After:</strong> ${esc(scene.after)}</p>`:''}${timSequence?`<p class="scene-sequence"><strong>Sequence:</strong> ${esc(timSequence)}</p>`:''}</article><article class="paired-scene biblical-scene"><span class="scene-label">Biblical scene</span><h4>${esc(join(row.biblical_refs)||'Scripture')}</h4><p>${esc(scripture.literary_context||scripture.canonical_context||'The exact biblical passage appears beside the modern scene below.')}</p>${bibleSequence?`<p class="scene-sequence"><strong>Sequence:</strong> ${esc(bibleSequence)}</p>`:''}</article></div></section>`;
  parallel.before(paired);
  const open=document.createElement('div');open.innerHTML=openEvidence(row,scene,argument,scripture,discovery);const section=open.firstElementChild;if(section)paired.after(section);
 }
 const why=article.querySelector('.why');
 if(why&&argument.why_dense){
  why.querySelector('h3').textContent='Where the stories rhyme';
  const body=why.querySelector('p');if(body)body.textContent=[argument.why_dense,argument.why_it_matters].filter(Boolean).join(' ');
  if(arr(argument.correspondences).length){const matches=document.createElement('div');matches.className='correspondence-list';matches.innerHTML=arr(argument.correspondences).map(item=>`<span>${esc(item)}</span>`).join('');why.appendChild(matches)}
 }
 const boundary=article.querySelector('.boundary-callout');
 if(boundary)boundary.firstChild.textContent='Where the rhyme stops: ';
 if(argument.maximum_claim){
  const max=document.createElement('div');max.className='maximum-claim';max.innerHTML=`<strong>What this comparison can actually establish:</strong> ${esc(argument.maximum_claim)}`;
  (boundary||article.querySelector('.relation-details'))?.before(max);
 }
 const details=article.querySelector('.relation-details');
 if(!details)return;
 const circumstances=document.createElement('details');
 circumstances.innerHTML=`<summary>Tim / Son scene &amp; sequence — supporting detail</summary><div class="detail-body dossier-detail">${paragraph('Setting',scene.setting)}${paragraph('Activity',scene.activity)}${paragraph('Trigger',scene.conversation_trigger)}${scene.participants?.length?paragraph('Participants',join(scene.participants)):''}${scene.surrounding_topics?.length?paragraph('Surrounding topics',join(scene.surrounding_topics)):''}${paragraph('Before',scene.before)}${paragraph('After',scene.after)}${argument.project_sequence?.length?`<h4>Modern sequence</h4>${list(argument.project_sequence)}`:''}<p class="source-status">Scene source status: <strong>${esc(scene.source_status||'unknown')}</strong></p></div>`;
 const bible=document.createElement('details');
 bible.innerHTML=`<summary>Biblical scene &amp; sequence — supporting detail</summary><div class="detail-body dossier-detail">${paragraph('Literary context',scripture.literary_context)}${paragraph('Canonical context',scripture.canonical_context)}${paragraph('Historical context',scripture.historical_context)}${paragraph('Reception history',scripture.reception_history)}${paragraph('Text / translation caveat',scripture.translation_or_textual_caveats)}${argument.biblical_sequence?.length?`<h4>Biblical sequence</h4>${list(argument.biblical_sequence)}`:''}</div>`;
 const history=document.createElement('details');
 history.innerHTML=`<summary>Timestamp &amp; discovery history</summary><div class="detail-body dossier-detail">${paragraph('Project anchor',discovery.project_anchor_date||row.date)}${paragraph('Scripture at the time',String(discovery.scripture_explicit_at_time??''))}${paragraph('First comparison',discovery.first_comparison_date)}${paragraph('Formal archive date',discovery.first_formal_archive_date)}${paragraph('Source direction',discovery.source_direction)}${row.wording_status?paragraph('Project wording status',row.wording_status):''}<p>The timestamp establishes when the modern-side material is attested. It does not by itself establish that the biblical event literally repeated.</p></div>`;
 details.prepend(history);details.prepend(bible);details.prepend(circumstances);
}

const observer=new MutationObserver(()=>decorate());
function start(){const active=document.getElementById('active-relation');if(!active)return;observer.observe(active,{childList:true,subtree:true});dossierPromise.then(d=>{if(!d)return;arr(d.new_relations).forEach(row=>mergedRows.set(row.id,enrichRow(row)));decorate()})}
document.readyState==='loading'?document.addEventListener('DOMContentLoaded',start):start();
})();
