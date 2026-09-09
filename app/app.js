const $=s=>document.querySelector(s);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let manifest=null,contextGraph={clusters:[]},active='root',cache=new Map(),searching=false;

async function loadResource(path){
  if(cache.has(path))return cache.get(path);
  const r=await fetch(path);
  if(!r.ok)throw new Error(`${r.status} ${path}`);
  const type=/\.json(?:$|\?)/i.test(path)?'json':'text';
  const data=type==='json'?await r.json():await r.text();
  const result={type,data};cache.set(path,result);return result;
}
async function loadJSON(path){const r=await loadResource(path);if(r.type!=='json')throw new Error(`Expected JSON: ${path}`);return r.data}
function human(k){return String(k).replace(/[_-]+/g,' ').replace(/\b\w/g,c=>c.toUpperCase())}
function renderValue(v,depth=0){if(v===null||v===undefined)return'<div class="value">—</div>';if(typeof v==='string'||typeof v==='number'||typeof v==='boolean')return`<div class="value">${esc(v)}</div>`;if(Array.isArray(v)){if(v.every(x=>['string','number','boolean'].includes(typeof x)))return `<div class="chips">${v.map(x=>`<span class="chip">${esc(x)}</span>`).join('')}</div>`;return v.map(x=>`<div class="nested">${renderValue(x,depth+1)}</div>`).join('')}return Object.entries(v).map(([k,val])=>`<div class="kv"><div class="key">${esc(human(k))}</div>${renderValue(val,depth+1)}</div>`).join('')}
function renderInline(s){return esc(s).replace(/`([^`]+)`/g,'<code>$1</code>').replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>').replace(/\*([^*]+)\*/g,'<em>$1</em>')}
function renderMarkdown(text){
  const lines=String(text).replace(/\r\n?/g,'\n').split('\n');let out=[],list=null,inCode=false,code=[];
  const closeList=()=>{if(list){out.push(`</${list}>`);list=null}};
  const closeCode=()=>{if(inCode){out.push(`<pre><code>${esc(code.join('\n'))}</code></pre>`);inCode=false;code=[]}};
  for(const raw of lines){
    const line=raw.trimEnd();
    if(line.trim().startsWith('```')){closeList();if(inCode)closeCode();else inCode=true;continue}
    if(inCode){code.push(raw);continue}
    let m=line.match(/^(#{1,6})\s+(.+)$/);if(m){closeList();out.push(`<h${m[1].length}>${renderInline(m[2])}</h${m[1].length}>`);continue}
    m=line.match(/^\s*[-*+]\s+(.+)$/);if(m){if(list!=='ul'){closeList();list='ul';out.push('<ul>')}out.push(`<li>${renderInline(m[1])}</li>`);continue}
    m=line.match(/^\s*\d+[.)]\s+(.+)$/);if(m){if(list!=='ol'){closeList();list='ol';out.push('<ol>')}out.push(`<li>${renderInline(m[1])}</li>`);continue}
    m=line.match(/^>\s?(.*)$/);if(m){closeList();out.push(`<blockquote>${renderInline(m[1])}</blockquote>`);continue}
    if(/^[-*_]{3,}\s*$/.test(line)){closeList();out.push('<hr>');continue}
    if(!line.trim()){closeList();continue}
    closeList();out.push(`<p>${renderInline(line.trim())}</p>`);
  }
  closeList();closeCode();return `<div class="markdown">${out.join('')}</div>`;
}
function branchById(id){return manifest.branches.find(b=>b.id===id)}
function relatedTo(id){return (manifest.relations||[]).filter(r=>r.from===id||r.to===id)}
function contextForBranch(id){return (contextGraph.clusters||[]).filter(c=>(c.branches||[]).includes(id))}
function relationCard(r,id){const other=r.from===id?r.to:r.from;const b=branchById(other);if(!b)return'';return `<button class="relation" data-branch="${esc(other)}"><span class="reltype">${esc(r.type)}</span><strong>${esc(b.title)}</strong><span>${esc(r.label)}</span></button>`}
function pathwayCard(p){return `<button class="pathway" data-pathway="${esc(p.id)}"><span class="pathlabel">PATHWAY</span><strong>${esc(p.title)}</strong><span>${esc(p.summary)}</span><div class="trail">${p.branches.map(id=>`<b>${esc(branchById(id)?.title||id)}</b>`).join('<i>→</i>')}</div></button>`}
function contextCard(c){return `<button class="contextcard" data-context="${esc(c.id)}"><span class="contextlabel">CONTEXT CLUSTER</span><strong>${esc(c.title)}</strong><span>${esc(c.summary)}</span><div class="chips compact">${(c.concepts||[]).slice(0,5).map(x=>`<span class="chip">${esc(x)}</span>`).join('')}</div></button>`}

async function showRecord(path){
  const target=$('#record-detail');if(!target)return;
  target.innerHTML=`<div class="status">Loading ${esc(path)}…</div>`;
  try{
    const resource=await loadResource(path);const branches=manifest.branches.filter(b=>(b.records||[]).includes(path));const clusters=(contextGraph.clusters||[]).filter(c=>(c.records||[]).includes(path));
    const isJSON=resource.type==='json',data=resource.data;
    const title=isJSON?(data.title||data.name||data.id||path):(String(data).match(/^#\s+(.+)$/m)?.[1]||path.split('/').pop().replace(/\.md$/i,''));
    const body=isJSON?renderValue(data):renderMarkdown(data);
    target.innerHTML=`<article class="record"><div class="recordhead"><div><span class="recordtype">${isJSON?'CANONICAL RECORD':'ARCHIVE DOCUMENT'}</span><h3>${esc(title)}</h3></div><code>${esc(path)}</code></div>${branches.length?`<div class="recordcontext"><span>Appears in</span>${branches.map(b=>`<button data-branch="${esc(b.id)}">${esc(b.title)}</button>`).join('')}</div>`:''}${clusters.length?`<div class="section mini"><h3>Context clusters</h3><div class="contexts">${clusters.map(contextCard).join('')}</div></div>`:''}${body}</article>`;
    bindDynamic();history.replaceState(null,'',`#record=${encodeURIComponent(path)}`)
  }catch(e){target.innerHTML=`<div class="record"><div class="status">Could not load ${esc(path)}: ${esc(e.message)}</div></div>`}
}

function branchHTML(b){const children=(b.children||[]).map(x=>`<span class="chip">${esc(x)}</span>`).join('');const records=(b.records||[]).map(p=>`<button class="record-link" data-record="${esc(p)}"><span class="recordtype">OPEN ${/\.md$/i.test(p)?'DOCUMENT':'RECORD'}</span><strong>${esc(p.split('/').pop().replace(/\.(json|md)$/,''))}</strong><code>${esc(p)}</code></button>`).join('');const dirs=[...(b.directories||[]),...(b.directory?[b.directory]:[])];const related=relatedTo(b.id).map(r=>relationCard(r,b.id)).join('');const contexts=contextForBranch(b.id).map(contextCard).join('');return `<div class="branchhero"><span class="branchmark">${esc(b.title.slice(0,1))}</span><div><div class="eyebrow">Connected branch</div><h2>${esc(b.title)}</h2><p class="summary">${esc(b.description||'')}</p></div></div>${contexts?`<div class="section"><h3>Contextual constellations</h3><div class="contexts">${contexts}</div></div>`:''}${children?`<div class="section"><h3>Canonical substructure</h3><div class="chips">${children}</div></div>`:''}${related?`<div class="section"><h3>Relationships</h3><div class="relations">${related}</div></div>`:''}${records?`<div class="section"><h3>Canonical records</h3>${records}</div>`:''}${dirs.length?`<div class="section"><h3>Mapped directories</h3>${dirs.map(d=>`<div class="directory"><code>${esc(d)}</code></div>`).join('')}</div>`:''}<div id="record-detail"></div>`}
function rootHTML(){const paths=(manifest.pathways||[]).map(pathwayCard).join('');const contexts=(contextGraph.clusters||[]).map(contextCard).join('');const relationCount=(manifest.relations||[]).length;return `<div class="rootintro"><div><div class="eyebrow">Relationship-first knowledge system</div><h2>${esc(manifest.root.title)}</h2><p class="summary">${esc(manifest.root.summary)}</p></div><div class="rootstats"><div><strong>${manifest.branches.length}</strong><span>branches</span></div><div><strong>${relationCount}</strong><span>explicit relations</span></div><div><strong>${(contextGraph.clusters||[]).length}</strong><span>context clusters</span></div></div></div>${contexts?`<div class="section"><h3>Contextual constellations</h3><p class="sectionnote">These clusters combine records because their structures illuminate one another while preserving evidence class.</p><div class="contexts">${contexts}</div></div>`:''}${paths?`<div class="section"><h3>Ways through the archive</h3><div class="pathways">${paths}</div></div>`:''}<div class="section"><h3>Branch field</h3><div class="branchfield">${manifest.branches.map(b=>`<button class="branchnode" data-branch="${esc(b.id)}"><span>${esc(b.title)}</span><small>${esc((b.children||[]).slice(0,4).join(' · ')||b.description)}</small></button>`).join('')}</div></div><div class="section"><h3>Architecture rules</h3><div class="chips">${manifest.principles.map(p=>`<span class="chip">${esc(p)}</span>`).join('')}</div></div><div class="section"><h3>Root record</h3><button class="record-link" data-record="${esc(manifest.root.record)}"><span class="recordtype">OPEN ROOT</span><strong>Potato of Life</strong><code>${esc(manifest.root.record)}</code></button></div><div id="record-detail"></div>`}
function showContext(id){const c=(contextGraph.clusters||[]).find(x=>x.id===id);if(!c)return;searching=false;const branchButtons=(c.branches||[]).map(id=>{const b=branchById(id);return b?`<button class="branchnode" data-branch="${esc(id)}"><span>${esc(b.title)}</span><small>${esc(b.description)}</small></button>`:''}).join('');const records=(c.records||[]).map(p=>`<button class="record-link" data-record="${esc(p)}"><span class="recordtype">OPEN CONTEXT RECORD</span><strong>${esc(p.split('/').pop().replace(/\.(json|md)$/,''))}</strong><code>${esc(p)}</code></button>`).join('');$('#reader').innerHTML=`<div class="eyebrow">Context cluster</div><h2>${esc(c.title)}</h2><p class="summary">${esc(c.summary)}</p><div class="section"><h3>Concepts in this constellation</h3><div class="chips">${(c.concepts||[]).map(x=>`<span class="chip">${esc(x)}</span>`).join('')}</div></div><div class="section"><h3>Epistemic layers</h3><div class="chips">${(c.epistemic_mix||[]).map(x=>`<span class="chip epistemic">${esc(human(x))}</span>`).join('')}</div></div><div class="section"><h3>Connected branches</h3><div class="branchfield">${branchButtons}</div></div><div class="section"><h3>Records that carry this context</h3>${records}</div><div id="record-detail"></div>`;bindDynamic();history.replaceState(null,'',`#context=${encodeURIComponent(id)}`)}

function bindDynamic(){
  document.querySelectorAll('[data-record]').forEach(b=>b.onclick=()=>showRecord(b.dataset.record));
  document.querySelectorAll('[data-branch]').forEach(b=>b.onclick=()=>selectBranch(b.dataset.branch));
  document.querySelectorAll('[data-pathway]').forEach(b=>b.onclick=()=>showPathway(b.dataset.pathway));
  document.querySelectorAll('[data-context]').forEach(b=>b.onclick=()=>showContext(b.dataset.context));
}
function showPathway(id){const p=(manifest.pathways||[]).find(x=>x.id===id);if(!p)return;searching=false;const steps=p.branches.map((bid,i)=>{const b=branchById(bid);if(!b)return'';return `<button class="pathstep" data-branch="${esc(bid)}"><span>${String(i+1).padStart(2,'0')}</span><div><strong>${esc(b.title)}</strong><small>${esc(b.description)}</small></div></button>`}).join('');$('#reader').innerHTML=`<div class="eyebrow">Guided pathway</div><h2>${esc(p.title)}</h2><p class="summary">${esc(p.summary)}</p><div class="pathsteps">${steps}</div>`;bindDynamic();history.replaceState(null,'',`#path=${encodeURIComponent(id)}`)}
function selectBranch(id){const b=id==='root'?null:branchById(id);if(id!=='root'&&!b)id='root';active=id;searching=false;document.querySelectorAll('.branchbtn').forEach(btn=>btn.classList.toggle('active',btn.dataset.id===id));$('#reader').innerHTML=id==='root'?rootHTML():branchHTML(branchById(id));bindDynamic();history.replaceState(null,'',id==='root'?'#root':`#branch=${encodeURIComponent(id)}`)}
function buildNav(){const nav=$('#branches');nav.innerHTML=manifest.branches.map(b=>`<button class="branchbtn" data-id="${esc(b.id)}"><span class="title">${esc(b.title)}</span><span class="desc">${esc(b.description||'')}</span></button>`).join('');nav.querySelectorAll('.branchbtn').forEach(b=>b.onclick=()=>selectBranch(b.dataset.id));$('#rootbtn').onclick=()=>selectBranch('root')}
function applySearch(raw){const q=raw.trim().toLowerCase();document.querySelectorAll('.branchbtn').forEach(btn=>{const b=branchById(btn.dataset.id);const rels=relatedTo(b.id).map(r=>r.label).join(' ');const ctx=contextForBranch(b.id).flatMap(c=>[c.title,c.summary,...(c.concepts||[])]).join(' ');const hay=[b.title,b.description,...(b.children||[]),...(b.records||[]),rels,ctx].join(' ').toLowerCase();btn.style.display=!q||hay.includes(q)?'block':'none'});if(!q){if(searching)selectBranch(active||'root');return}if(q.length>2){const matches=(contextGraph.clusters||[]).filter(c=>[c.title,c.summary,...(c.concepts||[]),...(c.epistemic_mix||[])].join(' ').toLowerCase().includes(q));if(matches.length){searching=true;$('#reader').innerHTML=`<div class="eyebrow">Context search</div><h2>Context matches</h2><p class="summary">Search reaches concepts and contextual constellations, not only branch titles.</p><div class="contexts">${matches.map(contextCard).join('')}</div>`;bindDynamic()}else if(searching){$('#reader').innerHTML=`<div class="eyebrow">Context search</div><h2>No context matches</h2><p class="summary">Try a broader term or choose a branch from the left navigation.</p>`}}}

async function routeHash(){
  if(!manifest)return;
  const hash=location.hash||'#root';
  if(hash.startsWith('#branch=')){const id=decodeURIComponent(hash.slice(8));selectBranch(branchById(id)?id:'root')}
  else if(hash.startsWith('#record=')){selectBranch('root');await showRecord(decodeURIComponent(hash.slice(8)))}
  else if(hash.startsWith('#path=')){showPathway(decodeURIComponent(hash.slice(6)))}
  else if(hash.startsWith('#context=')){showContext(decodeURIComponent(hash.slice(9)))}
  else selectBranch('root');
}

async function init(){try{[manifest,contextGraph]=await Promise.all([loadJSON('manifest.json'),loadJSON('knowledge/indexes/context-graph.json').catch(()=>({clusters:[]}))]);buildNav();await routeHash();window.addEventListener('hashchange',routeHash);$('#q').oninput=e=>applySearch(e.target.value)}catch(e){$('#reader').innerHTML=`<div class="status">Archive failed to load: ${esc(e.message)}</div>`}}
init();
