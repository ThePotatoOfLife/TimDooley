(() => {
  'use strict';
  const DATA_URL='./data/root-record-index.json', MANIFEST_URL='./data/root-navigation.json', STORAGE_KEY='potato-root-state-v7';
  const $=(s,r=document)=>r.querySelector(s);
  const esc=v=>String(v??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const state={manifest:null,records:[],selected:null,expanded:new Set(),rendered:new Set()};
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
    target.innerHTML='';
    if(!html)return false;
    try{
      const parsed=new DOMParser().parseFromString(String(html),'text/html');
      const source=parsed.body&&parsed.body.children.length?parsed.body:parsed.documentElement;
      [...source.childNodes].forEach(n=>target.appendChild(document.importNode(n,true)));
      return true;
    }catch(_){target.textContent=String(html);return true;}
  }
  function loadIntoFrame(r){
    const target=$('#frame-content');if(!target)return;
    target.classList.remove('is-loading');
    const html=r.html||r.content_html||r.document_html;
    if(html&&renderHtml(html,target))return;
    target.innerHTML=`<h1>${esc(r.name||r.id||'Record')}</h1><p>${esc(r.description||'No description is currently registered for this record.')}</p>`;
    if(r.url||r.href){const p=document.createElement('p');const a=document.createElement('a');a.href=r.url||r.href;a.target='_blank';a.rel='noopener';a.textContent='Open source';p.appendChild(a);target.appendChild(p);}
  }
  function showError(message){
    const target=$('#frame-content');
    if(target)target.innerHTML=`<h1>THE POTATO OF LIFE</h1><p>${esc(message)}</p><p>The reading frame is still available. The navigation data can be repaired without changing the shell.</p>`;
  }
  function select(r,path){state.selected=r.canonical_id||r.id;hash(state.selected);loadIntoFrame(r);save();}
  function recordRow(r,path){
    const x=document.createElement('div');x.className='tree-entry record-entry';
    x.innerHTML=`<button class="tree-button" type="button">${esc(r.name||r.id)}</button>`;
    $('.tree-button',x).onclick=()=>select(r,path);return x;
  }
  function renderCollection(details,c,branch){
    const key=`collection:${branch}:${c.id}`;if(state.rendered.has(key))return;state.rendered.add(key);
    const box=$('.tree-children',details),rows=unique(state.records.filter(r=>matches(r,c)));box.innerHTML='';
    const groups=new Map();rows.forEach(r=>{const g=(r.navigation_path||[branch,c.id,'RECORDS']).slice(-1)[0]||'RECORDS';if(!groups.has(g))groups.set(g,[]);groups.get(g).push(r);});
    if(rows.length>120){for(const [g,rs] of [...groups.entries()].sort()){const sub=document.createElement('details');sub.className='tree-subdir';sub.innerHTML=`<summary><span class="tree-name">${esc(g)}/</span></summary><div class="tree-children"></div>`;rs.forEach(r=>$('.tree-children',sub).appendChild(recordRow(r,`${branch}/${c.id}/${g}`)));box.appendChild(sub);}}
    else rows.forEach(r=>box.appendChild(recordRow(r,`${branch}/${c.id}`)));
    if(!box.children.length)box.innerHTML='<div class="tree-empty">empty</div>';
  }
  function collection(c,branch){
    const d=document.createElement('details');d.className='tree-dir tree-collection';const key=`collection:${branch}:${c.id}`;
    d.innerHTML=`<summary><span class="tree-name">${esc(c.label)}</span></summary><div class="tree-children"></div>`;
    d.addEventListener('toggle',()=>{if(d.open){state.expanded.add(key);renderCollection(d,c,branch);}else state.expanded.delete(key);save();});
    if(state.expanded.has(key)){d.open=true;renderCollection(d,c,branch);}return d;
  }
  function branch(b,cs){
    const d=document.createElement('details');d.className=`tree-dir tree-branch branch-${b.kind}`;const key=`branch:${b.id}`;
    d.innerHTML=`<summary><span class="tree-name">${esc(b.label)}</span></summary><div class="tree-children branch-children"></div>`;
    cs.forEach(c=>$('.branch-children',d).appendChild(collection(c,b.id)));
    d.addEventListener('toggle',()=>{if(d.open)state.expanded.add(key);else state.expanded.delete(key);save();});
    if(state.expanded.has(key))d.open=true;return d;
  }
  function tree(){
    const t=$('#root-tree');if(!t)return;t.innerHTML='';
    const world=state.manifest.branches.find(b=>b.id==='world'),axis=state.manifest.branches.find(b=>b.id==='axis');
    if(axis)t.appendChild(branch(axis,state.manifest.axis.collections));if(world)t.appendChild(branch(world,state.manifest.world.collections));
  }
  function collapse(){document.querySelectorAll('#root-tree details[open]').forEach(d=>d.open=false);state.expanded.clear();state.rendered.clear();save();}
  function roots(){document.querySelectorAll('#root-tree>details').forEach(d=>d.open=true);}
  function toggleFrame(){const frame=$('#center-frame'),button=$('#frame-toggle');if(!frame||!button)return;const hidden=frame.classList.toggle('is-hidden');button.textContent=hidden?'show':'hide';button.setAttribute('aria-expanded',String(!hidden));}
  async function init(){
    load();const button=$('#frame-toggle');if(button)button.onclick=toggleFrame;
    try{
      const [m,i]=await Promise.all([fetch(MANIFEST_URL,{cache:'no-store'}),fetch(DATA_URL,{cache:'no-store'})]);
      if(!m.ok)throw Error(`navigation manifest HTTP ${m.status}`);
      state.manifest=await m.json();
      if(i.ok){const j=await i.json();state.records=Array.isArray(j.records)?j.records:[];}
      else showError(`record index HTTP ${i.status}`);
      tree();
      const wanted=hashId()||state.selected;
      if(wanted){const r=state.records.find(x=>(x.canonical_id||x.id)===wanted||x.id===wanted);if(r)loadIntoFrame(r);}
    }catch(e){
      const t=$('#root-tree');
      if(t)t.innerHTML='<div class="tree-empty">navigation unavailable</div>';
      showError(`Navigation could not start: ${e.message||e}`);
    }
  }
  document.addEventListener('click',e=>{const a=e.target.closest('[data-action]')?.dataset.action;if(a==='collapse-all')collapse();if(a==='expand-roots')roots();});
  addEventListener('hashchange',()=>{const id=hashId();if(!id)return;const r=state.records.find(x=>(x.canonical_id||x.id)===id||x.id===id);if(r)loadIntoFrame(r);});
  init();
})();
