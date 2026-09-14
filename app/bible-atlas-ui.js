(()=>{
'use strict';
const $=id=>document.getElementById(id);
const norm=v=>String(v||'').trim().toLowerCase();
const uniq=items=>[...new Map(items.filter(Boolean).map(item=>[`${item.id}|${item.query}`,item])).values()];
function bookFromRef(ref){return String(ref||'').replace(/\s+\d.*$/,'').trim()}
function topicsFor(corpus,route){
  if(route==='stories')return (corpus.scenes||[]).map(scene=>({id:scene.id,label:scene.title,query:String(scene.canonical_span||scene.book||'').replace(/:\d.*$/,'')}));
  if(route==='symbols')return uniq((corpus.relations||[]).flatMap(row=>(row.motifs||[]).map(value=>({id:norm(value),label:value,query:value})))).sort((a,b)=>a.label.localeCompare(b.label));
  if(route==='actions')return uniq((corpus.relations||[]).flatMap(row=>(row.operators||[]).map(value=>({id:norm(value),label:value,query:value})))).sort((a,b)=>a.label.localeCompare(b.label));
  if(route==='roles')return uniq((corpus.relations||[]).flatMap(row=>[row.actor,...(row.roles||[])].filter(Boolean).map(value=>({id:norm(value),label:value,query:value})))).sort((a,b)=>a.label.localeCompare(b.label));
  if(route==='books')return uniq((corpus.relations||[]).flatMap(row=>(row.biblical_refs||[]).map(bookFromRef).filter(Boolean).map(value=>({id:norm(value),label:value,query:value})))).sort((a,b)=>a.label.localeCompare(b.label));
  if(route==='timeline')return ['2011','2016','2017','2018','2019','2024','2025','2026'].map(year=>({id:year,label:year,query:year}));
  return [];
}
function setFind(query){const field=$('search');if(!field)return;field.value=query||'';field.dispatchEvent(new Event('input',{bubbles:true}));}
function renderBreadcrumbs(state){const target=$('atlas-breadcrumbs');if(!target||!window.BibleAtlas)return;target.innerHTML='';window.BibleAtlas.breadcrumbs(state).forEach((crumb,index)=>{if(index){const sep=document.createElement('span');sep.textContent='›';sep.className='atlas-separator';target.appendChild(sep)}const button=document.createElement('button');button.type='button';button.className='atlas-crumb';button.textContent=crumb.label;button.addEventListener('click',()=>{if(crumb.kind==='route')selectRoute(crumb.id);else if(crumb.kind==='topic')selectTopic(crumb.id)});target.appendChild(button)})}
let corpus=null;let state={route:'stories'};
function selectTopic(id){const topic=topicsFor(corpus,state.route).find(item=>item.id===id);if(!topic)return;state={...state,topic:id};document.querySelectorAll('.atlas-topic').forEach(button=>button.classList.toggle('is-active',button.dataset.topic===id));setFind(topic.query);renderBreadcrumbs(state)}
function renderTopics(){const target=$('atlas-topics');if(!target)return;const items=topicsFor(corpus,state.route);target.innerHTML='';const head=document.createElement('div');head.className='atlas-topic-head';head.textContent=items.length?`Choose from ${items.length} paths`:'No paths in this route yet';target.appendChild(head);const grid=document.createElement('div');grid.className='atlas-topic-grid';items.slice(0,72).forEach(item=>{const button=document.createElement('button');button.type='button';button.className='atlas-topic';button.dataset.topic=item.id;button.textContent=item.label;button.addEventListener('click',()=>selectTopic(item.id));grid.appendChild(button)});target.appendChild(grid)}
function selectRoute(route){state={route};document.querySelectorAll('.atlas-route').forEach(button=>button.classList.toggle('is-active',button.dataset.route===route));setFind('');renderTopics();renderBreadcrumbs(state)}
function renderRoutes(){const target=$('atlas-routes');if(!target||!window.BibleAtlas)return;target.innerHTML='';window.BibleAtlas.routes.forEach(route=>{const button=document.createElement('button');button.type='button';button.className='atlas-route';button.dataset.route=route.id;button.textContent=route.label;button.addEventListener('click',()=>selectRoute(route.id));target.appendChild(button)})}
async function start(){const shell=$('atlas-explorer');if(!shell||!window.BibleCorpus||!window.BibleAtlas)return;try{corpus=await window.BibleCorpus.load();renderRoutes();selectRoute('stories');shell.hidden=false}catch(error){console.warn('Bible atlas explorer unavailable',error)}}
window.BibleAtlasUI={topicsFor,start};
document.readyState==='loading'?document.addEventListener('DOMContentLoaded',start):start();
})();
