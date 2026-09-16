(()=>{'use strict';
const $=s=>document.querySelector(s),doc=$('#gb-document'),toc=$('#gb-toc'),search=$('#gb-search'),status=$('#gb-status');
if(!doc||!toc)return;
const loaded=new Map();let manifest=null,ttsInstance=null;
const esc=s=>String(s).replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const safeChapterToken=value=>String(value||'').replace(/\./g,'-');
const safeChapterPath=path=>String(path||'').replace(/chapter-(\d+(?:\.\d+)+)/g,(_,number)=>`chapter-${safeChapterToken(number)}`);
async function loadSlot(slot){
  if(!slot||slot.dataset.loaded==='true'||loaded.has(slot.id))return loaded.get(slot?.id);
  slot.dataset.loaded='loading';
  const path=safeChapterPath(slot.dataset.path);
  const task=fetch(path).then(r=>{if(!r.ok)throw new Error(`${path} ${r.status}`);return r.text()}).then(markup=>{slot.innerHTML=markup;slot.dataset.loaded='true';ttsInstance?.ensureListenButtons?.();ttsInstance?.refresh?.();return slot}).catch(err=>{slot.dataset.loaded='error';slot.innerHTML=`<p class="caution">Could not load this chapter: ${esc(err.message)}</p>`;return slot});
  loaded.set(slot.id,task);return task;
}
async function loadAllSlots(){
  const slots=[...doc.querySelectorAll('.gb-slot')];
  await Promise.all(slots.map(loadSlot));
  return slots;
}
function slotFor(entry,kind='chapter'){
  const s=document.createElement('section');s.className='gb-slot';s.id=kind==='front'?entry.anchor:`chapter-${safeChapterToken(entry.number)}`;s.dataset.path=kind==='front'?entry.path:safeChapterPath(entry.path);s.dataset.loaded='false';
  s.innerHTML=`<p class="gb-placeholder">${kind==='front'?'Front matter':`Chapter ${esc(entry.number)}`} · loading when needed…</p>`;return s;
}
function renderToc(filter=''){
  if(!manifest)return;const q=filter.trim().toLowerCase(),entries=manifest.chapters.filter(c=>!q||c.number.toLowerCase().includes(q)||c.title.toLowerCase().includes(q)||(c.legacy_title||'').toLowerCase().includes(q));
  toc.innerHTML=`<a href="#front-matter">Front matter</a>`+entries.map(c=>`<a href="#chapter-${safeChapterToken(c.number)}"><strong>${esc(c.number)}</strong> ${esc(c.title)}${c.status==='index-only'?' <span class="gb-index-only-badge">index only</span>':''}</a>`).join('');
  toc.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>loadSlot(document.getElementById(a.hash.slice(1)))));
}
function observe(){
  const lazy=new IntersectionObserver(xs=>xs.forEach(x=>x.isIntersecting&&loadSlot(x.target)),{rootMargin:'900px 0px'}),active=new IntersectionObserver(xs=>xs.forEach(x=>{if(x.isIntersecting)toc.querySelectorAll('a').forEach(a=>a.setAttribute('aria-current',String(a.hash==='#'+x.target.id)))}),{rootMargin:'-20% 0px -70%'});
  doc.querySelectorAll('.gb-slot').forEach(s=>{lazy.observe(s);active.observe(s)});
}
function mountTts(){
  const host=$('#great-book-tts'),Longform=globalThis.PotatoLongformTTS,Drawer=globalThis.PotatoTTSDrawer;
  if(!host||!Longform||!Drawer)return;
  ttsInstance=Longform.mount({mount:host,root:doc,id:'great-book-reader',label:'The Great Book of Potato',allLabel:'Whole book',currentLabel:'Current chapter',selectionLabel:'Selection',itemSelector:'.gb-chapter-fragment',excludeSelector:'.gb-placeholder,.caution'});
  if(!ttsInstance)return;
  const drawer=ttsInstance.drawer,originalPlay=drawer.playSection?.bind(drawer);
  if(originalPlay)drawer.playSection=async id=>{if(id==='all'){status.textContent='Loading the complete book for reading…';await loadAllSlots();ttsInstance.refresh();status.textContent='Complete book loaded for reading.'}return originalPlay(id)};
}
async function init(){
  const spec=await fetch('../great-book/book-index.json').then(r=>{if(!r.ok)throw new Error(`book-index.json ${r.status}`);return r.json()}),parts=await Promise.all(spec.shards.map(p=>fetch(p).then(r=>{if(!r.ok)throw new Error(`${p} ${r.status}`);return r.json()})));
  manifest={front_matter:spec.front_matter,chapters:parts.flat()};doc.replaceChildren();doc.appendChild(slotFor(manifest.front_matter,'front'));manifest.chapters.forEach(c=>doc.appendChild(slotFor(c)));renderToc();observe();mountTts();
  const hash=safeChapterToken(decodeURIComponent(location.hash.slice(1))).replace(/^chapter-/,'chapter-'),target=document.getElementById(hash||'front-matter');await loadSlot(target);if(hash)requestAnimationFrame(()=>target?.scrollIntoView({block:'start'}));
}
search?.addEventListener('input',e=>renderToc(e.target.value));init().catch(err=>{(status||doc).textContent=`Reader error: ${err.message}`});
})();
