(()=>{'use strict';
const $=s=>document.querySelector(s),doc=$('#gb-document'),toc=$('#gb-toc'),search=$('#gb-search'),status=$('#gb-status');
if(!doc||!toc)return;
const loaded=new Map(),bundles=new Map();let manifest=null;
const esc=s=>String(s).replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
async function bundleTemplate(path,anchor){
  if(!bundles.has(path)) bundles.set(path,fetch(path).then(r=>{if(!r.ok)throw new Error(`${path} ${r.status}`);return r.text()}).then(html=>new DOMParser().parseFromString(html,'text/html')));
  const parsed=await bundles.get(path),tpl=[...parsed.querySelectorAll('template[data-anchor]')].find(t=>t.dataset.anchor===anchor);
  if(!tpl)throw new Error(`${anchor} missing from ${path}`);return tpl.innerHTML;
}
async function loadSlot(slot){
  if(!slot||slot.dataset.loaded==='true'||loaded.has(slot.id))return loaded.get(slot?.id);
  slot.dataset.loaded='loading';
  const task=(slot.dataset.bundle?bundleTemplate(slot.dataset.bundle,slot.id):fetch(slot.dataset.path).then(r=>{if(!r.ok)throw new Error(`${slot.dataset.path} ${r.status}`);return r.text()})).then(markup=>{slot.innerHTML=markup;slot.dataset.loaded='true';return slot}).catch(err=>{slot.dataset.loaded='error';slot.innerHTML=`<p class="caution">Could not load this chapter: ${esc(err.message)}</p>`;return slot});
  loaded.set(slot.id,task);return task;
}
function slotFor(entry,kind='chapter'){
  const s=document.createElement('section');s.className='gb-slot';s.id=entry.anchor;s.dataset.path=entry.path;s.dataset.loaded='false';if(entry.bundle)s.dataset.bundle=entry.bundle;
  s.innerHTML=`<p class="gb-placeholder">${kind==='front'?'Front matter':`Chapter ${esc(entry.number)}`} · loading when needed…</p>`;return s;
}
function renderToc(filter=''){
  if(!manifest)return;const q=filter.trim().toLowerCase(),entries=manifest.chapters.filter(c=>!q||c.number.toLowerCase().includes(q)||c.title.toLowerCase().includes(q)||(c.legacy_title||'').toLowerCase().includes(q));
  toc.innerHTML=`<a href="#front-matter">Front matter</a>`+entries.map(c=>`<a href="#${c.anchor}"><strong>${esc(c.number)}</strong> ${esc(c.title)}${c.status==='index-only'?' <span class="gb-index-only-badge">index only</span>':''}</a>`).join('');
  toc.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>loadSlot(document.getElementById(a.hash.slice(1)))));
}
function observe(){
  const lazy=new IntersectionObserver(xs=>xs.forEach(x=>x.isIntersecting&&loadSlot(x.target)),{rootMargin:'900px 0px'}),active=new IntersectionObserver(xs=>xs.forEach(x=>{if(x.isIntersecting)toc.querySelectorAll('a').forEach(a=>a.setAttribute('aria-current',String(a.hash==='#'+x.target.id)))}),{rootMargin:'-20% 0px -70%'});
  doc.querySelectorAll('.gb-slot').forEach(s=>{lazy.observe(s);active.observe(s)});
}
async function init(){
  const spec=await fetch('book-index.json').then(r=>{if(!r.ok)throw new Error(`book-index.json ${r.status}`);return r.json()}),parts=await Promise.all(spec.shards.map(p=>fetch(p).then(r=>{if(!r.ok)throw new Error(`${p} ${r.status}`);return r.json()})));
  manifest={front_matter:spec.front_matter,chapters:parts.flat()};doc.replaceChildren();doc.appendChild(slotFor(manifest.front_matter,'front'));manifest.chapters.forEach(c=>doc.appendChild(slotFor(c)));renderToc();observe();
  const hash=decodeURIComponent(location.hash.slice(1)),target=document.getElementById(hash||'front-matter');await loadSlot(target);if(hash)requestAnimationFrame(()=>target?.scrollIntoView({block:'start'}));
}
search?.addEventListener('input',e=>renderToc(e.target.value));init().catch(err=>{(status||doc).textContent=`Reader error: ${err.message}`});
})();
