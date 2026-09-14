(()=>{
'use strict';
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const arr=value=>Array.isArray(value)?value:(value==null?[]:[value]);
let corpus=null;
let relationMap=new Map();
let sceneMap=new Map();

function chips(values,className='scene-chip'){
  const items=arr(values).filter(Boolean);
  return items.length?`<div class="scene-chips">${items.map(item=>`<span class="${className}">${esc(item)}</span>`).join('')}</div>`:'';
}
function sequence(values){
  const items=arr(values).filter(Boolean);
  return items.length?`<ol class="whole-scene-sequence">${items.map(item=>`<li>${esc(item)}</li>`).join('')}</ol>`:'';
}
function sceneCard(scene,primary=false){
  const limits=arr(scene.counterreadings_or_limits).filter(Boolean);
  return `<article class="whole-scene-card${primary?' primary-scene':''}" data-biblical-scene="${esc(scene.id)}">
    <header><span class="scene-label">${primary?'Primary biblical situation':'Related biblical situation'}</span><h4>${esc(scene.title)}</h4><p class="scene-span">${esc(scene.canonical_span)}</p></header>
    <div class="scene-actions"><button type="button" class="read-scripture" data-read-scene="${esc(scene.id)}">Read exact WEB text</button></div>
    <p class="scene-summary">${esc(scene.summary)}</p>
    ${scene.lead_in?`<p><strong>Lead-in:</strong> ${esc(scene.lead_in)}</p>`:''}
    ${sequence(scene.sequence)}
    ${scene.outcome?`<p><strong>Outcome:</strong> ${esc(scene.outcome)}</p>`:''}
    ${scene.what_follows?`<p><strong>What follows:</strong> ${esc(scene.what_follows)}</p>`:''}
    ${(scene.roles?.length||scene.operators?.length)?`<div class="scene-function-grid"><div><strong>Roles</strong>${chips(scene.roles)}</div><div><strong>Actions</strong>${chips(scene.operators)}</div></div>`:''}
    ${scene.literary_context?`<details><summary>Literary context</summary><p>${esc(scene.literary_context)}</p></details>`:''}
    ${scene.historical_context?`<details><summary>Historical context</summary><p>${esc(scene.historical_context)}</p></details>`:''}
    ${limits.length?`<details class="scene-limits"><summary>Where not to overread it</summary><ul>${limits.map(item=>`<li>${esc(item)}</li>`).join('')}</ul></details>`:''}
  </article>`;
}
function linkedScenes(row){
  const ids=arr(row?.biblical_scene_ids),primary=row?.primary_biblical_scene_id;
  return ids.map(id=>sceneMap.get(id)).filter(Boolean).sort((a,b)=>a.id===primary?-1:b.id===primary?1:0);
}
function wireSceneButtons(section){
  section.querySelectorAll('[data-read-scene]').forEach(button=>button.addEventListener('click',()=>{
    const scene=sceneMap.get(button.dataset.readScene);
    if(scene&&window.BibleScriptureReader)window.BibleScriptureReader.openScene(scene);
  }));
}
function decorate(){
  const article=document.querySelector('#active-relation .relation[data-relation-id]');
  if(!article||!corpus)return;
  const id=article.dataset.relationId;
  if(article.dataset.sceneReaderFor===id)return;
  article.querySelector(':scope > .whole-scene-reader')?.remove();
  const row=relationMap.get(id),scenes=linkedScenes(row);
  article.dataset.sceneReaderFor=id;
  if(!scenes.length)return;
  const section=document.createElement('section');
  section.className='whole-scene-reader';
  section.innerHTML=`<div class="whole-scene-heading"><span class="dossier-kicker">Whole situation</span><h3>Read the biblical episode, not only the matching verse</h3><p>This scene layer keeps the passage's actors, order, setting and limits intact before the comparison is interpreted.</p></div>${scenes.map((scene,index)=>sceneCard(scene,index===0)).join('')}`;
  wireSceneButtons(section);
  const witness=article.querySelector(':scope > .witness-dossier');
  const paired=article.querySelector(':scope > .paired-narrative');
  const parallel=article.querySelector(':scope > .parallel');
  const anchor=witness||paired||parallel||article.firstElementChild;
  anchor?.before(section);
}
async function start(){
  const active=document.getElementById('active-relation');
  if(!active||!window.BibleCorpus)return;
  try{
    corpus=await window.BibleCorpus.load();
    relationMap=new Map(corpus.relations.map(row=>[row.id,row]));
    sceneMap=new Map(corpus.scenes.map(scene=>[scene.id,scene]));
    new MutationObserver(decorate).observe(active,{childList:true,subtree:true});
    decorate();
  }catch(error){console.warn('Whole biblical scene reader unavailable',error)}
}
window.BibleSceneReader={sceneCard,linkedScenes,start};
document.readyState==='loading'?document.addEventListener('DOMContentLoaded',start):start();
})();
