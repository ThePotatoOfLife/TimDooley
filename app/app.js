const $=s=>document.querySelector(s);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

let manifest=null;
let contextGraph={clusters:[]};
let canonicalRecordRegistry={records:[]};
let active='root';
let viewType='root';
let searching=false;
const cache=new Map();
let branchMap=new Map();
let relationsByBranch=new Map();
let contextsByBranch=new Map();
let branchesByRecord=new Map();
let contextsByRecord=new Map();
let searchIndex=new Map();
let recordPaths=new Set();
let searchFrame=0;
let recordRequestToken=0;

const RENDER_LIMITS=Object.freeze({maxDepth:18,maxNodes:1200,maxItems:160,maxStringChars:12000});

async function loadResource(path){
  if(cache.has(path))return cache.get(path);
  const r=await fetch(path);
  if(!r.ok)throw new Error(`${r.status} ${path}`);
  const type=/\.json(?:$|\?)/i.test(path)?'json':'text';
  const data=type==='json'?await r.json():await r.text();
  const result={type,data};
  cache.set(path,result);
  return result;
}
async function loadJSON(path){
  const r=await loadResource(path);
  if(r.type!=='json')throw new Error(`Expected JSON: ${path}`);
  return r.data;
}
function human(k){return String(k).replace(/[_-]+/g,' ').replace(/\b\w/g,c=>c.toUpperCase())}
function renderLimitNotice(message){return `<div class="value render-limit">${esc(message)}</div>`}
function renderValue(v,depth=0,state={nodes:0}){
  if(depth>RENDER_LIMITS.maxDepth)return renderLimitNotice('[maximum display depth reached]');
  if(state.nodes>=RENDER_LIMITS.maxNodes)return renderLimitNotice('[record display budget reached]');
  state.nodes+=1;
  if(v===null||v===undefined)return'<div class="value">—</div>';
  if(typeof v==='string'){
    if(v.length<=RENDER_LIMITS.maxStringChars)return`<div class="value">${esc(v)}</div>`;
    const omitted=v.length-RENDER_LIMITS.maxStringChars;
    return `<div class="value">${esc(v.slice(0,RENDER_LIMITS.maxStringChars))}</div>${renderLimitNotice(`[${omitted} additional characters not rendered]`)}`;
  }
  if(typeof v==='number'||typeof v==='boolean')return`<div class="value">${esc(v)}</div>`;
  if(Array.isArray(v)){
    const cap=Math.min(v.length,RENDER_LIMITS.maxItems);
    if(v.every(x=>['string','number','boolean'].includes(typeof x))){
      const budget=Math.max(0,RENDER_LIMITS.maxNodes-state.nodes);
      const count=Math.min(cap,budget);
      const chips=v.slice(0,count).map(x=>`<span class="chip">${esc(typeof x==='string'&&x.length>RENDER_LIMITS.maxStringChars?`${x.slice(0,RENDER_LIMITS.maxStringChars)}…`:x)}</span>`).join('');
      state.nodes+=count;
      const omitted=v.length-count;
      return `<div class="chips">${chips}</div>${omitted?renderLimitNotice(`[${omitted} array items not rendered]`):''}`;
    }
    const parts=[];
    let rendered=0;
    for(;rendered<cap&&state.nodes<RENDER_LIMITS.maxNodes;rendered++)parts.push(`<div class="nested">${renderValue(v[rendered],depth+1,state)}</div>`);
    const omitted=v.length-rendered;
    return parts.join('')+(omitted?renderLimitNotice(`[${omitted} array items not rendered]`):'');
  }
  if(typeof v==='object'){
    const entries=Object.entries(v);const cap=Math.min(entries.length,RENDER_LIMITS.maxItems);const parts=[];
    let rendered=0;
    for(;rendered<cap&&state.nodes<RENDER_LIMITS.maxNodes;rendered++){
      const [k,val]=entries[rendered];
      parts.push(`<div class="kv"><div class="key">${esc(human(k))}</div>${renderValue(val,depth+1,state)}</div>`);
    }
    const omitted=entries.length-rendered;
    return parts.join('')+(omitted?renderLimitNotice(`[${omitted} object fields not rendered]`):'');
  }
  return`<div class="value">${esc(String(v))}</div>`;
}
function renderInline(s){return esc(s).replace(/`([^`]+)`/g,'<code>$1</code>').replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>').replace(/\*([^*]+)\*/g,'<em>$1</em>')}
function renderMarkdown(text){
  const lines=String(text).replace(/\r\n?/g,'\n').split('\n');
  const out=[];
  let list=null,inCode=false,code=[];
  const closeList=()=>{if(list){out.push(`</${list}>`);list=null}};
  const closeCode=()=>{if(inCode){out.push(`<pre><code>${esc(code.join('\n'))}</code></pre>`);inCode=false;code=[]}};
  for(const raw of lines){
    const line=raw.trimEnd();
    if(line.trim().startsWith('```')){closeList();if(inCode)closeCode();else inCode=true;continue}
    if(inCode){code.push(raw);continue}
    let m=line.match(/^(#{1,6})\s+(.+)$/);
    if(m){closeList();out.push(`<h${m[1].length}>${renderInline(m[2])}</h${m[1].length}>`);continue}
    m=line.match(/^\s*[-*+]\s+(.+)$/);
    if(m){if(list!=='ul'){closeList();list='ul';out.push('<ul>')}out.push(`<li>${renderInline(m[1])}</li>`);continue}
    m=line.match(/^\s*\d+[.)]\s+(.+)$/);
    if(m){if(list!=='ol'){closeList();list='ol';out.push('<ol>')}out.push(`<li>${renderInline(m[1])}</li>`);continue}
    m=line.match(/^>\s?(.*)$/);
    if(m){closeList();out.push(`<blockquote>${renderInline(m[1])}</blockquote>`);continue}
    if(/^[-*_]{3,}\s*$/.test(line)){closeList();out.push('<hr>');continue}
    if(!line.trim()){closeList();continue}
    closeList();out.push(`<p>${renderInline(line.trim())}</p>`);
  }
  closeList();closeCode();
  return `<div class="markdown">${out.join('')}</div>`;
}

function indexPush(map,key,value){
  if(!map.has(key))map.set(key,[]);
  map.get(key).push(value);
}
function isRegistrySourcePath(path){
  return typeof path==='string'&&/^data\/[A-Za-z0-9._/-]+\.json$/i.test(path)&&!path.includes('..')&&!path.startsWith('/');
}
function buildIndexes(){
  branchMap=new Map((manifest.branches||[]).map(b=>[b.id,b]));
  relationsByBranch=new Map();
  contextsByBranch=new Map();
  branchesByRecord=new Map();
  contextsByRecord=new Map();
  searchIndex=new Map();
  recordPaths=new Set();
  if(manifest.root?.record)recordPaths.add(manifest.root.record);
  for(const r of manifest.relations||[]){
    indexPush(relationsByBranch,r.from,r);
    if(r.to!==r.from)indexPush(relationsByBranch,r.to,r);
  }
  for(const c of contextGraph.clusters||[]){
    for(const id of c.branches||[])indexPush(contextsByBranch,id,c);
    for(const path of c.records||[]){indexPush(contextsByRecord,path,c);recordPaths.add(path)}
  }
  for(const b of manifest.branches||[]){
    for(const path of b.records||[]){indexPush(branchesByRecord,path,b);recordPaths.add(path)}
    const rels=(relationsByBranch.get(b.id)||[]).map(r=>r.label).join(' ');
    const ctx=(contextsByBranch.get(b.id)||[]).flatMap(c=>[c.title,c.summary,...(c.concepts||[])]).join(' ');
    searchIndex.set(b.id,[b.title,b.description,...(b.children||[]),...(b.records||[]),rels,ctx].join(' ').toLowerCase());
  }
  for(const record of canonicalRecordRegistry.records||[]){
    for(const occurrence of record.occurrences||[]){
      if(isRegistrySourcePath(occurrence.source))recordPaths.add(occurrence.source);
    }
  }
}
function branchById(id){return branchMap.get(id)}
function relatedTo(id){return relationsByBranch.get(id)||[]}
function contextForBranch(id){return contextsByBranch.get(id)||[]}
function relationCard(r,id){
  const other=r.from===id?r.to:r.from;
  const b=branchById(other);
  if(!b)return'';
  return `<button class="relation" data-branch="${esc(other)}"><span class="reltype">${esc(r.type)}</span><strong>${esc(b.title)}</strong><span>${esc(r.label)}</span></button>`;
}
function pathwayCard(p){return `<button class="pathway" data-pathway="${esc(p.id)}"><span class="pathlabel">PATHWAY</span><strong>${esc(p.title)}</strong><span>${esc(p.summary)}</span><div class="trail">${(p.branches||[]).map(id=>`<b>${esc(branchById(id)?.title||id)}</b>`).join('<i>→</i>')}</div></button>`}
function contextCard(c){return `<button class="contextcard" data-context="${esc(c.id)}"><span class="contextlabel">CONTEXT CLUSTER</span><strong>${esc(c.title)}</strong><span>${esc(c.summary)}</span><div class="chips compact">${(c.concepts||[]).slice(0,5).map(x=>`<span class="chip">${esc(x)}</span>`).join('')}</div></button>`}
function setHash(hash){if(location.hash!==hash)history.replaceState(null,'',hash)}
function emitNavigation(type,id=null){window.dispatchEvent(new CustomEvent('potato:navigation',{detail:{type,id}}))}
function updateActiveNav(id){document.querySelectorAll('.branchbtn').forEach(btn=>btn.classList.toggle('active',btn.dataset.id===id))}
function safeDecodeHashValue(value){try{return decodeURIComponent(value)}catch{return null}}
function cancelRecordLoad(){recordRequestToken+=1}
function isCurrentRecordLoad(token,target){return token===recordRequestToken&&target.isConnected&&target===$('#record-detail')}
function isKnownRecord(path){return typeof path==='string'&&recordPaths.has(path)}

async function showRecord(path){
  if(!isKnownRecord(path)){selectBranch('root',{force:true});return false}
  const target=$('#record-detail');if(!target)return false;
  const token=++recordRequestToken;
  target.innerHTML=`<div class="status">Loading ${esc(path)}…</div>`;
  try{
    const resource=await loadResource(path);
    if(!isCurrentRecordLoad(token,target))return false;
    const branches=branchesByRecord.get(path)||[];
    const clusters=contextsByRecord.get(path)||[];
    const isJSON=resource.type==='json',data=resource.data;
    const title=isJSON?(data.title||data.name||data.id||path):(String(data).match(/^#\s+(.+)$/m)?.[1]||path.split('/').pop().replace(/\.md$/i,''));
    const body=isJSON?renderValue(data):renderMarkdown(data);
    if(!isCurrentRecordLoad(token,target))return false;
    target.innerHTML=`<article class="record"><div class="recordhead"><div><span class="recordtype">${isJSON?'CANONICAL RECORD':'ARCHIVE DOCUMENT'}</span><h3>${esc(title)}</h3></div><code>${esc(path)}</code></div>${branches.length?`<div class="recordcontext"><span>Appears in</span>${branches.map(b=>`<button data-branch="${esc(b.id)}">${esc(b.title)}</button>`).join('')}</div>`:''}${clusters.length?`<div class="section mini"><h3>Context clusters</h3><div class="contexts">${clusters.map(contextCard).join('')}</div></div>`:''}${body}</article>`;
    viewType='record';setHash(`#record=${encodeURIComponent(path)}`);emitNavigation('record',path);return true;
  }catch(e){
    if(!isCurrentRecordLoad(token,target))return false;
    target.innerHTML=`<div class="record"><div class="status">Could not load ${esc(path)}: ${esc(e.message)}</div></div>`;return false;
  }
}

function branchHTML(b){
  const children=(b.children||[]).map(x=>`<span class="chip">${esc(x)}</span>`).join('');
  const records=(b.records||[]).map(p=>`<button class="record-link" data-record="${esc(p)}"><span class="recordtype">OPEN ${/\.md$/i.test(p)?'DOCUMENT':'RECORD'}</span><strong>${esc(p.split('/').pop().replace(/\.(json|md)$/,''))}</strong><code>${esc(p)}</code></button>`).join('');
  const dirs=[...(b.directories||[]),...(b.directory?[b.directory]:[])];
  const related=relatedTo(b.id).map(r=>relationCard(r,b.id)).join('');
  const contexts=contextForBranch(b.id).map(contextCard).join('');
  return `<div class="branchhero" data-branch-view="${esc(b.id)}"><span class="branchmark">${esc(b.title.slice(0,1))}</span><div><div class="eyebrow">Connected branch</div><h2>${esc(b.title)}</h2><p class="summary">${esc(b.description||'')}</p></div></div>${contexts?`<div class="section"><h3>Contextual constellations</h3><div class="contexts">${contexts}</div></div>`:''}${children?`<div class="section"><h3>Canonical substructure</h3><div class="chips">${children}</div></div>`:''}${related?`<div class="section"><h3>Relationships</h3><div class="relations">${related}</div></div>`:''}${records?`<div class="section"><h3>Canonical records</h3>${records}</div>`:''}${dirs.length?`<div class="section"><h3>Mapped directories</h3>${dirs.map(d=>`<div class="directory"><code>${esc(d)}</code></div>`).join('')}</div>`:''}<div id="record-detail"></div>`;
}
function rootHTML(){
  const paths=(manifest.pathways||[]).map(pathwayCard).join('');const contexts=(contextGraph.clusters||[]).map(contextCard).join('');const relationCount=(manifest.relations||[]).length;
  return `<div class="rootintro"><div><div class="eyebrow">Relationship-first knowledge system</div><h2>${esc(manifest.root.title)}</h2><p class="summary">${esc(manifest.root.summary)}</p></div><div class="rootstats"><div><strong>${manifest.branches.length}</strong><span>branches</span></div><div><strong>${relationCount}</strong><span>explicit relations</span></div><div><strong>${(contextGraph.clusters||[]).length}</strong><span>context clusters</span></div></div></div>${contexts?`<div class="section"><h3>Contextual constellations</h3><p class="sectionnote">These clusters combine records because their structures illuminate one another while preserving evidence class.</p><div class="contexts">${contexts}</div></div>`:''}${paths?`<div class="section"><h3>Ways through the archive</h3><div class="pathways">${paths}</div></div>`:''}<div class="section"><h3>Branch field</h3><div class="branchfield">${manifest.branches.map(b=>`<button class="branchnode" data-branch="${esc(b.id)}"><span>${esc(b.title)}</span><small>${esc((b.children||[]).slice(0,4).join(' · ')||b.description)}</small></button>`).join('')}</div></div><div class="section"><h3>Architecture rules</h3><div class="chips">${manifest.principles.map(p=>`<span class="chip">${esc(p)}</span>`).join('')}</div></div><div class="section"><h3>Root record</h3><button class="record-link" data-record="${esc(manifest.root.record)}"><span class="recordtype">OPEN ROOT</span><strong>Potato of Life</strong><code>${esc(manifest.root.record)}</code></button></div><div id="record-detail"></div>`;
}
function showContext(id){
  const c=(contextGraph.clusters||[]).find(x=>x.id===id);if(!c){selectBranch('root',{force:true});return false}cancelRecordLoad();searching=false;
  const branchButtons=(c.branches||[]).map(branchId=>{const b=branchById(branchId);return b?`<button class="branchnode" data-branch="${esc(branchId)}"><span>${esc(b.title)}</span><small>${esc(b.description)}</small></button>`:''}).join('');
  const records=(c.records||[]).map(p=>`<button class="record-link" data-record="${esc(p)}"><span class="recordtype">OPEN CONTEXT RECORD</span><strong>${esc(p.split('/').pop().replace(/\.(json|md)$/,''))}</strong><code>${esc(p)}</code></button>`).join('');
  $('#reader').innerHTML=`<div class="eyebrow">Context cluster</div><h2>${esc(c.title)}</h2><p class="summary">${esc(c.summary)}</p><div class="section"><h3>Concepts in this constellation</h3><div class="chips">${(c.concepts||[]).map(x=>`<span class="chip">${esc(x)}</span>`).join('')}</div></div><div class="section"><h3>Epistemic layers</h3><div class="chips">${(c.epistemic_mix||[]).map(x=>`<span class="chip epistemic">${esc(human(x))}</span>`).join('')}</div></div><div class="section"><h3>Connected branches</h3><div class="branchfield">${branchButtons}</div></div><div class="section"><h3>Records that carry this context</h3>${records}</div><div id="record-detail"></div>`;
  viewType='context';setHash(`#context=${encodeURIComponent(id)}`);emitNavigation('context',id);return true;
}
function showPathway(id){
  const p=(manifest.pathways||[]).find(x=>x.id===id);if(!p){selectBranch('root',{force:true});return false}cancelRecordLoad();searching=false;
  const steps=(p.branches||[]).map((bid,i)=>{const b=branchById(bid);if(!b)return'';return `<button class="pathstep" data-branch="${esc(bid)}"><span>${String(i+1).padStart(2,'0')}</span><div><strong>${esc(b.title)}</strong><small>${esc(b.description)}</small></div></button>`}).join('');
  $('#reader').innerHTML=`<div class="eyebrow">Guided pathway</div><h2>${esc(p.title)}</h2><p class="summary">${esc(p.summary)}</p><div class="pathsteps">${steps}</div>`;
  viewType='path';setHash(`#path=${encodeURIComponent(id)}`);emitNavigation('path',id);return true;
}
function selectBranch(id,{force=false}={}){
  cancelRecordLoad();
  let b=id==='root'?null:branchById(id);if(id!=='root'&&!b){id='root';b=null}
  const sameBranch=id===active&&viewType==='branch';active=id;searching=false;updateActiveNav(id);
  if(!force&&sameBranch){setHash(id==='root'?'#root':`#branch=${encodeURIComponent(id)}`);return}
  $('#reader').innerHTML=id==='root'?rootHTML():branchHTML(b);
  viewType=id==='root'?'root':'branch';setHash(id==='root'?'#root':`#branch=${encodeURIComponent(id)}`);emitNavigation(viewType,id);
}
function buildNav(){const nav=$('#branches');nav.innerHTML=manifest.branches.map(b=>`<button class="branchbtn" data-id="${esc(b.id)}"><span class="title">${esc(b.title)}</span><span class="desc">${esc(b.description||'')}</span></button>`).join('')}
function applySearch(raw){
  const q=raw.trim().toLowerCase();
  for(const btn of document.querySelectorAll('.branchbtn'))btn.style.display=!q||(searchIndex.get(btn.dataset.id)||'').includes(q)?'block':'none';
  if(!q){if(searching)selectBranch(active||'root',{force:true});return}
  if(q.length<=2)return;
  cancelRecordLoad();
  const matches=(contextGraph.clusters||[]).filter(c=>[c.title,c.summary,...(c.concepts||[]),...(c.epistemic_mix||[])].join(' ').toLowerCase().includes(q));
  searching=true;viewType='search';
  $('#reader').innerHTML=matches.length?`<div class="eyebrow">Context search</div><h2>Context matches</h2><p class="summary">Search reaches concepts and contextual constellations, not only branch titles.</p><div class="contexts">${matches.map(contextCard).join('')}</div>`:`<div class="eyebrow">Context search</div><h2>No context matches</h2><p class="summary">Try a broader term or choose a branch from the left navigation.</p>`;
  emitNavigation('search',q);
}
function scheduleSearch(value){cancelAnimationFrame(searchFrame);searchFrame=requestAnimationFrame(()=>applySearch(value))}
function handleReaderClick(event){
  const reader=$('#reader');const trigger=event.target.closest('[data-record],[data-branch],[data-pathway],[data-context]');if(!trigger||!reader?.contains(trigger))return;
  if(trigger.dataset.record){showRecord(trigger.dataset.record);return}
  if(trigger.dataset.branch){selectBranch(trigger.dataset.branch);return}
  if(trigger.dataset.pathway){showPathway(trigger.dataset.pathway);return}
  if(trigger.dataset.context)showContext(trigger.dataset.context);
}
function handleNavClick(event){const button=event.target.closest('.branchbtn[data-id]');if(button&&$('#branches')?.contains(button))selectBranch(button.dataset.id)}
async function routeHash(){
  if(!manifest)return;
  const hash=location.hash||'#root';
  if(hash==='#root'){selectBranch('root',{force:true});return}
  if(hash.startsWith('#branch=')){
    const id=safeDecodeHashValue(hash.slice(8));
    if(id!==null&&branchById(id)){selectBranch(id,{force:true});return}
    selectBranch('root',{force:true});return;
  }
  if(hash.startsWith('#record=')){
    const path=safeDecodeHashValue(hash.slice(8));
    if(path===null||!isKnownRecord(path)){selectBranch('root',{force:true});return}
    selectBranch('root',{force:true});await showRecord(path);return;
  }
  if(hash.startsWith('#path=')){
    const id=safeDecodeHashValue(hash.slice(6));
    if(id!==null&&(manifest.pathways||[]).some(p=>p.id===id)){showPathway(id);return}
    selectBranch('root',{force:true});return;
  }
  if(hash.startsWith('#context=')){
    const id=safeDecodeHashValue(hash.slice(9));
    if(id!==null&&(contextGraph.clusters||[]).some(c=>c.id===id)){showContext(id);return}
    selectBranch('root',{force:true});return;
  }
  selectBranch('root',{force:true});
}
async function init(){
  try{
    [manifest,contextGraph,canonicalRecordRegistry]=await Promise.all([
      loadJSON('manifest.json'),
      loadJSON('knowledge/indexes/context-graph.json').catch(()=>({clusters:[]})),
      loadJSON('data/canonical-record-registry.json').catch(()=>({records:[]}))
    ]);
    buildIndexes();buildNav();
    $('#reader')?.addEventListener('click',handleReaderClick);
    $('#branches')?.addEventListener('click',handleNavClick);
    $('#rootbtn')?.addEventListener('click',()=>selectBranch('root'));
    $('#q')?.addEventListener('input',e=>scheduleSearch(e.target.value));
    window.addEventListener('hashchange',routeHash);
    await routeHash();
  }catch(e){const reader=$('#reader');if(reader)reader.innerHTML=`<div class="status">Archive failed to load: ${esc(e.message)}</div>`}
}
init();