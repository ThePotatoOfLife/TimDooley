(()=>{
  'use strict';

  const $=s=>document.querySelector(s);
  const state={manifest:null,cards:[],profiles:new Map(),visible:[],active:null,activeRef:null,bookCache:new Map()};
  const dims={P:'Provenance',E:'Explicitness',T:'Temporal independence',D:'Passage density',R:'Role fidelity',S:'Sequence fidelity',C:'Context survival',I:'Feature independence'};
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

  async function loadJson(url){
    const r=await fetch(url,{cache:'no-cache'});
    if(!r.ok)throw new Error(`${r.status} ${r.statusText}: ${url}`);
    return r.json();
  }

  function normalizeBook(book){return book==='Psalm'?'Psalms':book}

  function parseRef(ref){
    const m=String(ref).trim().match(/^(1 |2 |3 )?([A-Za-z]+(?: [A-Za-z]+)*)\s+(\d+)(?::(\d+)(?:-(\d+))?)?(?:-(\d+))?$/);
    if(!m)return null;
    const book=normalizeBook(`${m[1]||''}${m[2]}`.trim());
    const chapter=Number(m[3]);
    if(m[4])return{raw:ref,book,startChapter:chapter,endChapter:chapter,startVerse:Number(m[4]),endVerse:Number(m[5]||m[4])};
    return{raw:ref,book,startChapter:chapter,endChapter:Number(m[6]||chapter),startVerse:null,endVerse:null};
  }

  function bookNo(book){
    const i=state.manifest.book_order.indexOf(normalizeBook(book));
    return i<0?null:String(i+1).padStart(2,'0');
  }

  function refSortKey(ref){
    const p=parseRef(ref); if(!p)return[999,999,999];
    return[state.manifest.book_order.indexOf(p.book),p.startChapter,p.startVerse||0];
  }

  function cardBookSet(card){return new Set(card.scripture_refs.map(parseRef).filter(Boolean).map(x=>x.book))}
  function actorClass(a){const x=a.toLowerCase();if(x.includes('tim')&&!x.includes('son'))return'tim';if(x.includes('son')&&!x.includes('tim'))return'son';return'shared'}
  function projectYearKey(v){
    const m=String(v).match(/(20\d\d)(?:-(\d\d))?(?:-(\d\d))?/);if(!m)return Number.MAX_SAFE_INTEGER;
    return Number(m[1])*10000+Number(m[2]||12)*100+Number(m[3]||31);
  }

  function profile(card){return state.profiles.get(card.profile_id)||{scores:{}}}
  function sortCards(cards,lens){
    const out=[...cards];
    if(lens==='bible-order')return out.sort((a,b)=>{const A=refSortKey(a.scripture_refs[0]),B=refSortKey(b.scripture_refs[0]);return A[0]-B[0]||A[1]-B[1]||A[2]-B[2]});
    if(lens==='project-chronology')return out.sort((a,b)=>projectYearKey(a.project_date)-projectYearKey(b.project_date));
    const mode=state.manifest.reading_modes.find(x=>x.id===lens);const d=mode?.dimension;
    if(d)return out.sort((a,b)=>(profile(b).scores?.[d]||0)-(profile(a).scores?.[d]||0)||(profile(b).scores?.P||0)-(profile(a).scores?.P||0)||a.title.localeCompare(b.title));
    return out;
  }

  function applyFilters(){
    const lens=$('#lens').value,actor=$('#actor').value,book=$('#book').value,q=$('#search').value.trim().toLowerCase();
    let cards=state.cards.filter(card=>{
      if(actor!=='all'&&actorClass(card.actor)!==actor)return false;
      if(book!=='all'&&!cardBookSet(card).has(book))return false;
      if(q){const hay=[card.title,card.actor,card.project_date,card.project_anchor,card.overlap,card.boundary,...card.scripture_refs,...card.operators].join(' ').toLowerCase();if(!hay.includes(q))return false}
      return true;
    });
    state.visible=sortCards(cards,lens);renderIndex();
    if(state.active&&!state.visible.some(x=>x.profile_id===state.active.profile_id)){state.active=null;$('#reader-view').hidden=true;$('#empty').hidden=false}
    if(!state.active&&state.visible[0])selectCard(state.visible[0]);
  }

  function renderIndex(){
    $('#result-count').textContent=`${state.visible.length} / ${state.cards.length}`;
    $('#cards').innerHTML=state.visible.map(card=>{
      const p=profile(card),score=p.scores||{},lead=['E','T','D','R'].sort((a,b)=>(score[b]||0)-(score[a]||0))[0];
      return`<button class="br-card ${state.active?.profile_id===card.profile_id?'active':''}" data-id="${esc(card.profile_id)}"><small>${esc(card.scripture_refs[0])}</small><strong>${esc(card.title)}</strong><span>${esc(card.actor)} · ${lead||'P'} ${score[lead]||'–'}/5</span></button>`;
    }).join('')||'<div class="br-muted" style="padding:18px">No profiled overlaps match these filters.</div>';
    document.querySelectorAll('.br-card[data-id]').forEach(btn=>btn.addEventListener('click',()=>selectCard(state.cards.find(x=>x.profile_id===btn.dataset.id))));
  }

  function renderScores(scores={}){
    $('#score-summary').innerHTML=Object.keys(dims).map(k=>`<b title="${esc(dims[k])}">${k}${scores[k]??'–'}</b>`).join('');
    $('#scores').innerHTML=`<div class="br-score-grid">${Object.entries(dims).map(([k,name])=>`<div class="br-score-cell"><b>${k} ${scores[k]??'–'}/5</b><span>${esc(name)}</span></div>`).join('')}</div>`;
  }

  async function selectCard(card){
    if(!card)return;
    state.active=card;state.activeRef=card.scripture_refs[0];renderIndex();
    $('#empty').hidden=true;$('#reader-view').hidden=false;
    $('#active-actor').textContent=card.actor;
    $('#active-title').textContent=card.title;
    $('#active-direction').textContent=card.source_direction;
    $('#project-date').textContent=card.project_date;
    $('#operators').textContent=card.operators.join(' · ');
    $('#project-anchor').textContent=card.project_anchor;
    $('#overlap').textContent=card.overlap;
    $('#boundary').textContent=card.boundary;
    $('#owner').textContent=card.owner;
    renderScores(profile(card).scores);
    renderRefTabs();
    await renderScripture(state.activeRef);
  }

  function renderRefTabs(){
    $('#ref-tabs').innerHTML=state.active.scripture_refs.map(ref=>`<button class="${ref===state.activeRef?'active':''}" data-ref="${esc(ref)}">${esc(ref)}</button>`).join('');
    document.querySelectorAll('#ref-tabs button').forEach(btn=>btn.addEventListener('click',async()=>{state.activeRef=btn.dataset.ref;renderRefTabs();await renderScripture(state.activeRef)}));
  }

  async function fetchBook(book){
    const no=bookNo(book);if(!no)throw new Error(`Unknown book: ${book}`);
    if(state.bookCache.has(no))return state.bookCache.get(no);
    const url=state.manifest.source.upstream_json_template.replace('{book_no}',no);
    const promise=loadJson(url);state.bookCache.set(no,promise);
    try{return await promise}catch(e){state.bookCache.delete(no);throw e}
  }

  function cleanVerseHtml(html){
    const box=document.createElement('div');box.innerHTML=String(html||'');box.querySelectorAll('sup').forEach(x=>x.remove());
    return box.textContent.replace(/\u00a0/g,' ').replace(/\s+/g,' ').trim();
  }

  function inRef(item,p){
    const idx=String(item.index_reference||'').padStart(8,'0');
    const ch=Number(idx.slice(2,5)),v=Number(idx.slice(5,8));
    if(ch<p.startChapter||ch>p.endChapter)return false;
    if(p.startVerse==null)return true;
    return ch===p.startChapter&&v>=p.startVerse&&v<=p.endVerse;
  }

  async function renderScripture(ref){
    const p=parseRef(ref);$('#scripture-heading').textContent=ref;$('#scripture').innerHTML='';
    if(!p){$('#scripture-status').textContent='This citation is a comparative family label rather than a directly loadable verse range.';return}
    $('#scripture-status').textContent='Loading World English Bible…';
    try{
      const data=await fetchBook(p.book);const rows=data.filter(item=>inRef(item,p));
      if(!rows.length)throw new Error('No verses matched this reference.');
      $('#scripture-status').textContent=`${rows.length} verse${rows.length===1?'':'s'} · WEB`;
      $('#scripture').innerHTML=rows.map(item=>{const title=String(item.title||'');const vm=title.match(/:(\d+)$/);const no=vm?vm[1]:'?';return`<p class="br-verse"><span class="br-verse-no">${esc(no)}</span>${esc(cleanVerseHtml(item.content))}</p>`}).join('');
    }catch(err){
      $('#scripture-status').textContent='WEB passage could not be loaded.';
      $('#scripture').innerHTML=`<div class="br-error">${esc(err.message)} The reference and project annotation remain available; try again with network access.</div>`;
    }
  }

  function populateControls(){
    $('#lens').innerHTML=state.manifest.reading_modes.map(x=>`<option value="${esc(x.id)}">${esc(x.label)}</option>`).join('');
    $('#lens').value='bible-order';
    const represented=[...new Set(state.cards.flatMap(c=>[...cardBookSet(c)]))].sort((a,b)=>state.manifest.book_order.indexOf(a)-state.manifest.book_order.indexOf(b));
    $('#book').innerHTML='<option value="all">All represented books</option>'+represented.map(x=>`<option>${esc(x)}</option>`).join('');
    ['lens','actor','book'].forEach(id=>$(`#${id}`).addEventListener('change',applyFilters));$('#search').addEventListener('input',applyFilters);
  }

  async function init(){
    try{
      const [manifest,cards,profiles]=await Promise.all([
        loadJson('../data/bible/tim-son-reader-manifest.json'),
        loadJson('../data/bible/tim-son-reader-cards-top20.json'),
        loadJson('../knowledge/theology/biblical-overlap-profile-top20-2026-09-11.json')
      ]);
      state.manifest=manifest;state.cards=cards.cards||[];state.profiles=new Map((profiles.profiles||[]).map(x=>[x.id,x]));
      const s=manifest.baseline_snapshot||{};$('#stat-nodes').textContent=s.overlap_nodes??'–';$('#stat-refs').textContent=s.normalized_biblical_citation_forms??'–';$('#stat-books').textContent=s.biblical_books_represented??'–';$('#stat-profiles').textContent=s.profiled_nodes??state.cards.length;
      populateControls();applyFilters();
    }catch(err){
      $('#empty').innerHTML=`<div class="br-error">Reader data failed to load: ${esc(err.message)}</div>`;
    }
  }

  init();
})();
