(()=>{'use strict';
const $=s=>document.querySelector(s), doc=$('#gb-document'), toc=$('#gb-toc'), search=$('#gb-search'), status=$('#gb-status');
if(!doc||!toc)return;
const loaded=new Map(); let manifest=null, observer=null;
const esc=s=>String(s).replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
async function loadSlot(slot){
  if(!slot||slot.dataset.loaded==='true'||loaded.has(slot.id))return loaded.get(slot?.id);
  const path=slot.dataset.path; slot.dataset.loaded='loading';
  const task=fetch(path).then(r=>{if(!r.ok)throw new Error(`${path} ${r.status}`);return r.text()}).then(markup=>{slot.innerHTML=markup;slot.dataset.loaded='true';return slot}).catch(err=>{slot.dataset.loaded='error';slot.innerHTML=`<p class="caution">Could not load this chapter: ${esc(err.message)}</p>`;return slot});
  loaded.set(slot.id,task); return task;
}
function slotFor(entry,kind='chapter'){
  const section=document.createElement('section'); section.className='gb-slot'; section.id=entry.anchor; section.dataset.path=entry.path; section.dataset.loaded='false';
  section.innerHTML=`<p class="gb-placeholder">${kind==='front'?'Front matter':`Chapter ${esc(entry.number)}`} · loading when needed…</p>`; return section;
}
function renderToc(filter=''){
  if(!manifest)return; const q=filter.trim().toLowerCase();
  const entries=manifest.chapters.filter(c=>!q||c.number.toLowerCase().includes(q)||c.title.toLowerCase().includes(q)||(c.legacy_title||'').toLowerCase().includes(q));
  toc.innerHTML=`<a href="#front-matter">Front matter</a>`+entries.map(c=>`<a href="#${c.anchor}" data-anchor="${c.anchor}"><strong>${esc(c.number)}</strong> ${esc(c.title)}${c.status==='index-only'?' <span class="gb-index-only-badge">index only</span>':''}</a>`).join('');
  toc.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{const target=document.getElementById(a.hash.slice(1));loadSlot(target);}));
}
function observe(){
  observer=new IntersectionObserver(items=>items.forEach(x=>{if(x.isIntersecting)loadSlot(x.target);}),{rootMargin:'900px 0px'});
  doc.querySelectorAll('.gb-slot').forEach(s=>observer.observe(s));
  const active=new IntersectionObserver(items=>items.forEach(x=>{if(!x.isIntersecting)return;toc.querySelectorAll('a').forEach(a=>a.setAttribute('aria-current',String(a.hash==='#'+x.target.id)));}),{rootMargin:'-20% 0px -70%'});
  doc.querySelectorAll('.gb-slot').forEach(s=>active.observe(s));
}
async function init(){
  const r=await fetch('book-manifest.json'); if(!r.ok)throw new Error(`book-manifest.json ${r.status}`); manifest=await r.json();
  doc.replaceChildren(); const fm={...manifest.front_matter}; doc.appendChild(slotFor(fm,'front')); manifest.chapters.forEach(c=>doc.appendChild(slotFor(c)));
  renderToc(); observe();
  const hash=decodeURIComponent(location.hash.slice(1)); const target=document.getElementById(hash||'front-matter'); await loadSlot(target); if(hash)requestAnimationFrame(()=>target?.scrollIntoView({block:'start'}));
}
search?.addEventListener('input',e=>renderToc(e.target.value));
init().catch(err=>{if(status)status.textContent=`Reader error: ${err.message}`;else doc.innerHTML=`<p class="caution">Reader error: ${esc(err.message)}</p>`;});
})();
