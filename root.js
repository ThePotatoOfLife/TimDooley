(() => {
  'use strict';
  const DATA_URL='./data/root-record-index.json', MANIFEST_URL='./data/root-navigation.json', STORAGE_KEY='potato-root-state-v8';
  const $=(s,r=document)=>r.querySelector(s);
  const esc=v=>String(v??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const state={manifest:null,records:[],selected:null,expanded:new Set(),rendered:new Set(),sources:new Map()};
  const save=()=>{try{localStorage.setItem(STORAGE_KEY,JSON.stringify({expanded:[...state.expanded],selected:state.selected}));}catch(_) {}};
  const load=()=>{try{const x=JSON.parse(localStorage.getItem(STORAGE_KEY)||'{}');(x.expanded||[]).forEach(k=>state.expanded.add(k));state.selected=x.selected||null;}catch(_) {}};
  const hash=id=>history.replaceState(null,'',id?`${location.pathname}#node=${encodeURIComponent(id)}`:location.pathname);
  const hashId=()=>new URLSearchParams(location.hash.replace(/^#/,'')).get('node');
  const unique=rows=>{const seen=new Set();return rows.filter(r=>{const k=r.canonical_id||`${r.source}:${r.id}:${JSON.stringify(r.path||[])}`;if(seen.has(k))return false;seen.add(k);return true;}).sort((a,b)=>String(a.name||a.id).localeCompare(String(b.name||b.id)));};
  function matches(r,c){
    if(c.all)return true;
    if(c.paths?.length)return c.paths.some(p=>(r.navigation_path||[]).join('/').toLowerCase()===String(p).toLowerCase());
    if(c.root&&String(r.repository_root).toLowerCase()!==String(c.root).toLowerCase())return false;
    if(c.types?.length&&!c.types.includes(String(r.type||'').toLowerCase()))return false;
    if(c.families?.length&&!c.families.includes(String(r.owner_family||'').toLowerCase()))return false;
    if(c.scales?.length&&!c.scales.includes(String(r.repository_scale||'').toLowerCase()))return false;
    if(c.role&&String(r.record_role||'').toLowerCase()!==String(c.role).toLowerCase())return false;
    if(c.terms?.length){const h=[r.id,r.name,r.description,r.source,r.owner_family,r.repository_layer,(r.navigation_path||[]).join(' ')].join(' ').toLowerCase();if(!c.terms.some(t=>h.includes(String(t).toLowerCase())))return false;}
    return !!(c.types||c.families||c.scales||c.role||c.terms);
  }
  function renderHtml(html,target){
    target.innerHTML='';if(!html)return false;
    try{const parsed=new DOMParser().parseFromString(String(html),'text/html');const source=parsed.body&&parsed.body.children.length?parsed.body:parsed.documentElement;[...source.childNodes].forEach(n=>target.appendChild(document.importNode(n,true)));return true;}catch(_){target.textContent=String(html);return true;}
  }
  function valueHtml(v){
    if(v===null||v===undefined)return '';
    if(typeof v==='string')return `<p>${esc(v)}</p>`;
    if(typeof v==='number'||typeof v==='boolean')return `<p>${esc(v)}</p>`;
    if(Array.isArray(v))return v.length?`<ul>${v.map(x=>`<li>${typeof x==='object'?`<code>${esc(JSON.stringify(x))}</code>`:esc(x)}</li>`).join('')}</ul>`:'';
    if(typeof v==='object')return Object.entries(v).map(([k,x])=>`<section><h3>${esc(k.replace(/[_-]/g,' '))}</h3>${valueHtml(x)}</section>`).join('');
    return '';
  }
  async function hydrate(r){
    if(!r?.source||!Array.isArray(r.path)||!r.source.startsWith('data/'))return null;
    if(state.sources.has(r.source))return state.sources.get(r.source);
    try{const res=await fetch(`./${r.source}`,{cache:'no-store'});if(!res.ok)return null;const data=await res.json();state.sources.set(r.source,data);return data;}catch(_){return null;}
  }
  function atPath(root,path){let x=root;for(const p of path||[]){if(x==null)return null;x=x[p];}return x;}
  async function loadIntoFrame(r){
    const target=$('#frame-content');if(!target)return;
    target.innerHTML='<p>Opening record…</p>';
    const html=r.html||r.content_html||r.document_html;
    if(html&&renderHtml(html,target))return;
    const source=await hydrate(r), original=source?atPath(source,r.path):null;
    const rich=original&&typeof original==='object'?(original.html||original.content_html||original.document_html):null;
    if(rich&&renderHtml(rich,target))return;
    let body=`<h1>${esc(r.name||r.id||'Record')}</h1>`;
    if(r.description)body+=`<p>${esc(r.description)}</p>`;
    if(original&&typeof original==='object'){
      const skip=new Set(['id','slug','key','name','title','label','description','definition','summary','html','content_html','document_html']);
      const details=Object.entries(original).filter(([k])=>!skip.has(k));
      if(details.length)body+=`<div class="source-record"><h2>Record data</h2>${details.map(([k,v])=>`<section><h3>${esc(k.replace(/[_-]/g,' '))}</h3>${valueHtml(v)}</section>`).join('')}</div>`;
    }
    if(r.url||r.href)body+=`<p><a href="${esc(r.url||r.href)}" target="_blank" rel="noopener">Open source</a></p>`;
    if(r.source)body+=`<p><a href="./${esc(r.source)}" target="_blank" rel="noopener">Open source file: ${esc(r.source)}</a></p>`;
    target.innerHTML=body;
  }
  function showError(message){const target=$('#frame-content');if(target)target.innerHTML=`<h1>THE POTATO OF LIFE</h1><p>${esc(message)}</p><p>The directory remains available; this is a data connection problem, not a failure of the reading frame.</p>`;}
  function select(r,path){state.selected=r.canonical_id||r.id;hash(state.selected);loadIntoFrame(r);save();}
  function recordRow(r,path){const x=document.createElement('div');x.className='tree-entry record-entry';x.innerHTML=`<button class="tree-button" type="button">${esc(r.name||r.id)}</button>`;$('.tree-button',x).onclick=()=>select(r,path);return x;}
  function renderCollection(details,c,branch){
    const key=`collection:${branch}:${c.id}`;if(state.rendered.has(key))return;state.rendered.add(key);
    const box=$('.tree-children',details),rows=unique(state.records.filter(r=>matches(r,c)));box.innerHTML='';
    const groups=new Map();rows.forEach(r=>{const g=(r.navigation_path||[branch,c.id,'RECORDS']).slice(-1)[0]||'RECORDS';if(!groups.has(g))groups.set(g,[]);groups.get(g).push(r);});
    if(rows.length>120){for(const [g,rs] of [...groups.entries()].sort()){const sub=document.createElement('details');sub.className='tree-subdir';sub.innerHTML=`<summary><span class="tree-name">${esc(g)}/</span></summary><div class="tree-children"></div>`;rs.forEach(r=>$('.tree-children',sub).appendChild(recordRow(r,`${branch}/${c.id}/${g}`)));box.appendChild(sub);}}
    else rows.forEach(r=>box.appendChild(recordRow(r,`${branch}/${c.id}`)));
    if(!box.children.length)box.innerHTML='<div class="tree-empty">empty</div>';
  }
  function collection(c,branch){
    const d=document.createElement('details');d.className='tree-dir tree-collection';const key=`collection:${branch}:${c.id}`;d.innerHTML=`<summary><span class="tree-name">${esc(c.label)}</span></summary><div class="tree-children"></div>`;
    d.addEventListener('toggle',()=>{if(d.open){state.expanded.add(key);renderCollection(d,c,branch);}else state.expanded.delete(key);save();});if(state.expanded.has(key)){d.open=true;renderCollection(d,c,branch);}return d;
  }
  function centerRecords(){
    const c=state.manifest?.center?.records||[];if(!c.length)return null;
    const d=document.createElement('details');d.className='tree-dir tree-center';d.innerHTML=`<summary><span class="tree-name">POTATO OF LIFE/</span></summary><div class="tree-children"></div>`;const box=$('.tree-children',d);
    c.forEach(item=>{const r=state.records.find(x=>(x.canonical_id||x.id)===item.id||x.id===item.id);if(r)box.appendChild(recordRow(r,'CENTER'));else{const x=document.createElement('div');x.className='tree-entry';x.innerHTML=`<button class="tree-button" type="button">${esc(item.label||item.id)}</button>`;$('.tree-button',x).onclick=()=>showError(`The center node ${item.id} is declared in the navigation manifest but is not present in the record index yet.`);box.appendChild(x);}});return d;
  }
  function branch(b,cs){
    const d=document.createElement('details');d.className=`tree-dir tree-branch branch-${b.kind}`;const key=`branch:${b.id}`;d.innerHTML=`<summary><span class="tree-name">${esc(b.label)}</span></summary><div class="tree-children branch-children"></div>`;
    cs.forEach(c=>$('.branch-children',d).appendChild(collection(c,b.id)));d.addEventListener('toggle',()=>{if(d.open)state.expanded.add(key);else state.expanded.delete(key);save();});if(state.expanded.has(key))d.open=true;return d;
  }
  function tree(){const t=$('#root-tree');if(!t)return;t.innerHTML='';const center=centerRecords();if(center)t.appendChild(center);const world=state.manifest.branches.find(b=>b.id==='world'),axis=state.manifest.branches.find(b=>b.id==='axis');if(axis)t.appendChild(branch(axis,state.manifest.axis.collections));if(world)t.appendChild(branch(world,state.manifest.world.collections));}
  function collapse(){document.querySelectorAll('#root-tree details[open]').forEach(d=>d.open=false);state.expanded.clear();state.rendered.clear();save();}
  function roots(){document.querySelectorAll('#root-tree>details').forEach(d=>d.open=true);}
  function toggleFrame(){const frame=$('#center-frame'),button=$('#frame-toggle');if(!frame||!button)return;const hidden=frame.classList.toggle('is-hidden');button.textContent=hidden?'show':'hide';button.setAttribute('aria-expanded',String(!hidden));}
  async function init(){
    load();const button=$('#frame-toggle');if(button)button.onclick=toggleFrame;
    try{const [m,i]=await Promise.all([fetch(MANIFEST_URL,{cache:'no-store'}),fetch(DATA_URL,{cache:'no-store'})]);if(!m.ok)throw Error(`navigation manifest HTTP ${m.status}`);state.manifest=await m.json();if(i.ok){const j=await i.json();state.records=Array.isArray(j.records)?j.records:[];}else showError(`record index HTTP ${i.status}`);tree();const wanted=hashId()||state.selected;if(wanted){const r=state.records.find(x=>(x.canonical_id||x.id)===wanted||x.id===wanted);if(r)loadIntoFrame(r);}}
    catch(e){const t=$('#root-tree');if(t)t.innerHTML='<div class="tree-empty">navigation unavailable</div>';showError(`Navigation could not start: ${e.message||e}`);}
  }
  document.addEventListener('click',e=>{const a=e.target.closest('[data-action]')?.dataset.action;if(a==='collapse-all')collapse();if(a==='expand-roots')roots();});
  addEventListener('hashchange',()=>{const id=hashId();if(!id)return;const r=state.records.find(x=>(x.canonical_id||x.id)===id||x.id===id);if(r)loadIntoFrame(r);});init();
})();
