(()=>{
'use strict';
const $=id=>document.getElementById(id);
const norm=v=>String(v||'').trim().toLowerCase();
const uniq=items=>[...new Map(items.filter(Boolean).map(item=>[item.id,item])).values()];
function bookFromRef(ref){return String(ref||'').replace(/\s+\d.*$/,'').trim()}
function topicsFor(corpus,route){
  if(route==='stories')return (corpus.scenes||[]).map(scene=>({id:scene.id,label:scene.title,query:String(scene.canonical_span||scene.book||'').replace(/:\d.*$/,'')}));
  if(['roles','symbols','actions'].includes(route))return window.BibleAtlas?.curatedTopics?.[route]||[];
  if(route==='books'){
    const present=new Set((corpus.relations||[]).flatMap(row=>(row.biblical_refs||[]).map(bookFromRef).filter(Boolean)));
    return (window.BibleAtlas?.bookOrder||[]).filter(book=>present.has(book)).map(book=>({id:norm(book),label:book,query:book}));
  }
  if(route==='timeline')return ['2011','2016','2017','2018','2019','2024','2025','2026'].map(year=>({id:year,label:year,query:year}));
  return [];
}
function emit(node,event='change'){node?.dispatchEvent(new Event(event,{bubbles:true}))}
function setFind(query){const field=$('search');if(!field)return;field.value=query||'';emit(field,'input')}
function clearNative(){
  setFind('');
  const book=$('bible-book'),operator=$('operator'),actor=$('actor'),from=$('from-year'),to=$('to-year');
  if(book){book.value='';emit(book)} if(operator){operator.value='';emit(operator)} if(actor){actor.value='';emit(actor)}
  if(from){from.value='';emit(from,'input')} if(to){to.value='';emit(to,'input')}
}
function setSelect(id,value){const select=$(id);if(!select)return false;const option=[...select.options].find(item=>norm(item.value)===norm(value)||norm(item.textContent)===norm(value));if(!option)return false;select.value=option.value;emit(select);return true}
function setYear(year){const from=$('from-year'),to=$('to-year');if(!from||!to)return false;from.value=year;to.value=year;emit(from,'input');emit(to,'input');return true}
function applyTopic(topic){
  clearNative();
  if(state.route==='books'&&setSelect('bible-book',topic.label))return;
  if(state.route==='actions'&&setSelect('operator',topic.id))return;
  if(state.route==='roles'&&setSelect('actor',topic.id))return;
  if(state.route==='timeline'&&setYear(topic.id))return;
  setFind(topic.query);
}
function syncUrl(){const url=new URL(location.href);url.searchParams.set('route',state.route);if(state.topic)url.searchParams.set('topic',state.topic);else url.searchParams.delete('topic');history.replaceState(null,'',url)}
function renderBreadcrumbs(state){const target=$('atlas-breadcrumbs');if(!target||!window.BibleAtlas)return;target.innerHTML='';window.BibleAtlas.breadcrumbs(state).forEach((crumb,index)=>{if(index){const sep=document.createElement('span');sep.textContent='›';sep.className='atlas-separator';target.appendChild(sep)}const button=document.createElement('button');button.type='button';button.className='atlas-crumb';button.textContent=crumb.label;button.addEventListener('click',()=>{if(crumb.kind==='route')selectRoute(crumb.id);else if(crumb.kind==='topic')selectTopic(crumb.id)});target.appendChild(button)})}
let corpus=null;let state={route:'stories'};
function selectTopic(id,{persist=true}={}){const topic=topicsFor(corpus,state.route).find(item=>item.id===id);if(!topic)return;state={...state,topic:id};document.querySelectorAll('.atlas-topic').forEach(button=>button.classList.toggle('is-active',button.dataset.topic===id));applyTopic(topic);renderBreadcrumbs(state);if(persist)syncUrl()}
function renderTopics(){const target=$('atlas-topics');if(!target)return;const items=topicsFor(corpus,state.route);target.innerHTML='';const head=document.createElement('div');head.className='atlas-topic-head';head.textContent=items.length?`Choose from ${items.length} clear paths`:'No paths in this route yet';target.appendChild(head);const grid=document.createElement('div');grid.className='atlas-topic-grid';items.forEach(item=>{const button=document.createElement('button');button.type='button';button.className='atlas-topic';button.dataset.topic=item.id;button.textContent=item.label;button.addEventListener('click',()=>selectTopic(item.id));grid.appendChild(button)});target.appendChild(grid)}
function selectRoute(route,{persist=true,clear=true}={}){state={route};document.querySelectorAll('.atlas-route').forEach(button=>button.classList.toggle('is-active',button.dataset.route===route));if(clear)clearNative();renderTopics();renderBreadcrumbs(state);if(persist)syncUrl()}
function renderRoutes(){const target=$('atlas-routes');if(!target||!window.BibleAtlas)return;target.innerHTML='';window.BibleAtlas.routes.forEach(route=>{const button=document.createElement('button');button.type='button';button.className='atlas-route';button.dataset.route=route.id;button.textContent=route.label;button.addEventListener('click',()=>selectRoute(route.id));target.appendChild(button)})}
async function start(){const shell=$('atlas-explorer');if(!shell||!window.BibleCorpus||!window.BibleAtlas)return;try{corpus=await window.BibleCorpus.load();renderRoutes();const params=new URLSearchParams(location.search),route=params.get('route'),topic=params.get('topic'),valid=window.BibleAtlas.routes.some(item=>item.id===route);selectRoute(valid?route:'stories',{persist:false,clear:false});if(topic)selectTopic(topic,{persist:false});shell.hidden=false}catch(error){console.warn('Bible atlas explorer unavailable',error)}}
window.BibleAtlasUI={topicsFor,start};
document.readyState==='loading'?document.addEventListener('DOMContentLoaded',start):start();
})();
