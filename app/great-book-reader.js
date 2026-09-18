(()=>{'use strict';
const $=s=>document.querySelector(s),doc=$('#gb-document'),toc=$('#gb-toc'),search=$('#gb-search'),status=$('#gb-status');
if(!doc||!toc)return;
const loaderApi=globalThis.PotatoGreatBookLoader;
if(!loaderApi?.createChapterLoader){(status||doc).textContent='Reader error: chapter loader unavailable';return}
let manifest=null,activeCurrentId='';
const esc=s=>String(s).replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const safeChapterToken=value=>String(value||'').replace(/\./g,'-');
const safeChapterPath=path=>String(path||'').replace(/chapter-(\d+(?:\.\d+)+)/g,(_,number)=>`chapter-${safeChapterToken(number)}`);
const chapterLoader=loaderApi.createChapterLoader({
  sanitizePath:safeChapterPath,
  onError:(slot,error)=>{slot.innerHTML=`<p class="caution gb-load-error">Could not load this chapter: ${esc(error.message)}</p>`},
});
async function loadSlot(slot,options={}){
  const result=await chapterLoader.loadSlot(slot,options);
  if(result?.id&&result.id===activeCurrentId)publishCurrent(result);
  return result;
}
async function loadAllSlots(options={}){
  const slots=[...doc.querySelectorAll('.gb-slot')];
  if(!slots.length)return {loaded:[],failed:[]};
  if(status)status.textContent='Loading remaining book text for read-aloud…';
  const result=await chapterLoader.loadSlots(slots,{concurrency:5,signal:options.signal});
  if(status)status.textContent=result.failed.length
    ?`${result.failed.length} chapter${result.failed.length===1?'':'s'} could not load. Read-aloud will use the chapters that are available.`
    :'Whole book ready to read aloud.';
  return result;
}
function slotFor(entry,kind='chapter'){
  const s=document.createElement('section');s.className='gb-slot';s.id=kind==='front'?entry.anchor:`chapter-${safeChapterToken(entry.number)}`;s.dataset.path=kind==='front'?entry.path:safeChapterPath(entry.path);s.dataset.loaded='false';
  s.innerHTML=`<p class="gb-placeholder">${kind==='front'?'Front matter':`Chapter ${esc(entry.number)}`} · loading when needed…</p>`;return s;
}
function renderToc(filter=''){
  if(!manifest)return;const q=filter.trim().toLowerCase(),entries=manifest.chapters.filter(c=>!q||c.number.toLowerCase().includes(q)||c.title.toLowerCase().includes(q)||(c.legacy_title||'').toLowerCase().includes(q));
  toc.innerHTML=`<a href="#front-matter">Front matter</a>`+entries.map(c=>`<a href="#chapter-${safeChapterToken(c.number)}"><strong>${esc(c.number)}</strong> ${esc(c.title)}${c.status==='index-only'?' <span class="gb-index-only-badge">index only</span>':''}</a>`).join('');
  toc.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>loadSlot(document.getElementById(a.hash.slice(1))).catch(()=>{})));
}
function publishCurrent(slot){
  if(!slot||slot.dataset.loaded!=='true')return;
  doc.dispatchEvent(new CustomEvent('potato:tts-current',{bubbles:false,detail:{item:slot}}));
}
function observe(){
  const lazy=new IntersectionObserver(xs=>xs.forEach(x=>{if(x.isIntersecting)loadSlot(x.target).catch(()=>{})}),{rootMargin:'900px 0px'}),active=new IntersectionObserver(xs=>xs.forEach(x=>{if(!x.isIntersecting)return;activeCurrentId=x.target.id;toc.querySelectorAll('a').forEach(a=>a.setAttribute('aria-current',String(a.hash==='#'+x.target.id)));publishCurrent(x.target)}),{rootMargin:'-20% 0px -70%'});
  doc.querySelectorAll('.gb-slot').forEach(s=>{lazy.observe(s);active.observe(s)});
}
async function init(){
  const spec=await fetch('../great-book/book-index.json').then(r=>{if(!r.ok)throw new Error(`book-index.json ${r.status}`);return r.json()}),parts=await Promise.all(spec.shards.map(p=>fetch(p).then(r=>{if(!r.ok)throw new Error(`${p} ${r.status}`);return r.json()})));
  manifest={front_matter:spec.front_matter,chapters:parts.flat()};doc.replaceChildren();doc.appendChild(slotFor(manifest.front_matter,'front'));manifest.chapters.forEach(c=>doc.appendChild(slotFor(c)));renderToc();observe();
  const hash=safeChapterToken(decodeURIComponent(location.hash.slice(1))).replace(/^chapter-/,'chapter-'),target=document.getElementById(hash||'front-matter');
  activeCurrentId=target?.id||'';
  try{await loadSlot(target)}catch(error){if(status)status.textContent=`Could not load chapter: ${error.message}`}
  publishCurrent(target);if(hash)requestAnimationFrame(()=>target?.scrollIntoView({block:'start'}));
}
doc.addEventListener('potato:tts-prepare',event=>{
  const detail=event.detail;
  if(!detail||detail.sectionId!=='all'||typeof detail.waitUntil!=='function')return;
  detail.waitUntil(loadAllSlots({signal:detail.signal}));
});
search?.addEventListener('input',e=>renderToc(e.target.value));init().catch(err=>{(status||doc).textContent=`Reader error: ${err.message}`});
})();
